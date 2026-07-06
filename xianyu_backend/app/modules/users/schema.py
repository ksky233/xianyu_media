from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.modules.users.model import UserRole


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名或邮箱", min_length=3, max_length=100)
    password: str = Field(..., description="密码", min_length=6, max_length=50)


class UserChangePassword(BaseModel):
    """用户修改密码请求模型"""
    old_password: str = Field(..., description="原密码", min_length=6, max_length=50)
    new_password: str = Field(..., description="新密码", min_length=6, max_length=50)
    confirm_password: str = Field(..., description="确认新密码", min_length=6, max_length=50)
    
    def validate_passwords_match(self) -> bool:
        """验证新密码和确认密码是否一致"""
        return self.new_password == self.confirm_password


class LoginResponse(BaseModel):
    """JWT Token响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间（秒）")
    user_info: "UserInfo" = Field(..., description="用户基本信息")


class UserInfo(BaseModel):
    """用户基本信息模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: UserRole = Field(..., description="用户角色")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """用户响应模型（完整信息）"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: UserRole = Field(..., description="用户角色")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")
    
    class Config:
        from_attributes = True


class JWTPayload(BaseModel):
    """JWT载荷模型"""
    sub: str = Field(..., description="用户ID（subject）")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")
    exp: int = Field(..., description="过期时间戳")
    iat: int = Field(..., description="签发时间戳")


# 更新TokenResponse的前向引用
LoginResponse.model_rebuild()