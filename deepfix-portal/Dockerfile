FROM node:22-alpine AS frontend-builder
WORKDIR /app

# Install dependencies and build the React client
# Note: context is now root, so paths are relative to deepfix-portal/
COPY deepfix-portal/package-lock.json deepfix-portal/package.json ./
COPY deepfix-portal/tsconfig.json deepfix-portal/vite.config.ts deepfix-portal/vite-plugin-meta-images.ts deepfix-portal/postcss.config.js deepfix-portal/components.json ./
COPY deepfix-portal/client ./client
COPY deepfix-portal/shared ./shared
COPY deepfix-portal/attached_assets ./attached_assets
COPY deepfix-portal/script ./script
RUN npm install
RUN npm run build


FROM astral/uv:python3.11-bookworm-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_ENV=production

# System deps for compiling wheels like bcrypt/psycopg2, plus create non-root user
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/* \
 && adduser --disabled-password --no-create-home --gecos "" app

# Copy workspace structure (needed for uv to resolve workspace dependencies)
COPY pyproject.toml ./pyproject.toml
COPY deepfix-core ./deepfix-core
COPY deepfix-portal ./deepfix-portal

# Bring in the built frontend so FastAPI can serve it when NODE_ENV=production
COPY --from=frontend-builder /app/dist/public ./deepfix-portal/src/deepfix_portal/dist/public

# Install Python deps into a project-local venv
WORKDIR /app/deepfix-portal
RUN uv venv .venv
RUN uv pip install ../deepfix-core \
    && uv pip install . \
    && uv pip install opentelemetry-distro opentelemetry-exporter-otlp\
    && uv run opentelemetry-bootstrap -a requirements | uv pip install --requirement -

# Create .deepfix directory with proper permissions for the app user
RUN mkdir -p /app/deepfix-portal/.deepfix && chown -R app:app /app/deepfix-portal/.deepfix

USER app
ENV PATH="/app/deepfix-portal/.venv/bin:${PATH}"
ENV NODE_ENV=
ENV DEEPFIX_HOME=/app/deepfix-portal/.deepfix

EXPOSE 5041

# Start the FastAPI app (serves API and static assets)
CMD ["opentelemetry-instrument","uvicorn", "deepfix_portal.api.main:app", "--host", "0.0.0.0", "--port", "5041"]
