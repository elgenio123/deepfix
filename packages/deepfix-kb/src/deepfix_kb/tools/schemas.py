"""Input/Output schemas for knowledge tools."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """Standard input schema for knowledge tools.

    Attributes:
        query: The search or research query.
        context: Optional additional context.
        max_results: Maximum number of results to return.
    """

    query: str = Field(..., description="The search or research query")
    context: Optional[str] = Field(None, description="Additional context for the query")
    max_results: int = Field(5, ge=1, le=20, description="Maximum results")


class ToolOutput(BaseModel):
    """Standard output schema for knowledge tools.

    Attributes:
        content: The main content or answer.
        sources: List of source references.
        citations: List of citation URLs.
        metadata: Additional metadata about the results.
    """

    content: str = Field(..., description="The main content or answer")
    sources: List[str] = Field(default_factory=list, description="Source references")
    citations: List[str] = Field(default_factory=list, description="Citation URLs")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    def to_string(self) -> str:
        """Convert output to a formatted string for agent consumption."""
        parts = [self.content]

        if self.sources:
            parts.append("\nSources:")
            for source in self.sources:
                parts.append(f"  - {source}")

        if self.citations:
            parts.append("\nCitations:")
            for citation in self.citations[:5]:  # Limit displayed citations
                parts.append(f"  - {citation}")

        return "\n".join(parts)
