import secrets
import hashlib
from typing import Optional


from app.shared.exception import BusinessError, ErrorType
from app.modules.api_tokens.crud import TokenCRUD
from app.modules.api_tokens.schema import (
    TokenCreate,
    TokenCreateResponse,
    TokenResponse,
    TokenVerifyResponse,
    TokenListResponse,
    TokenUpdate
)

class AuthService:
    """认证服务类 - 使用Pure DI模式，依赖TokenCRUD而非直接数据库会话"""
    
    def __init__(self, token_crud: TokenCRUD):
        """初始化认证服务
        
        Args:
            token_crud: Token CRUD操作实例
        """
        self.token_crud = token_crud
    
    def _generate_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def create_token(self, token_data: TokenCreate) -> TokenCreateResponse:

        # 生成原始token
        raw_token = self._generate_token()
        
        # 哈希token用于存储
        hashed_token = self._hash_token(raw_token)
        
        # 创建token记录
        token_record = await self.token_crud.create_token(
            hashed_token=hashed_token,
            note=token_data.note
        )
        
        # 构造响应
        token_info = TokenResponse.model_validate(token_record)
        
        return TokenCreateResponse(
            token=raw_token,
            token_info=token_info
        )
    
    async def verify_token(self, token: str) -> TokenVerifyResponse:
        # 哈希token进行查找
        hashed_token = self._hash_token(token)
        
        # 验证token
        token_record = await self.token_crud.verify_token(hashed_token)
        
        if token_record:
            token_info = TokenResponse.model_validate(token_record)
            return TokenVerifyResponse(
                is_valid=True,
                token_info=token_info,
                message="Token验证成功"
            )
        else:
            return TokenVerifyResponse(
                is_valid=False,
                token_info=None,
                message="Token无效或已过期"
            )
    
    async def get_token_by_id(self, token_id: int) -> Optional[TokenResponse]:
        token_record = await self.token_crud.get_token_by_id(token_id)
        
        if token_record:
            return TokenResponse.model_validate(token_record)
        return None
    
    async def get_all_valid_tokens(self) -> TokenListResponse:

        token_records = await self.token_crud.get_all_valid_tokens()
        
        tokens = [TokenResponse.model_validate(record) for record in token_records]
        
        return TokenListResponse(
            tokens=tokens,
            total=len(tokens)
        )
    
    async def update_token(self, token_id: int, token_data: TokenUpdate) -> Optional[TokenResponse]:
        
        check_exist = await self.get_token_by_id(token_id)
        if not check_exist:
            raise BusinessError(ErrorType.INVALID_ERROR, "Token不存在")
        
        # 构造更新字段
        update_fields = {}
        if token_data.note is not None:
            update_fields['note'] = token_data.note
        if token_data.is_valid is not None:
            update_fields['is_valid'] = token_data.is_valid
        
        if not update_fields:
            # 没有需要更新的字段，直接返回当前信息
            return await self.get_token_by_id(token_id)
        
        # 执行更新
        updated_record = await self.token_crud.update_token(token_id, **update_fields)
        
        if updated_record:
            return TokenResponse.model_validate(updated_record)
        return None
    
    async def activate_token(self, token_id: int) -> Optional[TokenResponse]:
        activated_record = await self.token_crud.activate_token(token_id)
        
        if activated_record:
            return TokenResponse.model_validate(activated_record)
        return None
    
    async def deactivate_token(self, token_id: int) -> Optional[TokenResponse]:
        deactivated_record = await self.token_crud.deactivate_token(token_id)
        
        if deactivated_record:
            return TokenResponse.model_validate(deactivated_record)
        return None
    
    async def soft_delete_token(self, token_id: int) -> bool:
        return await self.token_crud.soft_delete_token(token_id)
    
