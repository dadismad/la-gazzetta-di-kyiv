# Living Stories — Enhanced Implementation Spec

> Review of the "living stories" proposal for Gazzetta di Kyiv, with architectural feedback from 3 personas plus a concrete implementation plan covering data model, update cadence, frontend changes, and pipeline changes.

---

## Persona Reviews

### 1. Frontend Architect — Data Structures, Rendering, UX

**Feedback:** The current `stories.json` is a flat snapshot — one `lead` + `stories[]`, overwritten each cycle. For living stories, the data must become an **append-only evolution log** with versioned state. The frontend currently fetches `stories.json` (single file, `cache: no-store`) and renders everything inline. This won't scale to thread expansion, subtopic branching, or per-story update timestamps. We need either:
- A multi-file store (`stories/{story_id}/timeline.json`, `stories/{story_id}/current.json`) and a lazy-load detail view, or
- An enriched `living_stories.json` that carries the full evolution payload, with a JavaScript `MutationObserver`-style renderer that patches only changed cards.

**Suggested enhancements:**
- Story cards become **stateful DOM objects** keyed by `story_id` — the boot loader hydrates all known stories, then a WebSocket-free polling mechanism (`setInterval` + `fetch` + ETag/Last-Modified headers) patches in new facts, asset prices, and "updated N min ago" badges without a full re-render.
- Detail view slides open (not navigates to) showing the story's full evolution timeline: original headline, each update with timestamp, changed asset projections, linked sources.
- Visual language: a thin vertical timeline running down the left edge of each card that extends as updates arrive. Gold dots for major updates, light gold dots for minor evidence additions. A pulsing "LIVE" indicator on actively evolving stories.

### 2. Editorial Architect — Workflow, Quality Gates, What's Worth Updating

**Feedback:** The editor-in-chief is right that enrichment beats replacement, but not every new RSS item warrants a thread update. We need editorial judgment encoded in the automation: a **"evolution score"** that decides whether a new evidence item upgrades an existing story, spawns a subtopic, or is ignored.

**Suggested enhancements:**
- **Evolution score = actor_match * 0.4 + geography_match * 0.3 + pillar_match * 0.2 + recency * 0.1** — threshold at 0.6 for "update existing story thread", 0.85 for "spawn new subtopic". Below 0.6: file as new standalone story or skip.
- Editorial state gains a `story_registry` — every story is tracked from first appearance through resolution. When an actor or geography accumulates 3+ updates across cycles, it automatically graduates from "news item" to "narrative thread" with its own dedicated tracking.
- **When to archive:** A story enters `resolved` status when: (a) its invalidation trigger fires, (b) 7 days pass with zero new evidence, or (c) the editor explicitly archives it. Resolved stories collapse into a "Past Narratives" archive section.
- **Human-in-the-loop surface:** A `data/pending_updates.json` file that flags high-confidence evolution candidates for editorial review before they auto-publish. The agent can review and approve/deny.

### 3. Pipeline Architect — Cron, Data Flow, Cost

**Feedback:** The current pipeline runs 2x/day (06:45/18:45) with a 30m Telegram monitor. Living stories need a **3-tier update frequency**: the main editorial cycles stay at 2x/day, but a lightweight micro-update runner (every 2 hours, no LLM — just evidence comparison + asset price refresh) feeds the evolution layer. Cost analysis: adding a mid-tier micro-update runner costs ~0 (Python-only, no LLM calls), while the full editorial write cycle stays at its current 2x/day LLM burn (~$0.03/cycle on deepseek-v4-flash = ~$1.80/month).

**Suggested enhancements:**
- New **Tier 2 cron job** (`living-story-micro-update`, every 2h on the :15 mark) — no LLM involvement. Runs `enrich_stories.py` which:
  1. Compares `events_latest.json` evidence sets against each active story's evidence history
  2. Computes evolution scores
  3. Refreshes asset prices (via a lightweight JSON API or cached ticker)
  4. Writes updated `stories/living_stories.json` and `stories/{story_id}/timeline.json`
  Estimated runtime: <5s.
- **Tier 3: Full editorial cycles** (2x/day) — unchanged. The LLM receives the living-story timeline as context and can write thread updates, frame shifts, and new lead stories informed by what evolved.
- **Cost guardrail:** The Telegram monitor (30m) already checks for change. If the monitor detects zero novel entities in the last 2 hours, the Tier 2 micro-update is skipped entirely — saves file I/O and avoids unnecessary writes to git.

