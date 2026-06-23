# Devvit Post Composer — Architecture Reference

Built June 2026. Lives at `scripts/post_composer.py` in the Gazzetta project.

## Design rationale

Bots are detected by structural repetition, not content quality. A human reading two posts that share the same section layout, heading style, and opening format will flag them as automated — regardless of data quality.

## Architecture

```
[Data Pipeline] → [Structured Data] → [Post Composer] → [Varied Markdown] → [Reddit API]
                                              │
                                  ┌───────────┼───────────┐
                              PhraseBank  FormatTemplates  FormatSelector
```

## Components

### A) PhraseBank — Pure data, zero logic
- 24 openings
- 22 closings  
- 15 disclaimers (incl. empty strings)
- 18 uncertainty markers ("could be wrong", "not sure", "hard to call")
- 14 opinion frames ("Personally,", "My read:", "In my view,")
- 27 title templates (3 groups × 9: briefing, deep_dive, rapid)

### B) Format Templates — 10 structurally unique functions
Each produces distinct markdown. No two share layout:

1. `macro_radar` — Regime → Contradiction → Outlook → Actionable
2. `capital_flow_brief` — Flow-first: claim → projected → positioning → narrative
3. `narrative_lab` — Full analytical: THEY SAY / REALITY / THESIS / PLAY
4. `briefing_board` — Table-heavy with key/value pairs
5. `signal_scan` — Signal → Implication → Actionable, one sentence per line
6. `market_pulse` — Quick condensed: stat + contradiction + trade
7. `conviction_trade` — Deep dive: Thesis → Contradiction → Risk Framework → Play
8. `contradiction_deep_dive` — Divergence focus: gap between consensus and reality
9. `sector_spotlight` — Single sector zoom with bullet analysis
10. `asset_claims_table` — Directional claims: Asset → Direction → Why → Confidence

### C) FormatSelector
- Weighted random selection (confidence biases: high → deep analysis, low → conversation starter)
- 50-item anti-repetition history
- Title prefix enforcement: ≤30% same prefix in any batch
- Opening/closing history: 25-item window, no repeats

### D) GazzettaComposer
Takes story dict → selects format/title/opening/closing → calls format function → appends disclaimer → returns `{title, body, format, opening, closing}`.

## Usage

```python
from scripts.post_composer import GazzettaComposer

composer = GazzettaComposer(seed=42)
result = composer.compose(story)  # story dict with headline, they_say, reality, etc.

# For batch generation with guaranteed variety:
batch = composer.compose_batch(stories, count=20)
```

## Testing

`scripts/test_composer.py` — 7 verification tests:
1. 20 posts generated
2. All openings unique (20/20)
3. All closings unique (20/20)
4. Title format diversity ≤30% same prefix
5. Uncertainty markers + opinion frames in all posts
6. ≥3 format templates used
7. Format concentration ≤30% single format

## Integration with Devvit pipeline

Composer output includes `READY_FOR_DEVVIT_POST` marker. Feed composer output into `bake_payload.py` → `.node_modules/.bin/devvit upload` → `devvit install`.

## Principles (platform-neutral)

- Every post axis needs variance: title, opening, format, closing, styling, disclaimer
- Anti-repetition is NOT cycling (A-B-C-A-B-C is itself a pattern). Use weighted random with recent-history penalty.
- Data pipeline is the constant; presentation is the variable
- Refresh every deploy: different output on different days even with identical data (date-dependent seed)
