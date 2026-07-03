from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

# 定义一个泛型类型变量 T，用于表示 data 字段的具体类型
# 最大的好处就是统一前后端传输结构，前端可以直接.msg来生成提示语。
DataType = TypeVar('DataType')

class UnifiedResponse(BaseModel, Generic[DataType]):
    code: int = Field(..., description="业务状态码，例如 1 表示成功，其他表示特定错误")
    msg: Optional[str] = Field(default=None, description="提示信息，成功或失败时都可能提供")
    data: Optional[DataType] = Field(default=None, description="实际返回的数据")

    @classmethod
    def success(cls, code:int = 1,data: Optional[DataType] = None, msg: Optional[str] = "操作成功") -> "UnifiedResponse[DataType]":
        return cls(code=code, msg=msg, data=data)

    @classmethod
    def error(cls, code:int = 0,data: Optional[DataType] = None, msg: Optional[str] = "操作异常") -> "UnifiedResponse[DataType]": # code 可以更具体
        return cls(code=code, msg=msg, data=data)
    class Config:
        from_attributes = True 

# 分页参数依赖
class PaginationParams(BaseModel):
    """分页参数类
    
    用于统一处理分页参数
    """
    page: int = Field(default=1, description="页码，从1开始", ge=1)
    size: int = Field(default=20, description="每页大小", ge=1, le=50)
    
    @property
    def skip(self) -> int:
        """计算跳过的记录数"""
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        """获取限制数量"""
        return self.size