# 🔍 DeepFix

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![MLflow](https://img.shields.io/badge/MLflow-3.0+-orange.svg)](https://mlflow.org/)
[![PyTorch Lightning](https://img.shields.io/badge/PyTorch%20Lightning-2.0+-yellow.svg)](https://pytorch-lightning.readthedocs.io/)

DeepFix is an AI agent assistant that automatically diagnoses common bugs in machine learning and provides a prioritized list of solutions backed by industry/research best practices. It integrates directly into ML workflows.

## ✨ Features

- **Automatic Bug Detection**: Identifies common ML issues automatically
- **Prioritized Solutions**: Get ranked suggestions based on best practices
- **Workflow Integration**: Seamlessly works with PyTorch Lightning and MLflow
- **Research-Backed**: Solutions are grounded in industry standards and research

## 🚀 Quick Start

### Installation

#### Option 1: Docker (Recommended for Server Deployment)

```bash
# Clone the repository
git clone https://github.com/delcaux-labs/deepfix.git
cd deepfix

# Copy environment example and configure
cp env.example .env
# Edit .env with your API keys

# Start the server using docker-compose
docker-compose up -d

# Or using Make
make docker-compose-up
```

See [Docker Deployment Guide](docs/DOCKER.md) for detailed instructions.

#### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/delcaux-labs/deepfix.git
cd deepfix

# Install with uv (recommended)
uv venv --python 3.11
uv pip install -e .
```

## Basic Usage

### Deploy deepfix server
```python
uv run  deepfix-server launch -e deepfix-server/.env -port 8844 -host 127.0.0.1
```

### Diagnose image classification dataset
```python
from deepfix_sdk.client import DeepFixClient
from deepfix_sdk.zoo.datasets.foodwaste import load_train_and_val_datasets
from deepfix_sdk.data.datasets import ImageClassificationDataset

client = DeepFixClient(api_url="http://deepfix.delcaux.com",timeout=120)

# Load image dataset
dataset_name="cafetaria-foodwaste"

train_data, val_data = load_train_and_val_datasets(
    image_size=448,
    batch_size=8,
    num_workers=4,
    pin_memory=False,)
train_data = ImageClassificationDataset(dataset_name=dataset_name, dataset=train_data)
val_data = ImageClassificationDataset(dataset_name=dataset_name, dataset=val_data)

# Ingest dataset
client.ingest(dataset_name=dataset_name,
                    train_data=train_data,
                    test_data=val_data,
                    train_test_validation=True,
                    data_integrity=True,
                    batch_size=8,
                    overwrite=False
                    )

# Diagnose dataset
result = client.diagnose_dataset(dataset_name=dataset_name)

# Visualize results
print(result.to_text())
```

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/delcaux-labs/deepfix/issues)
- **Email**: Contact us at fadel.seydou@delcaux.com

---

**Built with ❤️ for the ML community**