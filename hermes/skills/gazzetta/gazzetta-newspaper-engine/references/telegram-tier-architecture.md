# Telegram Three-Tier Broadcast Architecture

> Adopted June 23, 2026. Replaces single-tier GapFire Dispatch with priority-routed multi-tier system.

## Tier Hierarchy

| Tier | Name | Trigger | Frequency | Names Tickers? | Content |
|------|------|---------|-----------|----------------|---------|
| 1 | Tactical Bet | GAP ≥ 60 + directional conviction | Rare (1-3/day) | **YES** — single-name equities only | THE PLAY execution card (entry/stop/target/R-multiple) |
| 2 | Radar Alert | Narrative velocity ≥ 2× rolling 7-day avg | Rare (1-2/day) | **NO** — sectors/asset classes only | Macro anomaly brief — "why is this narrative accelerating?" |
| 3 | Macro Lens | Clock: 08:00 & 16:00 UTC | 2×/day | NO | Top-3 narrative synthesis with "Wait for the Tactical Bet" closer |

## Priority Routing (in `telegram_broadcast.py`)

```
1. Tier 1 present? → broadcast highest-conviction Tactical Bet → CLEAR Tier 2 queue → DONE
2. No Tier 1, Tier 2 queue non-empty? → pop oldest alert → broadcast → DONE  
3. Neither → silence (Tier 3 handled by separate cron)
```

**Rationale for queue clearing:** A Tactical Bet is the highest-value signal. Broadcasting a Radar Alert immediately after it dilutes the trade signal and confuses the audience about what to act on.

## Tier Boundary Rules (NON-NEGOTIABLE)

### Tier 1 owns ticker naming
Only Tier 1 names specific single-name equities (NVDA, XOM, CAT, etc.). This preserves the premium feel of Tactical Bets and prevents audience confusion about which signal to trade.

### Tier 2 is strictly macro
Radar Alerts describe **sectors, industries, and asset classes** showing capital flow divergence. The DeepSeek prompt explicitly forbids ticker naming:

> "Do NOT name specific company tickers or single-name equities. That belongs to a different tier."
> "DO highlight which broad sectors, industries, or asset classes are showing the largest capital flow divergence."

### Tier 3 teases Tier 1
Every Macro Lens ends with "Wait for the Tactical Bet" — positioning Tier 3 as a teaser/subscription driver for Tier 1, not a standalone trade signal.

## Anomaly Detection Query (narrative_pulse.py)

**Database:** `/opt/gazzetta-di-kyiv/data/gazzetta.db` (NOT `ingestion.db` — the ingestion_hashes table lives inside `gazzetta.db`)

```sql
SELECT current.narrative_tag, current.vol, avg_table.rolling_avg, 
       (current.vol / NULLIF(avg_table.rolling_avg, 0)) as anomaly_score
FROM 
  (SELECT narrative_tag, COUNT(*) as vol FROM ingestion_hashes 
   WHERE created_at > datetime('now', '-6 hours') GROUP BY narrative_tag) current
JOIN 
  (SELECT narrative_tag, COUNT(*)/28.0 as rolling_avg FROM ingestion_hashes 
   WHERE created_at > datetime('now', '-7 days') GROUP BY narrative_tag) avg_table
ON current.narrative_tag = avg_table.narrative_tag
WHERE (current.vol / NULLIF(avg_table.rolling_avg, 0)) >= 2.0 AND current.vol > 5;
```

**Guards:**
- `NULLIF(rolling_avg, 0)` — prevents division by zero on new narratives
- `vol > 5` — prevents firing on 2 stories vs. 0 baseline (mathematically infinite, practically noise)

## Queue Format (`mailbox/radar_queue.json`)

```json
[
  {
    "narrative_tag": "deglobalization",
    "anomaly_score": 2.4,
    "text": "🚨 **RADAR ALERT | DEGLOBALIZATION** ...",
    "generated_at": "2026-06-23T14:00:00Z"
  }
]
```

List of dicts (not strings) — preserves metadata for logging and future dedup.

## Pipeline Integration

`narrative_pulse.py` sits between `synthesis` and `telegram_post` in `governor.py`. The STEPS structure is a **list** `[...]`, not a tuple `(...)`:

```python
STEPS = [
    # ...
    ("synthesis",     [str(VENV), str(SCRIPTS/"contradiction_synthesizer.py")], 300, True),
    ("pulse",         [str(VENV), str(SCRIPTS/"narrative_pulse.py")],           60, False),  # NEW
    ("telegram_post", [str(VENV), str(SCRIPTS/"telegram_broadcast.py")],        60, False),
    # ...
]
```

`critical=False` — a DeepSeek API timeout in the pulse step won't trigger a CRITICAL incident or block the rest of the pipeline.

**API key delivery:** `governor.py` line 536 injects `DEEPSEEK_API_KEY` into subprocess environments via the `env=` parameter. `narrative_pulse.py` uses `os.getenv("DEEPSEEK_API_KEY")` — this works because it's called as a pipeline subprocess. The key is NOT in `.env` directly; it comes from GCP Secret Manager via `governor.py`'s `_secret()` function.

## DeepSeek Call Pattern

- **Endpoint:** `https://api.deepseek.com/chat/completions` (NO `/v1/` prefix — that 404s)
- **API key:** Injected via `governor.py` line 536 as `DEEPSEEK_API_KEY` env var into subprocess
- **Model:** `deepseek-chat`
- **Temperature:** 0.4 (low — factual macro briefing, not creative writing)
- **Timeout:** 45s

## Naming Collision Note

`narrative_pulse.py` is the velocity/anomaly detection engine. Do NOT confuse with a hypothetical "Tier 2 broadcaster" — broadcasting is handled by `telegram_broadcast.py` via priority routing. `narrative_pulse.py` only DETECTS and QUEUES; it never sends to Telegram directly.
