from __future__ import annotations
from typing import Dict, Any
from enum import StrEnum
import os
from pydantic import BaseModel, Field
from typing import Optional, Union
from omegaconf import DictConfig, OmegaConf
from platformdirs import (
    user_data_dir,
    user_cache_dir,
    user_log_dir,
)
import tempfile
from pathlib import Path
import logging



# Defaults
logger = logging.getLogger(__name__)

def get_workdir():
    candidates = [
        Path.home() / ".deepfix",
        Path("/content/.deepfix"), # for Google Colab
        Path(tempfile.gettempdir()) / ".deepfix",
    ]
    
    for path in candidates:
        parent = path.parent        
        # Check if parent exists and is writable
        if parent.exists() and os.access(parent, os.W_OK):
            path.mkdir(parents=True, exist_ok=True)
            return path
    
    raise RuntimeError("No writable directory found")

def _get_base_dirs() -> Dict[str, Path]:
    env_home = os.environ.get("DEEPFIX_HOME", get_workdir())
    if env_home:
        return {
            "data": env_home / "data",
            "cache": env_home / "cache",
            "log": env_home / "logs",
        }

def _default_mlflow_tracking_uri(data_dir: Path) -> str:
    mlruns_dir = data_dir / "deepfix_mlflow"
    mlruns_dir.parent.mkdir(parents=True, exist_ok=True)
    return mlruns_dir.resolve().as_uri() #.replace("file://", "sqlite://")


def _default_mlflow_downloads_dir(data_dir: Path) -> str:
    downloads = data_dir / "mlflow_downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    return str(downloads)


def _default_mlflow_artifact_root(data_dir: Path) -> str:
    artifact_root = data_dir / "mlflow_artifacts"
    artifact_root.mkdir(parents=True, exist_ok=True)
    return str(artifact_root)


def _default_sqlite_path(data_dir: Path) -> str:
    sqlite_path = data_dir / "tmp" / "artifacts.db"
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return str(sqlite_path)


def _default_output_dir(data_dir: Path) -> str:
    out = data_dir / "advisor_output"
    out.mkdir(parents=True, exist_ok=True)
    return str(out)


def _default_knowledge_base_dir(data_dir: Path) -> str:
    knowledge_base_dir = data_dir / "knowledge_base"
    knowledge_base_dir.mkdir(parents=True, exist_ok=True)
    return str(knowledge_base_dir)


def _default_knowledge_base_indices_dir(data_dir: Path) -> str:
    p = _default_knowledge_base_dir(data_dir)
    knowledge_base_indices_dir = Path(p) / "indices"
    knowledge_base_indices_dir.mkdir(parents=True, exist_ok=True)
    return str(knowledge_base_indices_dir)


def _default_knowledge_base_documents_dir(data_dir: Path) -> str:
    p = _default_knowledge_base_dir(data_dir)
    knowledge_base_documents_dir = Path(p) / "documents"
    knowledge_base_documents_dir.mkdir(parents=True, exist_ok=True)
    return str(knowledge_base_documents_dir)


_BASE_DIRS = _get_base_dirs()

class DataType(StrEnum):
    VISION = "vision"
    TABULAR = "tabular"
    NLP = "nlp"

class TaskType(StrEnum):
    # tabular tasks
    TABULAR_CLASSIFICATION = "tabular_classification"
    TABULAR_REGRESSION = "tabular_regression"
    # vision tasks
    IMAGE_SEGMENTATION = "image_segmentation"
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    # NLP tasks
    TEXT_CLASSIFICATION = "text_classification"
    TEXT_TOKEN_CLASSIFICATION = "text_token_classification"

class DeepchecksConfig(BaseModel):
    train_test_validation: bool = Field(
        default=True, description="Whether to run the train_test_validation suite"
    )
    data_integrity: bool = Field(
        default=True, description="Whether to run the data_integrity suite"
    )
    model_evaluation: bool = Field(
        default=False, description="Whether to run the model_evaluation suite"
    )
    max_samples: Optional[int] = Field(
        default=None, description="Maximum number of samples to run the suites on"
    )
    random_state: int = Field(
        default=42, description="Random seed to use for the suites"
    )
    save_results: bool = Field(default=False, description="Whether to save the results")
    output_dir: Optional[str] = Field(
        default=None, description="Output directory to save the results"
    )
    batch_size: int = Field(default=16, description="Batch size to use for the suites")
    data_type: DataType = Field(
        default=DataType.VISION, description="Type of data to run the suites on"
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        dumped_dict["data_type"] = self.data_type.value
        return dumped_dict

    @classmethod
    def from_dict(cls, config: Union[Dict[str, Any], DictConfig]) -> "DeepchecksConfig":
        return cls(**config)

    @classmethod
    def from_file(cls, file_path: str) -> "DeepchecksConfig":
        return cls.from_dict(OmegaConf.load(file_path))


class DefaultPaths(StrEnum):
    MLFLOW_TRACKING_URI = _default_mlflow_tracking_uri(_BASE_DIRS["data"])
    MLFLOW_DOWNLOADS = _default_mlflow_downloads_dir(_BASE_DIRS["data"])
    MLFLOW_RUN_NAME = "default"
    MLFLOW_DEFAULT_ARTIFACT_ROOT = _default_mlflow_artifact_root(_BASE_DIRS["data"])

    DATASETS_EXPERIMENT_NAME = "deepfix_datasets"
    EXPERIMENT_NAME = "deepfix"
    TRAINING_EXPERIMENT_NAME = "deepfix_training"

    ARTIFACTS_SQLITE_PATH = _default_sqlite_path(_BASE_DIRS["data"])

    ADVISOR_OUTPUT_DIR = _default_output_dir(_BASE_DIRS["data"])

    KNOWLEDGE_BASE_DIR = _default_knowledge_base_dir(_BASE_DIRS["data"])
    KNOWLEDGE_BASE_INDICES_DIR = _default_knowledge_base_indices_dir(_BASE_DIRS["data"])
    KNOWLEDGE_BASE_DOCUMENTS_DIR = _default_knowledge_base_documents_dir(
        _BASE_DIRS["data"]
    )