---

## Concrete Implementation Spec

---

### 1. Data Model

#### 1A. Persistent Story Registry — `data/story_registry.json`

```json
{
  "version": 1,
  "updated_at": "2026-06-04T10:15:00Z",
  "story_count": 3,
  "active_count": 3,
  "stories": {
    "n21_geopolitics__kuwait_airport": {
      "story_id": "n21_geopolitics__kuwait_airport",
      "first_seen": "2026-06-03T06:45:00Z",
      "last_updated": "2026-06-04T10:15:00Z",
      "status": "evolving",
      "status_reason": "New evidence: Iranian drone debris analysis released by Kuwait MOD",
      "update_count": 4,
      "original_setup_id": "n21_geopolitics",
      "original_headline": "Iranian Drones Hit Kuwait International Airport",
      "current_headline": "Iranian Drones Hit Kuwait Airport as Gulf Infrastructure Crisis Deepens",
      "sector": "geopolitics",
      "paradigm_pillar": "multi_pillar",
      "actors": ["Iran", "Kuwait", "US Central Command", "Gulf States"],
      "geography": ["Kuwait", "Persian Gulf", "Iran"],
      "thread_ids": [
        "n21_geopolitics__kuwait_airport__main",
        "n21_geopolitics__kuwait_airport__brent_repricing",
        "n21_geopolitics__kuwait_airport__gulf_state_repositioning"
      ],
      "primary_thread_id": "n21_geopolitics__kuwait_airport__main",
      "evolution_score_peak": 0.91,
      "evolution_score_current": 0.73,
      "invalidation_triggers": [
        "Gulf States announces policy reversal within 72 hours",
        "Kuwait airport reopens to civilian traffic"
      ],
      "last_asset_projection": {
        "asset": "Brent Crude",
        "price": "$78.00",
        "change": "+2.1%",
        "narrative_driven_pct": 68,
        "projected_2h": "$79.40"
      },
      "image_url": "https://ichef.bbci.co.uk/ace/standard/240/cpsprodpb/7499/live/..."
    },
    "n21_macro__oecd_dark_scenario": {
      "story_id": "n21_macro__oecd_dark_scenario",
      "first_seen": "2026-06-03T06:45:00Z",
      "last_updated": "2026-06-04T06:45:00Z",
      "status": "evolving",
      ...
    }
  }
}
```

#### 1B. Story Thread Timeline — `data/stories/{story_id}/timeline.json`

