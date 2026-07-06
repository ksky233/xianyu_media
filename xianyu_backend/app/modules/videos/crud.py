from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.videos.model import Video
from app.modules.videos.schema import VideoCreate, VideoUpdate, VideoQueryParams, VideoConditionParams
from app.shared.exception import BusinessError, ErrorType
from app.shared.logger import logger
from datetime import datetime, timezone
import json

class VideoCRUD:
    """视频CRUD操作类"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    def _process_video_extra_params(self, video: Video) -> Video:
        """
        处理视频对象的extra_params字段，将JSON字符串转换为字典
        
        Args:
            video: 视频对象
            
        Returns:
            Video: 处理后的视频对象
        """
        if video and video.extra_params and isinstance(video.extra_params, str):
            try:
                video.extra_params = json.loads(video.extra_params)
            except (json.JSONDecodeError, TypeError):
                video.extra_params = None
        return video
    
    async def create(self, video_data: VideoCreate) -> Video:
        """
        创建视频
        
        Args:
            video_data: 视频创建数据
            
        Returns:
            Video: 创建的视频实例
        """
        # 转换数据，处理JSON字段
        create_data = video_data.model_dump()
        if create_data.get('extra_params') is not None:
            create_data['extra_params'] = json.dumps(create_data['extra_params'], ensure_ascii=False)
        
        video = Video(**create_data)
        self.db_session.add(video)
        await self.db_session.commit()
        await self.db_session.refresh(video)
        logger.info(f"创建视频成功: {video.id} - {video.title}")
        return self._process_video_extra_params(video)
    
    async def get_by_id(self, video_id: int) -> Optional[Video]:
        """
        根据ID获取视频
        
        Args:
            video_id: 视频ID
            
        Returns:
            Optional[Video]: 视频实例或None
        """
        stmt = select(Video).where(
            and_(
                Video.id == video_id,
                Video.deleted_at.is_(None)
            )
        )
        result = await self.db_session.execute(stmt)
        video = result.scalar_one_or_none()
        
        if not video:
            logger.warning(f"视频不存在: {video_id}")
            return None
            
        return self._process_video_extra_params(video)
    
    async def get_by_id_or_raise(self, video_id: int) -> Video:
        """
        根据ID获取视频，不存在则抛出异常
        
        Args:
            video_id: 视频ID
            
        Returns:
            Video: 视频实例
            
        Raises:
            BusinessError: 视频不存在时抛出
        """
        video = await self.get_by_id(video_id)
        if not video:
            raise BusinessError(ErrorType.NOT_FOUND, "视频不存在")
        return video
    
    async def update(self, video_id: int, video_data: VideoUpdate) -> Video:
        """
        更新视频
        
        Args:
            video_id: 视频ID
            video_data: 更新数据
            
        Returns:
            Video: 更新后的视频实例
        """
        video = await self.get_by_id_or_raise(video_id)
        
        # 只更新非None的字段
        update_data = video_data.model_dump(exclude_unset=True)
        
        # 处理JSON字段
        if 'extra_params' in update_data and update_data['extra_params'] is not None:
            update_data['extra_params'] = json.dumps(update_data['extra_params'], ensure_ascii=False)
        
        for field, value in update_data.items():
            setattr(video, field, value)
        
        await self.db_session.commit()
        await self.db_session.refresh(video)
        logger.info(f"更新视频成功: {video.id} - {video.title}")
        return self._process_video_extra_params(video)
    
    async def delete(self, video_id: int) -> bool:
        """
        软删除视频
        
        Args:
            video_id: 视频ID
            
        Returns:
            bool: 删除成功返回True
        """
        video = await self.get_by_id_or_raise(video_id)
        
        # 软删除：设置deleted_at时间戳
        video.deleted_at = datetime.now(timezone.utc)
        
        await self.db_session.commit()
        logger.info(f"删除视频成功: {video.id} - {video.title}")
        return True
    
    async def get_list(
        self, 
        query_params: VideoQueryParams | VideoConditionParams
    ) -> tuple[List[Video], int]:
        """
        分页查询视频列表
        
        Args:
            query_params: 查询参数（VideoQueryParams或VideoConditionParams）
            
        Returns:
            tuple[List[Video], int]: (视频列表, 总数量)
        """
        # 构建基础查询条件
        conditions = [Video.deleted_at.is_(None)]
        
        # 判断是否为条件搜索（VideoConditionParams类型）
        is_condition_search = isinstance(query_params, VideoConditionParams)
        
        # 添加精确匹配条件
        if hasattr(query_params, 'type') and query_params.type:
            conditions.append(Video.type == query_params.type)
        
        if hasattr(query_params, 'url_status') and query_params.url_status is not None:
            conditions.append(Video.url_status == query_params.url_status)
        
        if hasattr(query_params, 'year') and query_params.year is not None:
            conditions.append(Video.year == query_params.year)
        
        if hasattr(query_params, 'rating') and query_params.rating is not None:
            conditions.append(Video.rating == query_params.rating)
        
        # 处理文本搜索条件
        search_conditions = []
        if hasattr(query_params, 'title') and query_params.title:
            search_conditions.append(Video.title.ilike(f"%{query_params.title}%"))
        
        if hasattr(query_params, 'actors') and query_params.actors:
            search_conditions.append(Video.actors.ilike(f"%{query_params.actors}%"))
        
        if hasattr(query_params, 'marketing_text') and query_params.marketing_text:
            search_conditions.append(Video.marketing_text.ilike(f"%{query_params.marketing_text}%"))
        
        if hasattr(query_params, 'quality_tag') and query_params.quality_tag:
            search_conditions.append(Video.quality_tag.ilike(f"%{query_params.quality_tag}%"))
        
        # 根据搜索类型决定条件连接方式
        if search_conditions:
            if is_condition_search:
                # 条件搜索：使用AND连接所有条件
                conditions.extend(search_conditions)
            else:
                # 普通搜索：使用OR连接搜索条件（为了向后兼容）
                if len(search_conditions) == 1:
                    conditions.append(search_conditions[0])
                else:
                    conditions.append(or_(*search_conditions))
        
        # 查询总数
        count_stmt = select(func.count(Video.id)).where(and_(*conditions))
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar()
        
        # 分页查询数据
        offset = (query_params.page - 1) * query_params.size
        stmt = (
            select(Video)
            .where(and_(*conditions))
            .order_by(Video.created_at.desc())
            .offset(offset)
            .limit(query_params.size)
        )
        
        result = await self.db_session.execute(stmt)
        videos = result.scalars().all()
        
        # 处理每个视频的extra_params字段
        processed_videos = [self._process_video_extra_params(video) for video in videos]
        
        search_type = "条件搜索" if is_condition_search else "普通搜索"
        logger.info(f"{search_type}视频列表成功: 总数={total}, 当前页={query_params.page}")
        return processed_videos, total
    
    async def get_by_title(self, title: str) -> Optional[Video]:
        """
        根据标题获取视频
        
        Args:
            title: 视频标题
            
        Returns:
            Optional[Video]: 视频实例或None
        """
        stmt = select(Video).where(
            and_(
                Video.title == title,
                Video.deleted_at.is_(None)
            )
         )
        result = await self.db_session.execute(stmt)
        video = result.scalar_one_or_none()
        return self._process_video_extra_params(video) if video else None
     
    async def check_title_exists(self, title: str) -> bool:
        """
        检查指定标题的视频是否已存在
        
        Args:
            title: 视频标题
            
        Returns:
            bool: 是否存在
            
        Raises:
            BusinessError: 标题为空时抛出
        """
        if not title or not title.strip():
            raise BusinessError(ErrorType.INVALID_PARAMETER, "视频标题不能为空")
        
        video = await self.get_by_title(title)
        return video is not None
    
    async def get_all_active(self) -> List[Video]:
        """
        获取所有有效的视频
        
        Returns:
            List[Video]: 有效视频列表
        """
        stmt = (
            select(Video)
            .where(
                and_(
                    Video.deleted_at.is_(None),
                    Video.url_status > 0
                )
            )
            .order_by(Video.created_at.desc())
        )
        
        result = await self.db_session.execute(stmt)
        videos = result.scalars().all()
        
        # 处理每个视频的extra_params字段
        processed_videos = [self._process_video_extra_params(video) for video in videos]
        
        logger.info(f"获取所有有效视频成功: 数量={len(videos)}")
        return processed_videos
    
    async def search_by_keyword(self, keyword: str, page: int = 1, size: int = 20, video_type: str = None) -> tuple[List[Video], int]:
        """
        根据关键词搜索视频（标题、演员和营销文本）
        
        Args:
            keyword: 搜索关键词
            page: 页码
            size: 每页数量
            video_type: 视频类型过滤
            
        Returns:
            tuple[List[Video], int]: (视频列表, 总数量)
        """
        logger.info(f"搜索视频: {keyword}, 类型: {video_type}")
        
        if not keyword or not keyword.strip():
            raise BusinessError(ErrorType.INVALID_PARAMETER, "搜索关键词不能为空")
        
        # 构建搜索条件，使用OR连接
        search_conditions = [
            Video.deleted_at.is_(None),
            or_(
                Video.title.ilike(f"%{keyword.strip()}%"),
                Video.actors.ilike(f"%{keyword.strip()}%"),
                Video.marketing_text.ilike(f"%{keyword.strip()}%")
            )
        ]
        
        # 如果指定了类型，添加类型过滤
        if video_type:
            search_conditions.append(Video.type == video_type)
        
        # 查询总数
        count_stmt = select(func.count(Video.id)).where(and_(*search_conditions))
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar()
        
        # 分页查询数据
        offset = (page - 1) * size
        stmt = (
            select(Video)
            .where(and_(*search_conditions))
            .order_by(Video.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        
        result = await self.db_session.execute(stmt)
        videos = result.scalars().all()
        
        # 处理每个视频的extra_params字段
        processed_videos = [self._process_video_extra_params(video) for video in videos]
        
        logger.info(f"搜索视频成功: 总数={total}, 当前页={page}")
        return processed_videos, total
    
    async def batch_delete(self, video_ids: List[int]) -> int:
        """
        批量删除视频（软删除）
        
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
        
        # 构建批量更新语句
        stmt = (
            update(Video)
            .where(Video.id.in_(video_ids))
            .where(Video.deleted_at.is_(None))
            .values(deleted_at=datetime.utcnow())
            .execution_options(synchronize_session="fetch")
        )
        
        result = await self.db_session.execute(stmt)
        deleted_count = result.rowcount
        
        await self.db_session.commit()
        
        logger.info(f"批量删除视频成功: 删除数量={deleted_count}")
        return deleted_count
    
    async def condition_search(self, params: VideoConditionParams) -> tuple[List[Video], int]:
        """
        条件搜索视频（复用get_list的逻辑，因为条件搜索和普通搜索在CRUD层可以统一处理）
        
        Args:
            params: 条件搜索参数
            
        Returns:
            tuple[List[Video], int]: (视频列表, 总数量)
        """
        logger.info(f"条件搜索视频: {params}")
        
        # 直接调用get_list方法，因为它已经支持VideoConditionParams
        return await self.get_list(params)