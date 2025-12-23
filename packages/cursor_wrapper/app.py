import asyncio
import json
import os
import traceback
from enum import StrEnum
from typing import AsyncIterator

import litserve as ls
from fastapi import HTTPException
from litserve.specs.openai import ChatCompletionRequest
from pydantic import BaseModel, Field

INSTRUCTIONS = """"You are a helpful assitant that answer questions without looking at the codebase. You DO NOT WRITE CODE.\n\n"""


class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"


class CursorAgentConfig(BaseModel):
    output_format: str = Field(
        default=OutputFormat.TEXT.value,
        description="Output format to use for the Cursor agent",
    )
    model_name: str = Field(
        default="auto", description="Model name to use for the Cursor agent"
    )


async def run_cursor_agent_stream_async(
    prompt: str, model_name: str
) -> AsyncIterator[str]:
    """Async version of run_cursor_agent_stream using asyncio.create_subprocess_exec."""
    config = CursorAgentConfig(
        output_format=OutputFormat.STREAM_JSON.value,
        model_name=model_name,
    )
    args = [
        "cursor-agent",
        "-p",
        INSTRUCTIONS + prompt,
        "--output-format",
        config.output_format,
        "--model",
        config.model_name,
    ]

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        if process.stdout is None:
            raise RuntimeError("Failed to capture cursor-agent stdout")

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            line = line.decode().strip()
            if not line:
                continue
            try:
                line_data = json.loads(line)
                if line_data.get("subtype", "") == "init":
                    continue
                if line_data.get("type", "") == "user":
                    continue
                if line_data.get("type", "") == "assistant":
                    yield line_data["message"]["content"][-1]["text"]
            except Exception as e:
                print(f"Error parsing line: {line}")
                raise e

        await process.wait()
        if process.returncode != 0:
            stderr_data = (
                await process.stderr.read() if process.stderr is not None else b""
            )
            stderr_text = stderr_data.decode()
            raise RuntimeError(f"Cursor agent failed to run: {stderr_text}")
    finally:
        try:
            process.kill()
        except Exception:
            pass


class CursorAgentAPI(ls.LitAPI):
    """Analyse Artifacts API."""

    def setup(self, device):
        if os.getenv("CURSOR_API_KEY") is None:
            raise HTTPException(
                status_code=500,
                detail="CURSOR_API_KEY is not set in the environment file",
            )
        if os.getenv("CURSOR_MODEL_NAME") is None:
            raise HTTPException(
                status_code=500,
                detail="CURSOR_MODEL_NAME is not set in the environment file",
            )
        self.model_name = os.getenv("CURSOR_MODEL_NAME")
        return

    async def predict(self, request: ChatCompletionRequest):
        try:
            prompt = request.messages[-1].content
            async for content in run_cursor_agent_stream_async(
                prompt=prompt, model_name=self.model_name
            ):
                yield content
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail=f"Error running cursor agent: {str(e)}"
            )


def run_cursor_agent_api(
    port: int = 8841, host: str = "0.0.0.0", fast_queue: bool = False
):
    server = ls.LitServer(
        CursorAgentAPI(spec=ls.OpenAISpec(), enable_async=True), fast_queue=fast_queue
    )
    server.run(
        host=host,
        port=port,
        generate_client_file=False,
        pretty_logs=True,
    )


if __name__ == "__main__":
    run_cursor_agent_api()
