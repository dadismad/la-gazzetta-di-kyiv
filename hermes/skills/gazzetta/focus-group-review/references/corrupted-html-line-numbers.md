# Corrupted HTML Line Numbers — Detection & Recovery (v24.0)

## Symptom

Three HTML files (`story.html`, `event_horizon.html`, `flow-nodes.html`) had line number
prefixes embedded in every line of the source:

```
     1|<!doctype html>
     2|<html lang="en">
     3|<head>
```

Every line starts with `    N|` (spaces + line number + pipe). The browser renders the `N|`
prefixes as visible text nodes in the DOM, producing:

- **story.html**: "53|" appears as static text on the page. Story loading breaks because
  the corrupt text nodes interfere with JS template literal DOM insertion.
- **event_horizon.html**: "773| 775| 776|…" renders as visible grid numbers above
  "Loading event horizon data…"
- **flow-nodes.html**: "460| 461| 462|" renders alongside "Keys: 1-6 filter · Esc close"

## Detection

```bash
# Check if first line has line number prefix
head -1 site/story.html | grep -qP '^\s+\d+\|' && echo "CORRUPTED" || echo "CLEAN"

# Python alternative
python3 -c "
with open('site/story.html','rb') as f:
    first = f.read(30).decode()
if '|' in first.split('\n')[0]:
    print('CORRUPTED')
"
```

## Fix

```python
import re

with open('path/to/file.html', 'r') as f:
    content = f.read()

# Strip line number prefixes: "    N|content" → "content"
cleaned = re.sub(r'^ +\d+\|', '', content, flags=re.MULTILINE)

with open('path/to/file.html', 'w') as f:
    f.write(cleaned)
```

## Root Cause

Not definitively traced. Likely a build script or manual edit that used `cat -n` or
`nl` and saved output back to the source files. The corruption affects only 3 files:
`story.html`, `event_horizon.html`, `flow-nodes.html` — the pages with the most
complex inline JS. The other 16 HTML files were clean.

## Prevention

Add to shipit.sh Stage 2 (build_site):
```bash
# Prevent line-number corruption in HTML files
for f in site/*.html; do
  if head -1 "$f" | grep -qP '^\s+\d+\|'; then
    echo "FATAL: $f has line number prefixes — refusing to deploy"
    exit 1
  fi
done
```

## Pages verified clean (June 2026, post-fix)

`story.html`, `event_horizon.html`, `flow-nodes.html` — all 3 cleaned and verified.
