# Kubernetes Controllers Examples

This repository contains example Kubernetes controllers built with Python and the Kopf framework. Each controller demonstrates different aspects of Kubernetes operator patterns and best practices.

## Controllers

### Pet Controller
Directory: ./pet-controller

A simple controller demonstrating basic Kubernetes operator patterns:
- Custom Resource Definition (CRD) management
- Status updates and conditions
- Health checks and validation
- Prometheus metrics

Quick start:
```bash
cd pet-controller
kubectl apply -k manifests/base/crds/
kubectl create namespace pet-system
kubectl apply -k manifests/base/rbac/
kubectl apply -k manifests/base/configmaps/
kubectl apply -f manifests/base/deployments/controller.yaml
```

### Application Metadata Controller
Directory: ./appmetadata-controller

A more complex controller for managing application metadata:
- Git repository validation
- Dependency management
- Issue tracking integration
- Advanced status conditions

Quick start:
```bash
cd appmetadata-controller
kubectl apply -k manifests/base/crds/
kubectl create namespace appmetadata-system
kubectl apply -k manifests/base/rbac/
kubectl apply -k manifests/base/configmaps/
kubectl apply -f manifests/base/deployments/controller.yaml
```

## Repository Structure

```
kubernetes-objects/
├── appmetadata-controller/    # Application Metadata Controller
│   ├── examples/             # Example resources
│   ├── manifests/           # Kubernetes manifests (kustomize)
│   │   └── base/
│   ├── scripts/
│   └── src/
├── pet-controller/           # Pet Controller
│   ├── examples/
│   ├── manifests/           # Kubernetes manifests (kustomize)
│   │   └── base/
│   └── src/
└── README.md
```

## Common Features

Both controllers demonstrate:

1. Kopf Framework Usage
   - Event handlers (create/update/delete)
   - Status management and conditions
   - Finalizers and cleanup
   - Error handling

2. Kubernetes Best Practices
   - CRD validation schemas
   - Proper RBAC setup
   - Non-root containers (security context)
   - Resource requests/limits

3. Project Structure
   - Kustomize-based deployment
   - Example resources (valid/invalid/tests)
   - Clear documentation per controller
   - Modular code organization

4. Monitoring
   - Prometheus metrics endpoint (:9090/metrics)
   - Status conditions and events
   - Health checks and probes

## Development

### Prerequisites
- Python 3.11+
- Kubernetes cluster (e.g., kind, k3d)
- kubectl
- kustomize (kubectl kustomize is sufficient)

### Run a controller locally
```bash
cd pet-controller   # or appmetadata-controller
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m controller.__main__
```

## Contributing

1. Choose or create a controller directory
2. Follow the existing project structure
3. Include documentation and example resources
4. Test on a Kubernetes cluster (kind/k3d recommended)

## License

These controllers are provided as examples for educational purposes.
