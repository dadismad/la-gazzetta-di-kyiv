# Flow Nodes Page — Mobile UX Architecture (v22.42)

## Architecture Overview

The Flow Nodes page renders an SVG node-link diagram (13 nodes, 23 edges) showing capital flow between 6 entity types. It includes an info panel with dynamically derived sources/destinations from edge data, delta badges, sparklines, and cross-links to story pages.

## Mobile Responsive Pattern (3-Tier Breakpoints)

```css
/* Base: 1200px viewBox SVG, desktop fonts, nav at full width */
/* ≤768px: flex→column layout, panel becomes bottom sheet, SVG text enlarged */
/* ≤480px: tighter spacing, smaller nav, compact masthead */
/* @media (hover: hover): hover effects ONLY on pointer devices */
```

Key principle: SVG text rendered at 7-10px is illegible when the SVG viewBox (1200×780) is scaled to a 390px viewport (~0.325x). Font sizes must be INCREASED at mobile breakpoints to compensate:

| Element | Desktop | ≤768px | ≤480px |
|---------|---------|--------|--------|
| Node labels | 10px | 13px | — |
| Node amounts | 8px | 10px | — |
| Node sub-labels | 7px | 9px | — |
| Edge labels | 8px | 10px | — |
| Legend items | 10px | 10px | 9px |
| Panel section titles | 9px | 10px | — |

## Touch Target Compliance (Apple HIG ≥44px)

Interactive elements on mobile:
- Nav links: min-height 36px (32px at 480px)
- Theme button: min-width 40px, min-height 36px
- Close button: min-width 44px, min-height 44px
- Legend items: min-height 36px with 6px padding
- Legend shapes: 14px (from 12px)
- Mobile filter buttons: min-height 36px each

## Touch vs Hover State Management

Critical pattern for SVG interactive elements:

```css
/* Touch devices get :active feedback */
.cn-node-group:active .cn-node-shape,
.cn-node-group.active .cn-node-shape { stroke-width: 2.5; }

/* Pointer devices get :hover (guarded!) */
@media (hover: hover) {
  .cn-node-group:hover .cn-node-shape { stroke-width: 2.5; }
  .cn-nav a:hover { color: var(--cn-text); }
  .cn-legend-item:hover { color: var(--cn-text); }
}
```

Without the `@media (hover: hover)` guard, hover effects are meaningless on touch devices and can cause sticky states after tapping.

## Mobile Filter Bar

Desktop: keyboard shortcuts (keys 1-6) + legend click to filter by node type.
Mobile: keyboard hint hidden, replaced by horizontal scrollable button bar:

```html
<div class="cn-mobile-filters" style="display:none;...">
  <button data-mf="gov">Gov</button>
  <button data-mf="institutional">Inst</button>
  ...
  <button class="cn-mf-reset">All</button>
</div>
```

CSS: `.cn-mobile-filters { display: none; }` → `display: flex;` at ≤768px.
JS: Each button triggers the corresponding legend item's click handler, sharing filter logic.

## Info Panel Design (Mobile Bottom Sheet)

At ≤768px, the side panel becomes a full-width bottom sheet:
```css
#cn-info-panel.cn-panel-open { width: 100%; max-height: 45vh; overflow-y: auto; }
```

Content is dynamically derived from edge data:
- **Sources**: edges where this node is TARGET (flows IN) — grouped by source node
- **Destinations**: edges where this node is SOURCE (flows OUT) — grouped by target node
- **Linked stories**: story_id from edges → clickable story.html links
- **Data sources**: extracted from edge `data_source` fields

## Trust & Comprehensibility

- Sparkline label: "modeled from flow data" (NOT "simulated" — trust killer)
- Methodology link: always present in thesis paragraph
- Data confidence %: visible with dashed edges for <60% confidence
- Timestamp: absolute ISO in masthead, with live indicator dot

## Keyboard Navigation (Desktop Power Users)

- 1-6: filter by node type
- Esc: close info panel (verified working with document-level keydown listener)
- Arrow keys: navigate between nodes (cycles through nodeMap keys)
- 0: reset all filters
