# Quickstart Guide

Get started with DeepFix in minutes. This guide will walk you through the basic workflow of ingesting a dataset and running diagnostics.

## Prerequisites

- DeepFix installed (see [Installation Guide](installation.md))
- DeepFix server running (see [Server Setup](#server-setup))
- Python 3.11 or higher

## Server Setup

Before using the SDK, start the DeepFix server:

```bash
# Navigate to the server directory
cd deepfix-server

# Create .env file with LLM configuration (if not exists)
# See Configuration Guide for details

# Launch the server
uv run deepfix-server launch -e .env -port 8844 -host 127.0.0.1
```

The server will start and display: `Starting DeepFix server on 127.0.0.1:8844`

## Basic Workflow

The typical DeepFix workflow consists of three steps:

1. **Initialize Client**: Create a client connection to the server
2. **Ingest Dataset**: Upload and validate your dataset
3. **Diagnose**: Run AI-powered analysis and get recommendations

## Example 1: Image Classification Dataset

This example shows how to diagnose an image classification dataset.

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.zoo.datasets.foodwaste import load_train_and_val_datasets
from deepfix_sdk.data.datasets import ImageClassificationDataset

# Step 1: Initialize client
client = DeepFixClient(
    api_url="http://localhost:8844",
    timeout=120  # Increase timeout for large datasets
)

# Step 2: Load and wrap dataset
dataset_name = "cafetaria-foodwaste"

train_data, val_data = load_train_and_val_datasets(
    image_size=448,
    batch_size=8,
    num_workers=4,
    pin_memory=False
)

# Wrap datasets for DeepFix
train_dataset = ImageClassificationDataset(
    dataset_name=dataset_name,
    dataset=train_data
)
val_dataset = ImageClassificationDataset(
    dataset_name=dataset_name,
    dataset=val_data
)

# Step 3: Ingest dataset with quality checks
client.ingest(
    dataset_name=dataset_name,
    train_data=train_dataset,
    test_data=val_dataset,
    train_test_validation=True,
    data_integrity=True,
    batch_size=8,
    overwrite=False
)

# Step 4: Diagnose dataset
result = client.diagnose_dataset(
    dataset_name=dataset_name,
    language="english"
)

# Step 5: View results
print(result.to_text())
```

## Example 2: Tabular Dataset

This example shows how to work with tabular (structured) data.

```python
import pandas as pd
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.data.datasets import TabularDataset

# Step 1: Initialize client
client = DeepFixClient(api_url="http://localhost:8844")

# Step 2: Load tabular data
df_train = pd.read_csv("train_data.csv")
df_test = pd.read_csv("test_data.csv")

# Step 3: Wrap datasets
train_dataset = TabularDataset(
    dataset_name="my-tabular-dataset",
    data=df_train
)
test_dataset = TabularDataset(
    dataset_name="my-tabular-dataset",
    data=df_test
)

# Step 4: Ingest dataset
client.ingest(
    dataset_name="my-tabular-dataset",
    train_data=train_dataset,
    test_data=test_dataset,
    train_test_validation=True,
    data_integrity=True,
    overwrite=False
)

# Step 5: Diagnose
result = client.diagnose_dataset(dataset_name="my-tabular-dataset")
print(result.to_text())
```

## Example 3: NLP Dataset

This example shows how to work with natural language processing datasets.

```python
from datasets import load_dataset
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.data.datasets import NLPDataset

# Step 1: Initialize client
client = DeepFixClient(api_url="http://localhost:8844")

# Step 2: Load NLP dataset
train_data = load_dataset("imdb", split="train")
test_data = load_dataset("imdb", split="test")

# Step 3: Wrap datasets
train_dataset = NLPDataset(
    dataset_name="imdb-sentiment",
    dataset=train_data
)
test_dataset = NLPDataset(
    dataset_name="imdb-sentiment",
    dataset=test_data
)

# Step 4: Ingest and diagnose
client.ingest(
    dataset_name="imdb-sentiment",
    train_data=train_dataset,
    test_data=test_dataset,
    batch_size=16,
    overwrite=False
)

result = client.diagnose_dataset(dataset_name="imdb-sentiment")
print(result.to_text())
```

## Understanding Results

The `diagnose_dataset()` method returns an `APIResponse` object containing:

- **Agent Results**: Detailed findings from each specialized analyzer agent
- **Summary**: Cross-artifact summary synthesizing all insights
- **Recommendations**: Prioritized suggestions for improvement

### Working with Results

```python
# Get formatted text output
result_text = result.to_text()
print(result_text)

# Access agent-specific results
for agent_name, agent_result in result.agent_results.items():
    print(f"\n{agent_name}:")
    print(agent_result.findings)

# Get summary
print(f"\nSummary: {result.summary}")

# Access additional outputs
if result.additional_outputs:
    print(f"\nAdditional outputs: {result.additional_outputs}")
```

## Common Patterns

### Using MLflow Integration

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.config import MLflowConfig

# Configure MLflow
mlflow_config = MLflowConfig(
    tracking_uri="http://localhost:5000",
    experiment_name="my-experiment",
    run_name="run-1"
)

# Initialize client with MLflow
client = DeepFixClient(
    api_url="http://localhost:8844",
    mlflow_config=mlflow_config
)

# Ingest and diagnose - results automatically tracked in MLflow
client.ingest(...)
result = client.diagnose_dataset(...)
```

### Handling Large Datasets

```python
# Increase timeout for large datasets
client = DeepFixClient(
    api_url="http://localhost:8844",
    timeout=300  # 5 minutes
)

# Use smaller batch sizes for memory constraints
client.ingest(
    dataset_name="large-dataset",
    train_data=train_dataset,
    batch_size=4,  # Reduce batch size
    overwrite=False
)
```

### Overwriting Existing Datasets

```python
# Overwrite existing dataset with same name
client.ingest(
    dataset_name="my-dataset",
    train_data=train_dataset,
    overwrite=True  # Allow overwriting
)
```

## Next Steps

- [Image Classification Guide](../guides/image-classification.md) - Deep dive into image classification
- [Tabular Data Guide](../guides/tabular-data.md) - Advanced tabular data workflows
- [NLP Datasets Guide](../guides/nlp-datasets.md) - Working with NLP datasets
- [MLflow Integration](../guides/mlflow-integration.md) - Integrate with MLflow
- [API Reference](../api-reference/index.md) - Complete API documentation
- [Configuration Guide](configuration.md) - Configure DeepFix for your needs

## Troubleshooting

### Connection Errors

**Problem**: Cannot connect to server

```python
# Solution: Verify server is running and URL is correct
client = DeepFixClient(api_url="http://localhost:8844")
# Test connection by checking server status
```

### Timeout Errors

**Problem**: Requests timing out

```python
# Solution: Increase timeout
client = DeepFixClient(
    api_url="http://localhost:8844",
    timeout=120  # Increase timeout
)
```

### Dataset Not Found

**Problem**: Dataset name not found

```python
# Solution: Ensure dataset was ingested first
client.ingest(dataset_name="my-dataset", ...)
# Wait for ingestion to complete before diagnosing
result = client.diagnose_dataset(dataset_name="my-dataset")
```

See the [Troubleshooting section](../guides/image-classification.md#troubleshooting) for more issues and solutions.

