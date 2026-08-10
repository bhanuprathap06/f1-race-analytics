#!/usr/bin/env python3
"""
Advanced ML Models Training - Ensemble & Comparison
Trains multiple algorithms and compares performance
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print("ADVANCED ML MODELS TRAINING & COMPARISON")
print("="*80 + "\n")

# Load data
print("Loading data...")
df = pd.read_csv('processed_data/01_race_prediction_dataset.csv')

# Prepare features
feature_cols = ['positionNumber', 'gridPositionNumber', 'points', 'driverNumber', 'laps']
feature_cols = [col for col in feature_cols if col in df.columns]

X = df[feature_cols].copy()
X = X.fillna(X.mean())

y_winner = df['winner'].copy()
y_podium = df['podium'].copy()

# Split data
X_train, X_test, y_w_train, y_w_test, y_p_train, y_p_test = train_test_split(
    X, y_winner, y_podium, test_size=0.2, random_state=42
)

print(f"Training set: {len(X_train):,} samples")
print(f"Test set: {len(X_test):,} samples\n")

# ============================================================================
# TRAIN MULTIPLE MODELS
# ============================================================================

models = {}
results = []

print("Training models for WINNER PREDICTION:\n")

# Model 1: Logistic Regression
print("  1. Logistic Regression...")
lr = LogisticRegression(max_iter=1000, random_state=42)
lr.fit(X_train, y_w_train)
pred_lr = lr.predict(X_test)
acc_lr = accuracy_score(y_w_test, pred_lr)
prec_lr = precision_score(y_w_test, pred_lr, zero_division=0)
rec_lr = recall_score(y_w_test, pred_lr, zero_division=0)
f1_lr = f1_score(y_w_test, pred_lr, zero_division=0)
models['Logistic Regression'] = lr
results.append({
    'Model': 'Logistic Regression',
    'Accuracy': acc_lr,
    'Precision': prec_lr,
    'Recall': rec_lr,
    'F1-Score': f1_lr
})
print(f"     ✓ Accuracy: {acc_lr*100:.2f}%\n")

# Model 2: Random Forest
print("  2. Random Forest...")
rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X_train, y_w_train)
pred_rf = rf.predict(X_test)
acc_rf = accuracy_score(y_w_test, pred_rf)
prec_rf = precision_score(y_w_test, pred_rf, zero_division=0)
rec_rf = recall_score(y_w_test, pred_rf, zero_division=0)
f1_rf = f1_score(y_w_test, pred_rf, zero_division=0)
models['Random Forest'] = rf
results.append({
    'Model': 'Random Forest',
    'Accuracy': acc_rf,
    'Precision': prec_rf,
    'Recall': rec_rf,
    'F1-Score': f1_rf
})
print(f"     ✓ Accuracy: {acc_rf*100:.2f}%\n")

# Model 3: Gradient Boosting
print("  3. Gradient Boosting...")
gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
gb.fit(X_train, y_w_train)
pred_gb = gb.predict(X_test)
acc_gb = accuracy_score(y_w_test, pred_gb)
prec_gb = precision_score(y_w_test, pred_gb, zero_division=0)
rec_gb = recall_score(y_w_test, pred_gb, zero_division=0)
f1_gb = f1_score(y_w_test, pred_gb, zero_division=0)
models['Gradient Boosting'] = gb
results.append({
    'Model': 'Gradient Boosting',
    'Accuracy': acc_gb,
    'Precision': prec_gb,
    'Recall': rec_gb,
    'F1-Score': f1_gb
})
print(f"     ✓ Accuracy: {acc_gb*100:.2f}%\n")

# Model 4: XGBoost
print("  4. XGBoost...")
xgb = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbosity=0)
xgb.fit(X_train, y_w_train)
pred_xgb = xgb.predict(X_test)
acc_xgb = accuracy_score(y_w_test, pred_xgb)
prec_xgb = precision_score(y_w_test, pred_xgb, zero_division=0)
rec_xgb = recall_score(y_w_test, pred_xgb, zero_division=0)
f1_xgb = f1_score(y_w_test, pred_xgb, zero_division=0)
models['XGBoost'] = xgb
results.append({
    'Model': 'XGBoost',
    'Accuracy': acc_xgb,
    'Precision': prec_xgb,
    'Recall': rec_xgb,
    'F1-Score': f1_xgb
})
print(f"     ✓ Accuracy: {acc_xgb*100:.2f}%\n")

# Model 5: Ensemble (Voting Classifier)
print("  5. Ensemble (Voting Classifier)...")
ensemble = VotingClassifier(
    estimators=[('lr', lr), ('rf', rf), ('gb', gb), ('xgb', xgb)],
    voting='soft'
)
ensemble.fit(X_train, y_w_train)
pred_ensemble = ensemble.predict(X_test)
acc_ensemble = accuracy_score(y_w_test, pred_ensemble)
prec_ensemble = precision_score(y_w_test, pred_ensemble, zero_division=0)
rec_ensemble = recall_score(y_w_test, pred_ensemble, zero_division=0)
f1_ensemble = f1_score(y_w_test, pred_ensemble, zero_division=0)
models['Ensemble'] = ensemble
results.append({
    'Model': 'Ensemble',
    'Accuracy': acc_ensemble,
    'Precision': prec_ensemble,
    'Recall': rec_ensemble,
    'F1-Score': f1_ensemble
})
print(f"     ✓ Accuracy: {acc_ensemble*100:.2f}%\n")

# ============================================================================
# RESULTS SUMMARY
# ============================================================================

print("="*80)
print("RESULTS SUMMARY - WINNER PREDICTION")
print("="*80 + "\n")

results_df = pd.DataFrame(results)
results_df['Accuracy'] = (results_df['Accuracy'] * 100).round(2)
results_df['Precision'] = (results_df['Precision'] * 100).round(2)
results_df['Recall'] = (results_df['Recall'] * 100).round(2)
results_df['F1-Score'] = (results_df['F1-Score'] * 100).round(2)

print(results_df.to_string(index=False))
print()

# Find best model
best_model = results_df.loc[results_df['Accuracy'].idxmax()]
print(f"\n🏆 BEST MODEL: {best_model['Model']}")
print(f"   Accuracy: {best_model['Accuracy']:.2f}%")
print(f"   Precision: {best_model['Precision']:.2f}%")
print(f"   Recall: {best_model['Recall']:.2f}%")
print(f"   F1-Score: {best_model['F1-Score']:.2f}%\n")

# Save results
results_df.to_csv('processed_data/advanced_models_comparison.csv', index=False)
print("✓ Results saved to: advanced_models_comparison.csv\n")

# ============================================================================
# FEATURE IMPORTANCE COMPARISON
# ============================================================================

print("="*80)
print("FEATURE IMPORTANCE COMPARISON")
print("="*80 + "\n")

print("XGBoost Feature Importance:")
xgb_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': xgb.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in xgb_importance.iterrows():
    bar = "█" * int(row['importance'] * 60)
    print(f"  {row['feature']:20} {bar} {row['importance']:.4f}")

print("\n\nRandom Forest Feature Importance:")
rf_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in rf_importance.iterrows():
    bar = "█" * int(row['importance'] * 60)
    print(f"  {row['feature']:20} {bar} {row['importance']:.4f}")

print("\n\nGradient Boosting Feature Importance:")
gb_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': gb.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in gb_importance.iterrows():
    bar = "█" * int(row['importance'] * 60)
    print(f"  {row['feature']:20} {bar} {row['importance']:.4f}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("✅ ADVANCED MODELS TRAINING COMPLETE")
print("="*80 + "\n")

print("Summary:")
print(f"  • Trained 5 models")
print(f"  • Tested on {len(X_test):,} samples")
print(f"  • Best model: {best_model['Model']}")
print(f"  • Best accuracy: {best_model['Accuracy']:.2f}%")
ensemble_acc = results_df[results_df['Model']=='Ensemble']['Accuracy'].values[0]
print(f"  • Ensemble model accuracy: {ensemble_acc:.2f}%")
print(f"\n  Results saved to: processed_data/advanced_models_comparison.csv\n")

print("Next steps:")
print("  1. Run REST API server: python3 api_server.py")
print("  2. Make predictions via API")
print("  3. Deploy for production\n")
