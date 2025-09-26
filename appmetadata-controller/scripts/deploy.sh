#!/bin/bash
set -e

# Ensure running from project root
cd "$(dirname "$0")/.."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl could not be found"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot access Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

echo "🔍 Verifying CRD..."
if ! kubectl get crd applicationmetadata.apps.company.io &> /dev/null; then
    echo "📦 Installing CRD..."
    kubectl apply -f manifests/crd.yaml
    # Wait for CRD to be established
    kubectl wait --for=condition=established --timeout=60s crd/applicationmetadata.apps.company.io
fi

echo "🚀 Deploying ApplicationMetadata Controller..."

# Apply manifests using kustomize
kubectl apply -k manifests/

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl -n appmetadata-system wait --for=condition=available --timeout=300s deployment/appmetadata-controller

echo "✅ ApplicationMetadata Controller has been deployed!"