import pickle
import requests
from pathlib import Path

model_dir = Path('F1_ML_DATASETS/trained_models')
with open(model_dir / 'feature_columns.pkl', 'rb') as f:
    features = pickle.load(f)
with open(model_dir / 'winner_stacking_ensemble.pkl', 'rb') as f:
    model = pickle.load(f)

def fetch_season(year):
    try:
        url = f"http://ergast.com/api/f1/{year}/driverStandings.json?limit=30"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            standings = data['MRData']['StandingsTable']['StandingsList']
            if standings:
                drivers = []
                for d in standings[0]['DriverStandings'][:5]:
                    name = d['Driver']['givenName'] + ' ' + d['Driver']['familyName']
                    pts = int(d['points'])
                    avg = pts / 20
                    drivers.append((name, pts, avg))
                return drivers
    except:
        pass
    return None

print("F1 PREDICTIONS 1950-2026\n")

for year in range(1950, 2027):
    drivers = fetch_season(year)
    if drivers:
        top_driver = max(drivers, key=lambda x: x[2])
        print(f"{year}: {top_driver[0]:25} ({top_driver[2]:5.2f} pts/race)")
    else:
        print(f"{year}: Data unavailable")
