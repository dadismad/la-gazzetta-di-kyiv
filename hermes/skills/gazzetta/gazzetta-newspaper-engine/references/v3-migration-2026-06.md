# v1→v3 Schema Migration — June 2026

## What `migrate_v1_to_v2.py` does

Retrofits 377 legacy stories from the old 6-container system to the new
8-narrative system. Operates on `gazzetta.db` directly.

### Container mapping

| Old Container | New Narrative |
|--------------|---------------|
| `monetary_order` | `dollar_decline` |
| `energy_resources` | `energy_sovereignty` |
| `flashpoints` | `deglobalization` |
| `technology_ai` | `tech_convergence` |
| `biosecurity_health` | `gene_editing` |
| `information_narrative` | `wealthy_sports` |

### Baseline fields

On every legacy story (those lacking the new fields):
- `capital_volume_usd` = 100,000,000 ($100M floor)
- `contradiction_gap` = 15 (neutral tier)
- Also sets `capital_flow.amount_b` and `contradiction_score` for compatibility

### What it touches

- `stories.container` column (SQL UPDATE)
- `stories.full_json` → `container`, `capital_volume_usd`, `contradiction_gap`, `contradiction_score`, `capital_flow`

### Post-migration

Runs `db_to_json.py` to regenerate `data/stories.json` and copies to `public/data/`.
Then deploy with `gsutil cp` to a versioned path to bypass CDN cache.

### Idempotency

Safe to run multiple times. Only modifies stories where `capital_volume_usd`
is null or `contradiction_gap` is null. Already-migrated stories are skipped
with "Already ok" count.

### Next step for real data

After migration, run `contradiction_synthesizer.py` to replace baseline values
with real DeepSeek-computed contradiction gaps and capital volumes. The
baseline values ($100M, gap=15) are placeholders that make bubbles visible
but do not represent real market analysis.
