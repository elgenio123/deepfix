import fire
import dspy
import os
from typing import Optional

def setup_dspy_lm(
    api_key: str="empty",
    model: str = "gpt-5",
    temperature: float = 1.0,
    max_tokens: int = 1600,
) -> None:
    lm = dspy.LM(
                model=f"openai/{model}",
                api_base="http://127.0.0.1:8841/v1",
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    dspy.configure(lm=lm)
    return lm


class SimpleQA(dspy.Signature):
    """Answer a simple question based on context."""

    context: str = dspy.InputField(
        desc="May contain relevant facts about the question"
    )
    question: str = dspy.InputField(desc="The question to answer")
    answer: str = dspy.OutputField(
        desc="A concise answer to the question, based on the context"
    )


class SimpleQAModule(dspy.Module):
    """A simple question-answering module using DSPy."""

    def __init__(self):
        super().__init__()
        self.qa = dspy.ChainOfThought(SimpleQA)

    def forward(self, context: str, question: str) -> dspy.Prediction:
        """Forward pass that answers a question given context."""
        return self.qa(context=context, question=question)


class SummarySignature(dspy.Signature):
    """Summarize a given text."""

    text: str = dspy.InputField(desc="The text to summarize")
    summary: str = dspy.OutputField(
        desc="A concise summary of the provided text"
    )


class SummaryModule(dspy.Module):
    """A text summarization module using DSPy."""

    def __init__(self):
        super().__init__()
        self.summarizer = dspy.ChainOfThought(SummarySignature)

    def forward(self, text: str) -> dspy.Prediction:
        """Forward pass that summarizes text."""
        return self.summarizer(text=text)


def example_simple_qa():
    """Example: Simple Question-Answering using DSPy."""
    print("\n=== Simple QA Example ===")

    # Initialize the module
    qa_module = SimpleQAModule()

    # Example context and question
    context = "Paris is the capital of France. It is known for the Eiffel Tower, the Louvre Museum, and its romantic atmosphere."
    question = "What is Paris famous for?"

    print(f"Context: {context}")
    print(f"Question: {question}")

    # Get prediction
    prediction = qa_module(context=context, question=question)

    print(f"Answer: {prediction.answer}")
    print(f"Reasoning: {prediction.reasoning}")


def example_text_summarization():
    """Example: Text Summarization using DSPy."""
    print("\n=== Text Summarization Example ===")

    # Initialize the module
    summary_module = SummaryModule()

    # Example text
    text = """
    Machine learning is a subset of artificial intelligence (AI) that focuses on the development 
    of algorithms and statistical models that enable computers to learn and improve their performance 
    on tasks without being explicitly programmed. These systems learn from data, identifying patterns 
    and making predictions or decisions based on that data. Machine learning has applications in 
    various domains including healthcare, finance, e-commerce, and autonomous vehicles.
    """

    print(f"Text: {text.strip()}")

    # Get prediction
    prediction = summary_module(text=text)

    print(f"\nSummary: {prediction.summary}")


def setup_and_query_example(model:str="gpt-5",temperature:float=1.0,max_tokens:int=16000):
    """
    Complete example showing how to setup and use DSPy with OpenAI-compatible API.
    """
    # Setup DSPy
    setup_dspy_lm(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Run examples
    example_simple_qa()
    example_text_summarization()

if __name__ == "__main__":
    fire.Fire(setup_and_query_example)
