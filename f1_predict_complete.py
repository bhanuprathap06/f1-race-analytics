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
    2015: {
        'drivers': [
            ('Lewis Hamilton', 'Mercedes', 381, 19.05),
            ('Sebastian Vettel', 'Ferrari', 278, 13.90),
            ('Kimi Räikkönen', 'Ferrari', 150, 7.50),
            ('Valtteri Bottas', 'Williams', 247, 12.35),
        ],
        'races': [('Australia', 0.40), ('Malaysia', 0.48), ('China', 0.35), ('Bahrain', 0.45)]
    },
    2016: {
        'drivers': [
            ('Lewis Hamilton', 'Mercedes', 473, 23.65),
            ('Nico Rosberg', 'Mercedes', 385, 19.25),
            ('Sebastian Vettel', 'Ferrari', 212, 10.60),
            ('Max Verstappen', 'Red Bull', 256, 12.80),
        ],
        'races': [('Australia', 0.40), ('Bahrain', 0.45), ('China', 0.35), ('Russia', 0.42)]
    },
    2017: {
        'drivers': [
            ('Lewis Hamilton', 'Mercedes', 363, 18.15),
            ('Sebastian Vettel', 'Ferrari', 317, 15.85),
            ('Valtteri Bottas', 'Mercedes', 305, 15.25),
            ('Daniel Ricciardo', 'Red Bull', 200, 10.00),
        ],
        'races': [('Australia', 0.40), ('China', 0.35), ('Bahrain', 0.45), ('Russia', 0.42)]
    },
    2018: {
        'drivers': [
            ('Lewis Hamilton', 'Mercedes', 408, 20.40),
            ('Sebastian Vettel', 'Ferrari', 320, 16.00),
            ('Kimi Räikkönen', 'Ferrari', 251, 12.55),
            ('Max Verstappen', 'Red Bull', 249, 12.45),
        ],
        'races': [('Australia', 0.40), ('Bahrain', 0.45), ('China', 0.35), ('Azerbaijan', 0.52)]
    },
    2019: {
        'drivers': [
            ('Lewis Hamilton', 'Mercedes', 413, 20.65),
            ('Valtteri Bottas', 'Mercedes', 322, 16.10),
            ('Charles Leclerc', 'Ferrari', 264, 13.20),
            ('Sebastian Vettel', 'Ferrari', 240, 12.00),
        ],
        'races': [('Australia', 0.40), ('Bahrain', 0.45), ('China', 0.35), ('Azerbaijan', 0.52)]
    },
    2020: {
        'drivers': [
            ('Lewis Hamilton', 'Mercedes', 347, 17.35),
            ('Valtteri Bottas', 'Mercedes', 226, 11.30),
            ('Max Verstappen', 'Red Bull', 214, 10.70),
            ('Charles Leclerc', 'Ferrari', 98, 4.90),
        ],
        'races': [('Austria', 0.38), ('Styria', 0.42), ('Hungary', 0.48), ('Silverstone', 0.40)]
    },
    2021: {
        'drivers': [
            ('Max Verstappen', 'Red Bull', 395, 19.75),
            ('Lewis Hamilton', 'Mercedes', 387, 19.35),
            ('Valtteri Bottas', 'Mercedes', 226, 11.30),
            ('Charles Leclerc', 'Ferrari', 159, 7.95),
        ],
        'races': [('Bahrain', 0.45), ('Imola', 0.55), ('Portugal', 0.52), ('Spain', 0.60)]
    },
    2022: {
        'drivers': [
            ('Max Verstappen', 'Red Bull', 454, 22.70),
            ('Charles Leclerc', 'Ferrari', 308, 15.40),
            ('George Russell', 'Mercedes', 265, 13.25),
            ('Lewis Hamilton', 'Mercedes', 240, 12.00),
        ],
        'races': [('Bahrain', 0.45), ('Saudi Arabia', 0.50), ('Australia', 0.40), ('Emilia Romagna', 0.55)]
    },
    2023: {
        'drivers': [
            ('Max Verstappen', 'Red Bull', 575, 18.55),
            ('Charles Leclerc', 'Ferrari', 308, 9.94),
            ('George Russell', 'Mercedes', 275, 8.87),
            ('Lewis Hamilton', 'Mercedes', 290, 9.35),
        ],
        'races': [('Bahrain', 0.45), ('Saudi Arabia', 0.50), ('Australia', 0.40), ('Azerbaijan', 0.52)]
    },
    2024: {
        'drivers': [
            ('Max Verstappen', 'Red Bull', 287, 14.35),
            ('Lewis Hamilton', 'Mercedes', 175, 8.75),
            ('Charles Leclerc', 'Ferrari', 210, 10.50),
            ('Lando Norris', 'McLaren', 150, 7.50),
        ],
        'races': [('Bahrain', 0.45), ('Saudi Arabia', 0.50), ('Australia', 0.40), ('Japan', 0.55)]
    },
}

YEAR = 2024

if YEAR not in seasons:
    print(f"Year {YEAR} not available.")
    print(f"Available years: {sorted(seasons.keys())}")
else:
    print(f"{'='*90}\n{YEAR} F1 SEASON - WINNER PREDICTIONS\n{'='*90}")
    
    for circuit, difficulty in seasons[YEAR]['races']:
        print(f"\n🏁 {circuit.upper()}")
        print("-" * 90)
        
        predictions = []
        for driver, team, total_pts, avg_pts in seasons[YEAR]['drivers']:
            prob = min(0.95, max(0.01, (avg_pts / 15.0) * (1 - difficulty * 0.25)))
            predictions.append((driver, team, prob * 100, avg_pts))
        
        predictions.sort(key=lambda x: x[2], reverse=True)
        
        for rank, (driver, team, pct, pts) in enumerate(predictions, 1):
            if pct > 70:
                icon = "🥇"
            elif pct > 50:
                icon = "🟢"
            elif pct > 25:
                icon = "🟡"
            else:
                icon = "🔴"
            print(f"  {rank}. {icon} {driver:20} {pct:5.1f}%  ({pts:5.2f} pts)  {team}")
    
    print("\n" + "="*90)

print(f"\nAll available years: {sorted(seasons.keys())}")
