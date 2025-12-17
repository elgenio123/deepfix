# Agent System

This document describes the agentic analysis system used by DeepFix, including agent types, execution flow, and coordination mechanisms.

## Overview

DeepFix uses a multi-agent system where specialized agents analyze different aspects of ML artifacts. Agents work in parallel where possible and their results are synthesized by a cross-artifact reasoning agent.

## Agent Architecture

### Agent Hierarchy

```
ArtifactAnalysisCoordinator
    │
    ├─── DatasetArtifactsAnalyzer
    ├─── DeepchecksArtifactsAnalyzer
    ├─── ModelCheckpointArtifactsAnalyzer
    ├─── TrainingArtifactsAnalyzer
    │
    └─── CrossArtifactReasoningAgent (sequential)
```

### Agent Types

#### 1. DatasetArtifactsAnalyzer

**Purpose**: Analyze dataset statistics and properties

**Responsibilities:**
- Examine dataset metadata
- Analyze class balance and distribution
- Detect anomalies in dataset
- Identify data quality issues

**Input**: `DatasetArtifacts`
**Output**: Findings on dataset quality, balance, and anomalies

**Execution**: Parallel with other artifact analyzers

#### 2. DeepchecksArtifactsAnalyzer

**Purpose**: Analyze deepchecks reports for data quality

**Responsibilities:**
- Review data quality check results
- Analyze data drift detection
- Examine integrity check results
- Identify data issues from deepchecks

**Input**: `DeepchecksArtifacts`
**Output**: Findings on data quality, drift, and integrity

**Execution**: Parallel with other artifact analyzers

#### 3. ModelCheckpointArtifactsAnalyzer

**Purpose**: Analyze model checkpoint integrity and readiness

**Responsibilities:**
- Validate checkpoint integrity
- Check configuration consistency
- Assess deployment readiness
- Identify model issues

**Input**: `ModelCheckpointArtifacts`
**Output**: Findings on checkpoint quality and deployment readiness

**Execution**: Parallel with other artifact analyzers

#### 4. TrainingArtifactsAnalyzer

**Purpose**: Analyze training dynamics and metrics

**Responsibilities:**
- Review training metrics and curves
- Analyze training dynamics
- Identify training issues
- Assess model convergence

**Input**: `TrainingArtifacts`
**Output**: Findings on training quality and dynamics

**Execution**: Parallel with other artifact analyzers

**Note**: Currently scaffolded, not fully implemented

#### 5. CrossArtifactReasoningAgent

**Purpose**: Synthesize findings across all agents

**Responsibilities:**
- Combine findings from all agents
- Generate holistic insights
- Create prioritized recommendations
- Generate natural language summary

**Input**: Results from all artifact analyzers
**Output**: Cross-artifact summary and recommendations

**Execution**: Sequential (after all other agents complete)

## Agent Execution Flow

### Parallel Execution

```
┌─────────────────────────────────────┐
│  Parallel Agent Execution           │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ DatasetArtifactsAnalyzer    │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ DeepchecksArtifactsAnalyzer │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ModelCheckpointArtifacts    │   │
│  │        Analyzer             │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ TrainingArtifactsAnalyzer   │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  CrossArtifactReasoningAgent        │
│  (Sequential)                       │
│                                     │
│  - Synthesize findings              │
│  - Generate summary                 │
│  - Create recommendations           │
└─────────────────────────────────────┘
```

### Execution Sequence

1. **Request Decoding**: Convert API request to `AgentContext`
2. **Parallel Agent Execution**: Run all artifact analyzers in parallel
3. **Agent Result Collection**: Collect results from all agents
4. **Cross-Artifact Reasoning**: Synthesize findings sequentially
5. **Response Generation**: Format final response

## Agent Implementation

### Base Agent Class

All agents inherit from a base `Agent` class:

```python
class Agent(dspy.Module):
    """Base agent class for DeepFix analysis agents."""

    def __init__(self, llm_config: LLMConfig):
        self.llm = configure_llm(llm_config)
        # Initialize agent-specific components

    def analyze(self, context: AgentContext) -> AgentResult:
        """Run analysis and return results."""
        # Agent-specific analysis logic
        pass
```

### Agent Context

