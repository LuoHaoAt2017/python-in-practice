"""
JWT 登录认证功能测试。

覆盖范围：
- config/security.py — 密码哈希 & JWT 工具函数
- models/user.py     — User ORM 模型
- services/auth.py   — AuthService 业务逻辑
- api/endpoints/auth.py  — 注册/登录接口
- api/router.py      — 受保护路由的 401 拦截
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from sqlalchemy.pool import StaticPool

from models import Base
from models.user import User

# ──────────────────────────────────────────────
# 测试专用内存数据库 Fixtures
# StaticPool 确保所有连接共享同一个 SQLite 内存 DB
# ──────────────────────────────────────────────

TEST_DB_URL_SYNC = "sqlite:///:memory:"
TEST_DB_URL_ASYNC = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="module")
def auth_sync_engine():
    engine = create_engine(
        TEST_DB_URL_SYNC,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def auth_async_engine():
    engine = create_async_engine(
        TEST_DB_URL_ASYNC,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def auth_db(auth_async_engine) -> AsyncSession:
    """每个测试独立的异步 SQLite 会话。"""
    factory = async_sessionmaker(
        auth_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        yield session


@pytest.fixture
def auth_client(auth_async_engine):
    """覆盖 get_async_db 依赖、使用 SQLite 的 TestClient。"""
    from main import app
    from config.database import get_async_db

    factory = async_sessionmaker(
        auth_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_async_db] = override_db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


# ──────────────────────────────────────────────
# 1. 安全工具函数测试（纯函数，无 DB）
# ──────────────────────────────────────────────

class TestSecurityUtils:
    """config/security.py 工具函数单元测试。"""

    def test_hash_password_returns_string(self):
        from config.security import hash_password
        result = hash_password("mysecret")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_password_is_not_plaintext(self):
        from config.security import hash_password
        result = hash_password("mysecret")
        assert result != "mysecret"

    def test_hash_password_different_hashes(self):
        """同一密码每次哈希结果不同（bcrypt 加盐）。"""
        from config.security import hash_password
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2

    def test_verify_password_correct(self):
        from config.security import hash_password, verify_password
        hashed = hash_password("correct_pass")
        assert verify_password("correct_pass", hashed) is True

    def test_verify_password_wrong(self):
        from config.security import hash_password, verify_password
        hashed = hash_password("correct_pass")
        assert verify_password("wrong_pass", hashed) is False

    def test_create_access_token_returns_string(self):
        from config.security import create_access_token
        token = create_access_token({"sub": "testuser"})
        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT 三段式

    def test_decode_access_token_valid(self):
        from config.security import create_access_token, decode_access_token
        token = create_access_token({"sub": "alice"})
        payload = decode_access_token(token)
        assert payload["sub"] == "alice"

    def test_decode_access_token_invalid_raises_401(self):
        from fastapi import HTTPException
        from config.security import decode_access_token
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_decode_access_token_tampered_raises_401(self):
        from fastapi import HTTPException
        from config.security import create_access_token, decode_access_token
        token = create_access_token({"sub": "alice"})
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered)
        assert exc_info.value.status_code == 401

    def test_token_expiry_in_payload(self):
        from config.security import create_access_token, decode_access_token
        token = create_access_token({"sub": "alice"})
        payload = decode_access_token(token)
        assert "exp" in payload


# ──────────────────────────────────────────────
# 2. User 模型测试
# ──────────────────────────────────────────────

class TestUserModel:
    """models/user.py ORM 模型测试（使用同步 SQLite）。"""

    def test_user_creation(self, auth_sync_engine):
        Session = sessionmaker(bind=auth_sync_engine)
        db = Session()
        try:
            user = User(
                username="modeluser",
                email="model@example.com",
                hashed_password="$2b$12$fakehash",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            assert user.user_id is not None
            assert user.username == "modeluser"
            assert user.email == "model@example.com"
            assert user.is_active is True
            assert user.is_superuser is False
            assert user.created_at is not None
            assert user.updated_at is not None
        finally:
            db.close()

    def test_user_repr(self, auth_sync_engine):
        Session = sessionmaker(bind=auth_sync_engine)
        db = Session()
        try:
            user = User(
                username="repruser",
                email="repr@example.com",
                hashed_password="$2b$12$fakehash",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            assert "repruser" in repr(user)
            assert "User" in repr(user)
        finally:
            db.close()

    def test_user_default_flags(self, auth_sync_engine):
        Session = sessionmaker(bind=auth_sync_engine)
        db = Session()
        try:
            user = User(
                username="flaguser",
                email="flag@example.com",
                hashed_password="hash",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            assert user.is_active is True
            assert user.is_superuser is False
        finally:
            db.close()


# ──────────────────────────────────────────────
# 3. AuthService 业务逻辑测试
# ──────────────────────────────────────────────

class TestAuthService:
    """services/auth.py 异步方法测试。"""

    @pytest.mark.asyncio
    async def test_create_user_success(self, auth_db):
        from schemas.auth import UserCreate
        from services.auth import AuthService

        data = UserCreate(username="svc_user", email="svc@example.com", password="pass1234")
        user = await AuthService.create_user(auth_db, data)

        assert user.user_id is not None
        assert user.username == "svc_user"
        assert user.email == "svc@example.com"
        assert user.hashed_password != "pass1234"  # 已哈希
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, auth_db):
        from fastapi import HTTPException
        from schemas.auth import UserCreate
        from services.auth import AuthService

        data = UserCreate(username="dup_user", email="dup1@example.com", password="pass1234")
        await AuthService.create_user(auth_db, data)

        data2 = UserCreate(username="dup_user", email="dup2@example.com", password="pass1234")
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.create_user(auth_db, data2)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, auth_db):
        from fastapi import HTTPException
        from schemas.auth import UserCreate
        from services.auth import AuthService

        data = UserCreate(username="email_u1", email="same@example.com", password="pass1234")
        await AuthService.create_user(auth_db, data)

        data2 = UserCreate(username="email_u2", email="same@example.com", password="pass1234")
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.create_user(auth_db, data2)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_get_user_by_username_exists(self, auth_db):
        from schemas.auth import UserCreate
        from services.auth import AuthService

        data = UserCreate(username="find_me", email="findme@example.com", password="pass1234")
        created = await AuthService.create_user(auth_db, data)

        found = await AuthService.get_user_by_username(auth_db, "find_me")
        assert found is not None
        assert found.user_id == created.user_id

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_exists(self, auth_db):
        from services.auth import AuthService

        result = await AuthService.get_user_by_username(auth_db, "ghost_user")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_exists(self, auth_db):
        from schemas.auth import UserCreate
        from services.auth import AuthService

        data = UserCreate(username="email_find", email="emailfind@example.com", password="pass1234")
        created = await AuthService.create_user(auth_db, data)

        found = await AuthService.get_user_by_email(auth_db, "emailfind@example.com")
        assert found is not None
        assert found.user_id == created.user_id

    @pytest.mark.asyncio
    async def test_authenticate_user_correct_password(self, auth_db):
        from schemas.auth import UserCreate
        from services.auth import AuthService

        data = UserCreate(username="auth_ok", email="authok@example.com", password="mypassword8")
        await AuthService.create_user(auth_db, data)

        user = await AuthService.authenticate_user(auth_db, "auth_ok", "mypassword8")
        assert user is not None
        assert user.username == "auth_ok"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_db):
        from schemas.auth import UserCreate
        from services.auth import AuthService

        data = UserCreate(username="auth_fail", email="authfail@example.com", password="realpass8")
        await AuthService.create_user(auth_db, data)

        result = await AuthService.authenticate_user(auth_db, "auth_fail", "wrongpass")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, auth_db):
        from services.auth import AuthService

        result = await AuthService.authenticate_user(auth_db, "nobody", "anypass")
        assert result is None


# ──────────────────────────────────────────────
# 4. 注册接口测试（HTTP）
# ──────────────────────────────────────────────

class TestRegisterEndpoint:
    """POST /api/v1/auth/register 接口测试。"""

    def test_register_success(self, auth_client):
        resp = auth_client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["is_active"] is True
        assert "hashed_password" not in data  # 密码不暴露

    def test_register_duplicate_username(self, auth_client):
        auth_client.post("/api/v1/auth/register", json={
            "username": "dupname",
            "email": "dup1@example.com",
            "password": "password123",
        })
        resp = auth_client.post("/api/v1/auth/register", json={
            "username": "dupname",
            "email": "dup2@example.com",
            "password": "password123",
        })
        assert resp.status_code == 409

    def test_register_duplicate_email(self, auth_client):
        auth_client.post("/api/v1/auth/register", json={
            "username": "uname1",
            "email": "dupemail@example.com",
            "password": "password123",
        })
        resp = auth_client.post("/api/v1/auth/register", json={
            "username": "uname2",
            "email": "dupemail@example.com",
            "password": "password123",
        })
        assert resp.status_code == 409

    def test_register_password_too_short(self, auth_client):
        resp = auth_client.post("/api/v1/auth/register", json={
            "username": "shortpw",
            "email": "short@example.com",
            "password": "1234567",  # 7 位，不足 8 位
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self, auth_client):
        resp = auth_client.post("/api/v1/auth/register", json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "password123",
        })
        assert resp.status_code == 422

    def test_register_missing_fields(self, auth_client):
        resp = auth_client.post("/api/v1/auth/register", json={
            "username": "incomplete",
        })
        assert resp.status_code == 422


# ──────────────────────────────────────────────
# 5. 登录接口测试（HTTP）
# ──────────────────────────────────────────────

class TestLoginEndpoint:
    """POST /api/v1/auth/login 接口测试。"""

    def _register(self, client, username="loginuser", password="pass12345"):
        client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        })

    def test_login_success_returns_token(self, auth_client):
        self._register(auth_client, "login_ok")
        resp = auth_client.post("/api/v1/auth/login", json={
            "username": "login_ok",
            "password": "pass12345",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 10

    def test_login_wrong_password(self, auth_client):
        self._register(auth_client, "login_wp")
        resp = auth_client.post("/api/v1/auth/login", json={
            "username": "login_wp",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, auth_client):
        resp = auth_client.post("/api/v1/auth/login", json={
            "username": "ghost",
            "password": "pass12345",
        })
        assert resp.status_code == 401

    def test_login_missing_username(self, auth_client):
        resp = auth_client.post("/api/v1/auth/login", json={
            "password": "pass12345",
        })
        assert resp.status_code == 422

    def test_login_token_is_valid_jwt(self, auth_client):
        """登录返回的 token 可被正确解码。"""
        self._register(auth_client, "jwt_check")
        resp = auth_client.post("/api/v1/auth/login", json={
            "username": "jwt_check",
            "password": "pass12345",
        })
        token = resp.json()["data"]["access_token"]

        from config.security import decode_access_token
        payload = decode_access_token(token)
        assert payload["sub"] == "jwt_check"
        assert "exp" in payload


# ──────────────────────────────────────────────
# 6. 受保护路由 401 拦截测试（HTTP）
# ──────────────────────────────────────────────

class TestProtectedRoutes:
    """验证业务路由在无 token 时返回 401，health 路由不受影响。"""

    PROTECTED = [
        "/api/v1/actors/",
        "/api/v1/films/",
        "/api/v1/customers/",
        "/api/v1/rentals/",
    ]

    def test_actors_without_token(self, auth_client):
        assert auth_client.get("/api/v1/actors/").status_code == 401

    def test_films_without_token(self, auth_client):
        assert auth_client.get("/api/v1/films/").status_code == 401

    def test_customers_without_token(self, auth_client):
        assert auth_client.get("/api/v1/customers/").status_code == 401

    def test_rentals_without_token(self, auth_client):
        assert auth_client.get("/api/v1/rentals/").status_code == 401

    def test_invalid_token_rejected(self, auth_client):
        resp = auth_client.get(
            "/api/v1/actors/",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert resp.status_code == 401

    def test_valid_token_passes_auth(self, auth_client):
        """有效 token 可通过认证校验（路由本身可能因 SQLite 无数据返回其他码，但不是 401）。"""
        auth_client.post("/api/v1/auth/register", json={
            "username": "token_pass",
            "email": "tokenpass@example.com",
            "password": "pass12345",
        })
        login = auth_client.post("/api/v1/auth/login", json={
            "username": "token_pass",
            "password": "pass12345",
        })
        token = login.json()["data"]["access_token"]

        resp = auth_client.get(
            "/api/v1/actors/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code != 401

    def test_health_no_auth_required(self, auth_client):
        """health 接口无需 token。"""
        resp = auth_client.get("/api/v1/health/")
        assert resp.status_code != 401

    def test_post_without_token_rejected(self, auth_client):
        """POST 操作无 token 同样返回 401。"""
        resp = auth_client.post(
            "/api/v1/actors/",
            json={"first_name": "Tom", "last_name": "Hanks"},
        )
        assert resp.status_code == 401
