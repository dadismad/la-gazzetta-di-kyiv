# Phase C — Sovereign Terminal Deployment (June 22, 2026)

## What Changed
- **Dark Mode**: Body background #0A0A0F, text #E6E4E0. Tailwind `darkMode: 'class'` already configured — just changed `<html class="light">` to `<html class="dark">` + `!important` on body CSS to beat Tailwind `bg-surface` class.
- **Sidebar Fix**: All 12 narratives now show real capital from `flows.json` aggregated ledger instead of per-story `capital_volume_usd` (which was $0 or LLM-hallucinated $100M). Fix: `flow_ledger = flows_raw.get("narrative_flows", {})` → `if flow_entry and flow_entry.get("total_capital_b", 0) > 0: total_cap = flow_entry["total_capital_b"]`
- **GAP Leaderboard**: Above the Stream on all tabs. Top 5 narratives by GAP score. Color-coded: crimson (#8B0000) for GAP>60, gold (#D4AF37) for GAP 30-60, gray for <30. Direction arrows (↗↘◉). Mobile: horizontal scroll.
- **GAP Physics**: Border thickness + color scale with contradiction magnitude. BREAKING (crimson 4px), ACTIVE (gold 2px), SETTLING (muted 1px, opacity 0.7). Pulse animation for GAP>70.
- **Deploy Fix**: Root cause `NoNewPrivileges=yes` in systemd service silently blocking `sudo gsutil` for days. Fix: `sed -i 's/NoNewPrivileges=yes/NoNewPrivileges=no/' /etc/systemd/system/gazzetta-governor.service && systemctl daemon-reload`

## Key Pitfalls Discovered

### NoNewPrivileges Blocks Sudo in Deploy Step
The systemd service had `NoNewPrivileges=yes` for security hardening. This also blocks `sudo`, which the deploy step uses. The deploy step failed SILENTLY — gsutil returned exit code 1 but the governor logged `[deploy] FAIL(1) in 0.0s` and continued. The site served stale content for days while the pipeline appeared healthy (10/11 OK). Detection: check journal for `[deploy] FAIL` — any failure means the site is serving stale content.

### Tailwind bg-surface Overrides Body Background
When `<body class="bg-surface">` uses a Tailwind utility class, the Tailwind class takes precedence over the `<style>` tag's `body{background:#0A0A0F}` because Tailwind injects inline-like specificity. Fix: `body{background:#0A0A0F!important}` — the `!important` beats Tailwind's utility class.

### !important Cascade Required for Text Color Too
`body{color:#E6E4E0}` must also use `!important` because Tailwind's `text-on-surface` class sets text color. Same override pattern needed for any Tailwind utility that conflicts with dark mode.

### Sidebar Data Source Mismatch
The sidebar NARRATIVES were built by summing `capital_volume_usd` from individual stories. But `capital_volume_usd` is set to 0 for most stories (the anti-hallucination fix from Phase A). The sidebar showed $0M for 6 of 12 narratives even though `flows.json` (built by `calculate_capital.py` using real CFTC/FRED/CoinGecko data) had correct aggregated numbers. Fix: read `flows.json` in `build()` and use `flow_ledger[narrative_id]["total_capital_b"]` as `capital_b` in the NARRATIVES dict. Fall back to story-level sum only if flows.json entry is missing or zero.

### Telegram Markdown parse_mode Breaks GapFire Unicode
The GapFire format uses Unicode box-drawing chars (━) and emoji (⚡💰📊🎯). Telegram's `parse_mode: "Markdown"` rejects these as invalid syntax, returning HTTP 400. Fix: remove `parse_mode` entirely — send plain text. The formatting is achieved via the characters themselves, not Markdown syntax.
