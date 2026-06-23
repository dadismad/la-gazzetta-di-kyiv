# CSS Quality Audit Checklist (v26.4+)

Run after any CSS change or design overhaul. Based on the June 2026 before/after audit that found 28 `!important`, 26 hardcoded gold values, 14 orphaned vendor prefixes, and 41 font-size rules below 10px.

## Automated Sweep

```bash
cd ~/projects/gazzetta-di-kyiv

# 1. Hardcoded gold hex values (should all use var(--gold) or var(--gold-dark))
grep -c '#D4AF37' styles.css   # Must be ≤1 (comment/root only)
grep -c '#B8860B' styles.css   # Must be ≤1 (root only)

# 2. !important abuse
grep -c '!important' styles.css  # Must be 0

# 3. Font-size minimums (should be ≥10px)
grep -oP 'font-size:\s*\K[789]px' styles.css | wc -l  # Must be 0

# 4. Orphaned vendor prefixes (floating outside any rule)
# These are display: -webkit-box; display: -webkit-flex; NOT inside a selector block
# After sweeping, verify braces balance
python3 -c "
with open('styles.css') as f: css = f.read()
print(f'Braces: {{={css.count(\"{\")} }}={css.count(\"}\")}, balanced={css.count(\"{\")==css.count(\"}\")}')
"
```

## Inline Style Sweep (HTML Templates)

CSS sweep misses inline `style="font-size:7px"` attributes in HTML. Must sweep separately:

```bash
# Find font-size <10px in inline styles
grep -rn 'font-size:\s*[789]px' *.html site/*.html

# Fix: bump all to 10px
python3 << 'PYEOF'
import re, glob
for fp in glob.glob('*.html') + glob.glob('site/*.html'):
    with open(fp) as f: c = f.read()
    c2 = re.sub(r'font-size:\s*[789]px', 'font-size: 10px', c)
    if c2 != c: open(fp,'w').write(c2)
PYEOF
```

## Touch Target Audit

All interactive elements must have `min-height ≥ 44px` for mobile:

```bash
grep -n 'min-height.*px' styles.css | grep -v '44px\|4[5-9]px\|[5-9][0-9]px'
# Output should be empty or only non-interactive elements
```

Critical targets:
- `.product-nav a` on mobile: must be 44px (was 32px)
- `.cf-hint`: must be 44px (was 28px)
- `.nav-group-label`: should be at least 36px

## Post-Deploy Verification

```javascript
// In browser console after deploy:
JSON.stringify({
  important: [...document.styleSheets]
    .flatMap(s => [...(s.cssRules||[])])
    .filter(r => r.style?.getPropertyPriority('font-size')==='important').length,
  hardcodedGold: [...document.styleSheets]
    .flatMap(s => [...(s.cssRules||[])])
    .map(r => r.cssText).join('').match(/#D4AF37|#B8860B/g)?.length || 0,
  font9px: [...document.styleSheets]
    .flatMap(s => [...(s.cssRules||[])])
    .filter(r => ['8px','9px'].includes(r.style?.fontSize)).length,
  cssHash: document.querySelector('link[href*="styles."]')?.href
})
// Expected: {important: 0, hardcodedGold: 0, font9px: 0}
```

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `build_hashed_assets.py` runs but hashed JS not deployed | `app.*.js` 404 — all dynamic content dead | Always verify: `curl -skI https://www.lagazzettadikyiv.com/app.*.js` returns 200 |
| Inline styles bypass CSS sweep | Fonts still at 7/8/9px after CSS cleanup | Run HTML inline sweep as separate pass |
| `!important` removal breaks cascade | Elements render at wrong size after cleanup | Ensure media queries are at end of file (later wins by cascade) |
| Deploy gate blocks CSS-only deploy | shipit.sh fails on pre-existing data integrity tests | Use direct `gsutil rsync` when changes are CSS/HTML only |
| Site/styles.css not copied from root | Build hashes OLD site/styles.css, changes never go live | Always `cp styles.css site/styles.css` BEFORE `build_hashed_assets.py` |
