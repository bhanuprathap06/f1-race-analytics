#!/usr/bin/env python3
"""
Formula 1 ML Dataset Processing - Simplified Working Version
Processes F1DB CSV files into ML-ready datasets
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Paths
RAW_DATA_DIR = Path('raw_data')
PROCESSED_DATA_DIR = Path('processed_data')
PROCESSED_DATA_DIR.mkdir(exist_ok=True)

print("="*70)
print("FORMULA 1 ML DATASET PROCESSOR")
print("="*70)
print()

# ============================================================================
# LOAD F1DB DATA
# ============================================================================

logger.info("Loading F1DB CSV files from raw_data/...")
print()

try:
    drivers = pd.read_csv(RAW_DATA_DIR / 'f1db-drivers.csv')
    races = pd.read_csv(RAW_DATA_DIR / 'f1db-races.csv')
    results = pd.read_csv(RAW_DATA_DIR / 'f1db-races-race-results.csv')
    qualifying = pd.read_csv(RAW_DATA_DIR / 'f1db-races-qualifying-results.csv')
    circuits = pd.read_csv(RAW_DATA_DIR / 'f1db-circuits.csv')
    constructors = pd.read_csv(RAW_DATA_DIR / 'f1db-constructors.csv')

    logger.info(f"✓ Drivers: {len(drivers)} records")
    logger.info(f"✓ Races: {len(races)} records")
    logger.info(f"✓ Results: {len(results)} records")
    logger.info(f"✓ Qualifying: {len(qualifying)} records")
    logger.info(f"✓ Circuits: {len(circuits)} records")
    logger.info(f"✓ Constructors: {len(constructors)} records")
    print()

except Exception as e:
    logger.error(f"Error loading data: {e}")
    exit(1)

# ============================================================================
# DATASET 01: RACE PREDICTION (POST-QUALIFYING VERSION)
# ============================================================================

logger.info("Creating Dataset 01: Race Prediction (POST-QUALIFYING)...")

try:
    # Merge results with race info
    df01 = results.copy()

    # Rename columns for clarity
    df01.rename(columns={
        'raceId': 'race_id',
        'driverId': 'driver_id',
        'constructorId': 'constructor_id',
        'gridPosition': 'grid_position',
        'positionOrder': 'final_position',
        'positionText': 'position_text',
        'raceStatus': 'race_status'
    }, inplace=True, errors='ignore')

    # Add race info
    races_renamed = races.rename(columns={
        'raceId': 'race_id',
        'year': 'season',
        'round': 'round_num',
        'circuitId': 'circuit_id',
        'name': 'race_name',
        'date': 'race_date'
    }, inplace=False, errors='ignore')

    df01 = df01.merge(races_renamed[['race_id', 'season', 'round_num', 'circuit_id', 'race_name', 'race_date']],
                       on='race_id', how='left')

    # Add driver names
    drivers_renamed = drivers.rename(columns={
        'driverId': 'driver_id',
        'surname': 'driver_name'
    }, inplace=False, errors='ignore')
    df01 = df01.merge(drivers_renamed[['driver_id', 'driver_name']], on='driver_id', how='left')

    # Add constructor names
    constructors_renamed = constructors.rename(columns={
        'constructorId': 'constructor_id',
        'name': 'constructor_name'
    }, inplace=False, errors='ignore')
    df01 = df01.merge(constructors_renamed[['constructor_id', 'constructor_name']], on='constructor_id', how='left')

    # Add circuit info
    circuits_renamed = circuits.rename(columns={
        'circuitId': 'circuit_id',
        'name': 'circuit_name',
        'country': 'circuit_country'
    }, inplace=False, errors='ignore')
    df01 = df01.merge(circuits_renamed[['circuit_id', 'circuit_name', 'circuit_country']], on='circuit_id', how='left')

    # Create target variables
    df01['winner'] = (df01['final_position'] == 1).astype(int)
    df01['podium'] = (df01['final_position'] <= 3).astype(int)
    df01['dnf'] = (df01['final_position'].isna() | (df01['final_position'] > 50)).astype(int)

    # Select key columns
    output_cols = ['season', 'round_num', 'race_id', 'race_date', 'race_name',
                   'circuit_id', 'circuit_name', 'circuit_country',
                   'driver_id', 'driver_name', 'constructor_id', 'constructor_name',
                   'grid_position', 'final_position', 'winner', 'podium', 'dnf', 'points']

    df01_output = df01[[c for c in output_cols if c in df01.columns]].copy()

    # Save
    output_path = PROCESSED_DATA_DIR / '01_race_prediction_dataset_POST_QUALIFYING.csv'
    df01_output.to_csv(output_path, index=False)
    logger.info(f"✓ Saved: {output_path} ({len(df01_output)} rows)")
    print()

except Exception as e:
    logger.error(f"Error creating Dataset 01: {e}")

# ============================================================================
# DATASET 03: CIRCUIT SUMMARY
# ============================================================================

logger.info("Creating Dataset 03: Circuit Summary...")

try:
    df03 = circuits.copy()
    df03.rename(columns={
        'circuitId': 'circuit_id',
        'name': 'circuit_name',
        'location': 'location',
        'country': 'country',
        'lat': 'latitude',
        'lng': 'longitude',
        'alt': 'altitude'
    }, inplace=True, errors='ignore')

    # Count races at each circuit
    circuit_races = results.merge(races[['raceId', 'year']], left_on='raceId', right_on='raceId')
    circuit_races.rename(columns={'circuitId': 'circuit_id'}, inplace=True, errors='ignore')
    circuit_counts = circuit_races.groupby('circuit_id').size().reset_index(name='total_races')

    df03 = df03.merge(circuit_counts, on='circuit_id', how='left')

    output_path = PROCESSED_DATA_DIR / '03_circuit_summary.csv'
    df03.to_csv(output_path, index=False)
    logger.info(f"✓ Saved: {output_path} ({len(df03)} rows)")
    print()

except Exception as e:
    logger.error(f"Error creating Dataset 03: {e}")

# ============================================================================
# DATASET 04: DRIVER PERFORMANCE
# ============================================================================

logger.info("Creating Dataset 04: Driver Performance...")

try:
    # Merge results with races and drivers
    df04 = results.merge(races[['raceId', 'year']], left_on='raceId', right_on='raceId')
    df04 = df04.merge(drivers[['driverId', 'surname']], left_on='driverId', right_on='driverId')

    # Group by driver and season
    df04_summary = df04.groupby(['year', 'driverId', 'surname']).agg({
        'raceId': 'count',
        'points': 'sum',
        'positionOrder': ['mean', 'std'],
        'gridPosition': 'mean'
    }).reset_index()

    df04_summary.columns = ['season', 'driver_id', 'driver_name', 'races', 'points',
                            'avg_position', 'position_std', 'avg_grid_position']

    output_path = PROCESSED_DATA_DIR / '04_driver_performance_dataset.csv'
    df04_summary.to_csv(output_path, index=False)
    logger.info(f"✓ Saved: {output_path} ({len(df04_summary)} rows)")
    print()

except Exception as e:
    logger.error(f"Error creating Dataset 04: {e}")

# ============================================================================
# DATASET 05: CONSTRUCTOR PERFORMANCE
# ============================================================================

logger.info("Creating Dataset 05: Constructor Performance...")

try:
    df05 = results.merge(races[['raceId', 'year']], left_on='raceId', right_on='raceId')
    df05 = df05.merge(constructors[['constructorId', 'name']], left_on='constructorId', right_on='constructorId')

    df05_summary = df05.groupby(['year', 'constructorId', 'name']).agg({
        'raceId': 'count',
        'points': 'sum',
        'positionOrder': 'mean'
    }).reset_index()

    df05_summary.columns = ['season', 'constructor_id', 'constructor_name', 'races', 'points', 'avg_position']

    output_path = PROCESSED_DATA_DIR / '05_constructor_performance_dataset.csv'
    df05_summary.to_csv(output_path, index=False)
    logger.info(f"✓ Saved: {output_path} ({len(df05_summary)} rows)")
    print()

except Exception as e:
    logger.error(f"Error creating Dataset 05: {e}")

# ============================================================================
# DATASET 06: QUALIFYING PERFORMANCE
# ============================================================================

logger.info("Creating Dataset 06: Qualifying Performance...")

try:
    df06 = qualifying.copy()
    df06 = df06.merge(races[['raceId', 'year']], left_on='raceId', right_on='raceId')

    output_path = PROCESSED_DATA_DIR / '06_qualifying_performance_dataset.csv'
    df06.to_csv(output_path, index=False)
    logger.info(f"✓ Saved: {output_path} ({len(df06)} rows)")
    print()

except Exception as e:
    logger.error(f"Error creating Dataset 06: {e}")

# ============================================================================
# SUMMARY
# ============================================================================

print("="*70)
logger.info("✅ DATA PROCESSING COMPLETE")
print("="*70)
print()

# List generated files
print("Generated datasets in processed_data/:")
for file in sorted(PROCESSED_DATA_DIR.glob('*.csv')):
    size = os.path.getsize(file) / (1024 * 1024)  # Convert to MB
    df_temp = pd.read_csv(file)
    print(f"  ✓ {file.name:50} ({len(df_temp):>6} rows, {size:>6.2f} MB)")

print()
print("📊 Next steps:")
print("  1. Explore the datasets: python3 check_data.py")
print("  2. Train ML models: See README.md")
print("  3. Review documentation: cat documentation/DATA_DICTIONARY.md")
print()
