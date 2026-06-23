# Senior Web Designer — Design QA Checklist (v22.33)

Checklist the Senior Web Designer persona MUST audit in every focus group. Learned from the June 2026 Mike Green × Degen × Web Designer comprehensive review cycle.

## 1. Color Contrast (WCAG AA)

| Requirement | Threshold | How to Check |
|-------------|-----------|--------------|
| Normal text (<18px) | ≥4.5:1 contrast ratio | `browser_console`: `getComputedStyle(el).color` vs background |
| Large text (≥18px bold or ≥24px) | ≥3:1 | Same method |
| Green on white | `#047857` minimum (NOT `#059669` — 3.77:1 fails AA) | `grep '--green.*059669' styles.css` → replace |
| Gold on white | `#B8860B` minimum (NOT `#D4AF37` — 2.10:1 severe fail) | `grep '--gold.*D4AF37' styles.css` → replace |

**Proven fix (June 2026):**
```css
--green: #047857;   /* was #059669 — 3.77:1 → 5.1:1, AA-pass */
--gold:  #B8860B;   /* was #D4AF37 — 2.10:1 → 3.8:1, large-text AA-pass */
```

## 2. Font Size Minimums

| Element | Minimum (desktop) | Minimum (mobile 390px) |
|---------|-------------------|------------------------|
| Data badges (heat score, PDR mini, confidence) | 10px | 10px |
| Labels (container titles, section headers) | 11px | 10px |
| Body text | 13px | 12px |
| Fine print (timestamps, source badges) | 9px | 9px |

**Pitfall — 8px data badges**: The 2026 focus group found heat scores and PDR mini badges at 8px. Degen Trader: "invisible on mobile." Mike Green: "looks like data is hidden, not surfaced." Fix: minimum 10px for any data-bearing element.

## 3. Touch Targets (Apple HIG)

| Element | Minimum | Proven violations (June 2026) |
|---------|---------|-------------------------------|
| All interactive elements | 44×44px | Share buttons (38px), hero CTA (40px), flow expand hint (8×8px) |
| Tap targets in nav | 44px min-height | Product nav links (no min-height set) |

**Fix pattern:**
```css
.share-btn { min-width: 44px !important; min-height: 44px !important; }
.hero-btn { min-height: 44px; }
```

## 4. Inline Style Elimination

Count `style="..."` attributes on any dynamic page. Target: zero inline styles for layout/typography/colors (functional styles like `display:none` are acceptable).

**Proven 2026 cleanup**: 31 inline styles removed from index.html (nav, hero, flow freshness) + app.js (sector grid, flow rows). Replaced with CSS classes: `.nav-link`, `.sector-stat-box`, `.flow-aggregate-badge`, `.flow-freshness`.

## 5. Dead Font Audit

Check Google Fonts URL against actual CSS usage. Every font in the `family=` parameter must have at least one `font-family` reference in the stylesheet.

**Proven 2026**: Roboto (400, 500, 700) loaded via Google Fonts, zero CSS references. Removed → saved ~15KB.

## 6. Frameless Contract Enforcement

If the design language says "frameless" (no shadows, no borders, no radius — 1px dividers only):

| Check | Grep |
|-------|------|
| `border-radius` on containers | `grep 'border-radius: [^0]' styles.css` → flag any non-zero |
| `box-shadow` | `grep 'box-shadow' styles.css` → flag any non-none |
| Inline violations in HTML | `grep 'border-radius:[^0]' index.html` |

**Proven 2026 violations**: `.hero-btn` radius 6px, `.flow-row` radius 2px, `#onboardingOverlay` radius 4px + shadow. All fixed → radius 0, shadow none.

## 7. Rendering Bugs — Specific Patterns

| Bug | Symptom | Check |
|-----|---------|-------|
| border-left doesn't render | Red/green accent bar invisible | `borderLeftColor` set but `borderLeftWidth`/`borderLeftStyle` missing |
| Empty values in inline styles | `border-left-width: ;` (empty) | `grep 'style="[^"]*:[[:space:]]*;'` |

**Fix**: Use `el.style.borderLeft = '3px solid ' + color` (shorthand), not individual property assignment.
