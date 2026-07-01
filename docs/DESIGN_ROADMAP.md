# La Gazzetta di Kyiv — Design Roadmap

**Version:** 1.0.0 | **Date:** 2026-06-27

---

## Current State: v33.0 White Metallic → v34.0 Dark Terminal

The platform is transitioning from white-metallic (#FFFFFF body, gold accents) to a dark institutional terminal (#0A0A0F, high-contrast amber/white).

### Design Tokens (v34.0 Dark Terminal)

```css
:root {
  /* Core palette */
  --bg-primary:    #0A0A0F;       /* Terminal black */
  --bg-secondary:  #12121A;       /* Card surface */
  --bg-tertiary:   #1A1A24;       /* Hover/active states */
  --text-primary:  #E6E4E0;       /* Body text — warm off-white, reduces eye strain */
  --text-secondary:#9B97B0;       /* Labels, metadata */
  --text-muted:    #5C5870;       /* Disabled, placeholder */
  
  /* Accents */
  --gold:          #D4AF37;       /* Unchanged — brand anchor */
  --gold-dim:      #8B7332;       /* Muted gold for borders */
  --crimson:       #C0392B;       /* BREAKING tags */
  --green:         #27AE60;       /* LONG / inflow indicators */
  --red:           #E74C3C;       /* SHORT / outflow indicators */
  --blue:          #5DADE2;       /* Interactive elements */
  
  /* Signal colors */
  --edge-extreme:  #FF6B35;       /* Δ Edge ≥ 80 — orange alert */
  --edge-high:     #D4AF37;       /* Δ Edge 60-79 — gold signal */
  --edge-medium:   #9B97B0;       /* Δ Edge 30-59 — neutral */
  --edge-low:      #5C5870;       /* Δ Edge < 30 — dormant */
  
  /* Typography */
  --font-display:  'Playfair Display', serif;
  --font-body:     'Inter', -apple-system, sans-serif;
  --font-mono:     'JetBrains Mono', 'Fira Code', monospace;
  
  /* Spacing */
  --phi:           1.618;
  --phi-sm:        1.272;
}
```

---

## Mobile Progressive Disclosure (v34.0)

### Default Mobile Card (Collapsed)

```
┌─────────────────────────────────────┐
│ 🏭  CAT   Δ EDGE 81   │ $245.30 ▲  │
│ Caterpillar's energy division is    │
│ pricing in a recession the media    │
│ hasn't spotted — a 3-month alpha    │
│ window.                             │
│ [ Tap to expand → trade setup ]     │
└─────────────────────────────────────┘
```

### Expanded Mobile Card

```
┌─────────────────────────────────────┐
│ 🏭  CAT   Δ EDGE 81   │ $245.30 ▲  │
│                                     │
│ THESIS                              │
│ Media consensus: industrial demand  │
│ recovery in H2.                     │
│ Reality: CAT dealer inventory at    │
│ 2016 levels — 3.2x normal.          │
│                                     │
│ TRADE                               │
│ Direction: SHORT                    │
│ Entry: $245.30                      │
│ Stop: $258.00                       │
│ Target: $218.00                     │
│ Conviction: HIGH                    │
│                                     │
│ ALPHA TRIGGER                       │
│ Market pricing CAT at 18x forward   │
│ earnings; dealer glut suggests      │
│ 14x is fair — 22% downside.         │
│                                     │
│ [▼ Collapse]                        │
└─────────────────────────────────────┘
```

### Implementation

```html
<details class="story-card-hint">
  <summary class="card-hook">
    <span class="asset-icon">🏭</span>
    <span class="ticker">CAT</span>
    <span class="edge-badge edge-81">Δ 81</span>
    <span class="price-move positive">$245.30 ▲</span>
    <span class="one-liner">Dealer glut signals 22% downside media hasn't priced</span>
  </summary>
  <div class="card-expanded">
    <!-- Full thesis, trade, alpha trigger -->
  </div>
</details>
```

**CSS Requirements:**
- `<details>` uses `scroll-behavior: smooth` for native expansion animation
- `summary::marker` hidden via `list-style: none`
- `card-hook` uses `display: flex; align-items: center; gap: 8px`
- `edge-badge` color varies by score tier (orange ≥80, gold 60-79, etc.)
- Max 3 visible line items in collapsed state at 390px viewport

---

## Horizontal Navigation (v34.0)

```
┌────────────────────────────────────────┐
│ ◀ STORIES │ FLOWS │ HORIZON │ NODES ▶ │  ← scroll-snap
└────────────────────────────────────────┘
```

```css
.top-nav {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;          /* Hide scrollbar */
  gap: 0;
  border-bottom: 1px solid var(--gold-dim);
}

.top-nav a {
  scroll-snap-align: start;
  flex: 0 0 auto;
  padding: 12px 20px;
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  white-space: nowrap;
}

.top-nav a.active {
  color: var(--gold);
  border-bottom-color: var(--gold);
}
```

---

## Future Visual Features (v35+)

| Feature | Description | Priority |
|---------|-------------|:--------:|
| **PnL Performance Cards** | Visual profit-loss tracker per trade thesis — entry price → current price → PnL % | P1 |
| **Interactive Heatmap** | 12-narrative grid with Δ Edge as color intensity, updated live | P1 |
| **Capital Flow Sankey** | Source → destination flow diagram replacing static node-link SVG | P2 |
| **Trade Calendar** | Timeline view of upcoming catalysts (FOMC, earnings, OPEC) overlaid with narrative positioning | P2 |
| **Dark/Light Toggle** | User-controlled theme switch (dark default, light available) | P3 |
| **Notification Bell** | Browser push for Δ Edge spikes > 15 points on watched narratives | P3 |

---

## Design Principles (Non-Negotiable)

1. **Frameless.** No border-radius on containers. No box shadows on cards. Structure expressed through borders and color, not depth illusions.
2. **Data-first.** Every visual element must encode data. If a color, shape, or position doesn't carry information, remove it.
3. **Mobile-native.** Design for 390px first. Desktop is the expanded view, not the default.
4. **Gold is signal.** Gold (#D4AF37) appears ONLY where there is a tradable edge. Never use gold as decoration.
5. **Conviction through contrast.** High Δ Edge = high contrast (orange on black). Low Δ Edge = muted (grey on dark). The visual intensity maps to signal intensity.
