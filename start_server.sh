#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LOG_FILE="server.log"

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARN:${NC} $1" | tee -a "$LOG_FILE"
}

# Cleanup on exit
cleanup() {
    log "Shutting down..."
    pkill -P $$ ssh
    docker compose down
    log "Cleanup complete"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Load environment variables
set -a
[ -f .env ] && source .env
set +a

# Validate required environment variables
if [ -z "$PINGGY_SSH_USER" ]; then
    error "PINGGY_SSH_USER not set in .env"
    exit 1
fi

log "Starting DeepFix server..."

# Start Docker
log "Starting Docker container..."
docker compose up > docker.log 2>&1 &
DOCKER_PID=$!

# Wait for Docker to be ready (max 30 seconds)
for i in {1..30}; do
    if docker compose ps | grep -q "healthy\|running"; then
        log "Docker container is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        error "Docker container failed to start"
        exit 1
    fi
    sleep 1
done

log "Starting SSH tunnel to Pinggy..."

# SSH tunnel loop with exponential backoff
RETRY_COUNT=0
MAX_RETRIES=5
BACKOFF=5

while true; do
    # Check if Docker container is still running
    if ! docker compose ps | grep -q "healthy\|running"; then
        error "Docker container is not running. Restarting..."
        docker compose up > docker.log 2>&1 &
    fi
    
    # Attempt SSH tunnel
    log "Connecting to Pinggy (attempt $((RETRY_COUNT+1)))..."
    ssh -p 443 \
        -R0:localhost:8844 \
        -o StrictHostKeyChecking=accept-new \
        -o ServerAliveInterval=30 \
        -o ServerAliveCountMax=3 \
        -o ConnectTimeout=10 \
        "$PINGGY_SSH_USER@pro.pinggy.io"
    
    SSH_EXIT_CODE=$?
    
    if [ $SSH_EXIT_CODE -eq 0 ]; then
        # Successful connection that was cleanly closed
        log "SSH tunnel disconnected (exit code: $SSH_EXIT_CODE)"
        RETRY_COUNT=0
        BACKOFF=5
    else
        # Connection failed or abnormal disconnect
        error "SSH tunnel error (exit code: $SSH_EXIT_CODE)"
        RETRY_COUNT=$((RETRY_COUNT + 1))
        
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            error "Max retries reached. Exiting."
            cleanup
            exit 1
        fi
        
        warn "Reconnecting in ${BACKOFF}s (retry $RETRY_COUNT/$MAX_RETRIES)..."
        sleep $BACKOFF
        
        # Exponential backoff (5s, 10s, 20s, 40s, 80s)
        BACKOFF=$((BACKOFF * 2))
    fi
done