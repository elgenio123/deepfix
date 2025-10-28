import typer
import os
from typing import Optional
import sys
from dotenv import load_dotenv

from .api import run_analyse_artifacts_api

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
        "127.0.0.1", "-host", help="Host to bind DeepFix server to"
    ),
    env_file: Optional[str] = typer.Option(
        None, "-e", "--env-file", help="Environment file to load"
    ),
) -> None:
    """Launch DeepFix server."""

    if env_file is not None:
        if not os.path.exists(env_file):
            typer.echo(f"❌ Environment file {env_file} not found", err=True)
            sys.exit(1)
        load_dotenv(env_file)

    typer.echo(f"🚀 Starting DeepFix server on {host}:{port}")

    run_analyse_artifacts_api(port=port, host=host)


def main():
    app()
