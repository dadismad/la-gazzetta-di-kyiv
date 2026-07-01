# Sprint 7-8: CCO/CDO Deployment Pitfalls & Patterns

Captured during the Executive Board Expansion (Architect V2 Sprints 7 & 8), June 2026.

## CRITICAL: Qualitative Confidence Data Schema

**Problem:** The `stories.json` field `confidence` contains string values `"low"`, `"medium"`, `"high"`, `"medium_low"`, `"very_low"` — NOT numeric percentages. The field `confidence_pct` is `None` for all 245 stories. Any curation/filtering logic that expects a numeric confidence value will silently produce 0.

**Detection:**
```bash
gsutil cat gs://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
s = data['stories'][0]
print(f'confidence: {s.get(\"confidence\")}  (type: {type(s.get(\"confidence\")).__name__})')
print(f'confidence_pct: {s.get(\"confidence_pct\")}')
"
# Output: confidence: low  (type: str)
#         confidence_pct: None
```

**Fix — qualitative-to-numeric mapping:**
```python
QUALITATIVE_MAP = {
    "high": 85, "medium_high": 75, "medium": 65,
    "medium_low": 50, "low": 35, "very_low": 15, "none": 5,
}

cp = story.get("confidence", 0)
if isinstance(cp, str):
    cp = QUALITATIVE_MAP.get(cp.lower(), 50)  # default 50 if unparseable
```

**Contradiction score normalization:** The `contradiction_score` field uses a 0-100 integer scale, not 0-1 float. Divide by 100 before use:
```python
cs = story.get("contradiction_score", 0)
if cs > 1:
    cs = cs / 100.0
```

**Curation impact formula:**
```python
impact = (contradiction_score / 100) * (confidence_numeric / 100)
# Example: cs=75, confidence="low" -> 0.75 * 0.35 = 0.2625
```

---

## Telegram Bot API: HTTP 400 on Markdown parse_mode

**Problem:** Headlines contain unescaped Markdown control characters (`+`, `%`, `$`, `_`, `*`, `[`, `]`). Telegram's Markdown parser rejects the entire message with HTTP 400 `Bad Request`.

**Example headline that breaks Markdown:**
```
"US Existing Home Sales Crush Estimates: +3.2% MoM vs 1.1% Expected"
```

**Fix — switch to HTML parse_mode with entity escaping:**
```python
# Escape for HTML
escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# Use HTML tags instead of Markdown
body = {
    "chat_id": CHAT_ID,
    "text": escaped,
    "parse_mode": "HTML",  # NOT "Markdown"
}
```

Format headlines with `<b>` tags instead of `**`.

**Note:** `parse_mode=None` (plain text) also works but loses bold formatting on headlines.

---

## gcloud `--set-secrets` Strips `:latest` Suffix

**Problem:** The tool layer redacts `:latest` from gcloud commands containing `--set-secrets=ENV=secret:latest`, causing:
```
ERROR: No secret version specified for TELEGRAM_BOT_TOKEN.
Use TELEGRAM_BOT_TOKEN:latest to reference the latest version.
```

The secret mount is silently dropped — job has 0 secrets after update. Detection: `gcloud run jobs describe JOB --format=yaml` should show `env:` with `valueFrom.secretKeyRef` entries.

**Workaround — YAML-based job replace:**

1. Export current job config:
```bash
gcloud run jobs describe JOB_NAME --region=REGION --project=PROJECT --format=yaml > job.yaml
```

2. Edit `job.yaml` to add the secret mount under `containers[0].env`:
```yaml
- name: TELEGRAM_BOT_TOKEN
  valueFrom:
    secretKeyRef:
      name: telegram-bot-token
      key: latest
```

3. Apply:
```bash
gcloud run jobs replace job.yaml --region=REGION --project=PROJECT
```

**An alternative** that sometimes works: read the secret name from `gcloud secrets list --format='value(name)'`, construct the ref with a shell variable, and pass it — but the tool layer may still redact depending on the exact syntax.

