# v3.0 Degen Dashboard — Heat-Bubble Architecture

## Files

| File | Role |
|------|------|
| `public/dashboard.js` | Vanilla JS renderer. Fetches stories.json, computes per-narrative aggregates, renders bubbles and trader cards. No framework dependencies. |
| `public/index.html` | Contains `<section class="heat-section">` + `<section class="trader-feed">` in main area. References dashboard.js via templates/footer.html. |
| `public/styles.css` | v3.0 CSS appended at end of file. `.heat-bubble`, `.trader-card`, `.capital-bar`, etc. |
| `templates/footer.html` | MUST include `<script src="./dashboard.js"></script>`. build_site.py overwrites FOOTER:START→FOOTER:END with this template. |

## Bubble Sizing Math (dashboard.js)

```javascript
function capitalToSize(cap) {
    // Log-scale: $50M → 48px, $500B → 140px diameter
    const logMin = Math.log10(50_000_000);
    const logMax = Math.log10(500_000_000_000);
    const logVal = Math.log10(Math.max(50M, Math.min(500B, cap)));
    const t = (logVal - logMin) / (logMax - logMin);
    return Math.round(48 + t * 92);
}
```

## Color Mapping

| Average Gap | Class | Color |
|-------------|-------|-------|
| 0-39 | neutral | White (#F8F8F8) |
| 40-64 | warm | Amber (#FFF8E7) |
| 65-79 | hot | Gold (#D4AF37) |
| 80-100 | critical | Pulsing red (#8B0000 + gold glow animation) |

## Bubble Interaction

- Click a bubble: filters trader feed to that narrative only
- Click again (or "Show All"): resets to all narratives
- Active bubble gets dark border + gold glow box-shadow

## Trader Card Structure

```
[TICKER]                    [time ago]
HEADLINE (Playfair Display 16px)
┌─ Media Consensus ─────────────────┐
│ they_say text (grey bg, grey L border) │
└────────────────────────────────────┘
┌─ Market Reality ──────────────────┐
│ reality text (amber bg, gold L border) │
└────────────────────────────────────┘
CONTRADICTION EDGE: [score/100 badge]
████████████░░░░  $24.5B at stake
```

## Pitfalls

1. **CSS filename MUST be `styles.css`** — no hash. Hashed CSS gets nuked by `gsutil rsync -d` while HTML still references the hash. Result: zero CSS loads, symbols appear black.
2. **Footer template controls scripts** — if scripts aren't in `templates/footer.html`, build_site.py will strip them from all pages. COMPONENT:FOOTER:END marker must be BEFORE script tags in the HTML.
3. **Old stories lack new fields** — pre-synthesizer stories have no `contradiction_gap` or `capital_volume_usd`. Bubbles show "—" until the pipeline processes them through contradiction_synthesizer.py.
4. **Container name mismatch** — old stories use 6-container names (`flashpoints`, `monetary_order`). New system uses 8-narrative tags (`dollar_decline`, `energy_sovereignty`). dashboard.js NARRATIVES object only maps the 8 new tags.
