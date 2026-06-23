# JavaScript Scope Fragility — story-app.js

## Current Architecture (v24.0 June 2026)

The CURRENT story-app.js uses **template literals** (backtick `${}` syntax), NOT string concatenation. The v22.x rewrite to `var`-only string concatenation was superseded by a cleaner template-literal version. This version has 280+ lines and runs inside a `(function() { 'use strict'; ... })()` IIFE.

## Critical Bugs Found in the Template-Literal Version (v24.0)

### 1. `renderIntelReport` → `buildHTML` reference bug
The namespace binding at the bottom of the file referenced a non-existent function:
```js
Gazzetta.Story.renderIntelReport = renderIntelReport; // ❌ undefined
```
The actual function is `buildHTML`. This caused the script to fail silently — `renderIntelReport` is `undefined` when assigned, and while the assignment itself doesn't throw, the script may fail later. Fix:
```js
Gazzetta.Story.renderIntelReport = buildHTML; // ✅ correct
```

### 2. `init()` missing `async` keyword
The init function uses `await` but was NOT declared `async`:
```js
function init() {           // ❌ not async
    await new Promise(...);  // Runtime error in strict mode
```
Browsers throw a runtime error in `'use strict'` IIFE contexts. Fix:
```js
async function init() { ... } // ✅
```

### 3. Multi-persona rendering didn't exist
All 8 stories had rich `multi_persona` data (c_suite, quant, degen keys) from the pipeline, but story-app.js had ZERO code to render these blocks. The data was generated but never displayed. The `buildHTML()` function needed a `${renderMultiPersona(story)}` call inserted between the extremum section and the share buttons, plus a `renderMultiPersona()` function that generates the 3-column persona grid HTML.

## Patch Corruption Patterns

### Line number embedding from read_file
When using `read_file()` output as input to `write_file()` or `patch()`, the Hermes `LINE_NUM|CONTENT` format gets written into the file as actual content. Every line starts with `    N|` where N is the line number.

**Detection:**
```bash
head -1 site/story-app.js | grep -qP '^\s+\d+\|' && echo "CORRUPTED"
```

**Fix:**
```python
import re
c = open('FILE').read()
open('FILE','w').write(re.sub(r'^ +\d+\|', '', c, flags=re.MULTILINE))
```

### Missing `</script>` closing tag
Patching the last line of a `<script>` block can remove the closing `</script>` tag. The browser then parses everything after as HTML, not JS — no console errors, no execution.

**Detection:**
```bash
for f in site/*.html; do
  opens=$(grep -c '<script' "$f")
  closes=$(grep -c '</script>' "$f")
  [ "$opens" != "$closes" ] && echo "FATAL: $f mismatched script tags"
done
```

### File truncation from bad patch match
When `patch()` old_string matches a generic pattern like `  }\n\n  function renderRelated(story) {`, it can match the WRONG occurrence or consume too much of the file. The first patch attempt in v24.0 truncated story-app.js from 314 → 228 lines because the match was ambiguous.

**Prevention:** Include 3+ lines of unique context in `old_string`. Verify line count after every patch: `wc -l FILE`.

## Recovery

The working backup is always on GCS:
```bash
curl -sk "https://www.lagazzettadikyiv.com/story-app.39bb2dd8.js" > site/story-app.js
```
The `39bb2dd8` hash is the last known-good version (v2.0 string concat, before template-literal rewrite). For the template-literal version, the latest deployed hash should be used.

## Related Files
- `site/story-app.js` — main file (~280 lines, template-literal version)
- `site/app.js` — homepage JS (hero indicators, flows, trade hooks)
- `site/styles.css` — has `.persona-*` CSS classes from v24.0
- `site/index.html` — homepage with hash-based routing script
- `site/story.html` — story detail shell (references hashed story-app.js)
