from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.modules.users.model import User
from app.shared.exception import BusinessError, ErrorType
from app.shared.logger import logger


class UserCRUD:
    """用户CRUD操作类
    
    提供用户的基础数据库操作，专注于JWT认证系统需要的功能
    """
    
    def __init__(self, db_session: AsyncSession):
        """初始化UserCRUD
        
        Args:
            db_session: 数据库会话
        """
        self.db_session = db_session
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User对象或None
        """
        stmt = select(User).where(
            User.username == username,
            User.deleted_at.is_(None)
        )
        result = await self.db_session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"根据用户名查询用户成功: {username}")
        else:
            logger.warning(f"用户不存在: {username}")
            return None
            
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            User对象或None
        """
        stmt = select(User).where(
            User.email == email,
            User.deleted_at.is_(None)
        )
        result = await self.db_session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"根据邮箱查询用户成功: {email}")
        else:
            logger.warning(f"邮箱对应的用户不存在: {email}")
            
        return user
    
    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """根据用户名或邮箱获取用户
        
        Args:
            identifier: 用户名或邮箱
            
        Returns:
            User对象或None
        """
        stmt = select(User).where(
            (User.username == identifier) | (User.email == identifier),
            User.deleted_at.is_(None)
        )
        result = await self.db_session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"根据用户名或邮箱查询用户成功: {identifier}")
        else:
            logger.warning(f"用户不存在: {identifier}")
            return None
            
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User对象或None
        """
        stmt = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None)
        )
        result = await self.db_session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"根据ID查询用户成功: {user_id}")
        else:
            logger.warning(f"用户不存在: {user_id}")
            return None
            
        return user
    
    async def update_password(self, user_id: int, hashed_password: str) -> bool:
        """更新用户密码
        
        Args:
            user_id: 用户ID
            hashed_password: 加密后的新密码
            
        Returns:
            是否更新成功
        """
        stmt = (
            update(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .values(hashed_password=hashed_password)
        )
        result = await self.db_session.execute(stmt)
        
        if result.rowcount > 0:
            logger.info(f"更新用户密码成功: {user_id}")
            return True
        else:
            logger.warning(f"用户不存在或已删除，无法更新密码: {user_id}")
            return False