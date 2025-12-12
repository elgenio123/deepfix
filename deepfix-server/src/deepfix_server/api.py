import traceback

import litserve as ls
from deepfix_core.models import APIRequest, APIResponse, DatasetArtifacts
from fastapi import HTTPException
import os

from .config import LLMConfig
from .coordinators import ArtifactAnalysisCoordinator
from .logging import get_logger, setup_dspy_logging
from .models import AgentContext

LOGGER = get_logger(__name__)


# Analyse Artifacts API
class AnalyseArtifactsAPI(ls.LitAPI):
    """API endpoint for artifact analysis.

    Provides a LitServe API for analyzing ML artifacts (datasets, training,
    deepchecks, model checkpoints) and returning diagnostic results.
    """

    def _ensure_initialized(self) -> None:
        """Initialize dependencies if setup has not run."""
        if (
            getattr(self, "portal_client", None) is not None
            and getattr(self, "coordinator", None) is not None
        ):
            return

        self.llm_config = LLMConfig.load_from_env()
        self.coordinator = ArtifactAnalysisCoordinator(llm_config=self.llm_config)

    def setup(self, device: str) -> None:
        """Setup the API endpoint.

        Initializes logging and creates the artifact analysis coordinator.

        Args:
            device: Device specification (unused, kept for LitAPI compatibility).
        """
        if os.getenv("MLFLOW_EXP_NAME") and os.getenv("MLFLOW_TRACKING_URI"):
            setup_dspy_logging(
                experiment_name=os.getenv("MLFLOW_EXP_NAME"),
                tracking_uri=os.getenv("MLFLOW_TRACKING_URI"),
            )
        else:
            print(f"Error setting up DSPy logging: {traceback.format_exc()}")

        self._ensure_initialized()

    async def decode_request(self, request: APIRequest) -> AgentContext:
        """Decode API request into AgentContext.

        Args:
            request: APIRequest containing artifacts and configuration.

        Returns:
            AgentContext with artifacts and settings.

        Raises:
            HTTPException: If request decoding fails (status 400).
        """
        try:
            dataset_artifacts = request.dataset_artifacts
            if isinstance(request.dataset_artifacts, dict):
                dataset_artifacts = DatasetArtifacts.from_dict(
                    request.dataset_artifacts
                )
            elif not isinstance(request.dataset_artifacts, DatasetArtifacts):
                raise ValueError("Dataset artifacts must be a DatasetArtifacts object")
            return AgentContext(
                dataset_artifacts=dataset_artifacts,
                training_artifacts=request.training_artifacts,
                deepchecks_artifacts=request.deepchecks_artifacts,
                model_checkpoint_artifacts=request.model_checkpoint_artifacts,
                dataset_name=request.dataset_name,
                language=request.language,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Error decoding request: {exc}",
            ) from exc

    async def predict(self, request_ctx: AgentContext) -> APIResponse:
        """Run artifact analysis and return results.

        Args:
            request_ctx: AgentContext containing artifacts to analyze.

        Returns:
            APIResponse with analysis results from all agents.

        Raises:
            HTTPException: If analysis fails (status 500).
        """
        try:
            results = await self.coordinator.run(request_ctx)
            response = APIResponse(
                agent_results=results.get_agent_results(),
                summary=results.summary,
                additional_outputs=results.additional_outputs,
                error_messages=results.get_error_messages(),
                dataset_name=request_ctx.dataset_name,
            )
            return response
        except Exception as exc:
            raise HTTPException(status_code=500, detail=traceback.format_exc()) from exc


def run_analyse_artifacts_api(
    port: int = 4141,
    host: str = "0.0.0.0",
    workers_per_device: int = 1,
    fast_queue: bool = False,
):
    """Run the artifact analysis API server.

    Args:
        port: Port number to listen on. Defaults to 4141.
        host: Host address to bind to. Defaults to "0.0.0.0".
        workers_per_device: Number of workers per device. Defaults to 1.
        fast_queue: Enable fast queue mode. Defaults to False.
    """

    server = ls.LitServer(
        AnalyseArtifactsAPI(api_path="/api/v1/analyse", enable_async=True),
        workers_per_device=workers_per_device,
        fast_queue=fast_queue,
    )

    server.run(
        host=host,
        port=port,
        generate_client_file=False,
        pretty_logs=True,
    )
