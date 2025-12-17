# MLflow Integration Guide

This guide covers integrating DeepFix with MLflow for experiment tracking, artifact storage, and model management.

## Overview

DeepFix integrates seamlessly with MLflow to provide:

- Automatic experiment tracking
- Artifact storage and retrieval
- Run metadata logging
- Model versioning support
- Experiment comparison

## Prerequisites

- DeepFix installed and configured
- MLflow installed (`pip install mlflow`)
- MLflow tracking server running (optional, can use local file storage)
- Python 3.11 or higher

## Basic Setup

### Step 1: Start MLflow Server (Optional)

For centralized tracking, start an MLflow tracking server:

```bash
# Local MLflow server
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000

# Or using Docker
docker run -p 5000:5000 \
    -e MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db \
    -e MLFLOW_DEFAULT_ARTIFACT_ROOT=/mlruns \
    -v $(pwd)/mlruns:/mlruns \
    ghcr.io/mlflow/mlflow:latest \
    mlflow server --host 0.0.0.0 --port 5000
```

### Step 2: Configure MLflow in DeepFix

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.config import MLflowConfig

# Create MLflow configuration
mlflow_config = MLflowConfig(
    tracking_uri="http://localhost:5000",  # MLflow server URI
    experiment_name="deepfix-analysis",    # Experiment name
    run_name="dataset-diagnosis-1"         # Run name
)

# Initialize client with MLflow
client = DeepFixClient(
    api_url="http://localhost:8844",
    mlflow_config=mlflow_config
)
```

### Step 3: Use DeepFix with MLflow

All operations are automatically tracked in MLflow:

```python
from deepfix_sdk.data.datasets import ImageClassificationDataset

# Ingest dataset - tracked in MLflow
client.ingest(
    dataset_name="my-dataset",
    train_data=train_dataset,
    test_data=test_dataset,
    overwrite=False
)

# Diagnose dataset - results tracked in MLflow
result = client.diagnose_dataset(dataset_name="my-dataset")

# Results and artifacts are automatically logged to MLflow
```

## Complete Example

Here's a complete example with MLflow integration:

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.config import MLflowConfig
from deepfix_sdk.zoo.datasets.foodwaste import load_train_and_val_datasets
from deepfix_sdk.data.datasets import ImageClassificationDataset

# Configure MLflow
mlflow_config = MLflowConfig(
    tracking_uri="http://localhost:5000",
    experiment_name="foodwaste-analysis",
    run_name="run-2024-01-15"
)

# Initialize client with MLflow
client = DeepFixClient(
    api_url="http://localhost:8844",
    mlflow_config=mlflow_config,
    timeout=120
)

# Load dataset
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

# Ingest - tracked in MLflow
client.ingest(
    dataset_name=dataset_name,
    train_data=train_dataset,
    test_data=val_dataset,
    train_test_validation=True,
    data_integrity=True,
    batch_size=8,
    overwrite=False
)

# Diagnose - results tracked in MLflow
result = client.diagnose_dataset(dataset_name=dataset_name)

# View results
print(result.to_text())

# All artifacts and metadata are now in MLflow
```

## MLflow Artifact Storage

DeepFix stores various artifacts in MLflow:

### Dataset Metadata

- Dataset statistics
- Class distributions
- Feature information
- Data splits

### Deepchecks Reports

- Data quality checks
- Drift detection results
- Integrity check results
- Visual reports

### Model Checkpoints

- Model state
- Model configuration
- Checkpoint metadata
- Deployment information

### Training Artifacts

- Training metrics
- Training logs
- Hyperparameters
- Validation results

## Accessing MLflow Data

### Using MLflow Python API

```python
import mlflow

# Set tracking URI
mlflow.set_tracking_uri("http://localhost:5000")

# Get experiment
experiment = mlflow.get_experiment_by_name("deepfix-analysis")
experiment_id = experiment.experiment_id

# Get all runs
runs = mlflow.search_runs(experiment_ids=[experiment_id])
print(runs)

# Get specific run
run_id = runs.iloc[0]['run_id']
run = mlflow.get_run(run_id)
print(f"Run ID: {run_id}")
print(f"Status: {run.info.status}")
print(f"Parameters: {run.data.params}")
print(f"Metrics: {run.data.metrics}")

# List artifacts
artifacts = mlflow.list_artifacts(run_id)
for artifact in artifacts:
    print(f"  - {artifact.path}")

# Download artifact
mlflow.artifacts.download_artifacts(
    run_id=run_id,
    artifact_path="dataset_metadata"
)
```

### Using MLflow UI

1. Start MLflow UI:
   ```bash
   mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
   ```

2. Open browser to `http://localhost:5000`

3. Navigate to experiments and runs

4. View metrics, parameters, and artifacts

## Advanced Usage

