# Patch Tool Bypass — Byte-Level Replacement

## When to Use

The `patch` tool (mode='replace') can fail with "escape-drift detected" when the target
text contains JavaScript-inside-Python string templates with heavy escaping (e.g.,
`<article class=\"py-stack-space...\">`). This happens because the tool's fuzzy matcher
cannot reconcile the escaped quote sequences in the patch with the actual file bytes.

**Symptom:**
```
Escape-drift detected: old_string and new_string contain the literal sequence
'\\\"' but the matched region of the file does not.
```

## The Fallback: execute_code + raw bytes

Use `execute_code` with `open(path, 'rb')`, operate on bytes, and `open(path, 'wb')`:

```python
with open("/path/to/file.py", "rb") as f:
    raw = f.read()

old = b'exact bytes from file'
new = b'replacement bytes'

count = raw.count(old)
print(f"Matches: {count}")

if count == 1:
    raw = raw.replace(old, new)
    with open("/path/to/file.py", "wb") as f:
        f.write(raw)
    print("OK")
elif count == 0:
    # Show the actual line for debugging
    for i, line in enumerate(raw.split(b'\n'), 1):
        if b'key substring' in line:
            print(f"L{i}: {line.decode().strip()[:150]}")
```

To find the exact bytes, print the file line with `repr()`:
```python
with open(path, "rb") as f:
    lines = f.read().split(b'\n')
print(repr(lines[616]))  # line N-1 (0-indexed)
```

## CRITICAL: read_file Corruption Pitfall

**DO NOT** use `read_file()` from `hermes_tools` inside `execute_code` to read a file,
then `write_file()` to write it back. `read_file()` returns content WITH LINE NUMBER
PREFIXES (e.g., `    42|actual content`), but `write_file()` writes the content as-is.
This embeds line numbers into the file, corrupting it.

**SAFE pattern:** Use standard Python `open()`:
```python
# SAFE:
with open(path) as f:
    content = f.read()
# ... modify ...
with open(path, "w") as f:
    f.write(content)
```

**Recovery from corruption:** If a file was corrupted with line numbers, check `git
checkout <file>` (if tracked) or copy from a known-good backup. In Gazzetta's case,
`build_frontend_staging.py` was recovered by copying from `build_frontend.py` (the
production version, which was identical at the time).
