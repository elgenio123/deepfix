from regex.regex import D
from torch.utils.data import Dataset
from typing import Optional, Any, Callable, Protocol, Union, List, Tuple, Dict
import pandas as pd
import numpy as np
from supervision.dataset.core import DetectionDataset
from supervision.detection.core import Detections
from deepchecks.tabular import Dataset as DeepchecksTabularDataset
from deepchecks.vision import VisionData
from ..utils.logging import get_logger
from ..data.loader import ClassificationVisionDataLoader, DetectionVisionDataLoader

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
        return dict(image=image,label=label)


class ObjectDetectionDataset(VisionDataset):
    def __init__(self, dataset_name: str, dataset: DetectionDataset):
        super().__init__(dataset_name=dataset_name, dataset=dataset)
    
    @classmethod
    def from_coco(cls,dataset_name: str, images_directory_path: str, annotations_path: str,force_masks:bool=False):
        data = DetectionDataset.from_coco(images_directory_path=images_directory_path, 
                                          annotations_path=annotations_path,
                                          force_masks=force_masks)
        return cls(dataset_name=dataset_name, dataset=data)
    
    @classmethod
    def from_yolo(cls,dataset_name: str, images_directory_path: str, data_yaml_path: str, annotations_directory_path: str,is_obb:bool=False,force_masks:bool=False):
        data = DetectionDataset.from_yolo(images_directory_path=images_directory_path, 
                                          data_yaml_path=data_yaml_path,
                                          annotations_directory_path=annotations_directory_path,
                                          is_obb=is_obb,
                                          force_masks=force_masks,
                                          )
        return cls(dataset_name=dataset_name, dataset=data)
    
    def get_label_map(self) -> Dict[int, str]:
        labels = list(range(len(self.dataset.classes)))
        return dict(zip(labels, self.dataset.classes))
    
    def get_annotations(self,)->Dict[str, Detections]:
        return self.dataset.annotations
    
    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx)->Dict[str, Union[str,np.ndarray, Detections]]:
        image_path, image, annotation =  self.dataset[idx]
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
