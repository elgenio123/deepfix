import torch
import numpy as np
from typing import Optional, Union, List, Dict, Any, Protocol
from tqdm import tqdm
import pandas as pd
from ..data import BaseDataset, VisionDataset, TabularDataset, ObjectDetectionDataset, ImageClassificationDataset
from deepfix_core.models import DataType


def get_data_statistics(
    data_type: Union[str, DataType],
    train_data: BaseDataset,
    test_data: Optional[BaseDataset] = None,
):
    if data_type == DataType.VISION:
        return VisionDataStatistics(
            train_data=train_data, test_data=test_data
        ).get_statistics()
    elif data_type == DataType.TABULAR:
        return TabularDataStatistics(
            train_data=train_data, test_data=test_data
        ).get_statistics()
    elif data_type == DataType.NLP:
        return NLPDataStatistics(
            train_data=train_data, test_data=test_data
        ).get_statistics()
    else:
        raise ValueError(f"Unsupported data type: {data_type}")


class BaseDataStatistics(Protocol):
    def get_statistics(
        self,
    ) -> Dict[str, Union[int, List[float]]]:
        stats = dict(self.get_train_statistics(), **self.get_test_statistics())
        return stats
    
    def get_train_statistics(self) -> Dict[str, Any]:
        return {}
    
    def get_test_statistics(self) -> Dict[str, Any]:
        return {}

    def _compute_statistics(self, dataset: BaseDataset) -> Dict[str, Any]:
        return {}


class VisionDataStatistics(BaseDataStatistics):
    def __init__(
        self,
        train_data: VisionDataset,
        test_data: Optional[VisionDataset] = None,
    ):
        assert isinstance(train_data, VisionDataset), (
            f"train_data must be an instance of {type(VisionDataset)}, got {type(train_data)}"
        )
        if test_data is not None:
            assert isinstance(test_data, VisionDataset), (
                f"test_data must be an instance of {type(VisionDataset)}, got {type(test_data)}"
            )
        self.train_data = train_data
        self.test_data = test_data        

    def get_statistics(
        self,
    ) -> Dict[str, Union[int, List[float]]]:
        stats = dict(self.get_train_statistics(), **self.get_test_statistics())
        return stats

    def get_train_statistics(
        self,
    ) -> Dict[str, Union[int, List[float]]]:
        num_samples = len(self.train_data)
        train_stats = self._compute_statistics(self.train_data)
        stats = dict(
            num_train_samples=num_samples,
            train_stats = train_stats
        )
        return stats

    def get_test_statistics(
        self,
    ) -> Dict[str, Union[int, List[float]]]:
        num_samples = len(self.test_data)
        test_stats = self._compute_statistics(self.test_data)
        stats = dict(
            num_test_samples=num_samples,
            test_stats=test_stats
        )
        return stats

    def _compute_statistics(self, dataset: VisionDataset) -> Dict[str, Any]:
        stats = self._compute_base_statistics(dataset)
        if isinstance(dataset,ObjectDetectionDataset):
            labels_stats = self._compute_box_statistics(dataset)
            stats.update(labels_stats)

        return stats
    
    def _compute_base_statistics(self,dataset: VisionDataset) -> Dict[str, Any]:
        assert isinstance(dataset, VisionDataset), (
            f"dataset must be an instance of VisionDataset. Received: {type(dataset)}"
        )

        # Initialize accumulators
        num_samples = len(dataset)
        if num_samples == 0:
            return {"mean": None, "std": None}

        # Get first sample to determine number of channels
        first_image = dataset[0]['image']

        H,W,C = first_image.shape  # C dimension
        assert C in [1,3], f"Expected image of shape H*W*1 or H*W*3. But got {H}*{W}*{C}."

        # Initialize accumulators for mean and variance computation (use float64 for stability)
        sum_pixels = torch.zeros(C, dtype=torch.float64)
        sum_squared_pixels = torch.zeros(C, dtype=torch.float64)
        count = 0
        class_counts = {}  # Will store count of each class

        # Compute mean
        for idx in tqdm(range(len(dataset)), desc="Computing dataset base statistics"):
            image = dataset[idx]['image']
            label = dataset[idx]['label']
            assert image.shape[2] == C, f"Expected image of shape H*W*{C}. But got {image.shape[0]}*{image.shape[1]}*{image.shape[2]}."

            if isinstance(dataset,ImageClassificationDataset):
                if isinstance(label,int):
                    pass
                elif isinstance(label,torch.Tensor):
                    label = int(label.cpu().item())
                else:
                    label = int(label)
                class_counts[label] = class_counts.get(label, 0) + 1
            elif isinstance(dataset,ObjectDetectionDataset):
                class_ids = label.class_id
                for class_id in map(int,class_ids):
                    class_counts[class_id] = class_counts.get(class_id, 0) + 1
            else:
                raise ValueError(f"Unsupported dataset type: {type(dataset)}")

            # Ensure image is a tensor and floating type
            if isinstance(image, np.ndarray):
                image = torch.from_numpy(image)
            elif isinstance(image, torch.Tensor):
                pass
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
            # Cast to float32 and normalize if in 0-255 range
            if image.dtype.is_floating_point:
                image = image.to(torch.float32)
            else:
                image = image.to(torch.float32)
                # Heuristic: if values look like 0-255, scale to 0-1
                if torch.max(image) > 1.0 and torch.min(image) >= 0.0:
                    image = image / 255.0

            # Flatten spatial dimensions (H, W) and keep channel dimension
            image_flat = image.reshape(C, -1)  # Shape: (C, H*W)

            # Accumulate sums
            sum_pixels += image_flat.sum(dim=1).to(
                torch.float64
            )  # Sum over spatial dimensions
            count += image_flat.shape[1]  # H*W
            sum_squared_pixels += (image_flat**2).sum(dim=1).to(torch.float64)

        # Compute mean and standard deviation
        mean = sum_pixels / count

        # Compute variance using the formula: Var(X) = E[X^2] - E[X]^2
        variance = (sum_squared_pixels / count) - (mean**2)
        std = torch.sqrt(variance)

        return {"mean": mean.tolist(), "std": std.tolist(),"class_distribution": class_counts}
        
    def _compute_box_statistics(self, dataset: ObjectDetectionDataset) -> Dict[str, Any]:
        """
        Compute statistics on bounding boxes for an object detection dataset.

        Args:
            dataset: ObjectDetectionDataset containing images and annotations

        Returns:
            dict: Dictionary containing various box statistics and negative sample count
        """
        assert isinstance(dataset, ObjectDetectionDataset), (
            f"dataset must be an ObjectDetectionDataset. Received: {type(dataset)}"
        )

        # Initialize accumulators
        num_samples = len(dataset)
        if num_samples == 0:
            return {
                "num_negative_samples": 0,
                "num_boxes": 0,
                "boxes_per_image": {},
                "box_dimensions": {
                    "width": {},
                    "height": {},
                },
                "box_areas": {},
            }

        num_negative_samples = 0
        num_boxes_total = 0
        boxes_per_image_list = []
        box_widths = []
        box_heights = []
        box_areas = []

        # Iterate through dataset
        annotations_dict = dataset.get_annotations()
        for annotation in tqdm(annotations_dict.values(), desc="Computing base box statistics"):
           
            # Check if there are any detections
            num_boxes_in_image = annotation.shape[0]
            
            if num_boxes_in_image == 0:
                num_negative_samples += 1
                boxes_per_image_list.append(0)
                continue

            num_boxes_total += num_boxes_in_image
            boxes_per_image_list.append(num_boxes_in_image)

            # Extract box coordinates and class IDs
            boxes = annotation.xyxy  # Shape: (N, 4) with format [x1, y1, x2, y2]            

            # Compute box dimensions and areas
            width = boxes[:,2] - boxes[:,0] # width
            heights = boxes[:,3] - boxes[:,1] # height
            areas = width * heights
            box_areas.extend(areas)
            box_widths.extend(width)
            box_heights.extend(heights)
            
        # Compute statistics using pandas Series and describe()
        boxes_per_image_stats = {}
        box_width_stats = {}
        box_height_stats = {}
        box_area_stats = {}

        if len(boxes_per_image_list) > 0:
            boxes_per_image_series = pd.Series(boxes_per_image_list)
            boxes_per_image_stats = boxes_per_image_series.describe().to_dict()

        if len(box_widths) > 0:
            box_width_series = pd.Series(box_widths)
            box_width_stats = box_width_series.describe().to_dict()

        if len(box_heights) > 0:
            box_height_series = pd.Series(box_heights)
            box_height_stats = box_height_series.describe().to_dict()

        if len(box_areas) > 0:
            box_area_series = pd.Series(box_areas)
            box_area_stats = box_area_series.describe().to_dict()

        return {
            "num_negative_samples": num_negative_samples,
            "num_boxes": num_boxes_total,
            "boxes_per_image": boxes_per_image_stats,
            "box_stats": {
                "width": box_width_stats,
                "height": box_height_stats,
                "area": box_area_stats
            },
        }
    

