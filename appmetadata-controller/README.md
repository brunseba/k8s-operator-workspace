# Application Metadata Controller

A Kubernetes operator for managing application metadata across your cluster, built with the Kopf framework.

## Overview

The Application Metadata Controller manages the lifecycle and validation of application metadata resources. It:
- Validates application metadata specifications
- Verifies Git repository references
- Validates dependencies between applications
- Updates resource status and conditions
- Exposes metrics for monitoring

## Project Structure

```
appmetadata-controller/
├── examples/                     # Example resources
│   ├── invalid/                 # Invalid examples (for validation testing)
│   └── valid/                  # Valid example resources
├── manifests/                   # Kubernetes manifests
│   └── base/                    # Kustomize base
│       ├── configmaps/         # Controller code and config
│       │   ├── controller-code.yaml
│       │   └── kustomization.yaml
│       ├── crds/               # Custom Resource Definitions
│       │   ├── kustomization.yaml
│       │   └── appmetadata.yaml
│       ├── deployments/        # Controller deployment
│       │   ├── controller.yaml
│       │   └── kustomization.yaml
│       ├── rbac/              # RBAC configuration
│       │   ├── role.yaml
│       │   └── kustomization.yaml
│       └── kustomization.yaml
├── scripts/                     # Helper scripts
│   └── prepare-kustomize.sh    # Prepare kustomize manifests
└── src/                        # Controller source code
    └── controller/             # Python package
        └── __main__.py

```

## Custom Resources

### ApplicationMetadata
```yaml
apiVersion: metadata.app.example.com/v1
kind: ApplicationMetadata
metadata:
  name: sample-webapp
  namespace: default
  labels:
    app: web
    environment: production
spec:
  # Application identification
  name: "Sample Web Application"
  description: "A sample web application demonstrating metadata management"
  version: "1.0.0"
  
  # Source code information
  repository:
    url: "https://github.com/company/sample-webapp"
    branch: "main"
    path: "/apps/webapp"
  
  # Dependencies
  dependencies:
    - name: "redis"
      version: ">=6.0.0"
      optional: false
    - name: "postgresql"
      version: "13.x"
      optional: false
  
  # Jira/Issue tracking
  issues:
    - type: "epic"
      id: "PROJ-123"
      url: "https://jira.company.com/browse/PROJ-123"
  
  # Environment configuration
  environment:
    name: "production"
    tier: "frontend"
    region: "us-west-1"
```

## Installation

1. Create namespace and apply CRDs:
   ```bash
   kubectl create namespace appmetadata-system
   kubectl apply -k manifests/base/crds/
   ```

2. Deploy RBAC and controller:
   ```bash
   kubectl apply -k manifests/base/rbac/
   kubectl apply -k manifests/base/configmaps/
   kubectl apply -f manifests/base/deployments/controller.yaml
   ```

3. Verify deployment:
   ```bash
   kubectl -n appmetadata-system get pods
   kubectl -n appmetadata-system logs -l app.kubernetes.io/name=appmetadata-controller
   ```

## Usage

1. Create an application metadata resource:
   ```bash
   cat << EOF | kubectl apply -f -
   apiVersion: metadata.app.example.com/v1
   kind: ApplicationMetadata
   metadata:
     name: sample-app
     namespace: default
   spec:
     name: "Sample Application"
     version: "1.0.0"
     repository:
       url: "https://github.com/company/sample-app"
       branch: "main"
   EOF
   ```

2. Check the status:
   ```bash
   kubectl get applicationmetadata
   kubectl describe applicationmetadata sample-app
   ```

3. Monitor the controller:
   ```bash
   kubectl -n appmetadata-system logs -l app.kubernetes.io/name=appmetadata-controller
   ```

## Features

### Validation
The controller validates:
- Required fields (name, version)
- Git repository URLs and accessibility
- Semantic version formats
- Dependency specifications
- Environment naming conventions

### Status Conditions
Resources include detailed status conditions:
```yaml
status:
  phase: Active
  conditions:
    - type: Ready
      status: "True"
      reason: ValidationPassed
      message: "All validations passed"
    - type: RepositoryAvailable
      status: "True"
      reason: GitCheckPassed
      message: "Git repository is accessible"
```

### Metrics
The controller exposes Prometheus metrics at `:9090/metrics`:
- Application count by phase
- Validation success/failure rates
- Git repository check latencies
- Dependency validation results

## Development

### Prerequisites
- Python 3.11+
- Kubernetes cluster (e.g., kind, k3d)
- kubectl

### Local Setup
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run controller locally:
   ```bash
   PYTHONPATH=src python -m controller.__main__
   ```

### Testing
1. Apply test resources:
   ```bash
   kubectl apply -f examples/valid/
   ```

2. Verify validation:
   ```bash
   kubectl apply -f examples/invalid/
   ```

3. Check controller logs:
   ```bash
   kubectl -n appmetadata-system logs -l app.kubernetes.io/name=appmetadata-controller
   ```

## Troubleshooting

### Common Issues

1. Validation Failures
   - Check the resource's status conditions
   - Verify Git repository accessibility
   - Validate dependency specifications

2. Controller Not Starting
   - Check pod status and logs
   - Verify RBAC permissions
   - Check ConfigMap exists

3. Git Checks Failing
   - Verify repository URL format
   - Check repository accessibility
   - Confirm branch/tag exists

### Debugging

```bash
# Check controller logs
kubectl -n appmetadata-system logs -l app.kubernetes.io/name=appmetadata-controller

# Check events
kubectl -n appmetadata-system get events

# Verify RBAC
kubectl auth can-i --as=system:serviceaccount:appmetadata-system:appmetadata-controller \
  -n default get applicationmetadata

# Check metrics
kubectl -n appmetadata-system port-forward svc/appmetadata-controller-metrics 9090:9090
curl localhost:9090/metrics
```

## Architecture

### Components
1. **Validator**
   - Field validation
   - Git repository checks
   - Dependency validation

2. **Status Manager**
   - Phase updates
   - Condition management
   - Event recording

3. **Metrics Collector**
   - Prometheus metrics
   - Operation latencies
   - Success/failure rates

### Workflow
1. Resource Created/Updated:
   - Validate all fields
   - Check Git repository
   - Verify dependencies
   - Update status/conditions

2. Periodic Reconciliation:
   - Recheck Git repository
   - Validate dependencies
   - Update metrics
   - Record events

3. Resource Deletion:
   - Clean up finalizers
   - Record deletion event
   - Update metrics

## License

This Application Metadata Controller is provided as an example for educational purposes.