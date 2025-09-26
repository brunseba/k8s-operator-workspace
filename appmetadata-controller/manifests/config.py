"""
Configuration management for the ApplicationMetadata controller.
"""
import os
from typing import Dict, Any

import yaml
from pydantic import BaseModel, Field


class MetricsConfig(BaseModel):
    """Prometheus metrics configuration."""
    enabled: bool = True
    port: int = 9090
    path: str = "/metrics"


class WebhookConfig(BaseModel):
    """Webhook configuration."""
    enabled: bool = True
    port: int = 8443
    cert_file: str = "/etc/webhook/certs/tls.crt"
    key_file: str = "/etc/webhook/certs/tls.key"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    json: bool = False


class ValidationConfig(BaseModel):
    """Validation configuration."""
    strict_dependency_checks: bool = True
    verify_git_repos: bool = True
    verify_jira_tickets: bool = False
    auto_status_updates: bool = True


class ControllerConfig(BaseModel):
    """Main controller configuration."""
    name: str = "appmetadata-controller"
    namespace: str = "appmetadata-system"
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    webhook: WebhookConfig = Field(default_factory=WebhookConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    reconcile_interval: int = 300  # seconds


def load_config() -> ControllerConfig:
    """Load controller configuration from file or environment."""
    config_path = os.environ.get("CONFIG_PATH", "/etc/appmetadata/config.yaml")
    
    # Default config
    config = ControllerConfig()
    
    # Load from file if exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            file_config = yaml.safe_load(f)
            if file_config:
                config = ControllerConfig(**file_config)
    
    return config