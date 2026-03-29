# Sakila数据库项目 - API设计与实现

## 概述

Sakila项目提供完整的RESTful API接口，遵循现代API设计最佳实践。所有端点都支持异步操作，提供完整的数据验证、错误处理和文档生成。

## API设计原则

### 1. RESTful设计
- 资源导向的设计
- 标准的HTTP方法（GET, POST, PUT, DELETE）
- 适当的HTTP状态码
- 统一的资源命名约定

### 2. 版本控制
- API版本前缀：`/api/v1/`
- 支持多版本共存
- 向后兼容性考虑

### 3. 一致性
- 统一的响应格式
- 标准的错误处理
- 一致的参数命名
- 可预测的端点行为

## API路由架构

### 1. 路由器配置 (`api/router.py`)
```python
from fastapi import APIRouter

from .endpoints import actors, films, customers, rentals, health

api_router = APIRouter()

# 包含不同模块的路由器
api_router.include_router(health.router, tags=["health"])
api_router.include_router(actors.router, prefix="/actors", tags=["actors"])
api_router.include_router(films.router, prefix="/films", tags=["films"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(rentals.router, prefix="/rentals", tags=["rentals"])
```

### 2. 主应用路由配置 (`main.py`)
```python
# 包含API路由器
app.include_router(api_router, prefix=settings.api_prefix)
```

## API端点设计

### 1. 健康检查端点 (`api/endpoints/health.py`)

#### 根端点
```python
@app.get("/")
async def root():
    """根端点，提供API信息"""
    return {
        "message": "Welcome to Sakila API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else None,
        "api_prefix": settings.api_prefix,
    }
```

#### 健康检查
```python
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}
```

### 2. 演员端点 (`api/endpoints/actors.py`)

#### 端点列表
```
GET    /api/v1/actors/              # 获取演员列表（支持分页和过滤）
GET    /api/v1/actors/{actor_id}    # 获取单个演员
GET    /api/v1/actors/{actor_id}/films  # 获取演员及其电影
POST   /api/v1/actors/              # 创建新演员
PUT    /api/v1/actors/{actor_id}    # 更新演员
DELETE /api/v1/actors/{actor_id}    # 删除演员
```

#### 代码示例：获取演员列表
```python
@router.get("/", response_model=ActorListResponse)
async def get_actors(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    name: Optional[str] = Query(None, description="按演员姓名过滤"),
):
    """获取演员列表，支持分页和过滤"""
    actors = await ActorService.get_actors(db, skip=skip, limit=limit, name=name)
    total = await ActorService.get_actors_count(db, name=name)

    return ActorListResponse(
        items=actors,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1,
    )
```

#### 设计特点
- 支持分页（skip, limit参数）
- 支持姓名过滤（模糊搜索）
- 返回分页元数据
- 异步数据库操作

### 3. 电影端点 (`api/endpoints/films.py`)

#### 端点列表
```
GET    /api/v1/films/                    # 获取电影列表
GET    /api/v1/films/{film_id}           # 获取单个电影
GET    /api/v1/films/{film_id}/actors    # 获取电影及其演员
GET    /api/v1/films/{film_id}/categories # 获取电影及其分类
POST   /api/v1/films/                    # 创建新电影
PUT    /api/v1/films/{film_id}           # 更新电影
DELETE /api/v1/films/{film_id}           # 删除电影
```

#### 代码示例：获取电影列表（带过滤）
```python
@router.get("/", response_model=FilmListResponse)
async def get_films(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    title: Optional[str] = Query(None, description="按电影标题过滤"),
    release_year: Optional[int] = Query(None, description="按发行年份过滤"),
    rating: Optional[str] = Query(None, description="按评级过滤"),
    language_id: Optional[int] = Query(None, description="按语言ID过滤"),
):
    """获取电影列表，支持多种过滤条件"""
    films = await FilmService.get_films(
        db,
        skip=skip,
        limit=limit,
        title=title,
        release_year=release_year,
        rating=rating,
        language_id=language_id,
    )
    total = await FilmService.get_films_count(
        db,
        title=title,
        release_year=release_year,
        rating=rating,
        language_id=language_id,
    )

    return FilmListResponse(
        items=films,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1,
    )
```

