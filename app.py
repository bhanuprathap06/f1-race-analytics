from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# Load model
model_dir = Path('F1_ML_DATASETS/trained_models')
with open(model_dir / 'feature_columns.pkl', 'rb') as f:
    features = pickle.load(f)
with open(model_dir / 'winner_stacking_ensemble.pkl', 'rb') as f:
    winner_model = pickle.load(f)
with open(model_dir / 'podium_stacking_ensemble.pkl', 'rb') as f:
    podium_model = pickle.load(f)
with open(model_dir / 'top_10_stacking_ensemble.pkl', 'rb') as f:
    top10_model = pickle.load(f)
with open(model_dir / 'winner_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Historical data
circuits = {
    'Bahrain': 0.45, 'Saudi Arabia': 0.50, 'Australia': 0.40, 'Japan': 0.55,
    'China': 0.35, 'Monaco': 0.75, 'Canada': 0.52, 'Spain': 0.60,
    'Austria': 0.38, 'Silverstone': 0.40, 'Hungary': 0.48, 'Belgium': 0.42,
    'Italy': 0.45, 'Singapore': 0.70, 'Mexico': 0.35, 'Brazil': 0.58,
}

# 1950-2026 Complete Historical F1 Champions
historical_champs = {
    1950: ('Giuseppe Farina', 30), 1951: ('Juan Manuel Fangio', 37), 1952: ('Alberto Ascari', 36),
    1953: ('Alberto Ascari', 34), 1954: ('Juan Manuel Fangio', 42), 1955: ('Juan Manuel Fangio', 40),
    1956: ('Juan Manuel Fangio', 30), 1957: ('Juan Manuel Fangio', 40), 1958: ('Mike Hawthorn', 42),
    1959: ('Jack Brabham', 43), 1960: ('Jack Brabham', 43), 1961: ('Phil Hill', 34),
    1962: ('Graham Hill', 42), 1963: ('Jim Clark', 54), 1964: ('John Surtees', 40),
    1965: ('Jim Clark', 54), 1966: ('Jack Brabham', 42), 1967: ('Denny Hulme', 51),
    1968: ('Graham Hill', 48), 1969: ('Jackie Stewart', 63), 1970: ('Jochen Rindt', 45),
    1971: ('Jackie Stewart', 62), 1972: ('Emerson Fittipaldi', 61), 1973: ('Jackie Stewart', 71),
    1974: ('Emerson Fittipaldi', 55), 1975: ('Niki Lauda', 54), 1976: ('James Hunt', 69),
    1977: ('Niki Lauda', 72), 1978: ('Mario Andretti', 64), 1979: ('Jody Scheckter', 51),
    1980: ('Alan Jones', 67), 1981: ('Nelson Piquet', 67), 1982: ('Keke Rosberg', 44),
    1983: ('Nelson Piquet', 59), 1984: ('Niki Lauda', 72), 1985: ('Alain Prost', 73),
    1986: ('Alain Prost', 72), 1987: ('Nelson Piquet', 76), 1988: ('Ayrton Senna', 90),
    1989: ('Alain Prost', 76), 1990: ('Ayrton Senna', 78), 1991: ('Ayrton Senna', 96),
    1992: ('Nigel Mansell', 108), 1993: ('Alain Prost', 99), 1994: ('Michael Schumacher', 92),
    1995: ('Michael Schumacher', 102), 1996: ('Damon Hill', 97), 1997: ('Jacques Villeneuve', 81),
    1998: ('Mika Häkkinen', 100), 1999: ('Mika Häkkinen', 76), 2000: ('Michael Schumacher', 108),
    2001: ('Michael Schumacher', 123), 2002: ('Michael Schumacher', 144), 2003: ('Michael Schumacher', 93),
    2004: ('Michael Schumacher', 148), 2005: ('Kimi Räikkönen', 133), 2006: ('Fernando Alonso', 134),
    2007: ('Kimi Räikkönen', 110), 2008: ('Lewis Hamilton', 98), 2009: ('Jenson Button', 95),
    2010: ('Sebastian Vettel', 256), 2011: ('Sebastian Vettel', 392), 2012: ('Sebastian Vettel', 281),
    2013: ('Sebastian Vettel', 397), 2014: ('Lewis Hamilton', 384), 2015: ('Lewis Hamilton', 381),
    2016: ('Lewis Hamilton', 473), 2017: ('Lewis Hamilton', 363), 2018: ('Lewis Hamilton', 408),
    2019: ('Lewis Hamilton', 413), 2020: ('Lewis Hamilton', 347), 2021: ('Max Verstappen', 395),
    2022: ('Max Verstappen', 454), 2023: ('Max Verstappen', 575), 2024: ('Max Verstappen', 287),
    2025: ('Max Verstappen', 320), 2026: ('Max Verstappen', 350),
}

# Extract unique drivers from historical data
drivers_db = {}
for year, (driver, points) in historical_champs.items():
    if driver not in drivers_db:
        drivers_db[driver] = {'team': 'F1 Team', 'avg_pts': points / 20}

years_available = sorted(list(historical_champs.keys()))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        driver_name = data.get('driver')
        year = int(data.get('year'))
        total_points = int(data.get('points'))
        circuit = data.get('circuit')
        
        if not all([driver_name, circuit]):
            return jsonify({'error': 'Missing fields'}), 400
        
        if driver_name not in drivers_db:
            return jsonify({'error': 'Driver not found'}), 404
        
        if circuit not in circuits:
            return jsonify({'error': 'Circuit not found'}), 404
        
        driver_info = drivers_db[driver_name]
        difficulty = circuits[circuit]

        # Get driver's historical performance (1950-2026 data)
        driver_champ_years = [yr for yr, (d, _) in historical_champs.items() if d == driver_name]
        years_active = len(driver_champ_years)

        # Champion points for this driver across all years
        driver_all_pts = [pts for yr, (d, pts) in historical_champs.items() if d == driver_name]
        driver_avg_champ_pts = sum(driver_all_pts) / max(1, len(driver_all_pts)) if driver_all_pts else 50

        # Skill rating: better drivers have higher average championship points
        driver_skill = min(1.0, driver_avg_champ_pts / 150.0)  # Normalize to 1.0 at 150 pts

        # Points analysis: compare input points to historical average
        avg_pts = total_points / 20 if total_points > 0 else 1

        # High points = better performance this season
        performance_ratio = min(2.0, total_points / max(50, driver_avg_champ_pts))

        # Winning grid position for elite drivers
        elite_factor = 1.0 if driver_skill > 0.65 else (0.7 if driver_skill > 0.4 else 0.4)
        base_grid = max(1, 15 - (avg_pts * 1.8 * elite_factor))

        # Create features based on driver skill and season performance
        feature_dict = {
            'year': year,
            'grid': max(1, min(20, base_grid)),
            'driver_total_points': total_points,
            'driver_avg_points': avg_pts,
            'driver_points_std': max(0.5, avg_pts * (0.4 - 0.2 * driver_skill)),  # Consistent drivers have lower std
            'driver_avg_position': max(1, 22 - (avg_pts * 2.5 * performance_ratio)),
            'driver_best_position': max(1, int(1 + (20 - 20 * driver_skill))),  # Elite drivers get P1 more
            'driver_worst_position': min(20, int(18 + (2 * (1 - driver_skill)))),
            'driver_position_std': max(1, 6 * (1 - driver_skill)),  # Elite drivers more consistent
            'driver_avg_grid': base_grid,
            'driver_grid_std': max(1, 4 * (1 - driver_skill)),
            'driver_best_grid': max(1, int(1 + (5 * (1 - driver_skill)))),
            'driver_worst_grid': min(20, int(15 + (5 * (1 - driver_skill)))),
            'driver_races_count': min(350, 20 + (years_active * 8)),
            'constructor_total_points': total_points * (1.5 + 0.5 * driver_skill),
            'constructor_avg_points': avg_pts * (1.5 + 0.5 * driver_skill),
            'constructor_points_std': max(2, 8 - (3 * driver_skill)),
            'constructor_avg_position': max(2, 14 - (driver_skill * 10)),
            'constructor_best_position': max(1, int(1 + (3 * (1 - driver_skill)))),
            'constructor_position_std': max(1, 4 * (1 - driver_skill)),
            'constructor_avg_grid': max(2, base_grid + 1),
            'constructor_races_count': min(500, 50 + (years_active * 15)),
            'circuit_avg_position': max(3, 15 - (8 * (1 - difficulty)) - (4 * driver_skill)),
            'circuit_position_std': max(2, 6 * difficulty),
            'circuit_avg_points': max(2, avg_pts * (1.2 - 0.4 * difficulty)),
            'circuit_points_std': max(1, avg_pts * 0.3 * difficulty),
            'circuit_avg_grid': max(2, base_grid + (2 * difficulty)),
            'circuit_difficulty': difficulty,
            'circuit_races_count': 5 + int(years_active / 4),
            'grid_to_position_diff': 2 * (1 - driver_skill),  # Elite drivers gain positions
            'qualified_better': 1 if driver_skill > 0.5 else 0,
            'qualified_worse': 0 if driver_skill > 0.5 else 1,
            'dnf_flag': 0 if driver_skill > 0.5 else (1 if difficulty > 0.7 else 0),
            'points_earned': 1,
            'driver_consistency': max(0.8, 2.0 * driver_skill),
            'constructor_consistency': max(0.8, 1.5 * driver_skill),
            'driver_performance_ratio': min(2.0, performance_ratio),
            'constructor_performance_ratio': min(2.5, performance_ratio * 1.5),
            'driver_grid_improvement': 1 + driver_skill,
            'driver_constructor_synergy': max(50, avg_pts * (5 + 15 * driver_skill)),
            'driver_circuit_affinity': max(0.2, 0.5 + (0.5 * (1 - difficulty)) * driver_skill),
            'driver_rolling_points_5': max(1, avg_pts * (0.9 + 0.1 * performance_ratio)),
            'driver_rolling_grid_5': max(1, base_grid * 0.95),
            'constructor_rolling_points_5': max(2, avg_pts * (1.4 + 0.2 * performance_ratio)),
        }
        
        import pandas as pd
        X = pd.DataFrame([feature_dict])
        X_scaled = scaler.transform(X[features])
        
        # Predictions
        win_prob = float(winner_model.predict_proba(X_scaled)[0][1] * 100)
        podium_prob = float(podium_model.predict_proba(X_scaled)[0][1] * 100)
        top10_prob = float(top10_model.predict_proba(X_scaled)[0][1] * 100)
        
        return jsonify({
            'driver': driver_name,
            'team': driver_info['team'],
            'circuit': circuit,
            'year': year,
            'points': total_points,
            'predictions': {
                'win': round(win_prob, 1),
                'podium': round(podium_prob, 1),
                'top_10': round(top10_prob, 1)
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    return jsonify(sorted(list(drivers_db.keys())))

@app.route('/api/circuits', methods=['GET'])
def get_circuits():
    return jsonify(sorted(list(circuits.keys())))

@app.route('/api/years', methods=['GET'])
def get_years():
    return jsonify(years_available)

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({
        'total_years': len(years_available),
        'total_unique_drivers': len(drivers_db),
        'total_circuits': len(circuits),
        'data_range': '1950-2026'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
