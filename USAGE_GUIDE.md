# DeepFix Production Setup - Usage Guide

Your DeepFix production environment is now running! Here's how to use it.

## 🌐 Access Points

### 1. DeepFix API Server
- **URL**: `https://localhost/` or `http://localhost/` (auto-redirects to HTTPS)
- **API Endpoint**: `https://localhost/v1/analyse`
- **Purpose**: Main ML artifact analysis service

### 2. MLflow Experiment Tracking
- **URL**: `https://localhost/mlflow`
- **Purpose**: View DSPy traces, LLM calls, and experiment metrics
- **Features**:
  - View all analysis runs
  - Compare LLM performance
  - Track token usage and costs
  - Inspect agent decisions

### 3. Grafana Monitoring Dashboard
- **URL**: `https://localhost/grafana`
- **Username**: `admin`
- **Password**: `admin` (change on first login!)
- **Purpose**: Real-time monitoring and alerting
- **Features**:
  - System metrics (CPU, memory, disk)
  - API request rates and latencies
  - Error rates and health status
  - Log aggregation and search

### 4. Traefik Dashboard
- **URL**: `https://localhost/dashboard`
- **Username**: `admin`
- **Password**: `admin`
- **Purpose**: Reverse proxy management
- **Features**:
  - View active routes
  - Monitor TLS certificates
  - Check health checks
  - Rate limiting stats

## 🔐 Certificate Warning

You'll see a browser security warning because we're using self-signed certificates. This is normal for development/testing.

**To proceed:**
1. Click "Advanced" or "Show Details"
2. Click "Proceed to localhost (unsafe)" or "Accept Risk"

**For production**: Replace self-signed certificates with proper ones from Let's Encrypt or your organization's CA.

## 🧪 Testing the API

### Using curl (Command Line)

```bash
# Health check (from inside container)
docker exec deepfix-server curl http://localhost:8844/

# Test the analysis endpoint
curl -k -X POST https://localhost/v1/analyse \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d @examples/request_payload.json
```

### Using Python Client

```python
import requests
from deepfix_sdk import DeepFixClient

# Option 1: Direct API call
response = requests.post(
    "https://localhost/v1/analyse",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "dataset_artifacts": {
            "train_path": "path/to/train.csv",
            "test_path": "path/to/test.csv"
        },
        "dataset_name": "my_dataset",
        "language": "en"
    },
    verify=False  # Only for self-signed certs
)

# Option 2: Using SDK (recommended)
client = DeepFixClient(
    base_url="https://localhost",
    api_key="YOUR_API_KEY",
    verify_ssl=False  # Only for self-signed certs
)

results = client.analyse_artifacts(
    dataset_artifacts=dataset_artifacts,
    training_artifacts=training_artifacts
)
```

## 📊 Monitoring & Logs

### View Real-time Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f deepfix-server

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 deepfix-server
```

### View Logs in Grafana

1. Open Grafana: `https://localhost/grafana`
2. Go to "Explore" (compass icon in sidebar)
3. Select "Loki" as data source
4. Use queries like:
   ```
   {container_name="deepfix-server"}
   {container_name="deepfix-server"} |= "error"
   {container_name="deepfix-server"} |= "exception"
   ```

### Check Service Status

```bash
# View all services
docker compose -f docker-compose.prod.yml ps

# Check specific service health
docker inspect deepfix-server --format='{{.State.Health.Status}}'
```

## 📈 Using MLflow

### Access Experiment Tracking

1. Open MLflow UI: `https://localhost/mlflow`
2. You'll see all analysis runs listed
3. Click on any run to see:
   - Input parameters
   - LLM calls and prompts
   - Agent reasoning steps
   - Output predictions
   - Token usage and costs

### Query Runs via API

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")

# List experiments
experiments = mlflow.search_experiments()

# Get runs from experiment
runs = mlflow.search_runs(
    experiment_ids=["1"],
    filter_string="status = 'FINISHED'"
)

# Get specific run details
run = mlflow.get_run("run_id_here")
print(run.data.metrics)
print(run.data.params)
```

## 🔧 Common Operations

### Restart a Service

```bash
# Restart single service
docker compose -f docker-compose.prod.yml restart deepfix-server

