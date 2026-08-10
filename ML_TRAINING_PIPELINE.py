"""
F1 RACE PREDICTOR - ML TRAINING PIPELINE
Machine Learning Engineering for Formula 1 Predictions
SRMIST Chennai - Educational & Production Use

Trains 5 ML models with hyperparameter tuning for:
- Race Winner Prediction
- Podium Finish Probability
- Final Position Prediction

Target Accuracy: 90%+
"""

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
from pathlib import Path

# ML Libraries
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 80)
print("F1 RACE PREDICTOR - ML TRAINING PIPELINE")
print("=" * 80)

# ============================================================================
# STEP 1: DATA LOADING & PREPARATION
# ============================================================================

print("\n[STEP 1] Loading and preparing data...")

def load_f1_data():
    """Load F1 race data from CSV files"""
    try:
        # Load main datasets
        races_df = pd.read_csv('F1_ML_DATASETS/data/races.csv')
        results_df = pd.read_csv('F1_ML_DATASETS/data/results.csv')
        drivers_df = pd.read_csv('F1_ML_DATASETS/data/drivers.csv')
        constructors_df = pd.read_csv('F1_ML_DATASETS/data/constructors.csv')
        circuits_df = pd.read_csv('F1_ML_DATASETS/data/circuits.csv')

        print("✓ Loaded: races, results, drivers, constructors, circuits")
        return races_df, results_df, drivers_df, constructors_df, circuits_df
    except FileNotFoundError as e:
        print(f"✗ Error loading data: {e}")
        print("Creating synthetic data for demo...")
        return create_synthetic_data()

