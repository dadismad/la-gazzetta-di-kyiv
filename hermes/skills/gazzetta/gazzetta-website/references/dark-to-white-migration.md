# Dark → White Metallic Migration Checklist

## Context

The website was on a v32 dark terminal theme (`body{background:#0A0A0F}`) and was migrated to white metallic (`body{background:#FFFFFF}`). This reference captures every pitfall and step so future migrations don't repeat the same mistakes.

## The Token System Discovery

**CRITICAL:** The Tailwind color tokens were ALREADY configured for light mode during the dark theme era:
- `surface: #FAF9F6` (warm paper — correct for light)
- `on-surface: #1A1C1A` (charcoal text — correct for light)
- `on-surface-variant: #444748` (medium grey — correct for light)

The dark theme was enforced by a single `!important` CSS override on `body`, plus hardcoded dark values on glass panels, zone headers, crosshair, decay meter, etc. The token system itself did NOT need changing. **Do not touch the Tailwind config block.**

## Complete Color Mapping

### Core Canvas
| Element | Before | After |
|---|---|---|
| `body` bg | `#0A0A0F` | `#FFFFFF` |
| `body` text | `#E6E4E0` | `#1A1C1A` |

### Glass & Panels
| Element | Selector | Before | After |
|---|---|---|---|
| Glass panel (masthead) | `.glass-panel` | `rgba(10,10,15,0.75)` | `rgba(255,255,255,0.85)` |
| Glass panel dark (sidebar) | `.glass-panel-dark` | `rgba(0,0,0,0.85)` | `rgba(255,255,255,0.92)` |
| Tactical radar (mobile) | `@media #tactical-radar` | `rgba(10,10,15,0.85)` | `rgba(255,255,255,0.85)` |
| Tactical radar border (mobile) | `@media #tactical-radar` | `rgba(255,255,255,0.05)` | `#E5E7EB` |

### Content Zones
| Element | Before | After |
|---|---|---|
| BREAKING zone header bg | `#141418` | `#F9FAFB` |
| ACTIVE zone header bg | `#141418` | `#F9FAFB` |
| SETTLING zone header bg | `#141418` | `#F9FAFB` |
| Crosshair plot bg | `#0D0D14` | `#FFFFFF` |
| Crosshair borders/dashes | `#1E1E24` | `#E5E7EB` |
| Decay meter bg | `#1E1E24` | `#E5E7EB` |
| Footer card bg | `bg-[#141418]` | `bg-[#F9FAFB]` |

### Typography
| Element | Before | After |
|---|---|---|
| `h2.text-gold` | `#8C7123` | `#B8860B` (DarkGoldenrod — visible on white) |
| Sidebar text class | `text-on-primary` (=white) | `text-on-surface` (=#1A1C1A) |
| Sidebar nav pills | `text-on-primary/70` | `text-on-surface-variant` |
| Mobile menu close | `text-on-primary` | `text-on-surface` |
| Share button hover | `hover:text-white` | `hover:text-on-surface` |
| GAP info icon hover | `hover:text-white` | `hover:text-on-surface` |
| Footer source text | `text-gray-300` | `text-on-surface-variant` |
| Verified badge text | `text-emerald-400` | `text-emerald-700` |
| Verified badge border | `border-emerald-500/20` | `border-emerald-500/40` |

## Contrast Traps (MISSED in original plan)

These 6 items were invisible white-on-white after the initial migration:

1. **Sidebar text** — `text-on-primary` renders white. On white glass background = invisible. Must be `text-on-surface`.
2. **Sidebar nav pills** — `text-on-primary/70` = white 70% opacity. Invisible on white.
3. **Share button hover** — `hover:text-white` on `#F9FAFB` card bg = disappears on hover.
4. **GAP info icon hover** — Same issue. `hover:text-white` on light bg = disappears.
5. **Mobile menu close** — `text-on-primary` on navy overlay = was fine on dark, needs `text-on-surface` on light.
6. **Tactical radar mobile bg** — Inside `@media` query, not caught by the desktop `.glass-panel` sweep.

## SETTLING Zone Double-Header Trap

The SETTLING zone has TWO instances on one JS template line (one for `settlingStories.length` ternary true, one for false). A `replace_all=False` patch only catches the first. Must use `replace_all=True` or target each variant uniquely.

## Verification Commands

After migration, verify with browser console:
```js
JSON.stringify({
  bg: getComputedStyle(document.body).backgroundColor,      // "rgb(255, 255, 255)"
  text: getComputedStyle(document.body).color,               // "rgb(26, 28, 26)"
  sidebarText: getComputedStyle(document.querySelector('#desktop-sidebar')).color,  // "rgb(26, 28, 26)"
  sidebarBg: getComputedStyle(document.querySelector('#desktop-sidebar')).backgroundColor  // "rgba(255,255,255,0.92)"
})
```

Verify remaining dark values in source:
```bash
grep -n '#0A0A0F\|#8C7123\|rgba(10,10,15\|#0D0D14\|#141418\|hover:text-white' build_frontend.py
# Must return empty — if anything remains, missed a trap.
```
