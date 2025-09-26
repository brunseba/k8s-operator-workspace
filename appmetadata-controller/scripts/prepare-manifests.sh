#!/bin/bash
set -e

cd "$(dirname "$0")/.."  # Change to project root

# Create directories if they don't exist
WORK_DIR="manifests/files"
mkdir -p "${WORK_DIR}"

# Copy Python files
cp src/controller/*.py "${WORK_DIR}"/

# Copy config file
cp manifests/config.yaml "${WORK_DIR}"/

echo "✅ Files prepared for kustomize in ${WORK_DIR}/"