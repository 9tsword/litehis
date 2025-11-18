from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import settings


# 依据配置构建数据库引擎；当使用 SQLite 时需关闭线程检查以便在 FastAPI 中复用连接
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)


def init_db() -> None:
    """根据 SQLModel 元数据自动创建数据表。"""

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """提供数据库会话给 FastAPI 依赖注入使用。"""

    # 使用上下文管理器保证请求结束后自动关闭会话，防止连接泄漏
    with Session(engine) as session:
        yield session
