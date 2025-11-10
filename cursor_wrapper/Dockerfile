FROM python:3.11-slim-bookworm

LABEL maintainer="fadel.seydou@delcaux.com"
LABEL version="0.0.1"
LABEL description="deepfix-server"

WORKDIR /app

EXPOSE 8841
RUN mkdir -p /logs
VOLUME /logs

COPY app.py .

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://cursor.com/install -o /app/cursor-install.sh && \
    sh /app/cursor-install.sh --install-dir /usr/local/bin && \
    rm /app/cursor-install.sh

RUN pip install litserve pydantic

CMD ["python", "app.py"]
