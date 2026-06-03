# Gazzetta di Kyiv — Pipeline Redesign: LLM-Driven Editorial Layer

## Root Cause Diagnosis

The content is stale and repetitive because the entire pipeline is **deterministic template-filling**, not editorial intelligence.

### The broken chain:

1. **`collect_multisource.py`** — Actually works fine. Collects 100+ real news events from RSS/Reddit. ✓

2. **`analyze_narratives_v2.py`** — THE SMOKING GUN. Keyword-counter with hardcoded claims. Every generated setup gets identical:
   - Generic thesis: `"X second-order effects remain underpriced by consensus"` (line 94)
   - Same invalidation triggers everywhere (lines 154-157)
   - Same retail execution everywhere (lines 158-161)
   - Same contradiction pattern: `"X is fully priced, but X transmission effects remain underpriced"` (lines 167-173)
   - The `SEM` dict (lines 11-47) has 7 static claims that never change

3. **`prepare_publish_payloads_v2.py`** — Mechanical string formatter, not a writer:
   - Always picks `setups[0]` as the lead story (line 212)
   - Human detail ledger has 5 entries (HD-001 through HD-005), months old
   - CTA rotation is the ONLY variety mechanism — 5 variants per platform
   - No cross-cycle memory of what was posted last time
   - Content is assembled from JSON fields via Python string concatenation

4. **`agentic_research_publish_cycle.sh`** — Bash script that runs Python scripts. The LLM (deepseek-v4-pro) is **present but unused for writing** — it only executes the bash script and reports results.

### Why the content reads as identical:

| Aspect | Current State |
|--------|---------------|
| Lead story | Always `setups[0]` = geopolitics |
| Thesis text | Same template sentence every cycle |
| Human details | Same 5 facts recycled randomly |
| CTAs | 5 variants rotated — minimal variety |
| Voice per platform | Same content, different template structure |
| Cross-cycle awareness | Zero — no memory of what ran last time |

---

## The Fix: LLM-Driven Editorial Layer

The core change: **replace `prepare_publish_payloads_v2.py`'s string formatting with an LLM-powered editorial writer that takes the narrative intelligence data and produces unique, platform-adapted content each cycle.**

### Architecture:

```
collect_multisource.py  →  analyze_narratives_v2.py  →  ┌─────────────────────────┐
  (keep as-is)               (keep as-is, feeds data)   │ LLM EDITORIAL WRITER     │
                                                         │ (new: replaces prepare_) │
                                                         │                          │
                                                         │ 1. Select lead story    │
                                                         │ 2. Write per platform   │
                                                         │ 3. Enforce variety      │
                                                         │ 4. Verify guardrails    │
                                                         └──────────┬──────────────┘
                                                                    │
                                                         ┌──────────▼──────────────┐
                                                         │ telegram_latest.md       │
                                                         │ reddit_latest.md         │
                                                         │ website content          │
                                                         └─────────────────────────┘
```

---

## Platform Content Adaptation Principles

### Telegram (Rapid Intelligence Terminal)
- **Role:** Signal-first alert system. First thing you read in the morning.
- **Voice:** Sharp, urgent, actionable. Named actors. Explicit claims. Cause → effect.
- **Structure:** What changed → Why it matters now → What to do → One verified fact → Where to dig deeper
- **Length:** 80-140 words. Under 90 chars per paragraph. Bullets when possible.
- **Differentiator vs Reddit:** No "what do you think" — this is the intelligence, not the discussion. Faster, more direct, 1/3 the length.
- **Anti-pattern:** Don't just shrink the Reddit post. Telegram needs its own angle — typically the most actionable/market-moving signal.

### Reddit (Narrative Laboratory)
- **Role:** Hypothesis testing ground. Where the thesis meets the community.
- **Voice:** Analytical, falsifiable, curious. "Here's what we think is happening, here's why we might be wrong."
- **Structure:** Context → Narrative → Explicit contradiction → Second-order → Strategy → Discussion prompt → Evidence
- **Length:** 180-260 words. Paragraphs, not bullets. Invites debate.
- **Differentiator vs Telegram:** The contradiction and discussion prompt are the key differentiators. The Reddit post should feel like the first draft of a research note, not a finished product.
- **Anti-pattern:** Don't just expand the Telegram post. Reddit needs the "we might be wrong" energy.

