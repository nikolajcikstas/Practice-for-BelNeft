#!/bin/sh

echo "=== Portal startup ==="

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set."
  echo "Add it in HF Space -> Settings -> Variables and secrets"
  exit 1
fi

cd /app

echo "Initializing database (Neon may need a few seconds to wake up)..."
attempt=1
max_attempts=10
while [ "$attempt" -le "$max_attempts" ]; do
  echo "DB init attempt $attempt/$max_attempts..."
  if alembic upgrade head; then
    echo "Alembic migrations applied."
    break
  fi
  if python -m app.init_db; then
    echo "Tables created via create_all."
    break
  fi
  if [ "$attempt" -eq "$max_attempts" ]; then
    echo "ERROR: cannot connect to database after $max_attempts attempts."
    echo "Check DATABASE_URL in HF secrets (copy full string from Neon -> Connection string)."
    exit 1
  fi
  sleep 5
  attempt=$((attempt + 1))
done

echo "Starting nginx + uvicorn on port 7860..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/app.conf
