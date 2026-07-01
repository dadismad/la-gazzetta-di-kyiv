# Gazzetta dark editorial nav + statement migration (session note)

## User request
Put the statement "People do not react only to facts. People react to stories they collectively believe about those facts." into the topnav container without the background image. Replace the image with colors where the text is visible more than the background itself.

## Color research
Researched premium intelligence/editorial publication tagline containers:

| Publication | BG Color | Text Color | Effect |
|---|---|---|---|
| The Economist | White/cream | Deep red + black | Authority through contrast |
| Foreign Affairs | Deep navy `#1a2433` | White/cream | Gravitas, institutional weight |
| Bloomberg | Near-black `#1a1a1a` | White + subtle blue | Terminal-grade seriousness |
| Stratfor/RANE | Dark charcoal | Muted gold/cream | Intelligence briefing aesthetic |
| FT | Salmon-cream `#fff1e5` | Dark ink | Editorial warmth |
| SemiAnalysis | `#0d1117` | Amber `#e6b450` on near-black | Analytical depth |

**Chosen:** deep ink gradient `#10151c → #181e26` with cream text `#ece4d5`.
Principle: dark background recedes, light text advances — text is the primary visual element.

## Implementation

### HTML change (`site/index.html`)
- Cut `<p class="statement">` from `.masthead`
- Pasted as first child of `<nav class="topnav">`, above the four `<a>` links

### CSS changes (`site/styles.css`)
1. `.topnav` — removed `background-image`, replaced with `background: linear-gradient(180deg, #10151c 0%, #181e26 100%)`, changed to `flex-direction: column`, `gap: 14px`, kept `min-height: 180px`
2. `.topnav .statement` — added: `font-family: var(--serif)`, `font-size: 18px`, `font-style: italic`, `color: #ece4d5`, `text-align: center`, `max-width: 680px`, `text-shadow: 0 1px 3px rgba(0,0,0,0.4)`, `text-transform: none`
3. `.topnav a` — updated for dark bg: `color: #ece4d5`, `background: rgba(255,255,255,0.08)`, `border: 1px solid rgba(255,255,255,0.12)`, `text-transform: uppercase`
4. `.topnav a:hover` — new: `background: rgba(255,255,255,0.16)`, `border-color: var(--gold-tint)`
5. Responsive `@media (max-width:760px)` — `.statement { font-size: 15px; max-width: 94vw }` replaced `.statement { font-size: 16px }`

## Verification pattern used

### Local (file://)
- `browser_navigate` to `file:///...index.html`
- `browser_snapshot(full=true)` confirmed `<p>` with statement text inside `<nav>`
- `browser_console` confirmed computed styles: `background: linear-gradient(rgb(16, 21, 28), rgb(24, 30, 38))`, `color: rgb(236, 228, 213)`, `font-size: 18px`

### Live (github.io)
- Polled `styles.css` for needle `10151c` in 7-second intervals → deployed on attempt 3 (~21 seconds)
- `browser_console` confirmed: `nav_has_statement: true`, `nav_bg: linear-gradient(...)`, `statement_color: rgb(236, 228, 213)`

### Browser snapshot blind spot
The compact accessibility-tree snapshot (`browser_snapshot` without `full=true`) did NOT show the `<p>` inside `<nav>`. The full snapshot and `browser_console` both confirmed it. Don't trust compact snapshots for non-interactive content inside nav containers.

## Commit
`208760c` — `feat(site): move statement into dark editorial nav, remove image, deep ink colors`
