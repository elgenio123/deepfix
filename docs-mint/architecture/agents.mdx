---
title: "Agent System"
description: "How DeepFix’s multi-agent analysis system works, including agent types and execution flow."
---

DeepFix uses a multi-agent system where specialized agents analyze different aspects of ML artifacts. Agents run in parallel where possible and their results are synthesized by a cross-artifact reasoning agent.

## Agent Architecture

### Agent Hierarchy

```text
ArtifactAnalysisCoordinator
    │
    ├── DatasetArtifactsAnalyzer
    ├── DeepchecksArtifactsAnalyzer
    ├── ModelCheckpointArtifactsAnalyzer
    ├── TrainingArtifactsAnalyzer
    │
    └── CrossArtifactReasoningAgent (sequential)
```

## Agent Types

### DatasetArtifactsAnalyzer

**Purpose**: Analyze dataset statistics and properties.

Responsibilities:

- Examine dataset metadata.
- Analyze class balance and distributions.
- Detect dataset anomalies.
- Identify data quality issues.

Input: `DatasetArtifacts`\
Output: findings on dataset quality, balance, and anomalies.\
Execution: in parallel with other artifact analyzers.

### DeepchecksArtifactsAnalyzer

**Purpose**: Analyze Deepchecks reports for data quality.

Responsibilities:

- Review Deepchecks data quality checks.
- Analyze drift detection results.
- Examine integrity checks.
- Highlight critical data issues.

Input: `DeepchecksArtifacts`\
Output: findings on data quality, drift, and integrity.\
Execution: in parallel with other artifact analyzers.

### ModelCheckpointArtifactsAnalyzer

**Purpose**: Analyze model checkpoint integrity and readiness.

Responsibilities:

- Validate checkpoint integrity.
- Check configuration consistency.
- Assess deployment readiness.
- Identify model-related issues.

Input: `ModelCheckpointArtifacts`\
Output: findings on checkpoint quality and deployment readiness.\
Execution: in parallel with other artifact analyzers.

### TrainingArtifactsAnalyzer

**Purpose**: Analyze training dynamics and metrics.

Responsibilities:

- Review training curves and metrics.
- Analyze training dynamics.
- Identify training issues and instabilities.
- Assess model convergence.

Input: `TrainingArtifacts`\
Output: findings on training quality and dynamics.\
Execution: in parallel with other artifact analyzers.

### CrossArtifactReasoningAgent

**Purpose**: Synthesize findings across all artifact analyzers.

Responsibilities:

- Combine findings from all agents.
- Generate holistic insights.
- Create prioritized recommendations.
- Produce a natural-language summary.

Input: results from all artifact analyzers.\
Output: cross-artifact summary, recommendations, and citations.\
Execution: runs **after** the parallel agents complete.

## Agent Execution Flow

### Parallel Execution

```text
┌─────────────────────────────────────┐
│  Parallel Agent Execution           │
│                                     │
│  DatasetArtifactsAnalyzer           │
│  DeepchecksArtifactsAnalyzer        │
│  ModelCheckpointArtifactsAnalyzer   │
│  TrainingArtifactsAnalyzer          │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  CrossArtifactReasoningAgent        │
│  (Sequential)                       │
└─────────────────────────────────────┘
```

### Execution Sequence

1. Decode `APIRequest` into an `AgentContext`.
2. Run all artifact analyzers in parallel.
3. Collect results (with timeouts and partial failures).
4. Run `CrossArtifactReasoningAgent`.
5. Build final `APIResponse`.

## Implementation Sketch

### Base Agent

Each agent is implemented as a module using the configured LLM and knowledge bridge.

```python
class Agent(dspy.Module):
    """Base agent for DeepFix analysis."""

    def __init__(self, llm_config: LLMConfig):
        self.llm = configure_llm(llm_config)

    def analyze(self, context: AgentContext) -> AgentResult:
        # Agent-specific analysis logic
        raise NotImplementedError
```

### Agent Context

Each agent receives an `AgentContext` containing:

- Dataset artifacts.
- Deepchecks artifacts.
- Model checkpoint artifacts.
- Training artifacts.
- Dataset name and language.

Agents focus only on the subset they need.

### Agent Result

Agents return an `AgentResult` with:

- Findings (issues, observations).
- Severity and confidence.
- Recommendations.
- Optional metadata.

## Coordination

### ArtifactAnalysisCoordinator

The coordinator orchestrates agent execution:

Responsibilities:

- Decode API requests into an agent context.
- Dispatch artifacts to appropriate agents.
- Run analyzers in parallel with timeouts.
- Handle agent errors and partial failures.
- Run cross-artifact reasoning.
- Produce the final API response.

## Knowledge Integration

### KnowledgeBridge

Agents use the knowledge bridge to query best practices and prior knowledge.

Knowledge sources:

- Architecture and training best practices.
- Data quality and drift playbooks.
- Internal notes and examples.

Caching:

- Queries cached with LRU.
- Cache key: hash of `(query, domain, type)`.
- TTL on entries (e.g. 24h).

## Performance & Reliability

- Typical analysis: 30–60 seconds.
- Knowledge cache improves latency.
- Per-agent timeouts avoid hangs.
- Partial results returned when some agents fail.

## Extending the Agent System

To add a new agent:

1. Implement a new `Agent` subclass.
2. Register it in the coordinator.
3. Wire any new artifacts or knowledge sources.
4. Add tests and documentation.

## Related Documentation

- [Architecture Overview](/architecture/overview)
- [Client–Server Architecture](/architecture/client-server)
- [Server API Reference](/api-reference/server)
