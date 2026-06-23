---
name: gazzetta-verify-deploy
description: Post-deploy verification — check live site against what was promised. Run after every deploy to catch discrepancies before the user does.
version: 2.4.0
author: Hermes Agent
---

# Post-Deploy Verification

Run after EVERY site change. Verify the live site reflects what was promised. Do not tell the user "done" until this passes.

## ⛔ ZERO: HARD DIAGNOSTICS ONLY (v26.11 — user directive)

The user's explicit command: *"Stop reporting 'Success' blindly. I need a hardcore technical diagnostic."*

Every verification output must include **live-measured, reproducible data points**:
- Byte counts (body size, file sizes, local vs GCS comparison)
- Card counts (`document.querySelectorAll('.card').length` — not "looks populated")
- Console errors (exact count from `browser_console()`, not "no errors found" without checking)
- Computed styles (`getComputedStyle(el).borderLeftWidth` — not source grep)
- Data array lengths (`window.STORIES_DATA?.length`, not "data loaded successfully")
- Timestamps (`generated_at`, cache `age:` header, deploy time)
- URL paths and fetch targets (exact strings, not "it fetches from the right place")

**A verdict without at least 3 live-measured metrics is a false positive.** If all you have is curl output and a snapshot, you haven't verified — you've guessed. Return to the browser or gsutil and measure.

## ⛔ FIRST: THE BLINDNESS RULES (v25.9 — mandatory before any claim)

These tools LIE about production state. Never make claims based on them:

| Tool | What it sees | What it MISSES | Why it lies |
|------|-------------|----------------|-------------|
| `curl` | Static HTML | All JS-rendered content | `—` placeholders are pre-JS; page works fine |
| `browser_snapshot` | Accessibility tree | JS-populated DOM, CSS, visual layout | Captures pre-JS state; `—` means JS hasn't run yet |
| `git log` | Source control | Whether GCS bucket was updated | Git push ≠ deploy; only `gsutil rsync` counts |
| `ls site/ru/` | Local filesystem | Whether GCS has the same files | Local `site/` ≠ GCS bucket |

**BEFORE reporting ANY bug:**
1. Wait 4+ seconds for JS async data to settle (`browser_console` → `window.STORIES_DATA?.length`)
2. Verify with `browser_vision` (actual screenshot) — NOT browser_snapshot alone
3. Compare GCS directly: `gsutil stat gs://www.lagazzettadikyiv.com/ru/stories.html`
4. If snapshot shows `—` but console shows populated values → **NOT A BUG, just pre-JS timing**

**THE GOLDEN RULE: If you can't see it in a browser screenshot, it's NOT confirmed. Curl, snapshot, and git are blind.**

## Verification Steps

### 0. Reversion Check (NEW — mandatory, 5 seconds)

Ghost cron jobs can silently overwrite yesterday's changes. Verify key visual elements survived:

```bash
# Font: must show Playfair
curl -sk https://www.lagazzettadikyiv.com/ | grep -o "Playfair\\|DM Serif" | head -1

# Emblem: must show caduceus, NOT fox
curl -sk https://www.lagazzettadikyiv.com/ | grep -o "masthead-[a-z]*" | sort -u

# Ghost: must not exist
ls ~/.hermes/hermes-agent/gazzetta-di-kyiv/ 2>&1 | head -1
```

If font shows "DM Serif" → ghost project reverted font. Re-apply Playfair Display.
If emblem shows "masthead-fox" → ghost project reverted emblem. Re-apply Caduceus.
If ghost path exists → delete immediately and fix cron jobs.
Full reversion recovery procedures: `references/reversion-check.md`
```bash
gsutil cp gs://www.lagazzettadikyiv.com/app.js - | grep -c "CHANGE_SIGNATURE"
```
- If the code change isn't on GCS → deploy failed
- If it's on GCS but not live → CDN cache (wait 5min)

### 0.1 GCS Old Asset Cleanup (v26.5 — mandatory after CSS/JS hash changes)

After deploying a new hashed CSS or JS file, delete OLD hashed files from GCS. Stale hashed files clutter the bucket, make verification harder, and can be served by cached HTML.

```bash
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
# List all hashed CSS — keep only the latest + styles.css + styles-modern*
$GSDK/gsutil ls gs://www.lagazzettadikyiv.com/styles.*.css
$GSDK/gsutil rm gs://www.lagazzettadikyiv.com/styles.OLDHASH.css ...
# Same for JS
$GSDK/gsutil ls gs://www.lagazzettadikyiv.com/app.*.js
# Delete locally too
cd site && rm -f styles.OLDHASH.css app.OLDHASH.js
```

### 0.2 GCS Auth (critical — wrong gsutil returns 401)

Use the **devvit SDK gsutil**, NOT the Hermes venv gsutil:
```bash
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
$GSDK/gsutil cp ...    # works — has boto config + credentials
$GSDK/gcloud compute ... # works
```

The Hermes venv gsutil (`~/.hermes/hermes-agent/venv/bin/gsutil`) has no boto config — reads succeed but writes fail with 401. Always use the devvit `GSDK` prefix for deploy operations.

### 0.25 CDN Cache Invalidation (v32.0+ June 2026 — MANDATORY after data deploys)

**The delete-reupload pattern (`gsutil rm` + `gsutil cp`) does NOT purge the CDN edge cache.** The CDN continues serving stale bytes until `max-age` expires, even when GCS has the new file. This is especially critical for data files (`stories.json`, `flows.json`) which have `max-age=3600` (1-hour stale window).

```bash
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin

# After EVERY deploy of non-hashed files, invalidate the CDN cache
$GSDK/gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path '/data/stories.json'
$GSDK/gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path '/index.html'
$GSDK/gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path '/'
```

Verify invalidation worked:
```bash
# GCS direct (bypasses CDN)
curl -sk "https://storage.googleapis.com/www.lagazzettadikyiv.com/data/stories.json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('total_stories'))"
# CDN via LB
curl -sk "https://www.lagazzettadikyiv.com/data/stories.json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('total_stories'))"
# Both must return the same count.
```

Full procedure: `references/cdn-cache-invalidation.md`

Deploy single files (not rsync for small changes):
```bash
$GSDK/gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/app.js gs://www.lagazzettadikyiv.com/app.js
$GSDK/gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/styles.css gs://www.lagazzettadikyiv.com/styles.css
$GSDK/gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/index.html gs://www.lagazzettadikyiv.com/index.html
$GSDK/gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/data/stories.json gs://www.lagazzettadikyiv.com/data/stories.json
```

### 2. Verify flows.json quality (CRITICAL — catches db_to_json.py regressions)

**⚠️ `db_to_json.py` is the AUTHORITATIVE flows.json source** — it reads directly from `gazzetta.db` (SQLite) and outputs 80+ flows. `generate_flows.py` is a separate, lighter-weight script that outputs a different format with fewer flows (12-20). **Never run `generate_flows.py` standalone** — it will overwrite `site/data/flows.json` and truncate 84 flows → 12. If you need to regenerate flows, run `db_to_json.py` instead. Full documentation: `references/db-to-json-authority.md`.

```bash
curl -sk https://www.lagazzettadikyiv.com/data/flows.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
flows = d['flows']
# Check for generic fallback flows (all \$1B with identical headlines)
generic = sum(1 for f in flows if f['amount_b'] == 1.0 and 'flowing' in f.get('headline',''))
rich = sum(1 for f in flows if f['amount_b'] >= 5.0)
# Check direction normalization — 'neutral' is the most common bad value
bad_dir = sum(1 for f in flows if f['direction'] not in ('inflow','outflow'))
bad_dir_names = set(f['direction'] for f in flows if f['direction'] not in ('inflow','outflow'))
print(f'Flows: {len(flows)} total, {rich} rich (>= \$5B), {generic} generic (\$1B), {bad_dir} bad directions')
if bad_dir > 0: print(f'  Bad direction values: {bad_dir_names}')
# PASS: flow_count > 50, rich >= 4, generic <= 3, bad_dir == 0
# WARN if flow_count < 30 → likely generate_flows.py overwrote db_to_json.py output
" 
```
- If flow_count < 30 → `generate_flows.py` was run standalone and truncated the file. Re-run `db_to_json.py`.
- If rich flows < 4 → db_to_json.py is reading from wrong data source
- If generic flows > 3 → stories don't have `capital_flow` dicts or parsing is falling through
- If bad_dir > 0 → db_to_json.py is missing `_normalize_direction()` call on loaded flows (see pitfall below)

### 2b. Verify stories.json capital_flow directions (v25.1 — catches "neutral" before it cascades)

"Neutral" directions in capital_flow dicts cause asymmetry scores to be skipped entirely (the asymmetry loop in `db_to_json.py` used to skip `direction == "neutral"`). Even after the skip is removed, "neutral" is an invalid direction for display. Verify 0 "neutral" in stories:

```bash
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
all_s = ([d.get('lead')] if d.get('lead') else []) + d.get('stories', [])
dirs = {}
for s in all_s:
    cf = s.get('capital_flow', {})
    if isinstance(cf, dict):
        dirs[cf.get('direction', '')] = dirs.get(cf.get('direction', ''), 0) + 1
print(f'Stories: {len(all_s)}')
for k,v in sorted(dirs.items()):
    print(f'  {k}: {v}')
neutral = dirs.get('neutral', 0)
if neutral > 0:
    print(f'FAIL: {neutral} stories have neutral direction — run db_to_json.py normalization pass')
else:
    print('PASS: 0 neutral directions')
"
# PASS: neutral=0. If >0 → db_to_json.py §v24.3 cleanup pass not running or data stale.
```

