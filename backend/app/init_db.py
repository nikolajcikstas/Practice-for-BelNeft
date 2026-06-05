"""Создание таблиц при первом запуске (fallback если alembic недоступен)."""

import app.models  # noqa: F401
from app.database import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables ready.")
