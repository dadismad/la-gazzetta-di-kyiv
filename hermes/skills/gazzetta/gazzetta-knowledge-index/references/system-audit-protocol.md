# Gazzetta di Kyiv — System Diagnostic Audit Protocol

Three-part diagnostic framework for comprehensive system health checks. Use when the user requests a full audit, or when something "looks broken" and you need to systematically trace the fault.

## ⛔ FIRST DIRECTIVE: Hard Diagnostics Only

**Never deliver blanket "success" or "everything works" summaries.** These are the enemy of trust. Every audit output must include **live-measured, reproducible data points**:

- Byte counts (body size, file sizes, local vs GCS comparison)
- Card counts (`document.querySelectorAll('.card').length`)
- Console errors (exact count, not "none found" without checking)
- Computed styles (`getComputedStyle(el).borderLeftWidth` — not source grep)
- Data array lengths (`STORIES_DATA.length`, not "data seems present")
- Timestamps (generated_at, last deploy, cache age)
- URL paths and fetch targets (exact strings, not "it fetches data")

A verdict of "Pass" without at least 3 live-measured metrics backing it is a **false positive**. The user's directive: *"Stop reporting 'Success' blindly. I need a hardcore technical diagnostic."*

**The hierarchy of evidence (strongest to weakest):**

```
1. browser_console expression result     ← GOLD — exact number from live JS
2. browser_vision screenshot             ← Confirms visual rendering
3. gsutil stat output (byte comparison)  ← Confirms deployment sync
4. browser_snapshot (full=true)          ← Post-JS DOM structure
5. curl response                         ← Pre-JS static HTML (BLIND to JS content)
6. git log                               ← Source control (NOT deployed state)
```

**Evidence level 5 or 6 alone CANNOT support a verdict.** If all you have is curl and git log, you haven't audited — you've guessed.

## Part 1: Data Pipeline Audit ("Why is it empty?")

### 1A. Trace the JSON
```bash
python3 -c "import json; d=json.load(open('site/data/stories.json')); s=d.get('stories',d); print(f'stories: {len(s) if isinstance(s,list) else len(s)}'); print('keys:', list(d.keys())[:15])"
python3 -c "import json; d=json.load(open('site/data/flows.json')); f=d.get('flows',d); print(f'flows: {len(f) if isinstance(f,list) else len(f)}'); print('keys:', list(d.keys())[:15])"
```
Expected: 200+ stories, 180+ flows. If 0 or keys don't include `stories`/`flows`, pipeline failed.

### 1B. Verify the Fetch Mechanism
```bash
grep -n "fetch\|getJSON" site/app.js | head -15
```
Confirm: `fetch()` with timestamp cache-busting (`?t=${Date.now()}`), AbortController for stale-request cancellation, 2-level retry with exponential backoff. If `fetch` is missing — the site may be serving static/hardcoded HTML.

### 1C. Diagnose DOM Injection
Check if the target DOM element exists:
```bash
grep -n "newsCol\|storiesCol\|storiesLoading\|storiesTeaser" site/index.html
```
Then verify in live browser:
```javascript
// In browser_console:
document.getElementById('newsCol') // null on index.html = expected, exists on stories.html
document.querySelectorAll('.card[data-story-id]').length // expected: 20 on index, 245+ on stories
```

**Key pitfall**: `newsCol` only exists on `stories.html`, not `index.html`. app.js uses `byId()` which safely returns null — no errors. The homepage uses `populateTeasers()` with `.slice(0, 20)` instead.

## Part 2: Code & Rendering Audit ("Visual Lens")

### 2A. CSS Display Audit
```bash
grep -n "display.*none\|visibility.*hidden" site/styles.css
```
Verify each rule is intentional (nav dropdowns, collapsed containers, mobile simplifications). Nothing should hide main content containers accidentally.

### 2B. GitHub Version Check
```bash
git log --oneline -5
```
Compare against remote:
```bash
curl -s "https://api.github.com/repos/pureciclismo/gazzetta-di-kyiv/commits/main?per_page=3" | python3 -c "import sys,json; data=json.load(sys.stdin); ..."
```

### 2C. Console Audit (Live Browser)
Navigate to live site, then:
```javascript
// browser_console with no expression = reads all console messages
```
Also verify:
```javascript
typeof window.Gazzetta  // should be "object"
typeof window.i18n      // should be "object"
window.STORIES_DATA?.length  // should be 200+
```

## Part 3: Deployment & Pipeline Audit

### 3A. GCS Sync Proof
```bash
gsutil ls -l "gs://www.lagazzettadikyiv.com/"
gsutil ls -l "gs://www.lagazzettadikyiv.com/data/"
```
Compare last-modified timestamps against local files. Check hashed asset variants (`.d0b7cbda.css`, `.13a04b5f.js`) exist on GCS.

### 3B. Orphaned Files
```bash
# List ALL GCS files
gsutil ls "gs://www.lagazzettadikyiv.com/**"
# Compare against local site/
ls -la site/ site/data/
```
Any file on GCS NOT in local `site/` is potentially orphaned. Known orphans:
- `api/v1/*` — pipeline-generated API endpoints (intentional, not in git)
- `data/en/` — post-RU scorched-earth vestige (should be removed)
- `dashboard/` — experimental, may exist

## Report Output Format

Every audit row MUST include at least one live-measured data point in the "Critical Error Found" or supporting text. No row may say "None" without citing a measurement.

```markdown
| Module | Audit Result | Live Data | Critical Error Found | Required Fix |
| :--- | :--- | :--- | :--- | :--- |
| Data Fetching | Pass | fetch() line 78, 246 STORIES_DATA, getDataPath='./data/stories.json' | None — verified via browser_console | None |
| Rendering | Pass | 246 cards, body=2.2MB, computed borderLeft='3px solid gold' | None — verified via getComputedStyle() | None |
| Deployment | Pass | stories.json: local=2,044,228 = GCS=2,044,228 bytes | None — verified via gsutil stat | None |
```

If you cannot fill the "Live Data" column, you have not verified — you are guessing. Return to the browser or gsutil and measure.

## Verification Golden Rule

> **If you can't see it in a browser_vision screenshot or browser_console expression, it's NOT confirmed.**

Never claim "broken" from:
- `curl` output (shows `—` placeholders pre-JS)
- `browser_snapshot` in compact mode (shows 17 elements for 2MB body)
- `git log` (source control ≠ deployed state)

Always verify with: browser_console expression OR browser_vision screenshot + 4s async wait.
