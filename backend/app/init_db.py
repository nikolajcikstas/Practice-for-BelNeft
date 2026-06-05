"""Создание таблиц при первом запуске."""

import sys
import time

import app.models  # noqa: F401
from app.database import Base, engine


def init_db(retries: int = 3, delay: int = 3) -> None:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(delay)
    raise last_error  # type: ignore[misc]


if __name__ == "__main__":
    try:
        init_db(retries=5, delay=4)
        print("Database tables ready.")
    except Exception as exc:
        print(f"init_db failed: {exc}", file=sys.stderr)
        sys.exit(1)
