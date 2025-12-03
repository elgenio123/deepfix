# DeepFix Production - Quick Start Guide

## 🎯 Your Services Are Running!

All services are healthy and accessible. Here's how to use them:

## 🌐 Web Access

Open these URLs in your browser:

| Service | URL | Credentials |
|---------|-----|-------------|
| **DeepFix API** | https://localhost/ | (uses API key) |
| **MLflow UI** | https://localhost/mlflow | (no login required) |
| **Grafana** | https://localhost/grafana | admin / admin |
| **Traefik Dashboard** | https://localhost/dashboard | admin / admin |

> ⚠️ **Certificate Warning**: You'll see a security warning because we're using self-signed certificates. 
> Click "Advanced" → "Proceed to localhost (unsafe)" to continue. This is normal for testing.

## 🧪 Quick API Test

### Test the API is running:

```bash
# From inside the container
docker exec deepfix-server curl http://localhost:8844/

# Expected response: "litserve running..."
```

### Make an analysis request (Python):

```python
import requests

# Example API call
response = requests.post(
    "https://localhost/v1/analyse",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "dataset_artifacts": {
            "train_path": "data/train.csv",
            "test_path": "data/test.csv"
        },
        "dataset_name": "my_dataset",
        "language": "en"
    },
    verify=False  # Only for self-signed certs
)

print(response.json())
```

## 📊 View Your Data

### MLflow - Track Experiments
1. Open: https://localhost/mlflow
2. See all your analysis runs
3. Click any run to view:
   - LLM prompts and responses
   - Token usage and costs
   - Agent reasoning steps
   - Model predictions

### Grafana - Monitor Performance
1. Open: https://localhost/grafana
2. Login with: admin / admin
3. Go to "Dashboards" → "DeepFix Overview"
4. View real-time metrics:
   - Request rates
   - Response times
   - Error rates
   - System resources

### Grafana - Search Logs
1. In Grafana, click "Explore" (compass icon)
2. Select "Loki" data source
3. Try these queries:
   ```
   {container_name="deepfix-server"}
   {container_name="deepfix-server"} |= "error"
   {container_name="deepfix-server"} |= "INFO"
   ```

## 🔧 Common Commands

```bash
# View all services status
docker compose -f docker-compose.prod.yml ps

# View live logs (all services)
docker compose -f docker-compose.prod.yml logs -f

# View logs for specific service
docker compose -f docker-compose.prod.yml logs -f deepfix-server

# Restart a service
docker compose -f docker-compose.prod.yml restart deepfix-server

# Stop all services (keeps data)
docker compose -f docker-compose.prod.yml stop

# Start all services
docker compose -f docker-compose.prod.yml start

# View resource usage
docker stats --no-stream
```

## 📈 What to Monitor

### In Grafana Dashboard:
- ✅ **Response Time**: Should be < 5 seconds for most requests
- ✅ **Error Rate**: Should be < 1%
- ✅ **CPU Usage**: Should stay under 80%
- ✅ **Memory**: DeepFix should use < 3GB

### In MLflow:
- 📊 Track token usage to control LLM costs
- 📊 Compare different runs to see improvements
- 📊 Review agent decisions and reasoning

## 🐛 Troubleshooting

### Service won't start?
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs deepfix-server

# Check health status
docker inspect deepfix-server --format='{{.State.Health.Status}}'
```

### Can't access web interface?
```bash
# Verify services are running
docker compose -f docker-compose.prod.yml ps

# Check Traefik logs
docker compose -f docker-compose.prod.yml logs traefik

# Restart Traefik
docker compose -f docker-compose.prod.yml restart traefik
```

### High memory usage?
```bash
# Check resource usage
docker stats

# Restart service
docker compose -f docker-compose.prod.yml restart deepfix-server
```

## 📚 Next Steps

1. **🔒 Security**: Change default passwords for Grafana and Traefik
2. **🔔 Alerts**: Configure email/Slack notifications in Grafana
3. **📜 Certificates**: Use Let's Encrypt for production SSL certificates
4. **💾 Backups**: Set up automated backups of MLflow data
5. **📊 Custom Dashboards**: Create your own Grafana dashboards

## 📖 More Information

- **Full Guide**: See `USAGE_GUIDE.md` for detailed instructions
- **Production Guide**: See `productionizing.md` for deployment details
- **Issues?** Check the Troubleshooting section above or logs

## 🎉 You're All Set!

Your DeepFix production environment is running and ready to analyze ML artifacts!

Try opening **https://localhost/grafana** and **https://localhost/mlflow** in your browser now!

