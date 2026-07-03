from functools import partial
import time
from pydantic import BaseModel, Field
from typing import TypedDict, Optional
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.graph import StateGraph, START, END
from langchain_dev_utils.chat_models import load_chat_model
from langchain.messages import SystemMessage, HumanMessage, ToolMessage,AnyMessage
from typing_extensions import TypedDict, Annotated
from langgraph.prebuilt import ToolNode
import operator
from typing import Literal
from app.workflow.mcp_tools import mcp_tools_by_name,mcp_tools
from app.core.prompt import INSTRUCTION_VIDEO_BASEINFO_V2, INSTRUCTION_VIDEO_HOTINFO_FORMAT, INSTRUCTION_VIDEO_HOTINFO_GET, INSTRUCTION_VIDEO_SEARCHINFO_FORMAT, INSTRUCTION_VIDEO_SEARCHINFO_GET

from app.core.logger import logger

# 视频识别器v2，简化版，合并基础信息和搜索信息，允许字段未知

class VideoBaseInfo(BaseModel):
    title: str = Field(description="视频标题") 
    description: str = Field(description="视频描述") 
    type: str = Field(description="视频类型") 
    quality_tag: Optional[str] = Field(description="视频质量标签,可选", default=None) 
    year: int = Field(description="视频年份，无年份则默认最新年份", default=2026)
    episode: Optional[int] = Field(description="视频集数，可选", default=None)
    finished: Optional[int] = Field(description="视频是否完结 0连载中,1已完结，可选", default=None)
    region: Optional[str] = Field(description="视频主要受众，如美剧/韩剧/日剧等，可选", default=None) 
    actors: Optional[str] = Field(description="视频主要演员，动漫则填声优，可选", default=None)

class VideoHotInfo(BaseModel):
    rating: Optional[float] = Field(description="视频评分，可选", default=None) 
    hot: int = Field(description="视频热度，0-100")
    hot_tags: Optional[str] = Field(description="视频热门度标签，逗号分隔，可选", default=None)
    hot_reason: str = Field(description="视频热度原因，可选")

    

class VideoRecongnizerState(TypedDict):
    hot_messages: Annotated[list[AnyMessage], operator.add]
    video_text: str # 视频原始素材
    video_baseinfo: VideoBaseInfo # 视频基础信息
    video_hot_info: VideoHotInfo # 视频热度信息
    hot_tool_count: Annotated[int, operator.add]  # 工具调用计数器，避免无限循环
    



