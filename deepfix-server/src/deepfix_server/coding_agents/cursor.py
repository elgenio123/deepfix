from pydantic import BaseModel, Field
import subprocess
import asyncio
from enum import StrEnum
import json
from typing import Iterator, AsyncIterator, Union

class ModelName(StrEnum):
    GPT_5 = "gpt-5"
    DEEPSEEK_V3 = "deepseek-v3.1"
    AUTO = "auto"

class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"


class CursorAgentConfig(BaseModel):
    output_format: str = Field(default=OutputFormat.TEXT.value,description="Output format to use for the Cursor agent")
    model_name: str = Field(default="auto",description="Model name to use for the Cursor agent")


INSTRUCTIONS = """"You are a helpful assitant that answer questions without looking at the codebase. You DO NOT WRITE CODE.\n\n"""

class CursorAgent:

    def __init__(self, output_format:str, model_name:str):
        self.config = CursorAgentConfig(
            output_format=OutputFormat(output_format).value,
            model_name=model_name,
        )

    def run(self, prompt:str) -> str:
        args = ["cursor-agent", 
                "-p", INSTRUCTIONS + prompt, 
                "--output-format", self.config.output_format, 
                "--model", self.config.model_name
            ]
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Cursor agent failed to run: {e.stderr}") from e


def run_cursor_agent_stream(prompt:str, model_name:str) -> Iterator[str]:
    config = CursorAgentConfig(
        output_format=OutputFormat.STREAM_JSON.value,
        model_name=model_name,
    )
    args = [
        "cursor-agent",
        "-p", INSTRUCTIONS + prompt,
        "--output-format", config.output_format,
        "--model", config.model_name,
    ]

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    try:
        if process.stdout is None:
            raise RuntimeError("Failed to capture cursor-agent stdout")
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                line = json.loads(line)
                if line.get("subtype","") == "init":
                    continue
                if line.get("type","") == "user":
                    continue
                if line.get("type","") == "assistant":
                    yield line['message']['content'][-1]['text']
            except Exception as e:
                print(f"Error parsing line: {line}")
                raise e

        process.wait()
        if process.returncode != 0:
            stderr_text = process.stderr.read() if process.stderr is not None else ""
            raise RuntimeError(f"Cursor agent failed to run: {stderr_text}")
    finally:
        try:
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
        except Exception:
            pass


async def run_cursor_agent_stream_async(prompt: str, model_name: str) -> AsyncIterator[str]:
    """Async version of run_cursor_agent_stream using asyncio.create_subprocess_exec."""
    config = CursorAgentConfig(
        output_format=OutputFormat.STREAM_JSON.value,
        model_name=model_name,
    )
    args = [
        "cursor-agent",
        "-p", INSTRUCTIONS + prompt,
        "--output-format", config.output_format,
        "--model", config.model_name,
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
                    yield line_data['message']['content'][-1]['text']
            except Exception as e:
                print(f"Error parsing line: {line}")
                raise e

        await process.wait()
        if process.returncode != 0:
            stderr_data = await process.stderr.read() if process.stderr is not None else b""
            stderr_text = stderr_data.decode()
            raise RuntimeError(f"Cursor agent failed to run: {stderr_text}")
    finally:
        try:
            process.kill()
        except Exception:
            pass