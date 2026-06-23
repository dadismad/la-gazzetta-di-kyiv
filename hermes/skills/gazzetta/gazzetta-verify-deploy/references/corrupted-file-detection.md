# Corrupted File Detection — Line-Number Prefix Bug

## Symptom
A page silently fails — stuck on "Loading…" with no console error. The JavaScript file returns HTTP 200 and has the right Content-Type, but never executes. `window.storyApp` / `window.renderStory` is undefined despite the script tag being present.

## Root Cause
A file was corrupted with line-number prefixes embedded in every line:
```
     1|// story-app.js — Immersive single-story intel report page
     2|// v24.1: +multi-persona +async init fix
```
The `     1|` prefix at the start of line 1 parses as `1 | // comment` — a valid expression (`1`) followed by an incomplete bitwise OR. The JavaScript parser chokes silently. No syntax error appears in console because the parser treats it as a broken expression, not a syntax error.

## Detection
```bash
head -1 FILE | grep -q '^\s*[0-9]\+\|' && echo "CORRUPTED"
```
The corruption adds ~15% overhead (1,967 bytes stripped from 15,647 → 13,608).

## Fix
```python
import re
c = open('FILE').read()
open('FILE', 'w').write(re.sub(r'^ +\d+\|', '', c, flags=re.MULTILINE))
```

## Affected Files (June 2026)
- `story-app.js` — 15,647 bytes corrupted, deployed to GCS as `story-app.cc2e0196.js`
- Previously: `story.html`, `event_horizon.html`, `flow-nodes.html` (earlier incidents)

## How It Happens
A `read_file` + `patch`/`write_file` cycle can embed line-number prefixes if the read_file output (which includes `LINE_NUM|` format) is redirected back to the file. The corruption is self-perpetuating: each read_file → write cycle adds another layer.

## Prevention
After EVERY file edit, verify: `head -1 FILE` — the first line must start with actual content (comment, code, doctype), never a number-pipe prefix. The `gazzetta-verify-deploy` §0.4 check catches this before deploy.
