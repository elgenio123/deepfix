# NLP Datasets Guide

This guide covers using DeepFix to diagnose natural language processing (NLP) datasets. Learn how to work with text data and analyze NLP datasets.

## Overview

DeepFix provides specialized support for NLP datasets, including:

- Text quality checks
- Token distribution analysis
- Vocabulary analysis
- Label distribution validation
- Dataset balance checks
- Text preprocessing recommendations

## Prerequisites

- DeepFix installed and configured
- DeepFix server running
- `datasets` library installed (`pip install datasets`)
- NLP dataset in Hugging Face datasets format or compatible
- Python 3.11 or higher

## Basic Workflow

### Step 1: Load NLP Dataset

Load your NLP dataset:

```python
from datasets import load_dataset

# Option 1: Load from Hugging Face Hub
train_data = load_dataset("imdb", split="train")
test_data = load_dataset("imdb", split="test")

# Option 2: Load from local files
train_data = load_dataset("csv", data_files="train.csv", split="train")
test_data = load_dataset("csv", data_files="test.csv", split="test")

# Option 3: Load from JSON
train_data = load_dataset("json", data_files="train.json", split="train")
test_data = load_dataset("json", data_files="test.json", split="test")
```

### Step 2: Wrap Dataset for DeepFix

```python
from deepfix_sdk.data.datasets import NLPDataset

dataset_name = "my-nlp-dataset"

# Wrap train and test datasets
train_dataset = NLPDataset(
    dataset_name=dataset_name,
    dataset=train_data
)

test_dataset = NLPDataset(
    dataset_name=dataset_name,
    dataset=test_data
)
```

### Step 3: Initialize Client

```python
from deepfix_sdk.client import DeepFixClient

client = DeepFixClient(api_url="http://localhost:8844")
```

### Step 4: Ingest Dataset

```python
client.ingest(
    dataset_name=dataset_name,
    train_data=train_dataset,
    test_data=test_dataset,
    train_test_validation=True,
    data_integrity=True,
    batch_size=16,  # Adjust based on text length
    overwrite=False
)
```

### Step 5: Diagnose Dataset

```python
result = client.diagnose_dataset(
    dataset_name=dataset_name,
    language="english"
)

# View results
print(result.to_text())
```

## Complete Example

Here's a complete example with an NLP dataset:

```python
from datasets import load_dataset
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.data.datasets import NLPDataset

# Initialize client
client = DeepFixClient(api_url="http://localhost:8844")

# Load NLP dataset
train_data = load_dataset("imdb", split="train")
test_data = load_dataset("imdb", split="test")

# Wrap datasets
dataset_name = "imdb-sentiment"

train_dataset = NLPDataset(
    dataset_name=dataset_name,
    dataset=train_data
)

test_dataset = NLPDataset(
    dataset_name=dataset_name,
    dataset=test_data
)

# Ingest and diagnose
client.ingest(
    dataset_name=dataset_name,
    train_data=train_dataset,
    test_data=test_dataset,
    batch_size=16,
    overwrite=False
)

result = client.diagnose_dataset(dataset_name=dataset_name)
print(result.to_text())
```

## Advanced Usage

### Custom Text Preprocessing

Preprocess text before ingestion:

```python
from datasets import Dataset

def preprocess_text(examples):
    # Example preprocessing
    examples['text'] = [text.lower() for text in examples['text']]
    examples['text'] = [text.strip() for text in examples['text']]
    return examples

# Apply preprocessing
train_data = train_data.map(preprocess_text)
test_data = test_data.map(preprocess_text)
```

### Handling Large NLP Datasets

For large NLP datasets, use streaming:

```python
from datasets import load_dataset

# Use streaming for large datasets
train_data = load_dataset("imdb", split="train", streaming=True)

# Process in batches
batch_size = 1000
for batch in train_data:
    # Process batch
    process_batch(batch)
```

### Custom Dataset Format

Create custom dataset from your data:

```python
from datasets import Dataset
import pandas as pd

# From pandas DataFrame
df = pd.read_csv("text_data.csv")
dataset = Dataset.from_pandas(df)

# From list of dictionaries
data = [
    {"text": "Sample text 1", "label": 0},
    {"text": "Sample text 2", "label": 1}
]
dataset = Dataset.from_list(data)

# Wrap for DeepFix
nlp_dataset = NLPDataset(dataset_name="custom-nlp", dataset=dataset)
```

### MLflow Integration

Track NLP analysis in MLflow:

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.config import MLflowConfig

