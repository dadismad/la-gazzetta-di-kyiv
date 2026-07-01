# Batch HTML Processing Corruption — June 2026

## Root Cause

The `read_file()` tool returns content with line number prefixes in the format:
```
LINE_NUM|CONTENT
```

When this output is split by newlines, the line number prefixes become part of
the content. If the content is then written back to the file via `write_file()`,
the line numbers are permanently embedded in the HTML.

## How It Happened

During Phase 2 site-wide container unification (2026-06-12), a Python script
processed 19 HTML files to add sentinel markers:

```python
content = read_file(fpath)['content']   # Returns "   1|CONTENT\n   2|CONTENT..."
lines = content.split('\n')             # Splits into ["   1|CONTENT", "   2|CONTENT"...]
# ... modifications to lines ...
write_file(fpath, '\n'.join(lines))     # Writes line numbers back into file
```

Result: 15 HTML files corrupted with embedded line number prefixes on every line.
The file content went from:
```html
<!doctype html>
<html lang="en">
```
to:
```
     1|<!doctype html>
     2|<html lang="en">
```

## Secondary Corruption: Inline Script Tags Destroyed

The batch script also removed lines containing `<script` between the footer
and `</body>` tags. This was intended to clean up hashed script references
(`app.13a04b5f.js`) but also removed the OPENING `<script>` tags of inline
JavaScript blocks in 5 product pages (signal.html, flows.html, trades.html,
track.html, sources.html).

Result: Raw JavaScript code dumped as HTML text without `<script>` wrappers.
BeautifulSoup's `decompose()` couldn't find the script tags to remove, so
the test gate flagged "null" and "[]" as HTML content violations.

## Fix Pattern

### Line Number Stripping
```python
import re
with open(filepath, 'r') as f:
    lines = f.read().split('\n')
cleaned = []
for line in lines:
    # Strip leading spaces then the line number prefix: '   NNN|'
    match = re.match(r'^(\s*)(\d+)\|(.*)', line)
    if match:
        cleaned.append(match.group(1) + match.group(3))  # Keep indentation, drop number
    else:
        cleaned.append(line)
with open(filepath, 'w') as f:
    f.write('\n'.join(cleaned))
```

### Script Tag Restoration
For files that lost inline `<script>` blocks, restore from git:
```bash
git show HEAD~2:public/FILE.html > /tmp/FILE_original.html
# Then re-apply only the header/footer sentinel markers
# Do NOT process the script tag area
```

### Prevention
- NEVER use `read_file()` output as the source for `write_file()` without
  stripping line number prefixes. Use `open(path).read()` in execute_code
  scripts instead.
- When batch-processing HTML files, identify `<script>` tag boundaries and
  preserve them intact.
- Always `tail -6` after batch-processing standalone pages — if the file
  doesn't end with `</html>`, assume corruption.
