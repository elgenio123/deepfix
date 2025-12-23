from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Optional

from deepfix_core.models import (
    AgentResult,
    Artifacts,
    DatasetArtifacts,
    DeepchecksArtifacts,
    ModelCheckpointArtifacts,
    TrainingArtifacts,
)
from pydantic import BaseModel, Field


## Agent Context
class AgentContext(BaseModel):
    """Context for agent execution.

    Contains all artifacts, configuration, and intermediate results needed
    for agent analysis.

    Attributes:
        dataset_artifacts: Optional dataset statistics and metadata.
        training_artifacts: Optional training metrics and parameters.
        deepchecks_artifacts: Optional Deepchecks validation results.
        model_checkpoint_artifacts: Optional model checkpoint information.
        dataset_name: Optional name of the dataset being analyzed.
        language: Language for analysis output. Defaults to "english".
        agent_results: Dictionary of results from previously run agents.
        knowledge_cache: Dictionary for caching knowledge retrieval results.
    """

    dataset_artifacts: Optional[DatasetArtifacts] = None
    training_artifacts: Optional[TrainingArtifacts] = None
    deepchecks_artifacts: Optional[DeepchecksArtifacts] = None
    model_checkpoint_artifacts: Optional[ModelCheckpointArtifacts] = None
    dataset_name: Optional[str] = None
    language: str = Field(default="english", description="Language of the analysis")
    agent_results: Dict[str, AgentResult] = Field(
        default={}, description="Results of the agents"
    )
    knowledge_cache: Dict[str, Any] = Field(default={})

    @property
    def artifacts(
        self,
    ) -> List[Artifacts]:
        """Get list of all non-None artifacts.

        Returns:
            List of all artifacts that are not None.
        """
        artifacts = [
            self.dataset_artifacts,
            self.training_artifacts,
            self.deepchecks_artifacts,
            self.model_checkpoint_artifacts,
        ]
        return [a for a in artifacts if a is not None]

    def insert_artifact(self, artifact: Artifacts):
        """Insert an artifact into the appropriate context field.

        Args:
            artifact: Artifact to insert. Must be one of: DatasetArtifacts,
                TrainingArtifacts, DeepchecksArtifacts, ModelCheckpointArtifacts.

        Raises:
            ValueError: If artifact type is not recognized.
        """
        if isinstance(artifact, DatasetArtifacts):
            self.dataset_artifacts = artifact
        elif isinstance(artifact, TrainingArtifacts):
            self.training_artifacts = artifact
        elif isinstance(artifact, DeepchecksArtifacts):
            self.deepchecks_artifacts = artifact
        elif isinstance(artifact, ModelCheckpointArtifacts):
            self.model_checkpoint_artifacts = artifact
        else:
            raise ValueError(f"Invalid artifact type: {type(artifact)}")


class ArtifactAnalysisResult(BaseModel):
    """Result from artifact analysis.

    Attributes:
        context: Agent context containing all artifacts and results.
        summary: Optional overall summary of the analysis.
        additional_outputs: Dictionary of additional outputs from agents.
    """

    context: AgentContext = Field(default=..., description="Context of the analysis")
    summary: Optional[str] = Field(default=..., description="Summary of the analysis")
    additional_outputs: Dict[str, Any] = Field(
        default={}, description="Additional outputs from the agent"
    )

    def get_agent_results(self) -> Dict[str, AgentResult]:
        """Get all agent results from the context.

        Returns:
            Dictionary mapping agent names to their results.
        """
        return self.context.agent_results

    def get_error_messages(self) -> Dict[str, str]:
        """Get error messages from all agents that failed.

        Returns:
            Dictionary mapping agent names to their error messages.
            Only includes agents that have error messages.
        """
        return {
            agent_name: agent_result.error_message
            for agent_name, agent_result in self.context.agent_results.items()
        }


# ============================================================================
# KnowledgeBridge Models
# ============================================================================


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


class AgentKnowledgeRequest(BaseModel):
    """Standard knowledge request from agents.

    Attributes:
        requesting_agent: Name of the agent making the request.
        domain: Optional knowledge domain to search. If None, all domains
            are searched.
        query_type: Type of knowledge query (best_practice, diagnostic, etc.).
        agent_result: Agent result providing context for the query.
        max_results: Maximum number of results to return (1-20). Defaults to 5.
        min_confidence: Minimum confidence threshold for results (0.0-1.0).
            Defaults to 0.7.
    """

    requesting_agent: str
    domain: Optional[KnowledgeDomain] = Field(
        default=None,
        description="Knowledge domain for the retrieval. If None, all domains will be searched.",
    )
    query_type: QueryType

    # Context from agent analysis
    agent_result: AgentResult

    # Retrieval preferences
    max_results: int = Field(default=5, ge=1, le=20)
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0)


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