### Custom MLflow Logging

Log additional information to MLflow:

```python
import mlflow

# Set experiment context
mlflow.set_experiment("deepfix-analysis")

with mlflow.start_run(run_name="custom-run"):
    # Log parameters
    mlflow.log_param("dataset_name", "my-dataset")
    mlflow.log_param("batch_size", 8)

    # Use DeepFix
    client = DeepFixClient(...)
    result = client.diagnose_dataset(...)

    # Log metrics
    mlflow.log_metric("num_issues", len(result.agent_results))
    mlflow.log_metric("severity_score", calculate_severity(result))

    # Log artifacts
    with open("diagnosis_report.txt", "w") as f:
        f.write(result.to_text())
    mlflow.log_artifact("diagnosis_report.txt")

    # Log tags
    mlflow.set_tag("dataset_type", "image")
    mlflow.set_tag("analysis_version", "1.0")
```

### Multiple Experiments

Organize analyses into multiple experiments:

```python
from deepfix_sdk.config import MLflowConfig

# Experiment 1: Image classification
image_config = MLflowConfig(
    tracking_uri="http://localhost:5000",
    experiment_name="image-classification",
    run_name="run-1"
)

# Experiment 2: Tabular analysis
tabular_config = MLflowConfig(
    tracking_uri="http://localhost:5000",
    experiment_name="tabular-analysis",
    run_name="run-1"
)

# Use different configs for different analyses
image_client = DeepFixClient(api_url="...", mlflow_config=image_config)
tabular_client = DeepFixClient(api_url="...", mlflow_config=tabular_config)
```

### MLflow Model Registry

Register models in MLflow Model Registry:

```python
import mlflow

# After diagnosis, if you train a model
# ... training code ...

# Log model
mlflow.sklearn.log_model(model, "model")

# Register model
model_version = mlflow.register_model(
    model_uri=f"runs:/{run_id}/model",
    name="my-model"
)

# Promote to staging
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="my-model",
    version=model_version.version,
    stage="Staging"
)
```

## Configuration Options

### Local File Storage

Use local file storage instead of server:

```python
mlflow_config = MLflowConfig(
    tracking_uri="file:./mlruns",  # Local file path
    experiment_name="local-experiment",
    run_name="run-1"
)
```

### Remote MLflow Server

Connect to remote MLflow server:

```python
mlflow_config = MLflowConfig(
    tracking_uri="https://mlflow.example.com",  # Remote server
    experiment_name="remote-experiment",
    run_name="run-1"
)
```

### Databricks MLflow

Connect to Databricks MLflow:

```python
mlflow_config = MLflowConfig(
    tracking_uri="databricks",  # Use Databricks
    experiment_name="/Shared/deepfix-analysis",
    run_name="run-1"
)
```

## Best Practices

### Experiment Organization

1. **Use Descriptive Names**: Use clear experiment and run names
   ```python
   experiment_name="foodwaste-classification-2024"
   run_name="baseline-model-v1"
   ```

2. **Tag Runs**: Add tags for filtering
   ```python
   mlflow.set_tag("dataset", "foodwaste")
   mlflow.set_tag("model_type", "resnet50")
   ```

3. **Version Control**: Track code versions
   ```python
   mlflow.log_param("git_commit", get_git_commit())
   ```

### Artifact Management

1. **Store Only Necessary Artifacts**: Don't log everything
2. **Use Relative Paths**: Use consistent artifact paths
3. **Clean Up Old Runs**: Archive or delete old experiments

### Performance

1. **Async Logging**: Use async logging for high-throughput scenarios
2. **Batch Logging**: Batch multiple log operations
3. **Artifact Compression**: Compress large artifacts before logging

## Troubleshooting

### Common Issues

**Problem**: Cannot connect to MLflow server

```python
# Solution: Verify server is running and URI is correct
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")
try:
    mlflow.list_experiments()  # Should not raise error
except Exception as e:
    print(f"Connection error: {e}")
```

**Problem**: Artifacts not appearing

```python
# Solution: Verify artifact root is accessible
mlflow_config = MLflowConfig(
    tracking_uri="http://localhost:5000",
    experiment_name="test",
    run_name="test-run"
)
# Check artifact root permissions and path
```

**Problem**: Large artifacts causing performance issues

```python
# Solution: Use artifact compression or external storage
import mlflow
mlflow.log_artifact("large_file.csv", artifact_path="compressed")
# Or use external storage and log URI
mlflow.log_param("data_uri", "s3://bucket/data.csv")
```

## Next Steps

- [Quickstart Guide](../getting-started/quickstart.md) - Basic DeepFix usage
- [Configuration Guide](../getting-started/configuration.md) - Configure DeepFix
- [API Reference](../api-reference/index.md) - Complete API documentation
