import asyncio
import traceback
from typing import List, Optional

from deepfix_core.models import Artifacts
from concurrent.futures import ThreadPoolExecutor
from .agents.artifact_analyzers import (
    DatasetArtifactsAnalyzer,
    DeepchecksArtifactsAnalyzer,
    ModelCheckpointArtifactsAnalyzer,
)
from .agents.base import Agent, ArtifactAnalyzer
from .agents.cross_artifact_reasoning import CrossArtifactReasoningAgent
from .config import LLMConfig
from .logging import get_logger
from .models import AgentContext, AgentResult, ArtifactAnalysisResult

LOGGER = get_logger(__name__)


class ArtifactAnalysisCoordinator(Agent):
    """Main orchestrator that coordinates specialized analyzer agents."""

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
    ):
        super().__init__(config=config)

        # initialize agents and loaders
        self.analyzer_agents = self._initialize_analyzer_agents()
        self.cross_artifact_reasoning_agent = CrossArtifactReasoningAgent(
            llm_config=self._llm_config
        )

    async def _analyze_one_artifact(self, artifact: Artifacts) -> AgentResult:
        agent_name = None
        try:
            analyzer_agent = self._get_analyzer_agent(artifact)
            agent_name = analyzer_agent.agent_name
            if analyzer_agent:
                focused_context = self._create_focused_context(artifact)
                result = await analyzer_agent.arun(focused_context)
                return result
        except Exception as e:
            LOGGER.error(f"Error with agent {agent_name}:\n {traceback.format_exc()}")
            raise e

    async def aforward(self, context: AgentContext) -> ArtifactAnalysisResult:
        """Analyze artifacts asynchronously and return results.

        Args:
            context: Agent context containing artifacts and configuration.

        Returns:
            ArtifactAnalysisResult containing analysis results from all agents.
        """
        # 1. Analyze artifacts
        LOGGER.info(
            f"Analyzing {len(context.artifacts)} artifacts linked to dataset {context.dataset_name}..."
        )
        results = await asyncio.gather(
            *[self._analyze_one_artifact(artifact) for artifact in context.artifacts]
        )
        for result in results:
            context.agent_results[result.agent_name] = result

        # 2. Cross-artifact reasoning
        LOGGER.info("Cross-artifact reasoning...")
        out = await self.cross_artifact_reasoning_agent.arun(
            previous_analyses=context.agent_results, output_language=context.language
        )
        context.agent_results[out.agent_name] = out

        # 3. Output results
        output = ArtifactAnalysisResult(
            context=context,
            summary=out.additional_outputs.get("summary", None),
        )
        return output

    async def arun(self, context: AgentContext) -> ArtifactAnalysisResult:
        """Run the coordinator asynchronously with error handling.

        Args:
            context: Agent context containing artifacts and configuration.

        Returns:
            ArtifactAnalysisResult with analysis results or error message if execution fails.
        """
        try:
            return await self.acall(context)
        except Exception as e:
            LOGGER.error(
                f"Error with coordinator {self.agent_name}:\n {traceback.format_exc()}"
            )
            error_result = AgentResult(agent_name=self.agent_name, error_message=str(e))
            context.agent_results[self.agent_name] = error_result
            return ArtifactAnalysisResult(
                context=context,
                summary=None,
            )

    def run(self, context: AgentContext) -> ArtifactAnalysisResult:
        """Run the coordinator (alias for arun for backward compatibility).

        Args:
            context: Agent context containing artifacts and configuration.

        Returns:
            ArtifactAnalysisResult containing analysis results from all agents.
        """
        try:
            return self(context)
        except Exception as e:
            LOGGER.error(
                f"Error with coordinator {self.agent_name}:\n {traceback.format_exc()}"
            )
            error_result = AgentResult(agent_name=self.agent_name, error_message=str(e))
            context.agent_results[self.agent_name] = error_result
            return ArtifactAnalysisResult(
                context=context,
                summary=None,
            )

    def _get_analyzer_agent(self, artifact: Artifacts) -> ArtifactAnalyzer:
        for analyzer_agent in self.analyzer_agents:
            if analyzer_agent.supports_artifact(artifact):
                return analyzer_agent
        raise ValueError(
            f"No analyzer agent found for artifact of type: {type(artifact)}"
        )

    def _create_focused_context(self, artifact: Artifacts) -> AgentContext:
        ctx = AgentContext()
        ctx.insert_artifact(artifact)
        return ctx

    def forward(self, context: AgentContext) -> ArtifactAnalysisResult:
        # 1. Analyze artifacts
        LOGGER.info(
            f"Analyzing {len(context.artifacts)} artifacts linked to dataset {context.dataset_name}..."
        )
        with ThreadPoolExecutor(max_workers=len(context.artifacts)) as executor:
            results = list(executor.map(self._analyze_one_artifact, context.artifacts))
        for result in results:
            context.agent_results[result.agent_name] = result

        # 2. Cross-artifact reasoning
        LOGGER.info("Cross-artifact reasoning...")
        out = self.cross_artifact_reasoning_agent.run(
            previous_analyses=context.agent_results, output_language=context.language
        )
        context.agent_results[out.agent_name] = out

        # 3. Output results
        output = ArtifactAnalysisResult(
            context=context,
            summary=out.additional_outputs.get("summary", None),
        )
        return output

    def _initialize_analyzer_agents(self) -> List[ArtifactAnalyzer]:
        """Initialize specialized analyzer agents"""
        agents = [
            DeepchecksArtifactsAnalyzer(config=self._llm_config),
            DatasetArtifactsAnalyzer(config=self._llm_config),
            ModelCheckpointArtifactsAnalyzer(config=self._llm_config),
        ]
        return agents
