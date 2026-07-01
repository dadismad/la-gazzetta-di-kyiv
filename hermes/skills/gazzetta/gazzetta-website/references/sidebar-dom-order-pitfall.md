# Sidebar DOM Order Pitfall (v31.1 — June 2026)

## Symptom: Incomprehensible data appears above the masthead

On page load, a wall of ticker-coded navigation pills appears ABOVE the masthead:
```
complementary
Narrative Exposure
DXY RESERVE CURRENCY REALIGNMENT 258.9B
BRENT STRATEGIC ENERGY INDEPENDENCE 8.8B
...
FRAGILITY INDEX
trending_down Reserve Currency Realignment 108
...
LA GAZZETTA DI KYIV  ← masthead appears BELOW the data pills
```

This makes the site look broken to first-time visitors — they see raw data before the brand identity.

## Root Cause: Sidebar is the first child of `<body>`

The desktop sidebar (`<aside id="desktop-sidebar">`) is the FIRST direct child of `<body>`. On desktop (`md:flex md:flex-col fixed left-0`), it's a fixed-position sidebar — acceptable. But when the `hidden` class is missing or the responsive breakpoint doesn't apply, the sidebar renders as **inline block flow at the very top of the page**, pushing the masthead down.

The correct DOM order:
```
BODY
  DIV#main-content
    HEADER (masthead)
    NAV (tab buttons)
    MAIN (content)
  ASIDE#desktop-sidebar  ← AFTER main content, positioned via CSS
```

## Fix (in build_frontend.py template)

Move the `<aside id="desktop-sidebar">` element to AFTER the `<header>` masthead element, inside the main content wrapper. Position it via CSS (`position: fixed; left: 0; top: 0`) on desktop, and `hidden` on mobile.

Desktop sidebar positioning:
```html
<aside id="desktop-sidebar" class="hidden md:flex md:flex-col fixed left-0 top-0 h-full w-72 bg-surface border-r border-outline-variant z-10">
```

Mobile: sidebar is hidden (`hidden` class). It can be optionally toggled via hamburger menu.

## Verification

After deploy, verify masthead is the first visible element on BOTH viewports:

**Desktop:**
```js
// Masthead should be at the top
document.querySelector('h1').getBoundingClientRect().top < 20
```

**Mobile (390px viewport):**
```js
// Sidebar must be hidden or collapsed
getComputedStyle(document.getElementById('desktop-sidebar')).display === 'none'
```

## Prevention

Never place any content container before the masthead in DOM order. The masthead is the brand anchor — it MUST be the first thing every visitor sees, on every device. Sidebars, navigation pills, and data indices belong AFTER the masthead, positioned with CSS.
