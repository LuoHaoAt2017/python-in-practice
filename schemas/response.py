from datetime import datetime
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """通用API响应格式"""
    code: int
    message: str
    data: Optional[T] = None
    timestamp: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class SuccessResponse(ApiResponse[dict]):
    """成功响应快捷方式"""
    def __init__(self, message: str = "Success", data: Optional[dict] = None):
        super().__init__(code=200, message=message, data=data)


class ErrorResponse(ApiResponse[None]):
    """错误响应快捷方式"""
    def __init__(self, code: int = 400, message: str = "Error"):
        super().__init__(code=code, message=message, data=None)


# HTTP状态码对应的常用响应
class OkResponse(SuccessResponse):
    """200 OK响应"""
    def __init__(self, message: str = "OK", data: Optional[dict] = None):
        super().__init__(message=message, data=data)


class CreatedResponse(SuccessResponse):
    """201 Created响应"""
    def __init__(self, message: str = "Created", data: Optional[dict] = None):
        super().__init__(message=message, data=data)
        self.code = 201


class BadRequestResponse(ErrorResponse):
    """400 Bad Request响应"""
    def __init__(self, message: str = "Bad Request"):
        super().__init__(code=400, message=message)


class NotFoundResponse(ErrorResponse):
    """404 Not Found响应"""
    def __init__(self, message: str = "Not Found"):
        super().__init__(code=404, message=message)


class InternalServerErrorResponse(ErrorResponse):
    """500 Internal Server Error响应"""
    def __init__(self, message: str = "Internal Server Error"):
        super().__init__(code=500, message=message)