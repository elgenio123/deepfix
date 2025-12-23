"""
Zoo datasets module.

Provides utilities for loading various datasets including custom food datasets
and pre-built datasets from the DeepChecks library.
"""

# DeepChecks Vision Dataset Loaders
# DeepChecks NLP Dataset Loaders
from .deepchecks_nlp import (
    load_just_dance_comment_classification,
    load_scierc_ner,
    load_tweet_emotion_classification,
)

# DeepChecks Tabular Dataset Loaders
from .deepchecks_tabular import (
    load_adult_classification,
    load_airbnb_regression,
    load_avocado_regression,
    load_iris_classification,
    load_wine_quality_regression,
)
from .deepchecks_vision import (
    load_coco_detection,
    load_mask_detection,
    load_mnist_classification,
    load_segmentation_dataset,
)

# Dataset Registry
from .registry import (
    DatasetMetadata,
    DatasetRegistry,
    DatasetType,
    get_registry,
)

__all__ = [
    # Vision datasets
    "load_mnist_classification",
    "load_coco_detection",
    "load_mask_detection",
    "load_segmentation_dataset",
    # Tabular datasets
    "load_adult_classification",
    "load_iris_classification",
    "load_airbnb_regression",
    "load_wine_quality_regression",
    "load_avocado_regression",
    # NLP datasets
    "load_tweet_emotion_classification",
    "load_just_dance_comment_classification",
    "load_scierc_ner",
    # Registry
    "DatasetRegistry",
    "DatasetType",
    "DatasetMetadata",
    "get_registry",
]
