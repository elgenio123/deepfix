# Architecture Overview

This document provides a high-level overview of the DeepFix architecture, including system components, data flow, and design principles.

## System Overview

DeepFix is a distributed system for AI-powered ML artifact analysis. It follows a client-server architecture that separates artifact computation from intelligent analysis.

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   DeepFix SDK   │────────▶│  DeepFix Server  │────────▶│  LLM Provider   │
│   (Client)      │         │   (Analysis)     │         │   (OpenAI/etc)  │
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                            │
        │                            │
        ▼                            ▼
┌─────────────────┐         ┌──────────────────┐
│     MLflow      │         │  Knowledge Base  │
│ (Artifact Store)│         │   (Best Practices│
└─────────────────┘         └──────────────────┘
```

## Core Components

### 1. DeepFix SDK (Client)

The SDK is responsible for:

- **Artifact Computation**: Generating datasets, running checks, collecting metrics
- **Artifact Recording**: Storing artifacts in MLflow
- **Workflow Integration**: Integrating with PyTorch Lightning, MLflow, etc.
- **Client Communication**: Sending analysis requests to the server

**Location**: `deepfix-sdk/`

### 2. DeepFix Server

The server is responsible for:

- **Artifact Retrieval**: Fetching artifacts from MLflow
- **AI-Powered Analysis**: Running specialized analysis agents
- **Knowledge Retrieval**: Querying best practices knowledge base
- **Result Synthesis**: Combining agent results into actionable insights

**Location**: `deepfix-server/`

### 3. DeepFix Core

Shared models and types:

- **Data Models**: APIRequest, APIResponse, artifact types
- **Type Definitions**: DataType, ArtifactPath, etc.

**Location**: `deepfix-core/`

### 4. Knowledge Base

Stores best practices and domain knowledge:

- **Architecture Best Practices**: Model design patterns
- **Data Quality Best Practices**: Dataset quality standards
- **Training Best Practices**: Training optimization strategies

**Location**: `deepfix-kb/`, `documents/`

## Architecture Principles

### 1. Separation of Concerns

- **Client**: Handles computation and workflow integration
- **Server**: Focuses on AI-powered analysis
- Clear boundaries between components

### 2. Stateless Server

- No session state between requests
- Enables horizontal scaling
- Easier deployment and maintenance

### 3. Artifact Storage

- MLflow as the single source of truth for artifacts
- Server pulls artifacts on-demand
- Client handles artifact generation and storage

### 4. Agentic Analysis

- Specialized agents for different artifact types
- Parallel agent execution where possible
- Cross-artifact reasoning for holistic insights

### 5. Local-First Design

- Designed for local deployment
- Can scale to cloud if needed
- Minimal external dependencies

## Data Flow

### Analysis Request Flow

```
1. Client computes artifacts (datasets, checks, metrics)
   ↓
2. Client stores artifacts in MLflow
   ↓
3. Client sends analysis request to server
   ↓
4. Server retrieves artifacts from MLflow
   ↓
5. Server runs analysis agents in parallel
   ↓
6. Server queries knowledge base
   ↓
7. Server synthesizes results
   ↓
8. Server returns structured response to client
   ↓
9. Client displays results to user
```

### Agent Execution Flow

```
AnalyseArtifactsAPI
    ↓
AgentContext (decode request)
    ↓
ArtifactAnalysisCoordinator
    ↓
┌─────────────────────────────────────┐
│  Parallel Agent Execution           │
│  - DatasetArtifactsAnalyzer         │
│  - DeepchecksArtifactsAnalyzer      │
│  - ModelCheckpointArtifactsAnalyzer │
│  - TrainingArtifactsAnalyzer        │
└─────────────────────────────────────┘
    ↓
CrossArtifactReasoningAgent (sequential)
    ↓
Synthesize results
    ↓
APIResponse
```

## Technology Stack

### Client (SDK)

- **Language**: Python 3.11+
- **Key Libraries**: 
  - `requests` for HTTP communication
  - `mlflow` for artifact tracking
  - `pydantic` for data validation

### Server

- **Language**: Python 3.11+
- **Framework**: FastAPI (via LitServe)
- **Key Libraries**:
  - `dspy` for LLM orchestration
  - `litserve` for API serving
  - `pydantic v2` for validation
  - `llama-index-retrievers-bm25` for knowledge retrieval

### Core

- **Language**: Python 3.11+
- **Key Libraries**:
  - `pydantic` for data models

## Communication Protocol

### REST API

- **Protocol**: HTTP/HTTPS
- **Format**: JSON
- **Endpoints**: 
  - `POST /v1/analyse` - Analyze artifacts

### Request Format

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

### Response Format

```json
{
  "agent_results": {
    "DatasetArtifactsAnalyzer": {...},
    "DeepchecksArtifactsAnalyzer": {...},
    ...
  },
  "summary": "Cross-artifact summary",
  "additional_outputs": {...},
  "error_messages": {...}
}
```

## Deployment Architecture

### Local Deployment

```
┌─────────────────────────────────────┐
│         Local Machine               │
│                                     │
│  ┌──────────┐    ┌──────────────┐  │
│  │  Client  │───▶│    Server    │  │
│  └──────────┘    └──────────────┘  │
│       │                 │           │
│       ▼                 ▼           │
│  ┌──────────┐    ┌──────────────┐  │
│  │  MLflow  │    │ Knowledge KB │  │
│  └──────────┘    └──────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

### Docker Deployment

```
┌─────────────────────────────────────┐
│      Docker Compose                 │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ deepfix-     │  │ mlflow      │ │
│  │ server       │  │ server      │ │
│  │ container    │  │ container   │ │
│  └──────────────┘  └─────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

## Design Decisions

### Why Client-Server?

- **Scalability**: Independent scaling of analysis service
- **Separation**: Clear separation of computation and analysis
- **Flexibility**: Client can work offline with graceful degradation

### Why MLflow for Artifacts?

- **Standardization**: Industry-standard artifact storage
- **Integration**: Works with existing ML workflows
- **Persistence**: Reliable artifact storage and versioning

### Why Stateless Server?

- **Scalability**: Easy horizontal scaling
- **Reliability**: No session state to manage
- **Simplicity**: Easier to deploy and maintain

### Why Agentic Architecture?

- **Specialization**: Each agent focuses on specific artifact type
- **Parallelism**: Agents can run in parallel
- **Extensibility**: Easy to add new agents

## Future Extensions

### Planned Enhancements

1. **Multi-Tenancy**: Support for multiple users/tenants
2. **Authentication**: User authentication and authorization
3. **Result Persistence**: Store analysis history
4. **Streaming Analysis**: Real-time analysis updates
5. **Cloud Deployment**: Support for cloud platforms

### Scalability Path

1. **Current**: Single server, local deployment
2. **Next**: Horizontal scaling with load balancer
3. **Future**: Distributed agents with message queue

## Related Documentation

- [Client-Server Architecture](client-server.md) - Detailed client-server design
- [Agent System](agents.md) - Agent architecture and execution
- [API Reference](../api-reference/index.md) - API documentation
- [Deployment Guide](../deployment/docker.md) - Deployment instructions

