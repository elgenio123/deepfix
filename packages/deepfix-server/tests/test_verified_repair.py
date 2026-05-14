import pytest
import os
import json
from deepfix_server.repair.executor import Executor
from deepfix_core.models import VerificationResult

def test_executor_basic():
    executor = Executor()
    
    # Mock scripts that use the save_verification_metric helper
    baseline_script = """
import os
import json
# Adding the path to deepfix-core to sys.path so it can find the utils
import sys
sys.path.append(os.path.join(os.getcwd(), 'packages/deepfix-core/src'))

from deepfix_core.utils.metrics import save_verification_metric
save_verification_metric("F1", 0.70)
"""
    
    patched_script = """
import os
import json
import sys
sys.path.append(os.path.join(os.getcwd(), 'packages/deepfix-core/src'))

from deepfix_core.utils.metrics import save_verification_metric
save_verification_metric("F1", 0.85)
"""
    
    result = executor.execute_and_verify(
        original_script_content=baseline_script,
        patched_script_content=patched_script,
        metric_name="F1"
    )
    
    assert isinstance(result, VerificationResult)
    assert result.baseline == 0.70
    assert result.post_fix == 0.85
    assert result.improvement == pytest.approx(0.15)
    assert result.metric_name == "F1"
    assert result.side_effect_check is True

def test_executor_failure():
    executor = Executor()
    
    baseline_script = "exit(1)" # Script fails
    patched_script = "exit(0)" # Script passes but no metrics
    
    result = executor.execute_and_verify(
        original_script_content=baseline_script,
        patched_script_content=patched_script,
        metric_name="F1"
    )
    
    assert result.baseline == 0.0
    assert result.post_fix == 0.0
    assert result.improvement == 0.0
