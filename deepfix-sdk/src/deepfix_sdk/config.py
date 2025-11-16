"""
Configuration management for DeepSight Advisor.

This module provides comprehensive configuration classes for the advisor,
including YAML loading, validation, and default value management.
"""

from typing import Optional

from deepfix_core.models import DefaultPaths
from pydantic import BaseModel, Field, field_validator


class MLflowConfig(BaseModel):
    """Configuration for MLflow integration.

    Attributes:
        tracking_uri: MLflow tracking server URI. Must start with http://,
            https://, or file://.
        run_id: Optional MLflow run ID to analyze.
        download_dir: Local directory for downloading artifacts.
        create_run_if_not_exists: Whether to create the run if it doesn't exist.
            Defaults to False.
        experiment_name: MLflow experiment name for deepfix.
        trace_dspy: Whether to trace dspy requests. Defaults to True.
    """

    tracking_uri: str = Field(
        default=DefaultPaths.MLFLOW_TRACKING_URI.value,
        description="MLflow tracking server URI",
    )
    run_id: Optional[str] = Field(default=None, description="MLflow run ID to analyze")
    download_dir: str = Field(
        default=DefaultPaths.MLFLOW_DOWNLOADS.value,
        description="Local directory for downloading artifacts",
    )
    create_run_if_not_exists: bool = Field(
        default=False,
        description="Whether to create the run if it doesn't exist",
    )
    experiment_name: str = Field(
        default=DefaultPaths.EXPERIMENT_NAME.value,
        description="MLflow experiment name for deepfix",
    )
    trace_dspy: bool = Field(
        default=True,
        description="Whether to trace dspy requests",
    )

    @field_validator("tracking_uri")
    @classmethod
    def validate_tracking_uri(cls, v: str) -> str:
        """Validate tracking URI format.

        Args:
            v: Tracking URI string to validate.

        Returns:
            Validated tracking URI.

        Raises:
            ValueError: If URI doesn't start with http://, https://, or file://.
        """
        if not v.startswith(
            (
                "http://",
                "https://",
                "file://",
            )
        ):
            raise ValueError(
                "tracking_uri must start with http://, https://, or file://"
            )
        return v


class ArtifactConfig(BaseModel):
    """Configuration for artifact management.

    Attributes:
        load_training: Whether to load training artifacts. Defaults to False.
        load_checks: Whether to load Deepchecks artifacts. Defaults to True.
        load_dataset_metadata: Whether to load dataset metadata. Defaults to True.
        load_model_checkpoint: Whether to load model checkpoint. Defaults to True.
        download_if_missing: Whether to download artifacts if not locally cached.
            Defaults to True.
        cache_enabled: Whether to enable local caching. Defaults to True.
        sqlite_path: Path to SQLite database for artifact caching.
    """

    load_training: bool = Field(
        default=False, description="Whether to load training artifacts"
    )
    load_checks: bool = Field(
        default=True, description="Whether to load Deepchecks artifacts"
    )
    load_dataset_metadata: bool = Field(
        default=True, description="Whether to load dataset metadata"
    )
    load_model_checkpoint: bool = Field(
        default=True, description="Whether to load model checkpoint"
    )
    download_if_missing: bool = Field(
        default=True, description="Whether to download artifacts if not locally cached"
    )
    cache_enabled: bool = Field(
        default=True, description="Whether to enable local caching"
    )
    sqlite_path: str = Field(
        default=DefaultPaths.ARTIFACTS_SQLITE_PATH.value,
        description="Path to SQLite database for artifact caching",
    )
