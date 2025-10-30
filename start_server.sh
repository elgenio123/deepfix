#!/bin/bash

set -e  # Exit on error

# Configuration
ENV_FILE="deepfix-server/.env"
LOG_DIR="logs"

# Create logs directory
mkdir -p "$LOG_DIR"

# Cleanup function
cleanup() {
    echo "Shutting down services..."
    jobs -p | xargs -r kill 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Check if env file exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

echo "Starting MLflow server..."
uv run deepfix-sdk launch-mlflow -port 5000 -host 0.0.0.0 \
    > "$LOG_DIR/mlflow.log" 2>&1 &

echo "Starting deepfix server..."
uv run deepfix-server launch -e "$ENV_FILE" -port 8844 -host 0.0.0.0 \
    -workers 2 -fast-queue > "$LOG_DIR/server.log" 2>&1 &

echo "Starting SSH tunnel..."
ssh -p 443 -R0:localhost:8844 a.pinggy.io