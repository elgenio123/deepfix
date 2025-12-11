#!/bin/bash
# Zero-Downtime Deployment Script for DeepFix Production
# Usage: ./scripts/deploy.sh [version] [--rollback]

set -e

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="deepfix-server"
HEALTH_ENDPOINT="http://localhost:8844/health"
MAX_RETRIES=30
RETRY_INTERVAL=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose v2 is not installed"
        exit 1
    fi

    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Get current image tag
get_current_image() {
    docker inspect --format='{{.Config.Image}}' "$SERVICE_NAME" 2>/dev/null || echo "none"
}

# Health check function
health_check() {
    local retries=0
    log_step "Waiting for service to become healthy..."

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            log_info "Health check passed"
            return 0
        fi

        retries=$((retries + 1))
        log_warn "Health check attempt $retries/$MAX_RETRIES failed, retrying in ${RETRY_INTERVAL}s..."
        sleep $RETRY_INTERVAL
    done

    log_error "Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Backup current state
backup_state() {
    local backup_dir="backups/$(date '+%Y%m%d_%H%M%S')"
    log_step "Creating backup in $backup_dir..."

    mkdir -p "$backup_dir"

    # Save current image info
    get_current_image > "$backup_dir/previous_image.txt"

    # Save docker-compose config
    docker compose -f "$COMPOSE_FILE" config > "$backup_dir/compose_config.yml"

    # Save container logs
    docker compose -f "$COMPOSE_FILE" logs "$SERVICE_NAME" > "$backup_dir/previous_logs.txt" 2>&1 || true

    log_info "Backup created: $backup_dir"
    echo "$backup_dir"
}

# Deploy new version
deploy() {
    local version=${1:-"latest"}
    log_step "Deploying version: $version"

    # Pull latest changes if version is latest
    if [ "$version" = "latest" ]; then
        log_info "Pulling latest code..."
        git pull origin main 2>/dev/null || log_warn "Git pull skipped (not a git repo or no changes)"
    fi

    # Build new image
    log_step "Building new image..."
    if [ "$version" != "latest" ]; then
        docker compose -f "$COMPOSE_FILE" build --build-arg VERSION="$version" "$SERVICE_NAME"
    else
        docker compose -f "$COMPOSE_FILE" build "$SERVICE_NAME"
    fi

    # Tag for rollback
    local current_image=$(get_current_image)
    if [ "$current_image" != "none" ]; then
        log_info "Tagging current image for potential rollback..."
        docker tag "$current_image" "${SERVICE_NAME}:rollback" 2>/dev/null || true
    fi

    # Rolling update
    log_step "Performing rolling update..."
    docker compose -f "$COMPOSE_FILE" up -d --no-deps --force-recreate "$SERVICE_NAME"

    # Health check
    if health_check; then
        log_info "Deployment successful!"

        # Cleanup old images
        log_step "Cleaning up old images..."
        docker image prune -f --filter "until=24h" > /dev/null 2>&1 || true

        return 0
    else
        log_error "Deployment failed - health check failed"
        return 1
    fi
}

# Rollback to previous version
rollback() {
    log_step "Initiating rollback..."

    # Check if rollback image exists
    if ! docker image inspect "${SERVICE_NAME}:rollback" &> /dev/null; then
        log_error "No rollback image available"

        # Try to find the latest backup
        local latest_backup=$(ls -td backups/*/ 2>/dev/null | head -1)
        if [ -n "$latest_backup" ] && [ -f "$latest_backup/previous_image.txt" ]; then
            local prev_image=$(cat "$latest_backup/previous_image.txt")
            log_info "Found previous image from backup: $prev_image"

            if docker image inspect "$prev_image" &> /dev/null; then
                docker tag "$prev_image" "${SERVICE_NAME}:rollback"
            else
                log_error "Previous image no longer exists"
                exit 1
            fi
        else
            exit 1
        fi
    fi

    # Perform rollback
    log_info "Rolling back to previous version..."
    docker compose -f "$COMPOSE_FILE" stop "$SERVICE_NAME"
    docker tag "${SERVICE_NAME}:rollback" "${SERVICE_NAME}:latest"
    docker compose -f "$COMPOSE_FILE" up -d --no-deps "$SERVICE_NAME"

    # Health check
    if health_check; then
        log_info "Rollback successful!"
        return 0
    else
        log_error "Rollback failed - service still unhealthy"
        return 1
    fi
}

# Show deployment status
status() {
    log_step "Deployment Status"
    echo ""

    echo -e "${BLUE}=== Services ===${NC}"
    docker compose -f "$COMPOSE_FILE" ps

    echo ""
    echo -e "${BLUE}=== Health Status ===${NC}"

    for service in deepfix-server mlflow traefik prometheus grafana loki; do
        if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
            local health=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "no healthcheck")
            case $health in
                "healthy")
                    echo -e "${GREEN}✓${NC} $service: $health"
                    ;;
                "unhealthy")
                    echo -e "${RED}✗${NC} $service: $health"
                    ;;
                *)
                    echo -e "${YELLOW}?${NC} $service: $health"
                    ;;
            esac
        else
            echo -e "${RED}✗${NC} $service: not running"
        fi
    done

    echo ""
    echo -e "${BLUE}=== Resource Usage ===${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | head -10 || true
}

# Main execution
main() {
    local command=${1:-"deploy"}
    local version=${2:-"latest"}

    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     DeepFix Production Deployment        ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""

    check_prerequisites

    case $command in
        deploy)
            backup_state
            deploy "$version"
            ;;
        --rollback|rollback)
            rollback
            ;;
        status)
            status
            ;;
        health)
            health_check
            ;;
        *)
            echo "Usage: $0 [deploy|rollback|status|health] [version]"
            echo ""
            echo "Commands:"
            echo "  deploy [version]  Deploy new version (default: latest)"
            echo "  rollback          Rollback to previous version"
            echo "  status            Show deployment status"
            echo "  health            Run health check"
            exit 1
            ;;
    esac
}

main "$@"
