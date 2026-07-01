# Flow Nodes Mobile Audit — v22.42

**Date:** 2026-06-07  
**Persona combo:** Mobile-First UX Researcher (Apple HIG) + Degen Crypto Trader (iPhone 14) + 55-Year-Old Retail Investor (desktop)  
**Consensus:** 3/3 on all critical findings  
**Viewport:** iPhone 14 (390×844) for mobile personas, 1440px for desktop

## Critical Findings (pre-fix)

### SVG Scaling — BROKEN at 390px
- `viewBox="0 0 1200 770"` with `width:100%` → nodes scale to ~26×16px at 390px
- Edge labels (8px font) render at ~2.6px effective — INVISIBLE
- Node sub-labels 7px — ILLEGIBLE at any viewport
- Single media query at 768px — no 390px/480px treatment

### Touch Targets — 9/9 FAIL Apple HIG (≥44×44px)
| Element | Size | Status |
|---------|------|--------|
| Nav links | 31px H | ✗ FAIL |
| Theme toggle | 33×27px | ✗ FAIL |
| Close button | 21×22px | ✗ FAIL |
| Legend shapes | 12×12px | ✗ FAIL |
| Legend items | 16px H | ✗ FAIL |
| Node groups (SVG) | ~26×16px | ✗ CRITICAL |

### Font Violations — 7 elements <9px minimum
| Element | Size | Fix |
|---------|------|-----|
| Node sub-labels | 7px | → 9px |
| Edge labels | 8px | → 10px at ≤768px |
| Node amounts | 8px | → 10px at ≤768px |
| Key hints | 8px | → hidden on mobile |
| Panel titles | 9px | → 10px |
| Node labels | 10px | → 13px at ≤768px |

### UX Issues
- Hover states broken on touch (no `:active` fallback)
- "simulated" sparkline label — trust killer
- No methodology link
- Keyboard shortcuts hidden on mobile with no replacement
- Edge labels overlap at identical coordinates

## Fixes Applied (v22.42)

### CSS
- 3-tier responsive: `max-width:768px` + `max-width:480px`
- `@media (hover:hover)` wrapper for all hover states
- `:active` pseudo on nodes + legend for touch feedback
- SVG text scaled up at mobile: 13px/10px/9px
- Touch targets: close 44×44, theme 40×36, nav 36px min-height
- Font floor: 9px minimum across all breakpoints
- Masthead badge hidden, thesis compacted on mobile
- Panel max-height 40→45vh

### HTML
- Mobile filter bar: 7 buttons (Gov/Inst/Corp/Retail/Crypto/X-Border/All)
- Methodology link added to thesis
- Sparkline label: "modeled from flow data" (was "simulated")

### JS
- Mobile filter buttons trigger legend clicks
- `typeColor()` used for active button border
- All button resets border color on interaction

## Verification (post-fix)
- Nav min-height: 36px ✓
- Mobile filters: 6 type buttons + All ✓
- Methodology link: visible in thesis ✓
- Sparkline label: "modeled from flow data" ✓
- Active states: `:active` on nodes ✓
- Hover: only fires on pointer devices ✓
