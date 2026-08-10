#!/bin/bash

# ============================================================================
# F1 ML SYSTEM - PRODUCTION STARTUP SCRIPT
# ============================================================================

PROJECT_DIR="/Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS"
cd "$PROJECT_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        F1 ML PRODUCTION SYSTEM - STARTING SERVICES            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Create logs directory
mkdir -p logs

# Kill any existing services
echo "🛑 Stopping existing services..."
pkill -f "streamlit" 2>/dev/null
pkill -f "gunicorn" 2>/dev/null
sleep 2

# ============================================================================
# GUNICORN API SERVER (Production WSGI Server)
# ============================================================================

echo "🚀 Starting Gunicorn WSGI server (4 workers)..."
nohup python3 -m gunicorn \
  -w 4 \
  -b 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile logs/gunicorn-access.log \
  --error-logfile logs/gunicorn-error.log \
  --log-level info \
  api_server:app > /dev/null 2>&1 &

GUNICORN_PID=$!
sleep 4

# Verify Gunicorn started (retry 3 times)
for i in {1..3}; do
  if curl -s http://localhost:8000/api/stats > /dev/null 2>&1; then
    echo "✅ Gunicorn WSGI server running at http://0.0.0.0:8000 (PID: $GUNICORN_PID)"
    echo "   Workers: 4 (sync workers)"
    echo "   Access log: logs/gunicorn-access.log"
    echo "   Error log: logs/gunicorn-error.log"
    GUNICORN_OK=1
    break
  else
    echo "   Waiting for Gunicorn to start (attempt $i/3)..."
    sleep 2
  fi
done

if [ -z "$GUNICORN_OK" ]; then
  echo "❌ Gunicorn failed to start or not responding"
  echo "   Check logs: tail -f logs/gunicorn-error.log"
  exit 1
fi

echo ""

# ============================================================================
# STREAMLIT DASHBOARD
# ============================================================================

echo "🎨 Starting Streamlit dashboard..."
nohup streamlit run streamlit_dashboard.py > logs/streamlit.log 2>&1 &

STREAMLIT_PID=$!
sleep 3

echo "✅ Streamlit dashboard running at http://localhost:8501 (PID: $STREAMLIT_PID)"
echo "   Log file: logs/streamlit.log"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   SYSTEM READY                                ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║  🚀 API Server    http://localhost:8000  (Gunicorn - 4 workers)║"
echo "║  📊 Dashboard     http://localhost:8501  (Streamlit)           ║"
echo "║                                                                ║"
echo "║  Available Endpoints:                                          ║"
echo "║    GET  /api/stats                                             ║"
echo "║    GET  /api/top-drivers?n=10                                  ║"
echo "║    GET  /api/driver/<name>                                     ║"
echo "║    POST /api/predict                                           ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 To stop services:"
echo "   pkill -f 'streamlit'"
echo "   pkill -f 'gunicorn'"
echo ""
echo "📊 To view logs:"
echo "   tail -f logs/gunicorn-access.log"
echo "   tail -f logs/gunicorn-error.log"
echo "   tail -f logs/streamlit.log"
echo ""
