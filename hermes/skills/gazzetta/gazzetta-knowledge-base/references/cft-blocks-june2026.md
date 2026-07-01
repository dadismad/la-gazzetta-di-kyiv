# Catalyst-Flow-Trade (CFT) Data Layer — June 2026

## What It Is

A pre-computed CFT summary block injected into each narrative's entry in `__NARRATIVES_JSON__`. 
The client-side `app.js` can render CFT blocks at the top of each narrative stream section 
without backend changes.

## Where It Lives

`build_frontend.py` — `build_cft_block(narrative_id, stories, narrative_config)` function.
Called inside the narrative computation loop, result added as `"cft": {...}` to each narrative dict.

## CFT Data Structure

```json
{
  "cft": {
    "catalyst_headline": "Ceasefire deal's $300B Iran fund clashes with energy rally",
    "catalyst_gap": 70,
    "capital_usd": 0,
    "capital_fmt": "$0",
    "affected_tickers": ["URA", "NLR", "QQQ", "SMH", "SOXX"],
    "affected_asset_classes": ["energy", "tech", "commodities"],
    "domino": [
      {"narrative_id": "tech_convergence", "title": "Tech Convergence", "score": 0.6},
      {"narrative_id": "ai_chips", "title": "AI Chips", "score": 0.5}
    ]
  }
}
```

Value is `null` when no qualifying catalyst exists (narrative has < 3 stories or gap < 25).

## Catalyst Selection Rules

1. Filter stories where `narrative_id == target` OR narrative_id is in the story's `containers` list (multi-vector routing)
2. Pick the story with `max(contradiction_gap)`
3. Gate: gap must be >= 25 (too low = no meaningful signal)
4. Extract: headline, gap, capital_volume_usd, affected_tickers, affected_asset_classes

## Domino Ripple Computation

Read `narrative_weights` from the catalyst story. For every OTHER vector scoring >= 0.25:
- Include narrative_id, display title (from narratives.json), and score
- Sorted descending by score
- Threshold 0.25 filters noise while showing meaningful cross-vector exposure

## Capital Formatting

Self-contained formatter (doesn't rely on `fmt_b`):
- >= $1B: `$X.XB`
- >= $1M: `$X.XM`
- < $1M: `$X,XXX`

## Multi-Vector Routing in CFT

The catalyst search uses `containers` list, not just `narrative_id`:
```python
mine = [s for s in stories if narrative_id in (s.get("containers") or [s.get("narrative_id")])]
```

This means a single article can be the catalyst for MULTIPLE narratives simultaneously. 
The Iran ceasefire article (id 10013) is the catalyst for energy_sovereignty, tech_convergence, 
AND ai_chips — each CFT block shows the Domino ripples from THAT narrative's perspective.

## Client-Side Consumption (Phase 9)

`app.js` reads `NARRATIVES[n].cft`. If `cft` is not null:
- Render CFT block at top of narrative section
- Show catalyst headline + gap badge
- Show capital flow amount
- Show affected tickers as trade vectors
- Show Domino ripples as cross-exposure tags

## File Modified

`scripts/build_frontend.py` — added `build_cft_block()` function (~50 lines), 
injected `"cft": build_cft_block(...)` into narrative dict at line ~142.

No template changes. No JS changes. Data flows through the existing `__NARRATIVES_JSON__` placeholder.
