from __future__ import annotations

import math
from enum import StrEnum
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import yaml
from omegaconf import DictConfig
from pydantic import BaseModel, Field, field_validator

from .defaults import DeepchecksConfig, TaskType


# Artifacts models
class ArtifactPath(StrEnum):
    # training artifacts
    TRAINING = "training_artifacts"
    TRAINING_METRICS = "metrics.csv"
    MODEL_CHECKPOINT = "model_checkpoint"
    TRAINING_PARAMS = "params.yaml"
    # deepchecks artifacts
    DEEPCHECKS = "deepchecks"
    # dataset artifacts
    DATASET = "dataset"


## Deepchecks
class DeepchecksResultHeaders(StrEnum):
    # Train-Test Validation
    LabelDrift = "Label Drift"
    ImageDatasetDrift = "Image Dataset Drift"
    ImagePropertyDrift = "Image Property Drift"
    PropertyLabelCorrelationChange = "Property Label Correlation Change"
    HeatmapComparison = "Heatmap Comparison"
    NewLabels = "New Labels"
    # Data Integrity
    ImagePropertyOutliers = "Image Property Outliers"
    PropertyLabelCorrelation = "Property Label Correlation"
    LabelPropertyOutliers = "Label Property Outliers"
    ClassPerformance = "Class Performance"


class DeepchecksConditionResult(BaseModel):
    status: str = Field(description="Status of the condition")
    condition: str = Field(description="Condition of the condition")
    more_info: str = Field(description="More info of the condition")


class DeepchecksCheckResult(BaseModel):
    check: Optional[str] = Field(default=None, description="Name of the check")
    params: Optional[dict] = Field(default=None, description="Parameters of the check")
    summary: Optional[str] = Field(default=None, description="Summary of the check")
    value: Optional[Any] = Field(default=None, description="Value of the check")
    conditions_results: List[DeepchecksConditionResult] = Field(
        default=[], description="Conditions results of the check"
    )
    link_in_summary: Optional[str] = Field(
        default=None, description="Link in summary of the check"
    )
    display_text: Optional[str] = Field(
        default=None, description="Display text of the check"
    )
    display_images: Optional[List[str]] = Field(
        default=None,
        description="Display images of the result as base64 encoded strings",
    )

    @field_validator("value", mode="before")
    @classmethod
    def convert_nan_infinity_to_string(cls, v):
        """Convert NaN and Infinity values to string representations."""
        if v is None:
            return v

        if isinstance(v, float):
            if math.isnan(v):
                return "NaN"
            elif math.isinf(v):
                return "Infinity" if v > 0 else "-Infinity"
        elif isinstance(v, dict):
            return {k: cls.convert_nan_infinity_to_string(val) for k, val in v.items()}
        elif isinstance(v, list):
            return [cls.convert_nan_infinity_to_string(item) for item in v]

        return v

    def to_dict(self, exclude: list[str] = []) -> dict:
        dumped = self.model_dump()
        keys_to_remove = set(exclude + [k for k, v in dumped.items() if v is None])
        for key in keys_to_remove:
            dumped.pop(key)
        return dumped


class DeepchecksParsedResult(BaseModel):
    header: str = Field(description="Header of the result")
    result: DeepchecksCheckResult = Field(description="Result of the check")

    def to_dict(self, exclude_images: bool = False) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        if exclude_images:
            dumped_dict.pop("display_images")
        return dumped_dict

    @classmethod
    def from_dict(
        cls, d: Union[Dict[str, Any], DictConfig]
    ) -> "DeepchecksParsedResult":
        return cls(**d)