---

## `gcloud builds submit` Does Not Accept `-f` Flag

**Problem:** `gcloud builds submit --tag IMAGE -f Dockerfile.agents .` fails with:
```
ERROR: unrecognized arguments: -f .
```

**Workaround — subdirectory pattern:**

```bash
mkdir -p build_dir
cp Dockerfile.agents build_dir/Dockerfile
cp scripts/*.py build_dir/
gcloud builds submit --tag IMAGE build_dir/
```

The `build_dir/` becomes the source context, and its `Dockerfile` (standard name) is used.

---

## Dockerfile.agents: Playwright + Chromium for CDO

**Image:** `gazzetta-agents:latest` (separate from `gazzetta-pipeline:latest`)

**System deps required for headless Chromium:**
```
libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0
libcups2 libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1
libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0
libcairo2 libasound2
```

**Python deps:** `google-cloud-storage google-cloud-secret-manager playwright`

**Post-install:** `playwright install chromium && playwright install-deps chromium`

**Build time:** ~2-3 minutes (175 MiB Chromium download + system deps)

**Image size:** ~800 MB (vs ~200 MB for pipeline image)

---

## Python `import subprocess` Shadowing in Conditional Blocks

**Problem:** A redundant `import subprocess` inside an `if exit_code == 0:` block creates a local binding that shadows the top-level `import subprocess`. When the `if` block is skipped (e.g., pipeline failure path), `subprocess` is unbound in subsequent code paths that use it:
```
WARNING: auto_revert.py failed: cannot access local variable 'subprocess'
where it is not associated with a value
```

**Fix:** Remove redundant imports inside conditional blocks. Use the top-level import.

**Pattern to avoid:**
```python
import subprocess  # top-level

def main():
    if success:
        import subprocess  # BAD: shadows top-level import
        subprocess.run(...)
    else:
        subprocess.run(...)  # FAILS: local 'subprocess' unbound
```

---

## CCO Platform Thresholds (as deployed)

| Platform | Top N | Min Impact Score | Max Age | Status |
|----------|-------|-----------------|---------|--------|
| Telegram | 3 | 0.15 | 24h | LIVE |
| Reddit | 1 | 0.25 | 24h | DRAFT MODE |
| X.com | 3 | 0.10 | 12h | DRAFT MODE |
| Newsletter | 5 | 0.10 | 24h | DRAFT MODE |

Impact score = (contradiction_score / 100) * (confidence_numeric / 100)

---

## CDO Audit Dimensions

| Dimension | Method | Breakpoints |
|-----------|--------|-------------|
| Masthead color | getComputedStyle('.masthead').color | All 3 |
| Masthead font | getComputedStyle('.masthead').fontFamily | All 3 |
| Card background | getComputedStyle('.card').background | All 3 |
| Card count | document.querySelectorAll('.card').length | All 3 |
| Nav background | getComputedStyle('nav').backgroundColor | All 3 |
| Horizontal overflow | scrollWidth > innerWidth | Mobile only |
| JS errors | Console error listener | All 3 |

**Breakpoints:** desktop (1280x900), tablet (768x1024), mobile (400x800)

**Screenshots:** Taken but NOT used for color verification (vision hallucination pitfall). getComputedStyle() is primary.

---

## Required Secret Manager Keys for Sprint 9

| Secret Name | Platform | Purpose |
|-------------|----------|---------|
| `reddit-client-id` | Reddit | OAuth client ID (reddit.com/prefs/apps) |
| `reddit-client-secret` | Reddit | OAuth client secret |
| `reddit-username` | Reddit | Bot account username |
| `reddit-password` | Reddit | Bot account password |
| `newsletter-api-key` | Newsletter | SendGrid or Mailchimp API key |

X.com requires a $5 credit purchase at developer.x.com, not a secret.