### 3. Verify summary matches actual flows (catches direction normalization failures)
```bash
curl -sk https://www.lagazzettadikyiv.com/data/flows.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
inflows = sum(1 for f in d['flows'] if f['direction'] == 'inflow')
outflows = sum(1 for f in d['flows'] if f['direction'] == 'outflow')
reported = d['summary']
actual = f'{inflows} inflows · {outflows} outflows'
print(f'Reported: {reported}')
print(f'Actual:   {actual}')
print('MATCH' if reported == actual else 'MISMATCH — direction normalization broken!')
"
```

### 4. Check live site via browser console
```js
// Verify each change with browser_console
JSON.stringify({
  font: getComputedStyle(document.querySelector('.masthead-name')).fontFamily,
  emblem: document.querySelector('.masthead-caduceus,.masthead-balance,.masthead-fox')?.className,
  confidence: document.getElementById('heroConfidence')?.innerHTML,
  hero_labels: Array.from(document.querySelectorAll('.hero-stat-label')).map(el => el.textContent)
})
```

### 4.5 JS INTERACTIVITY CHECK (CRITICAL — added v23.9, June 2026)

### 4.55 NULL-UNDEFINED LEAK CHECK (v25.4 — catches safeCF() gaps)

After every deploy, verify zero \"undefined\" or \"null\" strings in rendered DOM content:

```js
JSON.stringify({
  undefined: (document.body.innerHTML.match(/undefined/g)||[]).length,
  nullText: (document.body.innerHTML.match(/>null</g)||[]).length,
  cards: document.querySelectorAll('.card').length,
  firstBadge: document.querySelector('.cf-claim')?.textContent?.substring(0, 100)
})
// PASS: undefined = 0, nullText = 0
// If undefined > 0 → capital_flow fields are null, safeCF() not deployed or not covering all paths
```

### 0.3 ALL-PAGE VISUAL SWEEP (MANDATORY v24.0+)

Code-only verification misses: debug grid numbers rendered as visible text, keyboard hints in production, stuck loading states, truncated text, duplicate elements. After every deploy, visually verify EVERY nav-linked page:

```js
// Navigate to each nav-linked page and check it renders content
const pages = ['stories.html', 'flows.html', 'signal.html', 'trades.html', 'track.html', 'event_horizon.html', 'flow-nodes.html'];
// For each: browser_navigate → browser_snapshot → check element count > 10 AND no 'Loading...' AND no debug artifacts
```

**PASS criteria for each page:**
- Element count > 10 (bare skeleton = 5-9 elements)
- No debug artifacts: zero instances of `\d+\|` as visible text, no "Keys: * filter", no grid line numbers
- No stuck loading: no "Loading..." text that persists >5 seconds
- Content renders: stories page has stories, flows page has flows, signal has tickers

**⚠️ SNAPSHOT FALSE-NEGATIVE PATTERN (v24.0 June 2026):** The browser snapshot tool only captures static HTML elements — it CANNOT see dynamically-added DOM children. JS-rendered content (story detail pages, flow lists, hero indicators) will appear as 5-13 elements in the snapshot even when the page is rendering 30KB+ of content correctly. The story detail page (`story.html?id=...`) shows only 5 elements in snapshot but 8,629 bytes of body with full intel-report articles. **After every snapshot check, supplement with console verification:**

```js
// Mandatory console complement to prevent false negatives
JSON.stringify({
  bodyLen: document.body.innerHTML.length,
  hasMain: !!document.querySelector('main'),
  mainLen: (document.querySelector('main')?.innerHTML || '').length,
  storyCards: document.querySelectorAll('.intel-report, .story-card, .flow-row, article').length,
  anyContent: document.body.textContent.trim().length > 50
})
```

**PASS:** `bodyLen > 3000` AND `anyContent: true`. If snapshot says 5 elements but console shows `bodyLen > 8000`, the page IS rendering — the snapshot is a false negative. Do NOT report the page as broken based on snapshot alone.

Full reproduction: `references/snapshot-false-negatives.md`

### 0.4 CORRUPTED FILE DETECTION (v25.0 — extended to JS)

Line-number prefixes (`    N|`) embedded in every line of HTML or JS files cause silent failures. HTML files render garbage; JS files parse as invalid syntax and never execute — the page stays stuck on "Loading…" with no console error. **Any file touched by a patch or read_file → write cycle is at risk.**

```bash
# Check ALL HTML and JS files (not just the three known targets)
for f in site/*.html site/*.js; do
  [ -f "$f" ] || continue
  if head -1 "$f" | grep -q '^\s*[0-9]\+\|'; then
    echo "FATAL: $f corrupted with line numbers — refusing to deploy"
    exit 1
  fi
done
```

Full reproduction + detection guide: `references/corrupted-file-detection.md`

**Verify post-fix:** `head -3 FILE` — must show normal content (no leading `N|`). Also verify byte count dropped: corrupted files are ~15% larger due to the prefix overhead.

**Known targets (v25.0):** `story-app.js` was deployed corrupted — 15,647 bytes (should be 13,608). The `story-app.cc2e0196.js` hash originates from the corrupted file, so deploying the clean file under the same hash name is correct (the hash in story.html references the corrupted build, but the content is now clean).

**Also detect missing closing script tags (v24.10 June 2026):** A patch can truncate the closing script tag, causing the entire inline JS to be parsed as HTML text — silently, with no console error. The page loads but no JS runs.

**Also detect backslash-n literal insertion in generated JavaScript (v28, June 2026):** When patch-editing Python template files that emit JavaScript (e.g., build_frontend.py), the patch tool may insert literal backslash-n instead of a newline. The Python compiles clean (ast.parse passes), the build succeeds, but the generated JS has a syntax error that kills the entire inline script. Detection: grep the HTML output for backslash-n outside string literals, AND verify key render functions exist: grep -c 'STORIES.map' public/index.html must return at least 1. Fix: replace the literal backslash-n in the Python source with a true newline. event_horizon.html was deployed in this state: 47KB file, 0 script tags parsed by the browser, stuck on loading spinner.

```bash
# Verify every HTML file with inline scripts has matching close tags
for f in site/*.html site/ru/*.html; do
  opens=$(grep -c '<script' "$f" 2>/dev/null || echo 0)
  closes=$(grep -c '</script>' "$f" 2>/dev/null || echo 0)
  if [ "$opens" != "$closes" ]; then
    echo "FATAL: $f has $opens <script> opens but $closes </script> closes — JS will not execute"
  fi
done
```

Fix: append `</script>\n</body>\n</html>` if missing. BUT also verify the script content wasn't truncated mid-function — check `tail -3` for `})();` or `init();` before the closing tag.

### 0.35 DATA DIRECTORY EXISTENCE — THE SILENT SITE-KILLER (v27.0 June 2026)

**This is the most common silent failure.** `public/data/` is NOT part of the repo — it's a build artifact created by `build_site.py` (or Stage 5 of the unified pipeline). If this directory doesn't exist on GCS, ALL JS fetches return 404, every hero indicator shows `—`, teaser containers are empty, and the site appears completely dead — with zero console errors (the fetches just return empty/null and the code skips rendering).

```bash
# Verify data directory exists on GCS
curl -skI https://www.lagazzettadikyiv.com/data/stories.json | head -1
# MUST return HTTP/2 200. If 404 → public/data/ was never deployed.

# Verify at least 3 critical files
for f in stories.json flows.json narratives.json; do
  STATUS=$(curl -skI "https://www.lagazzettadikyiv.com/data/$f" 2>/dev/null | head -1 | awk '{print $2}')
  echo "$f: $STATUS"
done
# ALL must return 200.

# Verify file sizes are non-trivial (not empty objects)
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json,sys; d=json.load(sys.stdin)
count = len(d.get('stories',[]))
print(f'stories.json: {count} stories')
if count < 10: print('FAIL: too few stories — data directory likely stale or empty'); sys.exit(1)
"
```

**If missing:** Run `build_site.py` then deploy:
```bash
cd ~/lagazzettadikyiv && python3 scripts/build_site.py
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
$GSDK/gsutil -m rsync -r public/data/ gs://www.lagazzettadikyiv.com/data/
$GSDK/gsutil setmeta -h "Cache-Control:no-store,max-age=0" gs://www.lagazzettadikyiv.com/data/*.json
```

**Why this happens:** Manual deploys (`gsutil cp` or `gsutil rsync` of individual files) skip `build_site.py`. The `shipit.sh` Stage 2 runs it automatically, but ad-hoc deploys don't. Also, if `build_site.py` fails silently (e.g., missing data/ source files), it creates the directory but writes empty files.

### 0.35b STAGING SUBDIRECTORY DATA PATHS (v27.3 June 2026)

When a page lives at `staging/stitch-mobile/index.html` and fetches `./data/stories-v4.json`, the resolved URL is `staging/stitch-mobile/data/stories-v4.json` — NOT the root `data/stories-v4.json`. GCS doesn't traverse upward. **Every staging subdirectory must either (a) contain its own `data/` directory with copies, (b) use `../../data/` relative paths with `<base href="/">`, or (c) use absolute paths from root.**

