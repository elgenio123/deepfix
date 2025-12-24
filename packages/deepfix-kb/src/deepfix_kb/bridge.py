"""KnowledgeBridge - Main interface for knowledge retrieval system."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union
from deepfix_core.models import Analysis

from .retrieval import (
    HybridRetriever,
    PerplexitySonarRetriever,
    RetrievalResult,
    RetrievalStrategy,
    TavilySearchRetriever,
)

logger = logging.getLogger(__name__)


class Agent(dspy.Module):
    """Base class for all analysis agents.

    Provides common functionality for LLM configuration and context management.
    Subclasses should implement the forward method and system_prompt property.

    Attributes:
        _llm_config: Optional LLM configuration for the agent.
        agent_name: Name of the agent derived from class name.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the agent.

        Args:
            config: Optional LLM configuration. If None, a warning is logged
                and dspy-settings should be configured separately.
        """
        super().__init__()
        assert (config is None) or isinstance(config, LLMConfig), (
            "config must be an instance of LLMConfig"
        )
        self._llm_config = config
        self.agent_name = self.__class__.__name__.replace("agent", "")
        if config is None:
            LOGGER.warning(
                "No LLM config provided, Make sure to use dspy-settings.configure(...) to configure the LLM."
            )

    @contextmanager
    def _llm_context(self):
        """Context manager for LLM configuration.

        Yields a dspy context with the configured LLM if config is provided,
        otherwise yields a null context.

        Yields:
            dspy context with LLM configuration or null context.
        """
        if self._llm_config is None:
            with nullcontext():
                yield
            return
        with dspy.context(
            lm=dspy.LM(
                model=self._llm_config.model_name,
                cache=self._llm_config.cache,
                api_base=self._llm_config.base_url,
                api_key=self._llm_config.api_key,
                temperature=self._llm_config.temperature,
                max_tokens=self._llm_config.max_tokens,
            ),
            track_usage=self._llm_config.track_usage,
        ):
            yield

    def forward(self, *args, **kwargs) -> Any:
        """Forward method to be implemented by subclasses.

        Args:
            *args: Variable positional arguments.
            **kwargs: Variable keyword arguments.

        Returns:
            Result of the agent's analysis.

        Raises:
            NotImplementedError: Always raised, must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @property
    def system_prompt(self) -> str:
        """System prompt for the agent.

        Returns:
            Empty string by default. Subclasses should override to provide
            their specific system prompt.
        """
        return ""


