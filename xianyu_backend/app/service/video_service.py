from typing import List, Optional, Dict, Any
from app.crud.crud_video import VideoCRUD
from app.schemas.video_schema import (
    VideoCreate, 
    VideoUpdate, 
    VideoResponse, 
    VideoListResponse,
    VideoQueryParams,
    VideoConditionParams
)
from app.core.exception import BusinessError, ErrorType
from app.core.logger import logger
import math
import json


class VideoService:
    """视频业务服务类"""
    
    def __init__(self, video_crud: VideoCRUD):
        self.video_crud = video_crud
    
    async def create_video(self, video_data: VideoCreate) -> VideoResponse:
        """
        创建视频
        
        Args:
            video_data: 视频创建数据
            
        Returns:
            VideoResponse: 创建的视频信息
            
        Raises:
            BusinessError: 创建失败时抛出
        """
        logger.info(f"开始创建视频: {video_data.title}")
        
        # 验证必要字段
        if not video_data.title or not video_data.title.strip():
            raise BusinessError(ErrorType.INVALID_PARAMETER, "视频标题不能为空")
        
        # 检查标题是否已存在
        if await self._check_title_exists(video_data.title):
            raise BusinessError(ErrorType.RESOURCE_ALREADY_EXISTS, f"视频标题已存在: {video_data.title}")
        
        # 验证网盘状态值
        if video_data.url_status is not None and video_data.url_status not in [0, 1, 2, 3]:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "网盘状态值只能是0-3之间的整数")
        
        # 验证年份
        if video_data.year is not None and (video_data.year < 1900 or video_data.year > 2100):
            raise BusinessError(ErrorType.INVALID_PARAMETER, "年份必须在1900-2100之间")
        
        # 验证集数
        if video_data.episode_count is not None and video_data.episode_count < 0:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "集数不能为负数")
        
        video = await self.video_crud.create(video_data)
        return VideoResponse.model_validate(video)
    
    async def get_video_by_id(self, video_id: int) -> VideoResponse:
        """
        根据ID获取视频详情
        
        Args:
            video_id: 视频ID
            
        Returns:
            VideoResponse: 视频详情
            
        Raises:
            BusinessError: 视频不存在时抛出
        """
        logger.info(f"获取视频详情: {video_id}")
        
        if video_id <= 0:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "视频ID必须大于0")
        
        video = await self.video_crud.get_by_id_or_raise(video_id)
        return VideoResponse.model_validate(video)
    
    async def update_video(self, video_id: int, video_data: VideoUpdate) -> VideoResponse:
        """
        更新视频信息
        
        Args:
            video_id: 视频ID
            video_data: 更新数据
            
        Returns:
            VideoResponse: 更新后的视频信息
            
        Raises:
            BusinessError: 更新失败时抛出
        """
        logger.info(f"更新视频: {video_id}")
        
        if video_id <= 0:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "视频ID必须大于0")
        
        # 验证更新数据
        update_dict = video_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "没有提供任何更新字段")
        
        # 验证标题
        if "title" in update_dict:
            new_title = update_dict["title"]
            if not new_title or not new_title.strip():
                raise BusinessError(ErrorType.INVALID_PARAMETER, "视频标题不能为空")
            
            # 检查新标题是否与其他视频重复（排除当前视频）
            existing_video = await self.video_crud.get_by_title(new_title.strip())
            if existing_video and existing_video.id != video_id:
                raise BusinessError(ErrorType.RESOURCE_ALREADY_EXISTS, f"视频标题已存在: {new_title}")
        
        # 验证网盘状态值
        if "url_status" in update_dict and update_dict["url_status"] not in [0, 1, 2, 3]:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "网盘状态值只能是0-3之间的整数")
        
        # 验证年份
        if "year" in update_dict and update_dict["year"] is not None:
            year = update_dict["year"]
            if year < 1900 or year > 2100:
                raise BusinessError(ErrorType.INVALID_PARAMETER, "年份必须在1900-2100之间")
        
        # 验证集数
        if "episode_count" in update_dict and update_dict["episode_count"] is not None:
            episode_count = update_dict["episode_count"]
            if episode_count < 0:
                raise BusinessError(ErrorType.INVALID_PARAMETER, "集数不能为负数")
        
        video = await self.video_crud.update(video_id, video_data)
        return VideoResponse.model_validate(video)
    
    async def delete_video(self, video_id: int) -> bool:
        """
        删除视频（软删除）
        
        Args:
            video_id: 视频ID
            
        Returns:
            bool: 删除成功返回True
            
        Raises:
            BusinessError: 删除失败时抛出
        """
        logger.info(f"删除视频: {video_id}")
        
        if video_id <= 0:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "视频ID必须大于0")
        
        # 检查视频是否存在
        await self.video_crud.get_by_id_or_raise(video_id)
        
        return await self.video_crud.delete(video_id)
    
    async def get_videos(self, query_params: VideoQueryParams | VideoConditionParams) -> VideoListResponse:
        """
        分页查询视频列表
        
        Args:
            query_params: 查询参数
            
        Returns:
            VideoListResponse: 分页视频列表
            
        Raises:
            BusinessError: 查询失败时抛出
        """
        logger.info(f"查询视频列表: page={query_params.page}, size={query_params.size}")
        
        # 验证分页参数
        if query_params.page <= 0:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "页码必须大于0")
        
        if query_params.size <= 0 or query_params.size > 100:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "每页数量必须在1-100之间")
        
        videos, total = await self.video_crud.get_list(query_params)
        
        # 转换为响应模型
        video_responses = [VideoResponse.model_validate(video) for video in videos]
        
        return VideoListResponse(
            items=video_responses,
            total=total,
            page=query_params.page,
            size=query_params.size
        )
    
    async def get_all_active_videos(self) -> List[VideoResponse]:
        """
        获取所有有效的视频
        
        Returns:
            List[VideoResponse]: 有效视频列表
            
        Raises:
            BusinessError: 查询失败时抛出
        """
        logger.info("获取所有有效视频")
        
        videos = await self.video_crud.get_all_active()
        return [VideoResponse.model_validate(video) for video in videos]
    
    async def search_videos(self, keyword: str, query_params: VideoQueryParams) -> VideoListResponse:
        """
        根据关键词搜索视频（标题、演员和营销文本）
        
        Args:
            keyword: 搜索关键词
            query_params: 查询参数
            
        Returns:
            VideoListResponse: 搜索结果
            
        Raises:
            BusinessError: 搜索失败时抛出
        """
        logger.info(f"搜索视频: {keyword}")
        
        if not keyword or not keyword.strip():
            raise BusinessError(ErrorType.INVALID_PARAMETER, "搜索关键词不能为空")
        
        videos, total = await self.video_crud.search_by_keyword(
            keyword.strip(), 
            query_params.page, 
            query_params.size,
            query_params.type
        )
        
        # 转换为响应模型
        video_responses = [VideoResponse.model_validate(video) for video in videos]
        
        return VideoListResponse(
            items=video_responses,
            total=total,
            page=query_params.page,
            size=query_params.size
        )
    
    async def condition_search_videos(self, params: VideoConditionParams) -> VideoListResponse:
        """
        根据多个条件组合搜索视频
        
        Args:
            params: 条件搜索参数
            
        Returns:
            VideoListResponse: 搜索结果
            
        Raises:
            BusinessError: 搜索失败时抛出
        """
        logger.info(f"条件搜索视频: {params}")
        
        videos, total = await self.video_crud.condition_search(params)
        
        # 转换为响应模型
        video_responses = [VideoResponse.model_validate(video) for video in videos]
        
        return VideoListResponse(
            items=video_responses,
            total=total,
            page=params.page,
            size=params.size
        )
    
    async def batch_delete_videos(self, video_ids: List[int]) -> int:
        """
        批量删除视频
        
        Args:
            video_ids: 视频ID列表
            
        Returns:
            int: 删除的数量
            
        Raises:
            BusinessError: 删除失败时抛出
        """
        if not video_ids:
            return 0
        
        logger.info(f"批量删除视频: {video_ids}")
        
        deleted_count = await self.video_crud.batch_delete(video_ids)
        
        logger.info(f"批量删除视频成功: 删除数量={deleted_count}")
        return deleted_count
    
    async def _check_title_exists(self, title: str) -> bool:
        """
        私有方法：检查指定标题的视频是否已存在
        
        Args:
            title: 视频标题
            
        Returns:
            bool: 是否存在
            
        Raises:
            BusinessError: 标题为空时抛出
        """
        if not title or not title.strip():
            raise BusinessError(ErrorType.INVALID_PARAMETER, "视频标题不能为空")
        
        return await self.video_crud.check_title_exists(title.strip())