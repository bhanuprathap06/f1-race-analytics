"""
================================================================================
F1 RACE PREDICTOR - PREDICT SPECIFIC DRIVER PERFORMANCE
Predict whether a specific driver will win, podium, or finish top-10
================================================================================

Example: Will Lewis Hamilton win the next Grand Prix?
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path

print("="*80)
print("F1 RACE PREDICTOR - DRIVER-SPECIFIC PREDICTIONS")
print("="*80)

# ============================================================================
# STEP 1: LOAD TRAINED MODELS
# ============================================================================

print("\n[STEP 1] Loading trained models...")

model_dir = Path('F1_ML_DATASETS/trained_models')

# Load feature columns and models
with open(model_dir / 'feature_columns.pkl', 'rb') as f:
    feature_cols = pickle.load(f)

with open(model_dir / 'winner_stacking_ensemble.pkl', 'rb') as f:
    winner_model = pickle.load(f)
with open(model_dir / 'winner_scaler.pkl', 'rb') as f:
    winner_scaler = pickle.load(f)

with open(model_dir / 'podium_stacking_ensemble.pkl', 'rb') as f:
    podium_model = pickle.load(f)
with open(model_dir / 'podium_scaler.pkl', 'rb') as f:
    podium_scaler = pickle.load(f)

with open(model_dir / 'top_10_stacking_ensemble.pkl', 'rb') as f:
    top10_model = pickle.load(f)
with open(model_dir / 'top_10_scaler.pkl', 'rb') as f:
    top10_scaler = pickle.load(f)

print(f"✓ Models loaded successfully")

# ============================================================================
# STEP 2: CREATE DRIVER PROFILE - LEWIS HAMILTON EXAMPLE
# ============================================================================

print("\n[STEP 2] Creating driver profile for prediction...")

# Lewis Hamilton 2024 Season Statistics (Example Data)
# In practice, you'd fetch this from official F1 data sources

driver_profile = {
    'driver_name': 'Lewis Hamilton',
    'constructor': 'Mercedes',
    'circuit': 'Monaco Grand Prix',
    'year': 2024,

    # Current 2024 statistics (as of mid-season)
    'driver_total_points': 175,          # Total career points
    'driver_avg_points': 8.75,           # Average points per race this season
    'driver_points_std': 4.2,            # Consistency (std deviation)
    'driver_avg_position': 4.2,          # Average finishing position
    'driver_best_position': 1,           # Best position ever
    'driver_worst_position': 20,         # Worst position this season
    'driver_position_std': 3.5,          # Position consistency
    'driver_avg_grid': 3.1,              # Average grid position (qualifying)
    'driver_grid_std': 1.8,              # Grid consistency
    'driver_best_grid': 1,               # Best qualifying position
    'driver_worst_grid': 15,             # Worst qualifying this season
    'driver_races_count': 20,            # Races completed this season

    # Mercedes 2024 Statistics
    'constructor_total_points': 450,     # Team total
    'constructor_avg_points': 22.5,      # Team average per race
    'constructor_points_std': 8.5,       # Team consistency
    'constructor_avg_position': 3.2,     # Team average position
    'constructor_best_position': 1,      # Best team result
    'constructor_position_std': 2.8,     # Team position variance
    'constructor_avg_grid': 2.9,         # Team qualifying average
    'constructor_races_count': 20,       # Team races completed

    # Monaco specific statistics
    'circuit_avg_position': 5.2,         # Average finish position at Monaco
    'circuit_position_std': 3.1,         # Variance at Monaco
    'circuit_avg_points': 6.5,           # Average points at Monaco
    'circuit_points_std': 5.2,           # Points variance at Monaco
    'circuit_avg_grid': 4.3,             # Average grid at Monaco
    'circuit_difficulty': 0.75,          # Monaco difficulty (0-1 scale)
    'circuit_races_count': 5,            # Races at Monaco

    # Performance metrics
    'grid_to_position_diff': -2.1,       # Typically qualifies better than finishes
    'qualified_better': 1,               # Did better than qualifying suggests (1=yes)
    'qualified_worse': 0,                # Did worse than qualifying suggests
    'dnf_flag': 0,                       # Did not finish (0=finished)
    'points_earned': 1,                  # Earned points (1=yes)

    # Derived features
    'driver_consistency': 1.8,            # Inverse of std dev (higher=consistent)
    'constructor_consistency': 1.5,      # Team consistency
    'driver_performance_ratio': 0.44,    # Points per race average
    'constructor_performance_ratio': 1.13,
    'driver_grid_improvement': 0.3,      # Grid pos - Finish pos (positive=improved)
    'driver_constructor_synergy': 98.4,  # Driver × Constructor interaction
    'driver_circuit_affinity': 0.9,      # Driver fit for this circuit (0-1)

    # Rolling averages (last 5 races)
    'driver_rolling_points_5': 9.2,      # Avg points last 5 races
    'driver_rolling_grid_5': 3.3,        # Avg grid position last 5 races
    'constructor_rolling_points_5': 24.1,
}

print(f"✓ Created profile for: {driver_profile['driver_name']}")
print(f"  Constructor: {driver_profile['constructor']}")
print(f"  Circuit: {driver_profile['circuit']}")
print(f"  Season: {driver_profile['year']}")

# ============================================================================
# STEP 3: PREPARE DATA FOR MODEL
# ============================================================================

print("\n[STEP 3] Preparing data for prediction...")

# Create DataFrame with features in correct order
prediction_data = pd.DataFrame({
    feature: [driver_profile.get(feature, 0)] for feature in feature_cols
})

print(f"✓ Prepared {len(feature_cols)} features")
print(f"✓ Data shape: {prediction_data.shape}")

# ============================================================================
# STEP 4: MAKE PREDICTIONS
# ============================================================================

print("\n[STEP 4] Making race outcome predictions...")
print("-"*80)

# PREDICTION 1: Race Winner
print(f"\n1️⃣  RACE WINNER PREDICTION:")
X_winner = winner_scaler.transform(prediction_data[feature_cols])
winner_prob = winner_model.predict_proba(X_winner)[0][1]
winner_pred = winner_model.predict(X_winner)[0]

print(f"   {driver_profile['driver_name']} WINNING probability: {winner_prob*100:.1f}%")
if winner_prob >= 0.5:
    print(f"   Prediction: ✓ LIKELY TO WIN")
else:
    print(f"   Prediction: ✗ UNLIKELY TO WIN")

# PREDICTION 2: Podium Finish
print(f"\n2️⃣  PODIUM FINISH PREDICTION (Top 3):")
X_podium = podium_scaler.transform(prediction_data[feature_cols])
podium_prob = podium_model.predict_proba(X_podium)[0][1]
podium_pred = podium_model.predict(X_podium)[0]

print(f"   {driver_profile['driver_name']} PODIUM probability: {podium_prob*100:.1f}%")
if podium_prob >= 0.5:
    print(f"   Prediction: ✓ LIKELY PODIUM")
else:
    print(f"   Prediction: ✗ UNLIKELY PODIUM")

# PREDICTION 3: Top-10 Finish
print(f"\n3️⃣  TOP-10 FINISH PREDICTION:")
X_top10 = top10_scaler.transform(prediction_data[feature_cols])
top10_prob = top10_model.predict_proba(X_top10)[0][1]
top10_pred = top10_model.predict(X_top10)[0]

print(f"   {driver_profile['driver_name']} TOP-10 probability: {top10_prob*100:.1f}%")
if top10_prob >= 0.5:
    print(f"   Prediction: ✓ LIKELY TOP-10")
else:
    print(f"   Prediction: ✗ UNLIKELY TOP-10")

# ============================================================================
# STEP 5: CONFIDENCE ANALYSIS
# ============================================================================

print("\n[STEP 5] Confidence & Risk Analysis...")
print("-"*80)

print(f"\nPrediction Confidence Levels:")
print(f"  Winner Confidence:    {abs(winner_prob - 0.5) * 2 * 100:.1f}%")
print(f"  Podium Confidence:    {abs(podium_prob - 0.5) * 2 * 100:.1f}%")
print(f"  Top-10 Confidence:    {abs(top10_prob - 0.5) * 2 * 100:.1f}%")

print(f"\nProbability Distribution:")
print(f"  Winner:   [{winner_prob*100:5.1f}%] {'█' * int(winner_prob*50)}")
print(f"  Podium:   [{podium_prob*100:5.1f}%] {'█' * int(podium_prob*50)}")
print(f"  Top-10:   [{top10_prob*100:5.1f}%] {'█' * int(top10_prob*50)}")

# ============================================================================
# STEP 6: KEY FACTORS INFLUENCING PREDICTION
# ============================================================================

print("\n[STEP 6] Key Factors Influencing Prediction...")
print("-"*80)

factors = {
    'Positive Factors': [
        f"Driver avg grid position: {driver_profile['driver_avg_grid']:.1f} (Good qualifying)",
        f"Driver consistency: {driver_profile['driver_consistency']:.2f} (Reliable)",
        f"Driver-Circuit affinity: {driver_profile['driver_circuit_affinity']:.2f}/1.0 (Strong fit)",
        f"Constructor performance: {driver_profile['constructor_performance_ratio']:.2f} (Competitive)",
    ],
    'Risk Factors': [
        f"Points per race variance: {driver_profile['driver_points_std']:.1f} (Inconsistent)",
        f"Finish position variance: {driver_profile['driver_position_std']:.1f} (Unpredictable)",
        f"Circuit difficulty: {driver_profile['circuit_difficulty']:.2f}/1.0 (Challenging)",
    ]
}

print("\n✓ POSITIVE FACTORS:")
for factor in factors['Positive Factors']:
    print(f"  • {factor}")

print("\n⚠ RISK FACTORS:")
for factor in factors['Risk Factors']:
    print(f"  • {factor}")

# ============================================================================
# STEP 7: FINAL RECOMMENDATION
# ============================================================================

print("\n[STEP 7] Final Prediction Summary...")
print("="*80)

# Determine overall outlook
scores = [winner_prob, podium_prob, top10_prob]
avg_score = np.mean(scores)

print(f"\n🏎️  RACE OUTLOOK FOR {driver_profile['driver_name']}:")
print(f"    at {driver_profile['circuit']} 2024\n")

if winner_prob > 0.7:
    print(f"  🥇 STRONG FAVORITE TO WIN")
elif winner_prob > 0.5:
    print(f"  🟢 GOOD CHANCE TO WIN")
elif podium_prob > 0.7:
    print(f"  🥈 LIKELY PODIUM FINISH")
elif podium_prob > 0.5:
    print(f"  🟡 POSSIBLE PODIUM")
elif top10_prob > 0.7:
    print(f"  🟢 STRONG CHANCE TOP-10")
else:
    print(f"  🔴 CHALLENGING RACE AHEAD")

print(f"\n  Win Probability:     {winner_prob*100:5.1f}%")
print(f"  Podium Probability:  {podium_prob*100:5.1f}%")
print(f"  Top-10 Probability:  {top10_prob*100:5.1f}%")

print(f"\n  Best Expected Finish: ", end="")
if winner_prob == max(scores):
    print("Victory 🏆")
elif podium_prob == max(scores):
    print("Podium 🥈")
else:
    print("Top-10 🎯")

print("\n" + "="*80)
print("✓ PREDICTION COMPLETE")
print("="*80)

# ============================================================================
# STEP 8: HOW TO USE FOR OTHER DRIVERS
# ============================================================================

print("\n[STEP 8] How to predict for OTHER DRIVERS:")
print("-"*80)

print("""
To predict for any driver, modify the 'driver_profile' dictionary above:

1. Change driver statistics:
   - 'driver_name': 'Max Verstappen'
   - 'driver_total_points': [actual points]
   - 'driver_avg_points': [2024 season average]
   - etc.

2. Change team statistics (constructor):
   - 'constructor': 'Red Bull Racing'
   - 'constructor_total_points': [team total]
   - etc.

3. Change circuit:
   - 'circuit': 'Silverstone Grand Prix'
   - 'circuit_avg_position': [historical avg at this track]
   - etc.

4. Re-run the script to get new predictions

Example drivers to try:
  ✓ Max Verstappen (Red Bull)
  ✓ Carlos Sainz (Ferrari)
  ✓ Lando Norris (McLaren)
  ✓ Charles Leclerc (Ferrari)
  ✓ Sergio Perez (Red Bull)
""")

print("="*80)
