#!/bin/bash
set -e

echo "🚀 === Pet Controller ConfigMap-based Deployment ==="
echo

# Configuration
NAMESPACE="pet-system"
CONTROLLER_NAME="pet-controller-configmap"
CONFIG_MAP_NAME="pet-controller-enhanced-config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manifests/kustomization.yaml" ]; then
    print_error "Please run this script from the pet-controller directory"
    exit 1
fi

print_status "Checking prerequisites..."

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is required but not installed"
    exit 1
fi

# Check cluster connection
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

print_success "Prerequisites check passed"
echo

# Check if Pet CRD exists
print_status "Checking for Pet CRD..."
if kubectl get crd pets.petstore.example.com &> /dev/null; then
    print_success "Pet CRD found"
else
    print_error "Pet CRD not found. Please install the Pet CRD first"
    echo "Run: kubectl apply -f pet-crd.yaml"
    exit 1
fi

# Clean up old deployments if they exist
print_status "Cleaning up old deployments..."

# Remove old controller deployments
kubectl delete deployment pet-controller -n $NAMESPACE --ignore-not-found=true
kubectl delete deployment pet-controller-working -n $NAMESPACE --ignore-not-found=true

# Remove old ConfigMaps
kubectl delete configmap pet-controller-code -n $NAMESPACE --ignore-not-found=true

print_success "Cleanup completed"
echo

# Deploy using kustomize
print_status "Deploying Pet Controller with ConfigMap approach..."

cd manifests
kubectl apply -k .
cd ..

print_success "Manifests applied successfully"
echo

# Wait for deployment to be ready
print_status "Waiting for deployment to be ready..."

if kubectl wait --for=condition=available --timeout=300s deployment/$CONTROLLER_NAME -n $NAMESPACE; then
    print_success "Deployment is ready!"
else
    print_error "Deployment failed to become ready within 5 minutes"
    echo
    print_status "Checking pod status..."
    kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=pet-controller
    echo
    print_status "Recent events:"
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
    exit 1
fi

echo

# Show deployment status
print_status "Deployment Status:"
kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=pet-controller -o wide

echo
print_status "Service Information:"
kubectl get svc -n $NAMESPACE -l app.kubernetes.io/name=pet-controller || echo "No services found"

echo
print_status "ConfigMap Information:"
kubectl get configmap $CONFIG_MAP_NAME -n $NAMESPACE

echo
print_status "Controller Logs (last 10 lines):"
kubectl logs -n $NAMESPACE deployment/$CONTROLLER_NAME --tail=10 || echo "No logs available yet"

echo
print_success "=== Pet Controller Deployment Complete ==="
echo

# Provide useful commands
print_status "Useful Commands:"
echo
echo "📋 View controller status:"
echo "  kubectl get pods -n $NAMESPACE"
echo
echo "📝 View controller logs:"
echo "  kubectl logs -n $NAMESPACE deployment/$CONTROLLER_NAME -f"
echo
echo "⚙️ View configuration:"
echo "  kubectl get configmap $CONFIG_MAP_NAME -n $NAMESPACE -o yaml"
echo
echo "🔄 Restart controller:"
echo "  kubectl rollout restart deployment/$CONTROLLER_NAME -n $NAMESPACE"
echo
echo "📊 Check Pet resources:"
echo "  kubectl get pets --all-namespaces"
echo
echo "🧪 Test controller:"
echo "  ./scripts/test-controller.sh"
echo
echo "🗑️ Remove deployment:"
echo "  kubectl delete -k manifests/"
echo

# Test basic functionality
print_status "Running basic functionality test..."

# Create a test pet
TEST_PET="test-deployment-$(date +%s)"
cat <<EOF | kubectl apply -f -
apiVersion: petstore.example.com/v1
kind: Pet
metadata:
  name: $TEST_PET
  namespace: default
  labels:
    test: deployment-verification
spec:
  id: 42
  name: "Deployment Test Pet"
  tag: "configmap-deployment"
EOF

print_success "Test pet created: $TEST_PET"

# Wait a moment for processing
sleep 5

# Check if controller processed it
if kubectl logs -n $NAMESPACE deployment/$CONTROLLER_NAME --tail=5 | grep -q "$TEST_PET"; then
    print_success "Controller is processing Pet resources correctly!"
else
    print_warning "Controller might not be processing pets yet - check logs"
fi

# Cleanup test pet
kubectl delete pet $TEST_PET --ignore-not-found=true
print_status "Test pet cleaned up"

echo
print_success "🎉 Pet Controller is ready and operational!"

# Show final status
echo
print_status "Final Status Summary:"
echo "📍 Namespace: $NAMESPACE"
echo "🎛️ Controller: $CONTROLLER_NAME"
echo "📋 ConfigMap: $CONFIG_MAP_NAME"
echo "🔧 Configuration: Enhanced with comprehensive settings"
echo "🐍 Runtime: Python 3.11 with ConfigMap-based code loading"
echo "✅ Status: $(kubectl get deployment $CONTROLLER_NAME -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Available")].status}')"

replicas=$(kubectl get deployment $CONTROLLER_NAME -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
echo "🔢 Ready Replicas: ${replicas:-0}/1"