class Artifacts(BaseModel):
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

    @classmethod
    def from_file(cls, path: str) -> "Artifacts":
        with open(path, "r", encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return cls.from_dict(d)


class DeepchecksArtifacts(Artifacts):
    dataset_name: str = Field(description="Name of the dataset")
    model_name: Optional[str] = Field(default=None, description="Name of the model")
    results: Dict[str, List[DeepchecksParsedResult]] = Field(
        description="Results of the artifact"
    )
    config: Optional[DeepchecksConfig] = Field(
        default=None, description="Config of the artifact"
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        dumped_dict["results"] = {
            k: [r.to_dict() for r in v] for k, v in self.results.items()
        }
        dumped_dict["config"] = self.config.to_dict() if self.config else None
        return dumped_dict

    @classmethod
    def from_dict(self, d: Union[Dict[str, Any], DictConfig]) -> "DeepchecksArtifacts":
        results = {
            k: [DeepchecksParsedResult.from_dict(r) for r in v]
            for k, v in d["results"].items()
        }
        config = None
        if d.get("config"):
            config = DeepchecksConfig.from_dict(d["config"])
        return DeepchecksArtifacts(
            dataset_name=d["dataset_name"],
            model_name=d.get("model_name"),
            results=results,
            config=config,
        )

    @classmethod
    def from_file(cls, file_path: str) -> "DeepchecksArtifacts":
        with open(file_path, "r", encoding="utf-8") as f:
            d = yaml.safe_load(f)
        artifacts = cls.from_dict(d)
        return artifacts


class ModelCheckpointArtifacts(Artifacts):
    path: Optional[str] = Field(
        default=None, description="Path to the model checkpoint"
    )
    config: Optional[Dict[str, Any]] = Field(
        default=None, description="Config of the model"
    )
    model_type: Optional[str] = Field(
        default=None, description="Type/class name of the model"
    )
    hyperparameters: Optional[Dict[str, Any]] = Field(
        default=None, description="Model hyperparameters"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Context of the model checkpoint"
    )


## Training Artifacts
class TrainingArtifacts(Artifacts):
    model_config = {"arbitrary_types_allowed": True}

    metrics_path: Optional[str] = Field(
        default=None, description="Path to the metrics file"
    )
    metrics_values: Optional[Any] = Field(
        default=None, description="Metrics of the artifact"
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None, description="Parameters of the training routine"
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        if (
            isinstance(self.metrics_values, pd.DataFrame)
            and self.metrics_values is not None
        ):
            dumped_dict["metrics_values"] = self.metrics_values.to_dict(orient="list")
        return dumped_dict

    @classmethod
    def from_dict(cls, d: dict):
        if d.get("metrics_values"):
            metrics_values = pd.DataFrame.from_dict(d.get("metrics_values"))
        elif d.get("metrics_path"):
            metrics_values = pd.read_csv(d.get("metrics_path"))
        else:
            metrics_values = None
        return cls(
            metrics_path=d.get("metrics_path"),
            metrics_values=metrics_values,
            params=d.get("params"),
        )

    @classmethod
    def from_file(cls, metrics_path: str) -> "TrainingArtifacts":
        return cls(metrics_path=metrics_path, metrics_values=pd.read_csv(metrics_path))


class BaseDatasetStatistics(BaseModel):
    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        for k in list(dumped_dict.keys()):
            if dumped_dict[k] is None:
                dumped_dict.pop(k)
        return dumped_dict


class ObjectDetectionStatistics(BaseDatasetStatistics):
    num_negative_samples: int = Field(
        description="Number of negative samples in the dataset"
    )
    num_positive_samples: int = Field(
        description="Number of positive samples in the dataset"
    )
    negative_positive_ratio: float = Field(
        description="Ratio of negative to positive samples"
    )
    num_boxes: int = Field(description="Number of boxes in the dataset")
    boxes_per_image: Optional[Dict[str, Any]] = Field(
        default=None, description="Boxes per image statistics"
    )
    box_width_stats: Optional[Dict[str, Any]] = Field(
        default=None, description="Box width statistics"
    )
    box_height_stats: Optional[Dict[str, Any]] = Field(
        default=None, description="Box height statistics"
    )
    box_area_stats: Optional[Dict[str, Any]] = Field(
        default=None, description="Box area statistics"
    )


class VisionStatistics(BaseDatasetStatistics):
    num_samples: int = Field(description="Number of samples in the dataset")
    image_color_means: Optional[List[float]] = Field(
        default=None, description="Mean of the image color channels"
    )
    image_color_stds: Optional[List[float]] = Field(
        default=None, description="Standard deviation of the image color channels"
    )
    class_distribution: Optional[Dict[str, int]] = Field(
        default=None,
        description="Class distribution of target variable for classification tasks",
    )
    pixel_class_ratio: Optional[Dict[str, float]] = Field(
        default=None, description="Pixel class ratio for semantic segmentation"
    )
    object_detection_statistics: Optional[ObjectDetectionStatistics] = Field(
        default=None, description="Object detection statistics of the dataset"
    )

    other_statistics: Optional[Dict[str, Any]] = Field(
        default=None, description="Other statistics of the dataset"
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        if self.object_detection_statistics is not None:
            dumped_dict["object_detection_statistics"] = (
                self.object_detection_statistics.to_dict()
            )
        for k in list(dumped_dict.keys()):
            if dumped_dict[k] is None:
                dumped_dict.pop(k)
        return dumped_dict


class TabularStatistics(BaseDatasetStatistics):
    # Feature statistics from describe() - nested dict: feature_name -> {stat_name -> value}
    feature_statistics: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Statistical summary for each feature (count, mean, std, min, 25%, 50%, 75%, max)",
    )
    number_unique_values: Optional[Dict[str, int]] = Field(
        default=None, description="Number of unique values per feature"
    )
    percentage_unique_values: Optional[Dict[str, float]] = Field(
        default=None, description="Percentage of unique values per feature"
    )
    categorical_features: Optional[List[str]] = Field(
        default=None, description="List of categorical feature names"
    )
    numerical_features: Optional[List[str]] = Field(
        default=None, description="List of numerical feature names"
    )


class TextStatistics(BaseModel):
    """Statistics about text content."""

    character_length: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Statistical summary of character lengths (count, mean, std, min, 25%, 50%, 75%, max)",
    )
    word_count: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Statistical summary of word counts (count, mean, std, min, 25%, 50%, 75%, max)",
    )
    vocabulary_size: Optional[int] = Field(
        default=None, description="Total number of unique words in the dataset"
    )
    avg_chars_per_word: Optional[float] = Field(
        default=None, description="Average number of characters per word"
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        for k in list(dumped_dict.keys()):
            if dumped_dict[k] is None:
                dumped_dict.pop(k)
        return dumped_dict


class LabelStatistics(BaseModel):
    """Statistics about labels."""

    is_multi_label: Optional[bool] = Field(
        default=None, description="Whether the task is multi-label classification"
    )
    labels_per_sample: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Statistical summary of labels per sample for multi-label tasks (count, mean, std, min, 25%, 50%, 75%, max)",
    )
    class_distribution: Optional[Dict[str, int]] = Field(
        default=None,
        description="Distribution of classes for single-label tasks (class -> count)",
    )
    num_classes: Optional[int] = Field(
        default=None, description="Number of classes in the dataset"
    )
    label_distribution_stats: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Statistical summary of label distribution (count, mean, std, min, 25%, 50%, 75%, max)",
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        for k in list(dumped_dict.keys()):
            if dumped_dict[k] is None:
                dumped_dict.pop(k)
        return dumped_dict


class PropertiesStatistics(BaseModel):
    """Statistics about text properties (similar to TabularStatistics)."""

    feature_statistics: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Statistical summary for each property (count, mean, std, min, 25%, 50%, 75%, max)",
    )
    number_unique_values: Optional[Dict[str, int]] = Field(
        default=None, description="Number of unique values per property"
    )
    percentage_unique_values: Optional[Dict[str, float]] = Field(
        default=None, description="Percentage of unique values per property"
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        for k in list(dumped_dict.keys()):
            if dumped_dict[k] is None:
                dumped_dict.pop(k)
        return dumped_dict


class NLPStatistics(BaseDatasetStatistics):
    num_samples: int = Field(description="Number of samples in the dataset")
    task_type: Optional[str] = Field(
        default=None,
        description="Type of NLP task (e.g., text_classification, text_token_classification)",
    )
    text_statistics: Optional[TextStatistics] = Field(
        default=None, description="Statistics about the text content"
    )
    label_statistics: Optional[LabelStatistics] = Field(
        default=None, description="Statistics about the labels"
    )
    properties_statistics: Optional[PropertiesStatistics] = Field(
        default=None, description="Statistics about text properties"
    )
    categorical_properties: Optional[List[str]] = Field(
        default=None, description="List of categorical property names"
    )
    numerical_properties: Optional[List[str]] = Field(
        default=None, description="List of numerical property names"
    )
    categorical_metadata: Optional[List[str]] = Field(
        default=None, description="List of categorical metadata column names"
    )
    numerical_metadata: Optional[List[str]] = Field(
        default=None, description="List of numerical metadata column names"
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        if self.text_statistics is not None:
            dumped_dict["text_statistics"] = self.text_statistics.to_dict()
        if self.label_statistics is not None:
            dumped_dict["label_statistics"] = self.label_statistics.to_dict()
        if self.properties_statistics is not None:
            dumped_dict["properties_statistics"] = self.properties_statistics.to_dict()
        for k in list(dumped_dict.keys()):
            if dumped_dict[k] is None:
                dumped_dict.pop(k)
        return dumped_dict


## Dataset
class DatasetArtifacts(Artifacts):
    dataset_name: str = Field(..., description="Name of the dataset")
    train_statistics: Union[BaseDatasetStatistics, Dict[str, Any]] = Field(
        ..., description="Train statistics of the dataset"
    )
    task_type: TaskType = Field(..., description="Task type of the dataset")
    test_statistics: Optional[Union[BaseDatasetStatistics, Dict[str, Any]]] = Field(
        default=None, description="Test statistics of the dataset"
    )

    def to_dict(self) -> Dict[str, Any]:
        dumped_dict = self.model_dump()
        dumped_dict["train_statistics"] = self.train_statistics.to_dict()
        if self.test_statistics is not None:
            dumped_dict["test_statistics"] = self.test_statistics.to_dict()
        dumped_dict["task_type"] = self.task_type.value
        return dumped_dict

    @classmethod
    def from_file(cls, path: str) -> "DatasetArtifacts":
        with open(path, "r", encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return cls(**d)
