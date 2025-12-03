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
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
      ┌───────────────┐           ┌───────────────┐
      │  Prometheus   │◄──────────│    Loki       │
      │   (9090)      │           │   (3100)      │
      └───────────────┘           └───────────────┘
                                          ▲
                                          │
                                  ┌───────────────┐
                                  │   Promtail    │
                                  │ (log shipper) │
                                  └───────────────┘
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

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/delcaux-labs/deepfix.git
cd deepfix

# Copy environment template
cp deepfix-server/.env.example deepfix-server/.env

# Edit with your configuration
nano deepfix-server/.env
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

### Prometheus

Metrics collection with:
- 15-second scrape interval
- 15-day retention
- Alerting rules for service health

### Grafana

Visualization dashboard with:
- Pre-configured data sources (Prometheus, Loki)
- DeepFix server dashboard
- Alert notifications

### Loki + Promtail

Log aggregation:
- Promtail collects Docker container logs
- Loki stores and indexes logs
- 7-day retention by default

---

## Configuration

### Environment Variables

Create `deepfix-server/.env` with the following:

```bash
# Required - LLM Configuration
DEEPFIX_LLM_API_KEY=sk-your-api-key
DEEPFIX_LLM_BASE_URL=https://api.openai.com/v1
DEEPFIX_LLM_MODEL_NAME=gpt-4o
DEEPFIX_LLM_TEMPERATURE=0.4
DEEPFIX_LLM_MAX_TOKENS=6000
DEEPFIX_LLM_CACHE=true
DEEPFIX_LLM_TRACK_USAGE=true

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXP_NAME=deepfix-production

# Optional - Pinggy Tunnel (for remote access)
# PINGGY_SSH_USER=your-pinggy-user
```

### Resource Limits

Configured in `docker-compose.prod.yml`:

| Service        | CPU Limit | Memory Limit |
|----------------|-----------|--------------|
| deepfix-server | 2 cores   | 4 GB         |
| mlflow         | 0.5 cores | 512 MB       |
| traefik        | 0.5 cores | 256 MB       |
| prometheus     | 0.5 cores | 512 MB       |
| grafana        | 0.5 cores | 512 MB       |
| loki           | 0.5 cores | 512 MB       |
| promtail       | 0.25 cores| 128 MB       |

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

### Access Grafana

- URL: `https://your-domain/grafana` or `http://localhost:3000`
- Default credentials: `admin` / `admin` (change on first login)

### Pre-configured Dashboards

1. **DeepFix Overview**: Request rates, latencies, error rates
2. **System Metrics**: CPU, memory, disk usage
3. **Logs**: Live log streaming from all services

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

**Via Grafana:**
1. Navigate to Explore
2. Select "Loki" data source
3. Query: `{container_name="deepfix-server"}`

### Log Retention

Default: 7 days

Modify in `monitoring/loki-config.yml`:
```yaml
limits_config:
  retention_period: 168h  # 7 days
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

### Backup

**Data to backup:**
- `server_mlflow_data/`: MLflow experiments and artifacts
- `server_logs/`: Application logs
- `monitoring/data/`: Prometheus metrics (optional)

**Backup script:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/deepfix-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Stop services for consistent backup
docker compose -f docker-compose.prod.yml stop

# Backup volumes
tar -czf $BACKUP_DIR/mlflow.tar.gz server_mlflow_data/
tar -czf $BACKUP_DIR/logs.tar.gz server_logs/

# Restart services
docker compose -f docker-compose.prod.yml start
```

### Log Rotation

Docker daemon handles log rotation. Configure in `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
```

### Health Checks

Manual health verification:

```bash
# DeepFix server
curl -f http://localhost:8844/health

# MLflow
curl -f http://localhost:5000/health

# Prometheus
curl -f http://localhost:9090/-/healthy

# Grafana
curl -f http://localhost:3000/api/health
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

#### Connection Refused

```bash
# Verify service is running
docker compose -f docker-compose.prod.yml ps

# Check Traefik routing
docker compose -f docker-compose.prod.yml logs traefik

# Test internal connectivity
docker compose -f docker-compose.prod.yml exec traefik \
  wget -q -O- http://deepfix-server:8844/health
```

#### Certificate Issues

```bash
# Check certificate validity
openssl s_client -connect localhost:443 -servername deepfix.local

# Regenerate certificates
./scripts/generate-certs.sh
```

### Debug Mode

Enable debug logging:

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Restart service
docker compose -f docker-compose.prod.yml restart deepfix-server
```

### Support

- Documentation: https://deepfix.delcaux.com/docs
- Issues: https://github.com/delcaux-labs/deepfix/issues

---

## File Structure

```
deepfix/
├── docker-compose.prod.yml      # Production compose file
├── Dockerfile                   # Server image definition
├── start_server_docker.sh       # Server startup script
├── .env                         # Environment configuration
├── traefik/
│   ├── traefik.yml              # Traefik static config
│   ├── dynamic/
│   │   └── config.yml           # Traefik dynamic config
│   └── certs/
│       ├── server.crt           # TLS certificate
│       └── server.key           # TLS private key
├── monitoring/
│   ├── prometheus.yml           # Prometheus config
│   ├── loki-config.yml          # Loki config
│   ├── promtail-config.yml      # Promtail config
│   └── grafana/
│       └── provisioning/        # Grafana auto-provisioning
├── scripts/
│   └── deploy.sh                # Zero-downtime deploy script
├── server_logs/                 # Mounted log volume
└── server_mlflow_data/          # Mounted MLflow volume
```

