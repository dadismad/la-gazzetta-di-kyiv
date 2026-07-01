# GapFire Dispatch v2 — 6-Block Telegram Format

Deployed June 22, 2026. Replaces the headline-only Sovereign Auditor 3-block format.
Reads `flows.json` for real aggregated capital numbers instead of story-level LLM defaults.

## Format Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ GAP {gap} | {NARRATIVE_LABEL}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{headline}

💰 CAPITAL FLOW: {cap_str} tracked across {story_count} stories in {narrative} ({ticker})
   ■ {flow_str} | Avg narrative GAP: {avg_gap}/100 | Conviction: {conviction}
   ■ Source: flows.json aggregate ({story_count} stories, avg GAP {avg_gap})

⚡ CONTRADICTION:
   Media says: {they_say_short}
   Capital says: {reality_short}

📊 TWO VIEWS:
   {direction-specific Bull/Bear cases based on LONG/SHORT/NEUTRAL}

🎯 THE BET:
   {direction} {ticker} | Conviction: {conviction}
   Horizon: 14 days | Source: flows.json aggregate (...)

#{gap_tag} #{NARRATIVEHASHTAG} #{TICKER}

Full data: https://www.lagazzettadikyiv.com
```

## Data Sources

- **capital_total_b**: `flows.json → narrative_flows[{narrative_id}].total_capital_b`
- **dominant_direction**: `flows.json → narrative_flows[{narrative_id}].dominant_direction` → LONG/SHORT/NEUTRAL
- **story_count**: `flows.json → narrative_flows[{narrative_id}].story_count`
- **avg_gap**: `flows.json → narrative_flows[{narrative_id}].avg_contradiction_gap`

## Capital Formatting Rules

- `>= 1B`: `$X.XB`
- `> 0, < 1B`: `$XXXM`
- `= 0` or ledger unavailable: `N/A — data pending`

## Direction Mapping

| dominant_direction | THE BET | TWO VIEWS |
|---|---|---|
| `inflow` | LONG | Bull case first: "capital inflows signal institutional conviction" |
| `outflow` | SHORT | Bear case first: "outflows confirm institutional exit despite bullish media" |
| `neutral` | NEUTRAL | "Straddle/strangle opportunity — volatility spike expected" |

## Conviction Mapping

| GAP | Conviction |
|---|---|
| >= 70 | HIGH |
| >= 40 | MODERATE |
| < 40 | SPECULATIVE |

## Hashtag Mapping

| GAP | Tag |
|---|---|
| >= 70 | #GAP_ALERT |
| >= 40 | #GAP_ACTIVE |
| < 40 | #GAP_MONITOR |

## Implementation

File: `scripts/telegram_broadcast.py`
- `load_flow_ledger()` — reads `public/data/flows.json`
- `format_story_for_telegram(story, flow_ledger)` — 6-block dispatch
- `main()` — loads flow ledger at broadcast time, passes to formatter

## Pitfalls

- **Stale flows.json**: If `calculate_capital.py` hasn't run before broadcast, the flow ledger shows old numbers. Governor step order matters: calculate_capital → telegram_broadcast.
- **Narrative ID mismatch**: `telegram_broadcast.py` maps `narrative_id` field; verify it matches the key in `flows.json → narrative_flows`.
- **Zero-capital narratives**: When `total_capital_b = 0`, GapFire shows "N/A — data pending" (not manufactured numbers).
