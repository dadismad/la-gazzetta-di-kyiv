# Tailwind CDN Specificity Cascade (v32.1, June 2026)

## The Problem

The Gazzetta site loads `cdn.tailwindcss.com` via a `<script>` tag to provide utility CSS classes. This CDN script dynamically generates and injects a `<style>` block **after** the page's inline `<style>` block (which lives inside `build_frontend.py`). 

Because CSS cascade resolves ties by **source order** (later wins), Tailwind's generated rules silently override your carefully-crafted inline CSS even when the specificity is equal.

## Detection Pattern

```js
// curl says one thing, browser says another — the CDN won
// curl sees: font-size: 14px
// browser shows: font-size: 11px
// Root cause: Tailwind CDN injected a later rule with equal specificity

JSON.stringify({
  bodyFont: getComputedStyle(document.body).fontSize,
  h3Font: getComputedStyle(document.querySelector('article h3.font-headline-md')).fontSize,
  bodyBg: getComputedStyle(document.body).backgroundColor
})
```

## The Fix: `!important` + High-Specificity Selectors

### Body background
```css
/* BEFORE — Tailwind overrides this */
body { background: #0A0A0F; color: #E6E4E0; }
/* AFTER — wins against Tailwind */
body { background: #0A0A0F !important; color: #E6E4E0 !important; }
```

### Font sizes
```css
/* BEFORE — Tailwind compound selector wins */
h3, .font-headline-md { font-size: 14px; }
/* AFTER — matches Tailwind's specificity + !important */
h3.font-headline-md, h3, .font-headline-md { font-size: 14px !important; }
```

### Desktop-first overrides
```css
/* ALWAYS place global overrides OUTSIDE any @media query.
   @media queries don't help against the CDN — Tailwind injects
   its own media queries that match. Use !important at global scope: */
.font-body-md { font-size: 13px !important; line-height: 1.5; }
h3.font-headline-md, h3, .font-headline-md { font-size: 14px !important; line-height: 1.35 !important; font-weight: 600; }
```

## Tailwind Compound Selector Trap

Tailwind CDN may generate rules like `h3.font-headline-md { font-size: 11px !important; }` — a compound selector with higher specificity than your `.font-headline-md` alone. Always inspect the actual CSSRules in the browser to see what Tailwind generated:

```js
for (let sheet of document.styleSheets) {
  try {
    for (let rule of sheet.cssRules) {
      if (rule.selectorText?.includes('font-headline-md')) {
        console.log(rule.selectorText, rule.style.fontSize, rule.style.getPropertyPriority('font-size'));
      }
    }
  } catch(e) {}
}
```

## Also Remove Redundant Inline Styles

The body tag used `style="background:#0A0A0F!important;color:#E6E4E0!important"` — this was a workaround for the same CDN cascade. Once the CSS `!important` rules are in place, remove the inline style from the `<body>` tag for cleaner markup.

## Single-File Architecture Note

The entire site CSS lives in a `<style>` block inside `build_frontend.py`. There is NO external stylesheet. `public/styles.css` is a ghost file — never referenced, never deployed. All CSS changes go through:
1. Edit `build_frontend.py` (the inline `<style>` block around line 340)
2. Run `python3 scripts/build_frontend.py`
3. Deploy `public/index.html` to GCS
4. Verify with `browser_console` → `getComputedStyle()` — NOT curl alone
