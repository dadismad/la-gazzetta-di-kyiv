# Dockerfile — Gazzetta di Kyiv Cloud Run Pipeline
# Build: gcloud builds submit --tag gcr.io/PROJECT/gazzetta-pipeline:latest

FROM python:3.11-slim

WORKDIR /app

# Install system deps for sqlite3 and ca-certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --no-cache-dir google-cloud-storage google-cloud-secret-manager beautifulsoup4

# Copy pipeline scripts
COPY scripts/ /app/scripts/
COPY ops/ /app/ops/
COPY templates/ /app/templates/
COPY data/ /app/data/
COPY public/ /app/public/
COPY deploy_routine.sh /app/

# Copy config (path references are relative to project root)
COPY config.yaml /app/

# Create data directories
RUN mkdir -p /app/public/data/locales /app/public/api/v1/home

# Copy locale templates
RUN cp /app/templates/locales/*.json /app/public/data/locales/ 2>/dev/null || true

# Make scripts executable
RUN chmod +x /app/deploy_routine.sh

# Cloud entrypoint
COPY cloud_entrypoint.py /app/
RUN chmod +x /app/cloud_entrypoint.py

ENTRYPOINT ["python3", "/app/cloud_entrypoint.py"]
