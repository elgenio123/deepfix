# Image Classification Guide

This guide covers using DeepFix to diagnose image classification datasets. Learn how to ingest, validate, and analyze image datasets with DeepFix.

## Overview

DeepFix provides specialized support for image classification tasks, including:

- Dataset quality checks
- Class balance analysis
- Image distribution analysis
- Data integrity validation
- Training/test split validation

## Prerequisites

- DeepFix installed and configured (see [Installation Guide](../getting-started/installation.md))
- DeepFix server running
- Image dataset in PyTorch DataLoader format
- Python 3.11 or higher

## Basic Workflow

### Step 1: Prepare Your Dataset

Your image dataset should be in PyTorch DataLoader format:

```python
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Example: Load image dataset
transform = transforms.Compose([
    transforms.Resize((448, 448)),
    transforms.ToTensor()
])

train_dataset = datasets.ImageFolder('data/train', transform=transform)
val_dataset = datasets.ImageFolder('data/val', transform=transform)

train_loader = DataLoader(
    train_dataset,
    batch_size=8,
    shuffle=True,
    num_workers=4,
    pin_memory=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=8,
    shuffle=False,
    num_workers=4,
    pin_memory=True
)
```

### Step 2: Wrap Dataset for DeepFix

```python
from deepfix_sdk.data.datasets import ImageClassificationDataset

dataset_name = "my-image-classification"

# Wrap train and validation datasets
train_wrapped = ImageClassificationDataset(
    dataset_name=dataset_name,
    dataset=train_loader
)

val_wrapped = ImageClassificationDataset(
    dataset_name=dataset_name,
    dataset=val_loader
)
```

### Step 3: Initialize Client

```python
from deepfix_sdk.client import DeepFixClient

client = DeepFixClient(
    api_url="http://localhost:8844",
    timeout=120  # Increase timeout for large image datasets
)
```

### Step 4: Ingest Dataset

```python
client.ingest(
    dataset_name=dataset_name,
    train_data=train_wrapped,
    test_data=val_wrapped,
    train_test_validation=True,  # Validate train/test split
    data_integrity=True,          # Run data integrity checks
    batch_size=8,                 # Batch size for processing
    overwrite=False               # Don't overwrite existing dataset
)
```

### Step 5: Diagnose Dataset

```python
result = client.diagnose_dataset(
    dataset_name=dataset_name,
    language="english"
)

# View results
print(result.to_text())
```

## Complete Example

Here's a complete example using the food waste dataset:

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.zoo.datasets.foodwaste import load_train_and_val_datasets
from deepfix_sdk.data.datasets import ImageClassificationDataset

# Initialize client
client = DeepFixClient(api_url="http://localhost:8844", timeout=120)

# Load image classification dataset
dataset_name = "cafetaria-foodwaste"

train_data, val_data = load_train_and_val_datasets(
    image_size=448,
    batch_size=8,
    num_workers=4,
    pin_memory=False
)

# Wrap datasets
train_dataset = ImageClassificationDataset(
    dataset_name=dataset_name,
    dataset=train_data
)
val_dataset = ImageClassificationDataset(
    dataset_name=dataset_name,
    dataset=val_data
)

# Ingest dataset with quality checks
client.ingest(
    dataset_name=dataset_name,
    train_data=train_dataset,
    test_data=val_dataset,
    train_test_validation=True,
    data_integrity=True,
    batch_size=8,
    overwrite=False
)

# Diagnose dataset
result = client.diagnose_dataset(dataset_name=dataset_name)

# View analysis results
print(result.to_text())
```

## Advanced Usage

### Custom Image Transformations

```python
from torchvision import transforms

