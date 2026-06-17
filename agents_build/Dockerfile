# Dockerfile — Gazzetta di Kyiv Cloud Run Agents (CCO + CDO)
# Build: gcloud builds submit --tag europe-west1-docker.pkg.dev/PROJECT/gazzetta-docker/gazzetta-agents:latest . --config=agents_build/cloudbuild.yaml

FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --no-cache-dir google-cloud-storage google-cloud-secret-manager beautifulsoup4

# Copy agent scripts
COPY agents_build/ /app/

# Create data directories
RUN mkdir -p /app/data /app/logs /app/cco_drafts

RUN chmod +x /app/cco_entrypoint.py /app/cdo_entrypoint.py

# Default: CCO entrypoint (overridden per Cloud Run job)
ENTRYPOINT ["python3", "/app/cco_entrypoint.py"]