#### 设计特点
- 多条件过滤支持
- 复杂的查询逻辑封装在服务层
- 返回关联数据（演员、分类）
- 支持电影业务的特殊查询

### 4. 客户端点 (`api/endpoints/customers.py`)

#### 端点列表
```
GET    /api/v1/customers/                    # 获取客户列表
GET    /api/v1/customers/{customer_id}       # 获取单个客户
GET    /api/v1/customers/{customer_id}/rentals # 获取客户及其租赁记录
POST   /api/v1/customers/                    # 创建新客户
PUT    /api/v1/customers/{customer_id}       # 更新客户
DELETE /api/v1/customers/{customer_id}       # 删除客户
```

#### 设计特点
- 客户信息管理
- 租赁历史查询
- 电子邮件格式验证
- 激活状态管理

### 5. 租赁端点 (`api/endpoints/rentals.py`)

#### 端点列表
```
GET    /api/v1/rentals/                    # 获取租赁列表
GET    /api/v1/rentals/{rental_id}         # 获取单个租赁
GET    /api/v1/rentals/{rental_id}/details # 获取租赁详情（含电影和客户信息）
POST   /api/v1/rentals/                    # 创建新租赁
PUT    /api/v1/rentals/{rental_id}         # 更新租赁
PUT    /api/v1/rentals/{rental_id}/return  # 归还租赁（标记为已归还）
DELETE /api/v1/rentals/{rental_id}         # 删除租赁
```

#### 特殊端点：归还租赁
```python
@router.put("/{rental_id}/return")
async def return_rental(
    rental_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """标记租赁为已归还"""
    rental = await RentalService.return_rental(db, rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with ID {rental_id} not found",
        )
    return rental
```

#### 设计特点
- 核心业务操作
- 归还状态管理
- 租赁详情查询
- 库存关联管理

## 请求参数设计

### 1. 查询参数 (Query Parameters)
```python
# 分页参数
skip: int = Query(0, ge=0, description="跳过的记录数")
limit: int = Query(100, ge=1, le=1000, description="返回的记录数")

# 过滤参数
name: Optional[str] = Query(None, description="按姓名过滤")
title: Optional[str] = Query(None, description="按标题过滤")
release_year: Optional[int] = Query(None, description="按发行年份过滤")
rating: Optional[str] = Query(None, description="按评级过滤")
```

### 2. 路径参数 (Path Parameters)
```python
@router.get("/{actor_id}")
async def get_actor(
    actor_id: int,  # 路径参数
    db: AsyncSession = Depends(get_async_db),
):
    actor = await ActorService.get_actor_by_id(db, actor_id)
    return actor
```

### 3. 请求体参数 (Request Body)
```python
@router.post("/")
async def create_actor(
    actor_data: ActorCreate,  # Pydantic模型
    db: AsyncSession = Depends(get_async_db),
):
    actor = await ActorService.create_actor(db, actor_data)
    return actor
```

## 响应设计

### 1. 标准响应格式

#### 单对象响应
```json
{
  "actor_id": 1,
  "first_name": "PENELOPE",
  "last_name": "GUINESS",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 列表响应（带分页）
```json
{
  "items": [
    {"actor_id": 1, "first_name": "PENELOPE", "last_name": "GUINESS"},
    {"actor_id": 2, "first_name": "NICK", "last_name": "WAHLBERG"}
  ],
  "total": 200,
  "page": 1,
  "size": 10,
  "pages": 20
}
```

### 2. 关联数据响应

#### 演员带电影信息
```json
{
  "actor_id": 1,
  "first_name": "PENELOPE",
  "last_name": "GUINESS",
  "films": [
    {"film_id": 1, "title": "ACADEMY DINOSAUR"},
    {"film_id": 2, "title": "ACE GOLDFINGER"}
  ]
}
```

### 3. 错误响应
```json
{
  "detail": "Actor with ID 999 not found"
}
```

## 数据验证与序列化

### 1. Pydantic模型设计 (`schemas/`)

#### 基础模型
```python
class ActorBase(BaseModel):
    first_name: str
    last_name: str
```

#### 创建模型
```python
class ActorCreate(ActorBase):
    pass
```

#### 更新模型（字段可选）
```python
class ActorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
```

#### 响应模型
```python
class ActorResponse(ActorBase):
    actor_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### 2. 验证功能
