# 🚀 Production Deployment Guide

## Overview

Your F1 ML system is now configured for production deployment using **Gunicorn**, a production-grade WSGI server.

---

## Local Production Setup

### Quick Start

```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
chmod +x start_production.sh
./start_production.sh
```

This script:
- ✅ Kills any existing services
- ✅ Starts Gunicorn with 4 workers
- ✅ Starts Streamlit dashboard
- ✅ Logs everything to `logs/` directory

### Manual Start

**Terminal 1 - API Server (Gunicorn)**
```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
python3 -m gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 api_server:app
```

**Terminal 2 - Dashboard**
```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
streamlit run streamlit_dashboard.py
```

---

## Gunicorn Configuration

### Using Config File

```bash
python3 -m gunicorn -c gunicorn_config.py api_server:app
```

### Key Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| Workers | 4 | Parallel request handling |
| Worker Class | sync | Best for CPU-bound ML models |
| Timeout | 120s | Allow time for model training |
| Bind | 0.0.0.0:8000 | Listen on all interfaces, port 8000 |
| Max Requests | 1000 | Reload workers (prevent memory leaks) |
| Access Log | logs/gunicorn-access.log | HTTP request logging |
| Error Log | logs/gunicorn-error.log | Application errors |

### Adjusting Worker Count

For optimal performance, calculate:
```
workers = (2 × CPU_cores) + 1
```

Example:
- 2-core machine: 5 workers
- 4-core machine: 9 workers
- 8-core machine: 17 workers

Change in command:
```bash
python3 -m gunicorn -w 9 -b 0.0.0.0:8000 api_server:app
```

---

## Monitoring

### Check if Running

```bash
# Check Gunicorn
curl http://localhost:8000/api/stats

# Check Dashboard
curl http://localhost:8501
```

### View Logs

```bash
# Real-time API access logs
tail -f logs/gunicorn-access.log

# API error logs
tail -f logs/gunicorn-error.log

# Dashboard logs
tail -f logs/streamlit.log
```

### Memory Usage

```bash
# Check process memory
ps aux | grep gunicorn
ps aux | grep streamlit
```

---

## Production Deployment Options

### Option 1: Cloud Deployment (Recommended)

#### Heroku/Railway
```bash
# Create Procfile
echo "web: python3 -m gunicorn -w 4 -b 0.0.0.0:\$PORT api_server:app" > Procfile
git push heroku main
```

#### AWS EC2
```bash
# Create systemd service file
sudo nano /etc/systemd/system/f1-ml-api.service
```

#### Google Cloud Run
```bash
# Build Docker image
docker build -t f1-ml-api .
docker push gcr.io/your-project/f1-ml-api
gcloud run deploy f1-ml-api --image gcr.io/your-project/f1-ml-api
```

### Option 2: Docker Container

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python3", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "120", "api_server:app"]
```

Build and run:
```bash
docker build -t f1-ml-api .
docker run -p 8000:8000 f1-ml-api
```

### Option 3: systemd Service (Linux)

Create `/etc/systemd/system/f1-ml-api.service`:
```ini
[Unit]
Description=F1 ML Prediction API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/user/f1-ml-datasets
ExecStart=/usr/bin/python3 -m gunicorn -w 4 -b 127.0.0.1:8000 api_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable f1-ml-api
sudo systemctl start f1-ml-api
```

### Option 4: Nginx Reverse Proxy

Configure Nginx to forward requests to Gunicorn:

```nginx
upstream f1_ml_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://f1_ml_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Reload Nginx:
```bash
sudo nginx -s reload
```

---

## Performance Tuning

### Worker Class Selection

| Worker Class | Best For | Max Requests/sec |
|-------------|----------|-----------------|
| sync | CPU-bound (ML models) | 50-100 |
| async | I/O-bound (database) | 500+ |
| gevent | High concurrency | 1000+ |
| tornado | WebSockets | 1000+ |

For ML predictions: **Use `sync`** (default)

### Memory Management

```python
# In gunicorn_config.py
max_requests = 1000        # Reload after 1000 requests
max_requests_jitter = 50   # Random jitter (995-1050)
```

This prevents memory leaks from long-running model training.

### Connection Pooling

For database or cache connections, add to `api_server.py`:
```python
from redis import Redis
import psycopg2.pool

redis_client = Redis(host='localhost', port=6379, db=0)
db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, dbname='f1_db')
```

---

## Environment Variables

Create `.env`:
```bash
FLASK_ENV=production
LOG_LEVEL=info
MODEL_PATH=./processed_data/
DEBUG=False
```

Load in `api_server.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

---

## Scaling

### Horizontal Scaling (Multiple Servers)

1. Run Gunicorn on multiple machines
2. Place load balancer in front (Nginx, HAProxy)
3. Share data via network volume or database

### Vertical Scaling (Increase Resources)

Increase worker count:
```bash
# 2 → 4 → 8 → 16 workers
python3 -m gunicorn -w 16 -b 0.0.0.0:8000 api_server:app
```

Monitor CPU and memory:
```bash
top -p $(pgrep -f gunicorn | tr '\n' ',')
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Workers Not Starting

Check logs:
```bash
cat logs/gunicorn-error.log
```

Common issues:
- Missing Python packages: `pip install -r requirements.txt`
- Import errors: Check `api_server.py`
- Data file missing: Verify `processed_data/` exists

### High Memory Usage

Reduce workers:
```bash
python3 -m gunicorn -w 2 -b 0.0.0.0:8000 api_server:app
```

Or enable worker recycling:
```python
max_requests = 500  # Reload workers every 500 requests
```

### Slow Predictions

Check logs for slow requests:
```bash
grep "D)s" logs/gunicorn-access.log | sort -t' ' -k18 -rn | head -10
```

Optimize model or increase timeout:
```bash
python3 -m gunicorn --timeout 240 -w 4 api_server:app
```

---

## Monitoring & Observability

### Application Metrics

```python
# In api_server.py
from prometheus_client import Counter, Histogram

prediction_counter = Counter('predictions_total', 'Total predictions')
prediction_duration = Histogram('prediction_duration_seconds', 'Prediction duration')

@app.route('/api/predict', methods=['POST'])
def predict():
    with prediction_duration.time():
        prediction_counter.inc()
        # ... prediction logic
```

### Health Check Endpoint

```python
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'f1-ml-api'})
```

Load balancer health check:
```bash
curl http://localhost:8000/health
```

---

## Security Checklist

- [ ] Use HTTPS (SSL/TLS) in production
- [ ] Set `DEBUG = False`
- [ ] Use environment variables for secrets
- [ ] Validate all API inputs
- [ ] Rate limit API endpoints
- [ ] Run as non-root user
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated

---

## Support

For issues, check:
1. `logs/gunicorn-error.log`
2. `logs/gunicorn-access.log`
3. Gunicorn documentation: https://docs.gunicorn.org/

Happy deploying! 🚀
