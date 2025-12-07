# DeepFix Server Production Deployment Guide

This document outlines the requirements and steps to deploy the DeepFix server in a production-grade environment using Docker Compose on a self-hosted server.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Requirements](#requirements)
4. [Quick Start](#quick-start)
5. [Components](#components)
6. [Configuration](#configuration)
7. [Deployment](#deployment)
8. [Monitoring & Alerting](#monitoring--alerting)
9. [Logging](#logging)
10. [Security](#security)
11. [Maintenance](#maintenance)
12. [Troubleshooting](#troubleshooting)

---

## Overview

This production deployment provides:

- **Reverse Proxy**: Traefik for TLS termination, rate limiting, and load balancing
- **Monitoring**: Prometheus + Grafana for metrics collection and visualization
- **Centralized Logging**: Loki + Promtail for log aggregation
- **Security**: Non-root containers, network isolation, secrets management
- **Zero-Downtime Deployments**: Rolling update scripts with health checks

## Architecture

```
                         Internet
                            │
                            ▼
              ┌─────────────────────────────┐
              │      Traefik (443/80)       │
              │  - TLS termination          │
              │  - Rate limiting            │
              │  - Health-based routing     │
              └─────────────┬───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ DeepFix Server│   │    MLflow     │   │   Grafana     │
│  (8844)       │   │   (5000)      │   │   (3000)      │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
```

## Requirements

### Hardware (Minimum)

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU      | 2 cores | 4 cores     |
| RAM      | 4 GB    | 8 GB        |
| Disk     | 20 GB   | 50 GB SSD   |

### Software

- Docker Engine 24.0+
- Docker Compose v2.20+
- OpenSSL (for certificate generation)
- curl (for health checks)

### Network

- Ports 80 and 443 open for HTTP/HTTPS traffic
- Port 22 for SSH access (management)
- Outbound access to LLM API endpoints

---

## Quick Start

### 1. Configure Environment

```bash
# Copy environment template and edit with your LLM API credentials
cp deepfix-server/.env.example deepfix-server/.env
```

### 2. Generate TLS Certificates

For production, use Let's Encrypt or your organization's CA. For testing:

```bash
# Create certificates directory
mkdir -p traefik/certs

# Generate self-signed certificate (testing only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout traefik/certs/server.key \
  -out traefik/certs/server.crt \
  -subj "/CN=deepfix.local"
```

### 3. Start Production Stack

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### 4. Verify Deployment

```bash
# Health check
curl -k https://localhost/health

# API info
curl -k https://localhost/info
```

---

## Components

### DeepFix Server

The core ML artifact analysis service running on port 8844 internally.

**Configuration:**
- Workers: 2 (configurable via `start_server_docker.sh`)
- Fast queue: enabled
- Health endpoint: `/health`

### MLflow

Experiment tracking server for logging DSPy traces and metrics.

**Configuration:**
- Backend: SQLite (production may use PostgreSQL)
- Artifact store: Local filesystem (`/mlflow/artifacts`)
- UI: Available at `/mlflow` path

### Traefik (Reverse Proxy)

Handles incoming traffic with:
- Automatic HTTPS redirect
- TLS termination
- Rate limiting (100 requests/minute per IP)
- Health-based load balancing


---

## Configuration

### Environment Variables

See `deepfix-server/.env.example` for all available options. Key production settings:

```bash
# MLflow Configuration
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_EXP_NAME=deepfix-production
```

### Resource Limits

Configured in `docker-compose.prod.yml`:

| Service        | CPU Limit | Memory Limit |
|----------------|-----------|--------------|
| deepfix-server | 2 cores   | 4 GB         |
| mlflow         | 0.5 cores | 512 MB       |
| traefik        | 0.5 cores | 256 MB       |

### Rate Limiting

Default: 100 requests per minute per IP address.

Modify in `traefik/traefik.yml`:

```yaml
middlewares:
  rate-limit:
    rateLimit:
      average: 100
      burst: 50
      period: 1m
```

---

## Deployment

### Initial Deployment

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d

# Verify all services are healthy
docker compose -f docker-compose.prod.yml ps
```

### Zero-Downtime Updates

Use the provided deployment script:

```bash
# Deploy new version
./scripts/deploy.sh

# Deploy with specific image tag
./scripts/deploy.sh v1.2.0

# Rollback to previous version
./scripts/deploy.sh --rollback
```

The script performs:
1. Pulls/builds new image
2. Starts new container alongside old one
3. Waits for health check to pass
4. Switches traffic to new container
5. Stops old container
6. Cleans up old images

### Manual Rolling Update

```bash
# Pull latest changes
git pull origin main

# Rebuild specific service
docker compose -f docker-compose.prod.yml build deepfix-server

# Rolling update (zero-downtime)
docker compose -f docker-compose.prod.yml up -d --no-deps deepfix-server
```

---

## Monitoring & Alerting


### Alert Rules

Prometheus alerts configured in `monitoring/prometheus.yml`:

| Alert | Condition | Severity |
|-------|-----------|----------|
| ServiceDown | Service unreachable for 1m | critical |
| HighErrorRate | Error rate > 5% for 5m | warning |
| HighLatency | p95 latency > 10s for 5m | warning |
| DiskSpaceLow | Disk usage > 80% | warning |

### Notification Channels

Configure in Grafana UI:
- Email
- Slack
- PagerDuty
- Webhook

---

## Logging

### View Logs

**Via Docker:**
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f deepfix-server
```

### Log Levels

Set via environment variable:
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

---

## Security

### Container Security

- **Non-root user**: All containers run as non-root
- **Read-only filesystem**: Where possible
- **No privileged mode**: Unless explicitly required
- **Resource limits**: Prevent resource exhaustion

### Network Security

- **Internal network**: Services communicate on isolated network
- **No exposed ports**: Only Traefik exposes 80/443
- **TLS everywhere**: All external traffic encrypted

### Secrets Management

For production, use Docker secrets:

```bash
# Create secrets
echo "your-api-key" | docker secret create deepfix_llm_api_key -

# Reference in compose
services:
  deepfix-server:
    secrets:
      - deepfix_llm_api_key
```

### Firewall Rules

Recommended iptables/ufw rules:

```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable
```

---

## Maintenance

### Health Checks

Manual health verification:

```bash
# DeepFix server
curl -f http://localhost:8844/health

# MLflow
curl -f http://localhost:5000/health

```

### Updates

```bash
# Update all images
docker compose -f docker-compose.prod.yml pull

# Recreate containers
docker compose -f docker-compose.prod.yml up -d

# Prune old images
docker image prune -f
```

---

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs deepfix-server

# Check container status
docker inspect deepfix-server

# Verify environment variables
docker compose -f docker-compose.prod.yml config
```

#### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart specific service
docker compose -f docker-compose.prod.yml restart deepfix-server
```

#### Certificate Issues

```bash
# Check certificate validity
openssl s_client -connect localhost:443 -servername deepfix.local

# Regenerate certificates
./scripts/generate-certs.sh
```

