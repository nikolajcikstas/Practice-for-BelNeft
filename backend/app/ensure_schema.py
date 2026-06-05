import subprocess
import sys
import time

from sqlalchemy import inspect, text

import app.models  # noqa: F401
from app.database import Base, engine


def _run(conn, sql: str) -> None:
    conn.execute(text(sql))


def _apply_schema() -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "employees" not in tables:
        Base.metadata.create_all(bind=engine)
        return

    col_info = {c["name"]: c for c in inspector.get_columns("employees")}

    with engine.begin() as conn:
        if "middle_name" not in col_info:
            _run(conn, "ALTER TABLE employees ADD COLUMN middle_name VARCHAR(100)")

        _run(conn, """
            UPDATE employees
            SET middle_name = TRIM(position), position = NULL
            WHERE (middle_name IS NULL OR TRIM(middle_name) = '')
              AND position IS NOT NULL AND TRIM(position) != ''
        """)

        _run(conn, """
            UPDATE employees SET middle_name = '—'
            WHERE middle_name IS NULL OR TRIM(middle_name) = ''
        """)

        _run(conn, """
            UPDATE employees SET
              last_name = TRIM(last_name),
              first_name = TRIM(first_name),
              middle_name = TRIM(middle_name),
              position = NULLIF(TRIM(position), '')
        """)

    try:
        with engine.begin() as conn:
            _run(conn, "ALTER TABLE employees ALTER COLUMN position DROP NOT NULL")
    except Exception:
        pass


def _sync_alembic() -> None:
    subprocess.run(["alembic", "stamp", "head"], check=False, cwd="/app")


def ensure_schema(retries: int = 12, delay: int = 5) -> None:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            _apply_schema()
            subprocess.run(["alembic", "upgrade", "head"], check=False, cwd="/app")
            _sync_alembic()
            return
        except Exception as exc:
            last_error = exc
            err = str(exc).lower()
            if "already exists" in err or "does not exist" in err:
                try:
                    _sync_alembic()
                    return
                except Exception:
                    pass
            print(f"ensure_schema {attempt}/{retries}: {exc}", file=sys.stderr)
            if attempt < retries:
                time.sleep(delay)
    if last_error:
        raise last_error


if __name__ == "__main__":
    try:
        ensure_schema()
        print("Database ready.")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
