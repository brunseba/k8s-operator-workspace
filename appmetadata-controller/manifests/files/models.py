"""
Data models for ApplicationMetadata controller.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, constr


class ComponentType(str, Enum):
    """Type of application component."""
    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    FRONTEND = "frontend"
    BACKEND = "backend"
    MIDDLEWARE = "middleware"
    STORAGE = "storage"


class Environment(str, Enum):
    """Application deployment environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DR = "dr"
    TEST = "test"
    QA = "qa"


class Phase(str, Enum):
    """Application lifecycle phase."""
    PENDING = "Pending"
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"
    RETIRED = "Retired"


class ConditionType(str, Enum):
    """Types of conditions that can be set on ApplicationMetadata."""
    READY = "Ready"
    AVAILABLE = "Available"
    HEALTHY = "Healthy"
    UP_TO_DATE = "UpToDate"


class ConditionStatus(str, Enum):
    """Status values for conditions."""
    TRUE = "True"
    FALSE = "False"
    UNKNOWN = "Unknown"


class TeamInfo(BaseModel):
    """Team information."""
    owner: str = Field(pattern=r"^[a-zA-Z][-a-zA-Z0-9.]*[a-zA-Z0-9]$")
    email: str = Field(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    slack: str = Field(pattern=r"^#[a-zA-Z0-9_-]+$")


class Component(BaseModel):
    """Application component."""
    name: str = Field(pattern=r"^[a-zA-Z][-a-zA-Z0-9]*[a-zA-Z0-9]$")
    type: ComponentType
    version: str
    repository: Optional[HttpUrl] = None
    dependencies: Optional[List[str]] = None


class Tracking(BaseModel):
    """Application tracking information."""
    jira: Optional[str] = Field(None, pattern=r"^[A-Z]+-[0-9]+$")
    repository: HttpUrl
    pipeline: str = Field(pattern=r"^[a-zA-Z][-a-zA-Z0-9/]*[a-zA-Z0-9]$")
    documentation: HttpUrl


class Condition(BaseModel):
    """Status condition."""
    type: ConditionType
    status: ConditionStatus
    lastTransitionTime: datetime
    reason: Optional[str] = None
    message: Optional[str] = None


class ApplicationMetadataSpec(BaseModel):
    """ApplicationMetadata specification."""
    id: str = Field(pattern=r"^[a-zA-Z0-9][-a-zA-Z0-9]*[a-zA-Z0-9]$", min_length=3, max_length=63)
    name: str = Field(pattern=r"^[a-zA-Z][-a-zA-Z0-9]*[a-zA-Z0-9]$", min_length=2, max_length=253)
    businessUnit: str = Field(pattern=r"^[a-zA-Z][-a-zA-Z0-9]*[a-zA-Z0-9]$", min_length=2, max_length=63)
    environment: Environment
    version: str = Field(pattern=r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
    description: Optional[str] = Field(None, max_length=1024)
    team: TeamInfo
    composition: List[Component]
    tracking: Tracking
    tags: Optional[List[str]] = Field(None, pattern=r"^[a-zA-Z0-9][-a-zA-Z0-9_]*[a-zA-Z0-9]$")


class ApplicationMetadataStatus(BaseModel):
    """ApplicationMetadata status."""
    phase: Phase = Phase.PENDING
    conditions: Optional[List[Condition]] = None
    lastUpdated: Optional[datetime] = None
    observedVersion: Optional[str] = None
    observedGeneration: Optional[int] = None


class ApplicationMetadata(BaseModel):
    """Complete ApplicationMetadata resource."""
    apiVersion: str = "apps.company.io/v1"
    kind: str = "ApplicationMetadata"
    metadata: Dict
    spec: ApplicationMetadataSpec
    status: Optional[ApplicationMetadataStatus] = None