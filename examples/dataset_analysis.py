from deepfix.client import DeepFixClient
from deepfix.client.zoo.datasets.foodwaste import load_train_and_val_datasets
from deepfix.client.data.datasets import ImageClassificationDataset

# Load image datasets

dataset_name="cafetaria-foodwaste-lstroetmann"

client = DeepFixClient(timeout=120)

"""
train_data, val_data = load_train_and_val_datasets(
    image_size=448,
    batch_size=8,
    num_workers=4,
    pin_memory=False,)

train_data = ImageClassificationDataset(dataset_name=dataset_name, dataset=train_data)
val_data = ImageClassificationDataset(dataset_name=dataset_name, dataset=val_data)

client.ingest_dataset(dataset_name=dataset_name,
                    train_data=train_data,
                    test_data=val_data,
                    train_test_validation=True,
                    data_integrity=True,
                    batch_size=8,
                    overwrite=True
                    )
"""

result = client.diagnose_dataset(dataset_name=dataset_name)

print(result.to_text())