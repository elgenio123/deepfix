"""Configuration models for DeepFix Knowledge Base."""

from __future__ import annotations

import os
from enum import StrEnum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class KnowledgeDomain(StrEnum):
    """Knowledge domains for categorizing documents."""

    GLOBAL = "global"
    TRAINING = "training"
    DATA_QUALITY = "data_quality"
    MODEL_OPTIMIZATION = "model_optimization"
    DEBUGGING = "debugging"


class KnowledgeDocument(BaseModel):
    """Knowledge document model for local knowledge base.

    Attributes:
        id: Unique document identifier.
        title: Document title.
        content: Main document content.
        domain: Knowledge domain category.
        knowledge_type: Type of knowledge (concept, pattern, solution, etc.).
        source: Source reference for the document.
        confidence_level: Confidence in the information (0-1).
        tags: List of tags for categorization.
        examples: Optional example use cases.
        ml_frameworks: Applicable ML frameworks.
        model_types: Applicable model types.
    """

    id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Main document content")
    domain: KnowledgeDomain = Field(
        KnowledgeDomain.GLOBAL, description="Knowledge domain"
    )
    knowledge_type: str = Field("general", description="Type of knowledge")
    source: Optional[str] = Field(None, description="Source reference")
    confidence_level: float = Field(0.8, ge=0.0, le=1.0, description="Confidence level")
    tags: List[str] = Field(default_factory=list, description="Tags")
    examples: Optional[List[str]] = Field(None, description="Example use cases")
    ml_frameworks: List[str] = Field(default_factory=list, description="ML frameworks")
    model_types: List[str] = Field(default_factory=list, description="Model types")


class TavilyConfig(BaseModel):
    """Configuration for Tavily Search client.

    Attributes:
        api_key: Tavily API key.
        search_depth: Search depth ("basic" or "advanced").
        default_topic: Default topic filter.
        include_answer: Include AI-generated answer.
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY"),
        description="Tavily API key",
    )
    search_depth: Literal["basic", "advanced"] = Field(
        "basic", description="Search depth"
    )
    default_topic: Literal["general", "news", "finance", "code"] = Field(
        "general", description="Default topic"
    )
    include_answer: bool = Field(True, description="Include AI answer")


class PerplexityConfig(BaseModel):
    """Configuration for Perplexity Sonar client.

    Attributes:
        api_key: OpenRouter API key.
        model: Perplexity model variant.
        temperature: Sampling temperature.
        max_tokens: Maximum response tokens.
    """

    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENROUTER_API_KEY"),
        description="OpenRouter API key",
    )
    model: Literal["sonar", "sonar-pro", "sonar-reasoning"] = Field(
        "sonar", description="Perplexity model variant"
    )
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: Optional[int] = Field(None, description="Max tokens")


class KnowledgeBridgeConfig(BaseModel):
    """Configuration for KnowledgeBridge.

    This configuration model can be used to create a KnowledgeBridge
    instance with all settings.

    Attributes:
        tavily: Tavily configuration.
        perplexity: Perplexity configuration.
        default_strategy: Default retrieval strategy.
        max_results_per_source: Max results from each source.
        max_total_results: Max total results.
        enable_local_kb: Enable local knowledge base.
        enable_synthesis: Enable result synthesis by default.
    """

    tavily: TavilyConfig = Field(default_factory=TavilyConfig)
    perplexity: PerplexityConfig = Field(default_factory=PerplexityConfig)

    default_strategy: Literal[
        "parallel", "cascading", "web_first", "ai_first", "local_first"
    ] = Field("parallel", description="Default retrieval strategy")

    max_results_per_source: int = Field(
        3, ge=1, le=10, description="Max results per source"
    )
    max_total_results: int = Field(10, ge=1, le=50, description="Max total results")

    enable_local_kb: bool = Field(False, description="Enable local KB")
    enable_synthesis: bool = Field(True, description="Enable synthesis by default")

    @classmethod
    def from_env(cls) -> "KnowledgeBridgeConfig":
        """Create configuration from environment variables.

        Environment variables:
            TAVILY_API_KEY: Tavily API key
            OPENROUTER_API_KEY: OpenRouter API key
            PERPLEXITY_MODEL: Perplexity model (sonar, sonar-pro, sonar-reasoning)
            KNOWLEDGE_BRIDGE_STRATEGY: Default strategy
            KNOWLEDGE_BRIDGE_ENABLE_LOCAL_KB: Enable local KB (true/false)

        Returns:
            KnowledgeBridgeConfig instance.
        """
        perplexity_model = os.getenv("PERPLEXITY_MODEL", "sonar")
        strategy = os.getenv("KNOWLEDGE_BRIDGE_STRATEGY", "parallel")
        enable_local = (
            os.getenv("KNOWLEDGE_BRIDGE_ENABLE_LOCAL_KB", "false").lower() == "true"
        )

        return cls(
            perplexity=PerplexityConfig(model=perplexity_model),
            default_strategy=strategy,
            enable_local_kb=enable_local,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of configuration.
        """
        return self.model_dump()