Detection: `curl -sI "$STAGING_URL/$(grep -oP 'fetch\(["\x27]\.\/[^"\x27]+' <<< "$HTML" | head -1 | sed 's/fetch("\.\///;s/".*//')" | head -1` — if 404, the staging page can't load data.

Full verification workflow: `references/stitch-design-verification.md`

### 0.36 STORY FRESHNESS CHECK (v27.1 — added freshness label fallback verification)

Even when data/ exists and stories.json has content, the teaser may show stale stories (>24h old) because `db_to_json.py` sorts by `contradiction_score DESC` before `generated_at DESC`. New stories with default score=50 sort AFTER old stories with score=75.

Additionally (v27.1), the freshness label (`<span class="freshness-ago">`) only renders when `time_decay.current_freshness` is not `undefined`. Newly-approved stories may have `time_decay: {}` (empty object), which causes the label to be omitted entirely. The user sees story headlines with no time indicator — confusing. The fix (app.js ~line 2543): always render the freshness label, using `formatTimeAgo(s.generated_at)` as the time text. The CSS class defaults to `freshness-recent` when `current_freshness` is undefined.

```bash
# Check first 5 stories are from today
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json,sys
from datetime import datetime, timezone
d = json.load(sys.stdin)
stories = d.get('stories', [])
today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
fresh = [s for s in stories[:20] if s.get('generated_at','').startswith(today)]
print(f'First 20 stories: {len(fresh)} from today ({today})')
first_date = stories[0].get('generated_at','?')[:10] if stories else 'no stories'
print(f'First story date: {first_date}')
if len(fresh) == 0:
    print('FAIL: No fresh stories on front page — sort order is burying them')
    sys.exit(1)
elif len(fresh) < 5:
    print(f'WARN: Only {len(fresh)} fresh stories in top 20 — sort may need tuning')
else:
    print('PASS: Fresh stories visible')
"
```

If FAIL: run the fresh-story pipeline recovery procedure in `gazzetta-knowledge-base/references/fresh-story-pipeline-recovery.md`.

### 0.5 FRESHNESS PERCENTAGE CHECK (v24.0)

Bare percentages on story teasers are universally misinterpreted as CONFIDENCE. 5/5 professionals flagged "100%" on all 8 stories. Verify time labels are displayed:

```js
JSON.stringify({
  labels: Array.from(document.querySelectorAll('.freshness-ago')).map(s => s.textContent).slice(0,5),
  hasPercents: Array.from(document.querySelectorAll('.freshness-ago')).some(s => s.textContent.includes('%'))
})
```

PASS: `hasPercents` = false. If true → users WILL read it as confidence, trust destroyed.

**Fix pattern:** Replace `{pct}%` with `formatTimeAgo(s.generated_at)` in `populateTeasers()`. Full reproduction + fix: `references/freshness-percentage-bug.md`

### 4.7 HASHED ASSET VERIFICATION (v23.25 — June 2026)

Gazzetta uses content-hashed filenames (`app.bf173854.js`). Curl-based verification can miss the case where the hashed file IS deployed but the OLD hash is still referenced by HTML. After every deploy:

```js
// Verify browser loads the correct hashed JS
JSON.stringify({
  jsHash: document.querySelector('script[src*="app."]')?.src?.match(/app\.([a-f0-9]+)\.js/)?.[1],
  cssHash: document.querySelector('link[href*="styles."]')?.href?.match(/styles\.([a-f0-9]+)\.css/)?.[1],
  i18nHash: document.querySelector('script[src*="i18n."]')?.src?.match(/i18n\.([a-f0-9]+)\.js/)?.[1]
})
```

```bash
# Verify GCS manifest matches deployed hashes
curl -sk $SITE_URL/build-manifest.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('app','NO APP HASH'))"
```

If the browser loads an old hash → the build_hashed_assets.py step was skipped or ran out of order. Re-run: `cp app.js site/ && python scripts/build_hashed_assets.py && gsutil -m rsync -d -r site/ gs://BUCKET/`.

Curl-based verification CANNOT detect JS pipeline failures. The TDZ bug (gazzetta-website v23.8) survived multiple curl-only verifications because the static HTML looked correct — hero indicators and teaser counts are JS-populated and always show `—` placeholders in curl output. **After EVERY deploy, verify JS execution with browser tools:**

```js
// MANDATORY interactivity check via browser_console
JSON.stringify({
  // Hero indicators must NOT show dashes
  heroDivergence: document.getElementById('heroContradictions')?.querySelector('.hero-ind-value')?.textContent?.trim(),
  heroFreshness: document.getElementById('heroFreshness')?.textContent?.trim(),
  // Asymmetry gauge must have a value (not '—')
  gaugeValue: document.getElementById('heroGaugeValue')?.textContent?.trim(),
  
  // Teaser counts must NOT show dashes  
  storiesCount: document.getElementById('teaserStoryCount')?.textContent?.trim(),
  flowsCount: document.getElementById('teaserFlowSub')?.textContent?.trim(),
  
  // Gazzetta namespace must be populated (not empty object)
  gazzettaStateKeys: Object.keys(window.Gazzetta?.State || {}).length,
  
  // CAPITAL_FLOWS_DATA must be defined (set by fetchFlows())
  cfdDefined: typeof window.CAPITAL_FLOWS_DATA !== 'undefined'
})
```

**PASS criteria:**
- `heroDivergence` ≠ `"—"` (e.g., "5" — number of diverged flows)
- **Hero divergence sanity check (v24.10):** If `heroDivergence` = "0", manually verify it's genuine — ALL flows have confidence ≥ threshold. If the threshold is 70% and 12/12 flows are ≥81%, "0" is correct but misleading. Consider whether the label should show "ALIGNED" instead of "DIVERGENCE" when the count is 0. The old code counted `confidence_pct < 70` and showed "0 DIVERGENCE" — 5/5 focus group professionals read "0 DIVERGENCE" as "this indicator is broken." Changed to compute actual narrative-price divergence via `computeDivergence()` and show "ALIGNED" when count is 0.
- `gaugeValue` ≠ `"—"` (e.g., "58" — max asymmetry score)
- `storiesCount` ≠ `"—"` (e.g., "8 stories")
- `gazzettaStateKeys` > 0
- `cfdDefined` = true
- `storiesCount` ≠ `"—"` (e.g., "8 stories")
- `gazzettaStateKeys` > 0 (minimum: capturedStoryIds, STORIES_CACHE should exist)
- `cfdDefined` = true

If ANY of these fail, the JS pipeline is dead regardless of curl/static checks. The most common cause is a TDZ error in the namespace block (see `gazzetta-website` skill §Gazzetta-Namespace). Do NOT report success until ALL pass.

### 4.6 Ticker deduplication check
```js
// Live tickers must not have duplicates
JSON.stringify({
  tickers: Array.from(document.querySelectorAll('.side-freshness .fresh-item span:nth-child(2)'))
    .map(s => s.textContent),
  unique: new Set(Array.from(document.querySelectorAll('.side-freshness .fresh-item span:nth-child(2)'))
    .map(s => s.textContent)).size
})
```
If `unique` < count of ticker elements, a duplicate ticker exists — check `fetch_market_data.py` TICKER_MAP for redundant mappings.

### 4. Cross-check data sources
```python
# Verify data has required fields for new features
import json
with open('site/data/stories.json') as f: stories = json.load(f)
with open('site/data/flows.json') as f: flows = json.load(f)
# Check for field coverage
for s in stories[:5]:
    cf = s.get('capital_flow', {})
    print(f"{s.get('headline','')[:40]} | positioning: {'✓' if cf.get('positioning') else '✗'}")
```

### 5. Checklist of recent changes
- [ ] Font rendering: check `fontFamily` in browser
- [ ] Emblem: check DOM for correct class
- [ ] Confidence tier: check innerHTML for HIGH/MEDIUM/LOW
- [ ] Positioning labels: check `.flow-detail` for "Smart money"
- [ ] cf-hint with sectors: check `.cf-hint` textContent for sector names
- [ ] All hero stats: check non-dash values
- [ ] CDN cache TTL: `gsutil ls -L gs://www.lagazzettadikyiv.com/index.html | grep Cache`
- [ ] **app.js version bump**: `curl -s https://www.lagazzettadikyiv.com/ | grep -o 'app.js?v=[0-9.]*'` — must match latest version in `site/index.html`

### 0.7 RU PAGE EXISTENCE + SCRIPT PATH VERIFICATION + SUB-PAGE GATE (v25.9 — adds sub-page list fix)

**FIRST: verify ALL RU sub-pages return 200 (not homepage fallback).** If `/ru/stories.html` returns the same HTML as `/ru/`, the ru_sync_gate didn't copy sub-pages. Full fix: `references/ru-sync-gate-subpages.md`.

**SECOND: verify the RU page EXISTS on GCS.** The `/ru/` directory can go empty after a deploy that doesn't include `site/ru/`. Without an RU index.html, GCS serves the English homepage at `/ru/` as a 404 fallback — English text, no `<base>` tag, all hero indicators show `—`, JS partially works but data fetches 404.

```bash
# Verify RU page returns 200 (not fallback English homepage)
RU_STATUS=$(curl -skI "https://www.lagazzettadikyiv.com/ru/" | head -1 | awk '{print $2}')
if [ "$RU_STATUS" != "200" ]; then
  echo "FATAL: /ru/ returns $RU_STATUS — RU page missing from GCS"
fi

# Also verify it's actually Russian (not English fallback)
RU_LANG=$(curl -sk "https://www.lagazzettadikyiv.com/ru/" | grep -o 'lang="[^"]*"' | head -1)
echo "RU page lang: $RU_LANG (must be lang=\"ru\")"
```

