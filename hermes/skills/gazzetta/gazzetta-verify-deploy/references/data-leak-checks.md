# DOM Data Leak Detection (v32.0+ June 2026)

**Discovered:** Focus group audit after Phase 8 deploy. 156/156 tests passed but 17 UX bugs found — all presentation-layer string leaks.

## Leak Categories

### 1. Raw DB Keys in Visible DOM

Strings from database schemas or internal status enums that leak into user-facing text.

**Examples found (June 2026):**
- `FEED_SOURCE: BLOOMBERG` — column name prefix on every card footer (should be just `Bloomberg`)
- `VERIFIED_DISPATCH` — internal pipeline status flag rendered as a badge (should be `Verified`)

**Detection:**
```js
// Browser console — scan for raw internal keys
JSON.stringify({
  feedSource: (document.body.innerHTML.match(/FEED_SOURCE/g)||[]).length,
  verifiedDispatch: (document.body.innerHTML.match(/VERIFIED_DISPATCH/g)||[]).length,
  rawDbKeys: Array.from(document.querySelectorAll('*')).filter(el =>
    el.childNodes.length === 1 && el.childNodes[0].nodeType === 3 &&
    /^(FEED_SOURCE|VERIFIED_DISPATCH|PIPELINE_STATUS|INGESTION_STATE)/.test(el.textContent.trim())
  ).length
})
// PASS: all counts = 0
```

**Root cause:** The `injectSourceAttribution()` function in `build_frontend.py` (JS template, ~line 989) concatenates raw strings into `innerHTML` without humanizing them. Use `sourceData.charAt(0).toUpperCase() + sourceData.slice(1)` and replace internal status strings with human-readable alternatives.

### 2. Material Icon Names as Visible Text

Material Symbols `<span class="material-symbols-outlined">icon_name</span>` uses the text content as the icon glyph selector. The font replaces the text with the icon — but if the font fails to load (CDN issue, 404), the raw icon name appears as visible text. Screen readers also read the icon name aloud.

**Examples found:**
- `pest_control`, `gavel` — masthead icons
- `scatter_plot` — Narrative Crosshair heading
- `database` — card attribution footer
- `leaderboard` — GAP Leaderboard heading
- `share`, `unfold_more`, `radar`, `warning`, `trending_up`, `check_circle` — various UI elements

**Detection:**
```js
// Count icon spans without aria-hidden
JSON.stringify({
  exposedIcons: Array.from(document.querySelectorAll('.material-symbols-outlined'))
    .filter(s => !s.hasAttribute('aria-hidden') && s.textContent.trim().length > 0)
    .map(s => s.textContent.trim()).slice(0, 10),
  totalExposed: Array.from(document.querySelectorAll('.material-symbols-outlined'))
    .filter(s => !s.hasAttribute('aria-hidden')).length
})
// Fix: add aria-hidden="true" to all icon spans used as decoration
```

### 3. Light-Mode Classes on Dark Background

The site background is `#0A0A0F` (near-black). Tailwind light-mode classes produce invisible or broken-looking elements.

**Examples found:**
- `bg-gray-50` on `#0A0A0F` → white/light gray box on black background, jarring
- `text-gray-400` on `#141418` → invisible (gray text on dark gray)
- `border-gray-100`, `border-gray-200` → near-invisible borders
- Entire attribution footer rendered invisible

**Detection:**
```js
// Check for light-mode classes on dark background
JSON.stringify({
  lightBgOnDark: document.querySelectorAll('.bg-gray-50, .bg-white, .bg-gray-100').length,
  lightBorderOnDark: document.querySelectorAll('.border-gray-100, .border-gray-200').length,
  lightTextOnDark: document.querySelectorAll('.text-gray-400, .text-gray-500').length
})
// Fix: use dark equivalents: bg-[#141418], border-[#1E293B], text-[#747878]
```

### 4. Inline JS Handler Leakage

When `onclick` attributes contain complex inline JavaScript with string escaping, special characters in user data (headlines, trade thesis text) can break the attribute and render JS code as visible DOM text.

**Example found (June 2026):**
- 33 share buttons in BREAKING zone showed leaked `onclick` handler code as button text
- 680-character inline JS with `replace(/'/g,"\\'")` and `JSON.stringify()` nested escaping

**Detection:**
```js
// Check for JS syntax visible as text content
JSON.stringify({
  jsLeaked: document.body.textContent.includes('function()') &&
             document.body.textContent.includes('setTimeout'),
  handlerInText: (document.body.innerHTML.match(/onclick/g)||[]).length > 50
    ? 'Possible leak — onclick count unusually high' : 'ok'
})
```

**Fix pattern:** Replace inline onclick with `onclick="shareStory(this)"` referencing a global function. Store data in `article.dataset` attributes. Define the function once in a `<script>` block.

### 5. No Dollar Sign on Capital Numbers

Capital volume numbers displayed without `$` prefix look like abstract numbers rather than dollar amounts.

**Detection:**
```bash
# Check for bare capital numbers
curl -sk $SITE | grep -oP '>[0-9.]+[BM](?!</span)' | head -10
# If any match doesn't have $ before it, capital numbers are bare
```

**Fix:** Prefix formatting function with `$`: `f"${n:.1f}B"` instead of `f"{n:.1f}B"`.

## Integration into Verify-Deploy Workflow

After every deploy, add these checks to the JS interactivity sweep:
```js
JSON.stringify({
  // Data leaks
  feedSource: (document.body.innerHTML.match(/FEED_SOURCE/g)||[]).length,
  verifiedDispatch: (document.body.innerHTML.match(/VERIFIED_DISPATCH/g)||[]).length,
  // Icon accessibility
  exposedIcons: Array.from(document.querySelectorAll('.material-symbols-outlined'))
    .filter(s => !s.hasAttribute('aria-hidden')).length,
  // Light-mode residue
  lightClasses: document.querySelectorAll('.bg-gray-50, .bg-white, .text-gray-400').length,
  // JS leaks
  jsInText: document.body.textContent.includes('setTimeout(function')
})
// ALL must be 0/false
```
