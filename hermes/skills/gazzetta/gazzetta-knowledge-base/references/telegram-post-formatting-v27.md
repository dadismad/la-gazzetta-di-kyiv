# Telegram Post Formatting (v27.2, June 2026)

## format_story() Pitfalls

The `cco_telegram.py` `format_story()` function had three bugs discovered during the June 12, 2026 audit:

### 1. Contradiction Score Displayed as Percentage

**Bug:** `f"Contradiction: {contradiction:.0%}"` where `contradiction` is 50 (0-100 scale).
**Result:** Displays "Contradiction: 5000%" — Python's `:.0%` multiplies by 100.
**Fix:** Use `f"Contradiction: {contradiction}/100"` — the score is already on a 0-100 scale.

Same issue affected `Confidence: {confidence:.0%}` — `confidence_pct` is already a percentage (50 means 50%).

### 2. No Paragraph Breaks

**Bug:** Message joined with `"\n"` (single newlines) between all sections. No blank lines.
**Result:** Wall of text with no visual hierarchy.
**Fix:** Add empty strings (`""`) between sections to create double-newline paragraph breaks:
```python
lines.append("")  # blank line between sections
```

### 3. Empty Sections Still Rendered

**Bug:** `if they_say:` only checked truthiness of the field AFTER it was already appended.
**Result:** "Reality:" header shown with empty content body.
**Fix:** Wrap each section in `if field:` before appending both header and content.

## Canonical Telegram Post Format

```
🔴 <b>Headline text — bold, with tier emoji prefix</b>
📈 INFLOW · $0.1B · TECH · 2.3× velocity
Contradiction: 75/100 · Confidence: 50%

<b>THEY SAY</b>
Consensus narrative text...

<b>REALITY</b>
Contradiction evidence text...

<b>🎯 THE PLAY</b>
Trade implication...

source_name · lagazzettadikyiv.com/story.html?id=story_id
```

### Tier emoji legend
- 🔴 MAX TENSION (contradiction ≥ 67)
- 🟡 HIGH TENSION (contradiction ≥ 34)
- 🟢 BUILDING/CONSENSUS (contradiction < 34)

### Flow direction emoji
- 📈 INFLOW
- 📉 OUTFLOW

## parse_mode Note

Use `parse_mode: "HTML"` with entity escaping (`&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`). Bold via `<b>` tags. NEVER use `parse_mode: "Markdown"` — story headlines contain `$`, `%`, `+`, `_` characters that break Telegram's Markdown parser (HTTP 400).

## Both Code Paths

Two files must be kept in sync:
- `scripts/cco_telegram.py` — `format_story()` used by the CCO entrypoint
- `scripts/generate_broadcasts.py` — `generate_telegram_post()` used by the broadcast generator

Both also exist in `agents_build/` for Cloud Run deployment.
