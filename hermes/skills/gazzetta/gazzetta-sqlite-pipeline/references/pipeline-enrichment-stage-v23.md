# shipit.sh Pipeline — v23.0 Enrichment Stage

## Current 8-Stage Pipeline

```
Stage 1:   db_to_json (DB → JSON compilation)
Stage 1.5: enrich_editorial_stories + ensure_generated_at + generate_signal_api + generate_trades_api
Stage 2:   build_site
Stage 2.5: test_platform (142 assertions)
Stage 3:   hash_assets (SHA256 content hashing)
Stage 4:   GCS deploy (gsutil rsync + setmeta per cache tier)
Stage 5:   live verify (curl HTTP 200)
Stage 6:   deploy_report
Stage 7:   git sync
```

## Stage 1.5 Scripts

| Script | Purpose |
|--------|---------|
| `enrich_editorial_stories.py` | Adds capital_flow + generated_at to editorial writer stories (which lack both) |
| `ensure_generated_at.py` | Guarantees every story in stories.json has a generated_at field |
| `generate_signal_api.py` | Produces api/v1/signal.json — 35 triangulation signals |
| `generate_trades_api.py` | Produces api/v1/trades.json — 13 tradFi + crypto positions |

## Key Insight

Stage 1.5 runs before build_site. This means the enriched data flows through the entire chain — build_site sees complete stories, test_platform validates complete data, and GCS gets complete JSON.

Previously, editorial writer stories arrived without capital_flow dicts, causing story time badges to render empty and flows to skip those stories entirely. The enrichment stage bridges this two-generation-path gap.

## Cron Integration

- `f9a24ed64aa5` (deploy-to-gcs, every 60m) — runs `shipit.sh` (was `gazzetta_deploy_to_gcs.sh`)
- `51c1bb776729` (capital-flows, every 60m) — runs `scripts/generate_flows.py` (was `pipeline_chain.sh`)
