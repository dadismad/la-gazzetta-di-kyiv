# Stitch / Diplomatic Ledger Design Verification (v27.3, June 2026)

## Background

The Stitch design system (Diplomatic Ledger spec, `/tmp/stitch_inspect/.../diplomatic_ledger/DESIGN.md`) was intended to replace the old `build_site.py`-generated template. As of June 20, 2026:

- **Production** (`www.lagazzettadikyiv.com`): Still serves old `build_site.py` output with `styles.css?v=29.0`. Masthead has inline SVG fox/lion + crossed bulavas. Content loaded via `dashboard.js`.
- **Staging** (`staging/stitch-mobile/index.html`): Has Tailwind CSS + Material Symbols structure but **data files 404** (`./data/stories-v4.json`, `./data/flows.json`). Shows "LOADING..." indefinitely.
- **Stitch ZIP files**: Static HTML prototypes with hardcoded sample data — not deployable as-is.

## Verification Workflow

### 1. Design Spec Compliance Check

Compare live computed styles against DESIGN.md using `browser_console`:

```js
JSON.stringify({
  card: {
    borderRadius: getComputedStyle(document.querySelector('article')).borderRadius,
    boxShadow: getComputedStyle(document.querySelector('article')).boxShadow,
    borderLeft: getComputedStyle(document.querySelector('article')).borderLeft,
    backgroundColor: getComputedStyle(document.querySelector('article')).backgroundColor
  },
  masthead: {
    borderBottom: getComputedStyle(document.querySelector('.masthead, header')).borderBottom,
    backgroundColor: getComputedStyle(document.querySelector('.masthead, header')).backgroundColor,
    fontFamily: getComputedStyle(document.querySelector('.masthead-name, h1')).fontFamily
  },
  nav: {
    borderBottom: getComputedStyle(document.querySelector('nav')).borderBottom
  },
  footer: {
    borderTop: getComputedStyle(document.querySelector('footer')).borderTop
  },
  heatBubble: {
    border: getComputedStyle(document.querySelector('.heat-bubble')).border,
    borderRadius: getComputedStyle(document.querySelector('.heat-bubble')).borderRadius
  },
  stylesheet: document.querySelector('link[rel="stylesheet"]')?.href || 'none',
  hasTailwind: !!document.querySelector('script[src*="tailwind"]'),
  hasMaterialSymbols: !!document.querySelector('link[href*="material-symbols"]'),
  bodyClass: document.body.className,
  htmlClass: document.documentElement.className
})
```

**DESIGN.md pass criteria (Diplomatic Ledger spec):**
- `card.borderRadius`: `0px` (Sharp/0px shape language)
- `card.boxShadow`: `none` (ink-on-paper, no shadows)
- `card.borderLeft`: `2px solid rgb(212, 175, 55)` (gold accent)
- `card.backgroundColor`: `rgb(250, 249, 246)` (warm archival paper #FAF9F6)
- `masthead.borderBottom`: `1px solid rgb(212, 175, 55)` (gold separator)
- `nav.borderBottom`: `1px solid rgb(212, 175, 55)` (gold separator)
- `footer.borderTop`: `1px solid rgb(212, 175, 55)` (gold separator)
- `heatBubble.borderRadius`: `0px` (DESIGN.md: "Sharp (0px)... no rounded corners")

### 2. Data Path Verification

When a page uses dynamic JS data loading, verify the fetch targets exist:

```bash
# Extract fetch paths from the HTML
curl -s $PAGE_URL | grep -oP 'fetch\(["\x27]\./[^"\x27]+'

# Verify each path resolves
for path in ./data/stories-v4.json ./data/flows.json; do
  STATUS=$(curl -sI "$BASE_URL/$path" | head -1 | awk '{print $2}')
  echo "$path: $STATUS"
done
```

**Common pitfall**: Staging pages at `staging/stitch-mobile/index.html` reference `./data/stories-v4.json`. This resolves to `staging/stitch-mobile/data/stories-v4.json` — which doesn't exist. The actual data lives at root `data/stories-v4.json`. Fix: either copy data to staging subdirectory, or use `../../data/` relative paths, or set `<base href="/">`.

### 3. Production vs Staging Disconnect Detection

Verify what's actually deployed vs what was claimed:

```bash
# 1. Check GCS bucket contents
gsutil ls gs://www.lagazzettadikyiv.com/
gsutil ls gs://www.lagazzettadikyiv.com/staging/stitch-mobile/

# 2. Compare raw HTML (curl bypasses JS rendering)
curl -s https://www.lagazzettadikyiv.com/ | head -20
curl -s https://www.lagazzettadikyiv.com/staging/stitch-mobile/index.html | head -20

# 3. Check CSS reference on production
curl -s https://www.lagazzettadikyiv.com/ | grep -o 'styles.css[^"]*'
# If this shows styles.css?v=29.0 — the Stitch design was NEVER deployed to production.
# The Stitch design uses Tailwind CDN, not styles.css.
```

### 4. Browser DOM Content Check

The browser snapshot (accessibility tree) is sparse. Supplement with:

```js
JSON.stringify({
  bodyChildren: document.body.children.length,
  storyCards: document.querySelectorAll('article, .story-card, .trader-card').length,
  mainHTML: document.querySelector('main')?.innerHTML?.substring(0, 500),
  dataLoaded: typeof window.STORIES_DATA !== 'undefined',
  fetchErrors: performance.getEntriesByType('resource')
    .filter(r => r.name.includes('.json') && r.responseStatus >= 400)
    .map(r => r.name)
})
```

## Key Pitfalls

- **Staging path resolution**: `./data/` relative to a staging subdirectory does NOT traverse up to root. Files must exist at that exact relative path.
- **Design claim vs reality**: A previous session claimed "Stitch design deployed" but only pushed to staging (with broken paths). Production was never touched. Always verify BOTH.
- **Heat bubble radius**: The old CSS sets `border-radius: 50%` on heat bubbles (circles). DESIGN.md requires 0px (sharp rectangles). This is a spec violation on the live site.
