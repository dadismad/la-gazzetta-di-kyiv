# Lucide Icon Standard for Gazzetta di Kyiv

## Specification
- **Library:** Lucide (lucide.dev) — MIT licensed, 1700+ icons
- **ViewBox:** 24×24 (match Lucide's native grid)
- **Stroke width:** 2px (NOT 1.5)
- **Stroke:** currentColor (inherits from parent color)
- **Fill:** none
- **Stroke linecap:** round
- **Stroke linejoin:** round
- **Rendered size:** 14×14 or 16×16 (scale via width/height attributes, not viewBox)

## Icon Map

| Use Case | Lucide Icon | SVG Reference |
|---|---|---|
| Share toggle button | `share2` | Three connected dots (nodes) — universal share symbol |
| Copy link | `link` | Two chain links — universal link/copy symbol |
| X / Twitter share | `twitter` | Lucide bird geometry — recognizable |
| Telegram share | `send` | Paper plane — clear send/share direction |
| LinkedIn share | `linkedin` | Lucide standard |
| Expand / chevron-down | `chevron-down` | V-shaped polyline |
| Resolved / check | `check` | Simple checkmark polyline |
| Close / dismiss | `x` | X-shaped crossing lines |
| Menu / hamburger | `menu` | Three horizontal lines |
| Search | `search` | Magnifying glass |
| External link | `external-link` | Box with arrow |

## Anti-Patterns

- ❌ Custom hand-drawn SVG geometry — never invent icons
- ❌ Emoji or Unicode characters as UI icons (📋 ✈ 𝕏 ▾ ✓)
- ❌ Mixed stroke widths across icon set
- ❌ Different viewBox sizes across icons (all must be 24×24)
- ❌ Hardcoded fill colors — always use currentColor

## CSS for Icon Buttons

```css
.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--ink-muted);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--sans);
  font-size: 11px;
}
.icon-btn:hover { color: var(--ink); }
.icon-btn svg { flex-shrink: 0; }
```
