# Docker Deployment

This guide covers deploying DeepFix using Docker and Docker Compose for containerized deployment.

## Overview

Docker deployment provides a consistent, isolated environment for DeepFix. This is recommended for server deployment in production or development environments.

## Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Install Docker Compose](https://docs.docker.com/compose/install/))
- Docker daemon running

## Quick Start

### Step 1: Clone Repository

```bash
git clone https://github.com/delcaux-labs/deepfix.git
cd deepfix
```

### Step 2: Configure Environment

```bash
# Copy environment example
cp env.example .env

# Edit .env with your configuration
# - Set LLM API credentials
# - Configure server settings
# - Set MLflow tracking URI (if using external MLflow)
```

### Step 3: Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Or using Make (if available)
make docker-compose-up

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Docker Compose Configuration

### Default docker-compose.yml

The default `docker-compose.yml` typically includes:

```yaml
version: '3.8'

services:
  deepfix-server:
    build: .
    ports:
      - "8844:8844"
    environment:
      - DEEPFIX_LLM_API_KEY=${DEEPFIX_LLM_API_KEY}
      - DEEPFIX_LLM_BASE_URL=${DEEPFIX_LLM_BASE_URL}
      - DEEPFIX_LLM_MODEL_NAME=${DEEPFIX_LLM_MODEL_NAME}
      - DEEPFIX_LLM_TEMPERATURE=${DEEPFIX_LLM_TEMPERATURE}
      - DEEPFIX_LLM_MAX_TOKENS=${DEEPFIX_LLM_MAX_TOKENS}
      - MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-http://mlflow:5000}
    volumes:
      - ./mlruns:/app/mlruns
      - ./server_logs:/app/logs
    depends_on:
      - mlflow

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    command: >
      mlflow server
      --backend-store-uri sqlite:///mlflow.db
      --default-artifact-root /mlruns
      --host 0.0.0.0
      --port 5000
    volumes:
      - ./mlruns:/mlruns
      - ./mlflow.db:/mlflow.db
```

### Custom Configuration

Customize `docker-compose.yml` for your needs:

```yaml
version: '3.8'

services:
  deepfix-server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${DEEPFIX_PORT:-8844}:8844"
    environment:
      # LLM Configuration
      - DEEPFIX_LLM_API_KEY=${DEEPFIX_LLM_API_KEY}
      - DEEPFIX_LLM_BASE_URL=${DEEPFIX_LLM_BASE_URL}
      - DEEPFIX_LLM_MODEL_NAME=${DEEPFIX_LLM_MODEL_NAME}
      - DEEPFIX_LLM_TEMPERATURE=${DEEPFIX_LLM_TEMPERATURE}
      - DEEPFIX_LLM_MAX_TOKENS=${DEEPFIX_LLM_MAX_TOKENS}
      - DEEPFIX_LLM_CACHE=${DEEPFIX_LLM_CACHE:-true}

      # Server Configuration
      - DEEPFIX_HOST=${DEEPFIX_HOST:-0.0.0.0}
      - DEEPFIX_PORT=${DEEPFIX_PORT:-8844}

      # MLflow Configuration
      - MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-http://mlflow:5000}
    volumes:
      - ./mlruns:/app/mlruns
      - ./server_logs:/app/logs
      - ./documents:/app/documents  # Knowledge base
    depends_on:
      - mlflow
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8844/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Dockerfile

### Example Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY deepfix-server/ ./deepfix-server/
COPY deepfix-core/ ./deepfix-core/
COPY deepfix-kb/ ./deepfix-kb/

# Install dependencies
RUN uv pip install --system -e ./deepfix-core
RUN uv pip install --system -e ./deepfix-kb
RUN uv pip install --system -e ./deepfix-server

# Expose port
EXPOSE 8844

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8844/health || exit 1

# Run server
CMD ["deepfix-server", "launch", "--host", "0.0.0.0", "--port", "8844"]
```

## Environment Variables

Configure DeepFix via environment variables:

### Required Variables

```bash
# LLM Configuration
DEEPFIX_LLM_API_KEY=sk-...
DEEPFIX_LLM_BASE_URL=https://api.your-llm.com/v1
DEEPFIX_LLM_MODEL_NAME=gpt-4o
```

### Optional Variables

```bash
# LLM Settings
DEEPFIX_LLM_TEMPERATURE=0.4
DEEPFIX_LLM_MAX_TOKENS=6000
DEEPFIX_LLM_CACHE=true
DEEPFIX_LLM_TRACK_USAGE=true

# Server Settings
DEEPFIX_HOST=0.0.0.0
DEEPFIX_PORT=8844

# MLflow Settings
MLFLOW_TRACKING_URI=http://mlflow:5000

# Logging
LOG_LEVEL=INFO
```

