# 8-Narrative Migration — June 2026

## What Changed

Moved from 6 legacy containers to 8 narrative containers, parallel to the configuration in `config.yaml`:

| # | Old Container | New Narrative | Mapping Logic |
|---|--------------|---------------|---------------|
| 1 | monetary_order | dollar_decline | USD reserve erosion, BTC, CBDCs |
| 2 | energy_resources | energy_sovereignty | Fusion, rare earths, grid independence |
| 3 | flashpoints | deglobalization | Supply chain fragmentation, sanctions |
| 4 | technology_ai | tech_convergence | AI + quantum + biotech intersection |
| 5 | technology_ai | china_ascent | Parallel tech stack, BRI, semiconductors |
| 6 | technology_ai | space_economy | Orbital infrastructure, satellite internet |
| 7 | biosecurity_health | gene_editing | CRISPR, longevity biotech |
| 8 | information_narrative | wealthy_sports | Sovereign wealth in teams, soft power |

## Files That Must Be Updated Together

These three files MUST stay in sync. Changing container names in one without the other two causes validation failures:

| File | Role | What to Update |
|------|------|---------------|
| `scripts/db_to_json.py` | Compiles DB → stories.json | `CONTAINER_META` dict (names + sort orders) |
| `scripts/test_platform.py` | QA gate — blocks deploy | `VALID_CONTAINERS` set + container count check |
| `scripts/migrate_v1_to_v2.py` | DB migration | `OLD_TO_NEW` mapping dict |
| `public/dashboard.js` | Frontend renderer | `NARRATIVES` object (8 entries) |
| `public/index.html` | Page structure | Container HTML + `dashboard.js` script ref |

## Migration Execution (idempotent)

```bash
python3 scripts/migrate_v1_to_v2.py
```

This updates:
- `stories.container` column (old name → new narrative)
- `stories.full_json` → `story["container"]` → new narrative
- `story["capital_volume_usd"]` → $100M baseline
- `story["contradiction_gap"]` → 15 (baseline, neutral)
- Output: regenerated `data/stories.json` + synced to `public/data/`

## Post-Migration Orphan Purge

After migration, purge orphaned relational data:

```sql
DELETE FROM story_tags;      -- old 6-container tag references
DELETE FROM story_flow_links; -- old flow-to-story links
DELETE FROM flows;            -- old flow entries
```

Keep `ingestion_hashes` intact — those are for the synthesizer pipeline.

## Validation Gate

```bash
python3 scripts/test_platform.py
```

Must return `VERDICT: PASS — 94 checks passed` with exactly 8 container names validated.

## Common Failure Modes

1. **total_stories != container sum**: One or more stories has a container value not in the 8 valid names. Find with: `python3 -c "import json; d=json.load(open('data/stories.json')); valid={'dollar_decline',...}; print([s['container'] for s in d['all_stories'] if s['container'] not in valid])"` — then delete the orphan row from gazzetta.db.

2. **GCS CDN staleness**: `gsutil cp` succeeds but live site serves old data. Use versioned filename (stories-v2.json) to bypass CDN. Update dashboard.js fetch URL to match.

3. **dashboard.js still fetches old path**: After uploading versioned data, ensure `dashboard.js` fetches from the new path.
