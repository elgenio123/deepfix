"""Integration tests for OptimizationAdvisorAgent with KnowledgeBridge."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from deepfix_kb import KnowledgeBridge, KnowledgeResponse
from deepfix_kb.retrieval import RetrievalResult

from deepfix_server.agents.optimizationadvisor import OptimizationAdvisorAgent


@pytest.fixture
def mock_knowledge_bridge():
    """Mock KnowledgeBridge with predefined responses."""
    bridge = MagicMock(spec=KnowledgeBridge)

    # Mock query response
    bridge.query = AsyncMock(
        return_value=KnowledgeResponse(
            query="test query",
            results=[
                RetrievalResult(
                    content="Use dropout and weight decay for regularization.",
                    source="web",
                    url="https://example.com/regularization",
                )
            ],
            synthesis="Regularization helps prevent overfitting through dropout and L2 weight decay.",
            sources_used=["web", "perplexity"],
            total_citations=["https://example.com/regularization"],
        )
    )

    return bridge


@pytest.mark.asyncio
async def test_optimization_advisor_calls_knowledge_bridge(mock_knowledge_bridge):
    """Test that OptimizationAdvisorAgent queries KnowledgeBridge during forward()."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    # Act
    await agent.forward(
        artifacts_analysis="Training shows overfitting after epoch 10",
        optimization_areas=["regularization"],
    )

    # Assert KnowledgeBridge was called
    mock_knowledge_bridge.query.assert_called()
    call_args = mock_knowledge_bridge.query.call_args
    assert "regularization" in call_args.kwargs.get(
        "query", ""
    ).lower() or "regularization" in str(call_args)


@pytest.mark.asyncio
async def test_optimization_advisor_builds_queries_from_areas(mock_knowledge_bridge):
    """Test query generation from optimization areas."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    queries = agent._build_knowledge_queries(
        optimization_areas=["learning_rate", "data_augmentation"],
        artifacts_analysis="Model not converging",
    )

    assert len(queries) > 0
    assert any("learning rate" in q.lower() for q in queries)
    assert any("augmentation" in q.lower() for q in queries)


@pytest.mark.asyncio
async def test_optimization_advisor_handles_context_keywords(mock_knowledge_bridge):
    """Test that context keywords trigger additional queries."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    queries = agent._build_knowledge_queries(
        optimization_areas=["regularization"],
        artifacts_analysis="Model shows severe overfitting with vanishing gradients",
    )

    # Should detect overfitting and vanishing gradient keywords
    assert any("overfitting" in q.lower() for q in queries)
    assert any("vanishing" in q.lower() or "gradient" in q.lower() for q in queries)


@pytest.mark.asyncio
async def test_optimization_advisor_formats_retrieved_knowledge(mock_knowledge_bridge):
    """Test that retrieved knowledge is formatted with citations."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    knowledge = await agent._retrieve_knowledge(["test query"])

    assert "Regularization" in knowledge
    assert "https://example.com" in knowledge


@pytest.mark.asyncio
async def test_optimization_advisor_handles_empty_queries(mock_knowledge_bridge):
    """Test graceful handling of empty query list."""
    agent = OptimizationAdvisorAgent(knowledge_bridge=mock_knowledge_bridge)

    knowledge = await agent._retrieve_knowledge([])

    assert "No external knowledge" in knowledge