## Deployment Scenarios

### Development Deployment

```bash
# Use docker-compose for local development
docker-compose up

# Mount source code for development
docker-compose -f docker-compose.dev.yml up
```

### Production Deployment

```bash
# Build production image
docker build -t deepfix-server:latest .

# Run with production settings
docker run -d \
  --name deepfix-server \
  -p 8844:8844 \
  --env-file .env.production \
  -v ./mlruns:/app/mlruns \
  deepfix-server:latest
```

### Multi-Container Deployment

Deploy with MLflow and other services:

```bash
# Start all services
docker-compose up -d deepfix-server mlflow

# Check status
docker-compose ps

# View logs
docker-compose logs -f deepfix-server
```

## Networking

### Internal Network

Services communicate via Docker network:

```yaml
networks:
  deepfix-network:
    driver: bridge

services:
  deepfix-server:
    networks:
      - deepfix-network

  mlflow:
    networks:
      - deepfix-network
```

### External Access

Expose services to host:

```yaml
services:
  deepfix-server:
    ports:
      - "8844:8844"  # Host:Container
```

## Volumes

### Persistent Storage

Map volumes for persistent data:

```yaml
volumes:
  mlruns-data:
    driver: local

  mlflow-db:
    driver: local

services:
  deepfix-server:
    volumes:
      - mlruns-data:/app/mlruns

  mlflow:
    volumes:
      - mlruns-data:/mlruns
      - mlflow-db:/mlflow.db
```

### Local Development

Mount local directories:

```yaml
services:
  deepfix-server:
    volumes:
      - ./mlruns:/app/mlruns
      - ./server_logs:/app/logs
      - ./documents:/app/documents
```

## Health Checks

### Container Health Check

```yaml
services:
  deepfix-server:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8844/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Verify Health

```bash
# Check container health
docker ps

# Check health endpoint
curl http://localhost:8844/health

# View health logs
docker-compose logs deepfix-server | grep health
```

## Monitoring

### Logs

```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# View specific service
docker-compose logs deepfix-server

# View last 100 lines
docker-compose logs --tail=100 deepfix-server
```

### Resource Usage

```bash
# View container stats
docker stats

# View specific container
docker stats deepfix-server

# View resource limits
docker inspect deepfix-server | grep -A 10 Resources
```

## Troubleshooting

### Common Issues

**Problem**: Container fails to start

```bash
# Check logs
docker-compose logs deepfix-server

# Check environment variables
docker-compose config

# Verify .env file
cat .env
```

**Problem**: Port already in use

```bash
# Change port in docker-compose.yml
ports:
  - "8845:8844"  # Use different host port

# Or stop conflicting service
docker stop <container-name>
```

**Problem**: Cannot connect to MLflow

```bash
# Verify MLflow service is running
docker-compose ps mlflow

# Check network connectivity
docker-compose exec deepfix-server curl http://mlflow:5000

# Verify MLFLOW_TRACKING_URI
docker-compose exec deepfix-server env | grep MLFLOW
```

**Problem**: Out of memory

```bash
# Limit memory in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
    reservations:
      memory: 2G
```

### Debugging

```bash
# Enter container
docker-compose exec deepfix-server bash

# Check environment
docker-compose exec deepfix-server env

# Check network
docker-compose exec deepfix-server ping mlflow

# View process list
docker-compose exec deepfix-server ps aux
```

## Security

### Best Practices

1. **Use Secrets**: Store sensitive data in Docker secrets or environment files
2. **Limit Network**: Use internal networks where possible
3. **Update Images**: Regularly update base images
4. **Scan Images**: Scan images for vulnerabilities

```yaml
# Use secrets for sensitive data
secrets:
  llm_api_key:
    file: ./secrets/llm_api_key.txt

services:
  deepfix-server:
    secrets:
      - llm_api_key
    environment:
      - DEEPFIX_LLM_API_KEY_FILE=/run/secrets/llm_api_key
```

## Scaling

### Horizontal Scaling

```bash
# Scale server instances
docker-compose up -d --scale deepfix-server=3

# Use load balancer
# Configure nginx or traefik as load balancer
```

### Resource Limits

```yaml
services:
  deepfix-server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Next Steps

- [Local Setup](local-setup.md) - Set up local development environment
- [Configuration Guide](../getting-started/configuration.md) - Configure DeepFix
- [Architecture Overview](../architecture/overview.md) - Understand system architecture
