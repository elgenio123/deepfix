# Multi-stage Dockerfile for DeepFix Server
# Optimized for production deployment with smaller image size and faster builds

# Stage 1: Builder stage
FROM astral/uv:python3.11-bookworm-slim AS builder

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR /app

# Create virtual environment
RUN uv venv /opt/venv

# Install dependencies into the venv first (use lock/info from pyproject)
COPY deepfix-server ./deepfix-server
COPY deepfix-core ./deepfix-core

COPY pyproject.toml ./

RUN . /opt/venv/bin/activate \
    && uv pip install -r deepfix-server/pyproject.toml

# Install project into the venv (non-editable)
RUN . /opt/venv/bin/activate \
    && uv pip install ./deepfix-server \
    && uv pip install ./deepfix-core

###############
# Runtime stage
###############
FROM python:3.11-slim-bookworm AS runtime

LABEL maintainer="fadel.seydou@delcaux.com"
LABEL version="0.0.1"
LABEL description="deepfix-server"

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Ensure venv takes precedence
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

EXPOSE 8844 5000 8841
RUN mkdir -p /logs && mkdir -p /mlflow
VOLUME /logs /mlflow

COPY start_server_docker.sh .
RUN chmod +x start_server_docker.sh

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://cursor.com/install -o /app/cursor-install.sh && \
    sh /app/cursor-install.sh --install-dir /usr/local/bin && \
    rm /app/cursor-install.sh

CMD ["./start_server_docker.sh"]
