# app/core/exception_handlers.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.shared.response import UnifiedResponse # 导入你的统一响应模型
from app.shared.logger import logger # 导入日志记录器
from app.shared.exception import BusinessError, ErrorType # 导入业务异常

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    捕获并自定义处理 Pydantic 的请求体验证错误
    """
    # 记录详细的验证错误日志，方便调试
    logger.error(f"请求体验证失败: {exc.errors()}")
    
    # 我们可以将 Pydantic 原始的错误信息进行简化，提取关键部分
    # 这里我们只提取第一条错误的 loc 和 msg，通常这已经足够
    first_error = exc.errors()[0]
    field = " -> ".join(map(str, first_error['loc'])) # 将 loc 列表转换为 "body -> field_name" 格式
    message = f"字段 '{field}': {first_error['msg']}"


    # 使用你的 UnifiedResponse 模型来构建响应
    unified_response = UnifiedResponse(
        code=ErrorType.INVALID_ERROR.code,
        msg="请求参数验证失败",
        data={"detail": message} # 将简化后的错误信息放在 data 字段中
    )
    
    # 返回一个 JSONResponse，状态码为 422 (FastAPI 默认)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=unified_response.model_dump()
    )


async def business_exception_handler(request: Request, exc: BusinessError):
    """
    捕获并处理业务逻辑异常
    """
    # 记录业务异常日志
    logger.warning(f"业务异常: {exc.error_description} - {exc.detail}")
    
    # 使用UnifiedResponse模型构建响应
    # 统一使用code=0表示错误，将具体错误码放在data.error_code中
    data = {
        "error_code": exc.error_code,
        "error_description": exc.error_description,
    }
    if exc.detail:
        data["detail"] = exc.detail
        
    unified_response = UnifiedResponse(
        code=0,  # 统一使用0表示错误
        msg=exc.detail or exc.error_description,
        data=data
    )
    
    # 权限异常返回403状态码，其他业务异常返回200状态码
    if exc.error_code == ErrorType.PERMISSION_DENIED.code:
        status_code = 403
    else:
        status_code = 200  # 其他业务异常统一返回200状态码
    
    return JSONResponse(
        status_code=status_code,
        content=unified_response.model_dump()
    )
