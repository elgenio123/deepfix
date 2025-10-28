import litserve as ls
from fastapi import HTTPException
import traceback

from deepfix_core.models import APIRequest, APIResponse

from .coordinators import ArtifactAnalysisCoordinator
from .models import AgentContext
from .config import LLMConfig
from .logging import get_logger

LOGGER = get_logger(__name__)


# Analyse Artifacts API
class AnalyseArtifactsAPI(ls.LitAPI):
    """Analyse Artifacts API."""

    def setup(self, device):
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=traceback.format_exc())


def run_analyse_artifacts_api(port=4141, host="0.0.0.0"):
    server = ls.LitServer(AnalyseArtifactsAPI(api_path="/v1/analyse"))
    server.run(
        host=host,
        port=port,
        generate_client_file=False,
        pretty_logs=True,
    )
