# Multi-Vector Narrative Scoring — Architecture Refactor (June 2026)

## What Changed

Migrated from 1-story-1-narrative tagging to 12-vector weighted scoring matrix.
DeepSeek now scores every article against ALL 12 macro vectors simultaneously (0.0-1.0).
A story appears in every container where its score >= 0.40.

## Architecture

```
Ingestion → DeepSeek (12-vector scores) → assemble (containers_list) 
→ merge (multi-bucket append) → classify (bypass weighted, keyword legacy)
→ calculate_capital → build_frontend
```

## Files Patched

### contradiction_synthesizer.py (11 patches)
- SYSTEM_PROMPT: single `narrative_tag` → `narrative_scores` dict (12 float keys)
- Proportionality constraint: "asset-allocation weighting, not binary tag"
- pick_market_context(): expanded to iterate ALL 12 vectors with labeled blocks
- build_user_prompt(): stripped pre-assigned narrative_tag hint
- assemble_story(): extracts scores matrix, sets primary + containers_list + narrative_weights
- merge_stories(): multi-bucket append (loops containers list)
- Capping: per primary container only (avoids capital inflation)
- max_tokens: 800 → 1200 (matrix response is larger)
- run(): single full-market context call, not per-tag

### classify_stories.py (3 patches)
- DeepSeek bypass: stories with `narrative_weights` skip keyword matching
- tags_index: indexes by `containers` list for multi-vector stories
- GAZZETTA_HOME: path resolution via env var (was hardcoded /opt/gazzetta-di-kyiv)

## Key Data Fields (New)

| Field | Type | Description |
|---|---|---|
| narrative_weights | dict[12] | Full 0.0-1.0 scores from DeepSeek |
| containers | list[str] | Vectors scoring >= 0.40 |
| narrative_confidence | float | Score of primary vector (not hardcoded) |
| container | str | Primary vector (backward compat) |
| narrative_id | str | Primary vector (classifier compat) |

## 0.40 Threshold

Intentionally selective. A lunar economy article (space_economy 0.9) with tech_convergence 0.3 
and deglobalization 0.2 ripples will ONLY appear in space_economy container.
An Iran reconstruction article (energy_sovereignty 0.8, tech_convergence 0.6, ai_chips 0.5)
appears in 3 containers. Capital volume is capped at primary — no double-counting across buckets.

## Production Deployment Pitfalls

### governor.py DEEPSEEK_API_KEY export
The governor loads `DEEPSEEK_KEY` via Secret Manager into a Python variable but NEVER exports
it to `os.environ`. Subprocesses (contradiction_synthesizer.py) read from `os.environ`.
Fix: add `os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_KEY` after secret loading in governor.py.

### .env permissions
Production .env was 777 root:root. Lock to 600 gazzetta:gazzetta.
`sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/.env && sudo chmod 600 /opt/gazzetta-di-kyiv/.env`

### VM IP cycling
GCP ephemeral IPs change on VM restart. Current: 35.232.28.188.
SSH key: ~/.ssh/google_compute_engine. Config entry:
```
Host gazzetta-prod
    HostName <current-ip>
    User alexstocchi
    IdentityFile ~/.ssh/google_compute_engine
```
Check IP: `gcloud compute instances describe gazzetta-prod --zone=us-central1-a --format='json(networkInterfaces[0].accessConfigs[0].natIP)'`

### classify_stories.py local testing
Script hardcodes `/opt/gazzetta-di-kyiv/data`. Set `GAZZETTA_HOME` for local runs.
Also applies to calculate_capital.py and other pipeline scripts.

## Verification Pattern

After deploy, run governor cycle + verify:
```python
weighted = [s for s in d['all_stories'] if s.get('narrative_weights')]
# Should increase over time as DeepSeek processes more articles
```
