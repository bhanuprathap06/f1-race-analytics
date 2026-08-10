#!/bin/bash

# Formula 1 ML Dataset System - Dependency Installation Script
# Run this script to install all required Python packages

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Formula 1 ML Dataset System - Installing Dependencies       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python installation..."
python3 --version
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip setuptools wheel
echo ""

# Install core data science packages
echo "📊 Installing core data science packages..."
echo "   - pandas"
echo "   - numpy"
echo "   - scikit-learn"
echo "   - xgboost (gradient boosting)"
echo "   - lightgbm (light gradient boosting)"
echo "   - scipy"
python3 -m pip install pandas numpy scikit-learn xgboost lightgbm scipy
echo "✅ Core packages installed"
echo ""

# Install visualization packages
echo "🎨 Installing visualization packages..."
echo "   - matplotlib"
echo "   - seaborn"
python3 -m pip install matplotlib seaborn
echo "✅ Visualization packages installed"
echo ""

# Install Jupyter
echo "📓 Installing Jupyter & IPython..."
echo "   - jupyter"
echo "   - jupyterlab"
echo "   - ipython"
python3 -m pip install jupyter jupyterlab ipython
echo "✅ Jupyter installed"
echo ""

# Install utility packages
echo "🔧 Installing utility packages..."
echo "   - requests (HTTP library)"
echo "   - beautifulsoup4 (web scraping)"
echo "   - tqdm (progress bars)"
echo "   - openpyxl (Excel support)"
echo "   - python-dotenv (environment variables)"
python3 -m pip install requests beautifulsoup4 tqdm openpyxl python-dotenv
echo "✅ Utility packages installed"
echo ""

# Verify installations
echo "✅ Verifying installations..."
python3 << 'EOF'
import sys
print("=" * 60)
print("INSTALLATION VERIFICATION")
print("=" * 60)

packages = {
    'pandas': 'Data manipulation',
    'numpy': 'Numerical computing',
    'sklearn': 'ML algorithms',
    'xgboost': 'Gradient boosting',
    'lightgbm': 'Light gradient boosting',
    'scipy': 'Scientific computing',
    'matplotlib': 'Visualization',
    'seaborn': 'Statistical visualization',
    'jupyter': 'Notebooks',
    'ipython': 'Interactive shell',
    'requests': 'HTTP library',
    'bs4': 'Web scraping',
    'tqdm': 'Progress bars',
    'openpyxl': 'Excel support',
}

failed = []
for pkg, desc in packages.items():
    try:
        __import__(pkg)
        print(f"✓ {pkg:20} - {desc}")
    except ImportError:
        print(f"✗ {pkg:20} - {desc} [FAILED]")
        failed.append(pkg)

print("=" * 60)
if failed:
    print(f"⚠️  Failed to install: {', '.join(failed)}")
    print("Try running: python3 -m pip install --upgrade " + " ".join(failed))
else:
    print("✅ ALL PACKAGES INSTALLED SUCCESSFULLY!")
print("=" * 60)
EOF
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  ✅ INSTALLATION COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Next Steps:"
echo ""
echo "1. Navigate to the project directory:"
echo "   cd /Users/bhanubanny/Desktop/formulaOne/F1_ML_DATASETS"
echo ""
echo "2. Read the documentation:"
echo "   cat README.md"
echo ""
echo "3. Run the processing pipeline:"
echo "   python3 process_f1_datasets.py --source f1db --year-range 1950-2026"
echo ""
echo "4. Load data and train models:"
echo "   python3"
echo "   >>> import pandas as pd"
echo "   >>> df = pd.read_csv('processed_data/01_race_prediction_dataset_POST_QUALIFYING.csv')"
echo "   >>> print(f'Loaded {len(df)} rows')"
echo ""
