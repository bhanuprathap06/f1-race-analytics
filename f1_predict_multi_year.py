import pickle
import pandas as pd
import numpy as np
from pathlib import Path

model_dir = Path('F1_ML_DATASETS/trained_models')
with open(model_dir / 'feature_columns.pkl', 'rb') as f:
    features = pickle.load(f)
with open(model_dir / 'winner_stacking_ensemble.pkl', 'rb') as f:
    model = pickle.load(f)
with open(model_dir / 'winner_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Seasons database
seasons = {
    2024: {
        'drivers': [
            ('Max Verstappen', 'Red Bull', 287, 14.35),
            ('Lewis Hamilton', 'Mercedes', 175, 8.75),
            ('Charles Leclerc', 'Ferrari', 210, 10.50),
        ],
        'races': [
            ('Bahrain', 0.45),
            ('Saudi Arabia', 0.50),
            ('Australia', 0.40),
        ]
    },
    2025: {
        'drivers': [
            ('Max Verstappen', 'Red Bull', 320, 16.00),
            ('Lewis Hamilton', 'Ferrari', 200, 10.00),
            ('Charles Leclerc', 'Ferrari', 210, 10.50),
        ],
        'races': [
            ('Bahrain', 0.45),
            ('Saudi Arabia', 0.50),
            ('Australia', 0.40),
        ]
    },
    2026: {
        'drivers': [
            ('Max Verstappen', 'Red Bull', 350, 17.50),
            ('Lando Norris', 'McLaren', 280, 14.00),
        ],
        'races': [
            ('Bahrain', 0.45),
            ('Saudi Arabia', 0.50),
        ]
    }
}

# Select year
YEAR = 2021

print("="*90)
print(f"{YEAR} F1 SEASON - WINNER PREDICTIONS")
print("="*90)

season_data = seasons[2021]

for circuit_name, difficulty in season_data['races']:
    print(f"\n🏁 {circuit_name.upper()}")
    print("-" * 90)

    predictions = []

    for driver_name, team, total_pts, avg_pts in season_data['drivers']:
        base_prob = (avg_pts / 15.0) * (1 - difficulty * 0.25)
        win_prob = min(0.95, max(0.01, base_prob))

        predictions.append({
            'driver': driver_name,
            'team': team,
            'win': win_prob,
            'pts': avg_pts
        })

    predictions.sort(key=lambda x: x['win'], reverse=True)

    for rank, pred in enumerate(predictions[:5], 1):
        win_pct = pred['win'] * 100
        icon = "🥇" if win_pct > 70 else "🟢" if win_pct > 50 else "🟡" if win_pct > 25 else "🔴"
        print(f"  {rank}. {icon} {pred['driver']:18} {win_pct:5.1f}%  {pred['team']}")

print("\n" + "="*90)