```json
{
  "story_id": "n21_geopolitics__kuwait_airport",
  "current_headline": "Iranian Drones Hit Kuwait Airport as Gulf Infrastructure Crisis Deepens",
  "status": "evolving",
  "threads": [
    {
      "thread_id": "n21_geopolitics__kuwait_airport__main",
      "type": "main",
      "current_state": {
        "headline": "Iranian Drones Hit Kuwait Airport as Gulf Infrastructure Crisis Deepens",
        "they_say": "US-Iran strikes are contained to military targets — civilian infrastructure not at risk.",
        "reality": "Kuwait International Airport struck by Iranian drones on June 3. Civilian infrastructure targeting threshold crossed. Kuwait operations remain suspended as of June 4.",
        "thesis": "Energy corridor infrastructure targeting threshold crossed. Brent repricing accelerates as Gulf state positioning shifts.",
        "source_count": 7,
        "last_updated": "2026-06-04T10:15:00Z"
      },
      "evolution": [
        {
          "update_id": "ev_001",
          "timestamp": "2026-06-03T06:45:00Z",
          "type": "initial_broadcast",
          "evidence_titles": [
            "US and Iran launch new strikes as Kuwait says airport hit by Iranian drones",
            "British couple lose Iran jail sentence appeal"
          ],
          "source_count": 2,
          "reality_delta": "Initial report — airport struck, operations suspended.",
          "asset_projection": { "asset": "Brent Crude", "price": "$76.50", "change": "+1.2%", "narrative_driven_pct": 55 }
        },
        {
          "update_id": "ev_002",
          "timestamp": "2026-06-03T12:00:00Z",
          "type": "evidence_update",
          "evidence_titles": [
            "Kuwait MOD confirms Iranian-made Shahed-136 debris found on runway",
            "Gulf states call emergency GCC meeting"
          ],
          "source_count": 4,
          "reality_delta": "Debris analysis confirms Iranian origin. GCC emergency meeting called. Disruption expected to extend beyond 48h.",
          "evolution_score": 0.83,
          "asset_projection": { "asset": "Brent Crude", "price": "$77.20", "change": "+1.8%", "narrative_driven_pct": 62 }
        },
        {
          "update_id": "ev_003",
          "timestamp": "2026-06-04T06:45:00Z",
          "type": "frame_shift",
          "evidence_titles": [
            "OECD warns 'dark scenario' if Gulf energy corridor disruption lasts through Q3",
            "Brent futures open gap-up at $78.00 as Asian trading begins",
            "US CENTCOM confirms additional naval assets to Persian Gulf"
          ],
          "source_count": 7,
          "reality_delta": "OECD macro warning elevates from energy-sector story to macro regime risk. Brent breaks $78. US naval deployment signals escalation expectation.",
          "evolution_score": 0.91,
          "asset_projection": { "asset": "Brent Crude", "price": "$78.00", "change": "+2.1%", "narrative_driven_pct": 68 },
          "sub_thread_spawned": "n21_geopolitics__kuwait_airport__brent_repricing"
        },
        {
          "update_id": "ev_004",
          "timestamp": "2026-06-04T10:15:00Z",
          "type": "evidence_update",
          "evidence_titles": [
            "Tanker rates for Gulf routes spike 40% in 24h as war risk premiums surge",
            "Kuwait airport reopening delayed indefinitely — foreign ministries advise撤离"
          ],
          "source_count": 9,
          "reality_delta": "Tanker rates spike confirms second-order economic impact beyond crude. Airport reopening timeline collapses.",
          "evolution_score": 0.73,
          "asset_projection": { "asset": "Brent Crude", "price": "$78.00", "change": "+2.1%", "narrative_driven_pct": 68 }
        }
      ]
    },
    {
      "thread_id": "n21_geopolitics__kuwait_airport__brent_repricing",
      "type": "sub_thread",
      "spawned_at": "2026-06-04T06:45:00Z",
      "spawned_by_update": "ev_003",
      "current_state": {
        "headline": "Brent Breaks $78 as Gulf Tanker Rates Spike 40% on War Risk",
        "they_say": "The oil risk premium is already priced in at current levels — limited upside from here.",
        "reality": "Brent opens gap-up at $78. Gulf tanker war risk premiums surge 40% in 24h. Insurance costs for Strait of Hormuz transit are repricing at levels last seen in 2019 Abqaiq-Khurais attack.",
        "thesis": "Crude futures lagging the physical market — war risk insurance and tanker rates are the leading indicator for a sustained $80+ Brent.",
        "source_count": 5,
        "last_updated": "2026-06-04T10:15:00Z"
      },
      "evolution": [
        {
          "update_id": "ev_003_sub_001",
          "timestamp": "2026-06-04T06:45:00Z",
          "type": "thread_creation",
          "reality_delta": "Sub-thread spawned from main story evolution ev_003. Brent gap-up analysis.",
          "asset_projection": { "asset": "Brent Crude", "price": "$78.00", "change": "+2.1%", "narrative_driven_pct": 68 }
        }
      ]
    }
  ]
}
```

#### 1C. Aggregate Living Stories — `data/publish/living_stories.json`

What the frontend fetches and renders directly. A compressed, render-optimized view:

