#!/usr/bin/env python3
"""
gcf_governor_bridge.py — Cloud Function v1.0
Bridges the CEO (VM Governor) and Hermes (MacBook) via HTTP.

Deploy as a Google Cloud Function (2nd gen, Python 3.11+).
Trigger: HTTP (authenticated or public, your choice).
Runtime env vars: HERMES_WEBHOOK_URL (where Hermes listens)

Flow:
  1. CEO governor.py POSTs to this function when it has a directive for Hermes
     e.g., "Hermes, I need a new data source for Orbital Infrastructure"
  2. This function forwards to Hermes' webhook
  3. Hermes processes the request and responds
  4. Response gets written back to the VM's mailbox inbox.json

CLOUD FUNCTION URL (after deploy):
  https://<region>-<project>.cloudfunctions.net/governor-bridge
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Config from env vars ──
HERMES_WEBHOOK_URL = os.environ.get("HERMES_WEBHOOK_URL", "")
VM_SSH_HOST = os.environ.get("VM_SSH_HOST", "34.132.179.205")
VM_SSH_USER = os.environ.get("VM_SSH_USER", "gazzetta")
MAILBOX_PATH = "/opt/gazzetta-di-kyiv/mailbox/inbox.json"

def forward_to_hermes(directive: dict) -> dict:
    """
    Send a CEO directive to Hermes via webhook.
    
    directive = {
        "from": "CEO / Sovereign Auditor",
        "priority": "high|medium|low",
        "type": "request_tool | report_finding | escalate",
        "content": "Hermes, I need a new RSS source for Space Economy...",
        "context": {...}   # optional pipeline context
    }
    """
    if not HERMES_WEBHOOK_URL:
        return {"ok": False, "error": "HERMES_WEBHOOK_URL not configured"}
    
    payload = json.dumps(directive).encode()
    req = urllib.request.Request(
        HERMES_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return {"ok": True, "hermes_response": json.loads(resp.read().decode())}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def write_to_mailbox(message: dict) -> bool:
    """
    Write a response back to the VM's mailbox.
    Requires gcloud SSH access or a shared filesystem (NFS, GCS FUSE).
    
    ALTERNATIVE APPROACH: Use GCS as intermediary.
    Write to gs://www.lagazzettadikyiv.com/_governor/inbox/<timestamp>.json
    Governor polls this bucket.
    """
    # For now: write to GCS as intermediary
    # (Simpler than SSH from Cloud Function — no SSH keys in cloud env)
    import subprocess
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    gcs_path = f"gs://www.lagazzettadikyiv.com/_governor/inbox/{ts}.json"
    
    try:
        proc = subprocess.run(
            ["gsutil", "cp", "-", gcs_path],
            input=json.dumps(message).encode(),
            capture_output=True,
            timeout=15
        )
        return proc.returncode == 0
    except Exception:
        return False


def handle_request(request):
    """
    Cloud Function entry point.
    
    Called by CEO governor.py when it wants to:
    - Request a new tool/script from Hermes
    - Report a critical finding
    - Ask for configuration changes
    """
    # Parse incoming request
    try:
        data = request.get_json(silent=True) or {}
    except Exception:
        data = {}
    
    directive = data.get("directive", "")
    sender = data.get("from", "CEO")
    
    if not directive:
        return ("Missing 'directive' field", 400)
    
    # Forward to Hermes
    result = forward_to_hermes({
        "from": "CEO / Sovereign Auditor",
        "content": directive,
        "context": data.get("context", {}),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Write response to VM mailbox via GCS
    write_to_mailbox({
        "to": "governor",
        "from": "Hermes",
        "directive": directive,
        "response": result,
        "at": datetime.now(timezone.utc).isoformat()
    })
    
    return (json.dumps(result), 200)


# ═══════════════════════════════════════════════════════
# DEPLOYMENT COMMANDS (run from Alex's MacBook):
# ═══════════════════════════════════════════════════════
#
# 1. Deploy the Cloud Function:
#    gcloud functions deploy governor-bridge \
#      --runtime python311 \
#      --trigger-http \
#      --allow-unauthenticated \
#      --region us-central1 \
#      --entry-point handle_request \
#      --set-env-vars HERMES_WEBHOOK_URL=<your_webhook_url>
#
# 2. Get the function URL:
#    gcloud functions describe governor-bridge --region us-central1 --format='value(url)'
#
# 3. Test:
#    curl -X POST https://<region>-<project>.cloudfunctions.net/governor-bridge \
#      -H "Content-Type: application/json" \
#      -d '{"directive": "Hermes, the Energy narrative needs new RSS sources", "from": "CEO"}'
