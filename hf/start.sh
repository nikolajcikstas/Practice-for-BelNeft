#!/bin/sh

echo "=== Portal startup ==="

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set."
  echo "Add it in HF Space -> Settings -> Variables and secrets"
  exit 1
fi

cd /app

echo "Initializing database..."
if alembic upgrade head; then
  echo "Alembic migrations applied."
else
  echo "Alembic failed, trying create_all fallback..."
  python -m app.init_db || {
    echo "ERROR: cannot connect to database. Check DATABASE_URL from Neon."
    exit 1
  }
fi

echo "Starting nginx + uvicorn..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/app.conf
