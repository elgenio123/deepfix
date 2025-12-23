"""Base interfaces and models for knowledge retrieval."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RetrievalResult(BaseModel):
    """Standardized result from any retrieval source.

    This model provides a unified format for results coming from different
    retrieval sources (web search, AI research, local knowledge base).

    Attributes:
        content: The main content/text retrieved.
        source: The source name or title.
        source_type: Type identifier ("web", "perplexity", "local_kb").
        url: Optional URL for web sources.
        relevance_score: Optional relevance/similarity score.
        citations: Optional list of citation URLs.
        metadata: Optional additional metadata.
    """

    content: str = Field(..., description="The main content/text retrieved")
    source: str = Field(..., description="The source name or title")
    source_type: str = Field(
        ..., description="Type identifier: 'web', 'perplexity', 'local_kb'"
    )
    url: Optional[str] = Field(None, description="URL for web sources")
    relevance_score: Optional[float] = Field(
        None, description="Relevance/similarity score", ge=0.0, le=1.0
    )
    citations: Optional[List[str]] = Field(None, description="List of citation URLs")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class BaseRetriever(ABC):
    """Abstract base class for all retrieval implementations.

    All retrieval sources (Tavily, Perplexity, Local KB) must implement
    this interface to ensure consistent behavior across the system.
    """

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        max_results: int = 5,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        """Retrieve information based on query.

        Args:
            query: The search/research query.
            max_results: Maximum number of results to return.
            **kwargs: Additional retriever-specific parameters.

        Returns:
            List of RetrievalResult objects.
        """
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Return the type identifier for this source.

        Returns:
            String identifier for this retrieval source.
        """
        pass

    @property
    def is_available(self) -> bool:
        """Check if this retriever is properly configured and available.

        Returns:
            True if the retriever can be used, False otherwise.
        """
        return True

    async def health_check(self) -> bool:
        """Perform a health check on the retrieval source.

        Returns:
            True if the source is healthy and responding.
        """
        try:
            # Simple health check - try a minimal query
            results = await self.retrieve("test", max_results=1)
            return True
        except Exception as e:
            logger.warning(f"Health check failed for {self.source_type}: {e}")
            return False
