
from app.shared.logger import logger
import json
from typing import TypeVar, Type, Optional, Any
from pydantic import BaseModel

from app.workflows.video_recongnizer import VideoBaseInfo, VideoSearchInfo, VideoHotInfo

T = TypeVar('T', bound=BaseModel)


def clean_json_content(response_content: str) -> str:
    """清洗LLM返回的JSON内容，去除Markdown标记"""
    json_content = response_content.strip()
    
    # 去除各种可能的 Markdown 代码块标记
    if json_content.startswith('```json'):
        json_content = json_content[7:]
    elif json_content.startswith('```'):
        json_content = json_content[3:]
    
    if json_content.endswith('```'):
        json_content = json_content[:-3]
    
    return json_content.strip()


def parse_llm_json(response_content: str) -> dict:
    """解析LLM返回的JSON内容为字典"""
    json_content = clean_json_content(response_content)
    
    # 尝试直接解析JSON
    try:
        return json.loads(json_content)
    except json.JSONDecodeError as e:
        # 如果直接解析失败，尝试提取第一个JSON对象
        try:
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', json_content)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        raise ValueError(f"无法解析JSON内容: {e}") from e


def parse_llm_response(
    response_content: str,
    model_class: Type[T],
    field_mapping: Optional[dict[str, str]] = None,
    default_instance: Optional[T] = None
) -> T:
    """
    通用的LLM响应解析方法
    
    Args:
        response_content: LLM返回的原始响应内容
        model_class: 要解析成的Pydantic模型类
        field_mapping: 字段名映射，key为LLM返回的字段名，value为模型字段名
        default_instance: 解析失败时返回的默认实例，如果为None则使用模型的默认值
    
    Returns:
        解析后的模型实例
    """
    try:
        # 解析JSON内容
        data = parse_llm_json(response_content)
        
        if not isinstance(data, dict):
            raise ValueError("解析结果不是字典类型")
        
        # 应用字段映射
        if field_mapping:
            mapped_data = {}
            for llm_key, model_key in field_mapping.items():
                if llm_key in data:
                    mapped_data[model_key] = data[llm_key]
            
            # 添加未映射的字段
            for key, value in data.items():
                if key not in field_mapping:
                    mapped_data[key] = value
            
            data = mapped_data
        
        # 创建模型实例
        instance = model_class(**data)
        
        logger.info(f"成功解析 {model_class.__name__}: {instance}")
        return instance
        
    except Exception as e:
        logger.error(f"解析LLM响应失败 [{model_class.__name__}]: {e}\n原始响应: {response_content[:500]}...")
        
        # 返回默认实例或创建新的空实例
        if default_instance is not None:
            return default_instance
        
        # 尝试创建带有默认值的实例
        try:
            return model_class()
        except Exception:
            # 如果模型没有默认值，返回带有错误信息的实例
            return model_class.model_construct(
                **{field.name: f"解析失败: {str(e)}" for field in model_class.model_fields.values()}
            )


# 针对特定模型的便捷解析函数

VideoBaseInfo_FIELD_MAPPING = {
    'video_title': 'title',
    'video_description': 'description',
    'video_tags': 'quality_tag'
}


def parse_video_base_info(response_content: str) -> VideoBaseInfo:
    """解析视频基础信息"""
    return parse_llm_response(
        response_content=response_content,
        model_class=VideoBaseInfo,
        field_mapping=VideoBaseInfo_FIELD_MAPPING,
        default_instance=VideoBaseInfo(
            title='LLM响应解析失败',
            description='LLM响应解析失败',
            year=2026
        )
    )


def parse_video_search_info(response_content: str) -> VideoSearchInfo:
    """解析视频搜索信息"""
    return parse_llm_response(
        response_content=response_content,
        model_class=VideoSearchInfo,
        field_mapping={},
        default_instance=VideoSearchInfo(
            type='unknown'
        )
    )


def parse_video_hot_info(response_content: str) -> VideoHotInfo:
    """解析视频热度信息"""
    return parse_llm_response(
        response_content=response_content,
        model_class=VideoHotInfo,
        field_mapping={},
        default_instance=VideoHotInfo(
            hot=0,
            hot_reason='热度信息解析失败'
        )
    )
