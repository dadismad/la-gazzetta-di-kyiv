#!/usr/bin/env python3
"""
cloud_entrypoint.py — Gazzetta di Kyiv Cloud Run pipeline wrapper

1. Fetches DEEPSEEK_API_KEY from Secret Manager
2. Downloads gazzetta.db from GCS (if exists)
3. Runs deploy_routine.sh (which skips GCS ops in cloud mode)
4. Uploads gazzetta.db + public/ back to GCS
"""

import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# GCP clients — available in container, not locally
from google.cloud import storage  # type: ignore
from google.cloud import secretmanager_v1  # type: ignore

PROJECT_ID = os.environ.get("GCP_PROJECT", "project-e5e0244c-b94d-41a1-810")
BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
SECRET_NAME = os.environ.get("SECRET_NAME", "deepseek-api-key")
APP_DIR = Path("/app")
DB_FILE = APP_DIR / "gazzetta.db"
PUBLIC_DIR = APP_DIR / "public"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_secret() -> str:
    client = secretmanager_v1.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{SECRET_NAME}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8").strip()


def download_db():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob("gazzetta.db")
    if blob.exists():
        size = blob.size
        print(f"[{now()}] Downloading gazzetta.db from GCS ({size} bytes)")
        blob.download_to_filename(str(DB_FILE))
        local_size = DB_FILE.stat().st_size if DB_FILE.exists() else 0
        print(f"[{now()}] Downloaded — local size: {local_size}")
    else:
        print(f"[{now()}] No gazzetta.db in GCS — starting with local copy")


def upload_db():
    if not DB_FILE.exists():
        print(f"[{now()}] No gazzetta.db to upload — skipping")
        return
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob("gazzetta.db")
    size = DB_FILE.stat().st_size
    blob.upload_from_filename(str(DB_FILE))
    print(f"[{now()}] Uploaded gazzetta.db to GCS ({size} bytes)")


def sync_public():
    """Upload public/ directory to GCS using google-cloud-storage."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    
    if not PUBLIC_DIR.exists():
        print(f"[{now()}] public/ not found — skipping sync")
        return
    
    uploaded = 0
    for fpath in PUBLIC_DIR.rglob("*"):
        if fpath.is_file():
            rel = str(fpath.relative_to(PUBLIC_DIR))
            blob = bucket.blob(rel)
            
            # Cache policy
            cache = "public, max-age=0, must-revalidate"
            if rel.endswith(".json"):
                cache = "private, no-store"
            elif rel.endswith((".css", ".js")):
                cache = "public, max-age=31536000, immutable"
            
            blob.cache_control = cache
            blob.upload_from_filename(str(fpath))
            uploaded += 1
    
    print(f"[{now()}] Synced {uploaded} files from public/ to GCS")


def run_pipeline() -> int:
    env = os.environ.copy()
    # Signal to deploy_routine.sh that it's running in Cloud Run
    env["CLOUD_RUN"] = "1"
    
    cmd = ["bash", str(APP_DIR / "deploy_routine.sh")]
    print(f"[{now()}] Running pipeline...")
    result = subprocess.run(cmd, env=env, cwd=str(APP_DIR), text=True)
    return result.returncode


def main():
    print(f"[{now()}] cloud_entrypoint.py starting — project={PROJECT_ID}")
    
    # 1. Fetch secrets
    try:
        api_key = fetch_secret()
        os.environ["DEEPSEEK_API_KEY"] = api_key
        print(f"[{now()}] DEEPSEEK_API_KEY loaded from Secret Manager")
    except Exception as e:
        print(f"[{now()}] WARNING: Failed to fetch secret: {e}")
    
    # 2. Download DB from GCS
    try:
        download_db()
    except Exception as e:
        print(f"[{now()}] WARNING: DB download failed: {e}")
    
    # 3. Run pipeline
    exit_code = run_pipeline()
    print(f"[{now()}] Pipeline exit code: {exit_code}")
    
    # 4. Upload DB + public/ to GCS
    if exit_code == 0:
        try:
            sync_public()
        except Exception as e:
            print(f"[{now()}] WARNING: GCS upload failed: {e}")
    else:
        print(f"[{now()}] Skipping GCS upload — pipeline failed (exit={exit_code})")
    
    print(f"[{now()}] cloud_entrypoint.py complete")
    sys.exit(0 if exit_code == 0 else 1)


if __name__ == "__main__":
    main()
