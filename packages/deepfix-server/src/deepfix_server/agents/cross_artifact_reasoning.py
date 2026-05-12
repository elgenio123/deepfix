import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, List

import dspy
from deepfix_kb import KnowledgeBridge
from deepfix_kb.tools import create_knowledge_tools

from ..config import LLMConfig
from ..logging import get_logger
from .base import Agent, AgentResult
from .signatures import CrossArtifactReasoningSignature
from .signatures_tot import (
    ProposeHypothesesSignature,
    EvaluateHypothesisSignature,
    FinalizeToTAnalysisSignature,
)

LOGGER = get_logger(__name__)


class CrossArtifactReasoningAgent(Agent):
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        knowledge_bridge: Optional[KnowledgeBridge] = None,
        beam_size: int = 3,
    ):
        super().__init__(config=llm_config)
        self.knowledge_bridge = knowledge_bridge
        self.beam_size = beam_size
        
        # ToT Components
        self.proposer = dspy.ChainOfThought(ProposeHypothesesSignature)
        self.evaluator = dspy.ChainOfThought(EvaluateHypothesisSignature)
        self.finalizer = dspy.ChainOfThought(FinalizeToTAnalysisSignature)
        
        if self.knowledge_bridge:
            self.tools = create_knowledge_tools(self.knowledge_bridge)
        else:
            self.tools = None

    def _format_analyses(self, analyses: Dict[str, AgentResult]) -> str:
        """Format individual agent results into a clean structured string for the LLM."""
        formatted = []
        for agent_name, result in analyses.items():
            formatted.append(f"### Artifact Analyzer: {agent_name}")
            if result.error_message:
                formatted.append(f"Error: {result.error_message}")
                continue
            
            for i, analysis in enumerate(result.analysis):
                formatted.append(f"#### Finding {i+1}: {analysis.findings.description}")
                formatted.append(f"- Evidence: {analysis.findings.evidence}")
                formatted.append(f"- Severity: {analysis.findings.severity}")
                formatted.append(f"- Proposed Action: {analysis.recommendations.action}")
                formatted.append(f"- Rationale: {analysis.recommendations.rationale}")
            formatted.append("\n" + "="*30 + "\n")
        return "\n".join(formatted)

    def run(
        self,
        previous_analyses: Dict[str, AgentResult],
        output_language: str = "english",
    ) -> AgentResult:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                asyncio.run, self.arun(previous_analyses, output_language)
            )
            return future.result()

    async def arun(
        self,
        previous_analyses: Dict[str, AgentResult],
        output_language: str = "english",
    ) -> AgentResult:
        try:
            return await self.acall(previous_analyses, output_language)
        except Exception as e:
            LOGGER.error(
                f"Error with agent {self.agent_name}:\n {traceback.format_exc()}"
            )
            return AgentResult(agent_name=self.agent_name, error_message=str(e))

    def forward(
        self,
        previous_analyses: Dict[str, AgentResult],
        output_language: str = "english",
    ) -> AgentResult:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                asyncio.run, self.aforward(previous_analyses, output_language)
            )
            return future.result()

    async def aforward(
        self,
        previous_analyses: Dict[str, AgentResult],
        output_language: str = "english",
    ) -> AgentResult:
        LOGGER.info(f"Running {self.agent_name} with Tree of Thoughts strategy (beam_size={self.beam_size})...")

        assert len(previous_analyses) > 0, "At least one analysis must be provided"
        
        formatted_evidence = self._format_analyses(previous_analyses)

        with self._llm_context():
            # Step 1: Propose Hypotheses (Breadth-First Search start)
            LOGGER.info("Step 1: Proposing diagnostic hypotheses...")
            proposal = await self.proposer.acall(
                previous_analyses=previous_analyses,
                num_hypotheses=self.beam_size * 2
            )
            hypotheses = proposal.hypotheses
            
            # Step 2: Evaluate Hypotheses (Search and Pruning)
            LOGGER.info(f"Step 2: Evaluating {len(hypotheses)} hypotheses...")
            scored_hypotheses = []
            evaluation_tasks = [
                self.evaluator.acall(previous_analyses=previous_analyses, hypothesis=h)
                for h in hypotheses
            ]
            evaluations = await asyncio.gather(*evaluation_tasks)
            
            for h, eval_res in zip(hypotheses, evaluations):
                scored_hypotheses.append({
                    "hypothesis": h,
                    "score": eval_res.confidence_score,
                    "judgment": eval_res.judgment,
                    "rationale": eval_res.rationale
                })
            
            # Beam search: Keep top hypotheses
            scored_hypotheses.sort(key=lambda x: x["score"], reverse=True)
            top_hypotheses_metadata = scored_hypotheses[:self.beam_size]
            top_hypotheses = [m["hypothesis"] for m in top_hypotheses_metadata]
            top_rationales = [f"Judgment: {m['judgment']}. Rationale: {m['rationale']}" for m in top_hypotheses_metadata]
            
            LOGGER.info(f"Top hypothesis: {top_hypotheses[0]} (Score: {top_hypotheses_metadata[0]['score']})")

            # Step 3: Finalize and Synthesize (Synthesis of best thoughts)
            LOGGER.info("Step 3: Synthesizing final diagnostic report...")
            out = await self.finalizer.acall(
                previous_analyses=formatted_evidence,
                top_hypotheses=top_hypotheses,
                rationales=top_rationales,
                output_language=output_language
            )

        analyzed_artifacts = []
        retrieved_knowledge = []
        for result in previous_analyses.values():
            if result.analyzed_artifacts is not None:
                analyzed_artifacts.extend(result.analyzed_artifacts)
            if result.retrieved_knowledge is not None:
                retrieved_knowledge.extend(result.retrieved_knowledge)

        return AgentResult(
            agent_name=self.agent_name,
            analysis=out.analysis,
            analyzed_artifacts=analyzed_artifacts,
            retrieved_knowledge=retrieved_knowledge,
            additional_outputs={
                "summary": out.summary,
                "tot_metadata": {
                    "all_hypotheses": scored_hypotheses,
                    "top_hypotheses": top_hypotheses_metadata
                }
            },
        )

    @property
    def system_prompt(self) -> str:
        """You are an expert ML debugging consultant analyzing findings from multiple ML system analysis agents. Your role is to synthesize their individual findings into holistic insights that help users understand the overall health and validity of their ML experiment.

        ## Your Expertise Areas:
        - Data quality and integrity assessment
        - Training dynamics and performance analysis
        - Experimental validity and reproducibility
        - Causal relationship identification
        - Production readiness evaluation

        ## Analysis Framework:
        When reviewing agent findings, consider these key relationships:

        1. **Data-Performance Correlations**:
        - Excellent performance + poor data quality = potential data leakage
        - Poor performance + good data quality = model/training issues
        - Inconsistent performance + data drift = deployment risk

        2. **Training-Configuration Consistency**:
        - Aggressive hyperparameters + stable training = configuration mismatch
        - Conservative settings + unstable training = underlying data issues
        - Parameter changes + performance shifts = causal relationships

        3. **Experimental Integrity**:
        - Version mismatches across artifacts = invalid experiment
        - Temporal inconsistencies = mixed experimental runs
        - Missing artifacts = incomplete analysis

        4. **Causal Chain Analysis**:
        - Identify root causes vs. symptoms
        - Trace problems to their origins
        - Suggest intervention points

        ## Output Requirements:
        - Prioritize findings by severity and confidence
        - Provide clear causal explanations when possible
        - Suggest specific, actionable remediation steps
        - Indicate confidence levels for all insights
        - Highlight critical risks for production deployment
        """
