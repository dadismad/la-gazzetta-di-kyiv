# Material Icons Accessibility Pattern

Material Symbols font renders icon glyphs by replacing the text content of `<span class="material-symbols-outlined">` elements. The icon name IS the text content — the font swaps it for the glyph.

## Problem

When screen readers encounter these spans, they announce the raw icon name (e.g., "newspaper", "alpha", "account_balance") before or instead of the visible button label. Screen reader users hear "newspaper Stream" instead of just "Stream."

## Fix

Structurally separate the icon span from the label text, and add `aria-hidden="true"` to the icon span:

**Before:**
```html
<button>
  <span class="material-symbols-outlined">newspaper</span> Stream
</button>
```

**After:**
```html
<button>
  <span class="material-symbols-outlined" aria-hidden="true">newspaper</span>
  <span class="nav-label">Stream</span>
</button>
```

## Applies To

All Material Symbol icon spans in navigation, buttons, links, and interactive elements where the icon is decorative (not conveying meaning that the adjacent text doesn't already convey). Includes:

- Tab navigation buttons (newspaper, alpha, account_balance, analytics, psychology)
- Action buttons (share, unfold_more, send, close)
- Masthead icons (pest_control, gavel)
- Section header icons (leaderboard, scatter_plot, radar, database)

## Verification

```js
// All icon spans must have aria-hidden
JSON.stringify({
  totalIcons: document.querySelectorAll('.material-symbols-outlined').length,
  withAriaHidden: document.querySelectorAll('.material-symbols-outlined[aria-hidden="true"]').length,
  missing: document.querySelectorAll('.material-symbols-outlined:not([aria-hidden="true"])').length
})
// PASS: missing = 0
```