# Configure MLflow
mlflow_config = MLflowConfig(
    tracking_uri="http://localhost:5000",
    experiment_name="nlp-analysis",
    run_name="imdb-analysis"
)

client = DeepFixClient(
    api_url="http://localhost:8844",
    mlflow_config=mlflow_config
)

# Ingest and diagnose - results tracked in MLflow
client.ingest(...)
result = client.diagnose_dataset(...)
```

## Understanding Results

The diagnosis results for NLP datasets include:

### Dataset Statistics

- Text count and length distribution
- Vocabulary size and distribution
- Token count statistics
- Label distribution
- Dataset splits (train/val/test)

### Quality Issues

- Text length outliers
- Empty or very short texts
- Duplicate text detection
- Label imbalance
- Vocabulary overlap between train/test

### Recommendations

- Text preprocessing suggestions
- Vocabulary size recommendations
- Sequence length recommendations
- Tokenization strategies
- Model architecture suggestions

### Example Result Interpretation

```python
result = client.diagnose_dataset(dataset_name="my-nlp-dataset")

# Access dataset-specific findings
dataset_findings = result.agent_results.get("DatasetArtifactsAnalyzer", {}).findings
print("Dataset Findings:", dataset_findings)

# Get summary
print(f"\nSummary: {result.summary}")

# Access recommendations
if result.additional_outputs:
    recommendations = result.additional_outputs.get("recommendations", [])
    for rec in recommendations:
        print(f"- {rec}")
```

## Best Practices

### Data Quality

1. **Text Cleaning**: Clean and normalize text before ingestion
   ```python
   def clean_text(text):
       # Remove special characters
       text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
       # Normalize whitespace
       text = ' '.join(text.split())
       return text
   ```

2. **Handle Empty Texts**: Remove or handle empty texts
   ```python
   dataset = dataset.filter(lambda x: len(x['text']) > 0)
   ```

3. **Label Balance**: Ensure balanced labels for classification
   ```python
   from collections import Counter
   labels = Counter(dataset['label'])
   print(labels)  # Check distribution
   ```

### Performance

1. **Batch Size**: Adjust based on text length
   ```python
   # Short texts (tweets, headlines)
   batch_size = 32

   # Medium texts (reviews, articles)
   batch_size = 16

   # Long texts (documents, books)
   batch_size = 8
   ```

2. **Caching**: Cache preprocessed datasets
   ```python
   dataset = dataset.map(preprocess, cache_file_name="preprocessed.arrow")
   ```

3. **Streaming**: Use streaming for very large datasets
   ```python
   dataset = load_dataset("dataset", streaming=True)
   ```

### Validation

1. **Train/Test Split**: Validate splits for overlap
   ```python
   train_test_validation=True
   ```

2. **Data Integrity**: Check for corrupted entries
   ```python
   data_integrity=True
   ```

## Troubleshooting

### Common Issues

**Problem**: Memory errors with large datasets

```python
# Solution: Use streaming or process in batches
dataset = load_dataset("large-dataset", streaming=True)

# Or process in chunks
chunk_size = 10000
for i in range(0, len(dataset), chunk_size):
    chunk = dataset[i:i+chunk_size]
    process_chunk(chunk)
```

**Problem**: Text length variations

```python
# Solution: Normalize text length or truncate
max_length = 512
def truncate_text(examples):
    examples['text'] = [text[:max_length] for text in examples['text']]
    return examples

dataset = dataset.map(truncate_text)
```

**Problem**: Label imbalance

```python
# Solution: Balance dataset
from datasets import Dataset

# Option 1: Use balanced sampling
balanced_dataset = dataset.filter(lambda x: condition)

# Option 2: Use weighted sampling
from torch.utils.data import WeightedRandomSampler
weights = compute_label_weights(dataset)
sampler = WeightedRandomSampler(weights, len(dataset))
```

**Problem**: Vocabulary size too large

```python
# Solution: Limit vocabulary or use subword tokenization
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
# Tokenizer handles subword tokenization
```

### Performance Tips

1. **Use Caching**: Cache preprocessed datasets
2. **Batch Processing**: Process texts in batches
3. **Parallel Processing**: Use multiple workers for preprocessing
4. **Streaming**: Use streaming for very large datasets

## Next Steps

- [Image Classification Guide](image-classification.md) - Work with image data
- [Tabular Data Guide](tabular-data.md) - Analyze structured data
- [MLflow Integration](mlflow-integration.md) - Track experiments
- [API Reference](../api-reference/index.md) - Complete API documentation
