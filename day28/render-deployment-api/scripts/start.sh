
#!/usr/bin/env bash
set -e

echo "Applying database migrations..."
uv run --no-sync alembic upgrade head

echo "Starting FastAPI..."
exec uv run --no-sync uvicorn render_deployment_api.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-10000}"
