# Development Guide

This guide covers the development setup, practices, and workflows for contributing to DeepFix.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`
- Git
- Code editor (VS Code, PyCharm, etc.)

### Initial Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/delcaux-labs/deepfix.git
   cd deepfix
   ```

2. **Create Virtual Environment**:
   ```bash
   uv venv --python 3.11
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   ```

4. **Install Development Tools**:
   ```bash
   uv pip install ruff mypy pytest pytest-cov
   ```

## Project Structure

```
deepfix/
├── deepfix-core/          # Core models and types
│   └── src/
│       └── deepfix_core/
├── deepfix-sdk/           # Client SDK
│   └── src/
│       └── deepfix_sdk/
├── deepfix-server/        # Analysis server
│   └── src/
│       └── deepfix_server/
├── deepfix-kb/            # Knowledge base
│   └── src/
│       └── deepfix_kb/
├── docs/                  # Documentation
├── tests/                 # Test suite
├── specs/                 # Architecture specifications
└── pyproject.toml         # Root project config
```

## Development Workflows

### Making Changes

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes**: Edit code in appropriate package

3. **Test Changes**:
   ```bash
   uv run pytest
   uv run ruff check .
   ```

4. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### Working on SDK

```bash
# Navigate to SDK
cd deepfix-sdk

# Install in editable mode
uv pip install -e .

# Make changes to src/deepfix_sdk/
# Test changes
uv run pytest tests/

# Reinstall if needed
uv pip install -e .
```

### Working on Server

```bash
# Navigate to server
cd deepfix-server

# Install in editable mode
uv pip install -e .

# Configure environment
cp env.example .env
# Edit .env with your configuration

# Make changes to src/deepfix_server/
# Test changes
uv run deepfix-server launch -e .env

# Test with client
python -c "from deepfix_sdk.client import DeepFixClient; client = DeepFixClient(); ..."
```

### Working on Core

```bash
# Navigate to core
cd deepfix-core

# Install in editable mode
uv pip install -e .

# Make changes to src/deepfix_core/
# Test by running SDK or server tests
cd ../deepfix-sdk
uv run pytest
```

## Code Quality

### Formatting

Use `ruff` for code formatting:

```bash
# Format all code
uv run ruff format .

# Format specific directory
uv run ruff format deepfix-sdk/src
```

### Linting

Use `ruff` for linting:

```bash
# Lint all code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Lint specific directory
uv run ruff check deepfix-sdk/src
```

### Type Checking

Use `mypy` for type checking:

```bash
# Type check all packages
uv run mypy deepfix-core/src deepfix-sdk/src deepfix-server/src

# Type check specific package
uv run mypy deepfix-sdk/src
```

### Pre-commit Hooks

Set up pre-commit hooks (optional):

```bash
# Install pre-commit
uv pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_client.py

# Run specific test
uv run pytest tests/test_client.py::test_client_initialization

# Run with coverage
uv run pytest --cov=deepfix_sdk --cov=deepfix_server --cov-report=html

# Run in verbose mode
uv run pytest -v
```

### Writing Tests

```python
import pytest
from deepfix_sdk.client import DeepFixClient

def test_client_initialization():
    """Test DeepFixClient initialization."""
    client = DeepFixClient(api_url="http://localhost:8844")
    assert client.api_url == "http://localhost:8844"
    assert client.timeout == 30

def test_client_with_custom_timeout():
    """Test client with custom timeout."""
    client = DeepFixClient(
        api_url="http://localhost:8844",
        timeout=60
    )
    assert client.timeout == 60

@pytest.fixture
def mock_server():
    """Fixture for mock server."""
    # Setup
    server = start_mock_server()
    yield server
    # Teardown
    server.stop()
```

### Test Organization

- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test full workflows

## Documentation

### Code Documentation

Document all public APIs:

```python
def process_dataset(
    dataset_name: str,
    batch_size: int = 8
) -> Dict[str, Any]:
    """Process dataset and return results.

    This function processes a dataset and returns analysis results.

    Args:
        dataset_name: Name of the dataset to process
        batch_size: Batch size for processing. Defaults to 8.

    Returns:
        Dictionary containing:
            - results: Analysis results
            - metadata: Processing metadata

    Raises:
        ValueError: If dataset_name is invalid
        FileNotFoundError: If dataset not found

    Example:
        >>> result = process_dataset("my-dataset", batch_size=16)
        >>> print(result["results"])
    """
    pass
```

### Documentation Build

```bash
# Build documentation
uv run mkdocs build

# Serve documentation locally
uv run mkdocs serve

# Build with strict mode
uv run mkdocs build --strict
```

## Debugging

### Debugging Server

```bash
# Run server with debug logging
DEEPFIX_LOG_LEVEL=DEBUG uv run deepfix-server launch -e .env

# Use Python debugger
import pdb; pdb.set_trace()
```

### Debugging SDK

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

from deepfix_sdk.client import DeepFixClient
client = DeepFixClient(...)
```

### Debugging with IDE

- **VS Code**: Use Python debugger
- **PyCharm**: Use built-in debugger
- **Vim/Emacs**: Use `pdb` or `ipdb`

## Performance

### Profiling

```python
import cProfile
import pstats

# Profile code
profiler = cProfile.Profile()
profiler.enable()

# Your code here
client.diagnose_dataset("my-dataset")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

### Benchmarking

```python
import time

start = time.time()
result = client.diagnose_dataset("my-dataset")
end = time.time()

print(f"Time taken: {end - start:.2f} seconds")
```

## Version Management

### Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Updating Versions

```bash
# Update version in pyproject.toml
# deepfix-core/pyproject.toml
# deepfix-sdk/pyproject.toml
# deepfix-server/pyproject.toml
```

## CI/CD

### GitHub Actions

Tests run automatically on:

- Pull requests
- Pushes to main branch
- Manual workflow dispatch

### Local CI Checks

Run CI checks locally:

```bash
# Run all checks
uv run pytest
uv run ruff check .
uv run mypy deepfix-sdk/src deepfix-server/src

# Or use script
./scripts/check.sh
```

## Common Tasks

### Adding New Feature

1. Create feature branch
2. Implement feature
3. Add tests
4. Update documentation
5. Submit pull request

### Fixing Bug

1. Create fix branch
2. Write failing test
3. Fix bug
4. Verify test passes
5. Submit pull request

### Refactoring

1. Create refactor branch
2. Refactor code
3. Ensure tests pass
4. Update documentation
5. Submit pull request

## Troubleshooting

### Import Errors

```bash
# Reinstall packages
uv pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Test Failures

```bash
# Run tests in verbose mode
uv run pytest -v

# Run specific test
uv run pytest tests/test_specific.py -v

# Check test output
uv run pytest --tb=long
```

### Type Check Errors

```bash
# Check type errors
uv run mypy deepfix-sdk/src --show-error-codes

# Ignore specific errors (if necessary)
# type: ignore[error-code]
```

## Next Steps

- [Contributing Guidelines](guidelines.md) - Contribution process
- [Code Style](#code-quality) - Coding standards
- [Testing](#testing) - Testing practices
- [Documentation](#documentation) - Documentation guide
