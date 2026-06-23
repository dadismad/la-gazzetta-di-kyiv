## Masthead Symbols v27.2

### Layout
`[Fox & Lion] La Gazzetta di Kyiv [Crossed Bulavas]`

### Left: Machiavelli Sign (Fox & Lion)
- Class: `.masthead-machiavelli`
- SVG viewBox: 0 0 20 40, display 20x40px
- Color: `var(--gold)` = #D4AF37
- Title: "Fox & Lion -- prudence and strength"
- Design: Fox head profile (top, facing right, sharp ears/snout) + Lion head profile (bottom, facing left, mane)
- Line-art style, `stroke="currentColor"`, matching `currentColor` theme

### Right: Crossed Bulavas
- Class: `.masthead-bulavas`
- SVG viewBox: 0 0 28 38, display 28x38px
- Color: `var(--gold)` = #D4AF37
- Title: "Crossed bulavas -- Hetman's maces, dual authority"
- Design: Two identical ceremonial maces rotated +-42 degrees around center (14, 17)
- Single SVG element with two `<g transform="...">` groups
- Each mace: shaft, head sphere, collar bands, finial

### Name
- Class: `.masthead-name`
- Color: #8B0000 (dark red)
- Font: "Playfair Display", Georgia, serif, 22px, weight 400

### Template System
- Canonical source: `templates/header.html`
- Injected by `build_site.py` into all `public/*.html` via sentinel markers
- CSS classes defined in `public/styles.css`

### Hashed CSS Self-Nuke Pitfall
- HTML MUST reference `styles.css` directly (`<link href="./styles.css">`)
- NEVER use hashed CSS filenames (e.g. `styles.ab6de8dd.css`) with `gsutil rsync -d`
- `rsync -d` deletes old hashed files -- HTML still references them -- browser loads no CSS
- Symptom: all masthead symbols appear black (#111827) instead of gold (#D4AF37)
- Fix: `sed -i '' 's/styles\.[a-f0-9]*\.css/styles.css/g' public/*.html`

### Verification When browser_vision Fails
- Use `browser_console` + `getComputedStyle` for color verification
- Check: computed color (`rgb(212, 175, 55)` = gold), class presence, font family, dimensions
- Verify CSS actually loaded: `document.querySelector('link[rel="stylesheet"]')?.href`
