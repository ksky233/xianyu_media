from typing import Optional
from passlib.context import CryptContext
from app.modules.users.crud import UserCRUD
from app.modules.users.model import User
from app.modules.users.schema import UserLogin, UserChangePassword
from app.shared.exception import BusinessError, ErrorType
from app.shared.logger import logger


class UserService:
    """用户服务类
    
    处理用户相关的业务逻辑，包括登录验证和密码修改
    """
    
    def __init__(self, user_crud: UserCRUD):
        """初始化用户服务
        
        Args:
            user_crud: 用户CRUD操作实例
        """
        self.user_crud = user_crud
        # 密码加密上下文
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        # 验证输入参数
        if not login_data.username or not login_data.password:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "用户名和密码不能为空")
        
        # 根据用户名或邮箱查找用户
        user = await self.user_crud.get_by_username_or_email(login_data.username)
        
        if not user:
            logger.warning(f"用户登录失败，用户不存在: {login_data.username}")
            raise BusinessError(ErrorType.USER_NOT_REGISTERED, "未注册")
        
        # 检查用户是否被软删除
        if not user.is_active:
            logger.warning(f"用户登录失败，用户已被禁用: {login_data.username}")
            raise BusinessError(ErrorType.ACCOUNT_DISABLED, "账号已禁用")
        
        # 验证密码
        if not self.verify_password(login_data.password, user.hashed_password):
            logger.warning(f"用户登录失败，密码错误: {login_data.username}")
            raise BusinessError(ErrorType.PASSWORD_ERROR, "密码错误")
        
        logger.info(f"用户登录成功: {user.username} (ID: {user.id})")
        return user
    
    async def change_password(self, user_id: int, change_data: UserChangePassword) -> bool:
        # 验证输入参数
        if not change_data.old_password or not change_data.new_password:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "原密码和新密码不能为空")
        
        # 验证新密码和确认密码是否一致
        if not change_data.validate_passwords_match():
            raise BusinessError(ErrorType.INVALID_PARAMETER, "新密码和确认密码不一致")
        
        # 验证新密码不能与原密码相同
        if change_data.old_password == change_data.new_password:
            raise BusinessError(ErrorType.INVALID_PARAMETER, "新密码不能与原密码相同")
        
        # 获取用户信息
        user = await self.user_crud.get_by_id(user_id)
        if not user:
            raise BusinessError(ErrorType.RESOURCE_NOT_FOUND, "用户不存在")
        
        # 验证原密码
        if not self.verify_password(change_data.old_password, user.hashed_password):
            logger.warning(f"用户修改密码失败，原密码错误: {user.username}")
            raise BusinessError(ErrorType.INVALID_PARAMETER, "原密码错误")
        
        # 加密新密码
        new_hashed_password = self.get_password_hash(change_data.new_password)
        
        # 更新密码
        success = await self.user_crud.update_password(user_id, new_hashed_password)
        
        if success:
            logger.info(f"用户修改密码成功: {user.username} (ID: {user_id})")
            return True
        else:
            logger.error(f"用户修改密码失败: {user.username} (ID: {user_id})")
            raise BusinessError(ErrorType.DATABASE_ERROR, "密码修改失败")
