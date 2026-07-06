from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.api_tokens.crud import TokenCRUD
from app.modules.api_tokens.schema import TokenResponse
from app.modules.api_tokens.service import AuthService
from app.shared.db import get_db_session
from app.shared.logger import logger

security = HTTPBearer()


async def get_current_apitoken(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    return credentials.credentials


async def get_token_crud(db_session: AsyncSession = Depends(get_db_session)) -> TokenCRUD:
    return TokenCRUD(db_session=db_session)


async def get_auth_service(token_crud: TokenCRUD = Depends(get_token_crud)) -> AuthService:
    return AuthService(token_crud)


async def verify_api_token(
    token: str = Depends(get_current_apitoken),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    logger.debug(f"触发 token 验证: {token}")

    verify_result = await auth_service.verify_token(token)

    if not verify_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=verify_result.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_result.token_info