```json
{
  "version": 1,
  "generated_at": "2026-06-04T10:15:00Z",
  "last_full_cycle": "2026-06-04T06:45:00Z",
  "next_micro_update": "2026-06-04T12:15:00Z",
  "next_full_cycle": "2026-06-04T18:45:00Z",
  "lead": {
    "story_id": "n21_geopolitics__kuwait_airport",
    "headline": "Iranian Drones Hit Kuwait Airport as Gulf Infrastructure Crisis Deepens",
    "status": "evolving",
    "update_count": 4,
    "last_updated": "2026-06-04T10:15:00Z",
    "updated_ago": "0 min ago",
    "they_say": "US-Iran strikes are contained to military targets — civilian infrastructure not at risk.",
    "reality": "Kuwait International Airport struck by Iranian drones on June 3. Civilian infrastructure targeting threshold crossed. Kuwait operations remain suspended.",
    "thesis": "Energy corridor infrastructure targeting threshold crossed. Brent repricing accelerates.",
    "actors": ["Iran", "Kuwait", "US Central Command"],
    "sector": "geopolitics",
    "has_live_updates": true,
    "latest_evolution_type": "evidence_update",
    "thread_count": 3,
    "thread_previews": [
      {
        "thread_id": "n21_geopolitics__kuwait_airport__main",
        "type": "main",
        "headline": "Main thread",
        "update_count": 4,
        "last_updated": "2026-06-04T10:15:00Z"
      },
      {
        "thread_id": "n21_geopolitics__kuwait_airport__brent_repricing",
        "type": "sub_thread",
        "headline": "Brent Breaks $78 as Tanker Rates Spike",
        "update_count": 1,
        "last_updated": "2026-06-04T06:45:00Z"
      },
      {
        "thread_id": "n21_geopolitics__kuwait_airport__gulf_state_repositioning",
        "type": "sub_thread",
        "headline": "GCC Emergency Meeting — Gulf State Positioning Shifts",
        "update_count": 2,
        "last_updated": "2026-06-04T06:45:00Z"
      }
    ],
    "asset_claim": { "asset": "Brent Crude", "target": "$79.40", "change": "+2.1%", "narrative_driven_pct": 68 },
    "image_url": "https://..."
  },
  "stories": [
    {
      "story_id": "n21_macro__oecd_dark_scenario",
      "headline": "OECD Warns Global GDP Faces 'Dark Scenario' as Iran-Gulf Crisis Persists",
      "status": "evolving",
      "update_count": 2,
      "last_updated": "2026-06-04T06:45:00Z",
      "updated_ago": "3h ago",
      "sector": "macro",
      "has_live_updates": false,
      ...
    }
  ],
  "archived_stories": [
    {
      "story_id": "n21_markets__yen_160_intervention",
      "headline": "Yen Hovers Near 160 as Traders Eye Intervention Risk",
      "status": "resolved",
      "resolved_at": "2026-06-04T06:45:00Z",
      "resolution_summary": "BOJ intervened at 159.80, yen corrected to 157.20 within 2h. Carry trade unwind did not materialize. Story archived.",
      "final_update_count": 3,
      ...
    }
  ]
}
```

#### 1D. Enhanced Editorial State — `data/editorial_state.json`

```json
{
  "cycle_number": 3,
  "last_lead_topic": "n21_geopolitics__kuwait_airport",
  "last_full_cycle": "2026-06-04T06:45:00Z",
  "last_micro_update": "2026-06-04T10:15:00Z",
  "last_frame": "second-order",
  "story_registry_version": 1,
  "active_story_ids": [
    "n21_geopolitics__kuwait_airport",
    "n21_macro__oecd_dark_scenario",
    "n21_macro__trump_tariffs_forced_labour"
  ],
  "archived_story_ids": [
    "n21_markets__yen_160_intervention"
  ],
  "total_stories_ever": 4,
  "last_human_detail_ids": ["HD-007", "HD-006"],
  "last_telegram_opening": "OECD warns 'dark scenario'...",
  "topic_history": ["geopolitics", "macro"],
  "micro_update_skips": 0,
  "total_evolution_events": 6,
  "skip_micro_update_until": null
}
```

---

### 2. Update Cadence

| Tier | Name | Schedule | LLM? | Cost/Run | Purpose |
|------|------|----------|------|----------|---------|
| T1 | `gazzetta-telegram-monitor` | Every 30m | Yes | $0.015 | Detect new events, set `has_new_evidence` flag |
| T2 | `gazzetta-living-story-micro-update` | Every 2h (:15) | **No** | $0.00 | Compare evidence, compute evolution scores, refresh asset prices, write timeline entries |
| T3a | `gazzetta-editorial-writer` | 06:45 / 18:45 | Yes | $0.03 | Full editorial write: new lead story, frame shifts, narrative analysis |
| T3b | `gazzetta-hourly-narrative-review` | 06:30 / 18:30 | Yes | $0.015 | Telegram post with living-story context |
| T3c | `gazzetta-focus-group-quality-gate` | 07:00 / 19:00 | Yes | $0.02 | Quality gate on full cycle (15 min after editorial) |

**Execution rules:**