class TabularDataStatistics(BaseDataStatistics):
    def __init__(
        self,
        train_data: TabularDataset,
        test_data: Optional[TabularDataset] = None,
    ):
        assert isinstance(train_data, TabularDataset), (
            f"train_data must be an instance of {type(TabularDataset)}, got {type(train_data)}"
        )
        self.train_data = train_data

        if test_data is not None:
            assert isinstance(test_data, TabularDataset), (
                f"test_data must be an instance of {type(TabularDataset)}, got {type(test_data)}"
            )
            self.test_data = test_data
        else:
            self.test_data = None

    def get_statistics(self) -> Dict[str, Any]:
        stats = self.get_train_statistics()
        if self.test_data is not None:
            stats.update(**self.get_test_statistics())
        return stats

    def get_train_statistics(self) -> Dict[str, Any]:
        stats = self._compute_statistics(self.train_data.get_data())
        stats["categorical_features"] = self.train_data.get_categorical_features()
        stats["numerical_features"] = self.train_data.get_numerical_features()
        return {"train_statistics": stats}

    def get_test_statistics(self) -> Dict[str, Any]:
        stats = self._compute_statistics(self.test_data.get_data())
        stats["categorical_features"] = self.test_data.get_categorical_features()
        stats["numerical_features"] = self.test_data.get_numerical_features()
        return {"test_statistics": stats}

    def _compute_statistics(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        stats = dataset.describe().to_dict()
        number_unique_values = dataset.nunique().to_dict()
        stats["number_unique_values"] = number_unique_values
        stats["percentage_unique_values"] = (
            (dataset.nunique() * 100 / len(dataset)).round(2).to_dict()
        )
        return stats


class NLPDataStatistics(BaseDataStatistics):
    def __init__(
        self,
        train_data: BaseDataset,
        test_data: Optional[BaseDataset] = None,
    ):
        self.train_data = train_data
        self.test_data = test_data

    def get_statistics(self) -> Dict[str, Any]:
        pass