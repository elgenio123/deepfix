FROM python:3.11-slim-bookworm

LABEL maintainer="fadel.seydou@delcaux.com"
LABEL version="0.0.1"
LABEL description="deepfix-server"

WORKDIR /app

EXPOSE 8841
RUN mkdir -p /logs
VOLUME /logs

COPY app.py .

RUN apt-get update && apt-get install -y \
    curl \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install cursor-agent using the official installation script
RUN curl https://cursor.com/install -fsS | bash

# Ensure cursor-agent is in PATH
ENV PATH="/root/.local/bin:${PATH}"

# Verify installation
RUN cursor-agent --version

RUN pip install litserve pydantic rich

CMD ["python", "app.py"]
