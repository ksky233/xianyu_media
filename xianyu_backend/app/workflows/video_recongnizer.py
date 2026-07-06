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
from app.workflows.mcp_tools import mcp_tools_by_name,mcp_tools
from app.shared.prompt import INSTRUCTION_VIDEO_BASEINFO, INSTRUCTION_VIDEO_HOTINFO_FORMAT, INSTRUCTION_VIDEO_HOTINFO_GET, INSTRUCTION_VIDEO_SEARCHINFO_FORMAT, INSTRUCTION_VIDEO_SEARCHINFO_GET

from app.shared.logger import logger

class VideoBaseInfo(BaseModel):
    title: str = Field(description="视频标题") 
    description: str = Field(description="视频描述") 
    quality_tag: Optional[str] = Field(description="视频质量标签,可选", default=None) 
    year: int = Field(description="视频年份，无年份则默认最新年份", default=2026)
    episode: Optional[int] = Field(description="视频集数，可选", default=None)
    finished: Optional[int] = Field(description="视频是否完结 0连载中,1已完结，可选", default=None)


class VideoSearchInfo(BaseModel):
    type: str = Field(description="视频类型") 
    rating: Optional[float] = Field(description="视频评分，可选", default=None) 
    region: Optional[str] = Field(description="视频主要受众，如美剧/韩剧/日剧等，可选", default=None) 
    actors: Optional[str] = Field(description="视频主要演员，动漫则填声优，可选", default=None)

class VideoHotInfo(BaseModel):
    hot: int = Field(description="视频热度，0-100")
    hot_tags: Optional[str] = Field(description="视频热门度标签，逗号分隔，可选", default=None)
    hot_reason: str = Field(description="视频热度原因，可选")

    

class VideoRecongnizerState(TypedDict):
    hot_messages: Annotated[list[AnyMessage], operator.add]
    search_messages: Annotated[list[AnyMessage], operator.add]
    video_text: str # 视频原始素材
    video_baseinfo: VideoBaseInfo # 视频基础信息
    video_search_info: VideoSearchInfo # 视频搜索信息
    video_hot_info: VideoHotInfo # 视频热度信息
    search_tool_count: Annotated[int, operator.add]  # 工具调用计数器，避免无限循环
    hot_tool_count: Annotated[int, operator.add]  # 工具调用计数器，避免无限循环
    



