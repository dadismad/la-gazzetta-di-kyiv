# Gazzetta Website Design — v26.1 Update (June 2026)

## Color Palette Changes

| Element | v25.x (old) | v26.1 (new) | Reason |
|---------|------------|------------|--------|
| INTEL accent | #3B82F6 blue | **#0F172A black** | User: "black looks better" |
| INTEL label bg | #1E293B slate | **#0F172A black** | Matches accent |
| ALPHA accent | #D4AF37 gold | #D4AF37 gold | Unchanged |
| Nav buttons bg | transparent | **#FFFFFF white** | User: "make them white not black" |
| Nav buttons border | none | **1px solid #D4AF37 gold** | Gold lining |
| Nav buttons text | var(--gold) | **#0F172A dark** | Readable on white |
| Nav buttons hover | white text | **gold bg + dark text** | Clear interaction |
| Masthead border-bottom | 1px var(--divider) | **2px solid #D4AF37** | Golden lining |
| Master-nav border-bottom | 1px rgba(212,175,55,0.3) | **2px solid #D4AF37** | Golden lining |
| Story cards left border | none (except lead) | **2px solid #D4AF37** | Golden lining on ALL cards |

## CSS Reference

```css
/* Nav buttons — white bg + gold border */
.nav-dropdown-trigger {
  background: #FFFFFF;
  border: 1px solid #D4AF37;
  color: #0F172A;
  border-radius: 4px;
}
.nav-dropdown-trigger:hover {
  background: #D4AF37;
  color: #0F172A;
}

/* Masthead — 2px gold */
.masthead { border-bottom: 2px solid #D4AF37; }

/* Master nav — 2px gold */
.master-nav { border-bottom: 2px solid #D4AF37; }

/* Story cards — gold left edge */
article.card { border-left: 2px solid #D4AF37; }

/* INTEL header — black */
.intel-header .layer-label { background: #0F172A; }
.intel-header { border-left: 3px solid #0F172A; }
.intel-accent { color: #0F172A; border-left-color: #0F172A; }

/* Product page INTEL containers */
.product-page[data-layer="intel"] .container { border-left: 3px solid #0F172A; }
.product-page[data-layer="intel"] .container-subtitle { background: #0F172A; }
```

## Collapsible Containers

Desktop CSS rule required (was only in mobile media query):

```css
.container.collapsible .container-header { cursor: pointer; user-select: none; }
.container.collapsible.expanded .container-arrow { transform: rotate(180deg); }
.container.collapsible:not(.expanded) .container-body {
  max-height: 0 !important;
  overflow: hidden !important;
  opacity: 0;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
```

Flows + Trades containers should be `expanded` by default for better UX.

## CDN Cache Busting

After CSS changes, always bump the `?v=NN.NN` query string in ALL HTML files that reference CSS/JS. Without this, CDN edge cache serves stale CSS for up to 1 hour. Use `sed` to bump all references, then deploy both HTML and CSS.

```bash
for page in index.html stories.html flows.html ...; do
  sed -i '' 's/?v=25.XX/?v=26.1/g' "$page"
done
```

## Verification

After deploy, verify CSS applied via browser_console (not snapshot/curl):
```javascript
getComputedStyle(document.querySelector('.masthead')).borderBottomWidth  // must be "2px"
getComputedStyle(document.querySelector('.nav-dropdown-trigger')).backgroundColor  // must be "rgb(255, 255, 255)"
```