1. **T2 micro-update runs on the :15 of every even hour** (08:15, 10:15, 12:15, 14:15, 16:15 + 20:15, 22:15, 00:15, 02:15, 04:15 — 10x/day).
2. **Skip condition:** If T1 (Telegram monitor) has detected zero novel entities in the last 2 hours, T2 is skipped and `micro_update_skips` increments. After 3 consecutive skips, T2 is suppressed until T1 finds new evidence.
3. **T3 runs are unchanged** but they now receive `living_stories.json` as input context. The LLM can:
   - Write new evidence into existing story threads
   - Spawn a new sub-thread when a subtopic graduates
   - Promote a sub-thread to lead story
   - Archive a resolved story
   - Override the evolution score with editorial judgment

**States and transitions:**

```
NEW_STORY → [T3 creates initial entry] → evolving
evolving → [T2 adds evidence, score stays >0.6] → evolving
evolving → [T2/T3 adds evidence, score crosses 0.85] → evolving + sub-thread spawned
evolving → [7 days no updates] → resolved
evolving → [T2 score drops below 0.6 for 48h] → stale → resolved
evolving → [Invalidation trigger fires] → resolved
resolved → [T3 editorial override] → archived
```

---

### 3. Pipeline Changes

#### 3A. New Script: `enrich_stories.py` (T2 micro-update runner)

Location: `gazzetta-di-kyiv/scripts/enrich_stories.py`

**Inputs:**
- `data/normalized/events_latest.json` — current evidence pool
- `data/processed/narrative_intelligence_latest.json` — current setups with actors, evidence_titles
- `data/story_registry.json` — persistent story registry
- `data/publish/asset_claims_latest.json` — current asset projections

**Algorithm:**
```
1. Load all inputs
2. For each active story in story_registry:
   a. Compute evolution_score between current events and story's evidence history
      - actor_match = jaccard_similarity(current_actors, story_actors)
      - geography_match = jaccard_similarity(current_geography, story_geography)
      - pillar_match = 1.0 if current_narrative_intelligence pillar matches story pillar else 0.3
      - recency = 1.0 if evidence is <2h old else max(0, 1.0 - (age_hours / 48))
      - evolution_score = actor_match * 0.4 + geography_match * 0.3 + pillar_match * 0.2 + recency * 0.1
   b. If score >= 0.6 AND has novel evidence:
      - Append evolution entry to timeline
      - Update story.last_updated, story.update_count, story.evolution_score_current
      - Write updated timeline JSON
   c. If score >= 0.85 AND story has no sub-thread for this angle:
      - Spawn new sub_thread entry in timeline
      - Add thread_id to story_registry
      - Log sub_thread_spawned in the parent evolution entry
   d. If score < 0.6 for 48h continuous:
      - Tag story as stale (don't resolve yet — editorial decision)
3. If any story was updated:
   - Rebuild data/publish/living_stories.json from story_registry + timelines
   - Increment editorial_state.micro_update_count
   - Write progress to editorial_state
4. Else: increment editorial_state.skip_micro_update_until counter
```

**Outputs:**
- `data/stories/{story_id}/timeline.json` — appended
- `data/story_registry.json` — updated
- `data/publish/living_stories.json` — rebuilt (if any change)
- `data/editorial_state.json` — count updated

**No-LLM guarantee:** `enrich_stories.py` uses only Python string matching, Jaccard similarity, and file I/O. Zero API calls. Runtime: <5s.

#### 3B. Modified Pipeline Chain

```
Current:
  collect_multisource.py → analyze_narratives_v2.py → [LLM editorial writer] → build_site.py

New:
  collect_multisource.py → analyze_narratives_v2.py
       ↓ (triggered every 2h)
  enrich_stories.py → [if evidence found] → update timelines + living_stories.json
       ↓ (triggered at 06:45/18:45)
  [LLM editorial writer] ← reads living_stories.json as context
       ↓
  update_story_registry.py (merge LLM decisions: new stories, frame shifts, archives)
       ↓
  build_site.py
```

#### 3C. New Cron Jobs

**Job: `gazzetta-living-story-micro-update`**
- Schedule: `15 8,10,12,14,16,20,22,0,2,4 * * *` (every 2h, skipping 18:15 and 06:15 which are too close to editorial cycles)
- Skills: None (pure Python script)
- Prompt: "Run scripts/enrich_stories.py in the gazzetta-di-kyiv repo"
- Workdir: `/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv`
- Model: None (no-LLM script)
- No-agent mode: No (the agent runs the script and reports what changed)

Actually better to set as a traditional cron job that runs the script directly. We can use the no_agent mode with a script that does the enrichment and only reports if there are changes.

