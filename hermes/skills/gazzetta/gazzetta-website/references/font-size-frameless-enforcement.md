# Font-Size Floor & Frameless Contract Enforcement

## Problem

CSS accumulates small font sizes (7.5px, 9px, 10px) and decorative styling
violations (border-radius, box-shadow) over time. Manual review misses them.
Need automated enforcement.

## Font-Size Floor

### Detection

```bash
grep -nE 'font-size:\s*(7|8|9|10)\.?[0-9]?px' styles.css
```

Or programmatically:

```python
import re
pattern = re.compile(r'font-size:\s*((?:[7-9]|10)(?:\.\d+)?)px(\s*!important)?')
```

### Enforcement — bump to 11px minimum

```python
def bump_font(m):
    val = float(m.group(1))
    if val < 11:
        imp = m.group(2) or ''
        return f'font-size: 11px{imp}'
    return m.group(0)

css = re.sub(
    r'font-size:\s*((?:[7-9]|10)(?:\.\d+)?)px(\s*!important)?',
    bump_font, css
)
```

**Result (June 2026):** 88 violations → 0. All sizes 7.5px–10px bumped to 11px.

### Important

- Preserve `!important` flags during replacement
- Functional 50% border-radius (circular elements, dots, avatars) are NOT violations
- The regex `(?:[7-9]|10)` targets only sub-11px sizes, leaves 11px+ untouched
- WCAG AA requires 12px for body text; 11px is floor for UI labels/badges

## Frameless Contract Enforcement

The frameless contract: no border-radius, no box-shadows on containers/cards.
Only 1px `var(--divider)` borders separate elements.

### Detection

```bash
grep -c 'border-radius' styles.css
grep -c 'box-shadow' styles.css
```

### Enforcement

```python
# Zero all border-radius except functional 50% (circles)
css = re.sub(r'border-radius:\s*\d+px', 'border-radius: 0', css)
css = re.sub(r'border-radius:\s*\d+\.?\d*rem', 'border-radius: 0', css)

# Remove box-shadows
css = re.sub(r'box-shadow:\s*[^;};]+;', 'box-shadow: none;', css)
```

**Result (June 2026):** 24 border-radius → 3 (functional 50% circles). 7 box-shadows → 0.

### Post-Enforcement Check

Only 3 remaining border-radius values, all `border-radius: 50%` — these are
circular elements (dots, status indicators, avatars), not decorative frame violations.

## Automated Audit

Add to `refresh_context.py` or `verify_reality.py`:

```python
# Font-size audit
import re
with open('site/styles.css') as f:
    css = f.read()
violations = len(re.findall(r'font-size:\s*([7-9]|10)(?:\.\d+)?px', css))
if violations:
    print(f"  ⚠ {violations} font-size violations < 11px")

# Frameless audit  
radius = len(re.findall(r'border-radius:\s*(?!0|50%)', css))
shadows = len(re.findall(r'box-shadow:\s*(?!none)', css))
if radius or shadows:
    print(f"  ⚠ Frameless violations: {radius} border-radius, {shadows} box-shadow")
```

## Session Reference

June 10, 2026: Applied both enforcements in single session. Font-size: 88→0.
Frameless: 24 border-radius + 7 box-shadows → 0 (3 functional circles retained).
