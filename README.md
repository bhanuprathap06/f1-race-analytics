# F1 RACE PREDICTOR - Machine Learning System

Professional machine learning pipeline for Formula 1 race outcome predictions with 97.14% accuracy.

## Overview

A production-grade ML system that predicts Formula 1 race outcomes using historical data from 1950-2026. Trained on 27,533 race records with 28 engineered features, achieving 97.14% test accuracy using a Stacking Ensemble model.

## Key Results

- **Test Accuracy:** 97.14%
- **ROC-AUC:** 0.9820
- **Precision:** 82.19%
- **F1-Score:** 0.6704
- **Models Trained:** 6 algorithms
- **Data:** 27,533 race records

## Quick Start

### 1. Setup Environment
```bash
cd formulaOne
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy scikit-learn xgboost matplotlib seaborn streamlit
```

### 2. Train Models
```bash
python ML_PROFESSIONAL_PIPELINE.py
```

### 3. View Dashboard
```bash
cd F1_ML_DATASETS
streamlit run streamlit_dashboard.py
```

## Project Structure

```
formulaOne/
├── README.md                          # This file
├── ML_PROFESSIONAL_PIPELINE.py        # Main training pipeline
├── ML_TRAINING_SIMPLE.py              # Simplified version
├── FEATURE_IMPORTANCE_VISUALIZATION.py # Charts generation
├── F1_ML_DATASETS/
│   ├── trained_models/                # Saved ML models
│   │   ├── stacking_model.pkl
│   │   ├── voting_model.pkl
│   │   ├── feature_scaler.pkl
│   │   ├── feature_columns.pkl
│   │   ├── training_report.json
│   │   └── ...
│   ├── logs/                          # Training logs
│   ├── visualizations/                # Generated charts
│   └── streamlit_dashboard.py         # Interactive dashboard
├── F1_RACE_ANALYTICS_FRONTEND/        # React frontend
└── venv/                              # Python environment
```

## Features Engineered

**28 Professional Features:**
- Driver career statistics (points, position averages)
- Constructor performance metrics
- Circuit characteristics
- Grid position analysis
- Driver-constructor synergy
- Performance consistency indicators
- Temporal features

## Models Trained

1. **Logistic Regression** - Baseline classifier
2. **Random Forest** - Tree-based ensemble
3. **Gradient Boosting** - Sequential learning
4. **XGBoost** - Optimized gradient boosting
5. **Voting Ensemble** - Soft voting
6. **Stacking Ensemble** - Best performer (97.14% accuracy)

## Usage

### Train Models
```bash
python ML_PROFESSIONAL_PIPELINE.py
```

### Generate Visualizations
```bash
python FEATURE_IMPORTANCE_VISUALIZATION.py
```

### Run Dashboard
```bash
cd F1_ML_DATASETS
streamlit run streamlit_dashboard.py
```

## Model Performance

### Cross-Validation Results
- Accuracy: 0.9457 (±0.0089)
- Precision: 0.8156 (±0.0234)
- Recall: 0.5612 (±0.0456)
- F1-Score: 0.6567 (±0.0378)
- ROC-AUC: 0.9714 (±0.0067)

### Test Set Results
- Accuracy: 97.14%
- Precision: 82.19%
- Recall: 56.60%
- F1-Score: 0.6704
- ROC-AUC: 0.9820

## Top Features (by importance)

1. Driver average grid position
2. Constructor average points
3. Circuit average position
4. Driver career points
5. Constructor total points

## Technologies

- **Python 3.14**
- **Scikit-learn** - ML algorithms
- **XGBoost** - Advanced boosting
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Matplotlib/Seaborn** - Visualization
- **Streamlit** - Dashboard

## Installation Requirements

```
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
xgboost>=1.5.0
matplotlib>=3.4.0
seaborn>=0.11.0
streamlit>=1.0.0
```

## Production Deployment

Models are saved as serialized Python objects (.pkl) and ready for:
- Flask REST API integration
- Real-time predictions
- Batch processing
- Model serving

All models include:
- Input feature scaler (RobustScaler)
- Feature column index
- Cross-validation metrics
- Training timestamp and metadata

## Data Source

Historical Formula 1 data from official F1 records:
- **Records:** 27,533
- **Races:** 1,160
- **Drivers:** 860
- **Constructors:** 186
- **Circuits:** 77
- **Time Period:** 1950-2026

## Results & Insights

The Stacking Ensemble achieves exceptional performance by:
1. Combining 4 different base learners
2. Using Logistic Regression as meta-learner
3. Reducing overfitting through cross-validation
4. Leveraging ensemble diversity

Feature importance analysis reveals:
- Historical driver performance is most predictive
- Grid position (qualifying) significantly impacts outcomes
- Constructor strength is crucial
- Circuit-specific factors matter

## Limitations

- Model accuracy varies by prediction task (winner is harder than top-10)
- Real-world performance affected by:
  - Unexpected race incidents
  - Weather changes
  - Mechanical failures
  - Rule changes

## Next Steps

1. Deploy models to production API
2. Collect real-time race data
3. Implement online learning
4. Add telemetry features
5. Create prediction confidence intervals

## Author

Bhanu Guntuku  
Machine Learning Engineering  
SRMIST Chennai

## License

MIT License - See LICENSE file for details

---

**Status:** Production Ready ✅  
**Last Updated:** August 2026  
**Accuracy:** 97.14%
