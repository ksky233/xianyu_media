from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TokenBase(BaseModel):
    """Token基础模型"""
    note: Optional[str] = Field(None, description="Token备注信息")


class TokenCreate(TokenBase):
    """创建Token请求模型"""
    pass


class TokenUpdate(BaseModel):
    """更新Token请求模型"""
    note: Optional[str] = Field(None, description="Token备注信息")
    is_valid: Optional[bool] = Field(None, description="Token是否有效")


class TokenResponse(TokenBase):
    """Token响应模型"""
    id: int = Field(..., description="Token唯一标识")
    hashed_token: str = Field(..., description="Token哈希值")
    is_valid: bool = Field(..., description="Token是否有效")
    created_at: datetime = Field(..., description="创建时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")
    
    class Config:
        from_attributes = True


class TokenCreateResponse(BaseModel):
    """创建Token响应模型（包含原始token）"""
    token: str = Field(..., description="原始Token字符串")
    token_info: TokenResponse = Field(..., description="Token详细信息")
    
    class Config:
        from_attributes = True


class TokenVerifyRequest(BaseModel):
    """Token验证请求模型"""
    token: str = Field(..., description="待验证的Token")


class TokenVerifyResponse(BaseModel):
    """Token验证响应模型"""
    is_valid: bool = Field(..., description="Token是否有效")
    token_info: Optional[TokenResponse] = Field(None, description="Token详细信息（仅在有效时返回）")
    message: str = Field(..., description="验证结果消息")
    
    class Config:
        from_attributes = True


class TokenListResponse(BaseModel):
    """Token列表响应模型"""
    tokens: list[TokenResponse] = Field(..., description="Token列表")
    total: int = Field(..., description="总数量")
    
    class Config:
        from_attributes = True


class TokenStatusUpdate(BaseModel):
    """Token状态更新模型"""
    is_valid: bool = Field(..., description="Token是否有效")