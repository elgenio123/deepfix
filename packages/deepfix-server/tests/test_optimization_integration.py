"""Integration tests for OptimizationAdvisorAgent with KnowledgeBridge."""

import pytest
from unittest.mock import AsyncMock, MagicMock

# Mock deepfix_kb imports before importing the agent
import sys

mock_kb = MagicMock()
mock_kb.KnowledgeBridge = MagicMock
mock_kb.KnowledgeResponse = MagicMock
sys.modules["deepfix_kb"] = mock_kb

from deepfix_server.agents.optimizationadvisor import OptimizationAdvisorAgent


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


def test_optimization_advisor_builds_queries_from_areas(mock_knowledge_bridge):
    """Test query generation from optimization areas."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    queries = agent._build_knowledge_queries(
        optimization_areas=["learning_rate", "data_augmentation"],
        artifacts_analysis="Model not converging",
    )

    assert len(queries) > 0
    assert any("learning rate" in q.lower() for q in queries)
    assert any("augmentation" in q.lower() for q in queries)


def test_optimization_advisor_handles_overfitting_keyword(mock_knowledge_bridge):
    """Test that overfitting keyword triggers additional query."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    queries = agent._build_knowledge_queries(
        optimization_areas=["regularization"],
        artifacts_analysis="Model shows severe overfitting",
    )

    assert any("overfitting" in q.lower() for q in queries)


def test_optimization_advisor_handles_gradient_keyword(mock_knowledge_bridge):
    """Test that gradient issues trigger additional query."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    queries = agent._build_knowledge_queries(
        optimization_areas=["regularization"],
        artifacts_analysis="Training shows vanishing gradients",
    )

    assert any("vanishing" in q.lower() or "gradient" in q.lower() for q in queries)


def test_optimization_advisor_limits_queries(mock_knowledge_bridge):
    """Test that query count is limited to 3."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    queries = agent._build_knowledge_queries(
        optimization_areas=[
            "learning_rate",
            "regularization",
            "data_augmentation",
            "optimizer",
        ],
        artifacts_analysis="Model shows overfitting with vanishing gradients",
    )

    assert len(queries) <= 3


def test_optimization_advisor_maps_known_areas(mock_knowledge_bridge):
    """Test that known optimization areas are mapped to specific queries."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    for area in ["learning_rate", "regularization", "batch_size", "optimizer"]:
        queries = agent._build_knowledge_queries(
            optimization_areas=[area], artifacts_analysis="Test analysis"
        )
        assert len(queries) >= 1
        # Should not be a generic query for known areas
        assert (
            queries[0] != f"best practices for {area} optimization in machine learning"
        )
