#!/bin/bash
set -e

echo "=== Pet Controller Build and Deploy ==="

# Configuration
IMAGE_NAME="pet-controller"
IMAGE_TAG=${1:-"latest"}
REGISTRY=${REGISTRY:-""}
NAMESPACE="pet-system"

if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
fi

echo "Building image: $FULL_IMAGE_NAME"

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo "Error: Please run this script from the pet-controller directory"
    exit 1
fi

# Build Docker image
echo "Building Docker image..."
docker build -t "$FULL_IMAGE_NAME" .

# Push image if registry is specified
if [ -n "$REGISTRY" ]; then
    echo "Pushing image to registry..."
    docker push "$FULL_IMAGE_NAME"
fi

# Update deployment image
echo "Updating deployment with new image..."
cd manifests
kustomize edit set image pet-controller="$FULL_IMAGE_NAME"

# Apply manifests
echo "Applying Kubernetes manifests..."
kubectl apply -k .

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/pet-controller -n $NAMESPACE

echo "Deployment completed successfully!"
echo "Check controller status with: kubectl get pods -n $NAMESPACE"
echo "View controller logs with: kubectl logs -f deployment/pet-controller -n $NAMESPACE"