#!/usr/bin/env python3
"""Deploy public/ to GCS without gsutil multiprocessing issues.
Uses google-cloud-storage library directly. Works under systemd restrictions.
"""
import os, sys, subprocess
from pathlib import Path
from google.cloud import storage

PROJECT_ROOT = Path(os.environ.get("GAZZETTA_HOME", "/opt/gazzetta-di-kyiv"))
PUBLIC = PROJECT_ROOT / "public"
BUCKET_NAME = "www.lagazzettadikyiv.com"

def upload_file(bucket, local_path: Path, remote_name: str, cache_control: str):
    """Upload a single file with Cache-Control header."""
    blob = bucket.blob(remote_name)
    blob.cache_control = cache_control
    blob.upload_from_filename(str(local_path))
    print(f"  ✓ {remote_name} ({cache_control})")

def sync_directory(bucket, local_dir: Path, exclude: set):
    """Sync all files in local_dir to bucket root, excluding given filenames."""
    uploaded = 0
    for local_file in local_dir.rglob("*"):
        if local_file.is_dir():
            continue
        rel = str(local_file.relative_to(local_dir))
        if rel in exclude:
            continue
        blob = bucket.blob(rel)
        blob.upload_from_filename(str(local_file))
        uploaded += 1
    print(f"  ✓ synced {uploaded} files")

def invalidate_cdn():
    """Invalidate CDN cache (best-effort)."""
    try:
        subprocess.run(
            ["/usr/bin/gcloud", "compute", "url-maps", "invalidate-cdn-cache",
             "gazzetta-url-map", "--path=/*", "--async"],
            capture_output=True, timeout=30
        )
        print("  ✓ CDN invalidation triggered")
    except Exception as e:
        print(f"  ⚠ CDN invalidation skipped: {e}")

def main():
    print("[deploy_to_gcs] starting...")
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # 1. flows.json — no-store
    flows = PUBLIC / "data" / "flows.json"
    if flows.exists():
        upload_file(bucket, flows, "data/flows.json",
                    "no-store,no-cache,must-revalidate")

    # 2. index.html — no-cache
    index_html = PUBLIC / "index.html"
    if index_html.exists():
        upload_file(bucket, index_html, "index.html",
                    "no-cache,no-store,must-revalidate,max-age=0")

    # 3. Sync everything else
    sync_directory(bucket, PUBLIC, exclude={"index.html"})

    # 4. CDN invalidation (best-effort)
    invalidate_cdn()

    print("[deploy_to_gcs] done.")

if __name__ == "__main__":
    main()