### Website
- **Role:** Permanent intelligence terminal. The archive. The data layer.
- **Voice:** Institutional. Data-backed. Cross-referenced.
- **Structure:** Headline + thesis statement + evidence chain (3-5 data points) + actors/incentives map + invalidation criteria + related narratives
- **Length:** 300-600 words per story. Multiple stories per day.
- **Differentiator:** Longest form. Most data. No "what do you think" — this is the record.

---

## Content Variety Engine

To avoid repetition, the editorial writer must track and vary:

### 1. Lead Story Rotation
Track last 6 lead stories in `editorial_state.json`. Never repeat the same topic/sector as lead within 3 cycles. Priority: freshness > narrative strength > confidence score.

### 2. Angle Variation
Same topic can appear if angle changes:
- Geopolitics: Monday = Middle East risk premium, Tuesday = NATO posture, Wednesday = energy corridor fragility
- China: Monday = EV export friction, Tuesday = PBoC stimulus signaling, Wednesday = rare earth supply chain

### 3. Framing Rotation
Rotate through 5 editorial frames (not every frame fits every story):
- **Contradiction frame:** "Consensus says X, but Y"
- **Second-order frame:** "The obvious effect is X, but the hidden consequence is Y"
- **Velocity frame:** "X is accelerating faster than consensus models"
- **Convergence frame:** "Three separate narratives are merging into one"
- **Divergence frame:** "X and Y are decoupling, and here's why it matters"

### 4. Human Detail Freshness
- MUST pull at least one NEW verified detail per cycle from the actual news events
- Use `events_latest.json` titles/text to extract a real-world fact with source URL
- Append to ledger, rotate through last 20, retire anything older than 14 days
- Ledger should grow organically — 5 entries is not a magazine

### 5. CTA & Continuity Variation
- CTA rotation already works (keep it)
- Add: "Next cycle preview" line — hint at what's coming in 12h
- Add: "What we're watching" — 1-2 upcoming triggers

---

## Implementation Plan

### Step 1: Create the LLM Editorial Writer Prompt (cron job replacement)

The existing `gazzetta-agentic-nlp-guarded-autopost-8h` cron job runs a bash script. Replace its prompt with an LLM-driven workflow:

```
PROMPT FOR CRON JOB (agentic, not script-driven):

You are the Editor-in-Chief of Gazzetta di Kyiv, an AI-driven narrative intelligence publication. 
Your task this cycle: produce one Telegram post and one Reddit post from the latest pipeline data.

STEP 1: Load and analyze the data
- Read `data/processed/narrative_intelligence_latest.json`
- Read `data/publish/publish_manifest.json` for last cycle's lead story  
- Read `data/social_distribution_log.jsonl` (last 10 lines) for recent topics/CTAs
- Read `data/human_detail_ledger.md`

STEP 2: Select the lead story
- Pick the setup with: highest confidence × novelty (not the same topic as last cycle)
- If all topics were covered recently, pick the one with freshest evidence_titles
- Fallback: setups[0] if only one exists

STEP 3: Extract one new human detail
- Scan events_latest.json for a concrete, verifiable fact with source URL
- Must be: public, non-defamatory, time-anchored (last 7 days)
- Format: "¹ {detail} (source: {url})"
- Add to human_detail_ledger.md if novel

STEP 4: Select editorial frame
- Rotate through: contradiction / second-order / velocity / convergence / divergence
- Avoid the frame from last cycle

STEP 5: Write Telegram post
- Voice: Sharp, urgent, actionable. Named actors, explicit claims.
- Structure: Signal → Implication → Actionable (1-3 bullets) → Human detail → Continuity → CTA
- 80-140 words. Under 90 chars per line.
- DO NOT reuse phrases from last cycle. DO NOT start with "geopolitics second-order effects remain underpriced."

STEP 6: Write Reddit post  
- Voice: Analytical, falsifiable, discussion-inviting.
- Structure: Context → Dominant narrative → Explicit contradiction → Second-order → 24-72h path → Human detail → Discussion prompt → Evidence + CTA
- 180-260 words. 
- The contradiction must be SPECIFIC to this cycle's data, not the generic "X is fully priced but..."
- MUST differ in lead angle from Telegram post (different emphasis, not just longer version)

STEP 7: Write website story summaries (3-5 headlines + blurbs)
- One per setup. Each: headline (under 80 chars) + 2-sentence thesis + source count
- Write to `data/publish/website_stories_latest.json`

STEP 8: Quality gate
- Word count check per platform spec
- Cross-platform uniqueness check (Telegram and Reddit must not share >40% identical phrases)
- Evidence link check (at least 1 source URL per post)
- If any check fails, rewrite the failing post

STEP 9: Log everything
- Update social_distribution_log.jsonl
- Update editorial_state.json with: lead_topic, frame_used, human_detail_id, cycle_number

STEP 10: Output
- Print confirmation with: word counts, lead story title, frame used, new human detail
```

