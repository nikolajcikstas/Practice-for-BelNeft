#!/bin/sh

echo "=== Portal startup ==="

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set."
  exit 1
fi

cd /app

attempt=1
max_attempts=12
while [ "$attempt" -le "$max_attempts" ]; do
  echo "DB setup attempt $attempt/$max_attempts..."
  if python -m app.ensure_schema; then
    echo "Database ready."
    break
  fi
  if [ "$attempt" -eq "$max_attempts" ]; then
    echo "ERROR: database setup failed."
    exit 1
  fi
  sleep 5
  attempt=$((attempt + 1))
done

echo "Generating analytics reports..."
python -m app.analytics_service || echo "WARN: analytics generation failed"

echo "Starting nginx + uvicorn on port 7860..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/app.conf
