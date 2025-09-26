#!/bin/bash
set -e

# Change to project root directory
cd "$(dirname "$0")/.."

# Create files directory
mkdir -p manifests/files

# Copy Python files from src to files/
cp src/controller/*.py manifests/files/

# Create kustomization.yaml
cat > manifests/kustomization.yaml << 'EOL'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: appmetadata-system

resources:
- namespace.yaml
- serviceaccount.yaml
- role.yaml
- clusterrole.yaml
- clusterrolebinding.yaml
- deployment.yaml

commonLabels:
  app.kubernetes.io/name: appmetadata-controller
  app.kubernetes.io/part-of: appmetadata-system
  app.kubernetes.io/version: "1.0.0"

configMapGenerator:
- name: appmetadata-controller-code
  files:
  - files/__init__.py
  - files/__main__.py
  - files/config.py
  - files/models.py
  - files/metrics.py
  - files/handlers.py
  options:
    disableNameSuffixHash: true

- name: appmetadata-controller-config
  files:
  - files/config.yaml
  options:
    disableNameSuffixHash: true
EOL

echo "✅ Kustomize files prepared successfully"