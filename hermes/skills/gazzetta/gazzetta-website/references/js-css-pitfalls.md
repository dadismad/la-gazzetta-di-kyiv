# Gazzetta Website — JS & CSS Pitfalls (v25.19)

## Pitfall: CSS Class Name Mismatch with JS-Generated Elements

When adding CSS rules for JS-populated elements, always verify the ACTUAL class names in the DOM. JS rendering functions may use different class names than what CSS assumes.

**Examples of mismatch:**
- Flows page uses `.flow-row` (not `.flow-card`) for flow items
- Trades page uses `.anchor-item` (not `.anchor-card`) for trade items

**Fix pattern:** Include BOTH the expected and actual class names in CSS selectors:
```css
.product-page .flow-card,
.product-page .flow-row { /* ... */ }
```

**Verification:** After deploying CSS, check via browser_console:
```js
document.querySelectorAll('.product-page .container-body > div')[0].className
```

## Pitfall: Signal "Stories: 0" — Data-Loading Race Condition

`renderDivergenceMeter()` is called inside `fetchFlows()` (app.js line 403), which runs BEFORE `fetchStories()` populates `STORIES_DATA`. At render time, `STORIES_DATA` is still `[]`, so keyword-matching against story headlines returns 0 matches for every anchor asset.

**Fix:** After `STORIES_DATA` is populated, call `renderDivergenceMeter()` again to re-render with loaded data. Two injection points:
1. Standard stories path: after `STORIES_DATA = all` (line ~2281)
2. Living stories path: after `STORIES_DATA = all` (line ~2237)

```js
STORIES_DATA = all;
window.STORIES_DATA = all;
renderDivergenceMeter();  // Re-render now that stories are loaded
```

## Pitfall: i18n.js Missing from GCS Breaks ALL JS

If `i18n.js` is missing from the GCS bucket, the server returns index.html as the 404 fallback. The browser tries to parse HTML as JavaScript → `SyntaxError`. This cascades: `ReferenceError: i18n is not defined` at `formatT()`, which is called during `boot()`. Result: ALL pages render with zero content, masthead only.

**Detection:** `curl -sk https://www.lagazzettadikyiv.com/i18n.js | head -1` should return `// i18n.js...` not `<!doctype html>`.

**Fix:** `gsutil cp site/i18n.js gs://www.lagazzettadikyiv.com/i18n.js`

## Pitfall: Orphaned Code After Regex Cleanup

When stripping code blocks via regex (e.g., removing i18n wait logic), the regex must match the ENTIRE block including the closing braces. A regex that only removes the guard clause but leaves the block body creates orphaned statements (stray `setTimeout`, `});`, `}`) → `SyntaxError`.

**Example from this session:** `// i18n removed — direct render` comment was added but the `await new Promise(...)` body was left intact, creating a syntax error at line 2181.

**Fix pattern:** Use DOTALL regex to match the entire block, then verify with `node --check` before deploying.

## Product Page Lean Architecture (v25.17)

All product pages use `data-layer` attributes on `<main>` for INTEL/ALPHA color differentiation:

```html
<main class="product-page" data-layer="intel">  <!-- or data-layer="alpha" -->
```

CSS selectors:
```css
.product-page[data-layer="intel"] .container { border-left: 3px solid #3B82F6; }
.product-page[data-layer="alpha"] .container { border-left: 3px solid #D4AF37; }
.product-page[data-layer="intel"] .container-subtitle { background: #1E293B; color: #E2E8F0; }
.product-page[data-layer="alpha"] .container-subtitle { background: #D4AF37; color: #0F172A; }
```

**Exception:** `flow-nodes.html` uses `<body class="cn-body">` with no `<main>` tag — it has its own custom CSS architecture. Do NOT add `data-layer` or `product-page` classes to it.
