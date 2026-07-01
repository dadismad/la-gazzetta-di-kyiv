# Phase A/B Deployment Log — June 22, 2026

Triggered by 6-persona focus group audit scoring 4.4/10 (FAIL).
All changes deployed to VM (`gazzetta-prod`, `/opt/gazzetta-di-kyiv/scripts/`).

## Phase A: Low-Risk Immediate Fixes

### A3: Template-Rot Regex Guard Expansion
- **File**: `scripts/contradiction_synthesizer.py`, lines 480-498
- **Old behavior**: Regex caught "fails to move" → replaced with "leaves market pricing unchanged"
- **CRITICAL BUG FOUND**: The replacement phrase "leaves market pricing unchanged" WAS ITSELF template rot. The guard was a revolving door — swapping one toxic phrase for another.
- **New behavior**: 4 rot patterns with neutral replacements:
  - `fails to / market unmoved / markets shrug / no market impact` → "finds no immediate market catalyst in"
  - `leaves market pricing unchanged` → "finds no immediate market catalyst in"
  - `as markets rally` → "while tracked sectors diverge:"
  - `overshadowed by [tech] rally` → "concurrent with tech-sector outperformance in"
- **Pitfall pattern**: When adding anti-rot regex, ALWAYS check the REPLACEMENT text against the ban list. A guard that swaps one rot phrase for another is worse than no guard — it silently perpetuates the rot.

### A4: Mobile Touch-Target Compliance
- **File**: `scripts/build_frontend.py`, inline CSS
- `@media (max-width:768px)`: `.filter-pill` at 44px min, 14px font, `#filter-bar` horizontal scroll
- `@media (max-width:480px)`: tighter pills, radar font bump

### A2: GAP < 15 Filter
- **File**: `scripts/build_frontend.py`, story rendering loop
- `streamStories = STORIES.filter(s => gap >= 15)` before card HTML generation
- Low-signal stories excluded from Stream tab; remain in `stories.json` for data completeness

### A1: GapFire Dispatch v1
- **File**: `scripts/telegram_broadcast.py`, `format_story_for_telegram()`
- Initial 6-block format, used story-level fields (showed $21M, pipeline data pending)
- Superseded by B2 (see below)

## Phase B: Structural Realism

### B2: Capital Backfill from flows.json
- **File**: `scripts/telegram_broadcast.py`
- **Key insight**: Story-level `capital_volume_usd` is an LLM default (flat $100M). `flows.json` has real `calculate_capital.py` aggregates ($28.8B for Tech Convergence, $400M for Energy Sovereignty).
- **Fix**: `load_flow_ledger()` reads `public/data/flows.json` at broadcast time. `format_story_for_telegram()` maps `narrative_id` → real `total_capital_b`, `dominant_direction`, `story_count`, `avg_contradiction_gap`.
- **Pattern**: When individual records have LLM defaults but an aggregated file has computed real numbers, read from the aggregated file. Don't backfill individual records — fix the consumer.
- **Before**: `CAPITAL FLOW: $21M | Flow: pipeline data pending | THE BET: NEUTRAL QQQ`
- **After**: `CAPITAL FLOW: $400M across 52 stories | Net inflow $400M | THE BET: LONG CL=F`

### B1: NLP Overhaul — Forward Declaration
- **File**: `scripts/contradiction_synthesizer.py`, `SYSTEM_PROMPT` and `assemble_story()`
- **Schema added**: `trade_thesis` object with `direction`, `primary_ticker`, `entry_zone`, `invalidation`, `conviction`, `horizon_days`, `alpha_trigger`
- **Tone rules**: "Write like a PM at a macro hedge fund briefing their team. No hedging language. No passive voice. State your thesis directly."
- **Alpha trigger**: Most important field. Must answer "What EXACTLY is the market pricing wrong?" with a specific, falsifiable claim citing a number.
- **NEUTRAL rule**: Only allowed with a specific STRADDLE/volatility thesis. Never a default.
- **Extraction**: `assemble_story()` extracts trade_thesis from LLM JSON → stores in story dict
- **Takes effect on next governor synthesis cycle** (existing stories have no trade_thesis)

### B3: Mobile Progressive Disclosure
- **File**: `scripts/build_frontend.py`, inline CSS, `@media (max-width:768px)`
- Collapsed state: headline + GAP badge only (capital bars and tag rows hidden)
- "TAP TO EXPAND →" affordance via `summary::after` pseudo-element
- "TAP TO COLLAPSE ↑" on open state
- Copy-link buttons hidden on mobile
- Dispatch content single-column, 14px font

## Deployment Pattern (Phase A/B)

1. Make local changes to script files
2. Run syntax check: `python3 -c "import py_compile; py_compile.compile(f, doraise=True)"`
3. Run test suite: `python3 scripts/test_platform.py`
4. SCP to VM `/tmp/` (gazzetta user lacks write to `/opt/gazzetta-di-kyiv/scripts/`)
5. SSH: `sudo cp /tmp/file /opt/gazzetta-di-kyiv/scripts/ && sudo chown gazzetta:gazzetta`
6. Run GapFire dry-run: `sudo -u gazzetta python3 scripts/telegram_broadcast.py --dry-run --max-posts 1`
7. Full governor cycle: `sudo systemctl start gazzetta-governor`

## P0 Pitfall: Regex Revolving Door

**What**: Anti-rot guard replaced "fails to move" with "leaves market pricing unchanged" which was itself template rot.
**How found**: Chief Editor persona flagged "leaves market pricing unchanged" appearing 5+ times in headlines. Code inspection revealed the guard was the source.
**Prevention**: After adding any anti-rot regex pattern, grep the REPLACEMENT text against the ban list. The guard must never introduce what it purports to prevent.
**Detection command**: `grep -n "leaves market pricing" scripts/contradiction_synthesizer.py` — if found in a replacement string, it's a revolving door.