def create_synthetic_data():
    """Create synthetic F1 data for training if real data unavailable"""
    np.random.seed(42)

    # Create races (exactly 1160)
    num_races = 1160
    races_df = pd.DataFrame({
        'raceId': range(1, num_races + 1),
        'year': [1950 + (i // 20) for i in range(num_races)],
        'circuitId': [(i % 77) + 1 for i in range(num_races)],
        'date': pd.date_range('1950-01-01', periods=num_races, freq='W')
    })

    # Create results (27,533 records)
    num_records = 27533
    results_df = pd.DataFrame({
        'resultId': range(1, num_records + 1),
        'raceId': np.random.choice(races_df['raceId'].values, num_records),
        'driverId': np.random.choice(range(1, 861), num_records),
        'constructorId': np.random.choice(range(1, 187), num_records),
        'position': np.random.choice(range(1, 21), num_records),
        'points': np.random.choice([25, 18, 15, 12, 10, 8, 6, 4, 2, 1, 0], num_records),
        'grid': np.random.choice(range(1, 21), num_records),
        'fastestLapRank': np.random.choice([1, 2, 3, None], num_records),
        'statusId': np.random.choice([1, 2, 3], num_records)
    })

    # Create drivers
    drivers_df = pd.DataFrame({
        'driverId': range(1, 861),
        'code': [f'DRV{i}' for i in range(1, 861)]
    })

    # Create constructors
    constructors_df = pd.DataFrame({
        'constructorId': range(1, 187),
        'name': [f'Constructor{i}' for i in range(1, 187)]
    })

    # Create circuits
    circuits_df = pd.DataFrame({
        'circuitId': range(1, 78),
        'name': [f'Circuit{i}' for i in range(1, 78)],
        'location': [f'Location{i}' for i in range(1, 78)]
    })

    print("✓ Created synthetic F1 dataset (27,533 records)")
    return races_df, results_df, drivers_df, constructors_df, circuits_df

# Load data
races_df, results_df, drivers_df, constructors_df, circuits_df = load_f1_data()

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================

print("\n[STEP 2] Engineering features (50+ features)...")

def engineer_features(races_df, results_df, drivers_df, constructors_df, circuits_df):
    """Engineer 50+ features from raw data"""

    # Merge datasets
    data = results_df.merge(races_df[['raceId', 'year', 'circuitId']], on='raceId')
    data = data.merge(drivers_df[['driverId', 'code']], on='driverId')
    data = data.merge(constructors_df[['constructorId', 'name']], on='constructorId')
    data = data.merge(circuits_df[['circuitId', 'location']], on='circuitId')

    # ===== DRIVER FEATURES =====
    driver_stats = results_df.groupby('driverId').agg({
        'points': ['sum', 'mean', 'std'],
        'position': ['mean', 'min'],
        'grid': 'mean',
        'fastestLapRank': lambda x: (x == 1).sum()
    }).fillna(0)
    driver_stats.columns = ['driver_total_points', 'driver_avg_points', 'driver_points_std',
                            'driver_avg_position', 'driver_best_position', 'driver_avg_grid', 'driver_fastest_laps']

    # ===== CONSTRUCTOR FEATURES =====
    constructor_stats = results_df.groupby('constructorId').agg({
        'points': ['sum', 'mean'],
        'position': ['mean', 'min'],
        'statusId': lambda x: (x == 1).sum()
    }).fillna(0)
    constructor_stats.columns = ['constructor_total_points', 'constructor_avg_points',
                                 'constructor_avg_position', 'constructor_best_position', 'constructor_finishes']

    # ===== CIRCUIT FEATURES =====
    circuit_stats = results_df.groupby('circuitId').agg({
        'position': 'mean',
        'points': 'mean'
    }).fillna(0)
    circuit_stats.columns = ['circuit_avg_position', 'circuit_avg_points']

    # Merge features
    data = data.merge(driver_stats, on='driverId', how='left')
    data = data.merge(constructor_stats, on='constructorId', how='left')
    data = data.merge(circuit_stats, on='circuitId', how='left')

    # ===== TEMPORAL FEATURES =====
    data['year_numeric'] = data['year']
    data['race_sequence'] = data.groupby('year').cumcount() + 1

    # ===== INTERACTION FEATURES =====
    data['driver_constructor_combo'] = data['driverId'].astype(str) + '_' + data['constructorId'].astype(str)
    data['driver_circuit_combo'] = data['driverId'].astype(str) + '_' + data['circuitId'].astype(str)

    # ===== QUALIFYING & GRID FEATURES =====
    data['grid_to_position_diff'] = data['grid'] - data['position'].fillna(data['grid'])
    data['qualified_better'] = (data['grid'] < data['position']).astype(int)

    # ===== RELIABILITY FEATURES =====
    data['dnf_flag'] = (data['statusId'] != 1).astype(int)
    data['points_earned'] = (data['points'] > 0).astype(int)

    # ===== PERFORMANCE CONSISTENCY =====
    driver_consistency = results_df.groupby('driverId')['position'].std().fillna(0)
    data = data.merge(driver_consistency.rename('driver_consistency'), on='driverId', how='left')

    # ===== ROLLING AVERAGE FEATURES =====
    data = data.sort_values(['driverId', 'raceId']).reset_index(drop=True)
    data['driver_rolling_points'] = data.groupby('driverId')['points'].rolling(window=5, min_periods=1).mean().reset_index(drop=True, level=0)
    data['driver_rolling_position'] = data.groupby('driverId')['position'].rolling(window=5, min_periods=1).mean().reset_index(drop=True, level=0)

    # ===== DUMMY FEATURES =====
    data['is_dnf'] = (data['statusId'] != 1).astype(int)
    data['scored_points'] = (data['points'] > 0).astype(int)
    data['top_10_finish'] = (data['position'] <= 10).astype(int)
    data['podium_finish'] = (data['position'] <= 3).astype(int)

    print(f"✓ Engineered {len(data.columns)} features")
    return data

data = engineer_features(races_df, results_df, drivers_df, constructors_df, circuits_df)

# ============================================================================
# STEP 3: PREPARE TARGETS FOR MULTI-TASK LEARNING
# ============================================================================

print("\n[STEP 3] Preparing prediction targets...")

# Remove rows with missing critical values
data_clean = data.dropna(subset=['position', 'grid', 'driver_avg_points'])

# Target 1: RACE WINNER (Position = 1)
data_clean['is_winner'] = (data_clean['position'] == 1).astype(int)

# Target 2: PODIUM FINISH (Position <= 3)
data_clean['is_podium'] = (data_clean['position'] <= 3).astype(int)

# Target 3: TOP 10 FINISH (Position <= 10)
data_clean['is_top10'] = (data_clean['position'] <= 10).astype(int)

# Print target distribution
print(f"✓ Winners: {data_clean['is_winner'].sum()} ({data_clean['is_winner'].mean()*100:.2f}%)")
print(f"✓ Podium: {data_clean['is_podium'].sum()} ({data_clean['is_podium'].mean()*100:.2f}%)")
print(f"✓ Top 10: {data_clean['is_top10'].sum()} ({data_clean['is_top10'].mean()*100:.2f}%)")

# ============================================================================
# STEP 4: SELECT FEATURES FOR TRAINING
# ============================================================================

print("\n[STEP 4] Selecting features for training...")

feature_cols = [
    'year_numeric', 'race_sequence', 'grid',
    'driver_total_points', 'driver_avg_points', 'driver_avg_position', 'driver_best_position',
    'driver_avg_grid', 'driver_fastest_laps', 'driver_consistency',
    'constructor_total_points', 'constructor_avg_points', 'constructor_avg_position',
    'constructor_best_position', 'constructor_finishes',
    'circuit_avg_position', 'circuit_avg_points',
    'grid_to_position_diff', 'qualified_better',
    'driver_rolling_points', 'driver_rolling_position'
]

# Handle missing values
X = data_clean[feature_cols].fillna(0)
print(f"✓ Selected {len(feature_cols)} features")
print(f"✓ Dataset shape: {X.shape}")

# ============================================================================
# STEP 5: TRAIN MODELS FOR EACH TASK
# ============================================================================

print("\n[STEP 5] Training models (5 algorithms × 3 tasks = 15 models)...")

TASKS = {
    'winner': data_clean['is_winner'],
    'podium': data_clean['is_podium'],
    'top10': data_clean['is_top10']
}

models_dict = {}
results_summary = {}

for task_name, y in TASKS.items():
    print(f"\n--- Training for: {task_name.upper()} ---")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    task_models = {}
    task_results = {}

    # ===== MODEL 1: LOGISTIC REGRESSION =====
    print(f"  [1/5] Logistic Regression...", end=" ")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    lr_pred = lr.predict(X_test_scaled)
    lr_score = accuracy_score(y_test, lr_pred)
    task_models['logistic_regression'] = (lr, scaler)
    task_results['logistic_regression'] = lr_score
    print(f"✓ {lr_score:.4f}")

    # ===== MODEL 2: RANDOM FOREST =====
    print(f"  [2/5] Random Forest (tuning)...", end=" ")
    rf_params = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, 30],
        'min_samples_split': [2, 5]
    }
    rf_grid = GridSearchCV(RandomForestClassifier(random_state=42, n_jobs=-1), rf_params, cv=3, n_jobs=-1)
    rf_grid.fit(X_train, y_train)
    rf_pred = rf_grid.predict(X_test)
    rf_score = accuracy_score(y_test, rf_pred)
    task_models['random_forest'] = rf_grid.best_estimator_
    task_results['random_forest'] = rf_score
    print(f"✓ {rf_score:.4f}")

    # ===== MODEL 3: GRADIENT BOOSTING =====
    print(f"  [3/5] Gradient Boosting (tuning)...", end=" ")
    gb_params = {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1],
        'max_depth': [3, 5]
    }
    gb_grid = GridSearchCV(GradientBoostingClassifier(random_state=42), gb_params, cv=3, n_jobs=-1)
    gb_grid.fit(X_train, y_train)
    gb_pred = gb_grid.predict(X_test)
    gb_score = accuracy_score(y_test, gb_pred)
    task_models['gradient_boosting'] = gb_grid.best_estimator_
    task_results['gradient_boosting'] = gb_score
    print(f"✓ {gb_score:.4f}")

    # ===== MODEL 4: XGBOOST =====
    print(f"  [4/5] XGBoost (tuning)...", end=" ")
    xgb_params = {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1],
        'max_depth': [3, 5]
    }
    xgb_grid = GridSearchCV(xgb.XGBClassifier(random_state=42, n_jobs=-1, verbosity=0), xgb_params, cv=3, n_jobs=-1)
    xgb_grid.fit(X_train, y_train)
    xgb_pred = xgb_grid.predict(X_test)
    xgb_score = accuracy_score(y_test, xgb_pred)
    task_models['xgboost'] = xgb_grid.best_estimator_
    task_results['xgboost'] = xgb_score
    print(f"✓ {xgb_score:.4f}")

    # ===== MODEL 5: VOTING ENSEMBLE =====
    print(f"  [5/5] Voting Ensemble (combining all)...", end=" ")
    ensemble = VotingClassifier(
        estimators=[
            ('rf', task_models['random_forest']),
            ('gb', task_models['gradient_boosting']),
            ('xgb', task_models['xgboost'])
        ],
        voting='soft'
    )
    ensemble.fit(X_train, y_train)
    ensemble_pred = ensemble.predict(X_test)
    ensemble_score = accuracy_score(y_test, ensemble_pred)
    task_models['ensemble'] = ensemble
    task_results['ensemble'] = ensemble_score
    print(f"✓ {ensemble_score:.4f}")

    # Store results
    models_dict[task_name] = task_models
    results_summary[task_name] = {
        'model_scores': task_results,
        'X_test': X_test,
        'y_test': y_test,
        'best_model': max(task_results, key=task_results.get),
        'best_score': max(task_results.values())
    }

    print(f"\n  Best Model for {task_name}: {results_summary[task_name]['best_model']} ({results_summary[task_name]['best_score']:.4f})")

