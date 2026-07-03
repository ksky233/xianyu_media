# app/core/decorator.py
# 装饰器
from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from app.core.exception import BusinessError, ErrorType
from app.schemas.common_schema import UnifiedResponse
from app.core.logger import logger

def handle_exceptions(func: Callable) -> Callable:
    """统一异常处理装饰器
    
    专注于：
    1. 成功响应的统一包装
    2. 非业务异常的处理和转换
    
    BusinessError 由全局异常处理器统一处理，避免重复逻辑
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            result = await func(*args, **kwargs)  # 被装饰函数的返回值
            
            # 如果返回的已经是UnifiedResponse，直接返回
            if isinstance(result, UnifiedResponse):
                return result
            
            # 如果返回的是StreamingResponse，直接返回（不包装）
            if isinstance(result, StreamingResponse):
                return result
            
            # 否则包装成功响应
            return UnifiedResponse.success(data=result)
            
        except BusinessError:
            # BusinessError 让全局异常处理器处理，避免重复逻辑
            raise
            
        except ValueError as e:
            logger.error(f"参数值错误: {str(e)}")
            business_error = BusinessError(ErrorType.VALUE_ERROR, str(e))
            raise business_error  # 抛出给全局异常处理器处理
            
        except IntegrityError as e:
            logger.error(f"数据库完整性错误: {str(e)}")
            business_error = BusinessError(ErrorType.INTEGRITY_ERROR, str(e))
            raise business_error  # 抛出给全局异常处理器处理
            
        except HTTPException:
            # HTTPException 直接抛出，让 FastAPI 处理
            raise
            
        except Exception as e:
            # 未知异常转换为 BusinessError 后抛出
            logger.error(f"未知异常: {str(e)}", exc_info=True)
            business_error = BusinessError(ErrorType.UNKNOWN_ERROR, str(e))
            raise business_error  # 抛出给全局异常处理器处理
            
    return wrapper