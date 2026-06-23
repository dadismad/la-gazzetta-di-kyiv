---
name: gazzetta-backend-audit
description: Definitive backend architecture, file manifest, data flow DAG, and payload structures for La Gazzetta di Kyiv. Ground truth — do not rely on memory.
version: 1.0.0
---

# Gazzetta di Kyiv — Backend Architecture Audit

## Infrastructure

- **VM**: `gazzetta-prod` (SSH alias)
- **Project root**: `/opt/gazzetta-di-kyiv/`
- **User**: `gazzetta` (all pipeline processes)
- **Python venv**: `/opt/gazzetta-di-kyiv/venv/bin/python`
- **Secrets**: GCP Secret Manager (DeepSeek key, Telegram token, AlphaVantage key)
- **Deploy**: `deploy_to_gcs.py` → `gs://www.lagazzettadikyiv.com/` → CDN invalidation
- **Scheduler**: systemd timer `gazzetta-governor.service` (10-min cycle)
- **Hermes cron**: Tier 3 Macro Lens only (job `6c7645ee6430`, fires 10:00/18:00 Kyiv)

## Data Layer

### SQLite: `/opt/gazzetta-di-kyiv/data/gazzetta.db`

| Table | Key Columns | Purpose |
|---|---|---|
| `ingestion_hashes` | id, hash, source_url, source_type, title, full_text, narrative_tag, created_at, processed | Raw RSS/YT ingestion dedup |
| `stories` | id, headline, container, tier, contradiction_score, full_json, generated_at | Synthesized stories |
| `flows` | id, story_id, name, category, net_direction, amount_b, velocity | Capital flow entities |
| `story_flow_links` | story_id, flow_id | M2M join |
| `drafts` | id, source, raw_content, status | Pending editorial review |
| `pipeline_state` | state (IDLE/PROCESSING/ERROR), started_at, pid | Concurrency guard |
| `translation_checkpoint` | story_id, translated_at, status | RU translation tracking |
| `story_tags` | story_id, tag | Tag index |

### Key JSON Files

| File | Location | Structure |
|---|---|---|
| `stories.json` | `public/data/` | `{all_stories: [...], containers: [...], narrative_alpha: {...}}` |
| `flows.json` | `public/data/` | `{narrative_flows: {narrative_id: {total_capital_b, dominant_direction, ...}}, top_signals: [...]}` |
| `narratives.json` | `data/` | `{metadata: {...}, narratives: {...}}` |
| `market_prices.json` | `data/` | Live price snapshots |
| `cftc_cot.json` | `data/` | CFTC Commitment of Traders |
| `fred_macro.json` | `data/` | FRED economic series |
| `telegram_throttle.json` | `public/data/` | `{narrative_id: [iso_ts, gap]}` |
| `posted_stories.jsonl` | `public/data/` | One story_id per line |

### Inter-step communication: `/opt/gazzetta-di-kyiv/mailbox/`

| File | Purpose |
|---|---|
| `inbox.json` | CEO commands from external sources |
| `outbox.json` | CEO responses |
| `incidents.json` | Pipeline failure tickets |
| `radar_queue.json` | Tier 2 radar alerts awaiting broadcast (list of dicts) |

## Story Object (canonical schema)

Each story in `all_stories[]` has these fields used by the pipeline:

```
story_id, headline, slug, they_say, reality, narrative_id,
contradiction_gap (int 0-100), contradiction_score,
trade_thesis: {
  direction ("LONG"|"SHORT"|"STRADDLE"|"NEUTRAL"),
  primary_ticker (str),
  limit_entry_price (str),
  stop_loss (str),
  take_profit (str),
  invalidation (str),
  conviction ("HIGH"|"ELEVATED"|"SPECULATIVE"|"HOLD"),
  horizon_days (int),
  alpha_trigger (str)
},
affected_tickers, affected_asset_classes,
container, containers, tier, pillar, sector,
source_name, source_url, feed_source, generated_at,
capital_volume_usd, narrative_weights, tags, entity_tags
```

CRITICAL: `conviction` is NESTED inside `trade_thesis`, NOT a top-level field.
CRITICAL: `narrative_id` is the primary narrative key. Fallback: `container`.
CRITICAL: `contradiction_gap` is top-level, NOT inside `trade_thesis`.

## Pipeline DAG (14 steps)

