# CSS Brace-Depth Debugging

When CSS rules aren't taking effect despite being present in the source file, orphaned braces may be leaking @media rules to global scope or prematurely closing parent blocks.

## Detection

```bash
python3 -c "
with open('styles.css') as f:
    lines = f.readlines()
depth = 0
for i, line in enumerate(lines, 1):
    depth += line.count('{') - line.count('}')
    if depth < 0:
        print(f'NEGATIVE depth at line {i}: {line.rstrip()[:100]}')
"
# MUST output nothing (or final depth=0)
# Any NEGATIVE output = orphaned closing brace
```

## Real Example (June 2026)

styles.css had `font-size: 3em` at line 76 but computed to `16px`. Root cause:

1. **Orphaned `}` at line 270** — prematurely closed `@media (max-width: 768px)` at line 578, leaking all subsequent media-query rules (lines 271-621) to global scope
2. **Duplicate `.masthead-name { font-size: 16px; }` at line 898** — originally inside a media query, now in global scope, overriding the `3em` at line 76
3. **Orphaned `}` at line 983** — another media query closed twice, making depth negative

Fix: remove orphaned braces. Verify: `depth` never goes negative, final depth = 0.

## Browser Verification

Even after fixing source CSS, verify the browser loads the updated file:

```js
JSON.stringify({
  cssRule: [...document.styleSheets].flatMap(s => {
    try { return [...(s.cssRules||[])].filter(r => r.selectorText === '.masthead-name').map(r => ({fontSize: r.style.fontSize, sheet: s.href})) }
    catch(e) { return [] }
  })
})
// If font-size shows var(--φ-lg) but source has 3em → GCS cache still serving old CSS
// Fix: gsutil rm + sleep 1 + gsutil cp (not cp alone — LB caches even with no-store header)
```
