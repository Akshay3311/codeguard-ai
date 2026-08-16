# Multi-stage Dockerfile for CodeGuard AI
# Stage 1: Build Frontend Assets
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Backend & Static Server
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (git for repo cloning)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code and knowledge documents
COPY backend/app/ ./app/
COPY data/ ./data/

# Copy built frontend assets to static directory
COPY --from=frontend-builder /frontend/dist ./static

# Expose FastAPI port
EXPOSE 8000

ENV PYTHONPATH=/app
ENV STORAGE_DIR=/app/storage

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