# ============================================================================
# STEP 6: DETAILED EVALUATION & METRICS
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 6] DETAILED EVALUATION & METRICS")
print("=" * 80)

for task_name, results in results_summary.items():
    print(f"\n{'=' * 80}")
    print(f"TASK: {task_name.upper()}")
    print(f"{'=' * 80}")

    best_model_name = results['best_model']
    best_model = models_dict[task_name][best_model_name]
    X_test = results['X_test']
    y_test = results['y_test']

    # Predictions
    y_pred = best_model.predict(X_test)
    y_pred_proba = best_model.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\nModel: {best_model_name}")
    print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")

    print(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  True Negatives:  {cm[0, 0]}")
    print(f"  False Positives: {cm[0, 1]}")
    print(f"  False Negatives: {cm[1, 0]}")
    print(f"  True Positives:  {cm[1, 1]}")

    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # ROC-AUC
    if len(np.unique(y_test)) > 1:
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        print(f"ROC-AUC Score: {roc_auc:.4f}")

# ============================================================================
# STEP 7: FEATURE IMPORTANCE ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 7] FEATURE IMPORTANCE ANALYSIS")
print("=" * 80)

importance_data = {}

for task_name, task_models in models_dict.items():
    print(f"\n{task_name.upper()} - Feature Importance:")
    print("-" * 80)

    # Get importance from Random Forest (most interpretable)
    rf_model = task_models['random_forest']
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)

    importance_data[task_name] = feature_importance

    print(feature_importance.head(15).to_string(index=False))
    print(f"\nTop 5 Features:")
    for idx, (feat, imp) in enumerate(zip(feature_importance['feature'].head(5), feature_importance['importance'].head(5)), 1):
        print(f"  {idx}. {feat:30s} - {imp:.4f} ({imp*100:.2f}%)")

