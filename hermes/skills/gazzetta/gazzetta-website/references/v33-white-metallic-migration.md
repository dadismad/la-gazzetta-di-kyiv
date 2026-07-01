# v33.0 White Metallic Migration (June 23, 2026)

Dark terminal (#0A0A0F) → White metallic (#FFFFFF) broadsheet design.

## What Changed

22 total edits to `build_frontend.py`:

### Base Color Mappings (16)
| Element | Before | After |
|---|---|---|
| Body bg | `#0A0A0F!important` | `#FFFFFF!important` |
| Body text | `#E6E4E0!important` | `#1A1C1A!important` |
| h2.text-gold | `#8C7123` | `#B8860B` (DarkGoldenrod) |
| .glass-panel | `rgba(10,10,15,0.75)` | `rgba(255,255,255,0.85)` |
| .glass-panel-dark | `rgba(0,0,0,0.85)` | `rgba(255,255,255,0.92)` |
| Crosshair bg | `#0D0D14` | `#FFFFFF` |
| Crosshair borders | `#1E1E24` | `#E5E7EB` |
| Zone headers (BREAKING/ACTIVE/SETTLING) | `#141418` | `#F9FAFB` |
| Decay meter | `#1E1E24` | `#E5E7EB` |
| Tactical radar mobile | `rgba(10,10,15,0.85)` | `rgba(255,255,255,0.85)` |
| Tactical radar border | `rgba(255,255,255,0.05)` | `#E5E7EB` |
| Footer card bg | `bg-[#141418]` | `bg-[#F9FAFB]` |

### Contrast Trap Fixes (6)
These were white text on dark elements that would become invisible on white:

| Element | Before | After |
|---|---|---|
| Sidebar class | `text-on-primary` | `text-on-surface` |
| Sidebar nav pills | `text-on-primary/70` | `text-on-surface-variant` |
| Mobile menu close | `text-on-primary` | `text-on-surface` |
| Share button hover | `hover:text-white` | `hover:text-on-surface` |
| GAP info icon hover | `hover:text-white` | `hover:text-on-surface` |
| Footer text | `text-gray-300` | `text-on-surface-variant` |
| Verified badge | `text-emerald-400` | `text-emerald-700` |

## Key Discovery

The Tailwind token system was **already light-mode compatible**: `surface: #FAF9F6`, `on-surface: #1A1C1A`. Only the `!important` body override and hardcoded dark inline values needed changing. The Tailwind `bg-surface`, `text-on-surface`, etc. classes all work correctly on white without token changes.
