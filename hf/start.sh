#!/bin/sh

echo "=== Portal startup ==="

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set."
  echo "Add it in HF Space -> Settings -> Variables and secrets"
  exit 1
fi

cd /app

echo "Running database migrations..."
attempt=1
max_attempts=10
while [ "$attempt" -le "$max_attempts" ]; do
  echo "Migration attempt $attempt/$max_attempts..."
  if alembic upgrade head; then
    echo "Migrations applied."
    break
  fi
  if [ "$attempt" -eq "$max_attempts" ]; then
    echo "ERROR: migrations failed after $max_attempts attempts."
    echo "Check DATABASE_URL in HF secrets."
    exit 1
  fi
  sleep 5
  attempt=$((attempt + 1))
done

echo "Starting nginx + uvicorn on port 7860..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/app.conf
