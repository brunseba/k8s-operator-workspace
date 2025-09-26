"""
Core handlers for ApplicationMetadata controller.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

import kopf
import httpx
import json
from kubernetes import client

from controller.config import ControllerConfig, load_config
from controller.models import (
    ApplicationMetadata,
    ApplicationMetadataSpec,
    ApplicationMetadataStatus,
    Phase,
    ConditionType,
    ConditionStatus,
    Condition,
)
from controller.metrics import update_app_metrics

# Initialize logging
logger = logging.getLogger(__name__)

# Global configuration
config: ControllerConfig = load_config()

def create_condition(
    condition_type: ConditionType,
    status: ConditionStatus,
    reason: str,
    message: str
) -> Dict[str, Any]:
    """Create a status condition."""
    return {
        "type": condition_type.value,
        "status": status.value,
        "lastTransitionTime": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "message": message,
    }

async def verify_git_repository(url: str) -> tuple[bool, str]:
    """Verify that a Git repository exists and is accessible."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url, follow_redirects=True)
            return response.status_code == 200, "Repository verified"
    except Exception as e:
        return False, f"Failed to verify repository: {str(e)}"

async def verify_dependencies(
    components: List[Dict[str, Any]]
) -> tuple[bool, List[str]]:
    """Verify that all component dependencies exist."""
    component_names = {comp["name"] for comp in components}
    errors = []
    
    for component in components:
        if "dependencies" in component:
            for dep in component["dependencies"]:
                if dep not in component_names:
                    errors.append(
                        f"Component '{component['name']}' depends on '{dep}' which does not exist"
                    )
    
    return len(errors) == 0, errors

async def check_component_health(
    component: Dict[str, Any]
) -> tuple[bool, str]:
    """Check health of a component."""
    # This is a simplified health check
    # In production, you would:
    # 1. Check actual component health (e.g., database connectivity)
    # 2. Check associated resources (pods, services, etc.)
    # 3. Run component-specific health checks
    return True, f"Component '{component['name']}' is healthy"

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    """Configure the operator."""
    settings.posting.level = logging.INFO
    settings.watching.connect_timeout = 60
    settings.watching.server_timeout = 600
    
    # Set up logging
    log_level = getattr(logging, config.logging.level.upper())
    logging.basicConfig(
        level=log_level,
        format=config.logging.format
    )
    
    logger.info(f"🚀 Starting ApplicationMetadata controller v{config.version}")
    logger.info(f"⚙️ Configuration loaded: {config.dict()}")

@kopf.on.create("apps.company.io", "v1", "applicationmetadata")
async def create_fn(spec: Dict[str, Any], meta: Dict[str, Any], status: kopf.Status, patch: kopf.Patch, logger: logging.Logger, **kwargs):
    """Handle creation of ApplicationMetadata resources."""
    name = meta["name"]
    namespace = meta["namespace"]
    logger.info(f"📦 Creating ApplicationMetadata: {namespace}/{name}")
    
    try:
        # Validate using Pydantic model
        app_spec = ApplicationMetadataSpec(**spec)
        now = datetime.now(timezone.utc)
        
        # Initialize status
        new_status = ApplicationMetadataStatus(
            phase=Phase.PENDING,
            conditions=[
                Condition(
                    type=ConditionType.READY,
                    status=ConditionStatus.UNKNOWN,
                    lastTransitionTime=now,
                    reason="Initializing",
                    message=f"Initializing application {name}"
                )
            ],
            lastUpdated=now,
            observedVersion=spec["version"],
            observedGeneration=meta.get("generation", 1)
        )
        
        # Verify Git repositories if enabled
        if config.validation.verify_git_repos and app_spec.tracking.repository:
            repo_ok, repo_msg = await verify_git_repository(str(app_spec.tracking.repository))
            if not repo_ok:
                new_status.phase = Phase.ERROR
                new_status.conditions.append(
                    Condition(
                        type=ConditionType.READY,
                        status=ConditionStatus.FALSE,
                        lastTransitionTime=now,
                        reason="RepositoryNotAccessible",
                        message=repo_msg
                    )
                )
        
        # Verify dependencies if enabled
        if config.validation.strict_dependency_checks:
            deps_ok, errors = await verify_dependencies(spec.get("composition", []))
            if not deps_ok:
                new_status.phase = Phase.ERROR
                new_status.conditions.append(
                    Condition(
                        type=ConditionType.READY,
                        status=ConditionStatus.FALSE,
                        lastTransitionTime=now,
                        reason="DependencyValidationFailed",
                        message="; ".join(errors)
                    )
                )
        
        if new_status.phase != Phase.ERROR:
            new_status.conditions.append(
                Condition(
                    type=ConditionType.READY,
                    status=ConditionStatus.TRUE,
                    lastTransitionTime=now,
                    reason="ValidationPassed",
                    message="Application validated successfully"
                )
            )
        
        # Update metrics
        update_app_metrics(name, namespace, new_status)
        
        # Update status via patch (assign per-field for Kopf v1)
        status_payload = json.loads(new_status.json())
        for k, v in status_payload.items():
            patch.status[k] = v
        
    except Exception as e:
        logger.error(f"❌ Failed to create ApplicationMetadata {namespace}/{name}: {e}")
        raise kopf.PermanentError(f"Failed to create resource: {e}")

