#!/usr/bin/env python3
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('f1_predictor_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

output_dir = Path('F1_PREDICTIONS_OUTPUT')
output_dir.mkdir(exist_ok=True)

# Complete historical F1 data (1950-2024) + predictions (2025-2026)
all_seasons = {
    1950: {'driver': 'Giuseppe Farina', 'points': 30},
    1951: {'driver': 'Juan Manuel Fangio', 'points': 37},
    1952: {'driver': 'Alberto Ascari', 'points': 36},
    1953: {'driver': 'Alberto Ascari', 'points': 34},
    1954: {'driver': 'Juan Manuel Fangio', 'points': 42},
    1955: {'driver': 'Juan Manuel Fangio', 'points': 40},
    1956: {'driver': 'Juan Manuel Fangio', 'points': 30},
    1957: {'driver': 'Juan Manuel Fangio', 'points': 40},
    1958: {'driver': 'Mike Hawthorn', 'points': 42},
    1959: {'driver': 'Jack Brabham', 'points': 43},
    1960: {'driver': 'Jack Brabham', 'points': 43},
    1961: {'driver': 'Phil Hill', 'points': 34},
    1962: {'driver': 'Graham Hill', 'points': 42},
    1963: {'driver': 'Jim Clark', 'points': 54},
    1964: {'driver': 'John Surtees', 'points': 40},
    1965: {'driver': 'Jim Clark', 'points': 54},
    1966: {'driver': 'Jack Brabham', 'points': 42},
    1967: {'driver': 'Denny Hulme', 'points': 51},
    1968: {'driver': 'Graham Hill', 'points': 48},
    1969: {'driver': 'Jackie Stewart', 'points': 63},
    1970: {'driver': 'Jochen Rindt', 'points': 45},
    1971: {'driver': 'Jackie Stewart', 'points': 62},
    1972: {'driver': 'Emerson Fittipaldi', 'points': 61},
    1973: {'driver': 'Jackie Stewart', 'points': 71},
    1974: {'driver': 'Emerson Fittipaldi', 'points': 55},
    1975: {'driver': 'Niki Lauda', 'points': 54},
    1976: {'driver': 'James Hunt', 'points': 69},
    1977: {'driver': 'Niki Lauda', 'points': 72},
    1978: {'driver': 'Mario Andretti', 'points': 64},
    1979: {'driver': 'Jody Scheckter', 'points': 51},
    1980: {'driver': 'Alan Jones', 'points': 67},
    1981: {'driver': 'Nelson Piquet', 'points': 67},
    1982: {'driver': 'Keke Rosberg', 'points': 44},
    1983: {'driver': 'Nelson Piquet', 'points': 59},
    1984: {'driver': 'Niki Lauda', 'points': 72},
    1985: {'driver': 'Alain Prost', 'points': 73},
    1986: {'driver': 'Alain Prost', 'points': 72},
    1987: {'driver': 'Nelson Piquet', 'points': 76},
    1988: {'driver': 'Ayrton Senna', 'points': 90},
    1989: {'driver': 'Alain Prost', 'points': 76},
    1990: {'driver': 'Ayrton Senna', 'points': 78},
    1991: {'driver': 'Ayrton Senna', 'points': 96},
    1992: {'driver': 'Nigel Mansell', 'points': 108},
    1993: {'driver': 'Alain Prost', 'points': 99},
    1994: {'driver': 'Michael Schumacher', 'points': 92},
    1995: {'driver': 'Michael Schumacher', 'points': 102},
    1996: {'driver': 'Damon Hill', 'points': 97},
    1997: {'driver': 'Jacques Villeneuve', 'points': 81},
    1998: {'driver': 'Mika Häkkinen', 'points': 100},
    1999: {'driver': 'Mika Häkkinen', 'points': 76},
    2000: {'driver': 'Michael Schumacher', 'points': 108},
    2001: {'driver': 'Michael Schumacher', 'points': 123},
    2002: {'driver': 'Michael Schumacher', 'points': 144},
    2003: {'driver': 'Michael Schumacher', 'points': 93},
    2004: {'driver': 'Michael Schumacher', 'points': 148},
    2005: {'driver': 'Kimi Räikkönen', 'points': 133},
    2006: {'driver': 'Fernando Alonso', 'points': 134},
    2007: {'driver': 'Kimi Räikkönen', 'points': 110},
    2008: {'driver': 'Lewis Hamilton', 'points': 98},
    2009: {'driver': 'Jenson Button', 'points': 95},
    2010: {'driver': 'Sebastian Vettel', 'points': 256},
    2011: {'driver': 'Sebastian Vettel', 'points': 392},
    2012: {'driver': 'Sebastian Vettel', 'points': 281},
    2013: {'driver': 'Sebastian Vettel', 'points': 397},
    2014: {'driver': 'Lewis Hamilton', 'points': 384},
    2015: {'driver': 'Lewis Hamilton', 'points': 381},
    2016: {'driver': 'Lewis Hamilton', 'points': 473},
    2017: {'driver': 'Lewis Hamilton', 'points': 363},
    2018: {'driver': 'Lewis Hamilton', 'points': 408},
    2019: {'driver': 'Lewis Hamilton', 'points': 413},
    2020: {'driver': 'Lewis Hamilton', 'points': 347},
    2021: {'driver': 'Max Verstappen', 'points': 395},
    2022: {'driver': 'Max Verstappen', 'points': 454},
    2023: {'driver': 'Max Verstappen', 'points': 575},
    2024: {'driver': 'Max Verstappen', 'points': 287},
    2025: {'driver': 'Max Verstappen', 'points': 320},
    2026: {'driver': 'Max Verstappen', 'points': 350},
}

def predict_winner_probability(points):
    avg_points = points / 20
    prob = min(0.95, max(0.01, (avg_points / 15.0) * 0.85))
    return prob * 100

def generate_reports():
    logger.info("Generating reports...")
    
    # CSV
    data = []
    for year in sorted(all_seasons.keys()):
        info = all_seasons[year]
        data.append({
            'Year': year,
            'Champion': info['driver'],
            'Points': info['points'],
            'Avg_Points': f"{info['points']/20:.2f}",
            'Win_Prob_%': f"{predict_winner_probability(info['points']):.1f}",
            'Type': 'REAL' if year <= 2024 else 'PREDICTED'
        })
    
    df = pd.DataFrame(data)
    csv_path = output_dir / 'f1_1950_2026.csv'
    df.to_csv(csv_path, index=False)
    logger.info(f"✓ CSV: {csv_path}")
    
    # JSON
    json_data = {
        'generated': datetime.now().isoformat(),
        'total_seasons': len(all_seasons),
        'range': '1950-2026',
        'data': {
            str(year): {
                'champion': all_seasons[year]['driver'],
                'points': all_seasons[year]['points'],
                'win_probability_%': float(f"{predict_winner_probability(all_seasons[year]['points']):.1f}")
            }
            for year in sorted(all_seasons.keys())
        }
    }
    json_path = output_dir / 'f1_1950_2026.json'
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2)
    logger.info(f"✓ JSON: {json_path}")
    
    # TXT
    txt_path = output_dir / 'f1_1950_2026.txt'
    with open(txt_path, 'w') as f:
        f.write("="*110 + "\n")
        f.write("F1 WORLD CHAMPIONS (1950-2026)\n")
        f.write("="*110 + "\n\n")
        f.write("Year | Champion                 | Points | Avg Pts | Win % | Type\n")
        f.write("-"*110 + "\n")
        for year in sorted(all_seasons.keys()):
            info = all_seasons[year]
            avg = info['points'] / 20
            win_prob = predict_winner_probability(info['points'])
            typ = "REAL" if year <= 2024 else "PREDICTED"
            f.write(f"{year} | {info['driver']:25} | {info['points']:5} | {avg:6.2f} | {win_prob:5.1f}% | {typ}\n")
        
        f.write("\n" + "="*110 + "\n")
        f.write("TOP 10 CHAMPIONS (All Time)\n")
        f.write("="*110 + "\n")
        top = sorted(all_seasons.items(), key=lambda x: x[1]['points'], reverse=True)[:10]
        for rank, (year, info) in enumerate(top, 1):
            f.write(f"{rank:2d}. {info['driver']:25} ({year}) - {info['points']:4d} pts\n")
    
    logger.info(f"✓ TXT: {txt_path}")
    
    # Statistics
    driver_titles = {}
    for info in all_seasons.values():
        driver = info['driver']
        driver_titles[driver] = driver_titles.get(driver, 0) + 1
    
    stats = {
        'total_seasons': len(all_seasons),
        'total_unique_champions': len(driver_titles),
        'most_titles': max(driver_titles.values()),
        'top_champions': sorted(driver_titles.items(), key=lambda x: x[1], reverse=True)[:10],
        'highest_points': max([x['points'] for x in all_seasons.values()]),
        'avg_points': float(np.mean([x['points'] for x in all_seasons.values()]))
    }
    
    stats_path = output_dir / 'statistics.json'
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"✓ STATS: {stats_path}")
    
    return csv_path, json_path, txt_path, stats_path

def main():
    logger.info("="*110)
    logger.info("F1 PRODUCTION SYSTEM - COMPLETE 1950-2026")
    logger.info("="*110 + "\n")
    
    logger.info(f"Data loaded: {len(all_seasons)} seasons")
    logger.info(f"Historical: 1950-2024 ({len([y for y in all_seasons if y <= 2024])} seasons)")
    logger.info(f"Predicted: 2025-2026 ({len([y for y in all_seasons if y > 2024])} seasons)\n")
    
    csv_path, json_path, txt_path, stats_path = generate_reports()
    
    logger.info("\n" + "="*110)
    logger.info("✓ PRODUCTION SYSTEM COMPLETE & READY")
    logger.info("="*110)
    logger.info("\nOutput files:")
    logger.info(f"  1. {csv_path} (Excel/spreadsheet)")
    logger.info(f"  2. {json_path} (API/web ready)")
    logger.info(f"  3. {txt_path} (Human readable)")
    logger.info(f"  4. {stats_path} (Analytics)")
    logger.info("\n✓ All tasks completed")
    logger.info("="*110 + "\n")

if __name__ == '__main__':
    main()
