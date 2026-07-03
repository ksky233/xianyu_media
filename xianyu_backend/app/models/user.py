from .base import Base
from sqlalchemy import Column, String, DateTime, BigInteger, Enum
from sqlalchemy.sql import func
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """用户模型
    
    用于JWT认证系统的用户表，支持管理员和普通用户角色
    """
    
    __tablename__ = "users"
    
    # 主键ID
    id = Column(
        BigInteger, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="用户唯一标识符"
    )
    
    # 用户名
    username = Column(
        String(50), 
        nullable=False, 
        unique=True,
        index=True,
        comment="用户名，唯一标识"
    )
    
    # 邮箱
    email = Column(
        String(100), 
        nullable=False, 
        unique=True,
        index=True,
        comment="用户邮箱，唯一标识"
    )
    
    # 加密密码
    hashed_password = Column(
        String(255), 
        nullable=False,
        comment="加密后的用户密码"
    )
    
    # 用户角色
    role = Column(
        String(10), 
        nullable=False, 
        default=UserRole.USER,
        index=True,
        comment="用户角色：admin-管理员，user-普通用户"
    )
    
    # 创建时间
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        index=True,
        comment="创建时间"
    )
    
    # 更新时间
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False,
        index=True,
        comment="最后更新时间"
    )
    
    # 软删除时间
    deleted_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        index=True,
        comment="删除时间，用于软删除"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """检查用户是否为管理员"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_active(self) -> bool:
        """检查用户是否处于活跃状态（未被软删除）"""
        return self.deleted_at is None