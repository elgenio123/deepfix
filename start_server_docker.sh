#!/bin/bash

set -e

LOG_DIR="/logs"
MLFLOW_DATA_DIR="/mlflow"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/server.log"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_DIR/server.log"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARN:${NC} $1" | tee -a "$LOG_DIR/server.log"
}

#echo "Starting MLflow server..."
#mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:////$MLFLOW_DATA_DIR/mlflow.db --default-artifact-root $MLFLOW_DATA_DIR/artifacts \
#    > "$LOG_DIR/mlflow.log" 2>&1 &

echo "Starting deepfix server..."
deepfix-server launch -port 8844 -host 0.0.0.0 \
    -workers 2 -fast-queue > "$LOG_DIR/server.log" 2>&1 &

# If PINGGY_SSH_USER is set, establish SSH tunnel to Pinggy
if [ -n "$PINGGY_SSH_USER" ]; then
    log "PINGGY_SSH_USER is set, establishing Pinggy tunnel..."
    ssh -p 443 \
        -R0:localhost:8844 \
        -o StrictHostKeyChecking=accept-new \
        -o ServerAliveInterval=30 \
        -o ServerAliveCountMax=3 \
        -o ConnectTimeout=10 \
        "$PINGGY_SSH_USER@pro.pinggy.io"
else
    log "PINGGY_SSH_USER not set, skipping Pinggy tunnel..."
    # Keep the container running
    wait
fi

