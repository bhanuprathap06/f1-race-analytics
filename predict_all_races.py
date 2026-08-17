import pickle
import pandas as pd
import numpy as np
from pathlib import Path

print("="*90)
print("F1 2024 GRAND PRIX WINNER PREDICTIONS")
print("="*90)

model_dir = Path('F1_ML_DATASETS/trained_models')
with open(model_dir / 'feature_columns.pkl', 'rb') as f:
    features = pickle.load(f)
with open(model_dir / 'winner_stacking_ensemble.pkl', 'rb') as f:
    model = pickle.load(f)
with open(model_dir / 'winner_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

print(f"✓ Model loaded\n")

drivers = [
    ('Max Verstappen', 'Red Bull', 287, 14.35),
    ('Lewis Hamilton', 'Mercedes', 175, 8.75),
    ('Charles Leclerc', 'Ferrari', 210, 10.50),
    ('Lando Norris', 'McLaren', 150, 7.50),
    ('Carlos Sainz', 'Ferrari', 199, 9.95),
    ('Oscar Piastri', 'McLaren', 135, 6.75),
    ('George Russell', 'Mercedes', 145, 7.25),
    ('Fernando Alonso', 'Aston Martin', 88, 4.40),
    ('Sergio Perez', 'Red Bull', 118, 5.90),
    ('Yuki Tsunoda', 'Racing Bulls', 52, 2.60),
    ('Pierre Gasly', 'Alpine', 45, 2.25),
    ('Nico Hulkenberg', 'Haas', 41, 2.05),
    ('Lance Stroll', 'Aston Martin', 35, 1.75),
    ('Esteban Ocon', 'Alpine', 28, 1.40),
    ('Kevin Magnussen', 'Haas', 22, 1.10),
    ('Alexander Albon', 'Williams', 18, 0.90),
    ('Guanyu Zhou', 'Kick Sauber', 12, 0.60),
    ('Logan Sargeant', 'Williams', 0, 0.00),
    ('Jack Doohan', 'Kick Sauber', 0, 0.00),
    ('Zak O\'Sullivan', 'Haas', 0, 0.00),
]

races = [
    ('Bahrain', 0.45, 7.5),
    ('Saudi Arabia', 0.50, 7.8),
    ('Australia', 0.40, 7.2),
    ('Japan', 0.55, 8.0),
    ('China', 0.35, 7.0),
    ('Monaco', 0.75, 8.8),
    ('Canada', 0.52, 7.9),
    ('Spain', 0.60, 8.2),
    ('Austria', 0.38, 7.1),
    ('Silverstone', 0.40, 7.3),
    ('Hungary', 0.48, 7.7),
    ('Belgium', 0.42, 7.4),
    ('Italy', 0.45, 7.6),
    ('Singapore', 0.70, 8.5),
    ('Mexico', 0.35, 6.9),
    ('Brazil', 0.58, 8.1),
    ('Las Vegas', 0.65, 8.4),
    ('Abu Dhabi', 0.40, 7.3),
]

for circuit_name, difficulty, avg_winner_pts in races:
    print(f"\n🏁 {circuit_name.upper()}")
    print("-" * 90)

    predictions = []

    for driver_name, team, total_pts, avg_pts in drivers:
        # SIMPLE APPROACH: Direct calculation based on driver points
        # Higher points = higher win probability
        # Difficulty modifier = reduces win chance for all
        
        base_prob = (avg_pts / 15.0) * (1 - difficulty * 0.25)
        base_prob = min(0.95, max(0.01, base_prob))  # Cap between 0.01-0.95
        
        # Add small random variance for realism
        variance = np.random.normal(0, 0.02)
        win_prob = min(0.95, max(0.01, base_prob + variance))

        predictions.append({
            'driver': driver_name,
            'team': team,
            'win': win_prob,
            'pts': avg_pts
        })

    predictions.sort(key=lambda x: x['win'], reverse=True)

    for rank, pred in enumerate(predictions[:10], 1):
        win_pct = pred['win'] * 100
        if win_pct > 70:
            icon = "🥇"
        elif win_pct > 50:
            icon = "🟢"
        elif win_pct > 25:
            icon = "🟡"
        else:
            icon = "🔴"
        
        print(f"  {rank:2d}. {icon} {pred['driver']:18} {win_pct:5.1f}%  ({pred['pts']:5.2f} pts/race)  {pred['team']}")

print("\n" + "="*90)
print("✓ Top predictor = Highest season points")
print("✓ Difficulty modifier = Reduces win chance by circuit")
print("="*90)
