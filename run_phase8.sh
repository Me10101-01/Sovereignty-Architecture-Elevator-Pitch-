#!/bin/bash
# Phase 8: Paracelsus Principles Deepening, Alchemy Exploration, and Benchmark Precision Enhancement
# Simple wrapper script to run Phase 8

set -e

echo "========================================================================="
echo "Phase 8: Paracelsus Principles Deepening & Alchemy Exploration"
echo "========================================================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using Python: $PYTHON_CMD"
echo ""

# Check for required packages (note: yaml is imported but installed as pyyaml)
echo "Checking dependencies..."
REQUIRED_PACKAGES="numpy scipy mpmath sympy statsmodels networkx yaml"
MISSING_PACKAGES=""

for package in $REQUIRED_PACKAGES; do
    if ! $PYTHON_CMD -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES="$MISSING_PACKAGES $package"
    fi
done

if [ -n "$MISSING_PACKAGES" ]; then
    echo "Warning: Missing packages:$MISSING_PACKAGES"
    echo "Installing dependencies from phase8/requirements.txt..."
    $PYTHON_CMD -m pip install -q -r phase8/requirements.txt
    echo "Dependencies installed."
else
    echo "All required dependencies are available."
fi

echo ""
echo "Running Phase 8 script..."
echo "========================================================================="
echo ""

# Run the main script
$PYTHON_CMD deepen_paracelsus_explore_alchemy.py

echo ""
echo "========================================================================="
echo "Phase 8 execution complete!"
echo "Results saved to: benchmarks/paracelsus_alchemy.yaml"
echo "========================================================================="
