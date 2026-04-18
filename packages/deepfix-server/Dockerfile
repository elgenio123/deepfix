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
COPY packages/deepfix-server ./packages/deepfix-server
COPY packages/deepfix-core ./packages/deepfix-core
COPY packages/deepfix-kb ./packages/deepfix-kb

COPY pyproject.toml ./pyproject.toml

#RUN . /opt/venv/bin/activate \
#    && uv pip install -r deepfix-server/pyproject.toml

# Install project into the venv (non-editable)
RUN . /opt/venv/bin/activate \
    && uv pip install ./packages/deepfix-server \
    && uv pip install pip \
    && uv pip install opentelemetry-distro opentelemetry-exporter-otlp\
    && uv pip install ./packages/deepfix-core && opentelemetry-bootstrap -a requirements | uv pip install --requirement -

###############
# Runtime stage
###############
FROM python:3.11-slim-bookworm AS runtime

LABEL maintainer="fadel.seydou@delcaux.com"
LABEL version="0.0.1"
LABEL description="deepfix-server"

# Install runtime dependencies including curl for health checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       openssh-client \
       curl \
       tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} deepfix \
    && useradd -u ${UID} -g deepfix -m -s /bin/bash deepfix

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Ensure venv takes precedence
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Expose ports
EXPOSE 8844

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8844/health || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Switch to non-root user
USER deepfix

CMD ["deepfix-server", "launch", "-port", "8844", "-host", "0.0.0.0", "-workers", "2", "-fast-queue"]
