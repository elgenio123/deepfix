# Tabular Data Guide

This guide covers using DeepFix to diagnose tabular (structured) datasets. Learn how to work with pandas DataFrames and analyze structured data.

## Overview

DeepFix provides specialized support for tabular data, including:

- Dataset quality checks
- Feature distribution analysis
- Missing value detection
- Outlier detection
- Train/test split validation
- Data type validation

## Prerequisites

- DeepFix installed and configured
- DeepFix server running
- pandas installed (`pip install pandas`)
- Tabular data in CSV, Parquet, or pandas DataFrame format
- Python 3.11 or higher

## Basic Workflow

### Step 1: Load Tabular Data

Load your tabular data into pandas DataFrames:

```python
import pandas as pd

# Load from CSV
df_train = pd.read_csv("data/train.csv")
df_test = pd.read_csv("data/test.csv")

# Or from Parquet
df_train = pd.read_parquet("data/train.parquet")
df_test = pd.read_parquet("data/test.parquet")

# Or from database
# df_train = pd.read_sql("SELECT * FROM train_data", connection)
```

### Step 2: Wrap Dataset for DeepFix

```python
from deepfix_sdk.data.datasets import TabularDataset

dataset_name = "my-tabular-dataset"

# Wrap train and test datasets
train_dataset = TabularDataset(
    dataset_name=dataset_name,
    data=df_train
)

test_dataset = TabularDataset(
    dataset_name=dataset_name,
    data=df_test
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
    train_test_validation=True,  # Validate train/test split
    data_integrity=True,          # Run data integrity checks
    overwrite=False               # Don't overwrite existing dataset
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

Here's a complete example with a typical tabular dataset:

```python
import pandas as pd
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.data.datasets import TabularDataset

# Initialize client
client = DeepFixClient(api_url="http://localhost:8844")

# Load tabular data
df_train = pd.read_csv("train_data.csv")
df_test = pd.read_csv("test_data.csv")

# Wrap datasets
dataset_name = "my-tabular-dataset"

train_dataset = TabularDataset(
    dataset_name=dataset_name,
    data=df_train
)

test_dataset = TabularDataset(
    dataset_name=dataset_name,
    data=df_test
)

# Ingest dataset
client.ingest(
    dataset_name=dataset_name,
    train_data=train_dataset,
    test_data=test_dataset,
    train_test_validation=True,
    data_integrity=True,
    overwrite=False
)

# Diagnose
result = client.diagnose_dataset(dataset_name=dataset_name)

# View analysis results
print(result.to_text())
```

## Advanced Usage

### Data Preprocessing

Preprocess your data before ingestion:

```python
import pandas as pd

# Load raw data
df_train = pd.read_csv("raw_train.csv")
df_test = pd.read_csv("raw_test.csv")

# Preprocessing steps
def preprocess(df):
    # Handle missing values
    df = df.fillna(df.median())
    
    # Encode categorical variables
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        df[col] = pd.Categorical(df[col]).codes
    
    # Normalize numerical features
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    df[numerical_cols] = (df[numerical_cols] - df[numerical_cols].mean()) / df[numerical_cols].std()
    
    return df

# Preprocess
df_train = preprocess(df_train)
df_test = preprocess(df_test)

# Now wrap and ingest
train_dataset = TabularDataset(dataset_name="preprocessed-dataset", data=df_train)
test_dataset = TabularDataset(dataset_name="preprocessed-dataset", data=df_test)
```

### Handling Large Datasets

For large tabular datasets, consider chunking:

```python
import pandas as pd

# Process in chunks
chunk_size = 10000
chunks_train = []

for chunk in pd.read_csv("large_train.csv", chunksize=chunk_size):
    chunks_train.append(chunk)

df_train = pd.concat(chunks_train, ignore_index=True)

# Or use Dask for very large datasets
import dask.dataframe as dd

ddf_train = dd.read_csv("very_large_train.csv")
df_train = ddf_train.compute()  # Convert to pandas
```

### Feature Engineering

Create new features before ingestion:

```python
import pandas as pd

def create_features(df):
    # Create interaction features
    df['feature_interaction'] = df['feature1'] * df['feature2']
    
    # Create polynomial features
    df['feature_squared'] = df['feature1'] ** 2
    
    # Create time-based features (if applicable)
    if 'timestamp' in df.columns:
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
    
    return df

