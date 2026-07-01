# Hashed CSS Self-Nuke — Root Cause & Fix

## The Bug
1. `build_hashed_assets.py` generates `styles.ab6de8dd.css`
2. HTML references `styles.ab6de8dd.css` in `<link>` tags
3. You update `styles.css` with design changes
4. `gsutil rsync -d` syncs `public/` to GCS
5. The `-d` flag DELETES old hashed files on GCS: `styles.ab6de8dd.css` is gone
6. But HTML still references `styles.ab6de8dd.css`
7. Browser loads ZERO CSS
8. Symbols appear black (browser default), fonts fall back to Times

## The Fix
Always reference `styles.css` (unhashed) in all HTML files and templates. Never use hashed CSS filenames.

```html
<!-- CORRECT -->
<link rel="stylesheet" href="./styles.css"/>

<!-- WRONG — will break on deploy -->
<link rel="stylesheet" href="./styles.ab6de8dd.css"/>
```

## The Template Fix
`templates/header.html` and `templates/footer.html` must reference `styles.css`. build_site.py injects these into every public page.

## Detection
```javascript
// Browser console: check if CSS loaded
getComputedStyle(document.querySelector('.masthead-machiavelli')).color
// Should return: rgb(212, 175, 55) = gold
// If returns rgb(17, 24, 39) = CSS didn't load
```
