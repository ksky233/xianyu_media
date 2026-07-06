from typing import List
from fastapi import APIRouter, Depends, Query
from app.shared.decorator import handle_exceptions
from app.modules.api_tokens.deps import verify_api_token
from app.modules.users.deps import get_current_user_admin
from app.modules.videos.deps import get_video_service
from app.modules.users.model import User
from app.modules.videos.service import VideoService
from app.modules.videos.schema import (
    VideoCreate, 
    VideoUpdate, 
    VideoResponse, 
    VideoListResponse,
    VideoQueryParams,
    VideoConditionParams
)
from app.modules.api_tokens.schema import TokenResponse
from app.shared.response import UnifiedResponse
from app.shared.logger import logger

router = APIRouter(prefix="/videos", tags=["视频管理"])


@router.post("/api-create", response_model=UnifiedResponse, summary="创建视频")
@handle_exceptions
async def create_video_with_api_token(
    video_data: VideoCreate,
    token_info: TokenResponse = Depends(verify_api_token),
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    创建新的视频
    
    - title: 视频标题（必填）
    - subtitle: 副标题（可选）
    - cover_url: 封面图片URL（可选）
    - description: 视频描述（可选）
    - type: 视频类型（必填）
    - episode_count: 总集数（可选）
    - year: 年份（可选）
    - region: 地区（可选）
    - director: 导演（可选）
    - actors: 演员列表（可选）
    - genres: 类型标签（可选）
    - language: 语言（可选）
    - release_date: 上映日期（可选）
    - extra_params: 额外参数，存放对应type的专属属性（可选）
    - baidu_url: 百度网盘链接（可选）
    - quark_url: 夸克网盘链接（可选）
    - other_cloud_url: 其他网盘链接（可选）
    - url_status: 网盘链接状态，0-都失效，1-主流有效，2-其他有效，3-都有效（默认1）
    """
    logger.info(f"api接口 {token_info.hashed_token} 创建视频: {video_data.title}")
    video = await video_service.create_video(video_data)
    return UnifiedResponse.success(data=video)


@router.post("/create", response_model=UnifiedResponse, summary="创建视频")
@handle_exceptions
async def create_video(
    video_data: VideoCreate,
    current_user: User = Depends(get_current_user_admin),
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    创建新的视频（需要管理员权限）
    """
    logger.info(f"管理员 {current_user.username} 创建视频: {video_data.title}")
    video = await video_service.create_video(video_data)
    return UnifiedResponse.success(data=video)


@router.get("", response_model=UnifiedResponse, summary="获取视频列表")
@handle_exceptions
async def get_videos(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    video_type: str = Query(None, description="视频类型过滤"),
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    获取视频列表（基础分页）
    
    - page: 页码，从1开始
    - size: 每页数量，最大100
    - video_type: 视频类型过滤
    """
    params = VideoQueryParams(page=page, size=size, type=video_type)
    videos = await video_service.get_videos(params)
    return UnifiedResponse.success(data=videos)


@router.get("/search", response_model=UnifiedResponse, summary="搜索视频")
@handle_exceptions
async def search_videos(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    video_type: str = Query(None, description="视频类型过滤"),
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    根据关键词搜索视频
    
    - keyword: 搜索关键词，将在标题、副标题、描述、导演、演员中搜索
    - page: 页码，从1开始
    - page_size: 每页数量，最大100
    - video_type: 视频类型过滤
    """
    params = VideoQueryParams(page=page, page_size=page_size, type=video_type)
    videos = await video_service.search_videos(keyword, params)
    return UnifiedResponse.success(data=videos)


@router.post("/condition-search", response_model=UnifiedResponse, summary="条件搜索视频")
@handle_exceptions
async def condition_search_videos(
    params: VideoConditionParams,
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    根据多个条件组合搜索视频（POST方式，避免GET参数验证问题）
    
    支持以下条件：
    - title: 标题关键词搜索
    - type: 视频类型筛选
    - url_status: 网盘链接状态筛选
    - actors: 演员关键词搜索
    - marketing_text: 营销文本关键词搜索
    - year: 上映年份筛选
    - rating: 评分筛选（0-10分）
    - page: 页码，从1开始
    - size: 每页大小
    """
    videos = await video_service.condition_search_videos(params)
    return UnifiedResponse.success(data=videos)


@router.get("/{video_id}", response_model=UnifiedResponse, summary="获取视频详情")
@handle_exceptions
async def get_video(
    video_id: int,
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    根据ID获取视频详情
    """
    video = await video_service.get_video_by_id(video_id)
    return UnifiedResponse.success(data=video)


@router.put("/{video_id}", response_model=UnifiedResponse, summary="更新视频")
@handle_exceptions
async def update_video(
    video_id: int,
    video_data: VideoUpdate,
    current_user: User = Depends(get_current_user_admin),
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    更新视频信息（需要管理员权限）
    """
    logger.info(f"管理员 {current_user.username} 更新视频 ID: {video_id}")
    video = await video_service.update_video(video_id, video_data)
    return UnifiedResponse.success(data=video)


@router.delete("/{video_id}", response_model=UnifiedResponse, summary="删除视频")
@handle_exceptions
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user_admin),
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    删除视频（软删除，需要管理员权限）
    """
    logger.info(f"管理员 {current_user.username} 删除视频 ID: {video_id}")
    await video_service.delete_video(video_id)
    return UnifiedResponse.success(msg="视频删除成功")


@router.post("/batch-delete", response_model=UnifiedResponse, summary="批量删除视频")
@handle_exceptions
async def batch_delete_videos(
    video_ids: List[int],
    current_user: User = Depends(get_current_user_admin),
    video_service: VideoService = Depends(get_video_service)
) -> UnifiedResponse:
    """
    批量删除视频（软删除，需要管理员权限）
    """
    logger.info(f"管理员 {current_user.username} 批量删除视频，数量: {len(video_ids)}")
    await video_service.batch_delete_videos(video_ids)
    return UnifiedResponse.success(msg=f"成功删除 {len(video_ids)} 个视频")
