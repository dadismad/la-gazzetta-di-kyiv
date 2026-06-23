# Mobile Viewport Recalibration Guide (v2.2, June 2026)

Mobile-first design is mandatory for La Gazzetta di Kyiv. Every reader arrives via Telegram on a phone (375-414px). The desktop version is a fallback, not the design target.

## Known Defects Fixed (June 2026)

### 1. Masthead Wrapping
**Symptom**: "LA GAZZETTA DI KYIV" wraps to 2 lines on mobile.
**Root cause**: Fixed 26px font at all breakpoints + 0.1em letter-spacing + 1px text-stroke = rendered width ~340px in ~279px available space.
**Fix**:
```
text-lg sm:text-xl md:text-2xl          # 18px → 20px → 24px
whitespace-nowrap                       # single-line enforcement
tracking-tight sm:tracking-widest       # tight on mobile, wide on desktop
md:gold-outline                         # text-stroke only on desktop (blurry on small text)
```

### 2. Tab Navigation Wrapping
**Symptom**: Tab button text ("account_balance Capital Flows") wraps inside button.
**Fix**:
```
px-2 py-2 sm:px-4 sm:py-3              # compact padding on mobile
text-xs sm:text-metadata-sm             # downscaled font
whitespace-nowrap                       # no wrap
hidden sm:inline on text labels         # icon-only on mobile
max-w-full min-w-full overflow-x-auto   # scrollable container
```

### 3. Horizontal Overflow Leaks
**Symptom**: Cards, tables, and grids overflow viewport on small screens.
**Fix**:
```
# All articles: overflow-x-hidden
# Capital table: <div class="overflow-x-auto hide-scrollbar"> wrapper, min-w-[600px]
# Phase table: <div class="overflow-x-auto hide-scrollbar"> wrapper, min-w-[500px]
# Cross-asset grid: grid-cols-1 sm:grid-cols-2 md:grid-cols-4
# Horizontal padding: px-2 sm:px-margin-horizontal
```

### 4. Bottom Nav Overlap
**Symptom**: Last story card hidden behind fixed mobile bottom nav (56px).
**Fix**: `pb-20 sm:pb-stack-space-lg` on all four view containers (`#view-stream`, `#view-capital`, `#view-contradictions`, `#view-about`).

### 5. Global Typography Downscale for Mobile
| Element | Desktop | Mobile |
|---|---|---|
| Body text | 16px | 14px (`text-sm sm:text-body-md`) |
| Metadata | 13px | 12px (`text-xs sm:text-metadata-sm`) |
| Labels/badges | 12px | 10px (`text-[10px] sm:text-label-xs`) |
| Headlines | 22px | 16px (`text-base sm:text-lg md:text-headline-md`) |
| Capital table text | 16px | 14px (`text-sm sm:text-body-md`) |

## Mobile Verification Checklist

After any design change, verify at 375px viewport:
1. Masthead renders on ONE line
2. Tab buttons do NOT wrap
3. No horizontal scrollbar on any view
4. All bottom nav items visible without overlap
5. Story cards: headline visible, "Read Dispatch" tappable (48px min)
6. Capital Flows table: scrollable horizontally without breaking layout
7. Cross-asset grid: 1 column, labels readable
8. About phase table: scrollable horizontally

## Mobile-First Design Philosophy

Per C-Suite directive (June 2026):
- The story page IS the real homepage — 90% of traffic lands here
- Design for portrait, one-thumb scrolling, 375px wide
- Cards: full-width, 2-2.5 visible per screen (iPhone SE)
- Masthead: compact 48px bar, not a statement banner
- Navigation: bottom sheet or hamburger, not visible by default
- No hover states, no carousels, no desktop-only modals
- All interactive elements: 44px minimum tap target
- Warm white (#FAF9F6) background — easier on eyes than pure #FFFFFF
- Body text: 16px minimum, max 65 chars per line, 1.5 line height
- Desktop as fallback: single column, max-width 680px, centered
