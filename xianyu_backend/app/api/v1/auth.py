from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from app.core.decorator import handle_exceptions
from app.api.deps import get_auth_service, verify_api_token
from app.core.logger import logger
from app.service.auth_service import AuthService
from app.schemas.auth_schema import (
    TokenCreate,
    TokenResponse,
    TokenUpdate,
    TokenVerifyRequest,
)
from app.schemas.common_schema import UnifiedResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/tokens", response_model=UnifiedResponse, summary="创建API Token")
@handle_exceptions
async def create_token(
    token_data: TokenCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> UnifiedResponse:
    """创建新的API Token"""
    token_info = await auth_service.create_token(token_data)
    return UnifiedResponse.success(data=token_info)


@router.post("/tokens/verify", response_model=UnifiedResponse, summary="验证API Token")
@handle_exceptions
async def verify_token(
    verify_data: TokenVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> UnifiedResponse:
    """验证API Token"""
    verify_result = await auth_service.verify_token(verify_data.token)
    return UnifiedResponse.success(data=verify_result)


@router.get("/tokens", response_model=UnifiedResponse, summary="获取所有有效Token")
@handle_exceptions
async def get_all_tokens(
    auth_service: AuthService = Depends(get_auth_service),
    token_info: TokenResponse = Depends(verify_api_token)

) -> UnifiedResponse:
    """获取所有有效的Token列表
    """
    token_list = await auth_service.get_all_valid_tokens()
    return UnifiedResponse.success(data=token_list)


@router.get("/tokens/{token_id}", response_model=UnifiedResponse, summary="获取Token详情")
@handle_exceptions
async def get_token(
    token_id: int,
    token_info: TokenResponse = Depends(verify_api_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> UnifiedResponse:

    token_res = await auth_service.get_token_by_id(token_id)
    
    return UnifiedResponse.success(data=token_res) 


@router.put("/tokens/{token_id}", response_model=UnifiedResponse, summary="更新Token")
@handle_exceptions
async def update_token(
    token_id: int,
    token_data: TokenUpdate,
    token_info: TokenResponse = Depends(verify_api_token),
    auth_service: AuthService = Depends(get_auth_service)
) -> UnifiedResponse:           
    """更新Token信息"""
    updated_token = await auth_service.update_token(token_id, token_data)
    return UnifiedResponse.success(data=updated_token)