# app/core/exception.py
from enum import Enum
from typing import Optional
from fastapi import status

class ErrorType(Enum): 
    """业务错误码枚举，(业务码，异常描述)"""
    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description
        
    # 通用错误
    UNKNOWN_ERROR = (0, "未知异常")
    EXPIRED_ERROR = (400004, "资源过期")
    INVALID_ERROR = (400005, "资源无效")
    VALUE_ERROR = (400006, "参数值错误")
    INTEGRITY_ERROR = (400007, "数据库完整性错误")
    PERMISSION_DENIED = (403001, "权限不足")
    DATABASE_ERROR = (500001, "数据库操作错误")
    RESOURCE_NOT_FOUND = (404001, "资源不存在")
    RESOURCE_ALREADY_EXISTS = (400008, "资源已存在")

    INVALID_PARAMETER = (400001, "参数无效")
    UNAUTHORIZED_ERROR = (401001, "未认证")



class BusinessError(Exception):
    """业务逻辑异常基类，若使用此基类请传入ErrorType枚举，具体异常不需要。"""
    def __init__(self, error_type: ErrorType, detail: Optional[str] = None):
        self.error_code = error_type.code
        self.error_description = error_type.description
        self.detail = detail
        super().__init__(self.error_description)
    
       

# 具体异常类，提取预设一些常用的异常，避免频繁构造业务异常
class ExpiredError(BusinessError):
    """资源过期异常"""
    def __init__(self, detail: Optional[str] = None):
        super().__init__(ErrorType.EXPIRED_ERROR, detail)
    
class InvalidError(BusinessError):
    """资源无效异常"""
    def __init__(self, detail: Optional[str] = None):
        super().__init__(ErrorType.INVALID_ERROR, detail)
