# Client-Server Architecture

This document details the client-server architecture of DeepFix, including component responsibilities, communication protocols, and design decisions.

## Overview

DeepFix follows a client-server architecture that separates artifact computation (client) from AI-powered analysis (server). This design enables scalability, flexibility, and maintainability.

## Architecture Decision

**Server State Management: Hybrid (Stateless + In-Memory Cache)**

- Stateless core API for horizontal scalability
- In-memory LRU cache for KnowledgeBridge (upgradeable to Redis)
- MLflow as the persistent artifact store
- Local-first deployment model

**Key Design Choices:**

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Communication | REST API | Simple, HTTP-based, widely supported |
| Artifact Storage | Server pulls from MLflow | Simplifies client, centralizes access control |
| State Management | Stateless + cache | Enables scaling, simpler deployment |
| Deployment | Local-first | Matches current usage, easier migration |

## Server Responsibilities

The DeepFix server is responsible for:

### 1. Artifact Retrieval

- Connect to MLflow tracking server using provided URI
- Fetch artifacts for specified run_id or dataset_name
- Download and cache artifacts locally (temporary storage)
- Handle missing or incomplete artifacts gracefully

**Implementation Notes:**
- Reuse `ArtifactsManager` from `deepfix-core/artifacts/`
- Use MLflow Python client for artifact downloads
- Implement parallel downloads for multiple artifact types
- Store downloaded artifacts in ephemeral temp directory (clean up after analysis)

### 2. AI-Powered Analysis

- Execute multi-agent analysis pipeline
- Coordinate agent execution (parallel where possible)
- Aggregate agent results into unified output
- Generate natural language summaries

**NOT responsible for**: Training models or computing metrics

**Implementation Notes:**
- Reuse agent system from `deepfix-server/agents/`
- Maintain agent execution order:
  - Parallel: TrainingAnalyzer, DatasetAnalyzer, DeepchecksAnalyzer
  - Sequential: CrossArtifactIntegration → OptimizationAdvisor
- Implement timeout handling per agent
- Support partial results when some agents fail

### 3. Knowledge Retrieval

- Query knowledge base using KnowledgeBridge
- Cache knowledge retrieval results
- Validate retrieved knowledge against agent context
- Provide knowledge citations in responses

**NOT responsible for**: Knowledge base updates or curation

**Implementation Notes:**
- Reuse `KnowledgeBridge` from `deepfix-kb/`
- Implement in-memory LRU cache for query results
- Cache key: hash(query + domain + query_type)
- TTL: 24 hours

### 4. Result Formatting

- Transform agent results into API response format
- Generate natural language summaries
- Prioritize findings by severity and confidence
- Format recommendations with actionable steps

**NOT responsible for**: Result persistence or visualization

### 5. Error Handling

- Validate incoming requests against schema
- Handle MLflow connection failures
- Manage agent execution errors
- Provide detailed error messages with recovery suggestions

**NOT responsible for**: Client-side error recovery

## Server Constraints

### Performance Constraints

| Metric | Constraint | Rationale |
|--------|-----------|-----------|
| Response Time | <60s (typical) | User expectation for interactive analysis |
| Timeout | 300s (max) | Hard limit to prevent resource exhaustion |
| Concurrent Requests | 10 simultaneous | Local-first deployment assumption |
| Memory Usage | <4GB per analysis | Supports deployment on standard machines |
| Knowledge Query Time | <2s | Interactive query experience |

### Resource Constraints

- **Cache Size**: Max 1GB or 1000 entries (LRU eviction)
- **Artifact Storage**: Temporary only, cleaned after analysis
- **Database**: No persistent state (optional SQLite for artifact tracking)
- **Network**: Must handle MLflow server on different host

### Operational Constraints

- **Stateless Design**: No session state between requests
- **No User Authentication**: Relies on network security (add later)
- **No Artifact Storage**: Server doesn't persist artifacts beyond analysis
- **Single Tenant**: No multi-tenancy support in v1

### Compatibility Constraints

- **Python Version**: 3.11+
- **MLflow Version**: Compatible with 2.0+
- **Artifact Formats**: Must handle legacy and current formats
- **API Version**: Semantic versioning (v1 = stable)

## Server Boundaries

**What Server DOES:**

- ✅ Fetch artifacts from MLflow
- ✅ Run AI analysis on artifacts
- ✅ Query and cache knowledge
- ✅ Return structured results
- ✅ Health monitoring

**What Server DOES NOT:**

- ❌ Compute or generate artifacts
- ❌ Store artifacts permanently
- ❌ Log to MLflow
- ❌ Train models
- ❌ Manage user sessions
- ❌ Persist analysis history (v1)
- ❌ Update knowledge base (v1)

## Client Responsibilities

The DeepFix SDK (client) is responsible for:

### 1. Artifact Computation

- Generate datasets, deepchecks reports, model checkpoints
- Compute training metrics and logs
- Run data quality checks
- Extract dataset statistics

**Implementation Notes:**
- Use existing data loading and processing pipelines
- Integrate with PyTorch Lightning for training artifacts
- Use Deepchecks for data quality reports
- Generate artifacts in MLflow-compatible formats

