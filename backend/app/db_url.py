import os


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if "sslmode=" not in url and ("neon.tech" in url or "neon.db" in url):
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


def get_database_url() -> str:
    raw = os.getenv("DATABASE_URL", "postgresql://portal:portal@db:5432/portal")
    return normalize_database_url(raw)
