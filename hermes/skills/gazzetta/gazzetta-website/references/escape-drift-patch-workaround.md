# Escape-Drift Patch Workaround

## Problem

The `patch` tool frequently fails on JavaScript files (especially `app.js`) with:
```
Escape-drift detected: old_string and new_string contain the literal sequence
'\\"' but the matched region of the file does not.
```

This is a tool-call serialization artifact — quotes get prefixed with spurious backslashes during transport.

## Solution

Use `execute_code` to call `hermes_tools.patch()` directly from Python. The strings pass through the Python runtime unchanged, bypassing the serialization issue:

```python
from hermes_tools import patch

old = """// exact text from the file (read it first with read_file)"""
new = """// replacement text"""

result = patch("/path/to/file.js", old, new)
print(f"Success: {result['success']}")
```

## When to use this

- Any time `patch()` fails with "Escape-drift"
- When modifying `app.js` (most common victim — template literals with `${}`)
- When modifying `build_frontend.py` or `build_frontend_staging.py` — these Python files embed JS template strings with `\"` escaping, which triggers the same serialization issue
- When the old_string contains `\"`, `'`, or backtick characters inside JS template literals

## Verification

After the patch:
```python
from hermes_tools import read_file
# Read a few lines around the patched area to verify
content = read_file("/path/to/file.js", offset=line_num, limit=10)
print(content['content'])
```

## Known-safe patterns

- `patch()` works fine on: CSS files, HTML files, YAML files, most Python files
- `execute_code` + `hermes_tools.patch()` is needed for: JS files with template literals, Python files with embedded JS strings (build_frontend*.py), files with heavy escaping
