# CSS Orphaned Brace — Media Query Leak Detection

## The Problem

An extra `}` anywhere in the CSS closes a parent `@media` block prematurely. All rules that were scoped inside that `@media` now apply GLOBALLY — overriding desktop styles that were supposed to take precedence.

## Symptoms

- A CSS property set in the main stylesheet (e.g., `font-size: 3em`) shows up as a smaller value in the browser (e.g., `16px`)
- The CSSOM reports the overriding rule as `media: "none"` — it's NOT inside any media query
- `curl` shows the rule in the CSS but it's outside any `@media { ... }` block
- The override appears later in the file (later rules win in cascade)

## Detection — Python Brace Counter

```python
with open('styles.css') as f:
    lines = f.readlines()
depth = 0
for i, line in enumerate(lines, 1):
    depth += line.count('{') - line.count('}')
    if depth < 0:
        print(f'Orphaned }} at line {i}: depth={depth}')
        print(f'  Line: {line.rstrip()[:120]}')
        break
```

If `depth < 0` anywhere — there's an orphaned `}`.

## Finding What Broke

Check the enclosing block around reported orphaned braces:

```python
depth = 0
media_stack = []
for i, line in enumerate(lines, 1):
    if '@media' in line and '{' in line:
        media_stack.append((i, line.strip()))
    depth += line.count('{') - line.count('}')
    if i == target_line:
        print(f'At line {i}: depth={depth}, media_stack={[m[1][:50] for m in media_stack]}')
```

## Fix

Remove the orphaned `}`. Then re-check that all `@media` blocks close properly:

```python
for i, line in enumerate(lines, 1):
    if '@media' in line and '{' in line:
        # Track this media block
        ...
    if line.strip() == '}' and media_depth == 0:
        # This closes the media
```

## Pitfall: Cumulative Damage

A single orphaned `}` can cascade: removing it may expose the NEXT orphaned `}` (because the first one was prematurely closing a block that had a legitimate `}` later, and now that legitimate `}` becomes an extra one). After fixing one orphan, re-run the brace counter to find the next.

## Session Incidents

- **June 11, 2026**: `styles.css` line 270 — orphaned `}` after `.hero { }` block. This closed `@media (max-width: 768px)` at line 578 prematurely. All rules from line 271-621 leaked into global scope. The `.masthead-name { font-size: 16px; }` at line 898 (which was also outside any media query due to the leak) overrode the intended `3em`. Two fixes needed: (1) remove orphaned `}` at line 270, (2) change `16px` → `3em` at line 898 (which was itself a duplicate override from a poorly-scoped original rule).
