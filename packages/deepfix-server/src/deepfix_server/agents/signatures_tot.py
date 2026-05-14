"""DSPy signatures for Tree of Thoughts (ToT) reasoning."""

from typing import List, Dict, Optional
import dspy
from deepfix_core.models import Analysis
from ..models import AgentResult

class ProposeHypothesesSignature(dspy.Signature):
    """Propose multiple distinct diagnostic hypotheses based on ML artifacts analysis."""
    
    previous_analyses: Dict[str, AgentResult] = dspy.InputField(
        desc="Individual results from artifact analyzers (data, training, checkpoint, etc.)"
    )
    num_hypotheses: int = dspy.InputField(desc="Number of distinct hypotheses to generate")
    
    hypotheses: List[str] = dspy.OutputField(
        desc="List of distinct diagnostic hypotheses explaining the ML system behavior"
    )

class EvaluateHypothesisSignature(dspy.Signature):
    """Evaluate a diagnostic hypothesis against available ML artifact evidence."""
    
    previous_analyses: Dict[str, AgentResult] = dspy.InputField(desc="ML artifact evidence")
    hypothesis: str = dspy.InputField(desc="The hypothesis to evaluate")
    
    judgment: str = dspy.OutputField(
        desc="Evaluation: 'confident' (highly supported), 'likely' (some evidence), 'unlikely' (contradicted or weak)"
    )
    confidence_score: float = dspy.OutputField(desc="Numeric score between 0.0 and 1.0")
    rationale: str = dspy.OutputField(desc="Explanation for the judgment")

class FinalizeToTAnalysisSignature(dspy.Signature):
    """Synthesize the most highly-rated hypotheses into a final diagnostic report."""
    
    previous_analyses: str = dspy.InputField(desc="Original evidence from artifact analyzers")
    top_hypotheses: List[str] = dspy.InputField(desc="The winning reasoning paths/hypotheses")
    rationales: List[str] = dspy.InputField(desc="Rationales and evidence for why these hypotheses are strong")
    output_language: str = dspy.InputField(desc="Language of the output")
    
    analysis: List[Analysis] = dspy.OutputField(
        desc="Consolidated analysis with cross-artifact insights. Categorize findings as 'performance' or 'search'."
    )
    summary: str = dspy.OutputField(
        desc="Summary of the holistic reasoning and diagnostic conclusions"
    )
