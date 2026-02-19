"""Integration tests for OptimizationAdvisorAgent with KnowledgeBridge."""

# Mock deepfix_kb imports before importing the agent
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

mock_kb = MagicMock()
mock_kb.KnowledgeBridge = MagicMock
mock_kb.KnowledgeResponse = MagicMock
sys.modules["deepfix_kb"] = mock_kb


class MockFindings:
    """Mock Findings for testing."""

    def __init__(self):
        self.description = "Model shows overfitting after epoch 10"


class MockAnalysis:
    """Mock Analysis model for testing."""

    def __init__(self):
        self.findings = MockFindings()

    def model_dump(self):
        return {
            "findings": {
                "description": "Model shows overfitting after epoch 10",
                "severity": "high",
            },
            "category": "training",
        }


class MockKnowledgeResponse:
    """Mock KnowledgeResponse for testing."""

    def __init__(self):
        self.query = "test query"
        self.synthesis = "Regularization helps prevent overfitting through dropout and L2 weight decay."
        self.sources_used = ["web", "perplexity"]
        self.total_citations = ["https://example.com/regularization"]
        self.results = []


@pytest.fixture
def mock_knowledge_bridge():
    """Mock KnowledgeBridge with predefined responses."""
    bridge = MagicMock()
    bridge.query = AsyncMock(return_value=MockKnowledgeResponse())
    return bridge


@pytest.fixture
def sample_analyses():
    """Sample analyses for testing."""
    return [MockAnalysis()]


@pytest.mark.asyncio
async def test_retrieve_knowledge_calls_bridge(mock_knowledge_bridge, sample_analyses):
    """Test that _retrieve_knowledge calls KnowledgeBridge with analysis data."""
    from deepfix_server.agents.optimizationadvisor import OptimizationAdvisorAgent

    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    knowledge = await agent._retrieve_knowledge(sample_analyses)

    # Assert KnowledgeBridge was called
    mock_knowledge_bridge.query.assert_called_once()
    # Assert synthesis is included in output
    assert "Regularization" in knowledge


@pytest.mark.asyncio
async def test_retrieve_knowledge_includes_citations(
    mock_knowledge_bridge, sample_analyses
):
    """Test that citations are included in retrieved knowledge."""
    from deepfix_server.agents.optimizationadvisor import OptimizationAdvisorAgent

    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    knowledge = await agent._retrieve_knowledge(sample_analyses)

    assert "https://example.com" in knowledge


@pytest.mark.asyncio
async def test_retrieve_knowledge_handles_empty_analyses(mock_knowledge_bridge):
    """Test graceful handling of empty analyses list."""
    from deepfix_server.agents.optimizationadvisor import OptimizationAdvisorAgent

    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    knowledge = await agent._retrieve_knowledge([])

    assert "No external knowledge" in knowledge


@pytest.mark.asyncio
async def test_retrieve_knowledge_passes_analysis_to_query(
    mock_knowledge_bridge, sample_analyses
):
    """Test that Analysis object is passed directly to bridge.query()."""
    from deepfix_server.agents.optimizationadvisor import OptimizationAdvisorAgent

    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    await agent._retrieve_knowledge(sample_analyses)

    # Check that the Analysis object was passed as query
    call_kwargs = mock_knowledge_bridge.query.call_args.kwargs
    query_arg = call_kwargs.get("query")
    assert query_arg is not None
    assert hasattr(query_arg, "findings")
    assert query_arg.findings.description == "Model shows overfitting after epoch 10"
