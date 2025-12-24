from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class KnowledgeDomain(StrEnum):
    """Knowledge domains for retrieval.

    Defines different domains of ML knowledge that can be searched.
    """

    TRAINING = "training"
    DATA_QUALITY = "data_quality"
    ARCHITECTURE = "architecture"
    OPTIMIZATION = "optimization"
    GLOBAL = "global"


class QueryType(StrEnum):
    """Types of knowledge queries.

    Defines different types of queries that can be made to the knowledge base.
    """

    BEST_PRACTICE = "best_practice"
    DIAGNOSTIC = "diagnostic"
    SOLUTION = "solution"
    VALIDATION = "validation"


class KnowledgeDocument(BaseModel):
    """Structured knowledge document for indexing.

    Attributes:
        title: Title of the knowledge document.
        content: Main content of the document.
        domain: Knowledge domain this document belongs to.
        knowledge_type: Type of knowledge (best_practice, diagnostic, etc.).
        tags: List of tags for categorization.
        ml_frameworks: List of ML frameworks this applies to
            (e.g., pytorch, lightning, tensorflow).
        model_types: List of model types this applies to
            (e.g., cnn, transformer, mlp).
        problem_types: List of problem types this applies to
            (e.g., classification, regression).
        confidence_level: Confidence level in the knowledge (0.0-1.0).
            Defaults to 0.8.
        source: Source of the knowledge (research paper, documentation, etc.).
        last_updated: Optional last update timestamp.
        prerequisites: List of conditions when this knowledge is applicable.
        contraindications: List of conditions when this should NOT be used.
        examples: List of example use cases.
    """

    # Core Content
    title: str
    content: str
    domain: KnowledgeDomain
    knowledge_type: QueryType

    # Metadata for Retrieval
    tags: List[str] = Field(default=[])
    ml_frameworks: List[str] = Field(
        default=[], description="e.g., pytorch, lightning, tensorflow"
    )
    model_types: List[str] = Field(
        default=[], description="e.g., cnn, transformer, mlp"
    )
    problem_types: List[str] = Field(
        default=[], description="e.g., classification, regression"
    )

    # Validation
    confidence_level: float = Field(ge=0.0, le=1.0, default=0.8)
    source: str = Field(description="Research paper, documentation, case study")
    last_updated: Optional[datetime] = Field(default=None)

    # Application Context
    prerequisites: List[str] = Field(
        default=[], description="When is this knowledge applicable?"
    )
    contraindications: List[str] = Field(
        default=[], description="When should this NOT be used?"
    )
    examples: List[str] = Field(default=[])


class KnowledgeItem(BaseModel):
    """Single piece of retrieved knowledge.

    Attributes:
        content: Content of the knowledge item.
        source: Source of the knowledge.
        confidence: Optional confidence score on relevance (0.0-1.0).
        relevance_score: Optional relevance score to the query (0.0-1.0).
        metadata: Dictionary of additional metadata.
    """

    content: str
    source: str
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score on relevance of evidence to the question, between 0.0 and 1.0",
    )
    relevance_score: Optional[float] = Field(
        default=None,
        description="Relevance score of the evidence to the question, between 0.0 and 1.0",
    )
    metadata: Dict[str, Any] = Field(default={}, description="Metadata of the evidence")


class QueryGenerationResult(BaseModel):
    """Result from query generation process.

    Attributes:
        domain: Knowledge domain selected for retrieval.
        retrieval_queries: List of optimized queries for multi-aspect retrieval.
        search_strategy: Retrieval strategy to use (semantic, hybrid, keyword-based).
        rationale: Concise explanation of why these queries were generated.
    """

    domain: KnowledgeDomain = Field(description="Knowledge domain for the retrieval")
    retrieval_queries: List[str] = Field(
        description="List of optimized queries for multi-aspect retrieval"
    )
    search_strategy: str = Field(
        description="Retrieval strategy (semantic, hybrid, keyword-based)"
    )
    rationale: str = Field(description="Concise rationale behind the query formulation")


class EvidenceValidationResult(BaseModel):
    """Evidence validation result.

    Contains the confidence, relevance, and actionable status for an evidence item.

    Attributes:
        confidence: Confidence score on relevance (0.0-1.0).
        relevance: Explanation of why this evidence is or isn't relevant.
        is_actionable: Whether the evidence provides actionable insights.
        is_contradictory: Whether the evidence contradicts the question.
    """

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score on relevance of evidence to the question, between 0.0 and 1.0",
    )
    relevance: str = Field(
        description="Explanation of why this evidence is or isn't relevant"
    )
    is_actionable: bool = Field(
        description="Whether the evidence provides actionable insights True/False"
    )
    is_contradictory: bool = Field(
        description="Whether the evidence contradicts the question True/False"
    )


class KnowledgeQuery(BaseModel):
    """Input model for knowledge queries.

    Attributes:
        query: The question or topic to research.
        context: Additional context from the calling agent.
        sources: Specific sources to use (None = all available).
        max_results: Maximum number of results to return.
        require_citations: Whether citations are required.
        strategy: Retrieval strategy to use.
    """

    query: str = Field(..., description="The question or topic to research")
    context: Optional[str] = Field(
        None, description="Additional context from the agent"
    )
    sources: Optional[List[str]] = Field(
        None, description="Specific sources to use: 'web', 'perplexity', 'local_kb'"
    )
    max_results: int = Field(5, ge=1, le=20, description="Maximum results to return")
    require_citations: bool = Field(True, description="Whether citations are required")
    strategy: Optional[RetrievalStrategy] = Field(
        None, description="Retrieval strategy to use"
    )


class KnowledgeResponse(BaseModel):
    """Structured knowledge response.

    Attributes:
        query: The query that was used for retrieval.
        retrieved_knowledge: List of retrieved knowledge items.
        validation_results: List of validation results for each knowledge item.
    """

    query: str
    retrieved_knowledge: List[KnowledgeItem]
    validation_results: List[EvidenceValidationResult]
