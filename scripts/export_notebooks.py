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
from typing import Iterable, List, Sequence, Tuple

import nbformat
from nbconvert import MarkdownExporter
from traitlets.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CUSTOM_TITLES = {
    "nlp": "NLP",
}


def setup_exporter() -> MarkdownExporter:
    """Configure and return a MarkdownExporter with figure extraction."""
    # Create configuration to enable ExtractOutputPreprocessor
    c = Config()
    c.MarkdownExporter.preprocessors = [
        "nbconvert.preprocessors.ExtractOutputPreprocessor"
    ]

    # Create exporter with the configuration
    exporter = MarkdownExporter(config=c)
    return exporter


def export_notebook(
    notebook_path: Path, output_dir: Path, exporter: MarkdownExporter
) -> bool:
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

            logger.info(
                f"  ✓ Extracted {len(resources['outputs'])} figure(s) to {output_files_dir}/"
            )
        else:
            logger.info("  ℹ No figures to extract")

        return True

    except Exception as e:
        logger.error(
            f"  ✗ Failed to export {notebook_path.name}: {e}", exc_info=True
        )
        return False


def humanize_title(stem: str) -> str:
    """Convert a filename stem to a human-friendly title."""
    normalized = stem.lower()
    if normalized in CUSTOM_TITLES:
        return CUSTOM_TITLES[normalized]
    return stem.replace("-", " ").replace("_", " ").title()


def find_getting_started_block(lines: Sequence[str]) -> Tuple[int, int]:
    """Locate the Getting Started nav block in mkdocs.yml."""
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("- Getting Started:"):
            indent_len = len(line) - len(line.lstrip())
            end_idx = idx + 1
            while end_idx < len(lines):
                next_line = lines[end_idx]
                if not next_line.strip():
                    end_idx += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent_len:
                    break
                end_idx += 1
            return idx, end_idx
    raise ValueError("Could not find 'Getting Started' section in mkdocs.yml")


def remove_existing_tutorial_block(block_lines: List[str]) -> List[str]:
    """Remove any existing Tutorials block from the Getting Started section."""
    filtered: List[str] = []
    i = 0
    while i < len(block_lines):
        line = block_lines[i]
        stripped = line.strip()
        indent_len = len(line) - len(line.lstrip())
        if stripped.startswith("- Tutorials:"):
            tutorial_indent = indent_len
            i += 1
            while i < len(block_lines):
                next_line = block_lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= tutorial_indent:
                    break
                i += 1
            continue
        filtered.append(line)
        i += 1
    return filtered


def update_getting_started_nav(
    mkdocs_path: Path, tutorial_paths: Iterable[Path]
) -> None:
    """Ensure the Getting Started nav includes the Tutorials subsection."""
    tutorial_entries: List[Tuple[str, str]] = []
    docs_dir = Path("docs").resolve()

    for tutorial_path in tutorial_paths:
        if not tutorial_path.exists():
            continue
        tutorial_path = tutorial_path.resolve()
        try:
            rel_path = tutorial_path.relative_to(docs_dir)
        except ValueError:
            logger.warning(
                "Skipping %s because it is not inside the docs/ directory",
                tutorial_path,
            )
            continue

        title = humanize_title(tutorial_path.stem)
        tutorial_entries.append((title, rel_path.as_posix()))

    if not tutorial_entries:
        logger.info("No tutorials found inside docs/; skipping mkdocs nav update")
        return

    mkdocs_lines = mkdocs_path.read_text(encoding="utf-8").splitlines()

    try:
        start_idx, end_idx = find_getting_started_block(mkdocs_lines)
    except ValueError as exc:
        logger.error("%s; skipping mkdocs nav update", exc)
        return

    block_lines = mkdocs_lines[start_idx + 1 : end_idx]
    block_lines = remove_existing_tutorial_block(block_lines)

    tutorial_block = ["    - Tutorials:"]
    for title, rel_path in sorted(tutorial_entries, key=lambda item: item[0]):
        tutorial_block.append(f"      - {title}: {rel_path}")

    updated_lines = (
        mkdocs_lines[: start_idx + 1]
        + block_lines
        + tutorial_block
        + mkdocs_lines[end_idx:]
    )
    mkdocs_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    logger.info("Updated Tutorials section in mkdocs.yml")


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
    exported_paths: List[Path] = []
    for notebook_path in sorted(notebook_files):
        if export_notebook(notebook_path, args.output_dir, exporter):
            success_count += 1
            exported_paths.append(args.output_dir / f"{notebook_path.stem}.md")

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info(
        f"Export complete: {success_count}/{len(notebook_files)} notebook(s) processed successfully"
    )
    logger.info("=" * 60)

    mkdocs_path = Path("mkdocs.yml")
    if mkdocs_path.exists():
        update_getting_started_nav(mkdocs_path, exported_paths)
    else:
        logger.warning("mkdocs.yml not found; skipping nav update")

    if success_count < len(notebook_files):
        sys.exit(1)


if __name__ == "__main__":
    main()

