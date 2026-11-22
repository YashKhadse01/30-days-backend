
#!/usr/bin/env bash
set -e

echo "Installing uv..."
python -m pip install uv

echo "Installing production dependencies..."
uv sync --locked --no-dev

echo "Build completed successfully."
