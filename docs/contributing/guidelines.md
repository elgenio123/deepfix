# Contributing Guidelines

Thank you for your interest in contributing to DeepFix! This guide will help you get started with contributing.

## How to Contribute

There are many ways to contribute to DeepFix:

- **Bug Reports**: Report bugs and issues
- **Feature Requests**: Suggest new features
- **Code Contributions**: Submit pull requests
- **Documentation**: Improve documentation
- **Examples**: Add usage examples
- **Testing**: Write tests

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/deepfix.git
cd deepfix

# Add upstream remote
git remote add upstream https://github.com/delcaux-labs/deepfix.git
```

### 2. Set Up Development Environment

See [Development Guide](development.md) for detailed setup instructions.

```bash
# Create virtual environment
uv venv --python 3.11
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install in development mode
uv pip install -e ".[dev]"
```

### 3. Create Feature Branch

```bash
# Create branch for your changes
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## Contribution Workflow

### 1. Make Changes

- Write clear, readable code
- Follow code style guidelines
- Add tests for new features
- Update documentation

### 2. Test Your Changes

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy deepfix-sdk/src deepfix-server/src
```

### 3. Commit Changes

Follow conventional commit messages:

```bash
git add .
git commit -m "feat: add new feature"
git commit -m "fix: fix bug in client"
git commit -m "docs: update installation guide"
git commit -m "test: add tests for new feature"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Code Style

### Python Style

We use `ruff` for code formatting and linting:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

### Type Hints

Use type hints for function signatures:

```python
from typing import Optional, List, Dict

def process_dataset(
    dataset_name: str,
    batch_size: int = 8
) -> Dict[str, Any]:
    """Process dataset with given parameters."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def analyze_dataset(dataset_name: str) -> AnalysisResult:
    """Analyze dataset and return results.
    
    Args:
        dataset_name: Name of the dataset to analyze
        
    Returns:
        AnalysisResult: Analysis results with findings
        
    Raises:
        ValueError: If dataset not found
    """
    pass
```

## Testing

### Writing Tests

- Write tests for all new features
- Use descriptive test names
- Test edge cases and error conditions
- Keep tests isolated and independent

### Test Structure

```python
import pytest
from deepfix_sdk.client import DeepFixClient

def test_client_initialization():
    """Test DeepFixClient initialization."""
    client = DeepFixClient(api_url="http://localhost:8844")
    assert client.api_url == "http://localhost:8844"

def test_client_with_timeout():
    """Test client with custom timeout."""
    client = DeepFixClient(api_url="http://localhost:8844", timeout=60)
    assert client.timeout == 60
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_client.py

# Run with coverage
uv run pytest --cov=deepfix_sdk
```

## Documentation

### Code Documentation

- Document all public APIs
- Include examples in docstrings
- Keep documentation up to date

### User Documentation

- Update user-facing documentation
- Add examples for new features
- Keep guides current

### Building Documentation

```bash
# Build documentation
uv run mkdocs build

# Serve documentation locally
uv run mkdocs serve
```

## Pull Request Process

### Before Submitting

1. **Update Documentation**: Update docs for new features
2. **Add Tests**: Include tests for new code
3. **Run Checks**: Ensure all checks pass
4. **Update CHANGELOG**: Add entry to CHANGELOG (if applicable)

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
How has this been tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)
```

### Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: Maintainers review code
3. **Address Feedback**: Respond to review comments
4. **Merge**: Approved PRs are merged

## Issue Reporting

### Bug Reports

When reporting bugs, include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: How to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, etc.
- **Code Example**: Minimal code to reproduce

### Feature Requests

When requesting features, include:

- **Use Case**: Why this feature is needed
- **Proposed Solution**: How the feature should work
- **Alternatives**: Alternative solutions considered
- **Additional Context**: Any other relevant information

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome constructive feedback
- Focus on what is best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Any conduct that is inappropriate in a professional setting

## Getting Help

### Questions

- **GitHub Discussions**: Ask questions in discussions
- **GitHub Issues**: Open an issue for bugs/features
- **Email**: Contact maintainers directly

### Communication

- Be clear and concise
- Provide context
- Be patient and respectful
- Follow up on questions

## Recognition

Contributors are recognized in:

- **Contributors List**: GitHub contributors page
- **Release Notes**: Credit in release notes
- **Documentation**: Optional attribution in docs

## Next Steps

- [Development Guide](development.md) - Development setup
- [Code Style Guide](#code-style) - Coding standards
- [Testing Guide](#testing) - Testing practices
- [Documentation Guide](#documentation) - Documentation standards

Thank you for contributing to DeepFix!

