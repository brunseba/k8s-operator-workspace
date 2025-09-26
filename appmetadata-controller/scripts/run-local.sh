#!/bin/bash
set -e

# Ensure running from project root
cd "$(dirname "$0")/.."

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv venv
    . venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    . venv/bin/activate
fi

# Ensure Kubernetes config is available
if [ -z "$KUBECONFIG" ]; then
    if [ ! -f "$HOME/.kube/config" ]; then
        echo "❌ No Kubernetes configuration found. Please set KUBECONFIG or ensure ~/.kube/config exists."
        exit 1
    fi
fi

# Set environment variables
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
export CONFIG_PATH="$(pwd)/config/config.yaml"
export KOPF_NAMESPACE="default"

# Run the controller
echo "🚀 Starting ApplicationMetadata Controller locally..."
python -m src.controller