from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import settings


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)


def init_db() -> None:
    """Create database tables based on SQLModel metadata."""

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """Yield a database session for FastAPI dependency injection."""

    with Session(engine) as session:
        yield session
