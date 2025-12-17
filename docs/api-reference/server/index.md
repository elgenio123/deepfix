# Server API Reference

Complete API documentation for the DeepFix Server.

## API Endpoints

### AnalyseArtifactsAPI

::: deepfix_server.api.AnalyseArtifactsAPI

## Coordinators

### ArtifactAnalysisCoordinator

::: deepfix_server.coordinators.ArtifactAnalysisCoordinator

## Configuration

### LLMConfig

::: deepfix_server.config.LLMConfig

## Agents

Agent classes are internal to the server. See [Architecture](../../architecture/agents.md) for details.

## REST API

### POST /v1/analyse

Analyze ML artifacts and return diagnostic results.

**Request Body:**
```json
{
  "dataset_name": "my-dataset",
  "dataset_artifacts": {...},
  "deepchecks_artifacts": {...},
  "model_checkpoint_artifacts": {...},
  "training_artifacts": {...},
  "language": "english"
}
```

**Response:**
```json
{
  "agent_results": {...},
  "summary": "Cross-artifact summary...",
  "additional_outputs": {...},
  "error_messages": {}
}
```

## Examples

See the [Quickstart Guide](../../getting-started/quickstart.md) for usage examples.
