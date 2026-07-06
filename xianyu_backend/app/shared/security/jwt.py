from datetime import datetime, timedelta,timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.modules.users.schema import JWTPayload
from app.shared.config import settings
from app.shared.logger import logger


class JWTAuth:
    """JWT认证工具类
    
    处理JWT token的生成、验证和解析
    """
    
    def __init__(self):
        """初始化JWT认证工具"""
        self.secret_key = settings.ACCESS_TOKEN_SECRET_KEY
        self.algorithm = settings.ACCESS_TOKEN_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            JWT访问令牌
        """
        to_encode = data.copy()
        
        # 获取当前时间
        now = datetime.now(timezone.utc)
        
        # 设置过期时间
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        # 添加时间戳字段
        to_encode.update({
            "exp": int(expire.timestamp()),  # 过期时间戳
            "iat": int(now.timestamp())      # 签发时间戳
        })
        
        # 生成JWT token
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"JWT token创建成功，用户ID: {data.get('sub')}, 过期时间: {expire}")
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[JWTPayload]:
        """验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            验证成功返回JWTPayload，失败返回None
        """
        try:
            # 解码JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 获取用户基本信息
            user_id: str = payload.get("sub")
            role: str = payload.get("role")
            username: str = payload.get("username")

            # 创建JWT载荷对象
            jwt_payload = JWTPayload(
                sub=user_id,
                username=username,
                role=role,
                exp=payload.get("exp"),
                iat=payload.get("iat") or int(datetime.now(timezone.utc).timestamp())  # 为旧token提供默认iat值
            )
            
            logger.debug(f"JWT token验证成功，用户: {username} (ID: {user_id})")
            return jwt_payload
            
        except JWTError as e:
            logger.warning(f"JWT token验证失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"JWT token验证异常: {str(e)}")
            return None
    
    def create_user_token(self, user_id: int, username: str, role: str) -> str:
        """为用户创建JWT令牌
        
        Args:
            user_id: 用户ID
            username: 用户名
            role: 用户角色
            
        Returns:
            JWT访问令牌
        """
        token_data = {
            "sub": str(user_id),
            "username": username,
            "role": role
        }
        
        return self.create_access_token(data=token_data)
    



# 全局JWT认证实例
jwt_auth = JWTAuth()