### Step 2: Create editorial_state.json

Track what the LLM writer needs for cross-cycle consistency:
```json
{
  "cycle_number": 0,
  "last_lead_topic": null,
  "last_frame": null,
  "last_human_detail_ids": [],
  "last_telegram_first_line": null,
  "last_reddit_first_line": null
}
```

### Step 3: Update the cron job

Replace `gazzetta-agentic-nlp-guarded-autopost-8h` with the new LLM-driven prompt. The bash script stays for data collection/analysis only — the LLM takes over from `prepare_publish_payloads_v2.py` onward.

### Step 4: Script changes

- `prepare_publish_payloads_v2.py` → REPLACED by LLM writer (the cron agent does the writing)
- `run_pipeline_v2.sh` → truncated to just collection + analysis (remove prepare + audit steps)
- `agentic_research_publish_cycle.sh` → simplified, LLM handles the editorial work

---

## Skills to Create

1. **`gazzetta-editorial-writer`** — The core LLM prompt and voice guide for per-platform content production
2. **`gazzetta-content-variety-engine`** — Rotation logic, frame selection, anti-repetition rules
3. **`gazzetta-platform-adaptation`** — Per-platform voice/style/format specs with examples

---

## Prompts for Hermes to Execute

### Prompt 1: Create the editorial writer skill
"Create a skill called `gazzetta-editorial-writer` that encodes the LLM editorial workflow described in docs/PIPELINE_REDESIGN_LLM_EDITORIAL.md. Include: Step-by-step workflow, platform voice specs, anti-repetition rules, quality gate checks, and an example of good vs bad output for both Telegram and Reddit."

### Prompt 2: Update the cron job
"Update cron job `gazzetta-agentic-nlp-guarded-autopost-8h` (ID: 011c8be0b17c) to load the `gazzetta-editorial-writer` skill and follow its workflow instead of running the bash script. The cron should: (1) run collect_multisource.py + analyze_narratives_v2.py via terminal, (2) then use the LLM to write content following the skill, (3) deliver to origin."

### Prompt 3: Seed the editorial state
"Create `data/editorial_state.json` with initial values (cycle 0, no history)."

### Prompt 4: Test run
"Run one cycle of the new editorial pipeline now and show me the Telegram and Reddit posts it produces."

---

## Success Criteria

After this redesign, each cycle should produce:
- Different lead story from last cycle (rotated among top 3 setups)
- Different editorial frame
- Fresh human detail (not HD-001 through HD-005 on repeat)
- Platform-differentiated voice (Telegram ≠ Reddit ≠ Website)
- Telegram: sharp, urgent, under 140 words
- Reddit: analytical, falsifiable, with SPECIFIC contradiction
- No template phrases ("second-order effects remain underpriced by consensus" should never appear)
