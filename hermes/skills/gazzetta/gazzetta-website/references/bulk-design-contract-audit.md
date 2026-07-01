# Bulk Design Contract Audit & Fix

Reusable pattern for scanning the entire codebase for design rule violations and fixing them programmatically. Used for font-size floor enforcement, frameless contract restoration, and color palette audits.

## Pattern

```
1. SCAN → execute_code with Python regex to find all violations
2. CATEGORIZE → functional (circles, avatars) vs decorative (card corners)
3. FIX → regex substitution on the full file
4. HANDLE EDGE CASES → !important, media queries, nested rules
5. VERIFY → browser_navigate + browser_console for runtime confirmation
```

## Example: Font-size Floor (2026-06-10)

```python
import re

with open('site/styles.css', 'r') as f:
    css = f.read()

def bump_font(m):
    val = float(m.group(1))
    if val < 11:
        imp = m.group(2) or ''
        return f'font-size: 11px{imp}'
    return m.group(0)

css = re.sub(r'font-size:\s*((?:[7-9]|10)(?:\.\d+)?)px(\s*!important)?', bump_font, css)

# Verify zero remaining
remaining = re.findall(r'font-size:\s*((?:[7-9]|10)(?:\.\d+)?)px', css)
assert len(remaining) == 0, f"{len(remaining)} violations remain"
```

## Example: Frameless Contract (2026-06-10)

```python
# Zero out border-radius
css = re.sub(r'border-radius:\s*\d+px', 'border-radius: 0', css)
css = re.sub(r'border-radius:\s*\d+\.?\d*rem', 'border-radius: 0', css)

# Remove box-shadows
css = re.sub(r'box-shadow:\s*[^;};]+;', 'box-shadow: none;', css)

# Functional exceptions: border-radius: 50% for circles — leave these
```

## Pitfalls

- **Don't remove functional border-radius**: `border-radius: 50%` makes circles (status dots, avatars). Leave these.
- **Don't trust grep counts alone**: `grep -c` on regex can match false positives. Use Python for precise counting.
- **!important rules survive substitution**: The regex must capture `!important` and preserve it.
- **Browser verification is mandatory**: `node --check` and static analysis won't catch CSS rendering issues. Always verify with `browser_navigate` + `browser_console`.

## Common Audit Targets

| Rule | Regex Pattern | Expected Count |
|------|--------------|----------------|
| Font-size < 11px | `font-size:\s*(7\|8\|9\|10)(\.\d+)?px` | 0 |
| border-radius decorative | `border-radius:\s*\d+px` (not 50%) | 0 |
| box-shadow | `box-shadow:` | 0 |
| Colors outside palette | `#[0-9A-Fa-f]{6}` not in allowed set | 0 |
| Emoji in UI | `[\U0001F300-\U0001F9FF]` in HTML | 0 (use Lucide SVGs) |

## After Fixing

Always update `references/design-tokens.md` to reflect the new rules so future sessions know the current floor.