class VideoRecongnizer:
    def __init__(self, workflow_type: Optional[str] = None):
        self.llm = load_chat_model(model="qwen3-max", model_provider="dashscope", temperature=0.1)
        self.system_prompt_baseinfo = INSTRUCTION_VIDEO_BASEINFO
        self.system_prompt_searchinfo = INSTRUCTION_VIDEO_SEARCHINFO_GET
        self.system_prompt_hotinfo = INSTRUCTION_VIDEO_HOTINFO_GET
        self.system_prompt_hotinfo_format = INSTRUCTION_VIDEO_HOTINFO_FORMAT
        self.system_prompt_searchinfo_format = INSTRUCTION_VIDEO_SEARCHINFO_FORMAT
        self.workflow_type = workflow_type  # 可选值: "baseinfo", "searchinfo", "hotinfo", None(默认)
        self.app: Optional[CompiledStateGraph] = None
        self.search_tool_executor = ToolNode(mcp_tools)
        self.hot_tool_executor = ToolNode(mcp_tools)
    
    def _create_workflow(self):
        graph = StateGraph(state_schema=VideoRecongnizerState)

        # 根据 workflow_type 决定添加哪些节点
        if self.workflow_type == "baseinfo" or self.workflow_type is None:
            graph.add_node("baseinfo_node", self.baseinfo_node)
        
        if self.workflow_type == "searchinfo" or self.workflow_type is None:
            graph.add_node("searchinfo_node", self.searchinfo_node)
            graph.add_node("searchinfo_format_node", self.format_searchinfo_node)
            graph.add_node("tool_node_searchinfo", self.search_tool_wrapper) # 不再指向原生的ToolNode，而是指向包装器
            graph.add_node("search_limit_handler", self.search_limit_handler)
            
        if self.workflow_type == "hotinfo" or self.workflow_type is None:
            graph.add_node("hotinfo_node", self.hotinfo_node)
            graph.add_node("hotinfo_format_node", self.format_hotinfo_node)
            graph.add_node("tool_node_hotinfo", self.hot_tool_wrapper) # 不再指向原生的ToolNode，而是指向包装器
            graph.add_node("hot_limit_handler", self.hot_limit_handler)
       
        
        # 根据 workflow_type 决定添加哪些边
        if self.workflow_type in ["baseinfo", None]:
            graph.add_edge(START, "baseinfo_node")
            graph.add_edge("baseinfo_node", END)
        
        if self.workflow_type in ["searchinfo", None]:
            graph.add_edge(START, "searchinfo_node")
            graph.add_conditional_edges(
                "searchinfo_node",
                partial(self.should_continue, branch="search"),
                {
                    "continue": "tool_node_searchinfo",
                    "limit": "search_limit_handler",
                    "end": "searchinfo_format_node"
                }
            )
            graph.add_edge("tool_node_searchinfo", "searchinfo_node")
            graph.add_edge("search_limit_handler", "searchinfo_node") # 限制节点指回LLM节点，让LLM总结
            graph.add_edge("searchinfo_format_node", END)

        if self.workflow_type in ["hotinfo", None]:
            graph.add_edge(START, "hotinfo_node")
            graph.add_conditional_edges(
                "hotinfo_node",
                partial(self.should_continue, branch="hot"),
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
        return self.app.get_graph().draw_mermaid_png()
        
    async def run(self, video_text: str):
        if not self.app:
            self._compile_workflow()
        
        initial_state = {
            "video_text": video_text,
            "search_messages": [], # 显式初始化
            "hot_messages": [],
            "search_tool_count": 0,
            "hot_tool_count": 0
        }
        result = await self.app.ainvoke(initial_state)
        # 在这里进行最后的业务逻辑检查
        return result.get("video_baseinfo"), result.get("video_search_info"), result.get("video_hot_info")
        
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

    async def searchinfo_node(self, state: VideoRecongnizerState):
        video_text = state.get("video_text")
        if not video_text:
            raise ValueError("video_text is required")
        
        llm_with_tools = self.llm.bind_tools(mcp_tools)
        
        human_message_content = f"请按照规则利用网络搜索工具对如下视频资源进行的信息提取: {video_text}"
        human_message = HumanMessage(content=human_message_content)

        model_response = await llm_with_tools.ainvoke(
            input=[
                SystemMessage(content=self.system_prompt_searchinfo),
                human_message,
            ]+ state.get("search_messages", []))
                
        return {"search_messages": [model_response]}

    async def format_searchinfo_node(self, state: VideoRecongnizerState):
        search_messages = state.get("search_messages", [])
        if not search_messages:
            raise ValueError("search_messages is required")
        
        human_message_content = f"请按照规则对如下文本进行格式化抽取: {search_messages[-1].content}"
        human_message = HumanMessage(content=human_message_content)

        start_time = time.time()
        llm_with_structured_output = self.llm.with_structured_output(schema=VideoSearchInfo, method="json_mode")
        model_response = await llm_with_structured_output.ainvoke(
            input=[
                SystemMessage(content=self.system_prompt_searchinfo_format),
                human_message,
            ])
                
        end_time = time.time()
        logger.info(f"searchinfo_node 结构化耗时: {end_time - start_time}")
        return {"video_search_info": model_response}
    
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

    async def search_limit_handler(self, state: VideoRecongnizerState):
        """当达到上限时，生成虚拟的 ToolMessage"""
        last_message = state["search_messages"][-1]
        results = []
        
        for tool_call in last_message.tool_calls:
            results.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content="[系统提示]：工具调用已达最大上限。无法进一步搜索。请根据目前已掌握的信息进行最终总结，不要再尝试调用工具。"
            ))
        
        # 返回消息，这会让 LLM 在下一轮对话中看到这些“错误结果”
        return {"search_messages": results}

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

    async def search_tool_wrapper(self, state: VideoRecongnizerState):
        """适配器：将 search_messages 喂给 ToolNode 并累加计数"""
        # 1. 构造 ToolNode 期望的输入格式
        inputs = {"messages": state["search_messages"]}
        
        # 2. 调用内置的执行器
        response = await self.search_tool_executor.ainvoke(inputs)
        
        # 3. 将结果写回私有键名，并触发计数器累加
        return {
            "search_messages": response["messages"], # ToolNode 返回的是 {"messages": [...]}
            "search_tool_count": 1 # 触发 Annotated[int, operator.add] 自动累加
        }

    async def hot_tool_wrapper(self, state: VideoRecongnizerState):
        """适配器：将 hot_messages 喂给 ToolNode 并累加计数"""
        inputs = {"messages": state["hot_messages"]}
        response = await self.hot_tool_executor.ainvoke(inputs)
        return {
            "hot_messages": response["messages"],
            "hot_tool_count": 1
        }

    def should_continue(self, state: VideoRecongnizerState, branch: str) -> Literal["continue", "limit", "end"]:
       # 1. 根据传入的 branch 名称获取对应的动态限制和计数器
        limits = {"search": 2, "hot": 2}
        count_key = f"{branch}_tool_count" # 维护在状态中
        messages_key = f"{branch}_messages"
        
        max_limit = limits.get(branch, 3) # 获取当前分支限制
        current_count = state.get(count_key, 0) # 获取当前已经调用的次数
        
        # 2. 安全检查消息
        messages = state.get(messages_key, [])
        if not messages:
            return "end"
        
        last_msg = messages[-1]
        
        # 3. 核心路由逻辑，正常结束条件
        if not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
            return "end"
        
        # 4. 分支独立的熔断判断
        if current_count >= max_limit:
            logger.warning(f"分支 {branch} 已达调用上限 {max_limit} 次，触发熔断。")
            return "limit"
        
        return "continue"