---
name: gazzetta-living-stories
description: Living Stories system — stories evolve through the day via 3-tier update cadence. Micro-updates every 2h at zero LLM cost using Jaccard similarity entity matching.
version: 1.0.0
author: Hermes Agent
---

# Gazzetta Living Stories — Dynamic Front Page

Stories on the Gazzetta di Kyiv front page evolve through the day instead of being frozen between 12-hour editorial cycles. When a story like "Iranian drones hit Kuwait Airport" appears, it accumulates sub-story updates as new developments arrive — asset price changes, new evidence, frame shifts.

## Architecture

### 3-Tier Update Cadence

| Tier | Name | Frequency | Cost | What It Does |
|------|------|-----------|------|-------------|
| T1 | Telegram monitor | 30 min | LLM | Real-time event detection from 6 Telegram channels |
| T2 | `enrich_stories.py` | 2 hours | **$0** | Jaccard similarity matching, no LLM calls |
| T3 | Editorial writer | 12 hours | LLM | Full narrative synthesis with evolution context |

### Data Model

- **`data/story_registry.json`** — Persistent story database. Each story has: story_id, first_seen, last_updated, status (new→evolving→stable→resolved), update_count, actors, geography, paradigm_pillar, asset_claim with initial→current price tracking
- **`data/stories/{story_id}/timeline.json`** — Per-story evolution timeline. Append-only log: {update_id, timestamp, type, summary, source_url, asset_delta}
- **`data/publish/living_stories.json`** — Frontend aggregate payload. All active stories with current status, badges, asset claims

### Evolution Scoring

`score = actor_match * 0.4 + geography_match * 0.3 + pillar_match * 0.2 + recency * 0.1`

- **≥0.6**: Evidence update — append to existing story thread
- **≥0.85**: Sub-thread spawn — create new angle (e.g., "brent repricing")
- **<0.6 for 48h**: Mark as stable
- **7 days with no updates**: Resolve/archive

### Cron Job

`gazzetta-living-stories-enrich` — runs every 2 hours on the :15 mark. `no_agent=true`, zero LLM cost, pure Python. Script: `scripts/enrich_stories.py`

### 3 Non-Negotiable Guardrails

1. **Headline lock** — Original headline immutable within a cycle. Sub-stories go beneath
2. **Collapsed by default** — Front page shows current summary + "+N updates" badge. Full timeline on click
3. **Asset delta mandatory** — Every sub-update touching a tracked asset starts with `{ticker} {initial}→{current} | {change_pct}%`

### Frontend Features

- Stateful DOM patching (keyed by story_id)
- "+N updates" gold badge with pulsing dot for evolving stories
- "updated X min ago" timestamps
- Collapsible timeline detail panel with gold left border
- Asset claim line: `{ticker} $74→$78 | +5.4% | 68% narrative-driven`
- 2-minute polling with If-Modified-Since headers
- Responsive: mobile timeline slides up as overlay

### Key Files

| File | Purpose |
|------|---------|
| `scripts/enrich_stories.py` | T2 micro-update runner |
| `scripts/analyze_narratives_v2.py` | Seeds new stories into registry |
| `scripts/build_site.py` | Syncs living_stories.json to site/data/ |
| `data/story_registry.json` | Persistent story database |
| `data/stories/{id}/timeline.json` | Per-story evolution log |
| `data/publish/living_stories.json` | Frontend aggregate payload |
| `site/app.js` | Stateful frontend renderer |
| `site/styles.css` | Living story animations and badges |
| `docs/LIVING_STORIES_SPEC.md` | Full 831-line spec |
| `docs/LIVING_STORIES_MEMORY.md` | Canonical reference |

### Integration with Editorial Writer

The editorial writer (Step 1) now reads `story_registry.json` and `living_stories.json`. Step 3 prefers evolving stories with 3+ updates as lead candidates. Step 8.5 includes `story_id` in stories.json for persistent card keying.
