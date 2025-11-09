import fire
from tqdm import tqdm
from deepfix_sdk.zoo.datasets import (
    load_adult_classification,
    load_tweet_emotion_classification,
    load_segmentation_dataset
)
from deepfix_sdk.data.datasets import TabularDataset, NLPDataset
from deepfix_sdk.integrations.deepchecks import get_deepchecks_runner
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.zoo.datasets.foodwaste import load_train_and_val_datasets
from deepfix_sdk.data.datasets import ImageClassificationDataset, ObjectDetectionDataset, SemanticSegmentationDataset

url = "http://deepfix.delcaux.com"
client = DeepFixClient(timeout=60,api_url=url)

def diagnose_dataset(name: str):
    # Diagnose dataset
    result = client.diagnose_dataset(dataset_name=name)

    # Visualize results
    print(result.to_text())

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
    train, test = load_adult_classification(as_train_test=True)
    dataset_name = "adult-classification"

    runner = get_deepchecks_runner(data_type="tabular", config=None)

    train_data = TabularDataset(dataset=train, dataset_name=dataset_name)
    test_data = TabularDataset(dataset=test, dataset_name=dataset_name)
    runner.run_suites(
        dataset_name=dataset_name, train_data=train_data, test_data=test_data
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
    runner = get_deepchecks_runner(data_type="vision", config=None)
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
    train_data = SemanticSegmentationDataset(dataset_name=dataset_name, dataset=train_data.dataset)
    val_data = SemanticSegmentationDataset(dataset_name=dataset_name, dataset=val_data.dataset)
    runner = get_deepchecks_runner(data_type="vision", config=None)
    runner.run_suites(
        dataset_name=dataset_name, train_data=train_data.to_loader(), test_data=val_data.to_loader()
    )


## NLP
def ingest_nlp_dataset():
    train_data, test_data = load_tweet_emotion_classification(
        as_train_test=True, include_embeddings=True
    )
    dataset_name = "tweet_emotion_classification"
    train_data = NLPDataset(dataset_name=dataset_name, dataset=train_data)
    test_data = NLPDataset(dataset_name=dataset_name, dataset=test_data)
    client.ingest_dataset(
        dataset_name=dataset_name,
        data_type="nlp",
        train_data=train_data,
        test_data=test_data,
        train_test_validation=True,
        data_integrity=True,
        batch_size=8,
        overwrite=True,
    )

## Tabular
def ingest_tabular_dataset():
    train, test = load_adult_classification(as_train_test=True)
    dataset_name = "adult-classification"

    label = "income"
    cat_features = train.select_dtypes(include=['object','string','category']).columns.tolist()
    cat_features.remove(label)

    train_data = TabularDataset(dataset=train, dataset_name=dataset_name, label=label, cat_features=cat_features)
    test_data = TabularDataset(dataset=test, dataset_name=dataset_name, label=label, cat_features=cat_features)

    client.ingest_dataset(
        dataset_name=dataset_name,
        train_data=train_data,
        test_data=test_data,
        data_type="tabular",
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
    client.ingest_dataset(
        dataset_name=dataset_name,
        data_type="vision",
        train_data=train_data,
        test_data=val_data,
        train_test_validation=True,
        data_integrity=True,
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
    client.ingest_dataset(
        dataset_name=dataset_name,
        data_type="vision",
        train_data=train_data,
        test_data=val_data,
        train_test_validation=val_data is not None,
        data_integrity=True,
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
    train_data = SemanticSegmentationDataset(dataset_name=dataset_name, dataset=train_data.dataset)
    val_data = SemanticSegmentationDataset(dataset_name=dataset_name, dataset=val_data.dataset)

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
    train_data = SemanticSegmentationDataset(dataset_name=dataset_name, dataset=train_data.dataset)
    val_data = SemanticSegmentationDataset(dataset_name=dataset_name, dataset=val_data.dataset)
    client.ingest_dataset(
        dataset_name=dataset_name,
        data_type="vision",
        train_data=train_data,
        test_data=val_data,
        train_test_validation=True,
        data_integrity=True,
        batch_size=8,
        overwrite=True,
    )


if __name__ == "__main__":
    fire.Fire()
