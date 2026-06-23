# Browser Snapshot False-Negative Pattern (v24.0)

## Problem

The `browser_snapshot` tool renders an accessibility-tree view of the page. It detects only static HTML elements present at parse time — it CANNOT see dynamically-added DOM children created by JavaScript after page load.

## Concrete Examples from This Session

### Story Detail Page (story.html?id=...)
- **Snapshot reported:** 5 elements — masthead, language buttons, Telegram/Reddit links
- **Reality:** 8,629 bytes body, full `<main>` with `<article class="intel-report">`, headline, THEY SAY, REALITY sections, capital flow block, multi-persona blocks, related stories, related flows
- **Console proof:** `bodyLen: 8629, hasMain: true, mainHTML: "<div id=\"storyContent\"...intel-report...intel-header...TECH...THEY SAY..."`

### Product Pages (stories.html, flows.html, etc.)
- **Snapshot reported:** 13-14 elements — masthead nav only
- **Reality:** 32,608 bytes body with hidden containers populated by app.js boot() — flow rows, anchor grid, signal grid, hero confidence
- **Console proof:** `bodyLen: 32608, anyVisibleContent: ["86% BULLISH Strong conviction", "$300.0B ↑ IN crypto BTC BUY · HIGH"]`

## Detection Protocol

After every `browser_snapshot`, ALWAYS complement with `browser_console`:

```js
JSON.stringify({
  bodyLen: document.body.innerHTML.length,
  hasMain: !!document.querySelector('main'),
  mainLen: (document.querySelector('main')?.innerHTML || '').length,
  storyCards: document.querySelectorAll('.intel-report, .story-card, .flow-row, article').length,
  anyContent: document.body.textContent.trim().length > 50
})
```

## PASS/FAIL Heuristic

| bodyLen | hasMain | Conclusion |
|---------|---------|------------|
| < 2000 | false | Truly broken — static skeleton only |
| 3000-8000 | false/hidden | JS populated hidden containers — content exists but may not be visible |
| > 8000 | true | Page IS rendering — snapshot is a false negative |

### Archive Page (archive.html — v27.3 June 2026)

- **Snapshot reported:** 23 elements — masthead, nav pills, filter buttons, search box, footer. ZERO story cards visible.
- **Reality:** 99,673 bytes of innerHTML with 377 rendered `<article class="story-card">` elements, filter/search fully functional, container pills filter correctly.
- **Console proof:** `document.getElementById('archiveResults').innerHTML.length` → 99673, `document.querySelectorAll('article.story-card').length` → 52 after Monetary filter.
- **Why:** Inline `<script>` renders all 377 stories as HTML strings concatenated into `archiveResults.innerHTML`. The snapshot tool truncates output at ~8000 chars — 377 cards produce ~99KB which exceeds the limit entirely.
- **Detection:** `browser_console` → `getElementById('archiveResults').innerHTML.length` — if >5000, the page IS rendering. The snapshot is a false negative from volume, not timing.
- **Fix needed:** None — page works. Never report this as broken based on snapshot. Use `browser_console` DOM queries instead.

## Root Cause

The accessibility-tree snapshot reads elements from the initial DOM parse. JS frameworks (React, Vue) or manual DOM manipulation (innerHTML, appendChild) happen after the snapshot is captured. The snapshot has no mutation observer and no re-scan after JS execution. Additionally, the snapshot output is character-limited (~8000 chars) — pages with massive inline-rendered content (99KB+ archive pages, large tables) are truncated regardless of JS timing.
