import litserve as ls
from litserve.specs.openai import ChatCompletionRequest
from fastapi import HTTPException
import traceback
from pydantic import BaseModel
import os

from .cursor import run_cursor_agent_stream_async #,run_cursor_agent_stream


class OpenAIApiRequest(BaseModel):
    model: str
    messages: list[dict]
    stream: bool = False
    

class OpenAIApi(ls.LitAPI):
    """Analyse Artifacts API."""

    def setup(self, device):
        if os.getenv("CURSOR_API_KEY") is None:
            raise HTTPException(status_code=500, detail=f"CURSOR_API_KEY is not set in the environment file")
        return

    async def predict(self, request: ChatCompletionRequest):
        try:
            #print(request.model_dump_json(indent=2))
            prompt = request.messages[-1].content
            model = request.model or "auto"
            async for content in run_cursor_agent_stream_async(prompt=prompt, model_name=model):
                yield content
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error running cursor agent: {str(e)}")


def run_openai_api(port:int=4141, host:str="0.0.0.0", fast_queue:bool=False):
    server = ls.LitServer(OpenAIApi(spec=ls.OpenAISpec(),
                                    enable_async=True
                                ), 
                          fast_queue=fast_queue
                        )
    server.run(
        host=host,
        port=port,
        generate_client_file=False,
        pretty_logs=True,
    )