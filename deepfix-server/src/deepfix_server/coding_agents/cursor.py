from pydantic import BaseModel, Field
import subprocess
from enum import StrEnum
import json
from typing import Iterator, Union

class ModelName(StrEnum):
    GPT_4o = "gpt-4o"
    GPT_5 = "gpt-5"
    DEEPSEEK_V3 = "deepseek-v3"

class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"


class CursorAgentConfig(BaseModel):
    output_format: str = Field(default=OutputFormat.TEXT.value,description="Output format to use for the Cursor agent")
    model_name: str = Field(default=ModelName.DEEPSEEK_V3.value,description="Model name to use for the Cursor agent")


class CursorAgent:

    def __init__(self, output_format:str, model_name:str):
        self.config = CursorAgentConfig(
            output_format=OutputFormat(output_format).value,
            model_name=ModelName(model_name).value,
        )

    def run(self, prompt:str) -> str:
        args = ["cursor-agent", 
                "-p", prompt, 
                "--output-format", self.config.output_format, 
                "--model", self.config.model_name
            ]
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Cursor agent failed to run: {e.stderr}") from e


def run_cursor_agent_stream(prompt:str, model_name:Union[str, ModelName]) -> Iterator[str]:
    config = CursorAgentConfig(
        output_format=OutputFormat.STREAM_JSON.value,
        model_name=ModelName(model_name).value,
    )
    args = [
        "cursor-agent",
        "-p", prompt,
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
                yield line["content"]
            except json.JSONDecodeError:
                yield line["content"]
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