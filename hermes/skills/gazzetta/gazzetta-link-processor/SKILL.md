---
name: gazzetta-link-processor
description: Process a URL into a classified story for La Gazzetta di Kyiv. When the user sends a URL in the Stocchi Labs chat, run this to classify, store, and deploy.
category: gazzetta
---

# Gazzetta Link Processor

## Trigger
User sends a URL in the chat. Extract the URL and process it.

## Steps

1. **Process the URL:**
   ```
   cd /Users/alexstocchi/lagazzettadikyiv && python3 scripts/link_processor.py "<URL>"
   ```

2. **If successful**, the script:
   - Fetches the page content
   - Extracts title, source domain
   - Classifies into 1 of 6 containers (monetary_order, energy_resources, technology_ai, information_narrative, biosecurity_health, flashpoints)
   - Assigns power-vector tags if applicable
   - Writes to gazzetta.db
   - Runs `PRAGMA wal_checkpoint(TRUNCATE)`
   - Uploads DB to GCS (www.lagazzettadikyiv.com/gazzetta.db)

3. **After DB upload**, trigger pipeline deploy:
   - The 10-min cron `gazzetta-pipeline-cron` will pick it up automatically
   - Or run manually: `gcloud run jobs execute gazzetta-pipeline --region=europe-west1 --project=project-e5e0244c-b94d-41a1-810 --wait`

4. **Report** the container classification and any tags back to the user.

## Important Notes
- The script uses `--dry-run` for preview without writing to DB
- Use `--instant` flag to trigger immediate `db_to_json.py` run after DB write (otherwise wait for the 10-min pipeline cron)
- Most news sites block automated requests (Reuters, Bloomberg). Use `--stdin` mode with manually pasted content for those
- The 10-minute pipeline cron auto-deploys new stories
- **PITFALL — full_json format must match pipeline expectations:** On 2026-06-16 the script was fixed to include all 28 required fields (`source`, `they_say`, `reality`, `multi_persona`, `capital_flow`, `evidence`, `entity_tags`, `time_decay`, `body`, etc.). If link_processor stops working, check that `write_to_db()` produces the full 28-field JSON — a format mismatch silently breaks the CCO/distribution pipeline. The canonical format is in `scripts/link_processor.py` lines 165-195.