**If missing:** Build from root index.html:
```bash
mkdir -p site/ru
cp site/index.html site/ru/index.html
# Then fix: <base href="/">, lang="ru", ../ paths, nav links
python3 -c "
c = open('site/ru/index.html').read()
c = c.replace('<meta charset=\"utf-8\"/>', '<meta charset=\"utf-8\"/>\n  <base href=\"/\">')
c = c.replace('<html lang=\"en\">', '<html lang=\"ru\">')
for attr in ['src', 'href']:
  for f in ['i18n.', 'app.', 'styles.', 'stories.html', 'flows.html', 'event_horizon.html', 'flow-nodes.html', 'signal.html', 'trades.html', 'track.html', 'story.html', 'about.html', 'methodology.html']:
    c = c.replace(f'{attr}=\"./{f}', f'{attr}=\"../{f}')
c = c.replace('href=\"./\"', 'href=\"../\"')
open('site/ru/index.html', 'w').write(c)
"
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
$GSDK/gsutil -h 'Cache-Control:public,max-age=0,must-revalidate' cp site/ru/index.html gs://www.lagazzettadikyiv.com/ru/index.html
$GSDK/gsutil -m rsync -r site/ru/ gs://www.lagazzettadikyiv.com/ru/
```

**Also verify data files deployed to `/data/` (not `/ru/data/`):** `<base href="/">` makes all relative fetches resolve from root.
```bash
curl -skI https://www.lagazzettadikyiv.com/data/stories_ru.json | head -1  # must be 200
curl -skI https://www.lagazzettadikyiv.com/data/flows_ru.json | head -1    # must be 200
```

The RU index.html lives under `site/ru/`. If it references scripts with `./app.xxx.js` (relative to `/ru/`), all JS silently 404s — no console error visible to curl. The result: hero indicators show `—`, tickers are empty, flow sectors have no values, sentiment shows `—`. **Every element populated by app.js is dead on the RU page.**

```bash
# Verify RU script paths are correct (must use ../ not ./)
grep -o 'src="[^"]*"' site/ru/index.html | grep -E 'app\.|i18n\.'
# MUST show: src="../app.XXXXXXXX.js"  src="../i18n.XXXXXXXX.js"
# FAIL if:    src="./app.XXXXXXXX.js"  src="./i18n.XXXXXXXX.js"

# Verify the scripts actually resolve
curl -skI https://www.lagazzettadikyiv.com/ru/app.bf173854.js | head -1
# MUST return: HTTP/2 200
# If 404 → paths are wrong (./ instead of ../)

# Also check stylesheet path
grep -o 'href="[^"]*css"' site/ru/index.html
# MUST show: href="../styles.XXXXXXXX.css"
```

**Fix:** `sed -i '' 's|src="./app\\.|src="../app.|g; s|src="./i18n\\.|src="../i18n.|g; s|href="./styles\\.|href="../styles.|g' site/ru/index.html`

**Also verify `<base href="/">` is present (v24.10 June 2026):** Fixing script paths to `../` isn't enough — app.js fetches data with relative paths (`./data/stories.json`), which still resolve to `/ru/data/stories.json` from the RU page. Without `<base href="/">`, ALL data fetches silently 404. The result: flows, stories, tickers, sentiment — everything JS-populated — appears as `—`. The page looks identical to the script-path bug but with correct script URLs.

```bash
# Verify <base> tag exists in RU index.html
grep -c '<base href="/">' site/ru/index.html
# MUST print: 1
# If 0 → add after <meta charset>:
#   <base href="/">
```

Combined fix checklist for RU page:
1. Script paths: `./` → `../`
2. Stylesheet path: `./` → `../`  
3. Data preload paths: `./data/` → `../data/`
4. Inline fetch paths: `./data/` → `../data/`
5. `<base href="/">` after `<meta charset>`
6. `lang="en"` → `lang="ru"` on `<html>` tag
7. Nav links: `./stories.html` → `../stories.html` (etc.)

Full reproduction and lingering data-path issue: `references/ru-script-path-bug.md`

```bash
# Check stories_ru.json on GitHub Pages (fast — 60s deploy)
curl -s "https://pureciclismo.github.io/gazzetta-di-kyiv/data/stories_ru.json" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); s=d['stories'][0]; print('Cyrillic:', any(0x0400<=ord(c)<=0x04FF for c in str(s)))"
# Must print: Cyrillic: True

# Check live domain (CDN — up to 1h lag for data files)
curl -s "https://www.lagazzettadikyiv.com/data/stories_ru.json?t=$(date +%s)" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); s=d['stories'][0]; print('Cyrillic:', any(0x0400<=ord(c)<=0x04FF for c in str(s)))"
# Must print: Cyrillic: True

# Verify i18n key count
python3 -c "import json; d=json.load(open('site/i18n_ru.json')); print(f'Keys: {len(d)} (need >= 108)')"

# Verify translated texts count in latest run
python3 -c "import json; d=json.load(open('data/stories_ru.json')); print(f'Stories: {len(d.get(\"stories\",[]))}')"

# CRITICAL (v22.14+): Verify ALL container elements have data-i18n attributes
# This catches the #1 Russian translation bug — translations exist but HTML lacks attributes
curl -s "https://www.lagazzettadikyiv.com" | python3 -c "
import sys, re
html = sys.stdin.read()
# Find all container-title, container-subtitle, container-desc, asset-note elements
elements = re.findall(r'<(span|div)\s[^>]*class=\"[^\"]*(?:container-title|container-subtitle|container-desc|asset-note)[^\"]*\"[^>]*>', html)
missing = [el for el in elements if 'data-i18n=' not in el]
if missing:
    print(f'FAIL: {len(missing)} container elements missing data-i18n:')
    for el in missing:
        # Extract the English text
        text = re.search(r'>([^<]+)<', el)
        if text:
            print(f'  - \"{text.group(1)[:60]}\"')
else:
    print('PASS: all container elements have data-i18n')
"
```

**Minimum required `data-i18n` keys** (all must exist in deployed index.html):
- `container_stories_title`, `container_stories_desc`
- `container_flows_title`, `container_flows_desc`, `container_flows_footer`
- `container_anchors_title`, `container_anchors_subtitle`, `container_anchors_desc_prefix`
- `container_signal_title`, `container_signal_subtitle`, `container_signal_desc`, `container_signal_footer`
- `container_track_title`, `container_track_subtitle`, `container_track_desc`
- `pdr_label`, `anchor_note_key_levels`, `anchor_note_pdr`
- `masthead_tagline`, all `hero_*` keys

If GitHub Pages has Russian but custom domain doesn't → GCS deploy needed, not a translation problem.
If `pureciclismo.github.io` returns 404 or Latin-only → translation script didn't run or failed.

### 10. Trade Hook R:R Verification (v23.17 — catches quality gate failures)

The `anchorRowHTML()` function now filters trade hooks with R:R < 2.0. Verify the filter is active:

```bash
# Check that R:R computation exists in deployed app.js
curl -sk https://www.lagazzettadikyiv.com/app.js | grep -c 'rr >= 2.0\|return null.*R:R\|asset-rr'
# Must return >= 2 (R:R gate + CSS class usage)

# Check that hooks are actually rendering R:R badges
curl -sk https://www.lagazzettadikyiv.com/ | grep -c 'asset-rr'
# Should find R:R badge spans in sidebar (may be 0 if curl can't read JS-populated content — verify via browser_console instead)
```

**Browser verification (mandatory):**
```js
// Check trade hook count — should be less than total ANCHOR_ASSETS (13 → ~8 after filtering)
JSON.stringify({
  totalAssets: window.ANCHOR_ASSETS ? window.ANCHOR_ASSETS.length : '?',
  renderedHooks: document.querySelectorAll('.asset-rr').length,
  hasEliteHooks: document.querySelectorAll('.rr-elite').length,
  hiddenHooks: (window.ANCHOR_ASSETS || []).filter(a => !a._rr || a._rr < 2.0).length
})
```

PASS: `renderedHooks` < `totalAssets` (filter is active), `hiddenHooks` ≥ 3.

### 11. Freshness 2.0 Correlation Verification (v23.17)

The hero freshness indicator now uses `marketCorrelationLabel()` with CRITICAL/ACTIVE/DORMANT states:

```bash
# Verify freshness functions exist in deployed JS
curl -sk https://www.lagazzettadikyiv.com/app.js | grep -c 'marketCorrelationLabel\|freshnessLabel\|freshness-critical'
# Must return >= 3
```

**Browser verification:**
```js
// Hero freshness must show correlation state, not just time
JSON.stringify({
  freshnessText: document.getElementById('heroFreshness')?.querySelector('.hero-ind-value')?.textContent,
  freshnessClass: document.getElementById('heroFreshness')?.className,
  storiesStored: window._gazzettaStories ? window._gazzettaStories.length : 0
})
```

PASS: `freshnessText` contains CRITICAL, ACTIVE, DORMANT, or a temporal label. `freshnessClass` should not be the default hero-ind only (should have freshness-* modifier). `storiesStored` ≥ 1.

### 12. GCS Deploy Authentication (v23.17)

