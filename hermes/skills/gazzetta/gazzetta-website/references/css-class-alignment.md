# CSS Class Name Alignment — JS-to-CSS Mismatch Pattern

**Date:** June 2026 (v25.19)

## Problem

CSS rules target theoretical class names (`.flow-card`, `.anchor-card`, `.signal-card`) but the JS-generated DOM uses different class names (`.flow-row`, `.anchor-item`, `.triangulation-item`). Deployed CSS silently fails to style content.

## Detection

On each product page, check the actual DOM class:
```javascript
browser_console("document.querySelector('.product-page .container-body').children[0].className")
// Or for specific containers:
browser_console("document.querySelector('.flows-list').children[0].className")
```

## Affected Classes (June 2026)

| CSS Assumed | DOM Actual | Page | Container |
|---|---|---|---|
| `.flow-card` | `.flow-row` | flows.html | `.flows-list` |
| `.anchor-card` | `.anchor-item` | trades.html | `#anchorGrid` |
| `.signal-card` | `.triangulation-item` | signal.html | `#signalGrid` |

## Fix Pattern

Always add the actual DOM class alongside the theoretical one in CSS selectors:
```css
.product-page .flow-card,
.product-page .flow-row {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-left: 3px solid #3B82F6;
  border-radius: 4px;
  padding: 14px 16px;
  margin-bottom: 10px;
}
```

## Prevention

Before writing CSS for a product page, verify class names via `browser_console` on the live page. Never assume class names from reading the JS source — the JS may have changed and the actual rendered HTML is authoritative.
