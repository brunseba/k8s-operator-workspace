#!/bin/bash
set -e

echo "=== Pet Controller Test Suite ==="

NAMESPACE="default"
TEST_PET_NAME="test-pet-$(date +%s)"

cleanup() {
    echo "Cleaning up test resources..."
    kubectl delete pet "$TEST_PET_NAME" -n "$NAMESPACE" --ignore-not-found=true
}

trap cleanup EXIT

echo "Creating test pet: $TEST_PET_NAME"

# Create test pet
cat <<EOF | kubectl apply -f -
apiVersion: petstore.example.com/v1
kind: Pet
metadata:
  name: $TEST_PET_NAME
  namespace: $NAMESPACE
  labels:
    test: controller-test
spec:
  id: 42
  name: "Test Pet Controller"
  tag: "automated-test"
EOF

echo "Waiting for controller to process the pet..."
sleep 5

# Check initial status
echo "Checking initial status..."
kubectl get pet "$TEST_PET_NAME" -n "$NAMESPACE" -o yaml

echo "Waiting for controller to update status..."
for i in {1..10}; do
    PHASE=$(kubectl get pet "$TEST_PET_NAME" -n "$NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null || echo "")
    if [ -n "$PHASE" ] && [ "$PHASE" != "Unknown" ]; then
        echo "Pet phase updated to: $PHASE"
        break
    fi
    echo "Attempt $i/10: Waiting for status update..."
    sleep 3
done

# Display final status
echo "Final pet status:"
kubectl get pet "$TEST_PET_NAME" -n "$NAMESPACE" -o custom-columns=NAME:.metadata.name,PHASE:.status.phase,CONDITIONS:.status.conditions[*].type

# Test pet update
echo "Testing pet update..."
kubectl patch pet "$TEST_PET_NAME" -n "$NAMESPACE" --type merge -p '{"spec":{"tag":"updated-tag"}}'

echo "Waiting for update to be processed..."
sleep 5

echo "Updated pet status:"
kubectl get pet "$TEST_PET_NAME" -n "$NAMESPACE" -o yaml | grep -A 10 "status:"

echo "Test completed successfully!"
echo "Pet will be cleaned up on script exit."