- 数据类型验证
- 字符串长度限制
- 电子邮件格式验证
- 数值范围验证
- 可选字段处理

## 依赖注入设计

### 1. 数据库会话依赖
```python
async def get_async_db():
    """异步数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 2. 端点使用依赖
```python
@router.get("/{actor_id}")
async def get_actor(
    actor_id: int,
    db: AsyncSession = Depends(get_async_db),  # 注入数据库会话
):
    actor = await ActorService.get_actor_by_id(db, actor_id)
    return actor
```

## 错误处理设计

### 1. HTTP异常处理
```python
from fastapi import HTTPException, status

@router.get("/{actor_id}")
async def get_actor(actor_id: int, db: AsyncSession = Depends(get_async_db)):
    actor = await ActorService.get_actor_by_id(db, actor_id)
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with ID {actor_id} not found",
        )
    return actor
```

### 2. 状态码使用
- `200 OK`: 成功请求
- `201 Created`: 资源创建成功
- `204 No Content`: 成功删除，无返回内容
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

## 安全设计

### 1. CORS配置
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 输入验证
- Pydantic自动验证所有输入
- SQL注入防护（ORM处理）
- 防止恶意数据

## API文档生成

### 1. 自动文档生成
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### 2. 文档增强

#### 端点描述
```python
@router.get("/{actor_id}")
async def get_actor(actor_id: int, db: AsyncSession = Depends(get_async_db)):
    """根据ID获取演员信息"""
    actor = await ActorService.get_actor_by_id(db, actor_id)
    return actor
```

#### 参数描述
```python
async def get_actors(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
):
```

## 性能优化

### 1. 异步处理
- 所有端点和数据库操作异步
- 非阻塞I/O
- 支持高并发

### 2. 数据库连接池
```python
async_engine = create_async_engine(
    settings.database_url_async,
    echo=settings.debug,
    pool_pre_ping=True,      # 连接前检查
    pool_recycle=300,        # 连接回收时间（秒）
    future=True,
)
```

### 3. 查询优化
- 适当的索引设计
- 分页查询限制结果集大小
- 关联数据的延迟加载或预加载

## API测试示例

### 1. 使用curl测试
```bash
# 获取演员列表
curl -X GET "http://localhost:8000/api/v1/actors/"

# 获取演员详情
curl -X GET "http://localhost:8000/api/v1/actors/1"

# 创建新演员
curl -X POST "http://localhost:8000/api/v1/actors/" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Tom", "last_name": "Hanks"}'

# 过滤电影
curl -X GET "http://localhost:8000/api/v1/films/?title=adventure&rating=PG-13"
```

### 2. 使用Python requests测试
```python
import requests

# 获取演员列表
response = requests.get("http://localhost:8000/api/v1/actors/")
actors = response.json()

# 创建新电影
new_film = {
    "title": "New Adventure",
    "description": "An exciting adventure film",
    "language_id": 1,
    "rental_duration": 3,
    "rental_rate": 4.99,
    "replacement_cost": 19.99
}
response = requests.post("http://localhost:8000/api/v1/films/", json=new_film)
```

## 扩展性设计

### 1. 模块化端点
- 每个资源类型独立模块
- 易于添加新端点
- 清晰的职责分离

### 2. 版本控制支持
```python
# 当前版本
app.include_router(api_router, prefix="/api/v1")

# 未来版本
app.include_router(api_router_v2, prefix="/api/v2")
```

### 3. 中间件支持
- 可添加认证中间件
- 可添加日志中间件
- 可添加监控中间件

## 总结

Sakila项目的API设计体现了现代Web API的最佳实践：

1. **清晰的RESTful设计**：资源导向，标准HTTP方法
2. **完整的数据验证**：Pydantic提供强大的验证能力
3. **异步优先架构**：支持高并发，性能优异
4. **完善的错误处理**：统一的错误响应格式
5. **自动文档生成**：减少维护成本，提高开发效率
6. **模块化设计**：易于扩展和维护
7. **性能优化**：连接池、查询优化等

这种API设计不仅满足了Sakila项目的需求，也为其他类似项目提供了可复用的设计模式。通过FastAPI的强大功能，实现了开发效率和运行性能的平衡。