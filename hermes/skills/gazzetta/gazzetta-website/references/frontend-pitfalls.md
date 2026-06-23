# Frontend Pitfalls & Fixes (Gazzetta di Kyiv)

Quick reference for recurring frontend issues. Each entry: symptom → root cause → fix.

## Material Symbols Icons Not Rendering

**Symptom:** All `.material-symbols-outlined` icons show as raw text (`auto_stories`, `sync_alt`, `account_tree`) instead of glyphs. Icons have `width: 0, height: 0` despite correct font-family.

**Root cause:** The Google Fonts URL is missing the `opsz` (optical size) axis. Without it, the font's default optical size may be 0, causing zero-width rendering.

**Fix:**
1. Correct the stylesheet URL in the HTML `<head>`:
```
OLD: family=Material+Symbols+Outlined:wght,FILL@100..700,0..1
NEW: family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200
```
2. Add a global CSS rule:
```css
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
}
```

**Verification:** Any visible icon should have `offsetWidth > 0`. Query: `document.querySelector('.material-symbols-outlined').offsetWidth`

## Sidebar Above Masthead (Incomprehensible Top Section)

**Symptom:** Narrative exposure pills and fragility index appear above the masthead on page load.

**Root cause:** The `<aside id="desktop-sidebar">` is the first child of `<body>`, before the masthead `<header>`. On viewports where the sidebar isn't `position: fixed` (mobile), it renders as a visible block above the masthead.

**Fix:** Move the `<aside>` sidebar AFTER `<header>` (masthead) in DOM order. On desktop, the sidebar still positions as a fixed left panel via CSS. On mobile, it hides behind a hamburger or collapses entirely.

**DOM order must be:** Masthead → Sidebar → Tab Nav → Content

## Navigation Breakpoint Leakage

**Symptom:** Both desktop tab navigation and mobile bottom nav visible simultaneously.

**Root cause:** Desktop tab nav lacks `hidden` class for mobile. Mobile bottom nav has `md:hidden` (correct) but desktop nav has no counterpart.

**Fix:**
- Desktop tab nav: `class="hidden md:flex border-b..."`
- Mobile bottom nav: `class="md:hidden flex justify-around..."`
- Mobile hamburger menu: `class="hidden md:hidden..."` (hidden on all viewports until toggled)

## Narrative Pills as Dead Links

**Symptom:** Clicking sidebar narrative pills (DXY Reserve Currency Realignment 258.9B, etc.) adds `#` to URL, does nothing.

**Fix:** Replace `href="#"` with `href="javascript:void(0)" onclick="setNarrativeFilter('narrative_id')"` where `narrative_id` is quoted as a string. Must also implement the `setNarrativeFilter()` JS function that filters `STORIES` by `_container_title` and re-renders `#story-cards`.

**Critical detail:** The narrative ID in onclick MUST be quoted as a string: `setNarrativeFilter('dollar_decline')` NOT `setNarrativeFilter(dollar_decline)` (which passes an undefined variable).

## Headline Truncation Mid-Word

**Symptom:** Headlines like "BATRK liquidation signals decou" — cut off mid-word.

**Root cause:** The synthesizer (`contradiction_synthesizer.py`) applies `[:120]` hard character cut on headlines with no word-boundary check.

**Fix:** Replace `s[:120]` with word-boundary truncation:
```python
lambda h: h if len(h) <= 120 else h[:120].rsplit(" ", 1)[0] + "..."
```

## Coalescence Alert Duplication

**Symptom:** Two "CAPITAL CONVERGENCE" cards for the same narrative (one REINFORCING, one COMPLICATING) appear as visual duplicates.

**Root cause:** The coalescence computation groups by `(target_narrative, direction)` tuple, producing separate alerts when the same narrative has both REINFORCING and COMPLICATING signals.

**Fix — Cross-Current Aggregation:**
1. **Backend (Python):** Group signals by target narrative only, collecting both directions. When both `reinforcing_count >= 3` AND `complicating_count >= 3`, emit a single `type: "cross_current"` alert instead of two separate `type: "single"` alerts.
2. **Frontend (JS):** Detect `type === "cross_current"` and render a unified card with `swap_horiz` icon, title "CROSS-CURRENT CONVERGENCE", and side-by-side columns (gold panel for Reinforcing, crimson panel for Complicating). Use `grid grid-cols-1 md:grid-cols-2` for responsive layout.

## Data Integrity: Fix Data, Not Tests

**Principle:** When a test fails due to orphaned tags or stale references, fix the data (`stories.json`), never relax the test validation. A test that accepts orphans masks future pipeline regressions.

**Fix orphan tags:**
```python
# Find orphan
valid_ids = {s['story_id'] for s in all_stories}
orphans = set(tag_ids) - valid_ids
# Purge
data['tags_index'][tag_name] = [t for t in tag_ids if t not in orphans]
```
