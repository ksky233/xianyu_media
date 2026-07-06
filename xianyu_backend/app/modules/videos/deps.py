from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.videos.crud import VideoCRUD
from app.modules.videos.service import VideoService
from app.shared.db import get_db_session


async def get_video_crud(db_session: AsyncSession = Depends(get_db_session)) -> VideoCRUD:
    return VideoCRUD(db_session=db_session)


async def get_video_service(video_crud: VideoCRUD = Depends(get_video_crud)) -> VideoService:
    return VideoService(video_crud)