Agents receive an `AgentContext` containing:

- `dataset_artifacts`: Dataset metadata and statistics
- `deepchecks_artifacts`: Deepchecks reports
- `model_checkpoint_artifacts`: Model checkpoint information
- `training_artifacts`: Training metrics and logs
- `dataset_name`: Name of the dataset
- `language`: Output language

### Agent Result

Agents return an `AgentResult` containing:

- `findings`: List of findings/issues identified
- `confidence`: Confidence score (0.0-1.0)
- `severity`: Severity level (low/medium/high/critical)
- `recommendations`: List of recommended actions
- `metadata`: Additional agent-specific metadata

## Coordination

### ArtifactAnalysisCoordinator

The coordinator orchestrates agent execution:

**Responsibilities:**
- Decode API requests into agent context
- Dispatch artifacts to appropriate agents
- Coordinate parallel agent execution
- Collect and aggregate agent results
- Handle agent errors and timeouts
- Generate final response

**Execution Flow:**

```
1. Receive APIRequest
   ↓
2. Decode to AgentContext
   ↓
3. Start parallel agents
   │
   ├── DatasetArtifactsAnalyzer
   ├── DeepchecksArtifactsAnalyzer
   ├── ModelCheckpointArtifactsAnalyzer
   └── TrainingArtifactsAnalyzer
   ↓
4. Wait for all agents (with timeout)
   ↓
5. Collect results (handle partial failures)
   ↓
6. Run CrossArtifactReasoningAgent
   ↓
7. Generate APIResponse
   ↓
8. Return response
```

### Error Handling

**Agent Timeout:**
- Individual agent timeout: 60s
- Overall timeout: 300s
- Partial results returned if some agents fail

**Agent Failure:**
- Log error but continue with other agents
- Include error message in response
- Provide partial results when possible

**LLM Errors:**
- Retry with exponential backoff
- Fallback to cached knowledge if available
- Return error in agent result

## Knowledge Integration

### KnowledgeBridge

Agents use KnowledgeBridge to query best practices:

**Knowledge Sources:**
- Architecture best practices
- Data quality best practices
- Training best practices
- Research papers and documentation

**Query Process:**
1. Agent formulates query based on context
2. Query sent to KnowledgeBridge
3. KnowledgeBridge retrieves relevant knowledge
4. Knowledge integrated into agent analysis
5. Citations included in results

**Caching:**
- Knowledge queries cached for 24 hours
- Cache key: hash(query + domain + query_type)
- LRU eviction when cache full

## Agent Output

### Individual Agent Results

Each agent produces structured results:

```json
{
  "agent_name": "DatasetArtifactsAnalyzer",
  "findings": [
    {
      "issue": "Class imbalance detected",
      "severity": "high",
      "confidence": 0.95,
      "details": "...",
      "recommendations": [...]
    }
  ],
  "confidence": 0.95,
  "severity": "high"
}
```

### Cross-Artifact Summary

The cross-artifact reasoning agent generates:

- **Summary**: Natural language summary of all findings
- **Prioritized Recommendations**: Ranked list of actions
- **Citations**: References to best practices used
- **Additional Outputs**: Agent-specific insights

## Performance

### Execution Time

- **Typical**: 30-60 seconds for full analysis
- **Fast**: 10-20 seconds with cached knowledge
- **Slow**: Up to 5 minutes for complex analyses

### Optimization

1. **Parallel Execution**: All artifact analyzers run in parallel
2. **Knowledge Caching**: Cache knowledge queries
3. **Timeout Handling**: Individual agent timeouts prevent hanging
4. **Partial Results**: Return partial results on failures

## Future Enhancements

### Planned Features

1. **Streaming Results**: Real-time result streaming
2. **Custom Agents**: User-defined custom agents
3. **Agent Composition**: Chain agents together
4. **Agent Learning**: Agents learn from feedback

### Scalability

1. **Distributed Agents**: Agents on different machines
2. **Agent Pool**: Pool of agents for load balancing
3. **Message Queue**: Use message queue for coordination

## Related Documentation

- [Architecture Overview](overview.md) - High-level system architecture
- [Client-Server Architecture](client-server.md) - Component responsibilities
- [API Reference](../api-reference/index.md) - API documentation
