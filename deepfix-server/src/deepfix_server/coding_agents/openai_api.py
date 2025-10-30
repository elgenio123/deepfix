import litserve as ls
from fastapi import HTTPException
import traceback
from pydantic import BaseModel
from .cursor import run_cursor_agent_stream


class OpenAIApiRequest(BaseModel):
    model: str
    messages: list[dict]
    stream: bool = False
    

class OpenAIApi(ls.LitAPI):
    """Analyse Artifacts API."""

    def setup(self, device):
        return

    def decode_request(self, request: OpenAIApiRequest)->dict:
        try:
            model = request.model
            messages = request.messages
            prompt = messages[-1]["content"]

            return {
                "model": model,
                "prompt": prompt,
                "stream": request.stream,
            }
        except Exception:
            raise HTTPException(status_code=400, detail=traceback.format_exc())

    def predict(self, req_ctx: dict):
        try:
            model = req_ctx["model"]
            prompt = req_ctx["prompt"]
            for content in run_cursor_agent_stream(prompt=prompt, model_name=model):
                yield content
        
        except Exception:
            raise HTTPException(status_code=500, detail=traceback.format_exc())


def run_openai_api(port:int=4141, host:str="0.0.0.0", fast_queue:bool=False):
    server = ls.LitServer(OpenAIApi(spec=ls.OpenAISpec()), fast_queue=fast_queue)
    server.run(
        host=host,
        port=port,
        generate_client_file=False,
        pretty_logs=True,
    )