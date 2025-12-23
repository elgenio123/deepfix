"""DeepFix Knowledge Base - Knowledge retrieval system for AI agents.

This package provides a unified knowledge retrieval system that combines:
- Web Search (Tavily): Real-time web information
- AI Research (Perplexity Sonar): Synthesized analysis with citations
- Local KB (LlamaIndex): Domain-specific ML/DL knowledge

Example:
    >>> from deepfix_kb import KnowledgeBridge
    >>> from deepfix_kb.tools import create_knowledge_tools
    >>>
    >>> # Initialize the bridge
    >>> bridge = KnowledgeBridge()
    >>>
    >>> # Direct query
    >>> response = await bridge.query("How to fix gradient vanishing?")
    >>> print(response.synthesis)
    >>>
    >>> # Create tools for agents
    >>> tools = create_knowledge_tools(bridge)
"""

from .bridge import KnowledgeBridge, KnowledgeQuery, KnowledgeResponse
from .retrieval import (
    BaseRetriever,
    HybridRetriever,
    PerplexitySonarRetriever,
    RetrievalResult,
    RetrievalStrategy,
    TavilySearchRetriever,
)

__all__ = [
    # Main interface
    "KnowledgeBridge",
    "KnowledgeQuery",
    "KnowledgeResponse",
    # Retrievers
    "BaseRetriever",
    "RetrievalResult",
    "TavilySearchRetriever",
    "PerplexitySonarRetriever",
    "HybridRetriever",
    "RetrievalStrategy",
]

__version__ = "0.1.0"
