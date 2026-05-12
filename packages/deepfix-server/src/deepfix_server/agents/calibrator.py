import asyncio
import dspy
from typing import List, Optional
from deepfix_core.models import Finding, Analysis
from .signatures import CalibrateFindingSignature
from ..config import LLMConfig

class FindingCalibrator(dspy.Module):
    """Calibrates confidence of findings using Self-Consistency and P(True) estimation."""
    
    def __init__(self):
        super().__init__()
        self.evaluator = dspy.Predict(CalibrateFindingSignature)

    async def calibrate(
        self,
        finding: Finding,
        evidence_context: str,
        num_samples: int = 10,  # Default to 10 for performance, user mentioned 40+
        temperature: float = 0.7
    ) -> float:
        """Estimate P(True) for a finding using multiple reasoning samples."""
        
        # We use a higher temperature to get diverse reasoning paths for self-consistency
        tasks = []
        for _ in range(num_samples):
            # In DSPy, we can override LM settings in a context
            with dspy.settings.context(lm=dspy.settings.lm.copy(temperature=temperature)):
                tasks.append(
                    self.evaluator.acall(
                        evidence=evidence_context,
                        finding_description=finding.description,
                        finding_evidence=finding.evidence
                    )
                )
        
        results = await asyncio.gather(*tasks)
        
        # Majority voting / P(True) estimation
        supported_count = sum(1 for r in results if r.is_supported)
        calibrated_confidence = supported_count / num_samples
        
        return calibrated_confidence

async def calibrate_analyses(
    analyses: List[Analysis],
    evidence_context: str,
    num_samples: int = 10
) -> List[Analysis]:
    """Calibrate all findings in a list of analyses."""
    calibrator = FindingCalibrator()
    
    for analysis in analyses:
        new_confidence = await calibrator.calibrate(
            analysis.findings,
            evidence_context,
            num_samples=num_samples
        )
        analysis.findings.confidence = new_confidence
        # We can also update recommendation confidence based on finding confidence
        analysis.recommendations.confidence = min(analysis.recommendations.confidence, new_confidence)
        
    return analyses
