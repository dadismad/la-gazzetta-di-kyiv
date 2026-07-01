# Multi-Vector Narrative Scoring Architecture (v1.0 — June 2026)

Replaces the legacy 1:1 narrative tagging with a 12-vector proportional matrix. Each story is scored against ALL narratives simultaneously, then routed to every container where it crosses a 0.40 inclusion threshold.

## Problem

Pre-v1.0: DeepSeek was forced to pick ONE narrative_tag per story. A TSMC Arizona fab delay got tagged `ai_chips` — the `deglobalization` and `china_ascent` dashboards never saw it. Capital volume flowed into one bucket. Multi-dimensional shocks were flattened into single-tag news.

## Solution Architecture

### Layer 1: Prompt Design (DeepSeek SYSTEM_PROMPT)

The LLM must emit a `narrative_scores` dict with all 12 vectors, not a single `narrative_tag` string.

**Schema:**
```json
{
  "narrative_scores": {
    "dollar_decline": "float (0.0-1.0)",
    "energy_sovereignty": "float (0.0-1.0)",
    "deglobalization": "float (0.0-1.0)",
    "china_ascent": "float (0.0-1.0)",
    "space_economy": "float (0.0-1.0)",
    "gene_editing": "float (0.0-1.0)",
    "tech_convergence": "float (0.0-1.0)",
    "wealthy_sports": "float (0.0-1.0)",
    "ai_chips": "float (0.0-1.0)",
    "crypto_reserve": "float (0.0-1.0)",
    "rate_cycle": "float (0.0-1.0)",
    "commodity_supercycle": "float (0.0-1.0)"
  },
  "affected_tickers": ["string"],
  "affected_asset_classes": ["string"]
}
```

**Proportionality constraint (critical — must be in prompt rules):**
```
Score EVERY vector against this event. Most events touch 3-5 narratives.
This is an asset-allocation weighting, not a binary tag.
Use the FULL 0.0-1.0 range PROPORTIONALLY — a 0.9 on the primary vector
might ripple at 0.3-0.4 into adjacent vectors. Set 0.0 only for genuinely
unrelated vectors. Do NOT assign 1.0 to multiple vectors.
```

**DeepSeek-specific requirements:**
- `response_format={"type": "json_object"}` requires the word "json" to appear explicitly in the prompt text (e.g., "Respond with ONLY valid json")
- `max_tokens: 1200` (was 800) — 12 floats + 2 arrays needs more headroom

### Layer 2: Market Context Expansion

`pick_market_context()` was refactored from single-narrative to ALL 12 vectors:

**Old:** took `(narrative_tag, prices)`, returned ~8 lines for one vector's tickers + SPY/QQQ/VIX benchmarks.
**New:** takes only `(prices)`, iterates all 12 canonical vectors, returns ~50 lines with clear delimiters:
```
--- Vector: energy_sovereignty | Tickers: URA, NLR, REMX, URNM ---
  URA: $48.19 (+2.31%) ...
--- Vector: dollar_decline | Tickers: GLD, UUP, SLV, IAU ---
  GLD: $389.91 (+0.34%) ...
...
--- BENCHMARKS ---
  SPY: $5900.00 (+0.15%) [benchmark]
```

This gives the LLM enough context to score zeroes accurately on unrelated vectors. Without it, the LLM defaults to 0.3-0.5 on vectors it has no data for.

### Layer 3: Assembly (`assemble_story`)

Extracts `narrative_scores` from LLM response, computes:

- **primary** = `max(scores, key=scores.get)` — highest-scoring vector (for legacy compat)
- **containers_list** = `[nid for nid, score in scores.items() if score >= 0.40]` — all vectors above threshold
- **narrative_confidence** = `scores[primary]` — the LLM's actual confidence, not a hardcoded default

Fallback: if `narrative_scores` is empty (old-format response or malformed), normalizes the old `narrative_tag` → `{tag: 1.0}` so legacy items still work.

Stored fields on each story:
- `container`: primary (string, backward compat)
- `containers`: list of all vectors >= 0.40 (NEW — multi-vector routing)
- `narrative_weights`: full 12-key dict (NEW — raw matrix for frontend)
- `narrative_id`: primary (was "unassigned")
- `narrative_confidence`: float from scores dict (was 0.0)
- `tags`: equals containers_list (frontend-ready)
- `affected_tickers`: from LLM if provided, else static map
- `affected_asset_classes`: from LLM if provided, else static map

### Layer 4: Merge Routing (`merge_stories`)

Container rebuild iterates `containers` list, not single `container` field:

```python
for s in all_stories:
    story_containers = s.get("containers") or [s.get("container", "tech_convergence")]
    for c in story_containers:
        if c in containers:
            containers[c]["stories"].append(s)
            containers[c]["count"] += 1
```

One story appears in 2-5 container buckets simultaneously. Container counts reflect total appearances (a story in 3 containers = +3 to total).

### Capping Decision (Layer 4b)

**Cap by primary vector only.** If a story appears in 3 containers, it counts as 1 toward the primary's cap (MAX_PER_NARRATIVE = 50), not 3. Rationale: capping by all containers would create asymmetric drain — a 5-vector story would consume 5 cap slots at 5x the rate of a single-vector story, penalizing multi-dimensional analysis. Capital volume is proportional to the primary vector; secondary appearances are discovery routing, not volume duplication.

```python
# Cap per primary container only
c = s.get("container", story_containers[0])
n = container_counts.get(c, 0)
if n < MAX_PER_NARRATIVE:
    capped.append(s)
    container_counts[c] = n + 1
```

## 0.40 Inclusion Threshold — Rationale

Empirically determined from Dry Run #1 (lunar economy article):
- `space_economy: 0.9` → primary ✓
- `tech_convergence: 0.3` → real ripple, but too weak for dedicated dashboard placement
- `deglobalization: 0.2` → thematic connection, not tradeable
- `energy_sovereignty: 0.1`, `ai_chips: 0.1` → noise

0.40 gates out thematic adjacency while catching genuine multi-dimensional shocks. A PBOC rate cut (expected 0.7+ on rate_cycle, 0.5+ on china_ascent, 0.4+ on commodity_supercycle) would route to 3 containers. A local crime story scores 0.0-0.1 across all vectors and routes to none (caught by materiality gate).

## Test Results (June 2026)

| Article | Primary | Containers | Vectors Hit |
|---------|---------|------------|-------------|
| Space economy / lunar ambitions | space_economy (0.9) | 1 | Only primary crosses 0.40 |
| Iran $300B reconstruction fund | energy_sovereignty (0.8) | 3 | +tech_convergence (0.6), +ai_chips (0.5) |

Both results demonstrate correct proportional scoring and appropriate threshold gating.

## Files Modified

- `scripts/contradiction_synthesizer.py` — SYSTEM_PROMPT, pick_market_context(), build_user_prompt(), call_deepseek(), assemble_story(), merge_stories(), run() loop
- `scripts/classify_stories.py` — DONE (Phase 8, June 21 2026): DeepSeek multi-vector bypass. Stories with `narrative_weights` skip keyword matching entirely. `tags_index` rebuild indexes by `containers` list (multi-vector) with fallback to `narrative_id` (legacy). Also fixed hardcoded `/opt/gazzetta-di-kyiv/data` paths to respect `GAZZETTA_HOME` env var for local/VM portability.
- `scripts/build_frontend.py` — no changes needed (reads containers dict, multi-container stories just appear in multiple sections)
- `scripts/calculate_capital.py` — no changes needed (groups by container, same story in 3 containers = counted in 3 capital pools — correct spillover behavior)