**Modified Job: `gazzetta-agentic-nlp-guarded-autopost-8h`**
- Add `living_stories.json` to the context files loaded before the LLM writes
- The prompt gains: "You have access to living_stories.json with the current evolution state of every story. Reference thread timelines, update counts, and asset projection history when writing content."

#### 3D. Modified `build_site.py`

Add a new sync target to copy `data/publish/living_stories.json` to `site/api/v1/home/living_stories.json`:

```python
# In build_site.py, add:
shutil.copy2(
    os.path.join(DATA_DIR, 'publish', 'living_stories.json'),
    os.path.join(SITE_DIR, 'api', 'v1', 'home', 'living_stories.json')
)
```

---

### 4. Frontend Changes

#### 4A. Core Architecture: Stateful Renderer

`site/app.js` evolves from a one-shot render to a **poll-based stateful renderer**:

```javascript
// New architecture
const LIVING_DATA = './api/v1/home/living_stories.json';
const POLL_INTERVAL = 120000; // 2 minutes

let currentStories = {}; // keyed by story_id — never rebuild, only patch

async function pollLivingStories() {
  const data = await getJSON(LIVING_DATA, null);
  if (!data) return;

  // 1. Update masthead with cycle info
  updateMastheadLiving(data.generated_at, data.next_micro_update);

  // 2. Patch existing story cards (no re-render)
  data.stories.forEach(story => {
    const card = document.querySelector(`[data-story-id="${story.story_id}"]`);
    if (card) {
      patchStoryCard(card, story);
    } else {
      // New story — append to DOM
      appendStoryCard(story, story === data.lead);
    }
  });

  // 3. Update asset projections
  if (data.lead?.asset_claim) {
    patchAssetProjection(data.lead.asset_claim);
  }

  // 4. Update "updated ago" timestamps
  updateTimestamps();
}
```

#### 4B. Story Card Changes

Every story card gains the following new elements:

```html
<article class="card" data-story-id="n21_geopolitics__kuwait_airport"
         data-status="evolving" data-update-count="4"
         data-last-updated="2026-06-04T10:15:00Z">

  <!-- LIVING INDICATOR BADGE -->
  <div class="living-badge" data-has-live="true">
    <span class="living-dot gold"></span>
    <span class="living-text">Evolving</span>
    <span class="living-updates">+4 updates</span>
  </div>

  <!-- MAIN CARD BODY (unchanged layout) -->
  <div class="card-body"> ... </div>

  <!-- EVOLUTION TIMELINE (collapsed by default, toggled via click) -->
  <div class="evolution-timeline" data-expanded="false">
    <div class="timeline-entry" data-type="initial">
      <span class="timeline-dot"></span>
      <div class="timeline-content">
        <span class="timeline-time">06:45 · Jun 3</span>
        <p class="timeline-delta">Initial report — airport struck, operations suspended.</p>
      </div>
    </div>
    <div class="timeline-entry" data-type="evidence">
      ...
    </div>
    <div class="timeline-entry" data-type="frame_shift">
      ...
    </div>
    <div class="timeline-entry" data-type="evidence" data-latest="true">
      <span class="timeline-dot gold pulse"></span>
      <div class="timeline-content">
        <span class="timeline-time">10:15 · Today</span>
        <p class="timeline-delta">Tanker rates spike 40% — second-order impact confirmed.</p>
        <span class="timeline-sources">+2 new sources</span>
      </div>
    </div>
  </div>

  <!-- THREAD NAVIGATION -->
  <div class="thread-nav">
    <div class="thread-pill active">Main (4 updates)</div>
    <div class="thread-pill" onclick="switchThread('n21_geopolitics__kuwait_airport__brent_repricing')">
      Brent Repricing (1)
    </div>
    <div class="thread-pill">
      Gulf State (2)
    </div>
  </div>

  <!-- RESOLVED BADGE (if status=resolved) -->
  <div class="resolved-banner">
    <span class="resolved-icon">✓</span>
    <span>Resolved: BOJ intervened at 159.80, yen corrected to 157.20.</span>
    <span class="resolved-archive-link">Archived</span>
  </div>
</article>
```

#### 4C. CSS Additions

