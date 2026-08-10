# 🚀 Production Startup Guide

## Quick Start (Copy & Paste)

Open **3 terminal windows** and run:

### Terminal 1 - API Server (Gunicorn)
```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
python3 -m gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 api_server:app
```

**Expected output:**
```
[TIMESTAMP] [PID] [INFO] Starting gunicorn
[TIMESTAMP] [PID] [INFO] Listening at: http://0.0.0.0:8000 (PID)
[TIMESTAMP] [PID] [INFO] Using worker: sync
[TIMESTAMP] [PID] [INFO] Booting worker with pid: X
[TIMESTAMP] [PID] [INFO] Booting worker with pid: Y
```

✅ Keep this terminal open. The server is now running on **http://localhost:8000**

---

### Terminal 2 - Streamlit Dashboard
```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
python3 -m streamlit run streamlit_dashboard.py --server.port=8501
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

✅ Keep this terminal open. The dashboard is now running on **http://localhost:8501**

---

### Terminal 3 - Testing/Commands
```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# Test API
curl http://localhost:8000/api/stats

# View logs
tail -f server.log
tail -f dashboard.log
```

---

## Access Your System

| Service | URL | What to Do |
|---------|-----|-----------|
| **API** | http://localhost:8000 | `curl http://localhost:8000/api/stats` |
| **Dashboard** | http://localhost:8501 | Open in browser |

---

## One-Command Startup (Background Both)

If you want to start both services in one command:

```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
nohup python3 -m gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 api_server:app > api.log 2>&1 &
nohup python3 -m streamlit run streamlit_dashboard.py --server.port=8501 > dashboard.log 2>&1 &
echo "✅ Services started in background"
echo "   API: http://localhost:8000"
echo "   Dashboard: http://localhost:8501"
echo "   Logs: tail -f api.log dashboard.log"
```

---

## Full API Test Sequence

```bash
# 1. Get dataset stats
curl http://localhost:8000/api/stats

# 2. Get top 10 drivers
curl "http://localhost:8000/api/top-drivers?n=10"

# 3. Get Lewis Hamilton stats
curl "http://localhost:8000/api/driver/Hamilton"

# 4. Get all constructors
curl "http://localhost:8000/api/top-constructors?n=10"

# 5. Get all circuits
curl "http://localhost:8000/api/top-circuits?n=10"

# 6. Make a prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "grid_position": 5,
    "position_number": 5,
    "previous_points": 15,
    "driver_number": 44,
    "laps": 50
  }'
```

---

## Expected API Responses

### `/api/stats`
```json
{
  "podiums": 3501,
  "top10": 11341,
  "total_circuits": 77,
  "total_constructors": 186,
  "total_drivers": 860,
  "total_races": 1160,
  "total_records": 27533,
  "winners": 1163,
  "year_range": "1950-2026"
}
```

### `/api/top-drivers?n=5`
```json
{
  "top_drivers": {
    "Lewis Hamilton": 106,
    "Michael Schumacher": 91,
    "Max Verstappen": 71,
    "Sebastian Vettel": 53,
    "Alain Prost": 51
  }
}
```

### `/api/predict`
```json
{
  "confidence": "0.01%",
  "prediction": 0,
  "probability": 8.332065772265196e-05,
  "success": true,
  "will_win": false
}
```

---

## Stopping Services

```bash
# Kill all services
pkill -f gunicorn
pkill -f streamlit

# Or specifically
killall gunicorn
killall streamlit

# Check if running
ps aux | grep -E "gunicorn|streamlit" | grep -v grep
```

---

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python3 -m gunicorn -w 4 -b 0.0.0.0:9000 api_server:app
```

### Port 8501 Already in Use
```bash
# Kill Streamlit
pkill -f streamlit

# Start on different port
python3 -m streamlit run streamlit_dashboard.py --server.port=9501
```

### "ModuleNotFoundError: No module named 'gunicorn'"
```bash
pip install gunicorn
```

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask
```

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### API not responding
```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check if port is listening
lsof -i :8000

# Verify file exists
ls processed_data/01_race_prediction_dataset.csv

# Restart Gunicorn
pkill -f gunicorn
python3 -m gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 api_server:app
```

---

## Performance Tuning

### More Workers (for more concurrency)
```bash
python3 -m gunicorn -w 8 -b 0.0.0.0:8000 --timeout 120 api_server:app
```

### Fewer Workers (for low memory)
```bash
python3 -m gunicorn -w 2 -b 0.0.0.0:8000 --timeout 120 api_server:app
```

### Longer Timeout (for slow ML predictions)
```bash
python3 -m gunicorn -w 4 -b 0.0.0.0:8000 --timeout 300 api_server:app
```

---

## Docker Deployment (Alternative)

If you want to run in Docker instead:

```bash
# Build image
docker build -t f1-ml-api .

# Run container
docker run -p 8000:8000 f1-ml-api

# Or both services with Docker Compose
docker-compose up -d
```

---

## System Status Commands

```bash
# View all running Python processes
ps aux | grep python

# View memory usage
ps aux | grep gunicorn | awk '{print $6}' | tail -n +2 | awk '{sum+=$1} END {print "Memory: " sum/1024 "MB"}'

# Monitor Gunicorn in real-time
watch -n 1 "ps aux | grep gunicorn"

# Check network connections
netstat -an | grep 8000
netstat -an | grep 8501
```

---

## Environment Setup (One-Time)

If you're setting up for the first time:

```bash
# 1. Navigate to project
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Verify installation
python3 -c "import gunicorn, flask, streamlit, pandas, xgboost; print('✅ All packages installed')"

# 4. Check data exists
ls processed_data/01_race_prediction_dataset.csv

# 5. Ready to start!
echo "✅ Setup complete. Run the commands above to start services."
```

---

## Summary

**To run your production system:**

1. Open 2-3 terminal windows
2. In each, navigate to: `cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS`
3. **Terminal 1:** `python3 -m gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 api_server:app`
4. **Terminal 2:** `python3 -m streamlit run streamlit_dashboard.py --server.port=8501`
5. Access: http://localhost:8501 (Dashboard) or http://localhost:8000 (API)

That's it! 🎉

---

## Documentation Files

- `GUNICORN_QUICK_REFERENCE.txt` - Command cheat sheet
- `PRODUCTION_READY.md` - Full production guide
- `PRODUCTION_DEPLOYMENT.md` - Cloud deployment options
- `README.md` - API reference
- `DATA_DICTIONARY.md` - Variable definitions
