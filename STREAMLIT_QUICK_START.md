# Streamlit Dashboard — Quick Start

Run the dashboard locally to show graphs. Copy & paste these commands.

---

## 🚀 START STREAMLIT (3 Steps)

### Step 1: Open Terminal

```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
```

### Step 2: Activate Virtual Environment

```bash
source ../venv/bin/activate
```

### Step 3: Run Streamlit

```bash
streamlit run streamlit_app.py
```

That's it! The dashboard will open automatically at: **http://localhost:8501**

---

## 📊 What You'll See

✅ **Race Predictions** — See predicted race winners  
✅ **Driver Analytics** — Driver performance graphs  
✅ **Circuit Analysis** — Circuit-specific insights  
✅ **Model Performance** — ML model metrics  

---

## 🛑 STOP STREAMLIT

Press `Ctrl + C` in the terminal to stop

---

## ❌ IF IT DOESN'T WORK

### Error: "Command not found"

Make sure you're in the right directory:
```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS
source ../venv/bin/activate
```

### Error: "streamlit: command not found"

Reinstall Streamlit:
```bash
source ../venv/bin/activate
pip install streamlit
```

### Port Already in Use

If port 8501 is busy:
```bash
streamlit run streamlit_app.py --server.port 8502
```

Then access at: **http://localhost:8502**

---

## ⚡ ONE-LINER (Copy & Paste Everything)

```bash
cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS && source ../venv/bin/activate && streamlit run streamlit_app.py
```

That's all you need!

---

## 📱 Access from Phone/Tablet (Same Network)

1. Find your Mac's IP address:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

2. Open on phone/tablet:
```
http://YOUR_MAC_IP:8501
```

Example: `http://192.168.1.100:8501`

---

## ✅ YOU'RE DONE!

Dashboard is live. Show your ma'am the graphs! 🚀
