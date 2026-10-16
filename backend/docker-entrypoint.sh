#!/bin/sh
set -e

# Apply database migrations before serving traffic (set RUN_MIGRATIONS=false to skip).
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'
