from app.core.logger import logger
from langchain_mcp_adapters.client import MultiServerMCPClient
import json
from langchain.tools import tool
import asyncio
from typing import Dict, Any, Optional




async def get_mcp_tools():
    mcp_client = MultiServerMCPClient({
            "zhipu_websearch": {
                "transport": "http", 
                "url": "https://open.bigmodel.cn/api/mcp/web_search_prime/mcp",
                "headers": {  
                    "Authorization": "Bearer 99bef91b09c54276a62ea565b20f69fe.uD7Exz1PzdUidssm",  
                }
            },
            "zhipu_webreader": {
                "transport": "http", 
                "url": "https://open.bigmodel.cn/api/mcp/web_reader/mcp",
                "headers": {  
                    "Authorization": "Bearer 99bef91b09c54276a62ea565b20f69fe.uD7Exz1PzdUidssm",  
                }
            }
        })
    zhipu_websearch_tools = await mcp_client.get_tools()
    return zhipu_websearch_tools


@tool
async def web_search(query: str, content_size: str = "high"):
    """
    搜索互联网上的内容。

    :param query: 搜索的查询字符串。
    :param content_size: 搜索结果的内容大小，可选值为"high"或"medium"，默认值为"high"。
    :return: 搜索结果的列表，每个元素包含标题、链接和内容。如果触发并发限制，返回包含"并发错误"的字典。
    """
    try:
        tools = await get_mcp_tools()
        raw_result = await tools[0].ainvoke({"search_query": query,"content_size":content_size}) # 返回langchain的content_blocks结构
        text_result = json.loads(raw_result[0]['text']) # 这里的text为json字符串，需要解析
        final_result = json.loads(text_result)
        logger.debug(f"web_search 返回{len(final_result)}条结果")
        if len(final_result) > 5:
            return final_result[0:5] # 这里返回结果里列表
        else:
            return final_result
    except Exception as e:
        error_message = str(e)
        if "MCP error 429" in error_message or "并发数过高" in error_message:
            logger.warning(f"web_search 并发限制触发: {error_message}")
            return {"error": "并发错误", "message": "当前搜索并发数已达上限，请降低并发数"}
        else:
            logger.error(f"web_search 错误: {error_message}")
            return {"error": "搜索错误", "message": f"搜索失败: {error_message}"}

@tool
async def web_reader(url: str):
    """
    读取互联网上的内容。

    :param url: 要读取的URL字符串。
    :return: 读取到的URL内容字符串。如果触发并发限制，返回包含"并发错误"的字典。
    """
    try:
        tools = await get_mcp_tools()
        raw_result = await tools[1].ainvoke({"url": url}) # 返回langchain的content_blocks结构
        text_result = json.loads(raw_result[0]['text']) # 这里的text为json字符串，需要解析
        final_result = json.loads(text_result)
        logger.debug(f"web_reader 访问了{url}")
        return final_result['content']
    except Exception as e:
        error_message = str(e)
        if "MCP error 429" in error_message or "并发数过高" in error_message:
            logger.warning(f"web_reader 并发限制触发: {error_message}")
            return {"error": "并发错误", "message": "当前读取并发数已达上限，请降低并发数"}
        else:
            logger.error(f"web_reader 错误: {error_message}")
            return {"error": "读取错误", "message": f"读取失败: {error_message}"}

mcp_tools = [web_search, web_reader]

mcp_tools_by_name = {tool.name: tool for tool in mcp_tools}


# if __name__ == "__main__":
#     import asyncio
#     tool = asyncio.run(get_mcp_tools())
#     result = asyncio.run(tool.ainvoke({"search_query": "小米汽车","content_size":"high"})) # 返回langchain的content_blocks结构
#     search_result = json.loads(result[0]['text']) # 这里的text为json字符串，需要解析
#     #print(search_result) # 第一个结果的内容
    
#     # 调试信息
#     print(f"search_result 的类型: {type(search_result)}")
#     print(f"search_result 的长度: {len(search_result)}")

#     final_result = json.loads(search_result)

#     print(f"final_result 的类型: {type(final_result)}")
#     print(f"final_result 的长度: {len(final_result)}")

#     print(final_result[1]['content'])
#     print(type(final_result[1]['content']))


# if __name__ == "__main__":
#     import asyncio
#     tools = asyncio.run(get_mcp_tools())
#     web_reader_tool = tools[1]
#     result = asyncio.run(web_reader_tool.ainvoke({"url": "https://docs.bigmodel.cn/cn/coding-plan/mcp/reader-mcp-server"})) # 返回langchain的content_blocks结构
#     reader_result = json.loads(result[0]['text']) # 这里的text为json字符串，需要解析
#     final_result = json.loads(reader_result)
#     print(type(final_result))
