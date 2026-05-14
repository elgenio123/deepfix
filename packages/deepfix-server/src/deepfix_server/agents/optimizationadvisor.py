import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import dspy
from deepfix_core.models import AgentResult, Analysis
from deepfix_kb import KnowledgeBridge, KnowledgeResponse

from ..config import LLMConfig
from ..logging import get_logger
from ..repair.executor import Executor
from ..repair.patch_generator import PatchGenerator
from .base import Agent
from .signatures import OptimizationRecommendationSignature

LOGGER = get_logger(__name__)


class OptimizationAdvisorAgent(Agent):
    """Optimization advisor that uses KnowledgeBridge for grounded recommendations.

    Now upgraded to a "Verified-Repair" Advisor. It can generate code patches,
    execute them in a sandbox, and verify performance improvements.
    """

    def __init__(
        self,
        knowledge_bridge: KnowledgeBridge,
        llm_config: Optional[LLMConfig] = None,
    ):
        super().__init__(config=llm_config)
        signature = type(
            f"{self.agent_name}Signature",
            (OptimizationRecommendationSignature,),
            {"__doc__": self.system_prompt},
        )
        self.llm = dspy.ChainOfThought(signature)
        self.knowledge_bridge = knowledge_bridge
        self.patch_generator = PatchGenerator()
        self.executor = Executor()

    async def aforward(
        self,
        artifacts_analysis: List[Analysis],
        constraints: Optional[str] = None,
        verify_repairs: bool = False,
        original_code: Optional[str] = None,
    ) -> AgentResult:
        """Generate optimization recommendations and optionally verify them.

        Args:
            artifacts_analysis: Analysis from previous agents.
            constraints: Optional user constraints.
            verify_repairs: If True, attempt to generate and verify code patches.
            original_code: The source code to be patched if verify_repairs is True.

        Returns:
            AgentResult with grounded recommendations and optional verification results.
        """
        # Retrieve knowledge from KnowledgeBridge
        knowledge_context = await self._retrieve_knowledge(artifacts_analysis)

        # Call LLM with retrieved knowledge
        with self._llm_context():
            response = await self.llm.acall(
                artifacts_analysis=artifacts_analysis,
                constraints=constraints,
                retrieved_knowledge=knowledge_context,
            )

        analysis_list = response.analysis

        # Verified-Repair Loop
        if verify_repairs and original_code:
            LOGGER.info(f"Starting Verified-Repair loop for {len(analysis_list)} potential findings...")
            loop = asyncio.get_event_loop()
            for analysis in analysis_list:
                # Only attempt repair for high-confidence search/performance bugs
                if analysis.recommendations.confidence > 0.7:
                    try:
                        LOGGER.info(f"Attempting repair for: {analysis.findings.description} (Confidence: {analysis.recommendations.confidence})")
                        
                        # 1. Generate Patch
                        with self._llm_context():
                            # PatchGenerator.aforward is async, ensuring LM context is preserved
                            patch = await self.patch_generator.aforward(
                                findings=analysis.findings.description,
                                recommendations=analysis.recommendations.action,
                                code_context=original_code
                            )
                        
                        # 2. Execute and Verify (Long-running subprocess, must be in executor)
                        # and we determine metric based on bug type (F1 for Search, Time/Resource for Performance)
                        metric_name = "F1" if analysis.findings.bug_type == "search" else "ExecutionTime"
                        
                        verification = await loop.run_in_executor(
                            None,
                            self.executor.execute_and_verify,
                            original_code,
                            patch,
                            metric_name
                        )
                        
                        analysis.verification = verification
                        LOGGER.info(f"Verification complete: {verification.improvement} {metric_name} improvement.")
                        
                    except Exception as e:
                        LOGGER.error(f"Repair verification failed: {str(e)}")
                        LOGGER.error(traceback.format_exc())
                else:
                    LOGGER.info(f"Skipping repair for finding '{analysis.findings.description}' due to low confidence ({analysis.recommendations.confidence})")
        else:
            LOGGER.info(f"Verified-Repair loop skipped. verify_repairs={verify_repairs}, original_code_present={original_code is not None}")

        return AgentResult(
            agent_name=self.agent_name,
            analysis=analysis_list,
        )

    async def arun(
        self,
        artifacts_analysis: List[Analysis],
        constraints: Optional[str] = None,
        verify_repairs: bool = False,
        original_code: Optional[str] = None,
    ) -> AgentResult:
        try:
            return await self.acall(
                artifacts_analysis=artifacts_analysis, 
                constraints=constraints,
                verify_repairs=verify_repairs,
                original_code=original_code
            )
        except Exception as e:
            LOGGER.error(
                f"Error with agent {self.agent_name}:\n {traceback.format_exc()}"
            )
            return AgentResult(agent_name=self.agent_name, error_message=str(e))

    def forward(self, **kwargs):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, self.aforward(**kwargs))
            return future.result()

    async def _retrieve_knowledge(self, analyses: List[Analysis]) -> str:
        """Retrieve and format knowledge from KnowledgeBridge.

        Args:
            analyses: List of analyses to execute.

        Returns:
            Formatted knowledge context string with citations.
        """
        if not analyses:
            return "No external knowledge retrieved."

        knowledge_parts = []

        for analysis in analyses:
            try:
                response: KnowledgeResponse = await self.knowledge_bridge.query(
                    query=analysis,
                    max_results=3,
                    synthesize=True,
                )

                if response.synthesis:
                    knowledge_parts.append(f"{response.synthesis}")

                    # Add citations
                    if response.total_citations:
                        citations = "\n".join(
                            f"- {url}" for url in response.total_citations[:3]
                        )
                        knowledge_parts.append(f"Sources:\n{citations}")

            except Exception:
                # Log but continue with other queries
                # knowledge_parts.append(f"Retrieval failed: {str(e)}")
                print(f"Retrieval failed: {traceback.format_exc()}")

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

            1. **Bug Categorization (DREAM 2023)**:
            - **SEARCH Bug**: The system fails to find an accurate enough model (e.g., poor F1, high RMSE, sub-optimal hyperparameters). Focus on effectiveness.
            - **PERFORMANCE Bug**: The system takes unreasonably long or uses excessive resources (e.g., slow training, GPU bottlenecks). Focus on efficiency.
            - **MANDATORY**: Categorize every finding as either 'performance' or 'search'.

            2. **Root Cause Analysis**:
            - Identify underlying causes of poor performance or search failure.
            - Distinguish between data issues, model issues, and training issues.

            3. **Verified Repair Recommendation**:
            - Provide specific, implementable code modifications.
            - Your recommendations will be used to generate automated patches. Ensure they are precise.
            - For SEARCH bugs, prioritize fixes that improve accuracy/F1.
            - For PERFORMANCE bugs, prioritize fixes that reduce execution time or memory.

            4. **Impact Assessment**:
            - Estimate expected improvement for each recommendation.
            - Provide confidence intervals.

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
