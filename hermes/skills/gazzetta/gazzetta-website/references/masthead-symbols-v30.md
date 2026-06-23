# Masthead Symbols — v3.0

## Left: Machiavelli Sign (Fox & Lion)
- File: `templates/header.html`
- CSS class: `.masthead-machiavelli`
- SVG: 20x40 viewBox, `fill="none"`, `stroke="currentColor"`
- Content: Fox profile (top, facing right, sharp ears, long snout). Lion profile (bottom, facing left, mane circle, broad muzzle). Thin dividing line between them.
- Color: `var(--gold)` = #D4AF37
- Title attr: "Fox & Lion — prudence and strength"

## Right: Crossed Bulavas
- File: `templates/header.html`
- CSS class: `.masthead-bulavas`
- SVG: 28x38 viewBox (single SVG, NOT two separate SVGs)
- Content: Two identical bulava (ceremonial mace) groups at +-42deg rotation around center point (14,17). Each bulava has: shaft, handle bands, collar, head sphere with ornamental band, terminal finial.
- Color: `var(--gold)` = #D4AF37
- Title attr: "Crossed bulavas — Hetman's maces, dual authority"

## Name
- Text: "La Gazzetta di Kyiv"
- Font: Playfair Display, 22px, weight 400
- Color: #8B0000 (dark red)
- CSS class: `.masthead-name`

## CSS (in styles.css)
```css
.masthead-machiavelli { width: 20px; height: 40px; color: var(--gold); }
.masthead-machiavelli svg { width: 20px; height: 40px; }
.masthead-bulavas { width: 28px; height: 38px; color: var(--gold); }
.masthead-bulavas svg { width: 28px; height: 38px; }
```

## Pitfalls
1. NEVER revert to old class names (`.masthead-caduceus`, `.masthead-bulava`). These are gone.
2. CSS must be `styles.css` — hashed filenames break deploys.
3. The responsive override at max-width 600px scales both SVGs to 12x22px.
4. build_site.py injects templates/header.html into ALL public/*.html files. Changing the template changes every page.