class VideoRecongnizerV2:
    def __init__(self, workflow_type: Optional[str] = None):
        self.llm = load_chat_model(model="qwen3-max", model_provider="dashscope", temperature=0.1)
        self.system_prompt_baseinfo = INSTRUCTION_VIDEO_BASEINFO_V2
        self.system_prompt_hotinfo = INSTRUCTION_VIDEO_HOTINFO_GET
        self.system_prompt_hotinfo_format = INSTRUCTION_VIDEO_HOTINFO_FORMAT
        self.workflow_type = workflow_type  # 可选值: "baseinfo", "searchinfo", "hotinfo", None(默认)
        self.app: Optional[CompiledStateGraph] = None
        self.hot_tool_executor = ToolNode(mcp_tools)
    
    def _create_workflow(self):
        graph = StateGraph(state_schema=VideoRecongnizerState)

        # 根据 workflow_type 决定添加哪些节点
        if self.workflow_type == "baseinfo" or self.workflow_type is None:
            graph.add_node("baseinfo_node", self.baseinfo_node)
            
        if self.workflow_type == "hotinfo" or self.workflow_type is None:
            graph.add_node("hotinfo_node", self.hotinfo_node)
            graph.add_node("hotinfo_format_node", self.format_hotinfo_node)
            graph.add_node("tool_node_hotinfo", self.hot_tool_wrapper) # 包装器需要保留，用于统计次数+1
            graph.add_node("hot_limit_handler", self.hot_limit_handler)
       
        
        # 根据 workflow_type 决定添加哪些边
        if self.workflow_type in ["baseinfo", None]:
            graph.add_edge(START, "baseinfo_node")
            graph.add_edge("baseinfo_node", END)
        

        if self.workflow_type in ["hotinfo", None]:
            graph.add_edge(START, "hotinfo_node")
            graph.add_conditional_edges(
                "hotinfo_node",
                self.should_continue,
                {
                    "continue": "tool_node_hotinfo",
                    "limit": "hot_limit_handler",
                    "end": "hotinfo_format_node"
                }   
            )
            graph.add_edge("tool_node_hotinfo", "hotinfo_node")
            graph.add_edge("hot_limit_handler", "hotinfo_node") # 限制节点指回LLM节点
            graph.add_edge("hotinfo_format_node", END)
        
        return graph

    def _compile_workflow(self):
        graph = self._create_workflow()
        self.app = graph.compile()
    
    def get_graph(self):
        """获取工作流图的Mermaid PNG,Byte数据"""
        if not self.app:
            self._compile_workflow()
        return self.app.get_graph().draw_mermaid()
        
    async def run(self, video_text: str):
        if not self.app:
            self._compile_workflow()
        
        initial_state = {
            "video_text": video_text,
            "hot_messages": [],
            "hot_tool_count": 0
        }
        result = await self.app.ainvoke(initial_state)
        # 在这里进行最后的业务逻辑检查
        return result.get("video_baseinfo"), result.get("video_hot_info")
        
    async def baseinfo_node(self, state: VideoRecongnizerState):
        video_text = state.get("video_text")
        if not video_text:
            raise ValueError("video_text is required")
        
        human_message_content = f"请按照规则对如下视频资源进行基本信息的提取: {video_text}"
        human_message = HumanMessage(content=human_message_content)

        llm_with_structured_output = self.llm.with_structured_output(schema=VideoBaseInfo, method="json_mode")
        start_time = time.time()
        model_response = await llm_with_structured_output.ainvoke(
            input=[
                SystemMessage(content=self.system_prompt_baseinfo),
                human_message,
            ]
        )
        end_time = time.time()
        logger.info(f"baseinfo_node time: {end_time - start_time}")

        if model_response.year is None:
            model_response.year = int(time.strftime("%Y", time.localtime()))

        return {
            "video_baseinfo": model_response
        }

    
    async def hotinfo_node(self, state: VideoRecongnizerState):
        video_text = state.get("video_text")
        if not video_text:
            raise ValueError("video_text is required")
        
        llm_with_tools = self.llm.bind_tools(mcp_tools)
        
        human_message_content = f"请按照规则对如下视频资源进行热度信息的提取并生成简要报告: {video_text}"
        human_message = HumanMessage(content=human_message_content)

        model_response = await llm_with_tools.ainvoke(
            input=[
                SystemMessage(content=self.system_prompt_hotinfo),
                human_message,
            ]+state.get("hot_messages", [])
        )
        
        return {"hot_messages": [model_response]}
    
    async def format_hotinfo_node(self, state: VideoRecongnizerState):
        hot_messages = state.get("hot_messages", [])
        if not hot_messages:
            raise ValueError("hot_messages is required")
        
        human_message_content = f"请按照规则对如下文本进行格式化抽取: {hot_messages[-1].content}"
        human_message = HumanMessage(content=human_message_content)

        start_time = time.time()
        llm_with_structured_output = self.llm.with_structured_output(schema=VideoHotInfo, method="json_mode")
        model_response = await llm_with_structured_output.ainvoke(
            input=[
                SystemMessage(content=self.system_prompt_hotinfo_format),
                human_message,
            ])
                
        end_time = time.time()
        logger.info(f"hotinfo_node 结构化耗时: {end_time - start_time}")
        return {"video_hot_info": model_response}

    async def hot_limit_handler(self, state: VideoRecongnizerState):
        """当达到上限时，生成虚拟的 ToolMessage"""
        last_message = state["hot_messages"][-1]
        results = []
        
        for tool_call in last_message.tool_calls:
            results.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content="[系统提示]：工具调用已达最大上限。无法进一步搜索。请根据目前已掌握的信息进行最终总结，不要再尝试调用工具。"
            ))
        
        # 返回消息，这会让 LLM 在下一轮对话中看到这些“错误结果”
        return {"hot_messages": results}

    async def hot_tool_wrapper(self, state: VideoRecongnizerState):
        """适配器：将 hot_messages 喂给 ToolNode 并累加计数"""
        inputs = {"messages": state["hot_messages"]}
        response = await self.hot_tool_executor.ainvoke(inputs)
        return {
            "hot_messages": response["messages"],
            "hot_tool_count": 1
        }

    def should_continue(self, state: VideoRecongnizerState) -> Literal["continue", "limit", "end"]:
        
        current_count = state.get("hot_tool_count", 0) # 获取当前已经调用的次数
        
        # 2. 安全检查消息
        messages = state.get("hot_messages", [])
        if not messages:
            return "end"
        
        last_msg = messages[-1]
        
        # 3. 核心路由逻辑，正常结束条件
        if not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
            return "end"
        
        max_limit = 3 
        if current_count >= max_limit:
            logger.warning(f"hotinfo_node 已达工具调用上限 {max_limit} 次，触发熔断。")
            return "limit"
        
        return "continue"