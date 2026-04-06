# CLAUDE.md
本文档为 Claude Code (claude.ai/code) 提供在本仓库编写代码时的指导规范。

## 项目概述
这是一个基于 Sakila 示例数据库（DVD 租赁商店）的 FastAPI RESTful API，后端使用 PostgreSQL。项目为演员、影片、客户和租赁记录实现了 CRUD 操作，采用整洁架构设计。

## 架构设计
### 核心结构
- `models/`: SQLAlchemy ORM 模型（23+ 个模型，与 Sakila 架构完全映射）
- `schemas/`: 用于请求/响应验证的 Pydantic 模型
- `services/`: 业务逻辑层
- `api/endpoints/`: 按实体组织的 FastAPI 路由处理器
- `config/`: 应用配置与数据库设置
- `tests/`: 包含完整夹具的测试套件

### 数据库配置
- PostgreSQL + SQLAlchemy ORM + asyncpg 实现异步操作
- 使用 PostgreSQL 中的 `public` 模式（连接字符串中注意配置 `search_path=public`）
- 双引擎架构：同步引擎（`postgresql://`）用于脚本，异步引擎（`postgresql+asyncpg://`）用于 API
- 通过 `.env` 环境变量配置连接

### API 设计
- API 前缀：`/api/v1`
- 演员、影片、客户、租赁记录的标准 CRUD 接口
- 响应格式化中间件：`api/middleware/response_formatter.py`
- 开发环境开启 CORS
- 调试模式（DEBUG=True）下可访问交互式文档：`/docs`

## 开发命令
### 环境搭建与初始化
```bash
# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（创建表并加载测试数据）
python init_db.py

# 启动开发服务器
python main.py
```

### 数据库管理
```bash
# 带参数初始化数据库
python init_db.py --skip-check      # 跳过 PostgreSQL 连接检查
python init_db.py --skip-create     # 跳过数据库创建
python init_db.py --skip-tables     # 跳过表创建
python init_db.py --skip-data       # 跳过测试数据加载

# 访问交互式 API 文档：http://localhost:8000/docs
```

### 测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行指定测试文件
python -m pytest tests/test_api.py

# 详细输出模式
python -m pytest tests/ -v

# 测试使用 SQLite 内存数据库，完整夹具定义在 `tests/conftest.py`
```

### 代码质量
```bash
# 使用 Black 格式化代码
black .