```
ingestion → market_data → cftc_data → fred_data → derivatives
    → synthesis → classify → calc_capital → gen_flows
    → build_frontend → test_platform → pulse → telegram_post → deploy
```

### Step details

| # | Step | Script | Timeout | Critical | Reads | Writes |
|---|---|---|---|---|---|---|
| 1 | ingestion | `ingestion_triage.py` | 120 | Yes | RSS feeds | `gazzetta.db` (ingestion_hashes) |
| 2 | market_data | `market_reality.py --all` | 90 | Yes | yfinance | `data/market_prices.json` |
| 3 | cftc_data | `fetch_cftc.py` | 60 | No | CFTC API | `data/cftc_cot.json` |
| 4 | fred_data | `fetch_fred.py` | 120 | No | FRED API | `data/fred_macro.json` |
| 5 | derivatives | `fetch_derivatives.py` | 30 | No | — | `public/data/derivatives.json` |
| 6 | **synthesis** | `contradiction_synthesizer.py` | 180 | **Yes** | `gazzetta.db`, market data | `gazzetta.db` (stories), `public/data/stories.json` |
| 7 | classify | `classify_stories.py` | 30 | No | `stories.json` | `stories.json` (narrative_id updates) |
| 8 | calc_capital | `calculate_capital.py` | 60 | Yes | `stories.json`, market data | `stories.json` (capital fields) |
| 9 | gen_flows | `generate_flows.py` | 30 | No | `stories.json` | `public/data/flows.json` |
| 10 | build_frontend | `build_frontend.py` | 60 | Yes | `stories.json`, `flows.json` | `public/index.html` |
| 11 | test_platform | `test_platform.py` | 30 | No | `public/index.html` | — (validation only) |
| 12 | **pulse** | `narrative_pulse.py` | 60 | No | `gazzetta.db` (ingestion_hashes) | `mailbox/radar_queue.json` |
| 13 | **telegram_post** | `telegram_broadcast.py` | 60 | No | `stories.json`, `flows.json`, `radar_queue.json`, `telegram_throttle.json` | `telegram_throttle.json`, `posted_stories.jsonl`, Telegram API |
| 14 | deploy | `deploy_to_gcs.py` | 120 | No | `public/` | GCS bucket, CDN invalidation |

## State as of June 23, 2026 (end-of-session)

### Persona: Pal/Visser deployed across all three tiers
- **Tier 1**: Surgical injection into `contradiction_synthesizer.py:283` — Pal/Visser persona + guardrail. JSON schema preserved. See `references/prompt-injection-technique.md`.
- **Tier 2**: Full `system_prompt` replacement in `narrative_pulse.py` — denominator effect + asymmetry lens + structured output format (Velocity Surge / Denominator Shift headers). User prompt updated with explicit output template.
- **Tier 3**: Pal/Visser persona + Captivating Anchor rule layered into cron prompt `6c7645ee6430`. Self-posts via SSH+Python (see `references/cron-delivery-gotcha.md`).

### Tier 1 Trade Card Format (June 23 overhaul)
`format_story_for_telegram()` HIGH/ELEVATED block replaced (line ~257):
- Template opener (`EVERYONE'S WRONG ABOUT...`) removed — headline speaks first
- "Media says / Capital says" asymmetry added (was only in SPECULATIVE)
- GAP score moved into THE PLAY line with dynamic color
- Capital flow data (`$X.XB inflow/outflow`) injected into PLAY line
- Duplicate alpha trigger removed (appears once as "The edge:")
- TIER 1/2 conviction badges added to sourceLine

### Frontend UX (June 23 deploy)
Four quick wins deployed to `build_frontend.py`:
1. **Hero section**: Institutional tagline in Pal/Visser voice above The Stream
2. **GAP badges**: Dynamic color (burgundy/gold/muted) + font-weight:700
3. **Tier accents**: Conviction-based left border (burgundy for TIER 1, blue for TIER 2) + TIER 1/2 pills
4. **Capital flow fix**: Leaderboard reads from `NARRATIVES[].capital_b` (flows.json) instead of broken per-story `capital_volume_usd`
See `references/ux-audit-2026-06-23.md` for full analysis.

### Cron Jobs
- **Tier 3 Macro Lens**: `6c7645ee6430` — fires 10:00/18:00 Kyiv (07:00/15:00 UTC). `deliver='local'` + self-posting workaround.
- **DB Backup**: `29c13c55c5f3` — hourly `gazzetta.db` sync to GCS.

