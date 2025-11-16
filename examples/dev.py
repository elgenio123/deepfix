import os
from typing import Optional

import fire
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.data.datasets import (
    ImageClassificationDataset,
    NLPDataset,
    ObjectDetectionDataset,
    SemanticSegmentationDataset,
    TabularDataset,
)
from deepfix_sdk.integrations.deepchecks import get_deepchecks_runner
from deepfix_sdk.zoo.datasets import (
    load_segmentation_dataset,
    load_tweet_emotion_classification,
)
from deepfix_sdk.zoo.datasets.foodwaste import load_train_and_val_datasets
from tqdm import tqdm

url = "http://127.0.0.1:8844"
client = DeepFixClient(timeout=60, api_url=url)
os.environ["DEEPFIX_API_KEY"] = "DEEPFIX-IS-AMAZING"


def diagnose(dataset_name: str, model_name: Optional[str] = None):
    # Diagnose dataset
    result = client.diagnose(dataset_name=dataset_name, model_name=model_name)

    # Visualize results
    print(result.to_text(verbose=True))


def load_artifacts(dataset_name: str, model_name: Optional[str] = None):
    from deepfix_sdk.config import ArtifactConfig, MLflowConfig
    from deepfix_sdk.pipelines import ArtifactLoadingPipeline

    artifact_config = ArtifactConfig(
        load_dataset_metadata=True,
        load_checks=True,
        load_model_checkpoint=True,
        load_training=False,
    )
    loaded_artifacts = ArtifactLoadingPipeline(
        mlflow_config=MLflowConfig(),
        artifact_config=artifact_config,
        dataset_name=dataset_name,
        model_name=model_name,
    ).run()

    for key, value in loaded_artifacts.items():
        print(key, type(value))


## Run Deepchecks
def run_deepchecks_image_classification():
    train, test = load_train_and_val_datasets(
        image_size=448, batch_size=8, num_workers=4, pin_memory=False
    )
    dataset_name = "cafetaria-foodwaste-lstroetmann"

    train_data = ImageClassificationDataset(dataset_name=dataset_name, dataset=train)
    test_data = ImageClassificationDataset(dataset_name=dataset_name, dataset=test)
    runner = get_deepchecks_runner(data_type="vision", config=None)
    out = runner.run_suites(
        dataset_name=dataset_name,
        train_data=train_data.to_loader(),
        test_data=test_data.to_loader(),
    )
    print(out)


