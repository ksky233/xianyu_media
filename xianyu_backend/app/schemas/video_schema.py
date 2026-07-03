from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.common_schema import PaginationParams


class VideoBase(BaseModel):
    """视频基础模型"""
    title: str = Field(..., description="视频标题", max_length=255)
    type: Optional[str] = Field(None, description="视频类型：电影/电视剧/动漫/短剧等", max_length=100)
    cover_url: Optional[str] = Field(None, description="封面图片URL")
    rating: Optional[float] = Field(None, ge=0, le=10, description="视频评分，0-10分")
    quality_tag: Optional[str] = Field(None, description="视频质量标签：1080P/720P/480P/WEB-DL等", max_length=100)
    description: Optional[str] = Field(None, description="视频简短描述")
    episode_count: Optional[int] = Field(default=0, description="视频总集数")
    actors: Optional[str] = Field(None, description="演员列表，多个演员用逗号分隔")
    year: Optional[int] = Field(None, description="上映年份")
    baidu_url: Optional[str] = Field(None, description="百度网盘资源链接")
    quark_url: Optional[str] = Field(None, description="夸克网盘资源链接")
    other_cloud_url: Optional[str] = Field(None, description="其他云盘资源链接")
    url_status: int = Field(default=1, description="网盘链接状态：0-都失效，1-主流有效，2-其他有效，3-都有效")
    marketing_text: Optional[str] = Field(None, description="营销文本：闲鱼等平台推广文本")
    extra_params: Optional[Dict[str, Any]] = Field(None, description="额外参数，存放对应type的专属属性")


class VideoCreate(VideoBase):
    """创建视频请求模型"""
    pass


class VideoUpdate(BaseModel):
    """更新视频请求模型"""
    title: Optional[str] = Field(None, description="视频标题", max_length=255)
    type: Optional[str] = Field(None, description="视频类型：电影/电视剧/动漫/短剧等", max_length=100)
    cover_url: Optional[str] = Field(None, description="封面图片URL")
    rating: Optional[float] = Field(None, ge=0, le=10, description="视频评分，0-10分")
    quality_tag: Optional[str] = Field(None, description="视频质量标签：1080P/720P/480P/WEB-DL等", max_length=100)
    description: Optional[str] = Field(None, description="视频简短描述")
    episode_count: Optional[int] = Field(None, description="视频总集数")
    actors: Optional[str] = Field(None, description="演员列表，多个演员用逗号分隔")
    year: Optional[int] = Field(None, description="上映年份")
    baidu_url: Optional[str] = Field(None, description="百度网盘资源链接")
    quark_url: Optional[str] = Field(None, description="夸克网盘资源链接")
    other_cloud_url: Optional[str] = Field(None, description="其他云盘资源链接")
    url_status: Optional[int] = Field(None, description="网盘链接状态：0-都失效，1-主流有效，2-其他有效，3-都有效")
    marketing_text: Optional[str] = Field(None, description="营销文本：闲鱼等平台推广文本")
    extra_params: Optional[Dict[str, Any]] = Field(None, description="额外参数，存放对应type的专属属性")


class VideoResponse(VideoBase):
    """视频响应模型"""
    id: int = Field(..., description="视频ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """视频列表响应模型"""
    items: List[VideoResponse] = Field(..., description="视频列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")


class VideoQueryParams(PaginationParams):
    """视频分页查询参数（仅用于基础分页）"""
    type: Optional[str] = Field(None, description="视频类型过滤")


class VideoConditionParams(PaginationParams):
    """视频条件查询参数（用于高级条件搜索）"""
    title: Optional[str] = Field(None, description="标题关键词搜索")
    type: Optional[str] = Field(None, description="视频类型筛选")
    url_status: Optional[int] = Field(None, description="网盘链接状态筛选")
    actors: Optional[str] = Field(None, description="演员关键词搜索")
    marketing_text: Optional[str] = Field(None, description="营销文本关键词搜索")
    year: Optional[int] = Field(None, description="上映年份筛选")
    rating: Optional[float] = Field(None, ge=0, le=10, description="评分筛选，0-10分")
    quality_tag: Optional[str] = Field(None, description="视频质量标签筛选：1080P/720P/480P/WEB-DL等")


