import pandas as pd
import os

print("Checking available datasets...")
print("\nFiles in processed_data/:")
for file in os.listdir('processed_data/'):
    print(f"  - {file}")

print("\n" + "="*60)
print("Loading race prediction dataset...")
print("="*60)

try:
    df = pd.read_csv('processed_data/01_race_prediction_dataset_POST_QUALIFYING.csv')
    print(f"\n✅ Loaded: {len(df)} rows, {len(df.columns)} columns")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nDataset Info:")
    print(df.info())
    print("\n✅ Dataset ready for ML training!")
except FileNotFoundError:
    print("\n❌ Dataset not found. Run: python3 process_f1_datasets.py")