df_train = create_features(df_train)
df_test = create_features(df_test)
```

### MLflow Integration

Track tabular data analysis in MLflow:

```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.config import MLflowConfig

# Configure MLflow
mlflow_config = MLflowConfig(
    tracking_uri="http://localhost:5000",
    experiment_name="tabular-analysis",
    run_name="my-dataset-analysis"
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

The diagnosis results for tabular data include:

### Dataset Statistics

- Row and column counts
- Feature distributions
- Data type information
- Missing value counts
- Unique value counts per feature

### Quality Issues

- Missing value patterns
- Outlier detection
- Feature correlation issues
- Data type inconsistencies
- Train/test distribution drift

### Recommendations

- Missing value handling strategies
- Outlier treatment suggestions
- Feature engineering recommendations
- Data preprocessing steps
- Model selection guidance

### Example Result Interpretation

```python
result = client.diagnose_dataset(dataset_name="my-dataset")

# Access dataset-specific findings
dataset_findings = result.agent_results.get("DatasetArtifactsAnalyzer", {}).findings
print("Dataset Findings:", dataset_findings)

# Access deepchecks results (if available)
deepchecks_findings = result.agent_results.get("DeepchecksArtifactsAnalyzer", {}).findings
print("Deepchecks Findings:", deepchecks_findings)

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

1. **Handle Missing Values**: Address missing values before ingestion
   ```python
   # Strategy 1: Fill with median/mean
   df = df.fillna(df.median())
   
   # Strategy 2: Drop columns with high missing rate
   missing_rate = df.isnull().sum() / len(df)
   df = df.drop(columns=missing_rate[missing_rate > 0.5].index)
   ```

2. **Outlier Detection**: Identify and handle outliers
   ```python
   from scipy import stats
   
   z_scores = stats.zscore(df[numerical_cols])
   outliers = (z_scores > 3).any(axis=1)
   df = df[~outliers]
   ```

3. **Feature Types**: Ensure correct data types
   ```python
   df['categorical'] = df['categorical'].astype('category')
   df['datetime'] = pd.to_datetime(df['datetime'])
   ```

### Train/Test Split Validation

1. **Distribution Alignment**: Ensure train/test distributions are similar
2. **Temporal Splits**: For time-series data, use temporal splits
3. **Stratified Splits**: For classification, use stratified splits

### Performance

1. **Memory Optimization**: Use appropriate data types
   ```python
   # Reduce memory usage
   df['int_col'] = df['int_col'].astype('int32')  # Instead of int64
   df['float_col'] = df['float_col'].astype('float32')  # Instead of float64
   ```

2. **Chunking**: Process large datasets in chunks
3. **Caching**: Cache preprocessed data when possible

## Troubleshooting

### Common Issues

**Problem**: Memory errors with large datasets

```python
# Solution: Process in chunks or use Dask
chunk_size = 10000
for chunk in pd.read_csv("large_file.csv", chunksize=chunk_size):
    # Process chunk
    process_chunk(chunk)
```

**Problem**: Missing values detected

```python
# Solution: Handle missing values before ingestion
# Option 1: Fill with median
df = df.fillna(df.median())

# Option 2: Drop missing rows
df = df.dropna()

# Option 3: Use imputation
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median')
df[numerical_cols] = imputer.fit_transform(df[numerical_cols])
```

**Problem**: Train/test distribution drift

```python
# Solution: Check distributions and adjust splits
from scipy import stats

# Compare distributions
for col in numerical_cols:
    statistic, p_value = stats.ks_2samp(
        df_train[col],
        df_test[col]
    )
    if p_value < 0.05:
        print(f"Drift detected in {col}")
```

**Problem**: Data type inconsistencies

```python
# Solution: Ensure consistent data types
# Convert to consistent types
df_train = df_train.astype(df_test.dtypes.to_dict())
```

### Performance Tips

1. **Use Parquet**: More efficient than CSV for large datasets
2. **Optimize Dtypes**: Use appropriate data types to reduce memory
3. **Categorical Encoding**: Use category dtype for categorical features
4. **Chunking**: Process large files in chunks

## Next Steps

- [Image Classification Guide](image-classification.md) - Work with image data
- [NLP Datasets Guide](nlp-datasets.md) - Analyze text datasets
- [MLflow Integration](mlflow-integration.md) - Track experiments
- [API Reference](../api-reference/index.md) - Complete API documentation

