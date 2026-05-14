import dspy
from typing import List, Optional
from deepfix_core.models import Analysis, Finding, Recommendation
from .signatures import PatchGenerationSignature

class PatchGenerator(dspy.Module):
    """
    Generates code patches based on analysis findings and recommendations.
    """
    def __init__(self):
        super().__init__()
        self.generate_patch = dspy.ChainOfThought(PatchGenerationSignature)

    def _cleanup_patch(self, patch: str) -> str:
        """Strips markdown code blocks from the generated patch."""
        if "```python" in patch:
            patch = patch.split("```python")[1].split("```")[0].strip()
        elif "```" in patch:
            patch = patch.split("```")[1].split("```")[0].strip()
        return patch

    async def aforward(self, findings: str, recommendations: str, code_context: str) -> str:
        """
        Asynchronously generates a patch.
        """
        response = await self.generate_patch.acall(
            findings=findings,
            recommendations=recommendations,
            code_context=code_context
        )
        return self._cleanup_patch(response.patch)

    def forward(self, findings: str, recommendations: str, code_context: str) -> str:
        """
        Generates a patch (diff or full code block) to fix the identified issues.
        """
        response = self.generate_patch(
            findings=findings,
            recommendations=recommendations,
            code_context=code_context
        )
        return self._cleanup_patch(response.patch)
