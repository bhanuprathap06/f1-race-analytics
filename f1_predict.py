import pickle
from pathlib import Path

model_dir = Path('F1_ML_DATASETS/trained_models')
with open(model_dir / 'feature_columns.pkl', 'rb') as f:
    features = pickle.load(f)
with open(model_dir / 'winner_stacking_ensemble.pkl', 'rb') as f:
    model = pickle.load(f)
with open(model_dir / 'winner_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

seasons = {
    2020: {
        'drivers': [('Lewis Hamilton', 'Mercedes', 347, 17.35), ('Max Verstappen', 'Red Bull', 214, 10.70)],
        'races': [('Austria', 0.38), ('Hungary', 0.48), ('Silverstone', 0.40)]
    },
    2021: {
        'drivers': [('Max Verstappen', 'Red Bull', 395, 19.75), ('Lewis Hamilton', 'Mercedes', 387, 19.35)],
        'races': [('Bahrain', 0.45), ('Imola', 0.55), ('Portugal', 0.52)]
    },
    2022: {
        'drivers': [('Max Verstappen', 'Red Bull', 454, 22.70), ('Charles Leclerc', 'Ferrari', 308, 15.40)],
        'races': [('Bahrain', 0.45), ('Saudi Arabia', 0.50), ('Australia', 0.40)]
    },
    2023: {
        'drivers': [('Max Verstappen', 'Red Bull', 575, 18.55), ('Charles Leclerc', 'Ferrari', 308, 9.94)],
        'races': [('Bahrain', 0.45), ('Saudi Arabia', 0.50), ('Australia', 0.40)]
    },
    2024: {
        'drivers': [('Max Verstappen', 'Red Bull', 287, 14.35), ('Lewis Hamilton', 'Mercedes', 175, 8.75)],
        'races': [('Bahrain', 0.45), ('Saudi Arabia', 0.50), ('Australia', 0.40)]
    },
}

YEAR = 2020

if YEAR not in seasons:
    print(f"Year {YEAR} not available. Use: {list(seasons.keys())}")
else:
    print(f"{'='*80}\n{YEAR} F1 PREDICTIONS\n{'='*80}")
    for circuit, difficulty in seasons[YEAR]['races']:
        print(f"\n{circuit}")
        predictions = []
        for driver, team, total_pts, avg_pts in seasons[YEAR]['drivers']:
            prob = min(0.95, max(0.01, (avg_pts/15) * (1 - difficulty*0.25)))
            predictions.append((driver, team, prob*100, avg_pts))
        predictions.sort(key=lambda x: x[2], reverse=True)
        for rank, (driver, team, pct, pts) in enumerate(predictions, 1):
            icon = "🥇" if pct > 70 else "🟢" if pct > 50 else "🟡"
            print(f"  {rank}. {icon} {driver:15} {pct:5.1f}%")