class KnowledgeBridge:
    """Main interface for the knowledge retrieval system.

    KnowledgeBridge provides a unified API for retrieving knowledge from
    multiple sources, designed to be consumed as a tool by DeepFix agents.

    Features:
        - Unified query interface for all knowledge sources
        - Multiple retrieval strategies (parallel, cascading, priority)
        - Optional synthesis of results using AI
        - Citation aggregation and tracking
        - Context-aware query enhancement

    Data Sources:
        - Web Search (Tavily): Real-time web information
        - AI Research (Perplexity Sonar): Synthesized analysis with citations
        - Local KB: Domain-specific ML/DL knowledge

    Example:
        >>> bridge = KnowledgeBridge()
        >>>
        >>> # Simple query
        >>> response = await bridge.query(
        ...     "How to fix overfitting in transformers?"
        ... )
        >>> print(response.synthesis)
        >>>
        >>> # Query with specific sources
        >>> response = await bridge.query(
        ...     "Latest papers on gradient accumulation",
        ...     sources=["web", "perplexity"]
        ... )
    """

    def __init__(
        self,
        tavily_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        perplexity_model: str = "sonar",
        enable_local_kb: bool = False,
        default_strategy: RetrievalStrategy = RetrievalStrategy.PARALLEL,
    ):
        """Initialize KnowledgeBridge with configured retrieval sources.

        Args:
            tavily_api_key: Tavily API key (or set TAVILY_API_KEY env var).
            openrouter_api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var).
            perplexity_model: Perplexity model variant ("sonar", "sonar-pro", "sonar-reasoning").
            enable_local_kb: Whether to enable local knowledge base.
            default_strategy: Default retrieval strategy.
        """
        logger.info("Initializing KnowledgeBridge")

        # Initialize retrievers
        self.tavily = TavilySearchRetriever(api_key=tavily_api_key)
        self.perplexity = PerplexitySonarRetriever(
            api_key=openrouter_api_key,
            model=perplexity_model,
        )

        # Local KB is optional and requires additional setup
        self.local_kb = None
        if enable_local_kb:
            try:
                from .knowledge_base.manager import KnowledgeBaseManager

                # Note: Would need embed_model configuration
                logger.info("Local KB enabled but requires embed_model configuration")
            except ImportError:
                logger.warning("Local KB dependencies not available")

        # Initialize hybrid retriever
        self.retriever = HybridRetriever(
            tavily=self.tavily,
            perplexity=self.perplexity,
            local_kb=self.local_kb,
        )

        self.default_strategy = default_strategy

        # Log available sources
        logger.info(f"Available sources: {self.retriever.available_sources}")

    async def query(
        self,
        query: Union[str, Analysis],
        context: Optional[str] = None,
        sources: Optional[List[str]] = None,
        max_results: int = 5,
        strategy: Optional[RetrievalStrategy] = None,
        synthesize: bool = True,
        **kwargs: Any,
    ) -> KnowledgeResponse:
        """Query the knowledge system and return grounded results.

        Args:
            query: The question or topic to research.
            context: Additional context (e.g., from agent's current analysis).
            sources: Limit to specific sources ["web", "perplexity", "local_kb"].
            max_results: Maximum number of results.
            strategy: Retrieval strategy to use.
            synthesize: Whether to create an AI synthesis of results.
            **kwargs: Additional parameters passed to retrievers.

        Returns:
            KnowledgeResponse with results, synthesis, and citations.
        """
        logger.info(f"Knowledge query: '{query[:80]}...'")

        # Enhance query with context if provided
        enhanced_query = self._enhance_query(query, context)

        # Retrieve from sources
        results = await self.retriever.retrieve(
            query=enhanced_query,
            strategy=strategy or self.default_strategy,
            sources=sources,
            max_total_results=max_results,
            **kwargs,
        )

        # Optionally synthesize results
        synthesis = None
        if synthesize and results:
            synthesis = await self._synthesize_results(query, results)

        # Collect all citations
        all_citations = self._collect_citations(results)

        # Identify sources used
        sources_used = list(set(r.source_type for r in results))

        return KnowledgeResponse(
            query=query,
            results=results,
            synthesis=synthesis,
            sources_used=sources_used,
            total_citations=all_citations,
            metadata={
                "strategy": (strategy or self.default_strategy).value,
                "enhanced_query": enhanced_query if context else None,
                "result_count": len(results),
            },
        )

    async def search(
        self,
        query: str,
        max_results: int = 5,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        """Perform a web search using Tavily.

        A convenience method for quick web searches.

        Args:
            query: Search query.
            max_results: Maximum results.
            **kwargs: Additional Tavily parameters.

        Returns:
            List of web search results.
        """
        return await self.retriever.retrieve(
            query=query,
            sources=["web"],
            max_total_results=max_results,
            **kwargs,
        )

    async def research(
        self,
        topic: str,
        depth: str = "detailed",
        **kwargs: Any,
    ) -> RetrievalResult:
        """Research a topic using Perplexity Sonar.

        A convenience method for AI-powered research.

        Args:
            topic: Topic to research.
            depth: Research depth ("brief", "detailed", "comprehensive").
            **kwargs: Additional parameters.

        Returns:
            Single RetrievalResult with research findings.
        """
        if hasattr(self.perplexity, "research"):
            return await self.perplexity.research(topic, depth=depth, **kwargs)

        # Fallback to regular retrieve
        results = await self.retriever.retrieve(
            query=topic,
            sources=["perplexity"],
            max_total_results=1,
            **kwargs,
        )
        return results[0] if results else None

    def _enhance_query(
        self,
        query: Union[str, Analysis],
        context: Optional[str],
    ) -> str:
        """Enhance query with additional context.

        When agents provide context about their current analysis,
        this context can help retrieve more relevant information.

        For Analysis objects:
        - Query is extracted from findings.description
        - Context is built from evidence, severity, and recommendations

        Args:
            query: Original query string or Analysis object.
            context: Additional context from the agent (used for string queries).

        Returns:
            Enhanced query string optimized for knowledge retrieval.
        """
        if isinstance(query, Analysis):
            # Extract the main query from findings description
            main_query = query.findings.description

            # Build context from analysis details
            context_parts = []

            # Add evidence as context
            if query.findings.evidence:
                context_parts.append(f"Evidence: {query.findings.evidence}")

            # Add severity for prioritization
            context_parts.append(f"Severity: {query.findings.severity.value}")

            # Add recommendation context
            if query.recommendations.action:
                context_parts.append(f"Proposed action: {query.recommendations.action}")
            if query.recommendations.rationale:
                context_parts.append(f"Rationale: {query.recommendations.rationale}")

            analysis_context = "\n".join(context_parts)

            return (
                f"ML Training Issue: {main_query}\n\n"
                f"Context:\n{analysis_context}\n\n"
                f"Find best practices, research, and solutions for this issue."
            )

        # String query handling
        if not context:
            return query

        # Prepend context to query
        return f"Given the following context: {context}\n\nAnswer: {query}"

    async def _synthesize_results(
        self,
        query: str,
        results: List[RetrievalResult],
    ) -> Optional[str]:
        """Create a synthesized summary of retrieval results.

        Uses Perplexity to synthesize information from multiple sources
        into a coherent answer.

        Args:
            query: Original query.
            results: Retrieved results to synthesize.

        Returns:
            Synthesized summary string, or None if synthesis fails.
        """
        if not self.perplexity.is_available:
            logger.warning("Synthesis unavailable: Perplexity not configured")
            return None

        # Build context from results
        context_parts = []
        for i, r in enumerate(results[:5], 1):  # Limit to top 5 for synthesis
            source_info = f"[{r.source}]" if r.source else ""
            url_info = f" ({r.url})" if r.url else ""
            context_parts.append(f"{i}. {source_info}{url_info}\n{r.content[:500]}")

        context = "\n\n".join(context_parts)

        synthesis_prompt = (
            f"Based on the following search results, provide a concise and "
            f"accurate synthesis answering: {query}\n\n"
            f"Search Results:\n{context}\n\n"
            f"Synthesize the key information into a coherent answer. "
            f"Include specific details and cite the sources where relevant."
        )

        try:
            response = await self.perplexity.retrieve(
                synthesis_prompt,
                max_results=1,
            )
            if response:
                return response[0].content
        except Exception as e:
            logger.warning(f"Synthesis failed: {e}")

        return None

    def _collect_citations(
        self,
        results: List[RetrievalResult],
    ) -> List[str]:
        """Collect all unique citations from results.

        Args:
            results: List of retrieval results.

        Returns:
            List of unique citation URLs.
        """
        all_citations = []

        for result in results:
            # Add explicit citations
            if result.citations:
                all_citations.extend(result.citations)

            # Add result URL as citation
            if result.url:
                all_citations.append(result.url)

        # Return unique citations preserving order
        seen = set()
        unique = []
        for citation in all_citations:
            if citation not in seen:
                seen.add(citation)
                unique.append(citation)

        return unique
