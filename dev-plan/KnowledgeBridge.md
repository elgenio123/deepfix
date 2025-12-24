# KnowledgeBridge: Knowledge Retrieval System Design

## Overview

**KnowledgeBridge** is the knowledge retrieval backbone for the DeepFix multi-agent system. It provides grounded, up-to-date information to support agent responses by combining:

1. **Web Search**: Real-time information retrieval via Tavily Search API
2. **AI-Powered Research**: Deep reasoning and synthesis via Perplexity Sonar through OpenRouter, using DSPy Modules for composable research signatures
3. **Local Knowledge Base**: Domain-specific ML/DL knowledge via the existing LlamaIndex-based system

The system is designed as a **modular tool** that can be consumed by any agent in the DeepFix ecosystem.

---

## Architecture

### System Context

```
                           Raw Artifacts
                                ↓
┌───────────────────────────────────────────────────────────────────────┐
│                      DeepFix Agent System                             │
├───────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┬──────────────────────┐                       │
│  │ ArtifactAnalysis    │  TrainingDynamics    │  (Parallel execution) │
│  │    Coordinator      │       Agent          │                       │
│  └─────────┬───────────┴──────────┬───────────┘                       │
│            │                      │                                   │
│            └──────────┬───────────┘                                   │
│                       ↓                                               │
│         ┌──────────────────────────────┐                              │
│         │  CrossArtifactReasoningAgent │   (Sequential execution)     │
│         └──────────────┬───────────────┘                              │
│                        ↓                                              │
│         ┌──────────────────────────────┐     ┌─────────────────────┐  │
│         │   OptimizationAdvisorAgent   │◄────│   KnowledgeBridge   │  │
│         │  (Uses integration insights) │     │  (Retrieval Tool)   │  │
│         └──────────────────────────────┘     └──────────┬──────────┘  │
└─────────────────────────────────────────────────────────┼─────────────┘
                                                          │
                      ┌───────────────────────────────────┼───────────────────┐
                      │                                   │                   │
                      ▼                                   ▼                   ▼
              ┌───────────────┐                  ┌────────────────┐  ┌──────────────────┐
              │  Tavily API   │                  │  OpenRouter    │  │  Local KB        │
              │  (Web Search) │                  │  (Perplexity   │  │  (LlamaIndex)    │
              │               │                  │   Sonar)       │  │                  │
              └───────────────┘                  └────────────────┘  └──────────────────┘
```

### Component Architecture

```
packages/deepfix-kb/src/deepfix_kb/
├── __init__.py
├── config.py                           # Configuration models
├── knowledge_base/                     # Existing local KB
│   ├── __init__.py
│   └── manager.py                      # KnowledgeBaseManager
│
├── retrieval/                          # NEW: Retrieval components
│   ├── __init__.py
│   ├── base.py                         # Base retriever interface
│   ├── tavily_client.py                # Tavily Search integration
│   ├── perplexity_client.py            # Perplexity Sonar via OpenRouter
│   └── hybrid_retriever.py             # Combines multiple sources
│
├── tools/                              # NEW: Agent-consumable tools
│   ├── __init__.py
│   ├── dspy_tools.py                   # DSPy tool definitions
│   └── schemas.py                      # Tool input/output schemas
│
└── bridge.py                           # NEW: Main KnowledgeBridge class
```

## Implementation Timeline

### Phase 1: Core Infrastructure ✅ COMPLETED
- [x] Create `retrieval/` package structure
- [x] Implement `base.py` with `RetrievalResult` and `BaseRetriever`
- [x] Implement `tavily_client.py` with full API integration
  - `TavilySearchRetriever` with search depth control, topic filtering, domain filtering
  - `search_with_answer()` method for AI-generated summaries
- [x] Add configuration models to `config.py`\n  - `TavilyConfig`, `PerplexityConfig`, `KnowledgeBridgeConfig`\n  - `from_env()` factory method for environment variable loading

### Phase 2: Perplexity Integration ✅ COMPLETED
- [x] Implement `perplexity_client.py` with DSPy-based architecture
- [x] Create DSPy Signatures: `ResearchQuery`, `BriefResearchQuery`, `DetailedResearchQuery`, `ComprehensiveResearchQuery`
- [x] Implement `PerplexityResearchModule` with `ChainOfThought` reasoning
- [x] Add citation extraction logic
- [x] Implement multiple model variant support (sonar, sonar-pro, sonar-reasoning)
- [x] Add error handling (DSPy handles retry logic)\n  - Custom exceptions: `PerplexityError`, `PerplexityConfigError`, `PerplexityAPIError`, `PerplexityResponseError`

### Phase 3: Hybrid Retrieval ✅ COMPLETED
- [x] Implement `hybrid_retriever.py`
- [x] Add parallel and cascading strategies (`RetrievalStrategy` enum)
- [x] Implement result deduplication and ranking (`_deduplicate_results`, `_rank_results`)
- [x] Create fallback handling (`_safe_retrieve` with graceful error handling)

