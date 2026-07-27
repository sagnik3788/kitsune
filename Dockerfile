# Build the dashboard SPA
FROM node:20-alpine AS builder
WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm ci
COPY dashboard/ ./
ARG VITE_CLERK_PUBLISHABLE_KEY
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY
RUN npm run build

# Runtime
FROM python:3.12-slim
WORKDIR /app

# Install system deps for asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    redis \
    python-dotenv \
    clerk-backend-api \
    svix \
    asyncpg \
    pyyaml \
    pydantic

# Copy backend code
COPY engine.py schema.py db.py gateway.py ./

# Copy built frontend from builder
COPY --from=builder /app/dashboard/dist ./dashboard/dist

EXPOSE 8000
CMD ["python", "gateway.py"]
