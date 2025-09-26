# Pet Controller Backlog

## Status
Current implementation is functional but has some areas for improvement.

### Working Features
- ✅ Basic Pet CRD implementation
- ✅ Controller deployment with non-root security context
- ✅ Health checks and readiness probes
- ✅ RBAC setup for core functionality
- ✅ Basic metrics endpoint exposure

## Improvements Needed

### 1. Status Update Handling
**Problem**: Controller logs show "patching failed with inconsistencies" warnings.

**Solution**: Replace handler return payloads with explicit status updates.
```python
# Instead of returning dict:
return {"status": "created", "phase": "Active"}

# Use explicit status updates:
await kopf.patch_obj(
    resource=resource,
    namespace=namespace,
    name=name,
    patch={
        'status': {
            'phase': 'Active',
            'lastTransitionTime': datetime.now(timezone.utc).isoformat()
        }
    }
)
```

### 2. Prometheus Integration
**Problem**: ServiceMonitor cannot be created without Prometheus Operator CRDs.

**Tasks**:
1. Install Prometheus Operator CRDs
2. Apply monitoring manifests:
   - Service (metrics port 9090)
   - ServiceMonitor (30s scrape interval)
3. Add default alerts for:
   - Controller availability
   - Pet reconciliation failures
   - High error rates

### 3. Namespace Scoping
**Problem**: Controller running in cluster-wide mode with warnings.

**Solutions**:
1. Environment variable approach:
   ```yaml
   env:
   - name: KOPF_NAMESPACE
     value: "default,pet-system"  # Comma-separated list
   ```

2. CLI argument approach:
   ```yaml
   args:
   - --namespace=default
   - --namespace=pet-system
   ```

### 4. Additional Validations
1. **ID Uniqueness**:
   - Prevent duplicate Pet IDs across namespaces
   - Add a unique index or use a finalizer pattern

2. **Tag Validation**:
   - Implement PetStore CRD allowedTags validation
   - Add webhook for tag validation

### 5. Controller Enhancements
1. **Leader Election**:
   - Add multi-replica support
   - Implement proper leader election via leases

2. **Graceful Shutdown**:
   - Add finalizers cleanup
   - Implement proper resource cleanup on shutdown

3. **Event Recording**:
   - Add structured event recording
   - Implement event filtering and aggregation

### 6. Testing
1. **Unit Tests**:
   - Add handler unit tests
   - Add validation tests
   - Mock Kubernetes client

2. **Integration Tests**:
   - Add kind/k3d test cluster setup
   - Add e2e test suite
   - Add chaos testing scenarios

3. **Load Tests**:
   - Test with high pet count
   - Test concurrent operations
   - Measure and document limits

### 7. Documentation
1. **Architecture**:
   - Add architecture diagram
   - Document design decisions
   - Add failure handling documentation

2. **Operations**:
   - Add troubleshooting guide
   - Document common issues
   - Add runbook for alerts

3. **Development**:
   - Add development setup guide
   - Document test procedures
   - Add contribution guidelines

### 8. CI/CD Pipeline
1. **Build**:
   - Add containerization
   - Multi-arch image builds
   - Add version tagging

2. **Test**:
   - Add test automation
   - Add coverage reporting
   - Add security scanning

3. **Deploy**:
   - Add helm charts
   - Add release automation
   - Add rollback procedures

## Priority Order
1. Status Update Handling (High - affects reliability)
2. Namespace Scoping (High - security best practice)
3. Testing (High - quality assurance)
4. Leader Election (Medium - scalability)
5. Documentation (Medium - maintainability)
6. Prometheus Integration (Medium - observability)
7. Additional Validations (Low - feature enhancement)
8. CI/CD Pipeline (Low - development workflow)

## Next Steps
1. Create issues for each improvement
2. Prioritize based on user feedback
3. Create implementation plan
4. Set up development milestones