# White Metallic Color Migration (June 23, 2026)

## Migration: Dark Terminal (#0A0A0F) → White Metallic (#FFFFFF)

The v32 dark terminal theme was overridden by a single `!important` CSS rule on `body`. The Tailwind token system was already configured for light mode — the dark theme was enforced by hardcoded values.

### Color Token System (Already Light-Compatible)

These Tailwind tokens were already correct and did NOT need changing:
- `surface: #FAF9F6` (warm paper)
- `on-surface: #1A1C1A` (charcoal text)
- `on-surface-variant: #444748` (medium grey)
- `gold: #D4AF37`, `gold-accessible: #B45309`
- `crimson: #7F1D1D`, `emerald: #10B981`

### What Actually Changed

| Element | Before | After | Location |
|---|---|---|---|
| Body bg | `body{background:#0A0A0F!important` | `body{background:#FFFFFF!important` | Inline CSS |
| Body text | `color:#E6E4E0!important` | `color:#1A1C1A!important` | Inline CSS |
| Gold heading | `h2.text-gold{color:#8C7123!important}` | `h2.text-gold{color:#B8860B!important}` | Inline CSS |
| Glass panel | `rgba(10,10,15,0.75)` | `rgba(255,255,255,0.85)` | CSS |
| Glass panel dark | `rgba(0,0,0,0.85)` | `rgba(255,255,255,0.92)` | CSS |
| Crosshair bg | `#0D0D14` | `#FFFFFF` | Inline style |
| Crosshair borders | `#1E1E24` | `#E5E7EB` | Inline style ×2 |
| Zone headers | `#141418` | `#F9FAFB` | Inline style ×3 |
| Decay meter | `#1E1E24` | `#E5E7EB` | CSS |
| Tactical radar mobile | `rgba(10,10,15,0.85)` | `rgba(255,255,255,0.85)` | CSS @media |
| Tactical radar border | `rgba(255,255,255,0.05)` | `#E5E7EB` | CSS @media |

### Contrast Traps (Critical — Almost Missed)

When migrating from dark to light, Tailwind utility classes referencing dark-mode tokens MUST be changed:

| Element | Before | After | Why |
|---|---|---|---|
| Sidebar text | `text-on-primary` (= white) | `text-on-surface` (= #1A1C1A) | White text on white glass = invisible |
| Sidebar nav pills | `text-on-primary/70` | `text-on-surface-variant` | 70% white on white = invisible |
| Mobile menu close btn | `text-on-primary` | `text-on-surface` | Invisible button |
| Share button hover | `hover:text-white` | `hover:text-on-surface` | Disappears on hover |
| GAP info icon hover | `hover:text-white` | `hover:text-on-surface` | Disappears on hover |
| Footer source text | `text-gray-300` | `text-on-surface-variant` | Light grey on light bg |
| Verified badge text | `text-emerald-400` | `text-emerald-700` | Light green on light bg |

**PITFALL:** The Tailwind token system uses `on-primary: #FFFFFF` (white text on dark primary). Elements using `text-on-primary` expect a dark background. When the background becomes white glass, white text becomes invisible. Always audit `text-on-primary` and `hover:text-white` usage when migrating from dark to light.

### Zone Headers — Same-Line Multiple Occurrence

The BREAKING, ACTIVE, and SETTLING zone headers all use inline `style="background:#141418;border-left:..."` on the same line (line ~990 in build_frontend.py). The SETTLING header appears TWICE on the same line (one for stories present, one for empty state). When using `patch` with `replace_all=False`, only the first occurrence on the line is replaced. Use `replace_all=True` to catch both, then verify with grep.

### Verification

Use `browser_console` (not `browser_vision` — vision models hallucinate colors):
```js
JSON.stringify({
  bg: getComputedStyle(document.body).backgroundColor,
  text: getComputedStyle(document.body).color,
  sidebarText: getComputedStyle(document.querySelector('#desktop-sidebar')).color,
  sidebarBg: getComputedStyle(document.querySelector('#desktop-sidebar')).backgroundColor,
})
```
Expected: `{"bg":"rgb(255,255,255)","text":"rgb(26,28,26)","sidebarText":"rgb(26,28,26)","sidebarBg":"rgba(255,255,255,0.92)"}`
