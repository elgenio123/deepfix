from __future__ import annotations

from enum import StrEnum
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, Field


# ============================================================================
# Analysis data Models
# ============================================================================
class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnalyzerTypes(StrEnum):
    TRAINING = "training"
    DEEPCHECKS = "deepchecks"
    DATASET = "dataset"
    MODEL_CHECKPOINT = "model_checkpoint"


class Finding(BaseModel):
    description: str = Field(
        default=..., description="Short Description of the finding"
    )
    evidence: str = Field(default=..., description="Evidence of the finding")
    severity: Severity = Field(default=..., description="Severity of the finding")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the finding and severity"
    )


class Recommendation(BaseModel):
    action: str = Field(
        default=..., description="Action to take to address the finding"
    )
    rationale: str = Field(default=..., description="Rationale for the recommendation")
    # priority: Severity = Field(default=...,description="Priority of the recommendation")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the recommendation"
    )


class Analysis(BaseModel):
    findings: Finding = Field(default=..., description="Finding of the analysis")
    recommendations: Recommendation = Field(
        default=..., description="Recommendation based on the findings"
    )


class AgentResult(BaseModel):
    agent_name: str
    analysis: List[Analysis] = Field(
        default=[], description="List of Analysis elements"
    )
    analyzed_artifacts: Optional[List[str]] = Field(
        default=None, description="List of artifacts analyzed by the agent"
    )
    retrieved_knowledge: Optional[List[str]] = Field(
        default=None, description="External knowledge relevant to the analysis"
    )
    additional_outputs: Dict[str, Any] = Field(
        default={}, description="Additional outputs from the agent"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if the agent failed"
    )

    def to_dataframe(self) -> pd.DataFrame:
        rows = []
        for analysis in self.analysis:
            # Extract findings and recommendations from the Analysis object
            findings = analysis.findings
            recommendations = analysis.recommendations

            # Create a row combining findings and recommendations
            row = {
                "agent_name": self.agent_name,
                "analyzed_artifacts": ", ".join(self.analyzed_artifacts)
                if self.analyzed_artifacts
                else "",
                "retrieved_knowledge": ", ".join(self.retrieved_knowledge)
                if self.retrieved_knowledge
                else "",
                "summary": self.additional_outputs.get("summary", ""),
                "finding_description": findings.description,
                "finding_evidence": findings.evidence,
                "error_message": self.error_message,
                "finding_severity": findings.severity.value,
                "finding_confidence": findings.confidence,
                "recommendation_action": recommendations.action,
                "recommendation_rationale": recommendations.rationale,
                #'recommendation_priority': recommendations.priority.value,
                "recommendation_confidence": recommendations.confidence,
            }
            rows.append(row)

        return pd.DataFrame(rows)
