from sqlalchemy import inspect, text

from app.database import engine


def ensure_schema() -> None:
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "employees" not in tables:
        from app.init_db import init_db
        init_db()
        return

    columns = {col["name"] for col in inspector.get_columns("employees")}
    patches: list[str] = []

    if "middle_name" not in columns:
        patches.append("ALTER TABLE employees ADD COLUMN middle_name VARCHAR(100)")

    if not patches:
        return

    with engine.begin() as conn:
        for sql in patches:
            conn.execute(text(sql))
