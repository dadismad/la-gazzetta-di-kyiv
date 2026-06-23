# Navigation Breakpoint Isolation (v31.1 — June 2026)

## Symptom: Both desktop and mobile nav bars visible simultaneously

On desktop viewport, both the horizontal tab navigation bar AND the fixed bottom mobile nav bar are visible at the same time. The mobile nav's `fixed bottom-0` bar overlaps content at the bottom of the page.

## Root Cause: Missing `hidden` class on desktop nav

The desktop tab nav container has no responsive visibility class:

```html
<!-- WRONG — always visible on all viewports -->
<nav class="border-b border-gold/20 overflow-x-auto hide-scrollbar bg-surface">
  <div class="flex px-margin-horizontal gap-0 w-max max-w-4xl mx-auto" id="tab-nav">
    <button data-tab="stream">...</button>
    ...
  </div>
</nav>
```

The mobile bottom nav has `md:hidden` (hides on desktop) but the desktop nav has NO corresponding `hidden` class (doesn't hide on mobile). Result: both visible at both viewports.

## Fix

### Desktop tab nav

```html
<nav class="hidden md:flex border-b border-gold/20 overflow-x-auto hide-scrollbar bg-surface md:overflow-visible">
```

Key classes: `hidden` (hide by default), `md:flex` (show as flex on desktop breakpoint 768px+), `md:overflow-visible` (no scrollbar on desktop).

### Mobile bottom nav

```html
<nav class="md:hidden flex justify-around items-center bg-surface border-t border-gold px-margin-horizontal pb-2 pt-1 fixed bottom-0 left-0 w-full z-30">
```

Key classes: `md:hidden` (hide on desktop), `flex` (show as flex on mobile), `fixed bottom-0` (stick to bottom).

### Mobile hamburger menu

The overlay menu for the mobile sidebar content:

```html
<div class="hidden md:hidden bg-navy fixed inset-0 z-50 flex flex-col p-stack-space-lg" id="mobile-menu">
```

`hidden` = hidden by default, `md:hidden` = also hidden on desktop (belt-and-suspenders). Toggled via JavaScript.

## Verification

```js
// Desktop (>768px): mobile nav must be hidden
JSON.stringify({
  mobileNavDisplay: getComputedStyle(document.querySelector('nav.md\\:hidden')).display,
  desktopNavDisplay: getComputedStyle(document.querySelector('nav.hidden.md\\:flex')).display
})
// Expected: { mobileNavDisplay: "none", desktopNavDisplay: "flex" }

// Mobile (<768px): desktop nav must be hidden
JSON.stringify({
  desktopNavDisplay: getComputedStyle(document.querySelector('nav.hidden.md\\:flex')).display,
  mobileNavDisplay: getComputedStyle(document.querySelector('nav.md\\:hidden')).display
})
// Expected: { desktopNavDisplay: "none", mobileNavDisplay: "flex" }
```

## Prevention

Every nav element must have EXACTLY ONE combination active per viewport:
- Desktop nav: `hidden md:flex` (hidden <768px, visible >=768px)
- Mobile nav: `flex md:hidden` (visible <768px, hidden >=768px)
- Mobile overlay: `hidden` + toggled by JS (hidden always until activated)

Never use `block` or omit the `hidden`/`md:` prefix — both navs will leak across viewports.
