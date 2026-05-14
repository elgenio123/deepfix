import dspy
from typing import List

class PatchGenerationSignature(dspy.Signature):
    """
    Generate a Python code patch to fix identified machine learning bugs.
    The patch should be a valid Python code snippet or a full replacement 
    depending on the context.
    """
    findings = dspy.InputField(desc="The identified bugs and issues in the ML workflow.")
    recommendations = dspy.InputField(desc="The recommended actions to fix the bugs.")
    code_context = dspy.InputField(desc="The original source code that needs fixing.")
    
    patch = dspy.OutputField(desc="The patched Python code that resolves the issues.")
