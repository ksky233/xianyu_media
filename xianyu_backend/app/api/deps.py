from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger
from app.models import AsyncSessionFactory
from app.models.user import User
from app.schemas.auth_schema import TokenResponse
from app.service.auth_service import AuthService
from app.crud.crud_token import TokenCRUD
from app.service.video_service import VideoService
from app.crud.crud_video import VideoCRUD
# JWT用户认证相关导入
from app.core.jwt_auth import jwt_auth
from app.crud.crud_user import UserCRUD
from app.service.user_service import UserService


# API Token认证方案（用于API密钥认证）
security = HTTPBearer()

# OAuth2 Password Bearer认证方案（用于JWT用户认证）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_apitoken(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    获取当前请求的API令牌（仅提取，不验证）
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        str: 原始API令牌
    """
    return credentials.credentials

async def get_token_crud(
    db_session: AsyncSession = Depends(get_db_session)
) -> TokenCRUD:
    return TokenCRUD(db_session=db_session)

async def get_auth_service(
    token_crud: TokenCRUD = Depends(get_token_crud)
) -> AuthService:
    return AuthService(token_crud)


async def verify_api_token(
    token: str = Depends(get_current_apitoken),
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    验证API Token并返回Token信息
    
    Args:
        token: 从Authorization头中提取的Token
        auth_service: 认证服务实例
        
    Returns:
        TokenResponse: Token详细信息
        
    Raises:
        HTTPException: Token无效时抛出401错误
    """
    logger.debug(f"触发token验证: {token}")

    verify_result = await auth_service.verify_token(token)
    
    if not verify_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=verify_result.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return verify_result.token_info


# ==================== JWT用户认证相关依赖 ====================

def get_user_crud(db: AsyncSession = Depends(get_db_session)) -> UserCRUD:
    return UserCRUD(db)

def get_user_service(user_crud=Depends(get_user_crud)) -> UserService:
    return UserService(user_crud)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_crud: UserCRUD = Depends(get_user_crud)
) -> User:
    try:
        # 验证JWT token
        payload = jwt_auth.verify_token(token)
        
        if payload is None:
            logger.warning(f"JWT token验证失败: {token[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 根据用户ID获取用户信息
        user = await user_crud.get_by_id(int(payload.sub))
        
        if user is None:
            logger.warning(f"用户不存在: ID {payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 检查用户是否被软删除
        if not user.is_active:
            logger.warning(f"用户已被禁用: {user.username} (ID: {user.id})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 验证JWT中的用户名是否匹配
        if user.username != payload.username:
            logger.warning(f"JWT用户名不匹配: JWT中为 {payload.username}, 数据库中为 {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证信息不匹配",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 验证JWT中的角色是否匹配
        if user.role != payload.role:
            logger.warning(f"JWT角色不匹配: JWT中为 {payload.role}, 数据库中为 {user.role}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证信息不匹配",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        logger.debug(f"用户认证成功: {user.username} (ID: {user.id})")
        return user
        
    except ValueError:
        logger.warning(f"无效的用户ID: {payload.sub}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户ID",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前用户异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        logger.warning(f"用户权限不足: {current_user.username} (ID: {current_user.id}), 角色: {current_user.role.value}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    
    logger.debug(f"管理员权限验证成功: {current_user.username} (ID: {current_user.id})")
    return current_user


# ==================== Video相关依赖 ====================

async def get_video_crud(
    db_session: AsyncSession = Depends(get_db_session)
) -> VideoCRUD:
    """获取视频CRUD实例"""
    return VideoCRUD(db_session=db_session)


async def get_video_service(
    video_crud: VideoCRUD = Depends(get_video_crud)
) -> VideoService:
    """获取视频服务实例"""
    return VideoService(video_crud)