def run_deepchecks_tabular():
    from sklearn.datasets import load_breast_cancer
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import train_test_split

    X, y = load_breast_cancer(as_frame=True, return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    dataset_name = "breast_cancer_classification"

    label = "target"
    train = X_train.copy()
    train[label] = y_train
    cat_features = X_train.select_dtypes(
        include=["object", "string", "category"]
    ).columns.tolist()

    test = X_test.copy()
    test[label] = y_test

    train_data = TabularDataset(
        dataset=train, dataset_name=dataset_name, label=label, cat_features=cat_features
    )
    val_data = TabularDataset(
        dataset=test, dataset_name=dataset_name, label=label, cat_features=cat_features
    )

    # Fit model
    clf = HistGradientBoostingClassifier(max_depth=3)
    clf = clf.fit(train_data.X, train_data.y)

    runner = get_deepchecks_runner(
        data_type="tabular",
        model_evaluation=True,
        data_integrity=True,
        train_test_validation=True,
    )
    checks_artifact = runner.run_suites(
        dataset_name=dataset_name, model=clf, train_data=train_data, test_data=val_data
    )


def run_deepchecks_object_detection():
    dataset_name = "general_dataset"
    train_data = ObjectDetectionDataset.from_coco(
        dataset_name=dataset_name,
        images_directory_path=r"D:\workspace\general_dataset\coco\train",
        annotations_path=r"D:\workspace\general_dataset\coco\annotations\annotations_train.json",
    )
    val_data = ObjectDetectionDataset.from_coco(
        dataset_name=dataset_name,
        images_directory_path=r"D:\workspace\general_dataset\coco\val",
        annotations_path=r"D:\workspace\general_dataset\coco\annotations\annotations_val.json",
    )
    runner = get_deepchecks_runner(data_type="vision")
    runner.run_suites(
        dataset_name=dataset_name,
        train_data=train_data.to_loader(),
        test_data=val_data.to_loader() if val_data is not None else None,
    )


def run_deepchecks_nlp():
    train_data, test_data = load_tweet_emotion_classification(
        as_train_test=True, include_embeddings=True
    )
    dataset_name = "tweet_emotion_classification"
    runner = get_deepchecks_runner(data_type="nlp", config=None)
    runner.run_suites(
        dataset_name=dataset_name, train_data=train_data, test_data=test_data
    )


def run_deepchecks_semantic_segmentation():
    dataset_name = "coco_segmentation"
    train_data, val_data = load_segmentation_dataset(
        batch_size=8,
        shuffle=False,
        pin_memory=False,
    )
    train_data = SemanticSegmentationDataset(
        dataset_name=dataset_name, dataset=train_data.dataset
    )
    val_data = SemanticSegmentationDataset(
        dataset_name=dataset_name, dataset=val_data.dataset
    )
    runner = get_deepchecks_runner(data_type="vision", config=None)
    runner.run_suites(
        dataset_name=dataset_name,
        train_data=train_data.to_loader(),
        test_data=val_data.to_loader(),
    )


## NLP
def ingest_nlp_dataset():
    train_data, test_data = load_tweet_emotion_classification(
        as_train_test=True, include_embeddings=True
    )
    dataset_name = "tweet_emotion_classification"
    train_data = NLPDataset(dataset_name=dataset_name, dataset=train_data)
    test_data = NLPDataset(dataset_name=dataset_name, dataset=test_data)
    client.ingest(
        dataset_name=dataset_name,
        train_data=train_data,
        test_data=test_data,
        batch_size=8,
        overwrite=True,
    )


## Tabular
def ingest_tabular_dataset():
    from sklearn.datasets import load_breast_cancer
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import train_test_split

    X, y = load_breast_cancer(as_frame=True, return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    dataset_name = "breast_cancer_classification"

    label = "target"
    train = X_train.copy()
    train[label] = y_train
    cat_features = X_train.select_dtypes(
        include=["object", "string", "category"]
    ).columns.tolist()
    if len(cat_features) > 0:
        cat_features = None

    test = X_test.copy()
    test[label] = y_test

    train_data = TabularDataset(
        dataset=train, dataset_name=dataset_name, label=label, cat_features=cat_features
    )
    val_data = TabularDataset(
        dataset=test, dataset_name=dataset_name, label=label, cat_features=cat_features
    )

    # Fit model
    model_name = "HistGradientBoostingClassifier"
    clf = HistGradientBoostingClassifier(max_depth=3)
    clf = clf.fit(train_data.X, train_data.y)

    client.ingest(
        train_data=train_data,
        test_data=val_data,
        model_name=model_name,
        model=clf,
        overwrite=True,
    )


## Image Classification
def ingest_image_classification_dataset():
    dataset_name = "cafetaria-foodwaste"

    train_data, val_data = load_train_and_val_datasets(
        image_size=448,
        batch_size=8,
        num_workers=4,
        pin_memory=False,
    )
    train_data = ImageClassificationDataset(
        dataset_name=dataset_name, dataset=train_data
    )
    val_data = ImageClassificationDataset(dataset_name=dataset_name, dataset=val_data)

    # Ingest dataset
    client.ingest(
        train_data=train_data,
        test_data=val_data,
        batch_size=8,
        overwrite=True,
    )


## Object Detection
def load_object_detection_dataset():
    dataset_name = "savmap"
    train_data = ObjectDetectionDataset.from_coco(
        dataset_name=dataset_name,
        images_directory_path=r"D:\workspace\savmap\coco\images\train",
        annotations_path=r"D:\workspace\savmap\coco\annotations\train.json",
    )
    loader = train_data.to_loader()
    loader.validate()

    for _ in tqdm(loader, desc="Iterating over train data"):
        pass


def ingest_object_detection_dataset():
    dataset_name = "general_dataset"
    train_data = ObjectDetectionDataset.from_coco(
        dataset_name=dataset_name,
        images_directory_path=r"D:\workspace\general_dataset\coco\train",
        annotations_path=r"D:\workspace\general_dataset\coco\annotations\annotations_train.json",
    )
    val_data = ObjectDetectionDataset.from_coco(
        dataset_name=dataset_name,
        images_directory_path=r"D:\workspace\general_dataset\coco\val",
        annotations_path=r"D:\workspace\general_dataset\coco\annotations\annotations_val.json",
    )
    client.ingest(
        dataset_name=dataset_name,
        train_data=train_data,
        test_data=val_data,
        batch_size=8,
        overwrite=True,
    )


## Semantic Segmentation
def load_semantic_segmentation_dataset():
    train_data, val_data = load_segmentation_dataset(
        batch_size=8,
        shuffle=False,
        pin_memory=False,
    )
    dataset_name = "coco_segmentation"
    train_data = SemanticSegmentationDataset(
        dataset_name=dataset_name, dataset=train_data.dataset
    )
    val_data = SemanticSegmentationDataset(
        dataset_name=dataset_name, dataset=val_data.dataset
    )

    for _ in tqdm(train_data, desc="Iterating over train data"):
        pass
    for _ in tqdm(val_data, desc="Iterating over val data"):
        pass


def ingest_semantic_segmentation_dataset():
    dataset_name = "coco_segmentation"
    train_data, val_data = load_segmentation_dataset(
        batch_size=8,
        shuffle=False,
        pin_memory=False,
    )
    train_data = SemanticSegmentationDataset(
        dataset_name=dataset_name, dataset=train_data.dataset
    )
    val_data = SemanticSegmentationDataset(
        dataset_name=dataset_name, dataset=val_data.dataset
    )
    client.ingest(
        train_data=train_data,
        test_data=val_data,
        batch_size=8,
        overwrite=True,
    )


if __name__ == "__main__":
    fire.Fire()
