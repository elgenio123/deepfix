# DeepFix Knowledge Base (deepfix-kb)

Knowledge retrieval system for the DeepFix multi-agent ML debugging platform.

## Overview

**KnowledgeBridge** provides grounded, up-to-date information to support agent responses by combining:

1. **Web Search (Tavily)**: Real-time information retrieval optimized for AI agents
2. **AI Research (Perplexity Sonar)**: Deep reasoning and synthesis via OpenRouter
3. **Local Knowledge Base**: Domain-specific ML/DL knowledge via LlamaIndex

The system is designed as a **modular tool** that can be consumed by any agent in the DeepFix ecosystem.

## Installation

```bash
# Install with uv (recommended)
uv pip install -e packages/deepfix-kb

# Or with pip
pip install -e packages/deepfix-kb
```

## Configuration

Set the following environment variables:

```bash
# Required for web search
export TAVILY_API_KEY="tvly-xxxxxxxxxxxx"

# Required for AI research
export OPENROUTER_API_KEY="sk-or-xxxxxxxxxxxx"

# Optional: Perplexity model selection
export PERPLEXITY_MODEL="sonar"  # sonar, sonar-pro, sonar-reasoning
```

## Quick Start

### Direct Usage

```python
import asyncio
from deepfix_kb import KnowledgeBridge

async def main():
    # Initialize the bridge
    bridge = KnowledgeBridge()

    # Simple query
    response = await bridge.query(
        "How to diagnose gradient vanishing in deep networks?"
    )

    # Print synthesized answer
    print(response.synthesis)

    # Print sources
    for result in response.results:
        print(f"- {result.source}: {result.url}")

asyncio.run(main())
```

### With DSPy Agents

```python
import dspy
from deepfix_kb import KnowledgeBridge
from deepfix_kb.tools import create_knowledge_tools

# Initialize bridge and tools
bridge = KnowledgeBridge()
tools = create_knowledge_tools(bridge)

# Create ReAct agent with knowledge tools
agent = dspy.ReAct(
    signature="question -> answer",
    tools=tools
)

# Agent can now use knowledge retrieval
result = agent(question="What learning rate should I use for fine-tuning ViT?")
```

## Available Tools

### WebSearchTool
Real-time web search for current information.

```python
from deepfix_kb.tools import WebSearchTool

tool = WebSearchTool(bridge)
result = tool("PyTorch gradient checkpointing tutorial")
```

### ResearchTool
AI-powered research with citations.

```python
from deepfix_kb.tools import ResearchTool

tool = ResearchTool(bridge)
result = tool("Compare Adam vs AdamW optimizers for transformers")
```

### KnowledgeLookupTool
Local knowledge base for domain expertise.

```python
from deepfix_kb.tools import KnowledgeLookupTool

tool = KnowledgeLookupTool(bridge)
result = tool("overfitting detection best practices")
```

### HybridSearchTool
Combined search across all sources.

```python
from deepfix_kb.tools import HybridSearchTool

tool = HybridSearchTool(bridge)
result = tool("How to implement mixed precision training?")
```

## Retrieval Strategies

The hybrid retriever supports multiple strategies:

- **PARALLEL**: Query all sources simultaneously (default)
- **CASCADING**: Try sources sequentially until enough results
- **WEB_FIRST**: Prioritize web search results
- **AI_FIRST**: Prioritize Perplexity AI results
- **LOCAL_FIRST**: Prioritize local knowledge base

```python
from deepfix_kb import KnowledgeBridge, RetrievalStrategy

bridge = KnowledgeBridge(default_strategy=RetrievalStrategy.AI_FIRST)

# Or per-query
response = await bridge.query(
    "How to fix NaN loss?",
    strategy=RetrievalStrategy.WEB_FIRST
)
```

## Architecture

```
deepfix_kb/
├── __init__.py           # Package exports
├── bridge.py             # KnowledgeBridge main class
├── config.py             # Configuration models
│
├── retrieval/            # Retrieval sources
│   ├── base.py           # Base interfaces
│   ├── tavily_client.py  # Tavily web search
│   ├── perplexity_client.py  # Perplexity Sonar
│   └── hybrid_retriever.py   # Multi-source orchestration
│
├── tools/                # Agent tools
│   ├── dspy_tools.py     # DSPy tool definitions
│   └── schemas.py        # Input/output schemas
│
└── knowledge_base/       # Local KB (existing)
    └── manager.py        # LlamaIndex-based KB
```

## API Reference

### KnowledgeBridge

Main interface for knowledge retrieval.

```python
class KnowledgeBridge:
    async def query(
        self,
        query: str,
        context: Optional[str] = None,
        sources: Optional[List[str]] = None,
        max_results: int = 5,
        strategy: Optional[RetrievalStrategy] = None,
        synthesize: bool = True,
    ) -> KnowledgeResponse: ...

    async def search(self, query: str, max_results: int = 5) -> List[RetrievalResult]: ...

    async def research(self, topic: str, depth: str = "detailed") -> RetrievalResult: ...
```

### KnowledgeResponse

```python
class KnowledgeResponse:
    query: str                    # Original query
    results: List[RetrievalResult]  # Retrieved results
    synthesis: Optional[str]      # AI synthesis
    sources_used: List[str]       # Source types used
    total_citations: List[str]    # All citations
```

### RetrievalResult

```python
class RetrievalResult:
    content: str                  # Main content
    source: str                   # Source name
    source_type: str              # "web", "perplexity", "local_kb"
    url: Optional[str]            # Source URL
    relevance_score: Optional[float]  # Relevance score
    citations: Optional[List[str]]    # Citations
```

## Development

```bash
# Run tests
uv run pytest packages/deepfix-kb/tests

# Type checking
uv run mypy packages/deepfix-kb/src

# Linting
uv run ruff check packages/deepfix-kb/src
```

## License

See LICENSE file in the repository root.
