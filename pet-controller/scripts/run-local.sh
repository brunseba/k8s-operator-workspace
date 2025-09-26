#!/bin/bash
set -e

echo "=== Pet Controller Local Development ==="

# Check if we're in the right directory
if [ ! -f "src/controller.py" ]; then
    echo "Error: Please run this script from the pet-controller directory"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export CONFIG_PATH="$(pwd)/config.yaml"
export KOPF_LOG_FORMAT="plain"
export KOPF_LOG_LEVEL="INFO"

echo "Starting Pet Controller locally..."
echo "Configuration: $CONFIG_PATH"
echo "Press Ctrl+C to stop"
echo ""

# Run the controller
python -m src.controller