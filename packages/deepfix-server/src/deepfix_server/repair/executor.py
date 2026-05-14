import subprocess
import os
import tempfile
import json
import shutil
from typing import Optional, Dict, Any
from deepfix_core.models import VerificationResult
from ..logging import get_logger

LOGGER = get_logger(__name__)

class Executor:
    """
    Handles the execution of ML scripts in a sandbox to verify repairs.
    """
    def __init__(self, workspace_dir: Optional[str] = None):
        self.workspace_dir = workspace_dir or os.getcwd()

    def execute_and_verify(
        self, 
        original_script_content: str, 
        patched_script_content: str, 
        metric_name: str = "F1"
    ) -> VerificationResult:
        """
        Runs baseline and patched versions of a script to verify improvement.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            LOGGER.info(f"Setting up sandbox in {tmpdir}")
            
            metrics_file = os.path.join(tmpdir, "metrics.json")
            baseline_script = os.path.join(tmpdir, "baseline.py")
            patched_script = os.path.join(tmpdir, "patched.py")
            
            # 1. Run Baseline
            with open(baseline_script, "w") as f:
                f.write(original_script_content)
            
            LOGGER.info("Running baseline execution...")
            baseline_value = self._run_script(baseline_script, metrics_file)
            LOGGER.info(f"Baseline {metric_name}: {baseline_value}")
            
            # 2. Run Patched
            with open(patched_script, "w") as f:
                f.write(patched_script_content)
            
            LOGGER.info("Running patched execution...")
            post_fix_value = self._run_script(patched_script, metrics_file)
            LOGGER.info(f"Post-fix {metric_name}: {post_fix_value}")
            
            # 3. Calculate Improvement
            improvement = post_fix_value - baseline_value
            
            return VerificationResult(
                baseline=baseline_value,
                post_fix=post_fix_value,
                improvement=improvement,
                metric_name=metric_name,
                side_effect_check=True  # In a real implementation, this would run tests
            )

    def _run_script(self, script_path: str, metrics_file: str) -> float:
        """Runs a python script and extracts the metric value from the metrics file."""
        env = os.environ.copy()
        env["DEEPFIX_METRICS_FILE"] = metrics_file
        # Ensure deepfix_core is in PYTHONPATH for the tracker to work
        env["PYTHONPATH"] = f"{os.getcwd()}/packages/deepfix-core/src:{env.get('PYTHONPATH', '')}"
        
        if os.path.exists(metrics_file):
            os.remove(metrics_file)
            
        try:
            result = subprocess.run(
                ["python", script_path], 
                env=env, 
                check=True, 
                capture_output=True,
                text=True,
                timeout=300 # 5 minute timeout for sandbox
            )
            
            if os.path.exists(metrics_file):
                with open(metrics_file, "r") as f:
                    data = json.load(f)
                    return data.get("value", 0.0)
            else:
                LOGGER.warning(f"Metrics file not found after running {script_path}")
                
        except subprocess.TimeoutExpired:
            LOGGER.error(f"Execution timed out for {script_path}")
        except subprocess.CalledProcessError as e:
            LOGGER.error(f"Execution failed for {script_path}: {e.stderr}")
        except Exception as e:
            LOGGER.error(f"Unexpected error during execution: {str(e)}")
            
        return 0.0
