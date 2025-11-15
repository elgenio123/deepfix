import traceback

import litserve as ls
from deepfix_core.models import APIRequest, APIResponse
from fastapi import HTTPException

from .config import LLMConfig
from .coordinators import ArtifactAnalysisCoordinator
from .logging import get_logger, setup_dspy_logging
from .models import AgentContext

LOGGER = get_logger(__name__)


# Analyse Artifacts API
class AnalyseArtifactsAPI(ls.LitAPI):
    """Analyse Artifacts API."""

    def setup(self, device):
        try:
            setup_dspy_logging()
        except Exception:
            print(f"Error setting up DSPy logging: {traceback.format_exc()}")

        llm_config = LLMConfig.load_from_env()
        self.coordinator = ArtifactAnalysisCoordinator(llm_config=llm_config)

    def decode_request(self, request: APIRequest):
        try:
            return AgentContext(
                dataset_artifacts=request.dataset_artifacts,
                training_artifacts=request.training_artifacts,
                deepchecks_artifacts=request.deepchecks_artifacts,
                model_checkpoint_artifacts=request.model_checkpoint_artifacts,
                dataset_name=request.dataset_name,
                language=request.language,
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error decoding request: {e}",
            )

    def predict(self, request_ctx: AgentContext) -> APIResponse:
        try:
            results = self.coordinator.run(request_ctx)
            response = APIResponse(
                agent_results=results.get_agent_results(),
                summary=results.summary,
                additional_outputs=results.additional_outputs,
                error_messages=results.get_error_messages(),
                dataset_name=request_ctx.dataset_name,
            )
            return response
        except Exception:
            raise HTTPException(status_code=500, detail=traceback.format_exc())


def run_analyse_artifacts_api(
    port: int = 4141,
    host: str = "0.0.0.0",
    workers_per_device: int = 1,
    fast_queue: bool = False,
):
    server = ls.LitServer(
        AnalyseArtifactsAPI(api_path="/v1/analyse"),
        workers_per_device=workers_per_device,
        fast_queue=fast_queue,
    )
    server.run(
        host=host,
        port=port,
        generate_client_file=False,
        pretty_logs=True,
    )
