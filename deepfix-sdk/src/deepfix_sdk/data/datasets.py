from torch.utils.data import Dataset
from typing import Optional, Any, Callable, Protocol, Union, List
import pandas as pd
from deepchecks.tabular import Dataset as DeepchecksTabularDataset
from ..utils.logging import get_logger
from ..data.loader import ClassificationVisionDataLoader

logger = get_logger(__name__)


class BaseDataset(Protocol):
    def to_loader(self, model: Optional[Callable] = None, batch_size: int = 8) -> Any:
        raise NotImplementedError("Subclasses must implement this method")


class VisionDataset(BaseDataset):
    def __init__(self, dataset_name: str, dataset: Dataset):
        self.dataset = dataset
        self.dataset_name = dataset_name

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        return self.dataset[idx]

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


class ObjectDetectionDataset(VisionDataset):
    def __init__(self, dataset_name: str, dataset: Dataset):
        super().__init__(dataset_name=dataset_name, dataset=dataset)


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
