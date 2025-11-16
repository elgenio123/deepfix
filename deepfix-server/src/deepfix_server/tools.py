from abc import ABC, abstractmethod

from llama_index.core import VectorStoreIndex


class Tool(ABC):
    """Base class for Knowledge Bridge tools.

    Tools provide retrieval and query capabilities for the knowledge base.
    Subclasses should implement the __call__ method.

    Attributes:
        name: Name of the tool, derived from class name.
    """

    def __init__(self):
        """Initialize the tool."""
        self.name = self.__class__.__name__

    @abstractmethod
    def __call__(self, query: str) -> str:
        """Execute the tool with a query.

        Args:
            query: Query string to process.

        Returns:
            Formatted response string with results.
        """
        pass

    def _format_with_citations(self, response) -> str:
        """Format response with source citations for traceability.

        Args:
            response: Response object with source_nodes attribute.

        Returns:
            Formatted string with response text and source citations.
        """
        citations = [
            f"[{i + 1}] {node.metadata['source']}"
            for i, node in enumerate(response.source_nodes)
        ]
        return f"{response.response}\n\nSources:\n" + "\n".join(citations)


class DomainRetrieverTool(Tool):
    """Domain-specific knowledge retrieval tool.

    Retrieves knowledge from a specific domain using vector similarity search.

    Attributes:
        query_engine: LlamaIndex query engine for retrieval.
        domain: Knowledge domain this tool searches.
    """

    def __init__(self, index: VectorStoreIndex, domain: str, similarity_top_k=5):
        """Initialize the domain retriever tool.

        Args:
            index: VectorStoreIndex containing the knowledge base.
            domain: Knowledge domain name.
            similarity_top_k: Number of top similar results to retrieve.
                Defaults to 5.
        """
        super().__init__()
        self.query_engine = index.as_query_engine(
            similarity_top_k=similarity_top_k, response_mode="tree_summarize"
        )
        self.domain = domain

    def __call__(self, query: str) -> str:
        """Execute retrieval and return formatted results.

        Args:
            query: Query string to search for.

        Returns:
            Formatted response with citations.
        """
        response = self.query_engine.query(query)
        return self._format_with_citations(response)


class SemanticRetriever(DomainRetrieverTool):
    """Semantic knowledge retrieval tool.

    Specialized retriever for semantic similarity search in a knowledge domain.
    """

    def __init__(self, index: VectorStoreIndex, domain: str, similarity_top_k=5):
        """Initialize the semantic retriever.

        Args:
            index: VectorStoreIndex containing the knowledge base.
            domain: Knowledge domain name.
            similarity_top_k: Number of top similar results to retrieve.
                Defaults to 5.
        """
        super().__init__(index=index, domain=domain, similarity_top_k=similarity_top_k)


class ExampleRetriever(DomainRetrieverTool):
    """Example retrieval tool.

    Specialized retriever for finding example use cases in a knowledge domain.
    """

    def __init__(self, index: VectorStoreIndex, domain: str, similarity_top_k=5):
        """Initialize the example retriever.

        Args:
            index: VectorStoreIndex containing the knowledge base.
            domain: Knowledge domain name.
            similarity_top_k: Number of top similar results to retrieve.
                Defaults to 5.
        """
        super().__init__(index=index, domain=domain, similarity_top_k=similarity_top_k)