# Define custom transformations
custom_transform = transforms.Compose([
    transforms.Resize((448, 448)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

train_dataset = datasets.ImageFolder('data/train', transform=custom_transform)
```

### Large Dataset Handling

For large image datasets, optimize batch processing:

```python
# Use smaller batch size for memory-constrained environments
client.ingest(
    dataset_name="large-image-dataset",
    train_data=train_dataset,
    test_data=val_dataset,
    batch_size=4,  # Reduce batch size
    overwrite=False
)

# Increase timeout for large datasets
client = DeepFixClient(
    api_url="http://localhost:8844",
    timeout=300  # 5 minutes
)
```

### MLflow Integration

Track your image classification analysis in MLflow:

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.config import MLflowConfig

# Configure MLflow
mlflow_config = MLflowConfig(
    tracking_uri="http://localhost:5000",
    experiment_name="image-classification",
    run_name="foodwaste-analysis"
)

client = DeepFixClient(
    api_url="http://localhost:8844",
    mlflow_config=mlflow_config
)

# Ingest and diagnose - results tracked in MLflow
client.ingest(...)
result = client.diagnose_dataset(...)
```

## Understanding Results

The diagnosis results include:

### Dataset Statistics

- Image count and distribution
- Class balance and distribution
- Image size statistics
- Dataset splits (train/val/test)

### Quality Issues

- Class imbalance warnings
- Duplicate image detection
- Corrupted image detection
- Missing labels

### Recommendations

- Suggested preprocessing steps
- Class balancing strategies
- Data augmentation recommendations
- Training/test split suggestions

### Example Result Interpretation

```python
result = client.diagnose_dataset(dataset_name="my-dataset")

# Access agent-specific results
for agent_name, agent_result in result.agent_results.items():
    print(f"\n{agent_name} Findings:")
    print(agent_result.findings)

# Get summary
print(f"\nSummary: {result.summary}")

# Access recommendations
if result.additional_outputs:
    recommendations = result.additional_outputs.get("recommendations", [])
    for rec in recommendations:
        print(f"- {rec}")
```

## Best Practices

### Data Organization

1. **Structured Directory Layout**:
   ```
   data/
   ├── train/
   │   ├── class1/
   │   └── class2/
   └── val/
       ├── class1/
       └── class2/
   ```

2. **Consistent Image Sizes**: Use consistent image sizes for better performance

3. **Balanced Classes**: Ensure relatively balanced class distribution

### Performance Optimization

1. **Batch Size**: Adjust based on available GPU memory
   - GPU with 8GB+: batch_size=16-32
   - GPU with 4GB: batch_size=8-16
   - CPU only: batch_size=4-8

2. **Num Workers**: Set based on CPU cores
   ```python
   num_workers=4  # For 4+ core CPU
   ```

3. **Pin Memory**: Enable for GPU training
   ```python
   pin_memory=True  # If using GPU
   ```

### Validation

1. **Train/Test Split**: Always validate splits
   ```python
   train_test_validation=True
   ```

2. **Data Integrity**: Run integrity checks
   ```python
   data_integrity=True
   ```

3. **Overlap Detection**: Check for train/test overlap
   ```python
   # Handled automatically with train_test_validation=True
   ```

## Troubleshooting

### Common Issues

**Problem**: Memory errors during ingestion

```python
# Solution: Reduce batch size
client.ingest(
    dataset_name="my-dataset",
    train_data=train_dataset,
    batch_size=4  # Reduce from 8
)
```

**Problem**: Slow ingestion

```python
# Solution: Increase num_workers and optimize I/O
train_loader = DataLoader(
    train_dataset,
    batch_size=8,
    num_workers=8,  # Increase workers
    pin_memory=True,  # Enable pin memory
    persistent_workers=True  # Keep workers alive
)
```

**Problem**: Class imbalance warnings

```python
# Solution: Address class imbalance before training
# Use weighted sampling or data augmentation
from torch.utils.data import WeightedRandomSampler

# Calculate class weights
class_weights = compute_class_weights(train_dataset)
sampler = WeightedRandomSampler(
    weights=class_weights,
    num_samples=len(train_dataset)
)
train_loader = DataLoader(train_dataset, sampler=sampler)
```

**Problem**: Corrupted images detected

```python
# Solution: Clean dataset before ingestion
# Use PIL to validate images
from PIL import Image

def is_valid_image(path):
    try:
        Image.open(path).verify()
        return True
    except Exception:
        return False
```

### Performance Tips

1. **Use GPU**: Accelerate processing with GPU support
2. **Parallel Processing**: Increase `num_workers` for faster loading
3. **Caching**: Cache preprocessed data when possible
4. **Lazy Loading**: Load images on-demand for very large datasets

## Next Steps

- [Tabular Data Guide](tabular-data.md) - Work with structured data
- [NLP Datasets Guide](nlp-datasets.md) - Analyze text datasets
- [MLflow Integration](mlflow-integration.md) - Track experiments
- [API Reference](../api-reference/index.md) - Complete API documentation