@kopf.on.update("apps.company.io", "v1", "applicationmetadata")
async def update_fn(spec: Dict[str, Any], meta: Dict[str, Any], status: kopf.Status, patch: kopf.Patch, logger: logging.Logger, **kwargs):
    """Handle updates to ApplicationMetadata resources."""
    name = meta["name"]
    namespace = meta["namespace"]
    logger.info(f"📝 Updating ApplicationMetadata: {namespace}/{name}")
    
    try:
        # Re-validate using Pydantic model
        app_spec = ApplicationMetadataSpec(**spec)
        now = datetime.now(timezone.utc)
        
        # Check health of components
        healthy_components = []
        unhealthy_components = []
        
        for component in app_spec.composition:
            is_healthy, message = await check_component_health(component.dict())
            if is_healthy:
                healthy_components.append(component.name)
            else:
                unhealthy_components.append((component.name, message))
        
        # Determine overall health
        all_healthy = len(unhealthy_components) == 0
        health_status = ConditionStatus.TRUE if all_healthy else ConditionStatus.FALSE
        health_reason = "AllComponentsHealthy" if all_healthy else "UnhealthyComponents"
        health_message = (
            "All components are healthy"
            if all_healthy
            else f"Unhealthy components: {', '.join(c[0] for c in unhealthy_components)}"
        )
        
        # Update status
        new_status = ApplicationMetadataStatus(
            phase=Phase.ACTIVE if all_healthy else Phase.PENDING,
            conditions=[
                Condition(
                    type=ConditionType.HEALTHY,
                    status=health_status,
                    lastTransitionTime=now,
                    reason=health_reason,
                    message=health_message
                ),
                Condition(
                    type=ConditionType.READY,
                    status=ConditionStatus.TRUE,
                    lastTransitionTime=now,
                    reason="ValidationPassed",
                    message="Application validated successfully"
                )
            ],
            lastUpdated=now,
            observedVersion=spec["version"],
            observedGeneration=meta.get("generation", 1)
        )
        
        # Update metrics
        update_app_metrics(name, namespace, new_status)
        
        # Update status via patch (assign per-field for Kopf v1)
        status_payload = json.loads(new_status.json())
        for k, v in status_payload.items():
            patch.status[k] = v
        
    except Exception as e:
        logger.error(f"❌ Failed to update ApplicationMetadata {namespace}/{name}: {e}")
        raise kopf.PermanentError(f"Failed to update resource: {e}")

