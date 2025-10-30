#!/bin/bash

set -e

LOG_DIR="/logs"
MLFLOW_DATA_DIR="/mlflow"

echo "Starting MLflow server..."
mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:////$MLFLOW_DATA_DIR/mlflow.db --default-artifact-root $MLFLOW_DATA_DIR/artifacts \
    > "$LOG_DIR/mlflow.log" 2>&1 &

echo "Starting deepfix server..."
 deepfix-server launch -port 8844 -host 0.0.0.0 \
    -workers 2 -fast-queue > "$LOG_DIR/server.log" 2>&1