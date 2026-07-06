from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.crud import UserCRUD
from app.modules.users.model import User
from app.modules.users.service import UserService
from app.shared.db import get_db_session
from app.shared.logger import logger
from app.shared.security.jwt import jwt_auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


def get_user_crud(db: AsyncSession = Depends(get_db_session)) -> UserCRUD:
    return UserCRUD(db)


def get_user_service(user_crud: UserCRUD = Depends(get_user_crud)) -> UserService:
    return UserService(user_crud)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_crud: UserCRUD = Depends(get_user_crud),
) -> User:
    try:
        payload = jwt_auth.verify_token(token)

        if payload is None:
            logger.warning(f"JWT token 验证失败: {token[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await user_crud.get_by_id(int(payload.sub))

        if user is None:
            logger.warning(f"用户不存在: ID {payload.sub}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"用户已被禁用: {user.username} (ID: {user.id})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.username != payload.username:
            logger.warning(f"JWT 用户名不匹配: JWT={payload.username}, DB={user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证信息不匹配",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.role != payload.role:
            logger.warning(f"JWT 角色不匹配: JWT={payload.role}, DB={user.role}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证信息不匹配",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"用户认证成功: {user.username} (ID: {user.id})")
        return user

    except ValueError:
        logger.warning("无效的用户 ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户 ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"获取当前用户异常: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        logger.warning(f"用户权限不足: {current_user.username} (ID: {current_user.id}), 角色: {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )

    logger.debug(f"管理员权限验证成功: {current_user.username} (ID: {current_user.id})")
    return current_user
