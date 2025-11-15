import json
from typing import Any, Dict, Optional

from deepfix_core.models import (
    Artifacts,
    ModelCheckpointArtifacts,
)

from .base import BasePromptBuilder


class CheckpointPromptBuilder(BasePromptBuilder):
    """Builds prompts for training artifact analysis."""

    def can_build(self, artifact: Artifacts) -> bool:
        """Check if this builder can handle TrainingArtifacts."""
        return isinstance(artifact, ModelCheckpointArtifacts)

    def build_prompt(
        self,
        artifact: ModelCheckpointArtifacts,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build structured prompt from TrainingArtifacts."""
        prompt_parts = []
        if artifact.path is not None:
            prompt_parts.append(f"\nModel checkpoint path: {artifact.path}")
        if artifact.config is not None:
            prompt_parts.append(
                f"\nModel checkpoint config: {json.dumps(artifact.config, indent=2)}"
            )
        if artifact.model_type is not None:
            prompt_parts.append(f"\nModel type: {artifact.model_type}")
        if artifact.hyperparameters:
            prompt_parts.append(
                f"\nModel hyperparameters: {json.dumps(artifact.hyperparameters, indent=2)}"
            )
        if artifact.context:
            context_str = self._format_context(artifact.context)
            if context_str:
                prompt_parts.append(f"\nContext:\n{context_str}")

        if context:
            context_str = self._format_context(context)
            if context_str:
                prompt_parts.append(f"\nAdditional context:\n{context_str}")

        # Combine and truncate if necessary
        full_prompt = "\n".join(prompt_parts)
        return full_prompt