### 2. Artifact Recording

- Store artifacts in MLflow tracking server
- Tag artifacts with metadata (dataset_name, model_name, etc.)
- Version artifacts appropriately
- Handle artifact storage failures

**Implementation Notes:**
- Use MLflow Python API for artifact logging
- Implement retry logic for failed uploads
- Support offline mode with local artifact storage
- Clean up temporary artifacts after successful upload

### 3. Workflow Integration

- Integrate with PyTorch Lightning callbacks
- Integrate with MLflow experiments
- Support Jupyter notebooks and scripts
- Provide command-line interface

**Implementation Notes:**
- Create Lightning callback for automatic analysis
- Provide context managers for MLflow integration
- Support both synchronous and asynchronous workflows
- Handle workflow-specific errors gracefully

### 4. Client Communication

- Send analysis requests to DeepFix server
- Handle server responses and errors
- Implement retry logic for transient failures
- Support offline mode with graceful degradation

**Implementation Notes:**
- Use `requests` library for HTTP communication
- Implement exponential backoff retry strategy
- Cache server responses when appropriate
- Provide clear error messages to users

### 5. Result Processing

- Parse server responses
- Format results for display
- Integrate results into workflows
- Store results in MLflow (optional)

**NOT responsible for**: Running AI analysis or querying knowledge base

## Client Boundaries

**What Client DOES:**

- ✅ Compute artifacts (datasets, checks, metrics)
- ✅ Store artifacts in MLflow
- ✅ Send analysis requests
- ✅ Display results to users
- ✅ Integrate with ML workflows

**What Client DOES NOT:**

- ❌ Run AI analysis
- ❌ Query knowledge base directly
- ❌ Manage server state
- ❌ Store analysis results permanently (optional)

## Communication Protocol

### REST API

The client and server communicate via REST API:

**Endpoint**: `POST /v1/analyse`

**Request Format:**
```json
{
  "dataset_name": "my-dataset",
  "model_name": "my-model",
  "dataset_artifacts": {
    "metadata": {...},
    "statistics": {...}
  },
  "deepchecks_artifacts": {
    "reports": [...],
    "checks": [...]
  },
  "model_checkpoint_artifacts": {
    "checkpoint_path": "...",
    "metadata": {...}
  },
  "training_artifacts": {
    "metrics": {...},
    "logs": [...]
  },
  "language": "english"
}
```

**Response Format:**
```json
{
  "agent_results": {
    "DatasetArtifactsAnalyzer": {
      "findings": [...],
      "confidence": 0.95,
      "severity": "high"
    },
    "DeepchecksArtifactsAnalyzer": {...},
    ...
  },
  "summary": "Cross-artifact summary...",
  "additional_outputs": {
    "recommendations": [...],
    "citations": [...]
  },
  "error_messages": {}
}
```

### Error Handling

**Server Errors:**

- `400 Bad Request`: Invalid request format
- `404 Not Found`: Artifacts not found in MLflow
- `500 Internal Server Error`: Server processing error
- `503 Service Unavailable`: Server overloaded or unavailable
- `504 Gateway Timeout`: Request timeout

**Client Errors:**

- Connection errors: Retry with exponential backoff
- Timeout errors: Increase timeout or retry
- Validation errors: Fix request format
- Server errors: Log error and notify user

## Workflow Patterns

### 1. Synchronous Analysis

```
Client → Ingest Artifacts → Request Analysis → Wait for Results → Display
```

**Use Case**: Immediate feedback after training

### 2. Asynchronous Analysis

```
Client → Ingest Artifacts → Request Analysis → Continue Work → Poll for Results
```

**Use Case**: Long-running analysis

### 3. Batch Analysis

```
Client → Ingest Multiple Artifacts → Request Multiple Analyses → Aggregate Results
```

**Use Case**: Analyzing multiple experiments

## Design Rationale

### Why Client-Server?

1. **Separation of Concerns**: Clear separation of computation and analysis
2. **Scalability**: Independent scaling of analysis service
3. **Flexibility**: Client can work offline with graceful degradation
4. **Maintainability**: Easier to update and maintain components

### Why Stateless Server?

1. **Scalability**: Easy horizontal scaling
2. **Reliability**: No session state to manage
3. **Simplicity**: Easier deployment and maintenance
4. **Fault Tolerance**: No state corruption issues

### Why MLflow for Artifacts?

1. **Standardization**: Industry-standard artifact storage
2. **Integration**: Works with existing ML workflows
3. **Persistence**: Reliable artifact storage and versioning
4. **Tooling**: Rich ecosystem of tools

### Why In-Memory Cache?

1. **Performance**: Fast knowledge retrieval
2. **Simplicity**: No external cache dependency
3. **Upgradeable**: Can migrate to Redis if needed
4. **Cost**: No additional infrastructure needed

## Related Documentation

- [Architecture Overview](overview.md) - High-level system architecture
- [Agent System](agents.md) - Agent architecture
- [API Reference](../api-reference/index.md) - API documentation

> **Note:** Workflow and Service specifications are available in the `specs/` directory at the repository root.
