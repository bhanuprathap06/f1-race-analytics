# F1 Analytics — Commands Quick Reference

Quick access to all important terminal commands for the F1 Race Analytics project.

---

## 🚀 PROJECT SETUP

### Initial Setup (Run Once)

```bash
# Navigate to project
cd /Users/bhanubanny/Desktop/formulaOne

# Create virtual environment (backend)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
cd F1_ML_DATASETS
pip install -r requirements.txt

# Install frontend dependencies
cd ../F1_RACE_ANALYTICS_FRONTEND
npm install
```

---

## 🔧 BACKEND (Flask API)

### Start Flask API Server

```bash
# Navigate to backend
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# Activate virtual environment
source ../venv/bin/activate

# Start Flask development server (runs on http://localhost:8000)
python app.py
```

### Production Mode with Gunicorn

```bash
# Activate virtual environment
source ../venv/bin/activate

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Test Backend API

```bash
# In a new terminal, test if API is running
curl http://localhost:8000/api/health

# Get driver statistics
curl http://localhost:8000/api/drivers

# Get circuit analysis
curl http://localhost:8000/api/circuits

# Make a race prediction
curl -X POST http://localhost:8000/api/predict/race \
  -H "Content-Type: application/json" \
  -d '{"driver_id": 1, "circuit_id": 1}'
```

---

## ⚛️ FRONTEND (React)

### Start Development Server

```bash
# Navigate to frontend
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND

# Install dependencies (if not already done)
npm install

# Start development server (runs on http://localhost:5173)
npm run dev
```

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

### Code Quality

```bash
# Run linting
npm run lint

# Fix linting issues
npm run lint -- --fix

# Type check
npm run typecheck
```

---

## 📊 STREAMLIT DASHBOARD

### Run Streamlit App

```bash
# Navigate to backend
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# Activate virtual environment
source ../venv/bin/activate

# Run Streamlit dashboard (opens on http://localhost:8501)
streamlit run streamlit_app.py
```

### Run Specific Dashboard Page

```bash
# Run with page parameter
streamlit run streamlit_app.py -- --page race_predictions
```

---

## 📓 JUPYTER NOTEBOOKS

### Start Jupyter Lab

```bash
# Navigate to backend
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# Activate virtual environment
source ../venv/bin/activate

# Start Jupyter Lab (opens on http://localhost:8888)
jupyter lab
```

### Run Specific Notebook

```bash
# Execute notebook
jupyter nbconvert --to notebook --execute notebook_name.ipynb
```

---

## 🌐 FULL STACK (All Services Running)

### Terminal 1: Backend API

```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
source ../venv/bin/activate
python app.py
```

### Terminal 2: Frontend

```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND
npm run dev
```

### Terminal 3: Streamlit Dashboard (Optional)

```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
source ../venv/bin/activate
streamlit run streamlit_app.py
```

### Access Points

- **Frontend:** http://localhost:5173
- **API:** http://localhost:8000
- **Streamlit:** http://localhost:8501
- **Jupyter:** http://localhost:8888

---

## 🐙 GITHUB COMMANDS

### Push to GitHub (First Time)

```bash
# Navigate to frontend project
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/f1-race-analytics-frontend.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

### Regular Git Workflow

```bash
# Check status
git status

# Add files
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main

# View commit history
git log --oneline
```

### Update Repository After Changes

```bash
# Navigate to project
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND

# Add all changes
git add .

# Commit with message
git commit -m "Update: description of changes"

# Push to GitHub
git push origin main
```

---

## 📦 DEPENDENCY MANAGEMENT

### Update Backend Dependencies

```bash
# Navigate to backend
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# Activate virtual environment
source ../venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install from requirements
pip install -r requirements.txt

# Update requirements file
pip freeze > requirements.txt
```

### Update Frontend Dependencies

```bash
# Navigate to frontend
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND

# Check for updates
npm outdated

# Update packages
npm update

# Update specific package
npm install package-name@latest
```

---

## 🧪 TESTING

### Backend Tests