```css
/* Living badge */
.living-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0 0 0;
  font-family: Inter, sans-serif;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--ink-muted);
}
.living-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.living-dot.gold { background: var(--gold); }
.living-dot.gold.pulse { animation: pulse-gold 2s infinite; }
@keyframes pulse-gold {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* Evolution timeline */
.evolution-timeline {
  display: none;
  padding: 12px 0 8px 16px;
  border-left: 1px solid var(--divider);
  margin-left: 8px;
}
.card.expanded .evolution-timeline { display: block; }
.timeline-entry {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  position: relative;
}
.timeline-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--ink-muted);
  flex-shrink: 0;
  margin-top: 4px;
}
.timeline-dot.frame_shift { background: var(--gold); }
.timeline-entry[data-type="frame_shift"] .timeline-dot { background: var(--gold); }
.timeline-content {
  font-family: Source Serif 4, serif;
  font-size: 13px;
  line-height: 1.5;
  color: var(--ink-light);
}
.timeline-time {
  font-family: Inter, sans-serif;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ink-muted);
  display: block;
}
.timeline-delta { margin: 2px 0; }
.timeline-sources {
  font-size: 11px;
  color: var(--gold-dark);
  font-style: italic;
}

/* Thread navigation */
.thread-nav {
  display: flex;
  gap: 6px;
  padding: 8px 0 0 0;
  flex-wrap: wrap;
}
.thread-pill {
  font-family: Inter, sans-serif;
  font-size: 9px;
  padding: 3px 8px;
  border: 1px solid var(--divider);
  border-radius: 10px;
  cursor: pointer;
  color: var(--ink-muted);
  transition: all 0.15s;
}
.thread-pill.active {
  background: var(--gold-light);
  border-color: var(--gold);
  color: var(--gold-dark);
}
.thread-pill:hover { border-color: var(--gold); }

/* Resolved banner */
.resolved-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  margin-top: 8px;
  background: var(--sky-pale);
  border-radius: 4px;
  font-family: Inter, sans-serif;
  font-size: 10px;
  color: var(--ink-muted);
}
.resolved-icon { color: var(--sky); font-weight: bold; }
.resolved-archive-link {
  margin-left: auto;
  color: var(--sky);
  cursor: pointer;
}

/* Updated-ago badge on card */
.updated-ago {
  font-family: Inter, sans-serif;
  font-size: 9px;
  color: var(--ink-muted);
  display: inline-block;
  margin-left: 8px;
}
.updated-ago.recent { color: var(--gold); }

/* Masthead meta — show story count + update status */
.masthead-meta.living {
  font-size: 9px;
  display: flex;
  gap: 8px;
  align-items: center;
}
.masthead-meta.living .stories-count { color: var(--ink-light); }
.masthead-meta.living .next-update { color: var(--ink-muted); }
```

#### 4D. Story Detail View

When a story card with evolution data is expanded, the timeline shows beneath the card body. The lead story's evolution is always visible on page load. Sub-thread navigation switches the visible timeline without a page navigation.

Implementation: `site/app.js` gains:

```javascript
// ── Patch functions for living stories ──

function patchStoryCard(card, story) {
  // Update "updated ago" timestamp
  const agoEl = card.querySelector('.updated-ago');
  if (agoEl) agoEl.textContent = formatTimeAgo(story.last_updated);

  // Update living badge
  const badge = card.querySelector('.living-badge');
  if (badge) {
    badge.querySelector('.living-updates').textContent = `+${story.update_count} updates`;
    badge.dataset.hasLive = story.has_live_updates ? 'true' : 'false';
    const dot = badge.querySelector('.living-dot');
    dot.classList.toggle('pulse', story.has_live_updates);
    dot.classList.toggle('gold', story.has_live_updates);
  }

  // If new evidence arrived, flash the card
  if (story.last_updated && Date.now() - new Date(story.last_updated).getTime() < 600000) {
    card.classList.add('recently-updated');
    setTimeout(() => card.classList.remove('recently-updated'), 3000);
  }
}

function formatTimeAgo(isoString) {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

// ── Thread switching ──
function switchThread(storyId, threadId) {
  // Fetch detailed thread data (could be embedded in living_stories.json or lazy-loaded)
  // Replace the card's evolution-timeline content
  const card = document.querySelector(`[data-story-id="${storyId}"]`);
  if (!card) return;
  const timeline = card.querySelector('.evolution-timeline');
  // Load from embedded data or fetch stories/{storyId}/timeline.json?thread={threadId}
  // ...
}
```

