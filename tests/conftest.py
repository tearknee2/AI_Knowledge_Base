# 测试夹具：用 SQLite 内存库替代 MySQL，TestClient 通过 dependency_overrides
# 复用同一个会话，让"路由 -> 服务 -> 仓储 -> ORM"全链路跑在内存库上。
# 注意：内存库跨线程（TestClient 的 portal 线程）必须用 StaticPool 共享唯一连接，
# 否则每个线程各拿一个空库，报"表不存在"。
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.models.user import User
# 显式导入全部模型模块，确保表都注册到 Base.metadata
import app.models.user  # noqa: F401
import app.models.knowledge_base  # noqa: F401
import app.models.document  # noqa: F401
import app.models.conversation  # noqa: F401
import app.models.message  # noqa: F401


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    session = sessionmaker(
        bind=db_engine,
        autocommit=False,
        autoflush=False,
    )()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def api_client(db_session):
    from app.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def seed_user(db_session):
    """为需要认证的API测试准备用户；测试请求需通过登录或覆盖，get_current_user注入身份"""
    user = User(id=1, username="tester", password_hash="test-hash")
    db_session.add(user)
    db_session.commit()
    return user
