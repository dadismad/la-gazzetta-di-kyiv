# Sub-Page JavaScript Safety — Null-Guard Protocol

## Problem

`app.js` functions (`renderPDR()`, `renderAnchor()`, `populateTeasers()`, etc.) run on EVERY page that loads `app.js`. Sub-pages (trades, flows, signal, track, event_horizon, flow-nodes) do NOT have all the same DOM elements as the homepage. When a shared function queries a homepage-only element without null-guarding, it crashes — silently — blocking all subsequent code in that function.

## The Crash Pattern

```javascript
// ❌ CRASHES on sub-pages — .pdr-trend only exists on homepage PDR gauge
function renderPDR(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.querySelector('.pdr-value').textContent = ANCHOR_PDR.value;
  el.querySelector('.pdr-trend').textContent = ANCHOR_PDR.trend;  // 💥 null.textContent
  // anchorCount update below NEVER runs
}
```

## The Fix Pattern

```javascript
// ✅ Null-guarded — survives any page
function renderPDR(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  const pv = el.querySelector('.pdr-value');
  if (pv) pv.textContent = ANCHOR_PDR.value;
  const trendEl = el.querySelector('.pdr-trend');
  if (trendEl) trendEl.textContent = ANCHOR_PDR.trend;  // safe skip
}
```

## Real Bug — June 2026

**Symptom:** `anchorCount` badge shows `—` on trades.html despite 14 anchor cards rendering.

**Chain:** `renderAnchor()` → `renderPDR('pdrGauge')` crashes at `.pdr-trend` null → `anchorCount.textContent = String(ANCHOR_ASSETS.length)` never reached.

**Affected pages:** All sub-pages with PDR gauge but no `.pdr-trend` element (trades, flows, signal, track).

**Detection:** `browser_console` with expression `document.getElementById('anchorCount')?.textContent` showed `—`. Manual `renderAnchor()` call confirmed crash at `renderPDR:362`.

## Page-Aware `byId()` vs Direct `querySelector()`

The `byId()` helper (app.js line 70) is page-aware — on product pages it searches within `.product-page` first:

```javascript
function byId(id) {
  const pp = document.querySelector('.product-page');
  if (pp) { const el = pp.querySelector('#' + CSS.escape(id)); if (el) return el; }
  return document.getElementById(id);
}
```

`byId()` safely returns `null` for missing elements. But `querySelector()` chained on a container (like `el.querySelector('.pdr-trend').textContent`) does NOT null-guard — it crashes if the inner query returns null.

## Verification Protocol for JS Changes

After ANY JavaScript change to `app.js`:
1. `browser_navigate` to homepage + check hero values
2. `browser_navigate` to each sub-page + `browser_console` to check key elements
3. Verify count badges (anchorCount, storyCount, etc.) show numbers not `—`
4. Verify no console errors on any page

**Anti-pattern:** `node --check` (syntax only) and `refresh_context.py` (static HTML only) do NOT detect these runtime crashes.
