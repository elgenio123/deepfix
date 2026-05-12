"""DSPy signatures for agent reasoning"""

from typing import List, Optional, Dict

import dspy
from deepfix_core.models import Analysis

from ..models import AgentResult


class OptimizationRecommendationSignature(dspy.Signature):
    """Generate optimization recommendations grounded in external knowledge.

    Uses analysis from previous agents and retrieved knowledge from KnowledgeBridge
    to provide evidence-based optimization recommendations with citations.
    """

    artifacts_analysis: List[Analysis] = dspy.InputField(
        desc="Analysis from previous agents (training dynamics, data quality, etc.)"
    )
    constraints: Optional[str] = dspy.InputField(
        desc="Optional user constraints or requirements", default=None
    )
    retrieved_knowledge: str = dspy.InputField(
        desc="External research and best practices from KnowledgeBridge (web search, papers)"
    )

    analysis: List[Analysis] = dspy.OutputField(
        desc="Detailed recommendations with citations to retrieved sources"
    )


class ArtifactAnalysisSignature(dspy.Signature):
    """Analyze dataset, model checkpoint, training artifacts for issues and recommendations"""

    artifacts: str = dspy.InputField(
        desc="Structured artifacts (dataset, model checkpoint, training artifacts)"
    )
    output_language: str = dspy.InputField(desc="Language of the output analysis")
    analysis: List[Analysis] = dspy.OutputField(
        desc="Findings and recommendations based on the artifacts"
    )


class CalibrateFindingSignature(dspy.Signature):
    """Critically evaluate if a specific ML finding is supported by the provided evidence.
    Be extremely rigorous and skeptical. Only support findings that are clearly evidenced."""

    evidence: str = dspy.InputField(desc="The raw data/metrics or previous agent findings")
    finding_description: str = dspy.InputField(desc="Description of the finding to evaluate")
    finding_evidence: str = dspy.InputField(desc="The evidence cited for this finding")
    
    is_supported: bool = dspy.OutputField(desc="Is this finding clearly supported by the evidence?")
    rationale: str = dspy.OutputField(desc="Brief explanation of why the finding is or isn't supported")


class CrossArtifactReasoningSignature(dspy.Signature):
    """Integrate findings from multiple artifact analyzers"""

    previous_analyses: Dict[str, AgentResult] = dspy.InputField(
        desc="Results from multiple artifact analyzers"
    )
    output_language: str = dspy.InputField(desc="Language of the output analysis")

    analysis: List[Analysis] = dspy.OutputField(
        desc="Consolidated analysis with cross-artifact insights. Findings and recommendations based on the agents results"
    )
    summary: str = dspy.OutputField(
        desc="Summary of the cross-artifact reasoning & analysis"
    )