```bash
# Navigate to backend
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# Activate virtual environment
source ../venv/bin/activate

# Run tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test
pytest tests/test_models.py::test_function_name
```

### Frontend Tests

```bash
# Navigate to frontend
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

---

## 🔍 DEBUGGING

### View Backend Logs

```bash
# Check Flask logs (if running)
# Logs appear in terminal where Flask is running

# Check API response
curl -v http://localhost:8000/api/health
```

### View Frontend Logs

```bash
# Check browser console
# Open browser → F12 → Console tab

# View build errors
npm run build
```

### Database Check

```bash
# Navigate to backend
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# Activate virtual environment
source ../venv/bin/activate

# Check database with Python
python -c "import sqlite3; conn = sqlite3.connect('f1_data.db'); print(conn.cursor().fetchall())"
```

---

## 🚨 TROUBLESHOOTING

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process (replace PID)
kill -9 PID

# Or change Flask port in app.py
# from app import create_app
# app = create_app()
# if __name__ == '__main__':
#     app.run(debug=True, port=9000)
```

### Virtual Environment Issues

```bash
# Remove and recreate virtual environment
cd /Users/bhanubanny/Desktop/formulaOne
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r F1_ML_DATASETS/requirements.txt
```

### Clear Node Modules & Reinstall

```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND
rm -rf node_modules
rm package-lock.json
npm install
```

### Clear Build Artifacts

```bash
# Frontend
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND
rm -rf dist/
npm run build

# Python
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

---

## 📋 COMMON WORKFLOWS

### New Feature Development

```bash
# 1. Update frontend component
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND
# Edit component files

# 2. Test frontend
npm run dev
# Check in browser

# 3. Commit changes
git add .
git commit -m "feat: add new feature"
git push origin main
```

### Bug Fix Workflow

```bash
# 1. Make changes
cd /Users/bhanubanny/Desktop/formulaOne

# 2. Test thoroughly
npm run dev  # for frontend
python app.py  # for backend

# 3. Commit with fix message
git add .
git commit -m "fix: resolve issue description"
git push origin main
```

### Data Analysis Update

```bash
# Navigate to backend
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS

# Activate environment
source ../venv/bin/activate

# Update data
python scripts/update_data.py

# Reprocess features
python scripts/process_features.py

# Retrain models
python scripts/train_models.py
```

---

## ✅ VERIFICATION CHECKLIST

### Before Pushing to GitHub

```bash
# Frontend
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND
npm run lint  # Check for errors
npm run build  # Build successful
npm run dev  # Runs without errors

# Backend
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
source ../venv/bin/activate
python app.py  # Runs without errors

# Git
git status  # Check what's being pushed
git diff  # Review changes
git add .
git commit -m "message"
git push origin main
```

---

## 💾 ENVIRONMENT VARIABLES

### Backend (.env file)

```bash
# Create file: F1_ML_DATASETS/.env
FLASK_ENV=development
FLASK_APP=app.py
DATABASE_URL=sqlite:///f1_data.db
API_PORT=8000
DEBUG=True
```

### Frontend (.env.local file)

```bash
# Create file: F1_RACE_ANALYTICS_FRONTEND/.env.local
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=F1 Analytics
VITE_ENV=development
```

---

## 🎯 QUICK COMMAND REFERENCE

```bash
# Backend quick start
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS && source ../venv/bin/activate && python app.py

# Frontend quick start
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND && npm run dev

# Dashboard quick start
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS && source ../venv/bin/activate && streamlit run streamlit_app.py

# Quick git push
cd /Users/bhanubanny/Desktop/formulaOne/F1_RACE_ANALYTICS_FRONTEND && git add . && git commit -m "update" && git push origin main
```

---

## 📞 HELP

- **API Issues?** Check API logs in terminal where Flask is running
- **Frontend Issues?** Check browser console (F12 → Console)
- **Build Issues?** Clear node_modules and reinstall
- **Port Conflicts?** Use `lsof -i :PORT` to find and kill process

---

**Last Updated:** August 2026  
**Project:** F1 Race Analytics & Predictive Performance System
