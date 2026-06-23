# Material Symbols Font Rendering Pitfalls (v31.1 — June 2026)

## Symptom: All icons render as raw text codenames

343+ Material Symbols icon elements display their codename as visible text instead of icon glyphs:
- `auto_stories`, `sync_alt`, `call_split`, `account_tree`, `arrow_forward`
- `trending_down`, `bolt`, `public`, `language`, `rocket_launch`, `biotech`, `memory`, `sports_soccer`
- `expand_more`, `chevron_right`, `menu`, `close`

The font loads successfully (confirmed via computed style: `font-family: "Material Symbols Outlined"`) but icon elements render at **0x0 pixels**. The glyphs exist in the font but don't appear.

## Root Cause: Missing `opsz` axis in font URL + missing `font-variation-settings`

The Google Fonts CDN URL for Material Symbols requires the `opsz` (optical size) axis to render glyphs at a visible size:

```
WRONG: family=Material+Symbols+Outlined:wght,FILL@100..700,0..1
RIGHT: family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200
```

Without `opsz`, the font's default optical size may be zero, producing zero-width rendering even though the font file is loaded and the `font-family` is applied.

Additionally, the CSS must explicitly set `font-variation-settings` for browsers that don't infer axis defaults:

```css
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
```

## Fix (in build_frontend.py HTML template)

### Step 1: Fix the stylesheet link
```html
<!-- OLD -->
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">

<!-- NEW -->
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">
```

### Step 2: Add the CSS rule in the inline style block
```css
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
```

### Step 3: Verify
```js
// In browser console after deploy
const icon = document.querySelector('.material-symbols-outlined');
const cs = getComputedStyle(icon);
JSON.stringify({
  fontFamily: cs.fontFamily,           // Must be: "Material Symbols Outlined"
  width: icon.offsetWidth,             // Must be: > 0 (was 0 before fix)
  height: icon.offsetHeight,           // Must be: > 0 (was 0 before fix)
  fontVariationSettings: cs.fontVariationSettings
})
// Also check: document.querySelectorAll('.material-symbols-outlined').length === 0 elements with textContent matching icon names
```

## Detection Pattern

When icons are broken, count raw-text icon leaks:
```js
Array.from(document.querySelectorAll('.material-symbols-outlined')).filter(
  el => /^(auto_stories|sync_alt|call_split|account_tree|arrow_forward|expand_more|menu|close|trending_down|bolt|public|language|rocket_launch|biotech|memory|sports_soccer|chevron_right|pest_control)$/.test(el.textContent.trim())
).length
// 0 = fixed, >0 = broken (343 in June 2026 audit)
```

## Prevention

When adding Material Symbols to any HTML template, always include ALL FOUR axes in the URL: `opsz,wght,FILL,GRAD`. Never use the bare `wght,FILL` shorthand — it produces zero-width rendering in most browsers.

The `opsz` range (20..48) maps to optical sizes from 20px to 48px — matching typical icon sizes. The `GRAD` range (-50..200) controls weight grade but defaults to 0 for outlined style.