@kopf.on.delete("apps.company.io", "v1", "applicationmetadata")
async def delete_fn(spec: Dict[str, Any], meta: Dict[str, Any], status: kopf.Status, logger: logging.Logger, **kwargs):
    """Handle deletion of ApplicationMetadata resources."""
    name = meta["name"]
    namespace = meta["namespace"]
    logger.info(f"🗑️ Deleting ApplicationMetadata: {namespace}/{name}")
    
    try:
        # Update metrics (remove)
        update_app_metrics(name, namespace, None, deleted=True)
        
        logger.info(f"✅ Successfully deleted ApplicationMetadata {namespace}/{name}")
        
    except Exception as e:
        logger.error(f"❌ Failed to delete ApplicationMetadata {namespace}/{name}: {e}")
        raise kopf.PermanentError(f"Failed to delete resource: {e}")

@kopf.timer("apps.company.io", "v1", "applicationmetadata",
            interval=config.reconcile_interval)
async def reconcile_fn(spec: Dict[str, Any], meta: Dict[str, Any], status: kopf.Status, patch: kopf.Patch, logger: logging.Logger, **kwargs):
    """Periodically reconcile ApplicationMetadata resources."""
    name = meta["name"]
    namespace = meta["namespace"]
    logger.debug(f"🔄 Reconciling ApplicationMetadata: {namespace}/{name}")
    
    try:
        # Re-validate and check health
        app_spec = ApplicationMetadataSpec(**spec)
        now = datetime.now(timezone.utc)
        
        # Build fresh status
        new_status = ApplicationMetadataStatus(
            phase=Phase.PENDING,
            conditions=[],
            lastUpdated=now,
            observedVersion=spec["version"],
            observedGeneration=meta.get("generation", 1)
        )
        
        # Check Git repositories
        repo_ok = True
        if config.validation.verify_git_repos and app_spec.tracking.repository:
            repo_ok, _ = await verify_git_repository(str(app_spec.tracking.repository))
            if not repo_ok:
                new_status.phase = Phase.ERROR
                new_status.conditions.append(
                    Condition(
                        type=ConditionType.READY,
                        status=ConditionStatus.FALSE,
                        lastTransitionTime=now,
                        reason="RepositoryNotAccessible",
                        message=f"Repository {app_spec.tracking.repository} is not accessible"
                    )
                )
        
        if repo_ok:
            # Check component health
            healthy_components = []
            unhealthy_components = []
            
            for component in app_spec.composition:
                is_healthy, message = await check_component_health(component.dict())
                if is_healthy:
                    healthy_components.append(component.name)
                else:
                    unhealthy_components.append((component.name, message))
            
            # Update status based on health
            all_healthy = len(unhealthy_components) == 0
            if all_healthy:
                new_status.phase = Phase.ACTIVE
                new_status.conditions.extend([
                    Condition(
                        type=ConditionType.HEALTHY,
                        status=ConditionStatus.TRUE,
                        lastTransitionTime=now,
                        reason="AllComponentsHealthy",
                        message="All components are healthy"
                    ),
                    Condition(
                        type=ConditionType.READY,
                        status=ConditionStatus.TRUE,
                        lastTransitionTime=now,
                        reason="ValidationPassed",
                        message="Application validated successfully"
                    )
                ])
            else:
                new_status.phase = Phase.PENDING
                new_status.conditions.extend([
                    Condition(
                        type=ConditionType.HEALTHY,
                        status=ConditionStatus.FALSE,
                        lastTransitionTime=now,
                        reason="UnhealthyComponents",
                        message=f"Unhealthy components: {', '.join(c[0] for c in unhealthy_components)}"
                    ),
                    Condition(
                        type=ConditionType.READY,
                        status=ConditionStatus.TRUE,
                        lastTransitionTime=now,
                        reason="ValidationPassed",
                        message="Application is valid but not all components are healthy"
                    )
                ])
        
        # Update metrics
        update_app_metrics(name, namespace, new_status)
        
        # Update status via patch (assign per-field for Kopf v1)
        status_payload = json.loads(new_status.json())
        for k, v in status_payload.items():
            patch.status[k] = v
        
    except Exception as e:
        logger.error(f"❌ Failed to reconcile ApplicationMetadata {namespace}/{name}: {e}")
        # Don't raise error - let it retry next reconciliation
