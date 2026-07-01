# Stitch Design Integration Status (June 20, 2026)

## Current State

| Environment | Design | Status |
|---|---|---|
| Production (`www.lagazzettadikyiv.com`) | Old `build_site.py` template + `styles.css?v=29.0` | Live |
| Staging (`staging/stitch-mobile/index.html`) | Stitch Tailwind CSS + Material Symbols | Broken (data files 404) |
| Design Spec | Diplomatic Ledger (DESIGN.md in Stitch ZIP) | Reference only |

## Key Differences: Live vs DESIGN.md

| Element | Live (old) | DESIGN.md spec |
|---|---|---|
| Background | `#FAF9F6` (warm paper) | `#FAF9F6` ✓ |
| Masthead icons | Inline SVG fox/lion + crossed bulavas | Material Symbols (`account_balance`, `pest_control`, `gavel` in staging) |
| CSS framework | Custom `styles.css` | Tailwind CDN with Material 3 tokens |
| Heat bubbles | `border-radius: 50%` (circles) | `border-radius: 0px` (sharp rectangles) |
| Nav pills | `<a class="container-pill">` | Tailwind-styled flex chips |
| Data loading | `dashboard.js` (fetch + render) | Inline JS fetch + render |
| Story cards | Gold left border, 0px radius ✓ | Gold left border, 0px radius ✓ |
| Shadows | None ✓ | None ✓ |

## Staging Issues

The staging `stitch-mobile/index.html` cannot load data because:
1. Fetches `./data/stories-v4.json` (resolves to `staging/stitch-mobile/data/` — doesn't exist)
2. Fetches `./data/flows.json` (same problem)
3. Neither a `data/` subdirectory nor `<base href="/">` is set

Fix options:
- Copy `data/stories-v4.json` and `data/flows.json` to `staging/stitch-mobile/data/`
- OR change fetch paths to `../../data/` + add `<base href="/">`
- OR serve the Stitch page from root (replace production `index.html`)

Full verification procedure: see `gazzetta-verify-deploy/references/stitch-design-verification.md`.
