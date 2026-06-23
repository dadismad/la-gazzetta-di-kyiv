# Gazzetta Website — Design Conventions (v26.1, June 2026)

## Masthead (v26.2 — nav links IN masthead row)

```
[☤ caduceus] La Gazzetta di Kyiv [⚔ crossed bulavas]    INTEL · ALPHA · MENU
```

- Left side: caduceus → name → bulavas (`.masthead-left`)
- Right side: INTEL · ALPHA · MENU as text links (`.masthead-right`)
- Name: Playfair Display 3em, color `#8B0000` (dark red)
- Nav links: Inter 13px, `#8B0000` (dark red matching name), `#B8860B` (gold) on hover
- Gold 2px `border-bottom`
- White background (`#FFFFFF`)
- Position: sticky, top: 0, z-index: 100
- **NO language buttons** — removed entirely June 2026
- **NO separate navigation bar** — `master-nav` is `display: none`
- **NO dark bar** — white masthead only

## Navigation (v26.2 — hidden, links in masthead)

The `<nav class="master-nav">` element is HIDDEN. Navigation links (INTEL/ALPHA/MENU)
live directly in the masthead row via `.masthead-right`:

```css
.master-nav { display: none; }

.masthead-nav-link {
  font-family: Inter, sans-serif;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  color: #8B0000;            /* dark red, matching masthead name */
  text-decoration: none;
  padding: 6px 14px;
}
.masthead-nav-link:hover {
  color: #B8860B;            /* gold on hover */
}
```

**HTML structure:**
```html
<header class="masthead">
  <div class="masthead-left">
    <span class="masthead-caduceus">[SVG]</span>
    <span class="masthead-name">La Gazzetta di Kyiv</span>
    <span class="masthead-bulava">[SVGs]</span>
  </div>
  <div class="masthead-right">
    <a href="./stories.html" class="masthead-nav-link">INTEL</a>
    <a href="./signal.html" class="masthead-nav-link">ALPHA</a>
    <a href="./about.html" class="masthead-nav-link">MENU</a>
  </div>
</header>
```

## Containers — ALL START COLLAPSED

All front-page `<section class="container collapsible">` elements start CLOSED.
User sees:
- Title bar with arrow indicator
- Hint/description text
- Clicks arrow to expand

**Never add `expanded` class** to containers in HTML. The user wants the page to present
a clean overview — "hints on what is happening inside their contents."

Active containers: Stories, Capital Flows, Trade Ideas, The Signal, Track Record

## Story Cards

- Single column, full width, stacked vertically
- Each story: own row (not multi-column grid)
- `border-left: 2px solid #D4AF37` — gold left edge on every card
- Lead card: `border-left: 3px solid var(--gold)`
- Bottom separator between rows

## Pitfalls

- **Masthead invisible in accessibility snapshots**: When masthead has no buttons
  (after removing lang-switch), `browser_snapshot` compact mode won't show it.
  Always use `browser_vision` to verify visual masthead changes.
- **CSS multi-block drift**: When CSS changes span multiple `execute_code` blocks,
  `site/styles.css` can fall behind. Always `cp styles.css site/styles.css` before deploy.
- **CDN edge cache**: Deploying to GCS doesn't instantly update the live page.
  Use cache-bust query params for verification: `?nocache=TIMESTAMP`