**Working SDK:** `~/lagazzettadikyiv/google-cloud-sdk/bin/gsutil`
**Account:** `pureciclismo@gmail.com`
**NOT the Hermes venv gsutil** — returns 401 on writes.

Deploy single files:
```bash
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
$GSDK/gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/app.js gs://www.lagazzettadikyiv.com/app.js
```

Bulk sync (full site):
```bash
$GSDK/gsutil -m rsync -d -r site/ gs://www.lagazzettadikyiv.com/
```

Root bucket (`gs://lagazzettadikyiv.com`) is read-only — writes return 401. Both domains currently serve same content (likely via GCS Load Balancer).

### 13. Conviction Probability Check (v23.18)

Every story must have a `conviction_probability` field (0-100%):

```bash
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
all_s = ([d.get('lead')] if d.get('lead') else []) + d.get('stories', [])
probs = [s.get('conviction_probability', 0) for s in all_s if s]
missing = sum(1 for p in probs if not p)
print(f'Stories: {len(probs)}, Missing probs: {missing}, Unique: {len(set(probs))}')
if missing > 0: print('FAIL'); sys.exit(1) else: print('PASS')
"
# PASS: missing=0, unique >= 2
```

### 14. Ticker Tape Verification (v23.18)

Live ticker tape div must be present with ticker-track child:

```bash
curl -sk https://www.lagazzettadikyiv.com/ | grep -c 'ticker-tape\|ticker-track'
# Must return >= 2 (both divs present)
curl -sk https://www.lagazzettadikyiv.com/app.js | grep -c 'buildTicker\|renderTicker'
# Must return >= 2 (both functions present)
```

### 16. Market Regime Card Population Check (v25.1 — catches Object.forEach() silent failure)

The market regime section on flows.html shows 3 cards (Money Flow, Top Heavy, Bond Fear). The `renderMarketRegime()` function fetches `data/market_regime.json` which returns indicators as a dict: `{"money_flow": {"signal": "BULLISH", "strength": 88}, ...}`. **If the function calls `.forEach()` on this object instead of `Object.entries()`, it silently fails** — `.forEach()` is undefined on plain objects, but the error is caught by `.catch(() => mr.style.display = 'none')` which hides the entire regime section. The cards show `—` for all three indicators with zero console output.

**Also check for field-name mismatch (v25.1 June 2026):** The code originally checked `ind.indicator` (e.g., `"Money Flow"`) but the JSON uses `ind.signal` for direction and the key name (e.g., `"money_flow"`) for identification. If the code compares `name === "Money Flow"` but the JSON key is `"money_flow"`, the match fails silently → `valueEl` is never set → `if (!valueEl) return;` exits early. All three cards stay at `—`.

```bash
# Verify regime cards are not showing dashes
curl -sk https://www.lagazzettadikyiv.com/app.js | grep -c 'Object.entries(data.indicators)'
# Must return >= 1 — Object.entries() handles dict indicators
# If 0, check for 'data.indicators.forEach' — this will silently fail on dicts

# Verify market_regime.json has the correct structure
curl -sk https://www.lagazzettadikyiv.com/data/market_regime.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
ind = d.get('indicators', {})
if isinstance(ind, list):
    print('FAIL: indicators is an array — renderMarketRegime expects dict')
elif isinstance(ind, dict):
    for k, v in ind.items():
        sig = v.get('signal', 'MISSING')
        print(f'  {k}: {sig}')
    print('PASS: indicators dict structure ok')
else:
    print(f'FAIL: indicators is {type(ind).__name__}')
"
```

**Browser verification:**
```js
JSON.stringify({
  regimeCards: Array.from(document.querySelectorAll('.regime-card')).map(c => ({
    value: c.querySelector('.regime-value')?.textContent?.trim(),
    isDash: c.querySelector('.regime-value')?.textContent?.trim() === '—'
  })),
  allDashes: Array.from(document.querySelectorAll('.regime-value')).every(el => el.textContent.trim() === '—')
})
// PASS: allDashes = false. If true → renderMarketRegime() failed silently (likely .forEach() on object)
```

Verify the e2-micro VM and systemd timers are operational:

```bash
gcloud compute instances describe gazzetta-prod --zone=us-central1-a --format='value(status)'
# Must print: RUNNING

gcloud compute ssh gazzetta-prod --zone=us-central1-a --command="systemctl list-timers --no-pager | grep gazzetta | wc -l"
# Must print: 4 (intel, pipeline, marketdata, shipit)
### 7. Story-Level Scaling Monotony Check (v23.20 — SHA256 uniqueness guard)

After every deploy, verify all capital flow amounts are unique. The old SLS v1.0 (hash-based jitter) could produce up to 6 duplicates. SLS v2.0 (SHA256-based) must produce zero:

```bash
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json, sys
from collections import Counter
d = json.load(sys.stdin)
all_s = ([d.get('lead')] if d.get('lead') else []) + d.get('stories', [])
amounts = [s.get('capital_flow',{}).get('amount_b',0) for s in all_s if s]
c = Counter(amounts)
dups = {v:n for v,n in c.items() if n > 1}
print(f'Stories: {len(amounts)}, Unique: {len(set(amounts))}')
print(f'$88B count: {amounts.count(88.0)}')
if dups:
    print(f'FAIL: {len(dups)} duplicated amounts — {dups}')
    sys.exit(1)
else:
    print('PASS: all amounts unique')
"
# MUST: duplicated amounts = 0, $88B count ≤ 1
# If $88B appears > 2 times, FAIL THE BUILD — SLS is broken.
```

Note: `test_platform.py` includes this check as part of the 191-assertion suite. The SLS-aware drift threshold is 60× (raised from 20×) to accommodate SETTLING-tier stories getting only 2% of category flow.

### 8. Asymmetry Score Null Check (v23.16 — catches write-back bug)

The asymmetry computation in `compile_flows()` must persist scores to `stories.json`. Verify 0 null scores:

```bash
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
all_s = ([d.get('lead')] if d.get('lead') else []) + d.get('stories', [])
nulls = sum(1 for s in all_s if s and s.get('asymmetry_score') is None)
scores = [s.get('asymmetry_score', 0) for s in all_s if s]
if nulls > 0:
    print(f'FAIL: {nulls} null asymmetry scores — write-back bug!')
    sys.exit(1)
elif len(set(scores)) < 2:
    print(f'FAIL: all scores identical ({scores[0] if scores else \"?\"}) — computation regression')
    sys.exit(1)
else:
    print(f'PASS: {len(scores)} stories, 0 null, range {min(scores)}-{max(scores)}')
"
# PASS: nulls=0, unique scores >= 2
```

### 9. Onboarding Modal Check (v23.16 — institutional trust)

No welcome modals, onboarding tooltips, or first-visit overlays on any page:

```bash
curl -sk https://www.lagazzettadikyiv.com/ | grep -ci 'onboarding\|welcome.*gazzetta\|getting.started\|dismiss.*modal' 
# Must print: 0

