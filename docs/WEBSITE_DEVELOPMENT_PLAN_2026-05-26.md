# Gazzetta di Kyiv Website Development Plan (2026-05-26)

**Goal:** improve homepage story cards to be action-ready (named actors, explicit claim, implications, 24–72h bet snippet, and source links), then ship working UX controls.

## Task 1 — Fix interaction controls
- File: `site/app.js`
- Implement true card expand/collapse behavior:
  - `Collapse all` hides per-card detail blocks.
  - `Expand all` shows per-card detail blocks.
  - Search continues to filter cards.

## Task 2 — Upgrade story card intelligence payload
- File: `site/app.js`
- Enrich each card with:
  - Named actors
  - Core claim
  - Cause → effect implication sentence
  - Contradiction/misrepresentation lens
  - 24–72h bet snippet (instrument, direction, probability %, projection %, invalidation)

## Task 3 — Add full-intel source links
- File: `site/app.js`
- Convert `citations` into renderable links when URL-like; keep safe text fallback when not URL.

## Task 4 — Visual support for expandable detail
- File: `site/styles.css`
- Add styles for detail section and compact chips/labels so expanded mode remains readable.

## Task 5 — Verify build output
- Commands:
  - `python3 scripts/build_site.py`
- Verify:
  - Build succeeds.
  - `site/index.html` loads with cards, controls function, and links render.
