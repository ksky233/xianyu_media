from app.shared.db import Base
from sqlalchemy import Column, String, Boolean, DateTime, Text,BigInteger
from sqlalchemy.sql import func



class ApiToken(Base):# 这里虽然显示紫色，但是生效了
    """
    API Token 数据库模型
    
    用于存储和管理API访问令牌的信息
    """
    __tablename__ = "api_tokens"
    
    # 主键ID
    id = Column(
        BigInteger, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="API Token唯一标识符"
    )
    
    # Token内容（哈希值）- 使用VARCHAR而不是String
    hashed_token = Column(
        String(64), 
        unique=True, 
        nullable=False, 
        comment="API Token哈希值，用于验证"
    )
    
    # Token是否有效
    is_valid = Column(
        Boolean, 
        default=True, 
        nullable=False,
        index=True,  # 添加索引，便于查询有效token
        comment="Token是否有效，True为有效，False为无效"
    )
    
    # 创建时间 - 使用TIMESTAMP WITH TIME ZONE
    created_at = Column(  
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False,
        index=True,  
        comment="Token创建时间"
    )
    
    # 删除时间（软删除）
    deleted_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        index=True,  
        comment="Token删除时间，用于软删除"
    )
    
    # 备注信息
    note = Column(
        Text, 
        nullable=True,
        comment="Token备注信息，用于描述Token用途或其他说明"
    )