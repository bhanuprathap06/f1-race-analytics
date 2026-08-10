#!/usr/bin/env python3
"""
REST API Server for F1 ML Predictions
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Load data
print("Loading datasets...")
df = pd.read_csv('processed_data/01_race_prediction_dataset.csv')
df_circuits = pd.read_csv('processed_data/02_circuit_summary.csv')

# Prepare features and train model
feature_cols = ['positionNumber', 'gridPositionNumber', 'points', 'driverNumber', 'laps']
X = df[feature_cols].fillna(df[feature_cols].mean())
y = df['winner']

# Train model
print("Training model...")
model = XGBClassifier(n_estimators=100, max_depth=6, random_state=42, verbosity=0)
model.fit(X, y)

print("\n" + "="*80)
print("🚀 F1 ML REST API SERVER STARTED")
print("="*80)
print("\nAPI is running at: http://localhost:5000")
print("\nAvailable endpoints:")
print("  POST   /api/predict              - Make a prediction")
print("  GET    /api/stats               - Get dataset statistics")
print("  GET    /api/models              - Get available models")
print("  GET    /api/top-drivers         - Get top drivers")
print("  GET    /api/top-constructors    - Get top constructors")
print("  GET    /api/top-circuits        - Get top circuits")
print("  GET    /api/driver/<name>       - Get driver stats")
print("  GET    /api/constructor/<name>  - Get constructor stats")
print("\n" + "="*80 + "\n")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make a prediction"""
    try:
        data = request.json
        
        # Extract features
        features = np.array([[
            data.get('position_number', 10),
            data.get('grid_position', 5),
            data.get('previous_points', 10),
            data.get('driver_number', 1),
            data.get('laps', 50)
        ]])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]
        
        return jsonify({
            'success': True,
            'prediction': int(prediction),
            'will_win': bool(prediction),
            'probability': float(probability),
            'confidence': f"{probability*100:.2f}%"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get dataset statistics"""
    return jsonify({
        'total_races': int(df['raceId'].nunique()),
        'total_drivers': int(df['driverId'].nunique()),
        'total_constructors': int(df['constructorId'].nunique()),
        'total_circuits': int(df['circuitId'].nunique()),
        'total_records': len(df),
        'year_range': f"{int(df['year'].min())}-{int(df['year'].max())}",
        'winners': int(df['winner'].sum()),
        'podiums': int(df['podium'].sum()),
        'top10': int(df['top10'].sum())
    })

@app.route('/api/models', methods=['GET'])
def models_info():
    """Get available models"""
    return jsonify({
        'models': ['XGBoost', 'Random Forest', 'Gradient Boosting', 'Ensemble'],
        'default_model': 'XGBoost',
        'features': ['position_number', 'grid_position', 'previous_points', 'driver_number', 'laps']
    })

@app.route('/api/top-drivers', methods=['GET'])
def top_drivers():
    """Get top drivers"""
    n = request.args.get('n', 10, type=int)
    top = df[df['winner']==1].groupby('driver_name').size().sort_values(ascending=False).head(n)
    return jsonify({
        'top_drivers': top.to_dict()
    })

@app.route('/api/top-constructors', methods=['GET'])
def top_constructors():
    """Get top constructors"""
    n = request.args.get('n', 10, type=int)
    top = df[df['winner']==1].groupby('constructor_name').size().sort_values(ascending=False).head(n)
    return jsonify({
        'top_constructors': top.to_dict()
    })

@app.route('/api/top-circuits', methods=['GET'])
def top_circuits():
    """Get circuits with most races"""
    n = request.args.get('n', 10, type=int)
    top = df.groupby('circuit_name').size().sort_values(ascending=False).head(n)
    return jsonify({
        'top_circuits': top.to_dict()
    })

@app.route('/api/driver/<name>', methods=['GET'])
def get_driver(name):
    """Get driver statistics"""
    driver_data = df[df['driver_name'].str.contains(name, case=False, na=False)]
    if len(driver_data) == 0:
        return jsonify({'error': 'Driver not found'}), 404
    
    return jsonify({
        'driver_name': name,
        'races': len(driver_data),
        'wins': int(driver_data['winner'].sum()),
        'podiums': int(driver_data['podium'].sum()),
        'top10': int(driver_data['top10'].sum()),
        'total_points': float(driver_data['points'].sum()),
        'win_percentage': float(driver_data['winner'].mean() * 100),
        'podium_percentage': float(driver_data['podium'].mean() * 100)
    })

@app.route('/api/constructor/<name>', methods=['GET'])
def get_constructor(name):
    """Get constructor statistics"""
    const_data = df[df['constructor_name'].str.contains(name, case=False, na=False)]
    if len(const_data) == 0:
        return jsonify({'error': 'Constructor not found'}), 404
    
    return jsonify({
        'constructor_name': name,
        'races': len(const_data),
        'wins': int(const_data['winner'].sum()),
        'podiums': int(const_data['podium'].sum()),
        'top10': int(const_data['top10'].sum()),
        'total_points': float(const_data['points'].sum()),
        'win_percentage': float(const_data['winner'].mean() * 100),
        'podium_percentage': float(const_data['podium'].mean() * 100)
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'F1 ML Prediction API',
        'version': '1.0',
        'status': 'Running',
        'api_docs': 'See /api/models for available endpoints'
    })

# Production WSGI server (Gunicorn)
# Run with: gunicorn -w 4 -b 0.0.0.0:8000 api_server:app
# OR: gunicorn -w 4 -b 0.0.0.0:8000 --access-logfile - --error-logfile - api_server:app
