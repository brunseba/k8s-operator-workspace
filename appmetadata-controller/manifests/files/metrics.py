"""
Prometheus metrics for ApplicationMetadata controller.
"""
import logging
from typing import Dict, Optional

from prometheus_client import Counter, Gauge, Histogram
from controller.models import ApplicationMetadataStatus, Phase

# Initialize logger
logger = logging.getLogger(__name__)

# Metrics definitions
APPS_TOTAL = Gauge(
    "appmetadata_applications_total",
    "Total number of applications by phase",
    ["phase"]
)

APPS_BY_ENVIRONMENT = Gauge(
    "appmetadata_applications_by_environment",
    "Number of applications by environment",
    ["environment"]
)

APPS_BY_BUSINESS_UNIT = Gauge(
    "appmetadata_applications_by_business_unit",
    "Number of applications by business unit",
    ["business_unit"]
)

COMPONENT_COUNT = Gauge(
    "appmetadata_components_total",
    "Total number of components by type",
    ["type"]
)

STATUS_CHANGES = Counter(
    "appmetadata_status_changes_total",
    "Number of application status changes",
    ["from_phase", "to_phase"]
)

RECONCILIATION_DURATION = Histogram(
    "appmetadata_reconciliation_duration_seconds",
    "Time spent reconciling applications",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

VALIDATION_ERRORS = Counter(
    "appmetadata_validation_errors_total",
    "Number of validation errors by type",
    ["error_type"]
)

# Cache for tracking application phases
_app_phases: Dict[str, str] = {}

def _get_app_key(name: str, namespace: str) -> str:
    """Generate a unique key for an application."""
    return f"{namespace}/{name}"

def update_app_metrics(
    name: str,
    namespace: str,
    status: Optional[ApplicationMetadataStatus],
    deleted: bool = False
) -> None:
    """Update metrics for an application."""
    try:
        app_key = _get_app_key(name, namespace)
        
        if deleted:
            # Decrease counters if app is deleted
            if app_key in _app_phases:
                old_phase = _app_phases[app_key]
                APPS_TOTAL.labels(phase=old_phase).dec()
                del _app_phases[app_key]
            return
        
        if not status:
            return
            
        # Update phase metrics
        new_phase = status.phase
        if app_key in _app_phases:
            old_phase = _app_phases[app_key]
            if old_phase != new_phase:
                # Phase changed
                APPS_TOTAL.labels(phase=old_phase).dec()
                APPS_TOTAL.labels(phase=new_phase).inc()
                STATUS_CHANGES.labels(
                    from_phase=old_phase,
                    to_phase=new_phase
                ).inc()
        else:
            # New application
            APPS_TOTAL.labels(phase=new_phase).inc()
        
        _app_phases[app_key] = new_phase
        
    except Exception as e:
        logger.error(f"Failed to update metrics for {namespace}/{name}: {e}")

def record_validation_error(error_type: str) -> None:
    """Record a validation error."""
    try:
        VALIDATION_ERRORS.labels(error_type=error_type).inc()
    except Exception as e:
        logger.error(f"Failed to record validation error: {e}")

def start_reconciliation() -> None:
    """Start timing a reconciliation operation."""
    return RECONCILIATION_DURATION.time()