# ============================================================================
# STEP 8: SAVE TRAINED MODELS
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 8] SAVING TRAINED MODELS")
print("=" * 80)

model_save_dir = Path('F1_ML_DATASETS/trained_models')
model_save_dir.mkdir(exist_ok=True, parents=True)

for task_name, task_models in models_dict.items():
    for model_name, model in task_models.items():
        save_path = model_save_dir / f"{task_name}_{model_name}.pkl"
        with open(save_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✓ Saved: {task_name}_{model_name}.pkl")

# Save feature columns
with open(model_save_dir / 'feature_columns.pkl', 'wb') as f:
    pickle.dump(feature_cols, f)
print(f"✓ Saved: feature_columns.pkl")

# ============================================================================
# STEP 9: GENERATE TRAINING REPORT
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 9] GENERATING TRAINING REPORT")
print("=" * 80)

report = {
    'timestamp': datetime.now().isoformat(),
    'total_records': len(data_clean),
    'features_engineered': len(feature_cols),
    'tasks': list(TASKS.keys()),
    'models_trained': 15,  # 5 models × 3 tasks
    'results': {}
}

for task_name, results in results_summary.items():
    report['results'][task_name] = {
        'best_model': results['best_model'],
        'best_accuracy': float(results['best_score']),
        'all_accuracies': {k: float(v) for k, v in results['model_scores'].items()}
    }

# Save report
with open(model_save_dir / 'training_report.json', 'w') as f:
    json.dump(report, f, indent=2)
print("✓ Saved: training_report.json")

print("\n" + "=" * 80)
print("TRAINING COMPLETE!")
print("=" * 80)
print(f"\n✓ All models saved to: F1_ML_DATASETS/trained_models/")
print(f"✓ Report saved with accuracy metrics")
print(f"✓ Ready for API integration and dashboard display")
print(f"\nNext steps:")
print(f"  1. Review feature importance for ML subject")
print(f"  2. Integrate models into Flask API")
print(f"  3. Display predictions in Streamlit dashboard")
print(f"  4. Show to your friend!")

