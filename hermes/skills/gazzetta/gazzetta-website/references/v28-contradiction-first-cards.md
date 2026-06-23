# v28.0 — Contradiction-First Story Cards + Pipeline Corrections

Ratified June 2026. This reference documents the Phase 1 Product Re-Alignment
executed in commit `050153b`. See also `HERMES_DESIGN_AND_PRODUCT_GUIDELINES.md`
at repo root for the full 18-rule design system.

## SVG CSS-Loading Failsafe

Every SVG in `templates/header.html` MUST have explicit `width` and `height`
attributes matching their `viewBox`. When CSS is 404 (gsutil auth failure,
deleted hash, CDN edge cache), inline SVGs with only `viewBox` explode to
viewport width.

```html
<!-- CORRECT -->
<svg width="20" height="40" viewBox="0 0 20 40" fill="none" ...>
<svg width="14" height="38" viewBox="0 0 14 38" fill="none" ...>

<!-- WRONG -->
<svg viewBox="0 0 20 40" fill="none" ...>
```

Detection: `browser_console` → if caduceus SVG getBoundingClientRect().width > 100,
CSS isn't loading.

## livingCardHTML() — 4-Line Contradiction-First Structure

The `livingCardHTML()` function (app.js lines 1298-1401) renders each story as:

```
LINE 1: story-headline     — H3, 16px Source Serif 4, linked to full story
LINE 2: story-contradiction — Narrative: <they_say excerpt> + Reality: <reality excerpt> + Gap: <score>/100
LINE 3: story-flow          — $AMOUNT SECTOR DIRECTION VELOCITY (color-coded green/red)
LINE 4: story-actions       — Full intelligence report + View signal links
```

### Flow Indicator Color Coding
- INFLOW: green (#047857)
- OUTFLOW: red (#DC2626)

### Tier Badges (four contradiction levels)
- contradicted (red): gap >= 66/100
- divergent (gold): gap >= 51/100
- developing (blue): gap >= 31/100
- aligned (gray): gap < 31/100

### Card Layout
- Standard: #FFFFFF bg, 1px #E5E7EB bottom border, 16px padding
- Lead: 3px gold (#D4AF37) left border, 20px left padding
- Hover: #F9FAFB bg
- Expanded: `.story-expanded` div, toggled via `.card.expanded .story-expanded`

### Old Pattern (DEPRECATED)
The `card-collapsed` / `card-head` / `card-expanded-body` classes are no longer
used for story card rendering. They may still exist in other card contexts.

## CSS Design System (v28.0)

Located at `styles.css` lines 2628-2840. Key classes:
- `.story-card` — card container
- `.story-meta` — tier badge + freshness row
- `.story-headline` — headline (16px Source Serif 4, 600 weight)
- `.story-contradiction` — contradiction line (13px, italic excerpts, gap score)
- `.story-flow` — flow indicator row (12px Inter, color-coded)
- `.story-actions` — action links (11px Inter, uppercase)
- `.story-expanded` — hidden detail panel

## GCS Auth Correction

- **Working:** `~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil`
- **Broken:** `~/.hermes/hermes-agent/venv/bin/gsutil` (returns 401 on writes)
- **Account:** pureciclismo@gmail.com
- `shipit.sh` `GCLOUD_DIR` corrected to devvit SDK path

## Header Navigation — INTEL/ALPHA Hierarchy

`templates/header.html` now uses dropdown navigation:
- INTEL dropdown: Stories, Capital Flows
- ALPHA dropdown: The Signal, Trade Ideas, Track Record
- MENU: standalone link to About

## Operational Governance

All work governed by two repo-root files:
- `HERMES_OPERATIONAL_SOP.md` (v1.1) — 8 binding operational rules
- `HERMES_DESIGN_AND_PRODUCT_GUIDELINES.md` (v1.0) — 18 binding product/design/content rules

Key SOP rules for website work:
- Rule 1: No sed/regex on HTML/CSS/JS — use patch() or write_file()
- Rule 2: One change, one verify, atomic commits
- Rule 3: NEVER deploy to GCS without C-Suite approval
- Rule 6: SVGs must have explicit width/height failsafe
- Rule 7: browser_vision + getComputedStyle is gold standard
- Rule 8: Zero-symbol communication — no emojis, unicode icons, ASCII art

## deploy_routine.sh

10-minute refresh pipeline at repo root. Lighter than shipit.sh:
- No nuclear_clean, no git sync, no hashed assets
- Test gate is BLOCKING (aborts on failure)
- Uses devvit SDK gsutil for GCS deploy
- Crontab registered in commented-out state awaiting activation
