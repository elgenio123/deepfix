"""Round-trip serialization tests for DatasetArtifacts with vision task types."""

import pytest
from deepfix_core.models import (
    ObjectDetectionStatistics,
    TaskType,
    VisionStatistics,
)
from deepfix_core.models.artifacts import DatasetArtifacts


# --- Fixtures ---


def _make_vision_stats(
    with_od: bool = False,
) -> VisionStatistics:
    od = None
    if with_od:
        od = ObjectDetectionStatistics(
            num_negative_samples=2,
            num_positive_samples=8,
            negative_positive_ratio=0.25,
            num_boxes=42,
            boxes_per_image={"mean": 4.2, "std": 1.1, "min": 1, "max": 10},
            box_width_stats={"mean": 50.0, "std": 20.0},
            box_height_stats={"mean": 60.0, "std": 15.0},
            box_area_stats={"mean": 3000.0, "std": 800.0},
        )
    return VisionStatistics(
        num_samples=100,
        image_color_means=[0.485, 0.456, 0.406],
        image_color_stds=[0.229, 0.224, 0.225],
        class_distribution={"0": 40, "1": 60},
        pixel_class_ratio=None,
        object_detection_statistics=od,
    )


def _make_dataset_artifacts(
    task_type: TaskType, with_od: bool = False, with_test: bool = True
) -> DatasetArtifacts:
    return DatasetArtifacts(
        dataset_name="test_dataset",
        train_statistics=_make_vision_stats(with_od=with_od),
        test_statistics=_make_vision_stats(with_od=with_od) if with_test else None,
        task_type=task_type,
    )


# --- Tests ---


@pytest.mark.parametrize(
    "task_type,with_od",
    [
        (TaskType.IMAGE_CLASSIFICATION, False),
        (TaskType.OBJECT_DETECTION, True),
        (TaskType.IMAGE_SEGMENTATION, False),
    ],
)
def test_dataset_artifacts_roundtrip(task_type: TaskType, with_od: bool):
    """to_dict -> from_dict should produce equivalent DatasetArtifacts."""
    original = _make_dataset_artifacts(task_type, with_od=with_od, with_test=True)
    d = original.to_dict()
    restored = DatasetArtifacts.from_dict(d)

    assert restored.dataset_name == original.dataset_name
    assert restored.task_type == original.task_type

    # Train statistics
    assert isinstance(restored.train_statistics, VisionStatistics)
    assert restored.train_statistics.num_samples == 100
    assert (
        restored.train_statistics.image_color_means
        == original.train_statistics.image_color_means
    )
    assert (
        restored.train_statistics.image_color_stds
        == original.train_statistics.image_color_stds
    )
    assert (
        restored.train_statistics.class_distribution
        == original.train_statistics.class_distribution
    )

    # Test statistics
    assert isinstance(restored.test_statistics, VisionStatistics)
    assert restored.test_statistics.num_samples == 100

    if with_od:
        assert restored.train_statistics.object_detection_statistics is not None
        od = restored.train_statistics.object_detection_statistics
        assert od.num_boxes == 42
        assert od.num_positive_samples == 8


@pytest.mark.parametrize(
    "task_type",
    [
        TaskType.IMAGE_CLASSIFICATION,
        TaskType.OBJECT_DETECTION,
        TaskType.IMAGE_SEGMENTATION,
    ],
)
def test_dataset_artifacts_roundtrip_no_test(task_type: TaskType):
    """Round-trip works when test_statistics is None."""
    original = _make_dataset_artifacts(task_type, with_test=False)
    d = original.to_dict()
    restored = DatasetArtifacts.from_dict(d)

    assert restored.test_statistics is None
    assert isinstance(restored.train_statistics, VisionStatistics)


def test_vision_statistics_roundtrip():
    """VisionStatistics to_dict -> from_dict preserves all fields."""
    vs = _make_vision_stats(with_od=True)
    d = vs.to_dict()
    restored = VisionStatistics.from_dict(d)

    assert restored.num_samples == vs.num_samples
    assert restored.image_color_means == vs.image_color_means
    assert restored.image_color_stds == vs.image_color_stds
    assert restored.class_distribution == vs.class_distribution
    assert restored.object_detection_statistics is not None
    assert restored.object_detection_statistics.num_boxes == 42
