# Context Memory — Persistent Cognitive Core

v28, June 2026. The C-Suite identified that cloud agents suffer from operational amnesia:
they report "All Systems Operational" based on build exit codes while the live UX is broken,
buttons fail, and Telegram publishes stale stories. A server running bad design perfectly is
a total system failure.

## Solution: `context_memory.json`

A single JSON file at `public/data/context_memory.json` (pipeline artifact) and `data/context_memory.json`
(source copy). All cloud agents read this file at runtime — it acts as a "Chief of Staff" ensuring
no agent executes an action that violates the owner's standards.

### Schema

```json
{
  "_meta": { "version": "1.0.0", "generated_by": "hermes-agent" },
  "owner_directives": ["...", "..."],
  "never_again_list": ["Never report success based on local compilation if CDN caching blocks live view", "..."],
  "design_tokens": {
    "masthead": { "color": "rgb(17, 24, 39)", "borderBottom": "2px solid rgb(212, 175, 55)", ... },
    "cards": { "background": "rgb(255, 255, 255)", "borderLeft": "2px solid rgb(212, 175, 55)", "minCount": 30 },
    "nav": { "backgroundColor_contains": "26, 31, 46", "linkCount": 7 },
    "wcag": { "body_font_min": 16, "meta_font_min": 12, "touch_target_min": 44 },
    "body_font": "Source Serif 4",
    "container_count": 5
  },
  "voice_register": { "tone": "Clinical contrarian", "telegram_format": { ... } }
}
```

CRITICAL: `design_tokens` must mirror the structured layout of `DESIGN_TOKENS` in `cdo_audit.py`.
The merge function (`merge_design_tokens()`) expects sub-dicts `masthead`, `cards`, `nav`, `wcag`
and scalar keys `body_font`, `container_count`. If the JSON uses flat keys (e.g. `"background": "#FFFFFF"`)
the merge silently does nothing — it's a no-op, not an error. See pitfall below.

### Consumers

| Script | How it reads | What it uses |
|--------|-------------|--------------|
| `cdo_audit.py` | `load_context_memory()` → `merge_design_tokens(DESIGN_TOKENS, ctx)` | Design tokens override hardcoded defaults |
| `memory_synthesizer.py` | TBD — reads for synthesis | Owner directives, never-again list |
| Pipeline agents | Via `public/data/context_memory.json` | Full cognitive core |

### Loading Pattern (cdo_audit.py)

```python
def load_context_memory() -> dict:
    # Try local file first (Cloud Run pipeline artifact)
    local_path = Path(__file__).resolve().parent.parent / "public" / "data" / "context_memory.json"
    if local_path.exists():
        with open(local_path) as f:
            return json.load(f)
    # Fallback: fetch from live site
    try:
        with urllib.request.urlopen(f"{SITE_URL}/data/context_memory.json", timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        pass
    return {}
```

### Pitfall: Schema Drift Causes Silent No-Op

The `merge_design_tokens()` function looks for structured sub-dicts:

```python
for key in ("masthead", "cards", "nav", "wcag"):
    if key in dt:
        merged[key] = dt[key]
```

If `context_memory.json`'s `design_tokens` uses flat keys (`background`, `gold_primary`, `ink`, ...)
instead of structured sub-dicts, NONE of these for-loop checks match. `merge_design_tokens()` returns
the unchanged hardcoded `DESIGN_TOKENS`. The audit report shows `context_memory_loaded: true` but
zero tokens are overridden — a silent false positive.

**Detection:** After updating context_memory.json, run:
```python
tokens = merge_design_tokens(DESIGN_TOKENS, load_context_memory())
assert tokens["masthead"]["color"] == "rgb(17, 24, 39)", "Schema drift — tokens NOT merged"
```

**Fix:** Restructure JSON's `design_tokens` to mirror `DESIGN_TOKENS` structure exactly.

### Deployment

`public/data/` is gitignored (pipeline artifact per R4). The source copy at `data/context_memory.json`
IS committed. `build_site.py` syncs `data/` → `public/data/` during Stage 1. Both Cloud Run pipeline
image and agents image need this file present at build time (it's copied via `COPY public/ /app/public/`).
