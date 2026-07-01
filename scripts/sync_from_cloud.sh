#!/bin/bash
set -e

# Syncs the cloud GCS bucket down to the local ~/.gemini/antigravity folder.

BUCKET="gs://gazzetta-antigravity-sync"
LOCAL_DIR="$HOME/.gemini/antigravity"

# Create directory if it doesn't exist
mkdir -p "$LOCAL_DIR"

echo "=========================================================="
echo "Downloading Antigravity settings & history from Google Cloud..."
echo "=========================================================="

# Run rsync with delete unmatched so local exactly mirrors cloud
gcloud storage rsync -r --delete-unmatched-destination-objects "$BUCKET" "$LOCAL_DIR"

echo ""
echo "Success! Your local Antigravity session has been updated with the cloud state."
echo "Please restart or reload your Antigravity IDE to load the synced history."
