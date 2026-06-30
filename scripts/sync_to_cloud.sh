#!/bin/bash
set -e

# Syncs the local ~/.gemini/antigravity folder to the GCS bucket.
# Exclude the scratch directory if you don't want to sync temporary scratch files.
# For now, we sync everything including brains, conversations, and state.

BUCKET="gs://gazzetta-antigravity-sync"
LOCAL_DIR="$HOME/.gemini/antigravity"

if [ ! -d "$LOCAL_DIR" ]; then
    echo "Error: Local Antigravity folder $LOCAL_DIR not found."
    exit 1
fi

echo "=========================================================="
echo "Syncing local Antigravity settings & history to Google Cloud..."
echo "=========================================================="

# Run rsync with delete unmatched so cloud exactly mirrors local
gcloud storage rsync -r --delete-unmatched-destination-objects "$LOCAL_DIR" "$BUCKET"

echo ""
echo "Success! Your workspace session has been saved to the cloud."
echo "You can now run 'scripts/sync_from_cloud.sh' on your other laptop to retrieve it."
