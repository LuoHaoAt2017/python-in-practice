import json
import asyncio
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.testclient import TestClient

from api.middleware.response_formatter import add_response_formatter

# 创建测试应用
app = FastAPI()
add_response_formatter(app)

# 测试路由
router = APIRouter()

@router.get("/success")
async def success_endpoint():
    return {"message": "Success", "data": {"id": 1, "name": "test"}}

@router.get("/error")
async def error_endpoint():
    raise HTTPException(status_code=404, detail="Resource not found")

@router.get("/custom-error")
async def custom_error_endpoint():
    return {"detail": "Custom error"}, 400

app.include_router(router)

# 测试客户端
client = TestClient(app)

def test_success_response():
    """测试成功响应格式"""
    response = client.get("/success")
    print("Success Response Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    print()

    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "Success"
    assert data["data"] == {"message": "Success", "data": {"id": 1, "name": "test"}}
    assert "timestamp" in data

def test_error_response():
    """测试错误响应格式"""
    response = client.get("/error")
    print("Error Response Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    print()

    data = response.json()
    assert data["code"] == 404
    assert data["message"] == "Resource not found"
    assert data["data"] is None
    assert "timestamp" in data

def test_custom_error_response():
    """测试自定义错误响应格式"""
    response = client.get("/custom-error")
    print("Custom Error Response Test:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    print()

    data = response.json()
    assert data["code"] == 400
    assert data["message"] == "Custom error"
    assert data["data"] is None
    assert "timestamp" in data

if __name__ == "__main__":
    print("Testing Response Formatter Middleware")
    print("=" * 50)
    test_success_response()
    test_error_response()
    test_custom_error_response()
    print("All tests passed!")