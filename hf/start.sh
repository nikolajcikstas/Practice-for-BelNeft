#!/bin/sh
set -e

echo "Running migrations..."
cd /app
alembic upgrade head
echo "Migrations done."

echo "Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/app.conf
