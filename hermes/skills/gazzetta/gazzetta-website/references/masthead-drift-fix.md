# Masthead Symbol Drift — Detection & Fix (v26.2)

## Problem

The caduceus (☤) is present on `index.html` but COMPLETELY ABSENT from ALL 7 sub-pages:
`/stories`, `/flows`, `/trades`, `/signal`, `/track`, `/flow-nodes`, `/event_horizon`.

Bulavas (⚔) appear on the LEFT side instead of RIGHT on sub-pages.

**Root cause (v26.2 update):** `index.html` now uses `masthead-right` for INTEL/ALPHA/MENU nav links:
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

Sub-pages have a DIFFERENT masthead structure with product-specific nav:
```html
<div class="masthead-left">
  <a href="./">
    <span class="masthead-bulava">[SVGs]</span>  <!-- bulavas on LEFT — WRONG -->
    <span class="masthead-name">La Gazzetta di Kyiv</span>
  </a>
</div>
<div class="masthead-right">
  <nav class="product-nav">[links]</nav>
</div>
```

## Detection (before every deploy)

```bash
cd ~/projects/gazzetta-di-kyiv
# Must return ALL nav-linked pages:
grep -l 'masthead-caduceus' site/*.html
# Expected: index.html stories.html flows.html trades.html signal.html track.html event_horizon.html flow-nodes.html
```

## Fix (Python one-liner for all sub-pages)

```python
import re

caduceus_match = re.search(r'(<span class="masthead-caduceus".*?</span>)', 
                           open('site/index.html').read(), re.DOTALL)
caduceus = caduceus_match.group(1)

for page in ['stories.html', 'flows.html', 'trades.html', 'signal.html', 
             'track.html', 'event_horizon.html', 'flow-nodes.html']:
    with open(f'site/{page}') as f:
        html = f.read()
    if 'masthead-caduceus' in html:
        continue
    # Insert caduceus BEFORE the bulava span in masthead-left
    html = html.replace('<span class="masthead-bulava"', 
                        f'{caduceus}\n      <span class="masthead-bulava"', 1)
    with open(f'site/{page}', 'w') as f:
        f.write(html)
```

## Post-fix verification

```bash
# Count caduceus across all pages:
for f in site/*.html; do echo "$f: $(grep -c 'masthead-caduceus' $f)"; done
# Every nav-linked page should show "1"
```

## Design Contract (NON-NEGOTIABLE)

- **Caduceus**: LEFT side only (`.masthead-left`). NEVER on the right.
- **Bulavas**: RIGHT side only (`.masthead-right`). NEVER on the left.
- **Both symbols**: Static HTML, not JS-injected. Must survive cold-load, warm-navigation, and all sub-pages.
- **Gold 2px border-bottom** below masthead: `border-bottom: 2px solid #D4AF37`
