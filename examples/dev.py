import fire
from deepfix_sdk.zoo.datasets import (
    load_adult_classification,
    load_iris_classification,
    load_airbnb_regression,
    load_wine_quality_regression,
    load_avocado_regression,
)
from deepfix_sdk.data.datasets import TabularDataset
from deepfix_sdk.integrations.deepchecks import get_deepchecks_runner
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.zoo.datasets.foodwaste import load_train_and_val_datasets
from deepfix_sdk.data.datasets import ImageClassificationDataset

client = DeepFixClient(timeout=120)


def run_deepchecks_vision():
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


def ingest_tabular_dataset():
    train, test = load_adult_classification(as_train_test=True)
    dataset_name = "adult-classification"

    train_data = TabularDataset(dataset=train, dataset_name=dataset_name)
    test_data = TabularDataset(dataset=test, dataset_name=dataset_name)

    client.ingest_dataset(
        dataset_name=dataset_name,
        train_data=train_data,
        test_data=test_data,
        data_type="tabular",
        overwrite=True,
    )


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


def diagnose_dataset(name: str):
    # Diagnose dataset
    result = client.diagnose_dataset(dataset_name=name)

    # Visualize results
    print(result.to_text())


if __name__ == "__main__":
    fire.Fire()
