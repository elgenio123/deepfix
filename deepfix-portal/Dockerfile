FROM node:22-alpine AS frontend-builder
WORKDIR /app

# Install dependencies and build the React client
COPY package-lock.json package.json ./
COPY tsconfig.json vite.config.ts vite-plugin-meta-images.ts postcss.config.js components.json ./
COPY client ./client
COPY shared ./shared
COPY attached_assets ./attached_assets
# Need dev deps (vite) during build even though final image is production
RUN npm ci --include=dev
RUN npx vite build


FROM astral/uv:python3.11-bookworm-slim AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NODE_ENV=production

# System deps for compiling wheels like bcrypt/psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy backend source and lockfiles
COPY pyproject.toml ./
COPY src ./src
# Bring in the built frontend so FastAPI can serve it when NODE_ENV=production
COPY --from=frontend-builder /app/dist/public ./src/deepfix_portal/dist/public

# Install Python deps into a project-local venv
RUN uv sync --frozen --no-dev --no-progress
ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 5041

# Start the FastAPI app (serves API and static assets)
CMD ["uv", "run", "uvicorn", "deepfix_portal.api.main:app", "--host", "0.0.0.0", "--port", "5041"]
