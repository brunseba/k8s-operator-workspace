#!/bin/bash
set -e

# Ensure running from project root
cd "$(dirname "$0")/.."

# Create a working directory
WORK_DIR="manifests/files"
mkdir -p "$WORK_DIR"

# Copy files from src/controller to manifests/files
cp src/controller/*.py "$WORK_DIR"/
touch "$WORK_DIR"/__init__.py

# Create config.yaml in working directory
cat > "$WORK_DIR"/config.yaml << 'EOL'
logging:
  level: INFO
  format: json
  handlers:
    - console

metrics:
  enabled: true
  port: 9090
  path: /metrics

validation:
  strict: true
  auto_id_prefix: app-
  max_components: 20
  max_dependencies: 10
  max_maintainers: 5
  max_tags: 10
  reserved_tags:
    - system
    - legacy
    - critical
    - deprecated
EOL

# Update kustomization.yaml
cat > manifests/kustomization.yaml << 'EOL'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: appmetadata-system

commonLabels:
  app.kubernetes.io/name: appmetadata-controller
  app.kubernetes.io/part-of: appmetadata-system
  app.kubernetes.io/version: "1.0.0"

resources:
- crd.yaml
- namespace.yaml
- serviceaccount.yaml
- role.yaml
- clusterrole.yaml
- clusterrolebinding.yaml
- deployment.yaml

configMapGenerator:
- name: appmetadata-controller-code
  files:
  - files/config.yaml=config.yaml
  - files/__init__.py=__init__.py
  - files/__main__.py=__main__.py
  - files/config.py=config.py
  - files/models.py=models.py
  - files/metrics.py=metrics.py
  - files/handlers.py=handlers.py
  options:
    disableNameSuffixHash: true
EOL

echo "✅ Files prepared successfully"