curl -sk https://www.lagazzettadikyiv.com/ru/ | grep -ci 'onboarding\|welcome.*gazzetta\|getting.started\|dismiss.*modal'
# Must print: 0
```

## Pitfalls

- **⛔ browser_vision HALLUCINATES colors — NEVER trust it alone (v26.2 June 2026).** Both `browser_vision` AND `vision_analyze` repeatedly hallucinated a "dark bar" at the top of the page when the masthead background was proven `rgb(255, 255, 255)` (white) by `getComputedStyle()`. Three consecutive vision calls described a dark nav bar with white text — the DOM proved otherwise: `master-nav { display: none }`, masthead `backgroundColor: rgb(255, 255, 255)`, nav links `color: rgb(139, 0, 0)` (dark red). The vision models appear to conflate browser chrome (address bar) with page content, or misread thin gold borders as dark backgrounds. **After EVERY visual claim about colors or element presence, verify with `browser_console` `getComputedStyle()` — the DOM is deterministic, vision is not.** Full reproduction: `references/vision-hallucination-dark-bar.md`.
- **CSS duplicate rule trap (v26.2 June 2026).** When a CSS file has the SAME property defined twice on the same selector — once early in the file (e.g., `.masthead-name { font-size: 1.8em }` at line 116) and once later OUTSIDE any `@media` query (e.g., `.masthead-name { font-size: 3em }` at line 1080) — the later rule wins by cascade. The second occurrence was originally inside `@media (max-width: 600px)` but the `}` at line 1018 closed the media block early, leaking the rules to global scope. Detection: `grep -n '\.masthead-name\b.*font-size' styles.css` — if the same property appears twice, the later one wins. Fix: either scope the second occurrence properly or match the value to the first. Also check for orphaned `}` that prematurely close `@media` blocks — `grep -n '^}' styles.css` and trace brace matching manually near any suspicious global rules.
- **CSS hash → ALL HTML files chain (v26.2 June 2026).** When editing `styles.css`, the browser loads the HASHED file referenced in each HTML page. The chain: edit CSS → hash → copy to hashed file → update reference in EVERY HTML file (currently 20: index.html, stories.html, flows.html, signal.html, trades.html, track.html, event_horizon.html, flow-nodes.html, about.html, privacy.html, methodology.html, story.html, capital.html, data.html, geopolitics.html, markets.html, pleasure.html, sources.html, terms.html, wealth.html) → deploy ALL HTML + both CSS files. **Skipping sub-pages means those pages load old CSS.** User explicitly flagged this as a trust-breaking failure: "the site doesn't change even after you say you changed it." Verify: `curl -s $SITE_URL/PAGE.html | grep -o 'styles\.[a-f0-9]*\.css' | sort -u` — must return exactly one hash, and it must match the latest deployed hashed file.
- **`build_hashed_assets.py` regex misses non-numeric query strings (v27.1 June 2026).** The unhashed-match regex `\?v=\d.]+` only matches numeric version strings like `?v=22.22` but misses alphanumeric tags like `?v=fix2` or `?v=sprint4`. If you manually set a non-numeric cache buster then run the hasher, the hashed script won't replace the old reference — HTML stays stuck on the non-hashed filename. Fixed the regex to `\?v=\w+`. Detection: after running `build_hashed_assets.py`, verify `grep 'app\.js\?' *.html` returns empty — any remaining `?v=` means the regex missed it. Fix: use numeric version tags (`?v=23`) or run: `for f in *.html; do sed -i '' 's|app\.js?v=[^"]*|app.ad499bee.js|g' "$f"; done` with the current hash.
- **`gsutil cp public/*.html` does NOT deploy data files (v27.1 June 2026).** The shell glob `public/*.html` matches only HTML files in the `public/` root — it does NOT descend into subdirectories like `public/data/` or `public/api/`. If you deploy HTML-only without a separate `gsutil rsync -r public/data/` step, the data files on GCS remain stale (or absent). Symptoms: JS fetches return 404 or stale JSON, hero indicators show `—`, stories are days old. This happened twice in one session because the deploy command looked right (`gsutil -m cp public/*.html`) but silently skipped everything in `public/data/`. Fix: always deploy with `gsutil -m rsync -r public/` (recursive) or follow HTML deploy with explicit `gsutil -m cp -r public/data/* gs://BUCKET/data/`. GCS serves files with `cache-control: public, max-age=3600` by default. After `gsutil cp`, the GCS object updates immediately (`gsutil cat` confirms), but the HTTP edge cache serves stale bytes for up to 1 hour (`age:` header shows seconds since cache fetch). Manifestation: `gsutil cat gs://BUCKET/index.html` shows new hash, but `curl $URL` returns old hash. Fix: (1) `gsutil setmeta -h "Cache-Control:no-cache, max-age=0" gs://BUCKET/*.html gs://BUCKET/*.css gs://BUCKET/*.js` on all objects, (2) re-upload files with `-h "Cache-Control:no-cache, max-age=0"` flag so new cache headers take effect. The edge cache may still serve stale for a few minutes — verify with `curl -sI $URL | grep -E 'cache|age'`.\n- **⛔ DELETING OLD CSS HASHES BEFORE VERIFYING ALL PAGES — trust-breaking failure (v26.6 June 2026).** When you delete old hashed CSS files from GCS during cleanup, the edge cache may still serve OLD HTML referencing those deleted files. Result: sub-pages load with ZERO CSS — unstyled page, browser default black borders, user sees a completely broken site. This caused the user to scream \"are you fucking retarded\" and nearly abandon the project. The chain: (1) deploy new CSS hash + update all HTML → (2) delete old CSS hashes from GCS → (3) edge cache still serves old HTML referencing deleted CSS → (4) pages have no stylesheet → (5) user sees garbage. **NEVER delete old CSS/JS hashes from GCS until you have verified EVERY page via curl that it references the new hash.** Verification command: `for f in index.html stories.html flows.html signal.html trades.html track.html about.html; do echo -n \"$f: \" && curl -s \"\\$SITE_URL/$f?t=\\$(date +%s)\" | grep -o 'styles\\.[a-f0-9]*\\.css'; done` — must return the SAME new hash for every page. Only then delete old hashes. Also: after deleting, re-verify all pages still load CSS (edge cache may still serve deleted-file references). Full reproduction: `references/deleted-css-breaks-cached-html.md`.
- **Staging data path resolution trap (v27.3 June 2026).** Pages in staging subdirectories (e.g., `staging/stitch-mobile/index.html`) that fetch `./data/stories-v4.json` resolve to `staging/stitch-mobile/data/` — NOT root `data/`. GCS won't traverse upward. The page loads HTML and CSS but shows "LOADING..." with 404 console warnings. Fix: either copy data files into the staging subdirectory, use `../../data/` paths, or set `<base href="/">`. Detection: check `browser_console` for fetch 404s after navigating to the staging URL. Full procedure: `references/stitch-design-verification.md`.
- **Inline CSS architecture (v32.0+ June 2026).** The site has NO external stylesheet. ALL CSS lives in a `<style>` block inside `build_frontend.py` that gets baked into the single `index.html` SPA. `public/styles.css` is a ghost file — never referenced, never deployed. The entire CSS hash chain procedure in this skill (sections 0.1, 4.7, deploys with hashed filenames) does NOT apply to the current architecture. CSS changes require editing `build_frontend.py`, regenerating `public/index.html`, and deploying that single file. Verifying CSS: check the inline `<style>` block in the CDN HTML directly — `curl -sk $SITE | grep -c 'YOUR_CSS_RULE'`.
- **GCP backend bucket custom response headers for security (v32.1 June 2026).** GCS objects only support Cache-Control natively. Security headers (X-Frame-Options, X-Content-Type-Options, Referrer-Policy) MUST be injected via the Load Balancer: `gcloud compute backend-buckets update BACKEND --custom-response-header='X-Frame-Options: DENY' --custom-response-header='X-Content-Type-Options: nosniff' --custom-response-header='Referrer-Policy: strict-origin-when-cross-origin'`. Headers take up to 10 minutes to propagate. Verify with `curl -sI $CDN_URL`. Do NOT add CSP blindly — it blocks Tailwind CDN, Google Fonts, and Material Symbols unless all origins are whitelisted.
- **$0M display guard — show N/A for genuinely missing data (v32.1 June 2026).** When capital_volume_usd is exactly 0 because AUM data is absent (not because the value is zero), display "N/A" instead of "$0M". $0M reads as "your data pipeline is broken." N/A reads as "this metric is not yet available for this ticker." Implementation: `(n.capital_b >= 1 ? fmtB : n.capital_b > 0 ? fmtM : 'N/A')`. Applies to Domain Intelligence sidebar and GAP Leaderboard only — NOT story cards where 0 genuinely means "no capital at stake." This means browsers and edge CDN nodes cache app.js for ONE YEAR and never revalidate — even after the file content changes on GCS. GCS `stored-content-length` shows the new bytes, but `curl` returns the old cached content. The only reliable fix: upload with a versioned filename (app.v4.js) and update all HTML references, OR deploy with `Cache-Control: no-cache` temporarily to flush the CDN, then restore the immutable header after verification. Detection: compare `curl -sI $URL/app.js | grep stored-content-length` against local `wc -c public/app.js` — if they match but `curl -s $URL/app.js | grep YOUR_NEW_CODE` returns 0, the CDN is stale. Full reproduction in `references/cdn-immutable-stale-js.md`.
- **CDN may serve stale hashed HTML even with must-revalidate (v25.13 June 2026).** After deploying rewritten HTML with new CSS/JS hash references, the CDN can continue serving old HTML for several minutes. Browser loads old hashed JS → i18n errors, missing fixes. Fix: deploy new hashed assets first, then HTML, delete old hashes, verify browser loads new hashes. Full procedure: `references/cdn-hash-rotation-pitfall.md`.
- **CSS cleanup leaves orphaned declarations (v25.13 June 2026).** When removing CSS rules (e.g., `.lang-switch { ... }`), orphaned `display: -webkit-inline-flex;` statements can remain outside any rule block. These cause CSS parse failures downstream. After any CSS cleanup: `grep -n '^\s*display:' styles.css` — orphaned declarations appear as bare properties without a parent selector above them. Fix: remove the orphaned lines.
- **Regex block removal leaves orphaned body code (v25.13 June 2026).** When using regex to remove conditional blocks like `if (window.i18n && ...) { ... }`, the regex may remove only the `if` line, leaving the block body (setTimeout, addEventListener) as orphaned statements inside the parent function. This causes silent JS execution failures — `boot()` appears to run but hangs waiting for events that never fire. After any regex-based code removal: `grep -n 'addEventListener\|setTimeout\|resolve'` to verify no orphaned async primitives remain. Full example in today's session: `boot()` had orphaned `window.addEventListener('i18nReady', ...)` and `setTimeout(resolve, 5000)` after removing the wrapping `if (window.i18n)` condition.
- **GCS cp not taking effect (v25.1 June 2026)** — `gsutil cp` with `Cache-Control:no-store` can report success but the LB serves stale bytes. The fix: `gsutil rm` first, then `gsutil cp`. This hit again v25.2 — the css file was correct on GCS (`gsutil cat` confirmed) but curl showed old bytes. Full reproduction: `references/gcs-delete-reupload.md`.
- **CSS brace leakage (v25.2)** — Rules like `font-size: 3em` overridden to 16px by a leaked media-query rule. Root cause: orphaned `}` in the stylesheet prematurely closes @media blocks, leaking their contents to global scope. Detection + fix: `references/css-brace-debugging.md`.
- **Story data ≠ flow data** — stories.json may lack fields that flows.json has. Always check BOTH data sources when adding a field-dependent feature
- **Silent data fallbacks** — `cf.positioning ? label : ''` silently renders nothing if data is missing. Always verify data has the field before relying on it
- **Browser console succeeds but renders wrong** — CSS/class may hide correct content. Always do BOTH console check AND visual snapshot check
- **data/ vs site/data/ divergence** — `data/` is source of truth for editorial content, `site/data/` is deployed.
- **db_to_json.py is the AUTHORITATIVE flows.json source (v25.0 June 2026).** `generate_flows.py` is a lighter-weight alternative that outputs ~12 flows in a different format. Running `generate_flows.py` standalone WILL truncate flows.json from 84→12 flows. The cron pipeline runs `db_to_json.py`, not `generate_flows.py`. If you see `<30 flows on the live site, `generate_flows.py` was accidentally run — re-run `python3 scripts/db_to_json.py` to restore. The two scripts share no code path; they are independent generators with different data sources.
- **"neutral" direction asymmetry chain (v25.0 June 2026).** When `db_to_json.py` normalizes "neutral" → "inflow" in `compile_flows()`, the `compile_stories()` function at line 140-141 must ALSO normalize capital_flow direction in stories. Additionally, the asymmetry computation loop at ~line 377 skips `direction == "neutral"` — even after normalization, verify this skip is removed or you'll get dozens of null asymmetry scores. The chain: DB has "neutral" → flows.json normalized ✓ but stories.json capital_flow still "neutral" → asymmetry loop skips → null scores. Fix BOTH: (a) normalize cap_flow direction in story compilation, (b) remove the "neutral" skip from asymmetry loop. Full reproduction: `references/neutral-direction-chain.md`. Verify: `curl -sk $SITE/data/stories.json | python3 -c "import json,sys;d=json.load(sys.stdin);all_s=([d.get('lead')] if d.get('lead') else [])+d.get('stories',[]);nulls=sum(1 for s in all_s if s and s.get('asymmetry_score') is None);print(f'{nulls} null asymmetry scores')"` — must return `0 null asymmetry scores`.
- **market_regime.json indicator format — Object.forEach() silent failure (v25.1 June 2026).** `renderMarketRegime()` calls `data.indicators.forEach(...)`. If `market_regime.json` has indicators as a dict `{"money_flow": {...}}` (not an array), `.forEach()` is undefined on plain objects. The `.catch()` handler hides the entire regime section — all 3 cards show `—` with no console error. The fix: use `Object.entries(data.indicators).forEach(([key, ind]) => ...)` and match on key names (`'money_flow'`, `'top_heavy'`, `'bond_fear'`) not `ind.indicator`. Also use `ind.signal` (not `ind.direction`) for the direction value. Verify with: `curl -sk $SITE/app.js | grep -c 'Object.entries(data.indicators)'` must be ≥ 1.
- **Number audit — every visible number must be cross-referenced against source data.** After any deploy, extract all visible numbers from the browser snapshot and verify each one against its source JSON endpoint. The audit found these silent failures: SPX entry showed price ($735) not actual entry ($5,750), BTC stop was stale ($58K vs ATR-computed $63.8K), 6 of 8 live tickers were stale (hardcoded HTML values from days-old market data). Audit methodology: `browser_navigate` → snapshot → extract every number → `curl` data endpoints → diff. If any displayed number differs from source, fix the pipeline or regenerate HTML. `generate_flows.py` reads from `data/stories.json` (richer, 16+ with capital_flow dicts) NOT `site/data/stories.json` (subset, only 6 with CF). After ANY change to data/stories.json, always copy to site/data/ before deploying. Verify with: `diff <(python3 -c "import json;d=json.load(open('data/stories.json'));print(len(d.get('stories',[])))") <(python3 -c "import json;d=json.load(open('site/data/stories.json'));print(len(d.get('stories',[])))")`
- **Dual-domain split-brain**: `pureciclismo.github.io` (GitHub Pages, fast deploy) ≠ `www.lagazzettadikyiv.com` (GCS, slow CDN). Always verify BOTH — GitHub Pages first (confirms commit integrity), then custom domain. If they diverge, the GCS deploy is stale, not the code.
- **⛔ DUAL-GCS-BUCKET DISCONNECT (v27.2 June 2026) — pipeline deploys to wrong bucket.** The pipeline deploys to `gs://lagazzettadikyiv.com/` but the Load Balancer backend bucket may point to `gs://www.lagazzettadikyiv.com/`. Everything appears healthy — `gsutil cat` shows correct files, curls to CDN return 200, but ALL deployed fixes are invisible because the LB serves from a different bucket. The two buckets drift independently; one can be 4+ days stale. Detection: `gcloud compute backend-buckets describe gazzetta-backend --format='value(gcsBucketName)'` — must match the bucket the pipeline writes to. Also verify: `gsutil ls -l gs://lagazzettadikyiv.com/story.html | grep -o '2026-0[0-9]-[0-9]*'` vs `gsutil ls -l gs://www.lagazzettadikyiv.com/story.html | grep -o '2026-0[0-9]-[0-9]*'` — dates must match within 1 hour. Fix: `gcloud compute backend-buckets update gazzetta-backend --gcs-bucket-name=lagazzettadikyiv.com` or sync both buckets. Full reproduction: `references/dual-bucket-disconnect.md`.
- **Flows direction normalization** — `generate_flows.py` must normalize multi-word direction strings from `capital_flow` dicts to simple "inflow"/"outflow". The `normalize_direction()` function handles this. If flows count looks wrong (e.g., 12 total but only 9+3 counted), check for normalization failures.
- **heroStoryCount overwrite bug** — `updateMastheadFlows()` used to overwrite heroStoryCount with `total_flows_tracked` from flows.json (usually 8-12), which is LESS than actual story count. Fixed: story count is now managed exclusively by `updateCumulativeStats()` from DOM.
- **Ghost project copies** — Hermes-agent cron jobs sometimes create stale copies at `~/.hermes/hermes-agent/gazzetta-di-kyiv/`. This path MUST NOT exist. If it does, delete it immediately. If cron jobs reference it, update their prompts and workdir to `/Users/alexstocchi/lagazzettadikyiv`. Check with: `ls ~/.hermes/hermes-agent/gazzetta-di-kyiv/ 2>&1` — should return "No such file"
- **generate_flows.py data source** — Must read from `DATA_SOURCE / "stories.json"` (`data/stories.json`, 16+ stories with CF dicts) NOT `SITE_DATA / "stories.json"` (`site/data/stories.json`, only 6 with CF). If flows are all generic $1B values, the data source is reading the wrong stories file.
- **Hashed-filename deploy pitfall (v25.0 June 2026).** The site loads `app.280e9b5e.js` (hashed) — NOT `app.js`. When deploying a JS fix, you MUST deploy to BOTH the hashed filename AND `app.js`. **Critical trap (v25.10):** deploying only the new hashed JS without the rewritten HTML leaves the browser loading the old cached JS — HTML still references the old hash. Always deploy updated HTML + new hashed JS together. Full reproduction: `references/hashed-asset-deploy-trap.md`.
- **⛔ JS hash mismatch — HTML references hash that doesn't exist on GCS (v27.2 June 2026).** The build pipeline can generate a hash for a DIFFERENT version of the file than what was actually copied. Result: `story.html` references `story-app.58f8edd4.js` but GCS only has `story-app.861d7413.js`. The JS file returns 404 → page stuck on "Loading…" with zero console errors. Detection: extract the hashed filename from HTML with `grep -o 'story-app\\.[a-f0-9]*\\.js' story.html`, then verify it exists on GCS with `gsutil ls gs://BUCKET/story-app.HASH.js`. If missing, copy the existing hashed file to match: `gsutil cp gs://BUCKET/story-app.EXISTING.js gs://BUCKET/story-app.EXPECTED.js`. Also fix the root cause — verify `build_hashed_assets.py` runs AFTER `cp site/story-app.js public/story-app.js` and uses the same file for hashing.\n- **⛔ `build_hashed_assets.py` MISSING from pipeline entirely (v27.2 June 2026).** The script was never called by `deploy_routine.sh` or `cloud_entrypoint.py` — hashing only happened locally on the host. Every pipeline run deployed whatever hashed filenames were in `public/` at Docker build time. If `public/story-app.js` was stale (old version), the hash never updated and the HTML referenced the same old hash forever. Fix: add `build_hashed_assets.py` as Stage 2.1 in `deploy_routine.sh` (between `build_site.py` and `generate_broadcasts.py`). Detection: `grep 'build_hashed' deploy_routine.sh` — must return a match. Also add stale hashed JS cleanup: `find public/ -maxdepth 1 -name '*.????????.js' ! -name 'app.js' ! -name 'i18n.js' ! -name 'sector.js' ! -name 'story-app.js' -delete`. Full pipeline-stage audit: `references/pipeline-stage-audit.md`.
- **SVG CSS-loading failsafe — add explicit width/height to all inline SVGs (v26.11 June 2026).** When CSS is 404 (gsutil auth failure, deleted hash, CDN cache), inline SVGs with only `viewBox` explode to viewport width (caduceus: 1264×2528px). Adding `width="N" height="N"` attributes directly on `<svg>` tags provides a CSS-independent constraint — the SVG renders at correct size even without stylesheets. Apply to ALL masthead SVGs (caduceus, bulavas) and any container-arrow SVGs. After any SVG edit, verify: `JSON.stringify(Array.from(document.querySelectorAll('svg')).slice(0,3).map(s => s.getBoundingClientRect()))` — if caduceus width > 100, CSS isn't loading. Full pattern: `references/hashed-asset-auth-failure-cascade.md`.
- **Hashed-asset auth-failure cascade (v26.11 June 2026).** `build_hashed_assets.py` creates hashed CSS locally + rewrites HTML, but if gsutil has no write auth (wrong GCLOUD_DIR), the hashed file never reaches GCS. Result: CSS 404 on ALL pages — SVGs explode, fonts fall back to Times, gold border vanishes, `currentColor` SVGs go transparent. Detection: `browser_console` → `getComputedStyle()` → SVG rects, `fontFamily`, `borderBottom`. Fix: revert to unhashed `styles.css` + fix GCLOUD_DIR + re-deploy. curl/snapshot verification is blind to this — the HTML loads fine, CSS is the only missing piece. Full reproduction: `references/hashed-asset-auth-failure-cascade.md`.
- **CSS hash → HTML reference chain MUST be complete (v26.2 June 2026, hardened v26.5, procedure v26.7).** → Full numbered deploy procedure: `references/css-hash-deploy-chain.md`
```bash
HASH=$(curl -sk https://www.lagazzettadikyiv.com/ | grep -o 'app\.[a-f0-9]*\.js' | head -1)
$GSDK/gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/app.js gs://www.lagazzettadikyiv.com/$HASH
$GSDK/gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/app.js gs://www.lagazzettadikyiv.com/app.js
```
Deploying only to `app.js` leaves the hashed file stale — real users see the old code. The same applies to `story-app.CC2E0196.js` / `story-app.js`, `i18n.HASH.js`, and `styles.HASH.css`. After deploy, verify the fix landed on the hashed file: `curl -sk "$SITE/$HASH?t=$(date +%s)" | grep -c 'YOUR_FIX_SIGNATURE'` must be ≥ 1.
- **Root vs site/app.js divergence (v24.10)** — The build pipeline does `cp app.js site/app.js` then hashes. If you patch `site/app.js` but forget to patch root `app.js`, the `cp` overwrites your site patches with stale root code. The new hash deploys old logic — hero indicators, trade hooks, and any patched functions silently regress. After patching site/app.js, ALWAYS either (a) patch root app.js with the same change, or (b) reverse-copy: `cp site/app.js app.js` before running `build_hashed_assets.py`. Verify post-deploy with: `cmp -s app.js site/app.js && echo "SYNCED" || echo "DIVERGED — site changes will be lost on next build"`.
- **Commit messages can be fraudulent (v25.2 June 2026).** Never trust a commit message. `git log` may say "Masthead 300% title, container tooltips, nav dropdowns" but the CSS classes may not exist in the deployed file. Always verify with `grep -c 'EXPECTED_CLASS' live_CSS_URL` and `browser_console` to confirm DOM elements render. Commit `3bce90e` claimed 7 changes — 2 were never written to any file. The deploy CSS was 100% stale.\n- **Test gate blocking deploy on non-critical failures (v25.9 June 2026).** When `shipit.sh` aborts at Stage 2.5 with `VERDICT: N TEST(S) FAILED`, the GCS sync (Stage 4) NEVER ran. Options: (a) fix the test failures and re-run `shipit.sh`, or (b) if failures are pre-existing data-quality warnings (drift, scale violations, translation gap), run Stages 3-4 manually: hash assets → RU sync → `gsutil rsync`. Never report "deployed" after seeing test failures — `set -e` means the script exited before GCS upload. Full procedure: `references/ru-sync-gate-subpages.md`.\n- **RU sub-pages serving homepage template (v25.9 June 2026).** When `/ru/stories.html` returns the same HTML as `/ru/`, the ru_sync_gate didn't copy sub-pages. GCS returns 404 for the missing file and falls back to `ru/index.html`. The file list in shipit.sh §3.1 must include all sub-pages: `stories.html flows.html event_horizon.html flow-nodes.html signal.html trades.html track.html privacy.html`. Fix: expand the for-loop file list + add `<base href="/">` + `../` path fixes. Full reproduction: `references/ru-sync-gate-subpages.md`.\n- **RU page orphaned from local repo (v25.2 June 2026).** `~/projects/gazzetta-di-kyiv/ru/` may not exist — the RU page was built and deployed directly to GCS without being committed to the repo. Before editing the RU page: `mkdir -p ru && curl -s 'https://www.lagazzettadikyiv.com/ru/' > ru/index.html`. After fixing, commit `ru/index.html` to the repo so it's tracked. The same applies to any sub-page deployed ad-hoc.\n- **Null capital_flow fields → \"undefined\" in DOM (v25.4 June 2026).** When stories have `capital_flow.claim = null`, `amount_b = null`, or `confidence = null`, the JS card renderer (`cfClaim`, `cfHint` template literals) outputs literal \"undefined\" strings into the DOM. 37 stories in production had null claim + null confidence, producing cards like `undefined — projected undefined change at undefined confidence`. Detection: `browser_console` → `JSON.stringify({undefined: (document.body.innerHTML.match(/undefined/g)||[]).length})` — must return 0. Fix: `safeCF()` normalizer function that fills defaults for all null/undefined fields before rendering. Full pattern: `references/safecf-pattern.md`. Backfill: update `capital_flow_raw` in gazzetta.db with `json.dumps()` of normalized dict.\n- **Browser snapshot ≠ visual truth (v24.0)** — The accessibility-tree snapshot only captures static HTML. JS-populated pages (story detail, flows, hero indicators) appear as 5-13 element skeletons even when rendering 30KB+ of content. The story detail page at `story.html?id=...` showed 5 elements in snapshot but had full intel-report articles with THEY SAY/REALITY/CAPITAL FLOW blocks. Always supplement snapshots with `browser_console` checks: `bodyLen`, `hasMain`, `mainHTML.length`. If `bodyLen > 5000`, the page IS rendering — the snapshot is a false negative.
- **Truncated JS init() detection (v24.0)** — If a page shows a loading spinner that never resolves and the init function ends with a simple statement like `const prices = await fetchPrices();` at the file's last line, the rendering code was truncated. The function fetches data but never calls render functions, hides the loading spinner, or shows content. Check: `tail -5 site/PAGE.html` — if the last line is mid-function without a closing brace or rendering call, the file is incomplete. Fix: add `loading.style.display='none'; content.style.display='block';` followed by render calls. event_horizon.html was found in this state at line 1209/1209. Full reproduction: `references/truncated-init-missing-script.md`
- **Closure variable not passed to extracted function (v27.2 June 2026)** — When a helper function is extracted from a parent that defines closure-scoped variables (like `t` for i18n), the extracted function must receive those variables as parameters. Symptom: page stuck on "Loading…" with `ReferenceError: t is not defined` at the helper function. The error is swallowed if `init()` has an empty `.catch()`. Detection: for any function that uses template literals with closure variables, verify the function signature includes all referenced variables. Full reproduction: `references/js-scope-bug-closure-variable.md`.
- **Story order reversal from afterbegin + forEach (v25.10 June 2026).** `insertAdjacentHTML('afterbegin', html)` PREPENDS each element. When `all.forEach(s => appendStoryCard(s))` iterates forward through stories.json (newest→oldest), the last array item (oldest) gets prepended last → appears at TOP. The homepage teasers use `innerHTML = items.map().join('')` which preserves forward order. Result: stories page shows oldest-first, homepage teasers show newest-first — completely different lists from the same STORIES_DATA. Fix: reverse the iteration (`[...all].reverse().forEach(...)`) so `afterbegin` produces correct newest-first order. Do NOT change `afterbegin` to `beforeend` — poll updates (`pollLivingStories()`) rely on `afterbegin` to prepend breaking news at the top. Full reproduction: `references/story-order-reversal.md`.
- **⛔ VM governor overwrites CDN frontend with old build_frontend.py (v32.0 June 2026).** When you deploy a patched `build_frontend.py` locally and build HTML, but the VM governor runs `build_frontend.py` from the VM's copy (which is the OLD version), the governor cycle overwrites all your frontend fixes on CDN. Symptoms: share buttons revert to broken JS-leak state, `FEED_SOURCE:` reappears, font sizes regress. This happened after deploying Groups 1-3 frontend fixes — the next governor cycle rebuilt HTML with the old VM copy and pushed it to GCS, silently reverting everything. **Fix: after ANY build_frontend.py change, SCP the patched file to the VM AND the CDN.** Verify with: `md5 -q local/scripts/build_frontend.py` vs `ssh gazzetta-prod 'md5sum /opt/gazzetta-di-kyiv/scripts/build_frontend.py'` — must match. Same applies to `contradiction_synthesizer.py` and any script the governor invokes.
- **Local data divergence from CDN data (v32.0 June 2026).** `build_frontend.py` reads from `DATA / "stories.json"` which is `data/stories.json` (local). The pipeline writes fresh data to `public/data/stories.json` on the VM, which gets deployed to GCS. The local `data/stories.json` can be DAYS stale. Symptoms: CDN shows 401 stories with 394 feed_source, local build shows 191 stories with 2 feed_source. You report a data pipeline bug that doesn't exist. **Fix: before local build, copy fresh data from VM:** `scp gazzetta-prod:/opt/gazzetta-di-kyiv/public/data/stories.json public/data/ && cp public/data/stories.json data/stories.json`. Then rebuild. Verify story count matches CDN before making claims about data quality.
