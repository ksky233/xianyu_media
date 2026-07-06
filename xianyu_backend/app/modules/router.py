from fastapi import APIRouter

from app.modules.api_tokens.router import router as api_token_router
from app.modules.users.router import router as user_router
from app.modules.videos.router import router as video_router

api_router = APIRouter()
api_router.include_router(api_token_router)
api_router.include_router(user_router)
api_router.include_router(video_router)
