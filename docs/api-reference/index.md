# API Reference

Complete API documentation for DeepFix SDK, Server, and Core components.

## Overview

The DeepFix API is organized into three main components:

1. **SDK API**: Client library for interacting with DeepFix server
2. **Server API**: REST API endpoints for analysis
3. **Core API**: Shared data models and types

## API Components

### SDK API

The DeepFix SDK provides a Python client for interacting with the DeepFix server.

**Main Components:**
- `DeepFixClient`: Main client class for analysis requests
- `MLflowConfig`: Configuration for MLflow integration
- `ArtifactConfig`: Configuration for artifact loading
- Dataset classes: `ImageClassificationDataset`, `TabularDataset`, `NLPDataset`

**Location**: `deepfix-sdk/src/deepfix_sdk/`

[SDK Reference →](sdk/index.md)

### Server API

The DeepFix Server provides REST API endpoints for artifact analysis.

**Main Components:**
- `AnalyseArtifactsAPI`: Main API endpoint for analysis
- `ArtifactAnalysisCoordinator`: Coordinates agent execution
- Agent classes: Specialized analyzers for different artifact types

**Location**: `deepfix-server/src/deepfix_server/`

[Server Reference →](server/index.md)

### Core API

DeepFix Core provides shared data models and types used across components.

**Main Components:**
- `APIRequest`: Request model for analysis
- `APIResponse`: Response model for analysis results
- `AgentResult`: Agent analysis results
- Artifact models: Dataset, Deepchecks, Model Checkpoint, Training

**Location**: `deepfix-core/src/deepfix_core/`

[Core Reference →](core/index.md)

## Quick Links

- [SDK: DeepFixClient](sdk/index.md#deepfixclient) - Main client class
- [SDK: Configuration](sdk/index.md#configuration) - Configuration classes
- [SDK: Datasets](sdk/index.md#datasets) - Dataset wrapper classes
- [Server: API Endpoints](server/index.md#api-endpoints) - REST API
- [Server: Coordinators](server/index.md#coordinators) - Analysis coordination
- [Core: Models](core/index.md#models) - Data models
- [Core: Types](core/index.md#types) - Type definitions

## Usage Examples

### SDK Usage

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.config import MLflowConfig

# Initialize client
client = DeepFixClient(api_url="http://localhost:8844")

# Diagnose dataset
result = client.diagnose_dataset(dataset_name="my-dataset")
print(result.to_text())
```

### Server Usage

```python
# Server runs via CLI
uv run deepfix-server launch -e .env -port 8844
```

### Core Models

```python
from deepfix_core.models import APIRequest, APIResponse

# Create request
request = APIRequest(
    dataset_name="my-dataset",
    dataset_artifacts={...},
    language="english"
)

# Process response
response: APIResponse = analyze(request)
print(response.summary)
```

## Related Documentation

- [Quickstart Guide](../getting-started/quickstart.md) - Get started with DeepFix
- [Architecture](../architecture/overview.md) - System architecture
- [Guides](../guides/image-classification.md) - Usage guides

