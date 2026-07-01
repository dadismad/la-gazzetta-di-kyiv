# Tier 2 Radar Alert — Implementation Spec

**Deployed:** June 23, 2026  
**Parent skill:** `gazzetta-newspaper-engine` v2.8.0

---

## Architecture

Three-tier Telegram broadcast system with priority routing:

| Tier | Trigger | Delivery | Cost |
|------|---------|----------|------|
| 1 — Tactical Bet | HIGH/ELEVATED conviction in pipeline | governor → telegram_broadcast.py | $0 |
| 2 — Radar Alert | Narrative velocity ≥2x rolling 7-day avg | governor → narrative_pulse.py → queue → telegram_broadcast.py | ~$0.02/day |
| 3 — Macro Lens | 08:00, 16:00 UTC (cron) | Hermes cron job → DeepSeek → Telegram | ~$0.04/day (pending) |

**Priority:** Tier 1 > Tier 2 > normal loop. Tier 1 clears the Tier 2 radar queue to prevent channel dilution.

---

## File Map

| File | Role |
|------|------|
| `scripts/narrative_pulse.py` | SQLite velocity query → anomaly detection → DeepSeek Radar Alert → queue writer |
| `scripts/governor.py` | Pipeline step `("pulse", ...)` inserted between synthesis and telegram_post |
| `scripts/telegram_broadcast.py` | Priority router at top of `main()` — Tier 1 check → Tier 2 queue check → normal loop |
| `mailbox/radar_queue.json` | List of dicts: `[{narrative_tag, anomaly_score, text, generated_at}]` |

---

## SQLite Anomaly Query

Database: `data/gazzetta.db` table: `ingestion_hashes`

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
- `NULLIF(rolling_avg, 0)` — prevents division by zero for new narratives
- `current.vol > 5` — floor prevents false positives on 2 hits vs. 0 baseline

---

## DeepSeek Radar Alert Prompt

**Critical boundary:** Tier 2 must NOT name specific tickers or suggest trade levels. That's Tier 1 territory. Tier 2 focuses on sectors, asset classes, and the structural "why" behind the volume anomaly.

```
System: You are a Quantitative Macro Forecaster at an elite proprietary trading desk.
Our ingestion engine just detected a major structural narrative volume spike.
Your task is to write a high-signal 'Radar Alert' summarizing the tectonic shift.

CRITICAL RULES:
- Do NOT predict specific price movements or offer explicit entry/stop/target levels.
- Do NOT name specific company tickers or single-name equities. That belongs to a different tier.
- DO highlight which broad sectors, industries, or asset classes are showing the largest capital flow divergence.
- Focus strictly on the structural 'why' behind the volume anomaly.

User: Narrative: {TAG}
Anomaly Multiplier: {X.XX}x baseline
Recent Ingested Headlines: {15 headlines}
Format: 🚨 **RADAR ALERT | {TAG}**
```

**Model:** `deepseek-chat`, temperature 0.4, timeout 45s  
**API URL:** `https://api.deepseek.com/chat/completions` (NO `/v1/` — will 404)

---

## Priority Routing Logic (telegram_broadcast.py)

```
1. Load stories, filter for HIGH/ELEVATED conviction via trade_thesis.conviction
2. If Tier 1 found → format & post → clear radar_queue.json → RETURN
3. If radar_queue.json has items → pop first → post → save mutated queue → RETURN  
4. Fall through to normal broadcast loop (only if no Tier 1 or Tier 2 ready)
```

The router goes at the top of `main()`, BEFORE the existing `posted_ids` / `recent_stories` loop. If Tier 1 or Tier 2 fires, `return` immediately — normal loop never runs.

---

## VM Signature Pitfalls (discovered during Tier 2 deployment)

These burned 3 rounds of corrections. The live VM signatures differ from what you'd assume from context alone.

### Database
- **DB file:** `data/gazzetta.db` (NOT `ingestion.db`)
- **Table:** `ingestion_hashes` — columns: `id, hash, source_url, source_type, title, text_preview, full_text, narrative_tag, created_at, processed`

### Story JSON field names (stories.json)
- **Story ID:** `story_id` (NOT `id`)
- **Narrative:** `narrative_id` with fallback `container` (NOT `narrative_tag` — that's the SQLite column)
- **Conviction:** nested in `trade_thesis.conviction` (NOT top-level `trade_conviction`)
- **Gap:** top-level `contradiction_gap` (NOT inside `trade_thesis.gap`)
- **Ticker:** resolved inside `format_story_for_telegram()` from `trade_thesis.primary_ticker` → `affected_tickers[0]` → defaults (NOT top-level `trade_ticker`)

### Function signatures (telegram_broadcast.py)
- `save_posted_id(story_id: str)` — appends to `posted_stories.jsonl`
- `save_throttle_state(narrative_id: str, gap: int)` — takes 2 args, NOT zero
- `format_story_for_telegram(story: dict, flow_ledger: dict = None) -> str` — returns empty string for HOLD
- `send_telegram(text: str) -> bool` — sends to configured channel

### Governor STEPS format
- `STEPS = [...]` is a **list** (not tuple). Format: `(name, cmd_list, timeout_seconds, critical_bool)`
- New step: `("pulse", [str(VENV), str(SCRIPTS/"narrative_pulse.py")], 60, False)`
- `critical=False` means DeepSeek timeout won't trigger CRITICAL incident

### API key injection
- `governor.py` injects `DEEPSEEK_API_KEY` into subprocess `env` — narrative_pulse.py reads it via `os.getenv("DEEPSEEK_API_KEY")`
- DeepSeek URL: `https://api.deepseek.com/chat/completions` — NO `/v1/` prefix

### Deployment pattern
```bash
scp file.py gazzetta-prod:/tmp/
ssh gazzetta-prod 'sudo cp /tmp/file.py /opt/gazzetta-di-kyiv/scripts/ && sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/scripts/file.py'
ssh gazzetta-prod 'sudo -u gazzetta python3 -c "import py_compile; py_compile.compile(\"/opt/gazzetta-di-kyiv/scripts/file.py\", doraise=True); print(\"OK\")"'
```

### Pipeline verification
```bash
sudo journalctl -u gazzetta-governor --no-pager -n 80
```
Look for: `[pulse] OK`, `[ROUTER] Tier 1/Tier 2`, `[governor] 13/14 OK` (14 = original 13 + pulse step)
