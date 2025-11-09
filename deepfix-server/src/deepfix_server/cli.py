import typer
import os
from typing import Optional
import sys
from dotenv import load_dotenv

from .api import run_analyse_artifacts_api
from .coding_agents.openai_api import run_openai_api

app = typer.Typer(
    name="deepfix-server",
    help="DeepFix server for artifact analysis and diagnosis",
    add_completion=False,
)


@app.command(name="version")
def version() -> None:
    """Print the version of the DeepFix Server."""
    typer.echo(f"DeepFix Server version: 0.1.0")


@app.command(name="launch")
def launch(
    port: int = typer.Option(8844, "-port", help="Port to run DeepFix server on"),
    host: str = typer.Option(
        "0.0.0.0", "-host", help="Host to bind DeepFix server to"
    ),
    env_file: Optional[str] = typer.Option(
        None, "-e", "--env-file", help="Environment file to load"
    ),
    workers_per_device: int = typer.Option(1, "-workers", help="Workers per device"),
    fast_queue: bool = typer.Option(False, "-fast-queue", help="Fast queue"),
) -> None:
    """Launch DeepFix server."""

    if env_file is not None:
        if not os.path.exists(env_file):
            typer.echo(f"❌ Environment file {env_file} not found", err=True)
            sys.exit(1)
        load_dotenv(env_file)

    typer.echo(f"🚀 Starting DeepFix server on {host}:{port}")

    run_analyse_artifacts_api(port=port, host=host, workers_per_device=workers_per_device, fast_queue=fast_queue)

@app.command(name="launch-cursor-agent")
def launch_cursor_agent_api(port:int=typer.Option(8841, "-port", help="Port to run Cursor Agent API on"), 
                            host:str=typer.Option("0.0.0.0", "-host", help="Host to bind Cursor Agent API to"), 
                            fast_queue:bool=typer.Option(False, "-fast-queue", help="Fast queue"),
                            env_file: Optional[str] = typer.Option(
        None, "-e", "--env-file", help="Environment file to load"
    ),
                        ):
    """Launch Cursor Agent API."""
    if env_file is not None:
        if not os.path.exists(env_file):
            typer.echo(f"❌ Environment file {env_file} not found", err=True)
            sys.exit(1)
        load_dotenv(env_file)
    
    if os.getenv("CURSOR_API_KEY") is None:
        typer.echo(f"❌ CURSOR_API_KEY is not set in the environment file", err=True)
        sys.exit(1)

    typer.echo(f"🚀 Starting Cursor Agent API on {host}:{port}")
    run_openai_api(port=port, host=host, fast_queue=fast_queue)

def main():
    app()
