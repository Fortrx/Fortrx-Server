#!/bin/sh
set -eu

echo "Running migrations..."
alembic -c /app/alembic.ini upgrade head

echo "Starting app..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --proxy-headers \
  --forwarded-allow-ips='*'