### Phase 4: KnowledgeBridge & Tools ✅ COMPLETED
- [x] Implement main `bridge.py` class
  - `KnowledgeBridge` with `query()`, `search()`, `research()` methods
  - `KnowledgeQuery` and `KnowledgeResponse` models
  - Result synthesis via `_synthesize_results()`
- [x] Create DSPy tool definitions in `tools/dspy_tools.py`
  - `WebSearchTool`, `ResearchTool`, `KnowledgeLookupTool`, `HybridSearchTool`
  - `create_knowledge_tools()` factory function
- [x] Add synthesis capability
- [ ] Documentation and usage examples
- [ ] End-to-end integration tests

### Phase 5: Agent Integration and Testing

**KnowledgeBridge → OptimizationAdvisorAgent Integration**:
The KnowledgeBridge provides retrieved insights (web search results, scientific papers, best practices) to the `OptimizationAdvisorAgent`. This grounds the optimization recommendations in up-to-date research and external knowledge.

```
CrossArtifactReasoningAgent
         ↓ (integration insights: training issues, data quality signals)
OptimizationAdvisorAgent ◄── KnowledgeBridge (retrieval: web search, papers)
         ↓
   Grounded Recommendations
```

#### Integration Requirements

**Current State**: `OptimizationAdvisorAgent` already accepts `KnowledgeBridge` as a constructor dependency (`knowledge_bridge: KnowledgeBridge`), but it's not yet utilized in the `forward()` method.

**Required Changes**:

1. **Query Formation** — Build intelligent queries from optimization context:
   ```python
   # In forward(), before calling LLM
   queries = self._build_knowledge_queries(optimization_areas, artifacts_analysis)
   # Example: ["learning rate scheduling for overfitting", "data augmentation for small datasets"]
   ```

2. **Knowledge Retrieval** — Query KnowledgeBridge with optimization-relevant questions:
   ```python
   knowledge_context = await self.knowledge_bridge.query(
       query=queries[0],
       sources=["perplexity", "tavily", "local_kb"]
   )
   ```

3. **Update Signature** — Extend `OptimizationRecommendationSignature` to accept retrieved knowledge:
   ```python
   class OptimizationRecommendationSignature(dspy.Signature):
       # ... existing fields ...
       retrieved_knowledge: str = dspy.InputField(desc="External research and best practices")
   ```

4. **Citation Formatting** — Include source URLs in recommendations output:
   ```python
   citations = [f"[{r.title}]({r.url})" for r in knowledge_context.results]
   ```

5. **Async Support** — Convert `forward()` to async for KnowledgeBridge calls:
   ```python
   async def forward(self, artifacts_analysis, optimization_areas, constraints=None):
       knowledge = await self.knowledge_bridge.query(...)
   ```

#### Integration Checklist

- [ ] Implement `_build_knowledge_queries()` helper method
- [ ] Add async `forward()` with KnowledgeBridge retrieval
- [ ] Update `OptimizationRecommendationSignature` with `retrieved_knowledge` field
- [ ] Format and inject citations into final recommendations
- [ ] Add to `CrossArtifactReasoningAgent` (optional, for context enrichment)
- [ ] E2E integration tests for KnowledgeBridge flow
- [ ] Performance optimization (parallel queries, caching)
- [ ] Production documentation

---

### Integration Testing Strategy
- Hybrid retriever with multiple sources
- KnowledgeBridge end-to-end queries
- DSPy tool execution

### Mocking Strategy
```python
# For testing without API calls
@pytest.fixture
def mock_tavily():
    with patch("deepfix_kb.retrieval.tavily_client.TavilyClient") as mock:
        mock.return_value.search.return_value = {
            "results": [{"content": "Test", "url": "http://test.com", "score": 0.9}]
        }
        yield mock
```

## Security Considerations

1. **API Key Management**: All API keys loaded from environment variables
2. **Rate Limiting**: Implement rate limiting for external API calls
3. **Input Sanitization**: Validate and sanitize user queries before API calls
4. **Error Handling**: Never expose API keys or internal errors in responses
5. **Logging**: Audit logging for all external API calls (without sensitive data)

---

## Future Enhancements

### Phase 2 Features
- **Caching Layer**: Redis-based caching for repeated queries
- **Custom Sources**: Ability to register domain-specific search endpoints
- **Query Router**: ML-based routing to optimal source based on query type
- **Citation Verification**: Automatic verification of cited sources

### Phase 3 Features
- **Streaming Responses**: Real-time streaming for long research queries
- **Multi-Modal**: Support for image search and analysis
- **Feedback Loop**: Learn from agent usage to improve retrieval quality
