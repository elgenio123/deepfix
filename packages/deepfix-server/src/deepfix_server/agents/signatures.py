"""DSPy signatures for agent reasoning"""

from typing import List, Optional

import dspy
from deepfix_core.models import Analysis

from ..models import AgentResult


class OptimizationRecommendationSignature(dspy.Signature):
    """Generate optimization recommendations grounded in external knowledge.

    Uses cross-artifact analysis and retrieved knowledge from KnowledgeBridge
    to provide evidence-based optimization recommendations with citations.
    """

    system_prompt: str = dspy.InputField(desc="System prompt for optimization expert")
    artifacts_analysis: str = dspy.InputField(
        desc="Analysis from previous agents (training dynamics, data quality, etc.)"
    )
    optimization_areas: List[str] = dspy.InputField(
        desc="Specific areas to focus optimization on"
    )
    constraints: Optional[str] = dspy.InputField(
        desc="Optional user constraints or requirements", default=None
    )
    retrieved_knowledge: str = dspy.InputField(
        desc="External research and best practices from KnowledgeBridge (web search, papers)"
    )

    analysis: str = dspy.OutputField(
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


class CrossArtifactReasoningSignature(dspy.Signature):
    """Integrate findings from multiple artifact analyzers"""

    previous_analyses: List[AgentResult] = dspy.InputField(
        desc="Results from multiple artifact analyzers"
    )
    output_language: str = dspy.InputField(desc="Language of the output analysis")

    analysis: List[Analysis] = dspy.OutputField(
        desc="Consolidated analysis with cross-artifact insights. Findings and recommendations based on the agents results"
    )
    summary: str = dspy.OutputField(
        desc="Summary of the cross-artifact reasoning & analysis"
    )