#### 4E. Boot Flow (Updated)

```javascript
async function boot() {
  // 1. Load living stories (aggregate view)
  const livingData = await getJSON(LIVING_DATA, null);
  if (!livingData || !livingData.lead) {
    renderFallback();
    return;
  }

  // 2. Render all stories with living indicators
  const all = [livingData.lead, ...livingData.stories, ...(livingData.archived_stories || [])];
  const el = byId('newsCol');
  el.innerHTML = all.map((s, i) => livingCardHTML(s, i === 0)).join('');

  // 3. Update masthead with living metadata
  updateMastheadLiving(livingData.generated_at, livingData.next_micro_update);

  // 4. Render assets
  renderAssets();

  // 5. Wire interactions
  wireExpand();
  wireBBToggle();
  wireThreadNavigation();

  // 6. Start polling (2min interval)
  setInterval(pollLivingStories, POLL_INTERVAL);
}
```

---

### 5. Story ID Naming Convention

Story IDs must be stable across cycles. Convention:

```
{sector}__{actor_action_geography}__{suffix?}
```

Examples:
- `n21_geopolitics__kuwait_airport` — main story
- `n21_geopolitics__kuwait_airport__brent_repricing` — sub-thread
- `n21_macro__oecd_dark_scenario`
- `n21_markets__yen_160_intervention`

Generation: automatically derived from setup title in `enrich_stories.py`, using NER-style extraction of the primary actor + geography + action from the first evidence title. The `story_registry` maps original `setup_id` → canonical `story_id`.

---

### 6. Rollout Order

| Phase | What | Depends On | Effort |
|-------|------|-----------|--------|
| **P1** | Write `enrich_stories.py` with evolution scoring, timeline writing, and `living_stories.json` generation | Nothing | 3-4h |
| **P2** | Create T2 cron job running `enrich_stories.py` every 2h | P1 | 15min |
| **P3** | Modify `build_site.py` to copy `living_stories.json` | P1 | 5min |
| **P4** | Frontend: add living badge, timeline CSS, updated-ago timestamps. Keep polling disabled initially. | P1 | 3h |
| **P5** | Frontend: enable 2-min polling, thread navigation, evolution rendering | P4 (tested) | 2h |
| **P6** | Modify editorial writer prompt to consume `living_stories.json` as context | P1 | 30min |
| **P7** | Add `story_registry.json` and migration script for existing stories (backfill timeline from past cycles) | P1 | 1h |
| **P8** | Observer feedback + tuning of evolution score thresholds | P5+P6 in production | Ongoing |

---

### 7. Success Metrics

| Metric | Current | Target (2 weeks post-launch) |
|--------|---------|------------------------------|
| Stories with evolution updates per day | 0 | 4-8 |
| Avg update depth per story | 1 (static) | 3-5 timeline entries |
| Time from event to story update | 6-12h (next editorial cycle) | <2h (micro-update) |
| Frontend re-renders per day | 2 (full page) | ~6 (patch-only) |
| Pipeline cost/month | ~$1.80 | ~$2.00 (micro-updates are free) |
| Archived stories (resolved) | 0 | 3-5/week |
| Sub-threads spawned | 0 | 1-2/week |

---

### 8. Anti-Patterns (What NOT to Do)

- ❌ **Don't embed full evolution timelines in the main stories.json** — it's too large. Use a separate aggregate view (`living_stories.json`) with lazy-loaded detail.
- ❌ **Don't add WebSocket/SSE** — polling with `cache: no-store` is sufficient and avoids infrastructure complexity. The 2-min interval is fine for a static site.
- ❌ **Don't auto-archive stories without editorial approval** — the micro-update runner can tag as stale/resolved, but only the full editorial cycle (with LLM judgment) should move stories to `archived`.
- ❌ **Don't update every 30m** — 2h is frequent enough for evidence accumulation. Sub-30m updates risk churn without narrative value.
- ❌ **Don't regenerate living_stories.json if nothing changed** — check the skip condition first to avoid unnecessary git diff noise.
- ❌ **Don't add taxonomy language to the frontend UI** — "Evolving" is the only acceptable label (not "Narrative Acceleration Phase 2" or "Cross-source confirmation threshold crossed").
- ❌ **Don't break the existing stories.json format** — the legacy file must continue to exist for backward compatibility during rollout. The new frontend can prefer `living_stories.json` when available and fall back to `stories.json`.
