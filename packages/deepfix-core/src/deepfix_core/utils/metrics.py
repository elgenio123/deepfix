import functools
import json
import os
from typing import Any, Callable, Dict, Optional

def track_metrics(metric_name: str = "metric"):
    """
    Decorator to capture and save performance metrics to a JSON file.
    
    Used by the DeepFix Executor to verify the impact of code repairs.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            metrics_file = os.environ.get("DEEPFIX_METRICS_FILE", "metrics.json")
            
            # Execute the training/fitting process
            result = func(*args, **kwargs)
            
            # Logic to extract metrics. 
            # In a real-world scenario, this would involve calling .evaluate() or
            # checking internal state. For this implementation, we expect the 
            # patched script to provide the metric value via a standard attribute
            # or we parse it from logs.
            
            # Here we look for a standard 'deepfix_metric' attribute on the object
            # (e.g., the Pipeline or Trainer instance)
            metric_value = 0.0
            if args and hasattr(args[0], "deepfix_metric"):
                metric_value = args[0].deepfix_metric
            elif "deepfix_metric" in kwargs:
                metric_value = kwargs["deepfix_metric"]
            
            metrics = {
                "metric_name": metric_name,
                "value": metric_value,
            }
            
            with open(metrics_file, "w") as f:
                json.dump(metrics, f)
                
            return result
        return wrapper
    return decorator

def save_verification_metric(name: str, value: float):
    """Helper to manually save a metric value for verification."""
    metrics_file = os.environ.get("DEEPFIX_METRICS_FILE", "metrics.json")
    metrics = {
        "metric_name": name,
        "value": value,
    }
    with open(metrics_file, "w") as f:
        json.dump(metrics, f)
