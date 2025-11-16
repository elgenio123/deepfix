# Local Setup

This guide covers setting up DeepFix for local development and testing.

## Overview

Local setup is recommended for development, testing, and experimentation. This guide provides step-by-step instructions for setting up DeepFix on your local machine.

## Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`
- Git
- (Optional) MLflow tracking server
- (Optional) Docker for MLflow server

## Quick Start

### Step 1: Clone Repository

```bash
git clone https://github.com/delcaux-labs/deepfix.git
cd deepfix
```

### Step 2: Create Virtual Environment

Using `uv` (recommended):

```bash
uv venv --python 3.11
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

Using `venv`:

```bash
python3.11 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### Step 3: Install DeepFix

```bash
# Install all packages in editable mode
uv pip install -e .

# Or using pip
pip install -e .
```

This installs:
- `deepfix-core`: Core models and types
- `deepfix-sdk`: Client SDK
- `deepfix-server`: Analysis server

### Step 4: Install Development Dependencies (Optional)

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Or install manually
uv pip install pytest ruff mypy
```

### Step 5: Verify Installation

```bash
# Check SDK version
uv run python -c "import deepfix_sdk; print(deepfix_sdk.__version__)"

# Check server version
uv run deepfix-server version

# Check imports
uv run python -c "from deepfix_sdk import DeepFixClient; print('SDK OK')"
```

## Configuration

### Step 1: Configure Server

Create `.env` file in `deepfix-server/` directory:

```bash
cd deepfix-server
cp env.example .env
```

Edit `.env` with your configuration:

```bash
# LLM Configuration
DEEPFIX_LLM_API_KEY=sk-...
DEEPFIX_LLM_BASE_URL=https://api.your-llm.com/v1
DEEPFIX_LLM_MODEL_NAME=gpt-4o
DEEPFIX_LLM_TEMPERATURE=0.4
DEEPFIX_LLM_MAX_TOKENS=6000
DEEPFIX_LLM_CACHE=true
DEEPFIX_LLM_TRACK_USAGE=true

# Server Configuration
LIT_SERVER_API_KEY=ACCESS-TOKEN-TO-BE-DEFINED
```

### Step 2: Start MLflow Server (Optional)

Option 1: Using Python:

```bash
# Start MLflow server
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000
```

Option 2: Using Docker:

```bash
docker run -d \
    -p 5000:5000 \
    -v $(pwd)/mlruns:/mlruns \
    -v $(pwd)/mlflow.db:/mlflow.db \
    ghcr.io/mlflow/mlflow:latest \
    mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root /mlruns \
    --host 0.0.0.0 \
    --port 5000
```

Option 3: Local file storage (no server):

```python
# Use local file storage in code
mlflow_config = MLflowConfig(
    tracking_uri="file:./mlruns",
    experiment_name="local-experiment"
)
```

### Step 3: Start DeepFix Server

```bash
# Navigate to server directory
cd deepfix-server

# Launch server
uv run deepfix-server launch -e .env -port 8844 -host 127.0.0.1
```

Server should display: `Starting DeepFix server on 127.0.0.1:8844`

## Development Setup

### Project Structure

```
deepfix/
├── deepfix-core/          # Core models and types
├── deepfix-sdk/           # Client SDK
├── deepfix-server/        # Analysis server
├── deepfix-kb/            # Knowledge base
├── docs/                  # Documentation
├── tests/                 # Tests
└── pyproject.toml         # Root project config
```

### Install Individual Packages

If working on specific packages:

```bash
# Install only SDK
cd deepfix-sdk
uv pip install -e .

# Install only server
cd deepfix-server
uv pip install -e .

# Install only core
cd deepfix-core
uv pip install -e .
```

### Development Dependencies

Install development tools:

```bash
# Code formatting
uv pip install ruff black

# Type checking
uv pip install mypy

# Testing
uv pip install pytest pytest-cov

