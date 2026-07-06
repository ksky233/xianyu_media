from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func
from app.modules.api_tokens.model import ApiToken


class TokenCRUD:
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create_token(self, hashed_token: str, note: Optional[str] = None) -> ApiToken:

    
        db_token = ApiToken(
            hashed_token=hashed_token,
            is_valid=True,
            note=note
        )
        
        self.db_session.add(db_token)
        await self.db_session.commit()
        await self.db_session.refresh(db_token)
        
        return db_token
    
    async def get_token_by_hash(self, hashed_token: str) -> Optional[ApiToken]:
        """
        根据哈希值获取token记录
        
        Args:
            hashed_token: token哈希值
            
        Returns:
            ApiToken实例或None
        """
        stmt = select(ApiToken).where(
            ApiToken.hashed_token == hashed_token,
            ApiToken.is_valid == True,
            ApiToken.deleted_at.is_(None)
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_token_by_id(self, token_id: int) -> Optional[ApiToken]:
        stmt = select(ApiToken).where(
            ApiToken.id == token_id,
            ApiToken.deleted_at.is_(None)
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all_valid_tokens(self, limit: int = 100, offset: int = 0) -> List[ApiToken]:
        """
        获取所有有效的token记录
        
        Args:
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            ApiToken列表
        """
        stmt = select(ApiToken).where(
            ApiToken.is_valid == True,
            ApiToken.deleted_at.is_(None)
        ).order_by(ApiToken.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
    
    async def deactivate_token(self, token_id: int) -> bool:
        """
        停用token（设置为无效）
        
        Args:
            token_id: token ID
            
        Returns:
            操作是否成功
        """
        stmt = update(ApiToken).where(
            ApiToken.id == token_id,
            ApiToken.deleted_at.is_(None)
        ).values(
            is_valid=False
        )
        
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        
        return result.rowcount > 0
    
    async def activate_token(self, token_id: str) -> bool:
        """
        激活token（设置为有效）
        
        Args:
            token_id: token ID
            
        Returns:
            操作是否成功
        """
        stmt = update(ApiToken).where(
            ApiToken.id == token_id,
            ApiToken.deleted_at.is_(None)
        ).values(
            is_valid=True
        )
        
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        
        return result.rowcount > 0
    
    async def soft_delete_token(self, token_id: int) -> bool:
        """
        软删除token
        
        Args:
            token_id: token ID
            
        Returns:
            操作是否成功
        """
        stmt = update(ApiToken).where(
            ApiToken.id == token_id,
            ApiToken.deleted_at.is_(None)
        ).values(
            deleted_at=func.now(),
            is_valid=False
        )
        
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        
        return result.rowcount > 0
    
    
    async def update_token(self, token_id: int, **update_fields) -> Optional[ApiToken]:
        
        if not update_fields:
            # 如果没有更新字段，直接返回当前记录
            return await self.get_token_by_id(token_id)
        
        stmt = update(ApiToken).where(
            ApiToken.id == token_id,
            ApiToken.deleted_at.is_(None)
        ).values(**update_fields)
        
        result = await self.db_session.execute(stmt)
        await self.db_session.commit()
        
        if result.rowcount > 0:
            # 返回更新后的记录
            return await self.get_token_by_id(token_id)
        return None
    
    async def verify_token(self, hashed_token: str) -> Optional[ApiToken]:
        """
        验证token是否有效
        
        Args:
            hashed_token: token哈希值
            
        Returns:
            如果token有效则返回ApiToken实例，否则返回None
        """
        stmt = select(ApiToken).where(
            ApiToken.hashed_token == hashed_token,
            ApiToken.is_valid == True,
            ApiToken.deleted_at.is_(None)
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()