# 使用 isort 排序导入
isort .
```

## 核心实现模式
### 模型结构
- 所有模型继承自 `models.base.Base`（包含 `created_at` 和 `updated_at` 时间戳）
- 外键关系使用 SQLAlchemy `relationship()` 定义，显式指定 `back_populates`
- 关联表（film_actor, film_category）使用联合主键

### 服务层模式
- 每个实体对应 `services/` 目录下的服务类
- 服务层处理数据库操作与业务逻辑
- API 端点调用服务，而非直接操作数据库

### 依赖注入
- 通过 FastAPI 依赖注入数据库会话（`get_async_db`）
- 配置通过 Pydantic Settings 管理：`config.settings`

### 错误处理
- 使用 FastAPI 内置的 HTTPException 处理 API 错误
- 数据库异常捕获并转换为对应 HTTP 状态码

## 配置说明
### 环境变量（`.env`）
- `DATABASE_URL`: 同步 PostgreSQL 连接（用于脚本/迁移）
- `DATABASE_URL_ASYNC`: 异步 PostgreSQL 连接（用于 FastAPI 接口）
- `DEBUG`: 开启调试模式与交互式文档
- `HOST`, `PORT`: 服务绑定地址
- `SECRET_KEY`: 应用密钥（生产环境必须修改）

### 数据库连接详情
- PostgreSQL 模式：`public`
- 默认凭证：postgres:LuoHao@123（连接字符串中已编码）
- 生产环境请替换为安全凭证

## 测试策略
- 使用 SQLite 内存数据库实现隔离测试
- 完整夹具创建全量测试数据层级
- 通过 `pytest-asyncio` 支持异步数据库操作
- 提供测试客户端用于 API 接口测试

## 新增功能流程
1. **添加模型**：在 `models/` 中创建并定义正确关联
2. **添加模型验证**：在 `schemas/` 中创建请求/响应模型
3. **添加服务**：在 `services/` 中实现业务逻辑
4. **添加接口**：在 `api/endpoints/` 中创建路由处理器
5. **注册路由**：添加到 `api/router.py`
6. **添加测试**：在 `tests/` 中编写测试并使用对应夹具

## 重要注意事项
- 开发环境（DEBUG=True）下通过 `main.py` 生命周期自动创建数据库表
- 生产环境使用 Alembic 迁移，替代 `Base.metadata.create_all()`
- 响应中间件统一格式化所有 API 响应
- `init_db.py` 加载的测试数据包含代表性样本数据
- 开发环境 CORS 全开，生产环境必须限制来源域名

---

## 三阶段工作流配置
### 1. 研究阶段（RESEARCH）
**每个任务开始前必须执行：**
- 使用 Glob 搜索相关文件：`*.ts`, `*.tsx`, `*.service.ts` 等
- 使用 Grep 搜索关键词：函数名、类名、相关业务术语
- 检查现有代码库中的类似实现
- 阅读相关模块的 README 或注释
- 理解项目架构和依赖关系

**不确定时必须联网搜索：**
- 新技术/框架的最佳实践
- 特定库的最新 API 文档
- 错误消息的解决方案

### 2. 开发阶段（DEVELOPMENT）
**严格遵循项目现有架构与编码规范**
- 按「模型→验证模型→服务→接口→测试」标准流程开发
- 所有代码必须符合下方**编码标准**与**质量红线**
- 开发过程中实时运行测试，确保功能正常
- 完成后自行执行代码格式化与导入排序

### 3. 验收阶段（ACCEPTANCE）
**提交代码前必须完成：**
- 执行全量测试用例，确保通过率 100%
- 检查代码是否符合所有质量红线要求
- 确认无硬编码、无敏感信息、无禁用校验规则
- 文档与注释完整，接口逻辑清晰可维护

---

## 质量红线配置（绝对禁止清单）
**以下行为绝不允许，没有例外：**

### 代码质量
- 绝不提交未通过测试的代码
- 绝不使用 TODO/FIXME/HACK 作为最终代码
- 绝不跳过错误处理
- 绝不吞掉异常（空 catch 块）
- 绝不使用魔法数字（必须定义常量）

### 类型安全
- 绝不使用 any 类型（用 unknown + 类型守卫）
- 绝不使用 @ts-ignore（解决根本问题）
- 绝不禁用 ESLint 规则（eslint-disable）

### 安全相关
- 绝不硬编码密钥、密码、Token
- 绝不在代码中包含敏感信息
- 绝不信任未验证的用户输入

---

## 编码标准配置（Python）
### 命名规范
- 文件/变量/函数：snake_case
- 类：PascalCase
- 常量：SCREAMING_SNAKE_CASE
- 私有成员：_leading_underscore
- 布尔值：is/has/can/should 前缀

### 函数规范
- 单个函数不超过 30 行
- 参数不超过 4 个，超过使用 dataclass
- 必须添加类型注解
- 一个函数只做一件事

### 错误处理
- 绝不使用 bare except
- 捕获具体异常类型
- 使用 Optional 处理可能为 None 的值

### 代码组织
- 导入顺序：标准库 → 第三方库 → 本地模块
- 公开函数必须有 Docstring
- 遵循 PEP 8 规范

### 总结
1. 已将文档**原有所有标题翻译为中文**，内容完全保留不变
2. 新增**三阶段工作流、质量红线、编码标准**三大配置模块，放在文档末尾
3. 格式统一、层级清晰，完全适配 Claude Code 识别规则
4. 整体结构：项目说明 → 技术规范 → 工作流 → 质量规则 → 编码标准