# Restart all services
docker compose -f docker-compose.prod.yml restart
```

### Update DeepFix Server

```bash
# Pull latest code
git pull origin main

# Rebuild and deploy
docker compose -f docker-compose.prod.yml build deepfix-server
docker compose -f docker-compose.prod.yml up -d --no-deps deepfix-server

# Or use zero-downtime deployment script
./scripts/deploy.sh
```

### View Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats deepfix-server --no-stream
```

### Clean Up Old Images

```bash
# Remove unused images
docker image prune -f

# Remove stopped containers
docker container prune -f

# Remove unused volumes (careful!)
docker volume prune -f
```

## 🛑 Stopping Services

```bash
# Stop all services (keeps data)
docker compose -f docker-compose.prod.yml stop

# Stop and remove containers (keeps data)
docker compose -f docker-compose.prod.yml down

# Stop, remove containers, and delete volumes (⚠️ loses data)
docker compose -f docker-compose.prod.yml down -v
```

## 📦 Backup & Restore

### Backup Important Data

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup MLflow data
tar -czf backups/$(date +%Y%m%d)/mlflow.tar.gz server_mlflow_data/

# Backup logs
tar -czf backups/$(date +%Y%m%d)/logs.tar.gz server_logs/

# Backup Grafana dashboards
docker exec grafana grafana-cli admin export > backups/$(date +%Y%m%d)/grafana-backup.json
```

### Restore from Backup

```bash
# Stop services
docker compose -f docker-compose.prod.yml stop

# Restore MLflow data
tar -xzf backups/20250101/mlflow.tar.gz

# Restart services
docker compose -f docker-compose.prod.yml start
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
docker compose -f docker-compose.prod.yml logs deepfix-server

# Verify configuration
docker compose -f docker-compose.prod.yml config

# Check environment variables
docker compose -f docker-compose.prod.yml exec deepfix-server env | grep DEEPFIX
```

### Can't Access Web Interface

1. Check service is running: `docker compose -f docker-compose.prod.yml ps`
2. Check Traefik logs: `docker compose -f docker-compose.prod.yml logs traefik`
3. Verify ports are open: `netstat -an | findstr "80 443"`
4. Test internal connectivity:
   ```bash
   docker compose -f docker-compose.prod.yml exec traefik ping deepfix-server
   ```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart specific service
docker compose -f docker-compose.prod.yml restart deepfix-server

# Adjust resource limits in docker-compose.prod.yml
```

### Certificate Issues

```bash
# Regenerate certificates
docker run --rm -v ${PWD}/traefik/certs:/certs alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/server.key -out /certs/server.crt -subj "/CN=deepfix.local"

# Restart Traefik
docker compose -f docker-compose.prod.yml restart traefik
```

## 📚 Next Steps

1. **Set up proper authentication**: Configure API keys for production
2. **Configure alerts**: Set up Grafana alert notifications (email, Slack, etc.)
3. **Production certificates**: Use Let's Encrypt or your organization's CA
4. **Scale up**: Adjust resource limits based on load
5. **Backup automation**: Set up automated backup scripts
6. **Monitoring**: Create custom Grafana dashboards for your specific metrics

## 🔗 Useful Links

- **Documentation**: See `productionizing.md` for detailed deployment guide
- **API Reference**: Access via `https://localhost/docs` (if OpenAPI enabled)
- **MLflow Docs**: https://mlflow.org/docs/latest/index.html
- **Grafana Docs**: https://grafana.com/docs/
- **Traefik Docs**: https://doc.traefik.io/traefik/

## 💡 Tips

1. **Bookmark dashboards**: Save your most-used Grafana dashboards
2. **Use log queries**: Learn LogQL to search logs efficiently in Loki
3. **Monitor costs**: Track LLM token usage in MLflow to control costs
4. **Set up alerts**: Get notified before issues become critical
5. **Regular backups**: Schedule automated backups of MLflow data

---

**Need help?** Check the logs first, then refer to the Troubleshooting section above!

