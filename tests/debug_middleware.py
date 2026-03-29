import json
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.testclient import TestClient

from api.middleware.response_formatter import ResponseFormatterMiddleware, add_response_formatter

# 创建测试应用
app = FastAPI()

# 手动添加中间件，不通过装饰器
app.add_middleware(ResponseFormatterMiddleware)

# 测试路由
router = APIRouter()

@router.get("/success")
async def success_endpoint():
    return {"test": "data"}

@router.get("/error")
async def error_endpoint():
    raise HTTPException(status_code=404, detail="Resource not found")

app.include_router(router)

# 测试客户端
client = TestClient(app)

# 测试
print("Testing middleware...")
print("-" * 50)

# 测试成功响应
response = client.get("/success")
print(f"Success endpoint - Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Body: {json.dumps(response.json(), indent=2)}")

print("\n" + "-" * 50)

# 测试错误响应
response = client.get("/error")
print(f"Error endpoint - Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Body: {json.dumps(response.json(), indent=2)}")

print("\n" + "-" * 50)

# 测试中间件是否正确处理了响应格式
print("Checking response format...")
success_response = client.get("/success").json()
if isinstance(success_response, dict):
    if "code" in success_response:
        print("✓ Success response has code field")
    else:
        print("✗ Success response missing code field")
    if "data" in success_response:
        print("✓ Success response has data field")
    else:
        print("✗ Success response missing data field")
    if "timestamp" in success_response:
        print("✓ Success response has timestamp field")
    else:
        print("✗ Success response missing timestamp field")