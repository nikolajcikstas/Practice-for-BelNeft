import subprocess
import sys
import time

from sqlalchemy import inspect, text

import app.models  # noqa: F401
from app.database import Base, engine


def _apply_schema() -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "employees" not in tables:
        Base.metadata.create_all(bind=engine)
        return

    col_info = {c["name"]: c for c in inspector.get_columns("employees")}

    with engine.begin() as conn:
        if "middle_name" not in columns:
            conn.execute(text("ALTER TABLE employees ADD COLUMN middle_name VARCHAR(100)"))

        conn.execute(text("""
            UPDATE employees
            SET middle_name = position, position = NULL
            WHERE (middle_name IS NULL OR TRIM(middle_name) = '')
              AND position IS NOT NULL AND TRIM(position) != ''
        """))
        conn.execute(text("""
            UPDATE employees SET middle_name = '—'
            WHERE middle_name IS NULL OR TRIM(middle_name) = ''
        """))

        if col_info.get("middle_name", {}).get("nullable", True):
            conn.execute(text("ALTER TABLE employees ALTER COLUMN middle_name SET NOT NULL"))
        if col_info.get("position") and not col_info["position"].get("nullable", True):
            conn.execute(text("ALTER TABLE employees ALTER COLUMN position DROP NOT NULL"))


def _sync_alembic() -> None:
    subprocess.run(["alembic", "stamp", "head"], check=False)


def ensure_schema(retries: int = 10, delay: int = 5) -> None:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            _apply_schema()
            try:
                subprocess.run(["alembic", "upgrade", "head"], check=False)
            except Exception:
                pass
            _sync_alembic()
            return
        except Exception as exc:
            last_error = exc
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
