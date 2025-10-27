"""
Deepchecks prompt builder for PromptBuilder.

This module provides the DeepchecksPromptBuilder for creating prompts
from DeepchecksArtifacts instances.
"""

from typing import Optional, Dict, Any,
from .base import BasePromptBuilder
from deepfix_core.models import (
    DeepchecksArtifacts,
    Artifacts,
)
from omegaconf import OmegaConf


class DeepchecksPromptBuilder(BasePromptBuilder):
    """Builds prompts for Deepchecks artifact analysis."""

    def can_build(self, artifact: Artifacts) -> bool:
        """Check if this builder can handle DeepchecksArtifacts."""
        return isinstance(artifact, DeepchecksArtifacts)

    def build_prompt(
        self,
        artifact: DeepchecksArtifacts,
        context: Optional[Dict[str, Any]] = None,
        exclude_fields_from_result: list[str] = ["value", "params", "link_in_summary"],
        exclude_empty_conditions_results: bool = True,
    ) -> str:

        """Build structured prompt from DeepchecksArtifacts."""
        prompt_parts = [
            f"Dataset: {artifact.dataset_name}",
            f"Validation checks performed: {sum(len(results) for results in artifact.results.values())}",
            f"Check types: {', '.join(artifact.results.keys())}",
        ]

        # Add configuration context if available
        if artifact.config:
            prompt_parts.append(f"\nValidation configuration:")
            prompt_parts.append(
                f"- Train-test validation: {artifact.config.train_test_validation}"
            )
            prompt_parts.append(
                f"- Data integrity checks: {artifact.config.data_integrity}"
            )
            prompt_parts.append(
                f"- Model evaluation: {artifact.config.model_evaluation}"
            )
            if artifact.config.max_samples:
                prompt_parts.append(f"- Max samples: {artifact.config.max_samples}")

        # Add results
        for k, v in artifact.results.items():
            prompt_parts.append(f"\n{k}:")
            for parsed_result in v:
                check_result = parsed_result.result
                if (
                    len(check_result.conditions_results) == 0
                    and exclude_empty_conditions_results
                ):
                    continue
                else:
                    prompt_parts.append(
                        f"- {OmegaConf.to_yaml(check_result.to_dict(exclude_fields_from_result), 
                        resolve=True)}"
                    )

        # Add context if provided
        if context:
            context_str = self._format_context(context)
            if context_str:
                prompt_parts.append(f"\nAdditional context:\n{context_str}")

        # Combine and truncate if necessary
        full_prompt = "\n".join(prompt_parts)
        return full_prompt
