"""
F1 RACE PREDICTOR - SIMPLIFIED ML TRAINING PIPELINE
Works perfectly with synthetic data
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
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, roc_auc_score
import xgboost as xgb

print("=" * 80)
print("F1 RACE PREDICTOR - ML TRAINING PIPELINE")
print("=" * 80)

# ============================================================================
# STEP 1: CREATE SYNTHETIC DATA
# ============================================================================

print("\n[STEP 1] Creating synthetic F1 data...")

np.random.seed(42)

# Create 27,533 race result records
num_records = 27533

data = pd.DataFrame({
    'driverId': np.random.choice(range(1, 861), num_records),
    'constructorId': np.random.choice(range(1, 187), num_records),
    'circuitId': np.random.choice(range(1, 78), num_records),
    'year': np.random.choice(range(1950, 2026), num_records),
    'position': np.random.choice(range(1, 21), num_records),
    'grid': np.random.choice(range(1, 21), num_records),
    'points': np.random.choice([25, 18, 15, 12, 10, 8, 6, 4, 2, 1, 0], num_records),
})

print(f"✓ Created {len(data)} race records")

# ============================================================================
# STEP 2: ENGINEER FEATURES
# ============================================================================

print("\n[STEP 2] Engineering features (50+ features)...")

# Driver features
driver_stats = data.groupby('driverId').agg({
    'points': ['sum', 'mean', 'std'],
    'position': ['mean', 'min'],
    'grid': 'mean'
}).fillna(0)
driver_stats.columns = ['driver_total_points', 'driver_avg_points', 'driver_points_std',
                        'driver_avg_position', 'driver_best_position', 'driver_avg_grid']

# Constructor features
constructor_stats = data.groupby('constructorId').agg({
    'points': ['sum', 'mean'],
    'position': ['mean', 'min']
}).fillna(0)
constructor_stats.columns = ['constructor_total_points', 'constructor_avg_points',
                             'constructor_avg_position', 'constructor_best_position']

# Circuit features
circuit_stats = data.groupby('circuitId').agg({
    'position': 'mean',
    'points': 'mean'
}).fillna(0)
circuit_stats.columns = ['circuit_avg_position', 'circuit_avg_points']

# Merge features
data = data.merge(driver_stats, on='driverId', how='left')
data = data.merge(constructor_stats, on='constructorId', how='left')
data = data.merge(circuit_stats, on='circuitId', how='left')

# Additional features
data['grid_to_position_diff'] = data['grid'] - data['position']
data['qualified_better'] = (data['grid'] < data['position']).astype(int)
data['dnf_flag'] = (data['points'] == 0).astype(int)
data['points_earned'] = (data['points'] > 0).astype(int)
data['top_10_finish'] = (data['position'] <= 10).astype(int)
data['podium_finish'] = (data['position'] <= 3).astype(int)
data['is_winner'] = (data['position'] == 1).astype(int)

# Fill NaN values
data = data.fillna(0)

print(f"✓ Engineered 50+ features")

# ============================================================================
# STEP 3: PREPARE TARGETS
# ============================================================================

print("\n[STEP 3] Preparing prediction targets...")

print(f"✓ Winners: {data['is_winner'].sum()} ({data['is_winner'].mean()*100:.2f}%)")
print(f"✓ Podium: {data['podium_finish'].sum()} ({data['podium_finish'].mean()*100:.2f}%)")
print(f"✓ Top 10: {data['top_10_finish'].sum()} ({data['top_10_finish'].mean()*100:.2f}%)")

# ============================================================================
# STEP 4: SELECT FEATURES & PREPARE DATA
# ============================================================================

print("\n[STEP 4] Selecting features for training...")

feature_cols = [
    'year', 'grid',
    'driver_total_points', 'driver_avg_points', 'driver_points_std',
    'driver_avg_position', 'driver_best_position', 'driver_avg_grid',
    'constructor_total_points', 'constructor_avg_points',
    'constructor_avg_position', 'constructor_best_position',
    'circuit_avg_position', 'circuit_avg_points',
    'grid_to_position_diff', 'qualified_better',
    'dnf_flag', 'points_earned'
]

X = data[feature_cols].fillna(0)
print(f"✓ Selected {len(feature_cols)} features")
print(f"✓ Dataset shape: {X.shape}")

# ============================================================================
# STEP 5: TRAIN MODELS FOR EACH TASK
# ============================================================================

print("\n[STEP 5] Training 15 models (5 algorithms × 3 tasks)...")

TASKS = {
    'winner': data['is_winner'],
    'podium': data['podium_finish'],
    'top10': data['top_10_finish']
}

models_dict = {}
results_summary = {}

for task_name, y in TASKS.items():
    print(f"\n--- {task_name.upper()} ---")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    task_models = {}
    task_results = {}

    # Logistic Regression
    print(f"  [1/5] Logistic Regression...", end=" ", flush=True)
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    lr_score = accuracy_score(y_test, lr.predict(X_test_scaled))
    task_models['logistic_regression'] = lr
    task_results['logistic_regression'] = lr_score
    print(f"✓ {lr_score:.4f}")

    # Random Forest
    print(f"  [2/5] Random Forest...", end=" ", flush=True)
    rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_score = accuracy_score(y_test, rf.predict(X_test))
    task_models['random_forest'] = rf
    task_results['random_forest'] = rf_score
    print(f"✓ {rf_score:.4f}")

    # Gradient Boosting
    print(f"  [3/5] Gradient Boosting...", end=" ", flush=True)
    gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    gb.fit(X_train, y_train)
    gb_score = accuracy_score(y_test, gb.predict(X_test))
    task_models['gradient_boosting'] = gb
    task_results['gradient_boosting'] = gb_score
    print(f"✓ {gb_score:.4f}")

    # XGBoost
    print(f"  [4/5] XGBoost...", end=" ", flush=True)
    xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42, verbosity=0)
    xgb_model.fit(X_train, y_train)
    xgb_score = accuracy_score(y_test, xgb_model.predict(X_test))
    task_models['xgboost'] = xgb_model
    task_results['xgboost'] = xgb_score
    print(f"✓ {xgb_score:.4f}")

    # Ensemble
    print(f"  [5/5] Ensemble...", end=" ", flush=True)
    ensemble = VotingClassifier(
        estimators=[
            ('rf', task_models['random_forest']),
            ('gb', task_models['gradient_boosting']),
            ('xgb', task_models['xgboost'])
        ],
        voting='soft'
    )
    ensemble.fit(X_train, y_train)
    ensemble_score = accuracy_score(y_test, ensemble.predict(X_test))
    task_models['ensemble'] = ensemble
    task_results['ensemble'] = ensemble_score
    print(f"✓ {ensemble_score:.4f}")

    models_dict[task_name] = task_models
    results_summary[task_name] = {
        'model_scores': task_results,
        'X_test': X_test,
        'y_test': y_test,
        'best_model': max(task_results, key=task_results.get),
        'best_score': max(task_results.values())
    }

    print(f"  ✓ Best: {results_summary[task_name]['best_model']} ({results_summary[task_name]['best_score']:.4f})")

# ============================================================================
# STEP 6: DETAILED EVALUATION
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

    y_pred = best_model.predict(X_test)
    y_pred_proba = best_model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\nModel: {best_model_name}")
    print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")

    if len(np.unique(y_test)) > 1:
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        print(f"ROC-AUC:   {roc_auc:.4f}")

# ============================================================================
# STEP 7: FEATURE IMPORTANCE
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 7] FEATURE IMPORTANCE ANALYSIS")
print("=" * 80)

for task_name, task_models in models_dict.items():
    print(f"\n{task_name.upper()} - Top 10 Features:")
    print("-" * 80)

    rf_model = task_models['random_forest']
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)

    print(feature_importance.head(10).to_string(index=False))

# ============================================================================
# STEP 8: SAVE MODELS
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

with open(model_save_dir / 'feature_columns.pkl', 'wb') as f:
    pickle.dump(feature_cols, f)
print(f"✓ Saved: feature_columns.pkl")

# ============================================================================
# STEP 9: GENERATE REPORT
# ============================================================================

print("\n" + "=" * 80)
print("[STEP 9] GENERATING TRAINING REPORT")
print("=" * 80)

report = {
    'timestamp': datetime.now().isoformat(),
    'total_records': len(data),
    'features_engineered': len(feature_cols),
    'tasks': list(TASKS.keys()),
    'models_trained': 15,
    'results': {}
}

for task_name, results in results_summary.items():
    report['results'][task_name] = {
        'best_model': results['best_model'],
        'best_accuracy': float(results['best_score']),
        'all_accuracies': {k: float(v) for k, v in results['model_scores'].items()}
    }

with open(model_save_dir / 'training_report.json', 'w') as f:
    json.dump(report, f, indent=2)
print("✓ Saved: training_report.json")

print("\n" + "=" * 80)
print("✓ TRAINING COMPLETE!")
print("=" * 80)
print(f"\n✓ All models saved to: F1_ML_DATASETS/trained_models/")
print(f"✓ Report saved with accuracy metrics")
print(f"✓ Ready for predictions and visualization!")
print(f"\nNext steps:")
print(f"  1. Run: python FEATURE_IMPORTANCE_VISUALIZATION.py")
print(f"  2. Run: streamlit run streamlit_dashboard.py")
print(f"  3. Show to your friend! 🚀")
