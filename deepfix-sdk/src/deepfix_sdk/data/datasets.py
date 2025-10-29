from torch.utils.data import Dataset
from typing import Optional, Any, Callable, Protocol, Union, List, Dict
import pandas as pd
import numpy as np
import torch
from supervision.dataset.core import DetectionDataset
from supervision.detection.core import Detections
from deepchecks.tabular import Dataset as DeepchecksTabularDataset
from deepchecks.vision import VisionData
from deepchecks.nlp import TextData
from ..utils.logging import get_logger
from ..data.loader import ClassificationVisionDataLoader, DetectionVisionDataLoader, SegmentationVisionDataLoader

logger = get_logger(__name__)


class BaseDataset(Protocol):
    def to_loader(self, model: Optional[Callable] = None, batch_size: int = 8) -> Any:
        raise NotImplementedError("Subclasses must implement this method")


class VisionDataset(BaseDataset):
    def __init__(self, dataset_name: str, dataset: Union[Dataset, DetectionDataset]):
        self.dataset = dataset
        self.dataset_name = dataset_name

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        raise NotImplementedError("should be implemented by subclass")

    def __iter__(self):
        return iter(self.dataset)


class ImageClassificationDataset(VisionDataset):
    def __init__(self, dataset_name: str, dataset: Dataset):
        super().__init__(dataset_name=dataset_name, dataset=dataset)

    def to_loader(
        self, model: Optional[Callable] = None, batch_size: int = 8
    ) -> ClassificationVisionDataLoader:
        return ClassificationVisionDataLoader.load_from_dataset(
            self.dataset,
            batch_size=batch_size,
            model=model,
        )

    def __getitem__(self, idx):
        image, label = self.dataset[idx]
        return dict(image=image, label=label)


class ObjectDetectionDataset(VisionDataset):
    def __init__(self, dataset_name: str, dataset: DetectionDataset):
        super().__init__(dataset_name=dataset_name, dataset=dataset)

    @classmethod
    def from_coco(
        cls,
        dataset_name: str,
        images_directory_path: str,
        annotations_path: str,
        force_masks: bool = False,
    ):
        data = DetectionDataset.from_coco(
            images_directory_path=images_directory_path,
            annotations_path=annotations_path,
            force_masks=force_masks,
        )
        return cls(dataset_name=dataset_name, dataset=data)

    @classmethod
    def from_yolo(
        cls,
        dataset_name: str,
        images_directory_path: str,
        data_yaml_path: str,
        annotations_directory_path: str,
        is_obb: bool = False,
        force_masks: bool = False,
    ):
        data = DetectionDataset.from_yolo(
            images_directory_path=images_directory_path,
            data_yaml_path=data_yaml_path,
            annotations_directory_path=annotations_directory_path,
            is_obb=is_obb,
            force_masks=force_masks,
        )
        return cls(dataset_name=dataset_name, dataset=data)

    def get_label_map(self) -> Dict[int, str]:
        labels = list(range(len(self.dataset.classes)))
        return dict(zip(labels, self.dataset.classes))

    def get_annotations(
        self,
    ) -> Dict[str, Detections]:
        return self.dataset.annotations

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> Dict[str, Union[str, np.ndarray, Detections]]:
        image_path, image, annotation = self.dataset[idx]
        return dict(image_path=image_path, image=image, label=annotation)

    def __iter__(self):
        return iter(self.dataset)

    def to_loader(
        self, batch_size: int = 8, shuffle: bool = False, **kwargs
    ) -> VisionData:
        return DetectionVisionDataLoader.load_from_dataset(
            self.dataset,
            label_map=self.get_label_map(),
            batch_size=batch_size,
            shuffle=shuffle,
        )


class SemanticSegmentationDataset(VisionDataset):

    def __init__(self, dataset_name: str, dataset: Dataset, label_map: Optional[Dict[int, str]] = None):
        assert isinstance(dataset, Dataset), f"dataset must be an instance of Dataset. Received: {type(dataset)}"
        super().__init__(dataset_name=dataset_name, dataset=dataset)
        self.label_map = label_map
        
    
    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx) -> Dict[str, Union[np.ndarray, np.ndarray]]:
        image, annotation = self.dataset[idx]
        c = image.shape[0]        
        if isinstance(image, torch.Tensor):
            image = image.cpu().numpy()
        if isinstance(annotation, torch.Tensor):
            annotation = annotation.cpu().numpy()
        if c in [1, 3]:
            image = image.transpose(1, 2, 0) # (c,h,w) -> (h,w,c)
        return dict(image=image, label=annotation)

    def __iter__(self):
        return iter(self.dataset)

    def get_label_map(self) -> Dict[int, str]:
        if self.label_map is None:
            return {i: f"class_{i}" for i in range(len(self.dataset))}
        self.label_map = self._build_label_map()
        return self.label_map
    
    def _build_label_map(self) -> Dict[int, str]:
        label_map = set()
        for idx in range(self.__len__()):
            label = self.dataset[idx]['label']
            if isinstance(label, torch.Tensor):
                label = label.view(-1)
            elif isinstance(label, np.ndarray):
                label = label.ravel()

            label_map = label_map.union(set(label.flatten()))
        return {i: f"class_{i}" for i in label_map}

    def to_loader(self, model: Optional[Callable] = None, batch_size: int = 8, shuffle: bool = False) -> VisionData:
        if isinstance(self.dataset, VisionData):
            return self.dataset
        else:
            return SegmentationVisionDataLoader.load_from_dataset(
                self.dataset,
                label_map=self.get_label_map(),
                batch_size=batch_size,
                shuffle=shuffle,
            )


class TabularDataset(BaseDataset):
    def __init__(
        self,
        dataset_name: str,
        dataset: Union[pd.DataFrame, DeepchecksTabularDataset],
        label: Optional[str] = None,
        cat_features: List[str] = [],
    ):
        if isinstance(dataset, pd.DataFrame):
            assert label is not None, "Label column is required"
            if len(cat_features) == 0:
                logger.warning(
                    "No categorical features provided, will automatically detect them. (Not Recommended)"
                )
            self.dataset = DeepchecksTabularDataset(
                dataset, label=label, cat_features=cat_features
            )

        elif isinstance(dataset, DeepchecksTabularDataset):
            self.dataset = dataset

        else:
            raise ValueError(f"Invalid dataset type: {type(dataset)}")

        self.dataset_name = dataset_name

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        return self.dataset.iloc[idx]

    def __iter__(self):
        return iter(self.dataset)

    def get_data(self) -> pd.DataFrame:
        return self.dataset.data.copy()

    def get_categorical_features(self) -> List[str]:
        return self.dataset.cat_features

    def get_numerical_features(self) -> List[str]:
        return self.dataset.numerical_features

    def to_loader(self, *args, **kwargs) -> "TabularDataset":
        return self


class NLPDataset(BaseDataset):
    def __init__(self, dataset_name: str, dataset: TextData):
        self.dataset = dataset
        self.dataset_name = dataset_name

    def to_loader(self, *args, **kwargs) -> TextData:
        return self.dataset
    
    def __len__(self):
        return len(self.dataset)