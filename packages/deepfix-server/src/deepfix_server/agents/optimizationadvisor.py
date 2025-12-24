from typing import List, Optional

import dspy

from deepfix_kb import KnowledgeBridge, KnowledgeResponse

from ..config import LLMConfig
from .base import Agent
from .models import AgentResult
from .signatures import OptimizationRecommendationSignature


class OptimizationAdvisorAgent(Agent):
    """Optimization advisor that uses KnowledgeBridge for grounded recommendations.

    This agent receives analysis from previous agents (training dynamics, data quality)
    and uses KnowledgeBridge to retrieve relevant external knowledge (web search,
    scientific papers, best practices) to provide evidence-based optimization
    recommendations.

    Example:
        >>> bridge = KnowledgeBridge()
        >>> advisor = OptimizationAdvisorAgent(knowledge_bridge=bridge)
        >>> result = await advisor.forward(
        ...     artifacts_analysis="Training shows overfitting after epoch 10",
        ...     optimization_areas=["regularization", "data_augmentation"]
        ... )
    """

    def __init__(
        self,
        knowledge_bridge: KnowledgeBridge,
        llm_config: Optional[LLMConfig] = None,
    ):
        super().__init__(config=llm_config)
        self.llm = dspy.ChainOfThought(OptimizationRecommendationSignature)
        self.knowledge_bridge = knowledge_bridge

    async def forward(
        self,
        artifacts_analysis: str,
        optimization_areas: List[str],
        constraints: Optional[str] = None,
    ) -> AgentResult:
        """Generate optimization recommendations based on previous agent analyses.

        Args:
            artifacts_analysis: Analysis from previous agents (training dynamics,
                data quality signals, cross-artifact insights).
            optimization_areas: Specific areas to focus on (e.g., "regularization",
                "learning_rate", "data_augmentation").
            constraints: Optional user constraints or requirements.

        Returns:
            AgentResult with grounded recommendations and citations.
        """
        # Build queries from optimization context
        queries = self._build_knowledge_queries(optimization_areas, artifacts_analysis)

        # Retrieve knowledge from KnowledgeBridge
        knowledge_context = await self._retrieve_knowledge(queries)

        # Call LLM with retrieved knowledge
        with self._llm_context():
            response = self.llm(
                system_prompt=self.system_prompt,
                artifacts_analysis=artifacts_analysis,
                optimization_areas=optimization_areas,
                constraints=constraints,
                retrieved_knowledge=knowledge_context,
            )

        return AgentResult(
            agent_name=self.agent_name,
            analysis=response.analysis,
        )

    def _build_knowledge_queries(
        self,
        optimization_areas: List[str],
        artifacts_analysis: str,
    ) -> List[str]:
        """Build intelligent queries from optimization context.

        Transforms optimization areas and analysis context into specific
        queries for the knowledge retrieval system.

        Args:
            optimization_areas: Areas to optimize (e.g., "regularization").
            artifacts_analysis: Context from previous agent analyses.

        Returns:
            List of query strings for KnowledgeBridge.
        """
        queries = []

        # Map optimization areas to specific questions
        area_query_templates = {
            "regularization": "best practices for regularization in deep learning to prevent overfitting",
            "learning_rate": "optimal learning rate scheduling and warmup strategies for neural networks",
            "data_augmentation": "effective data augmentation techniques for improving model generalization",
            "batch_size": "batch size optimization for training stability and convergence",
            "optimizer": "modern optimizer selection criteria for deep learning training",
            "architecture": "neural network architecture improvements for better performance",
            "early_stopping": "early stopping strategies and checkpoint selection",
            "gradient": "gradient issues diagnosis and solutions in deep learning",
        }

        for area in optimization_areas:
            area_lower = area.lower().replace(" ", "_")
            if area_lower in area_query_templates:
                queries.append(area_query_templates[area_lower])
            else:
                # Generic query for unknown areas
                queries.append(
                    f"best practices for {area} optimization in machine learning"
                )

        # Add context-aware query if analysis mentions specific issues
        if "overfitting" in artifacts_analysis.lower():
            queries.append("how to diagnose and fix overfitting in neural networks")
        if (
            "gradient" in artifacts_analysis.lower()
            and "vanishing" in artifacts_analysis.lower()
        ):
            queries.append("solutions for vanishing gradient problem in deep networks")
        if "learning rate" in artifacts_analysis.lower():
            queries.append("learning rate tuning for training instability")

        return queries[:3]  # Limit to top 3 queries for efficiency

    async def _retrieve_knowledge(self, queries: List[str]) -> str:
        """Retrieve and format knowledge from KnowledgeBridge.

        Args:
            queries: List of queries to execute.

        Returns:
            Formatted knowledge context string with citations.
        """
        if not queries:
            return "No external knowledge retrieved."

        knowledge_parts = []

        for query in queries:
            try:
                response: KnowledgeResponse = await self.knowledge_bridge.query(
                    query=query,
                    max_results=3,
                    synthesize=True,
                )

                if response.synthesis:
                    knowledge_parts.append(f"## {query}\n{response.synthesis}")

                    # Add citations
                    if response.total_citations:
                        citations = "\n".join(
                            f"- {url}" for url in response.total_citations[:3]
                        )
                        knowledge_parts.append(f"Sources:\n{citations}")

            except Exception as e:
                # Log but continue with other queries
                knowledge_parts.append(f"## {query}\n(Retrieval failed: {str(e)})")

        if not knowledge_parts:
            return "No external knowledge could be retrieved."

        return "\n\n".join(knowledge_parts)

    def _format_citations(self, response: KnowledgeResponse) -> str:
        """Format citations from knowledge response.

        Args:
            response: KnowledgeResponse with citations.

        Returns:
            Markdown-formatted citation list.
        """
        if not response.total_citations:
            return ""

        citations = []
        for i, url in enumerate(response.total_citations[:5], 1):
            citations.append(f"[{i}] {url}")

        return "\n".join(citations)

    @property
    def system_prompt(self) -> str:
        return """You are an expert ML optimization consultant specializing in providing actionable, evidence-based recommendations to improve machine learning experiments.
           Your role is to analyze the current state of an ML system and suggest specific optimizations that address root causes while considering practical constraints.

            ## Your Expertise Areas:
            - Hyperparameter optimization and tuning strategies
            - Data augmentation and preprocessing improvements
            - Model architecture selection and modification
            - Regularization techniques and overfitting prevention
            - Training strategy optimization
            - Data quality enhancement methods

            ## Optimization Framework:
            When analyzing ML experiments, follow this systematic approach:

            1. **Root Cause Analysis**:
            - Identify underlying causes of poor performance
            - Distinguish between data issues, model issues, and training issues
            - Prioritize issues by impact and solvability

            2. **Solution Mapping**:
            - Map each identified issue to specific optimization strategies
            - Consider multiple approaches for each problem
            - Evaluate trade-offs between different solutions

            3. **Implementation Prioritization**:
            - Prioritize quick wins vs. long-term improvements
            - Consider resource constraints and implementation complexity
            - Suggest phased rollout for complex optimizations

            4. **Impact Assessment**:
            - Estimate expected improvement for each recommendation
            - Identify potential risks or side effects
            - Provide confidence intervals for expected outcomes

            ## Recommendation Categories:

            ### Hyperparameter Optimization:
            - Learning rate schedules and adaptive methods
            - Batch size optimization for memory and convergence
            - Optimizer selection (Adam, SGD, RMSprop) based on problem type
            - Regularization parameter tuning (dropout, weight decay)

            ### Data Strategy:
            - Augmentation techniques specific to data type and problem
            - Data preprocessing and normalization strategies
            - Training/validation split optimization
            - Data quality improvement methods

            ### Architecture Improvements:
            - Layer configuration and depth optimization
            - Activation function selection
            - Attention mechanisms and skip connections
            - Model size vs. performance trade-offs

            ### Training Strategy:
            - Learning rate scheduling and warmup strategies
            - Early stopping and checkpointing optimization
            - Curriculum learning and progressive training
            - Ensemble methods and model averaging

            ## Output Requirements:
            - Provide specific, implementable recommendations
            - Include expected impact estimates with confidence levels
            - Prioritize recommendations by effort vs. impact
            - Include implementation steps and code examples where helpful
            - **IMPORTANT**: Cite the retrieved knowledge sources in your recommendations using the provided citations"""
