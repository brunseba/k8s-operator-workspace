# Pet Controller

A Kubernetes controller for managing Pet Custom Resource Definitions (CRDs).

## Overview

The Pet Controller automatically manages the lifecycle and status of Pet resources in your Kubernetes cluster. It:

- Validates Pet specifications when created or updated
- Performs health checks on pets (simulated)
- Updates Pet status phases: `Pending` → `Active` (or `Error` if issues occur)
- Manages status conditions for detailed state tracking
- Runs periodic reconciliation to ensure desired state

## Project Structure

```
pet-controller/
├── examples/                    # Example resources
│   ├── invalid/                # Invalid examples (for validation testing)
│   │   └── pets.yaml
│   ├── tests/                  # Test scenarios
│   │   └── *.yaml
│   └── valid/                  # Valid example resources
│       └── pets.yaml
├── manifests/                  # Kubernetes manifests
│   └── base/                   # Kustomize base
│       ├── configmaps/        # Controller code and config
│       │   ├── controller-code.yaml
│       │   └── kustomization.yaml
│       ├── crds/              # Custom Resource Definitions
│       │   ├── pets.yaml
│       │   ├── petstores.yaml
│       │   └── kustomization.yaml
│       ├── deployments/       # Controller deployment
│       │   ├── controller.yaml
│       │   └── kustomization.yaml
│       ├── monitoring/        # Metrics and monitoring
│       │   ├── service.yaml
│       │   ├── servicemonitor.yaml
│       │   └── kustomization.yaml
│       ├── rbac/             # RBAC configuration
│       │   ├── role.yaml
│       │   └── kustomization.yaml
│       └── kustomization.yaml
├── src/                        # Controller source code
│   └── controller/            # Python package
│       └── main.py
├── BACKLOG.md                  # Planned improvements
├── Dockerfile                  # Container build
└── README.md                   # This file
```

### Quick Start

### Prerequisites

- Kubernetes cluster with kubectl access
- Python 3.11+ (for local development)
- Docker (for building images)

### Installation

1. Install CRDs and create namespace:
   ```bash
   kubectl apply -k manifests/base/crds/
   kubectl create namespace pet-system
   ```

2. Deploy RBAC and controller:
   ```bash
   kubectl apply -k manifests/base/rbac/
   kubectl apply -k manifests/base/configmaps/
   kubectl apply -f manifests/base/deployments/controller.yaml
   ```

3. (Optional) Deploy metrics service:
   ```bash
   kubectl apply -k manifests/base/monitoring/
   ```

4. Verify deployment:
   ```bash
   kubectl -n pet-system get pods
   kubectl -n pet-system logs -l app.kubernetes.io/name=pet-controller
   ```

### Local Development

1. Setup Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run controller locally:
   ```bash
   PYTHONPATH=src python -m controller.main
   ```

### Testing

1. Create a test Pet:
   ```bash
   kubectl apply -f examples/valid/pets.yaml
   ```

2. Check status:
   ```bash
   kubectl get pets
   kubectl describe pet buddy
   ```

3. Verify validation:
   ```bash
   # This should fail validation
   kubectl apply -f examples/invalid/pets.yaml
   ```

## Controller Behavior

### Pet Lifecycle

1. **Creation**: When a Pet is created, the controller:
   - Validates the specification
   - Sets initial status to `Pending`
   - Adds a `Ready: Unknown` condition

2. **Health Checks**: The controller periodically:
   - Performs health checks (simulated based on Pet ID)
   - Updates status to `Active` if healthy
   - Updates conditions with detailed status

3. **Updates**: When a Pet spec is modified:
   - Re-validates the specification
   - Triggers reconciliation
   - Updates status accordingly

4. **Deletion**: Performs cleanup (if needed)

### Status Phases

- **`Pending`**: Initial state or health check in progress
- **`Active`**: Pet is healthy and ready
- **`Inactive`**: Pet is not currently active (future use)
- **`Error`**: Validation or other errors occurred

### Health Check Logic (Simulated)

The controller includes a simple simulation:
- Pets with even IDs → immediately healthy (`Active`)
- Pets with odd IDs → may need time to become healthy
- IDs divisible by 3 → become healthy after some checks

*In a real implementation, this would be actual business logic specific to your use case.*

## Custom Resources

### Pet
```yaml
apiVersion: petstore.example.com/v1
kind: Pet
metadata:
  name: buddy
  namespace: default
spec:
  id: 1            # Unique identifier (required)
  name: "Buddy"    # Display name (required)
  tag: "dog"       # Optional tag
```

### PetStore
```yaml
apiVersion: petstore.example.com/v1
kind: PetStore
metadata:
  name: downtown
  namespace: default
spec:
  name: "Downtown Pet Store"
  config:
    maxPets: 100
    allowedTags:
      - "dog"
      - "cat"
      - "bird"
```

## Monitoring

The controller exposes metrics at `:9090/metrics`:
- Pet count by phase
- Reconciliation durations
- Error rates

### Metrics Access
```bash
# Port forward the metrics service
kubectl -n pet-system port-forward svc/pet-controller-metrics 9090:9090

# Query metrics
curl localhost:9090/metrics
```

### Logs
```bash
# Controller logs
kubectl logs -f deployment/pet-controller -n pet-system

# Events related to Pet resources
kubectl get events --field-selector involvedObject.kind=Pet
```

### Status
```bash
# List all pets with status
kubectl get pets --all-namespaces

# Detailed pet status
kubectl get pet <pet-name> -o yaml
```

## Development

### Adding New Features

1. **Modify controller logic** in `src/controller.py`
2. **Update configuration** in `config.yaml` if needed
3. **Test locally** with `./scripts/run-local.sh`
4. **Build and deploy** with `./scripts/build-and-deploy.sh`

### Key Libraries Used

- **[kopf](https://kopf.readthedocs.io/)**: Kubernetes operator framework
- **[kubernetes](https://github.com/kubernetes-client/python)**: Official Kubernetes Python client
- **[pyyaml](https://pyyaml.org/)**: YAML parsing

## Troubleshooting

### Controller Not Starting
- Check RBAC permissions: `kubectl auth can-i get pets --as=system:serviceaccount:pet-system:pet-controller`
- Verify CRD exists: `kubectl get crd pets.petstore.example.com`
- Check logs: `kubectl logs deployment/pet-controller -n pet-system`

### Status Not Updating
- Verify controller is running: `kubectl get pods -n pet-system`
- Check for errors in logs
- Ensure Pet resources are not in `Error` state (requires manual fix)

### Permission Issues
- Verify ClusterRole includes all necessary permissions
- Check ClusterRoleBinding is correct
- Ensure ServiceAccount is properly configured

## Contributing

1. Make changes to the controller logic
2. Test locally with existing Pet resources
3. Run the test suite: `./scripts/test-controller.sh`
4. Update documentation if needed

## License

This Pet Controller is provided as an example for educational purposes.