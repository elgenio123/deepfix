#!/usr/bin/env python3
"""
Export Jupyter notebooks to Markdown for MkDocs.

This script converts all .ipynb files from the tutorials/ directory
to Markdown files in docs/tutorials/ using nbconvert with figure extraction.
"""

import argparse
import logging
import sys
from pathlib import Path

import nbformat
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExtractOutputPreprocessor
from traitlets.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def setup_exporter() -> MarkdownExporter:
    """Configure and return a MarkdownExporter with figure extraction."""
    # Create configuration to enable ExtractOutputPreprocessor
    c = Config()
    c.MarkdownExporter.preprocessors = ["nbconvert.preprocessors.ExtractOutputPreprocessor"]

    # Create exporter with the configuration
    exporter = MarkdownExporter(config=c)
    return exporter


def export_notebook(notebook_path: Path, output_dir: Path, exporter: MarkdownExporter) -> bool:
    """
    Export a single notebook to Markdown.

    Args:
        notebook_path: Path to the input .ipynb file
        output_dir: Directory where output .md file should be written
        exporter: Configured MarkdownExporter instance

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing {notebook_path.name}...")

        # Read the notebook
        with open(notebook_path, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

        # Convert to Markdown
        (body, resources) = exporter.from_notebook_node(notebook)

        # Determine output paths
        notebook_stem = notebook_path.stem
        output_md_path = output_dir / f"{notebook_stem}.md"
        output_files_dir = output_dir / f"{notebook_stem}_files"

        # Write Markdown file
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(body)

        logger.info(f"  ✓ Wrote {output_md_path}")

        # Write extracted figures if any
        if "outputs" in resources and resources["outputs"]:
            output_files_dir.mkdir(parents=True, exist_ok=True)
            for filename, data in resources["outputs"].items():
                output_file_path = output_files_dir / filename
                with open(output_file_path, "wb") as f:
                    f.write(data)
                logger.info(f"  ✓ Extracted {filename}")

            logger.info(f"  ✓ Extracted {len(resources['outputs'])} figure(s) to {output_files_dir}/")
        else:
            logger.info("  ℹ No figures to extract")

        return True

    except Exception as e:
        logger.error(f"  ✗ Failed to export {notebook_path.name}: {e}", exc_info=True)
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Export Jupyter notebooks to Markdown for MkDocs"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("tutorials"),
        help="Directory containing input .ipynb files (default: tutorials/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/tutorials"),
        help="Directory for output .md files (default: docs/tutorials/)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input directory
    if not args.input_dir.exists():
        logger.error(f"Input directory does not exist: {args.input_dir}")
        sys.exit(1)

    if not args.input_dir.is_dir():
        logger.error(f"Input path is not a directory: {args.input_dir}")
        sys.exit(1)

    # Find all .ipynb files
    notebook_files = list(args.input_dir.glob("*.ipynb"))

    if not notebook_files:
        logger.warning(f"No .ipynb files found in {args.input_dir}")
        sys.exit(0)

    logger.info(f"Found {len(notebook_files)} notebook(s) to process")
    logger.info(f"Output directory: {args.output_dir}")

    # Setup exporter
    exporter = setup_exporter()

    # Process each notebook
    success_count = 0
    for notebook_path in sorted(notebook_files):
        if export_notebook(notebook_path, args.output_dir, exporter):
            success_count += 1

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Export complete: {success_count}/{len(notebook_files)} notebook(s) processed successfully")
    logger.info("=" * 60)

    if success_count < len(notebook_files):
        sys.exit(1)


if __name__ == "__main__":
    main()

