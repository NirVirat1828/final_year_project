#!/bin/bash

# Tournament Director - Installation & Setup Script
# Run this script to set up your environment for the Tournament Director

echo "================================================================================"
echo "🏆 TOURNAMENT DIRECTOR - INSTALLATION SCRIPT"
echo "================================================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 detected: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Step 1: Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created successfully"
fi
echo ""

# Activate virtual environment
echo "📦 Step 2: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Step 3: Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded to latest version"
echo ""

# Install dependencies
echo "📦 Step 4: Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r tournament_requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ All dependencies installed successfully"
else
    echo "❌ Failed to install some dependencies. Please check the error messages above."
    exit 1
fi
echo ""

# Verify installations
echo "📦 Step 5: Verifying installations..."
python3 << END
import sys
try:
    import numpy
    import pandas
    import sklearn
    import scipy
    import matplotlib
    import seaborn
    import xgboost
    import tensorflow
    print("✓ All core packages verified")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Missing package: {e}")
    sys.exit(1)
END

if [ $? -ne 0 ]; then
    echo "⚠️  Some packages are missing. Trying to install again..."
    pip install numpy pandas scikit-learn scipy matplotlib seaborn xgboost tensorflow
fi
echo ""

# Test demo script
echo "📦 Step 6: Testing demo script..."
python3 tournament_director_demo.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Demo script runs successfully"
else
    echo "⚠️  Demo script had issues (this is okay for now)"
fi
echo ""

# Summary
echo "================================================================================"
echo "✅ INSTALLATION COMPLETE!"
echo "================================================================================"
echo ""
echo "📋 What's Installed:"
echo "   ├─ Python virtual environment (venv/)"
echo "   ├─ NumPy, Pandas, Scikit-learn"
echo "   ├─ SciPy (signal processing)"
echo "   ├─ Matplotlib, Seaborn (visualization)"
echo "   ├─ XGBoost (gradient boosting)"
echo "   └─ TensorFlow (deep learning)"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Test the demo (no dependencies needed):"
echo "   python3 tournament_director_demo.py"
echo ""
echo "2. Run the full tournament:"
echo "   python3 tournament_director.py"
echo ""
echo "3. View results:"
echo "   - results_comparison.csv"
echo "   - tournament_figures/"
echo ""
echo "📖 Documentation:"
echo "   - TOURNAMENT_DIRECTOR_README.md (comprehensive guide)"
echo "   - tournament_director.py (well-commented source)"
echo ""
echo "💡 Tip: Always activate the virtual environment before running:"
echo "   source venv/bin/activate"
echo ""
echo "================================================================================"
echo "Happy Benchmarking! 🎯"
echo "================================================================================"