### Prompt Modification Safety
See `references/prompt-modification-guardrails.md` — mandatory checklist including common file-mapping errors, field-name errors, and SQLite access pattern.

### Common Pitfalls
See `references/prompt-modification-guardrails.md` for the complete catalog. Key ones:
- **Wrong file**: `telegram_broadcast.py` has NO synthesis prompt — it's in `contradiction_synthesizer.py`
- **Wrong field**: `conviction` is nested in `trade_thesis`, NOT top-level. `narrative_id` not `narrative_tag`. `contradiction_gap` is top-level, not in `trade_thesis`.
- **SQLite access**: Must use `sudo -u gazzetta sqlite3` — bare `sqlite3` fails with readonly error.
- **Cron delivery**: `deliver='telegram:<chat_id>'` silently fails for unconnected channels.

---

## Broadcast Routing (telegram_broadcast.py)

Priority chain inside `main()`:

1. **Tier 1 check**: Filter stories where `trade_thesis.conviction in ("HIGH", "ELEVATED")` AND `is_recent()` AND `contradiction_gap > 50`. If found → format & send → clear `radar_queue.json` → `return`
2. **Tier 2 check**: If `radar_queue.json` exists and non-empty → pop first alert → send → `return`
3. **Normal loop**: Filter recent stories (GAP>50, has trade_thesis) → throttle check → format → send (max `MAX_POSTS=2`)
4. HOLD conviction stories are silently skipped (format returns empty string)

## Key Functions (do not hallucinate)

| Function | File | Signature |
|---|---|---|
| `format_story_for_telegram` | `telegram_broadcast.py` | `(story: dict, flow_ledger: dict = None) -> str` |
| `send_telegram` | `telegram_broadcast.py` | `(text: str) -> bool` |
| `save_posted_id` | `telegram_broadcast.py` | `(story_id: str)` |
| `save_throttle_state` | `telegram_broadcast.py` | `(narrative_id: str, gap: int)` |
| `load_throttle_state` | `telegram_broadcast.py` | `() -> dict` |
| `load_stories` | `telegram_broadcast.py` | `() -> list` |
| `load_flow_ledger` | `telegram_broadcast.py` | `() -> dict` |
| `is_recent` | `telegram_broadcast.py` | `(story: dict) -> bool` |
| `generate_radar_alert` | `narrative_pulse.py` | `(narrative_tag, anomaly_score, headlines) -> str or None` |

## LLM Prompts (where they live)

| Tier | File | Variable | Line |
|---|---|---|---|
| Tier 1 (synthesis) | `contradiction_synthesizer.py` | `SYSTEM_PROMPT` | ~283 |
| Tier 2 (radar) | `narrative_pulse.py` | `system_prompt` (inside `generate_radar_alert()`) | ~60 |
| Tier 3 (macro lens) | Hermes cron job `6c7645ee6430` | prompt field | — |

⚠️ `telegram_broadcast.py` does NOT contain any LLM prompts — it only formats and routes.

## Reference Files

- **[UX Audit (2026-06-23)](references/ux-audit-2026-06-23.md)** — Full frontend audit: four-lens analysis, broken data catalog, quick-win fixes, tech notes.
- **[Cron Delivery Gotcha](references/cron-delivery-gotcha.md)** — Hermes cron `deliver='telegram:<chat_id>'` silently fails for channels not connected as Hermes platforms. Workaround: agent self-posts via SSH + Python.
- **[Surgical Prompt Injection](references/prompt-injection-technique.md)** — Pattern for changing LLM persona without breaking downstream JSON parsers. Replace only the "who you are" paragraph, never the schema. Includes anti-patterns and verification checklist.
- **[Prompt Modification Guardrails](references/prompt-modification-guardrails.md)** — Mandatory pre-modification checklist. Catalog of common file-mapping errors, field-name errors, SQLite access pattern, shell-escaping pitfall, and post-modification verification steps.
- **[UTM Telemetry](references/utm-telemetry.md)** — Zero-infrastructure click tracking via UTM parameters on Telegram links. CDN log parsing pattern. When to upgrade to Plausible/Umami.

### Scripts

- **[Telegram Stats Tracker](scripts/telegram_stats.py)** — Polls `getChatMemberCount` and appends to CSV. Deployed at `/opt/gazzetta-di-kyiv/scripts/telegram_stats.py`. Cron: daily at 09:00 Kyiv (job `1fb9dda62b76`).
