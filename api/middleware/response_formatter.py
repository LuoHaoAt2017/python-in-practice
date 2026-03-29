import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Union
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from schemas.response import ApiResponse, SuccessResponse, ErrorResponse

logger = logging.getLogger(__name__)


class ResponseFormatterMiddleware(BaseHTTPMiddleware):
    """统一响应格式中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            # 调用下一个中间件或路由处理程序
            response = await call_next(request)

            # 如果已经是JSONResponse，检查是否需要包装
            if isinstance(response, JSONResponse):
                # 检查是否已经是我们的格式（通过headers标记）
                if response.headers.get("X-Response-Formatted") == "true":
                    return response

                # 获取响应内容
                body = response.body
                if body:
                    # 解码响应体
                    response_data = json.loads(body.decode("utf-8"))

                    # 根据状态码决定响应格式
                    if 200 <= response.status_code < 300:
                        # 成功响应
                        formatted_response = SuccessResponse(
                            message="Success", data=response_data
                        )
                    else:
                        # 错误响应
                        formatted_response = ErrorResponse(
                            code=response.status_code,
                            message=response_data.get("detail", "Error"),
                        )

                    # 创建新的JSONResponse
                    formatted_json = json.dumps(
                        formatted_response.model_dump(), default=str
                    )
                    new_response = JSONResponse(
                        content=formatted_response.model_dump(),
                        status_code=response.status_code,
                        headers=dict(response.headers),
                    )
                    new_response.headers["X-Response-Formatted"] = "true"
                    return new_response

            return response

        except Exception as e:
            logger.error(f"Error in response formatter: {str(e)}")
            # 发生错误时返回统一错误格式
            error_response = ErrorResponse(
                code=500, message=f"Internal Server Error: {str(e)}"
            )
            return JSONResponse(
                content=error_response.model_dump(),
                status_code=500,
                headers={"X-Response-Formatted": "true"},
            )


def add_response_formatter(app: FastAPI) -> None:
    """添加响应格式化中间件到FastAPI应用"""
    app.add_middleware(ResponseFormatterMiddleware)  # type: ignore


# 便捷函数，用于在路由中手动返回格式化响应
def format_success_response(
    data: Any = None, message: str = "Success"
) -> Dict[str, Any]:
    """格式化成功响应"""
    return {"code": 200, "message": message, "data": data, "timestamp": datetime.now()}


def format_error_response(code: int = 400, message: str = "Error") -> Dict[str, Any]:
    """格式化错误响应"""
    return {"code": code, "message": message, "data": None, "timestamp": datetime.now()}
