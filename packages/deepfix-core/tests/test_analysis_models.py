import pytest
import pandas as pd
from deepfix_core.models import AgentResult, Analysis, Finding, Recommendation, Severity, BugType, VerificationResult, APIResponse

def test_agent_result_to_dataframe_with_verification():
    finding = Finding(
        description="Low F1 score due to class imbalance",
        evidence="Class 0: 90%, Class 1: 10%",
        severity=Severity.HIGH,
        confidence=0.9,
        bug_type=BugType.SEARCH
    )
    recommendation = Recommendation(
        action="Use SMOTE or class weights",
        rationale="Oversampling minority class improves recall",
        confidence=0.85
    )
    verification = VerificationResult(
        baseline=0.72,
        post_fix=0.85,
        improvement=0.13,
        metric_name="F1",
        side_effect_check=True
    )
    
    analysis = Analysis(
        findings=finding,
        recommendations=recommendation,
        verification=verification
    )
    
    result = AgentResult(
        agent_name="OptimizationAdvisorAgent",
        analysis=[analysis],
        analyzed_artifacts=["dataset", "training"]
    )
    
    df = result.to_dataframe()
    
    assert len(df) == 1
    assert df.iloc[0]["finding_bug_type"] == "search"
    assert df.iloc[0]["verification_baseline"] == 0.72
    assert df.iloc[0]["verification_improvement"] == 0.13
    assert df.iloc[0]["verification_metric"] == "F1"

def test_api_response_to_text():
    # Similar to above, but testing the Rich output generation
    finding = Finding(
        description="Search Bug identified",
        evidence="Evidence here",
        severity=Severity.HIGH,
        confidence=0.9,
        bug_type=BugType.SEARCH
    )
    recommendation = Recommendation(
        action="Recommended Action",
        rationale="Rationale here",
        confidence=0.9
    )
    verification = VerificationResult(
        baseline=0.6,
        post_fix=0.8,
        improvement=0.2,
        metric_name="F1"
    )
    analysis = Analysis(findings=finding, recommendations=recommendation, verification=verification)
    result = AgentResult(agent_name="CrossArtifactReasoningAgent", analysis=[analysis])
    
    response = APIResponse(agent_results={"CrossArtifactReasoningAgent": result})
    
    text_report = response.to_text(verbose=True)
    
    assert "SEARCH" in text_report
    assert "VERIFIED REPAIR" in text_report
    assert "Baseline: 0.600" in text_report
    assert "Post-Fix: 0.800" in text_report
    assert "Δ 0.200 F1" in text_report