# Documentation
uv pip install mkdocs mkdocs-material
```

### IDE Setup

#### VS Code

1. Install Python extension
2. Select Python 3.11 interpreter
3. Configure settings:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.ruffEnabled": true
}
```

#### PyCharm

1. Open project
2. Configure Python interpreter to use virtual environment
3. Mark source directories as source roots:
   - `deepfix-core/src`
   - `deepfix-sdk/src`
   - `deepfix-server/src`

## Running Tests

### Run All Tests

```bash
# From project root
uv run pytest

# Or using pytest directly
pytest
```

### Run Specific Tests

```bash
# Run specific test file
uv run pytest tests/test_deepchecks_runners.py

# Run specific test
uv run pytest tests/test_deepchecks_runners.py::test_specific_function

# Run with coverage
uv run pytest --cov=deepfix_sdk --cov=deepfix_server
```

### Test Configuration

Create `pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
```

## Code Quality

### Formatting

```bash
# Format with ruff
uv run ruff format .

# Or with black
uv run black .
```

### Linting

```bash
# Lint with ruff
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Type Checking

```bash
# Type check with mypy
uv run mypy deepfix-sdk/src deepfix-server/src deepfix-core/src
```

## Building Documentation

### Build Docs

```bash
# Build documentation
uv run mkdocs build

# Serve documentation locally
uv run mkdocs serve

# Build and serve
uv run mkdocs serve --dev-addr=127.0.0.1:8000
```

### View Documentation

Open `http://localhost:8000` in browser

## Common Workflows

### Development Workflow

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make Changes**: Edit code in packages

3. **Test Changes**:
   ```bash
   uv run pytest
   ```

4. **Format and Lint**:
   ```bash
   uv run ruff format .
   uv run ruff check .
   ```

5. **Commit Changes**:
   ```bash
   git add .
   git commit -m "Add feature"
   ```

### Testing Server Changes

1. **Make Changes**: Edit server code

2. **Restart Server**:
   ```bash
   # Stop current server (Ctrl+C)
   # Restart server
   uv run deepfix-server launch -e .env
   ```

3. **Test with Client**:
   ```python
   from deepfix_sdk.client import DeepFixClient
   client = DeepFixClient(api_url="http://localhost:8844")
   # Test your changes
   ```

### Testing SDK Changes

1. **Make Changes**: Edit SDK code

2. **Reinstall SDK**:
   ```bash
   cd deepfix-sdk
   uv pip install -e .
   ```

3. **Test Changes**:
   ```python
   from deepfix_sdk.client import DeepFixClient
   # Test your changes
   ```

## Troubleshooting

### Common Issues

**Problem**: Import errors after installation

```bash
# Solution: Reinstall in editable mode
uv pip install -e .

# Or reinstall specific package
cd deepfix-sdk
uv pip install -e .
```

**Problem**: Virtual environment not activated

```bash
# Solution: Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

**Problem**: Server fails to start

```bash
# Solution: Check .env file exists and is configured
cd deepfix-server
cat .env

# Check required environment variables
echo $DEEPFIX_LLM_API_KEY

# Check port is available
lsof -i :8844  # macOS/Linux
netstat -ano | findstr :8844  # Windows
```

**Problem**: MLflow connection errors

```bash
# Solution: Verify MLflow server is running
curl http://localhost:5000

# Check MLflow configuration
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.list_experiments()
```

### Environment Issues

**Problem**: Python version mismatch

```bash
# Solution: Use correct Python version
python --version  # Should be 3.11+
uv venv --python 3.11
```

**Problem**: Permission errors

```bash
# Solution: Use virtual environment or --user flag
uv pip install --user -e .
```

## Next Steps

- [Quickstart Guide](../getting-started/quickstart.md) - Get started with DeepFix
- [Configuration Guide](../getting-started/configuration.md) - Configure DeepFix
- [Development Guide](../contributing/development.md) - Development practices
- [Docker Deployment](docker.md) - Deploy with Docker

