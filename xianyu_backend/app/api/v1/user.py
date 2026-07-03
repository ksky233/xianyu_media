from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.common_schema import UnifiedResponse
from app.schemas.user_schema import (
    LoginResponse,
    UserLogin, 
    UserChangePassword, 
    UserResponse,
    UserInfo
)
from app.service.user_service import UserService
from app.api.deps import get_user_service, get_current_user
from app.core.jwt_auth import jwt_auth
from app.models.user import User
from app.core.logger import logger
from app.core.exception import BusinessError, ErrorType
from app.core.decorator import handle_exceptions

router = APIRouter(
    prefix="/user",
    tags=["用户相关"]
)

@router.post("/login",response_model=UnifiedResponse,summary="用户登录")
@handle_exceptions
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    # 验证用户身份
    user = await user_service.authenticate_user(login_data)
    
    
    # 生成JWT访问令牌
    access_token = jwt_auth.create_user_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )
    
    # 构造响应数据
    user_info = UserInfo(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        created_at=user.created_at
    )
    
    token_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=jwt_auth.access_token_expire_minutes * 60,  # 转换为秒
        user_info=user_info
    )
    
    logger.info(f"用户登录成功: {user.username} (ID: {user.id})")
    
    return UnifiedResponse.success(data=token_response)


@router.post("/change-password",response_model=UnifiedResponse,summary="修改密码",)
@handle_exceptions
async def change_password(
    change_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    
    # 修改密码
    success = await user_service.change_password(current_user.id, change_data)
    return UnifiedResponse.success(data=success)        


@router.get("/profile",response_model=UnifiedResponse,summary="获取用户信息")
@handle_exceptions
async def get_user_profile(
    current_user: User = Depends(get_current_user),
):
  
 
    # 直接从current_user获取用户基本信息
    # 构造响应数据
    user_response = UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    
    logger.debug(f"获取用户信息成功: {current_user.username} (ID: {current_user.id})")
    
    return UnifiedResponse.success(data=user_response)