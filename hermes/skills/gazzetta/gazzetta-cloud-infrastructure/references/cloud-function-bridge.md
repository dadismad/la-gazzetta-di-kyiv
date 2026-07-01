# Cloud Function Bridge — CEO → Hermes Communication

Deployed as `gcf_governor_bridge.py` at project root `scripts/`.

## Architecture

```
CEO (VM governor.py)  →  HTTP POST  →  Cloud Function  →  Hermes Webhook
                                        │
                                        └── Writes response to GCS: gs://BUCKET/_governor/inbox/<ts>.json
```

The Cloud Function bridges the CEO (running on the VM with restricted networking) and Hermes (running on Alex's MacBook behind NAT). Instead of SSH-polling the mailbox (fragile, requires VM to be reachable), the CEO POSTs to the Cloud Function when it has a critical directive for Hermes.

## Deployment

```bash
gcloud functions deploy governor-bridge \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --region us-central1 \
  --entry-point handle_request \
  --set-env-vars HERMES_WEBHOOK_URL=<your_webhook_url>
```

## Required env var

- `HERMES_WEBHOOK_URL` — HTTP endpoint where Hermes listens for directives

## On the VM (governor.py)

Set `GCF_GOVERNOR_BRIDGE_URL` in `/opt/gazzetta-di-kyiv/.env`:
```
GCF_GOVERNOR_BRIDGE_URL=https://<region>-<project>.cloudfunctions.net/governor-bridge
```

The governor calls `notify_hermes(directive, context, priority)` which POSTs to this URL.

## Test

```bash
curl -X POST https://<region>-<project>.cloudfunctions.net/governor-bridge \
  -H "Content-Type: application/json" \
  -d '{"directive": "Hermes, the Energy narrative needs new RSS sources", "from": "CEO", "priority": "medium"}'
```
