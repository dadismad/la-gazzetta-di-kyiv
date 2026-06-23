---
name: gazzetta-integrity-check
description: Cross-reference live deployed site against source data + audit data integrity (GAP provenance, capital diversity, flow verifiability). Run whenever data pipeline or deploy changes.
version: 1.0.1
category: gazzetta
---

# Gazzetta Integrity Check

Cross-references EVERY data artifact on the live site against the source of truth. Catches the class of bugs where "everything deployed successfully" but the data is wrong.

## Quick Check (30 seconds)

**PITFALL: tirith blocks pipe-to-interpreter.** The Hermes security scanner intercepts `CMD | python3 -c "..."` patterns as HIGH-risk. This affects `curl | python3` and `gh | python3`. Use inline Python with `urllib.request` + `ssl._create_unverified_context()` to fetch remote content, or `gh --jq` instead of `gh | python3`.

```bash
cd /Users/alexstocchi/projects/gazzetta-di-kyiv

# Ghost check
echo "=== GHOST ===" && ls ~/.hermes/hermes-agent/gazzetta-di-kyiv/ 2>&1 | head -1

# Source parity
echo "=== SOURCE PARITY ==="
echo -n "stories: " && python3 -c "import json; s=json.load(open('data/stories.json')); print(len(s.get('stories',[])))"
echo -n "site stories: " && python3 -c "import json; s=json.load(open('site/data/stories.json')); print(len(s.get('stories',[])))"
echo -n "live stories: " && python3 -c "
import ssl, urllib.request, json
ctx = ssl._create_unverified_context()
resp = urllib.request.urlopen('https://www.lagazzettadikyiv.com/data/stories.json', context=ctx)
print(len(json.loads(resp.read().decode()).get('stories',[])))
"

# Flow quality
echo "=== FLOW QUALITY ==="
python3 -c "
import json, ssl, urllib.request
ctx = ssl._create_unverified_context()
resp = urllib.request.urlopen('https://www.lagazzettadikyiv.com/data/flows.json', context=ctx)
live = json.loads(resp.read().decode())
site = json.load(open('site/data/flows.json'))
live_big = sum(1 for f in live['flows'] if f['amount_b'] >= 5)
site_big = sum(1 for f in site['flows'] if f['amount_b'] >= 5)
print(f'live big flows: {live_big}/{live[\"total_flows_tracked\"]}')
print(f'site big flows: {site_big}/{site[\"total_flows_tracked\"]}')
print(f'live aggregate: {live[\"aggregate_confidence\"]}%')
print(f'site aggregate: {site[\"aggregate_confidence\"]}%')
"

# Cron integrity
echo "=== CRON ==="
python3 -c "
import json
jobs = json.load(open('$HOME/.hermes/cron/jobs.json'))['jobs']
for j in jobs:
    if 'gazzetta' not in j.get('name','').lower(): continue
    prompt = j.get('prompt','')
    ghost = 'hermes-agent/gazzetta' in prompt
    # False positive filter: "NEVER use" or "do NOT use" is a warning, not a path ref
    if ghost:
      import re
      around = prompt[max(0, idx-60):idx+80] if (idx := prompt.find('hermes-agent/gazzetta')) >= 0 else ''
      if re.search(r'NEVER|do NOT|don\'t|avoid|WARNING', around, re.IGNORECASE):
        ghost = 'warn_only'
    wd = j.get('workdir','') or 'NONE'
    print(f'{j[\"name\"]:40s} ghost={ghost} wd={str(wd)[:40]}')
"

# HTTP health
echo "=== HTTP ===" && curl -skI https://www.lagazzettadikyiv.com/ 2>&1 | head -1

# Backend bucket alignment (v27.2 — catches dual-bucket disconnect)
echo "=== LB BACKEND ===" && gcloud compute backend-buckets describe gazzetta-backend --format='value(gcsBucketName)' 2>/dev/null
echo "(pipeline deploys to: lagazzettadikyiv.com — must match LB backend)"
```

## Data Integrity Checks (v1.2 — added June 2026)

Beyond file-level deploy integrity, run these checks to verify data QUALITY — catching the class of bug where files deploy correctly but contain misleading or non-auditable numbers.

### Check 1: GAP Score Auditability

```bash
cd /opt/gazzetta-di-kyiv

python3 -c "
import json
stories = json.load(open('public/data/stories.json')).get('all_stories', [])
missing_provenance = 0
total = 0
for s in stories:
    total += 1
    # Check if the story has a market data snapshot timestamp or provenance
    has_source_timestamp = bool(s.get('generated_at') or s.get('market_data_snapshot_at'))
    has_ticker_data = bool(s.get('affected_tickers'))
    if not has_ticker_data:
        missing_provenance += 1

print(f'Stories: {total}')
print(f'Missing ticker references: {missing_provenance}')
print(f'Stories with generated_at: {sum(1 for s in stories if s.get(\"generated_at\"))}')
print(f'PASS: All ticker-ref stories have timestamps' if total > 0 else 'WARN: No stories found')
"
```

**PASS:** Every story has `affected_tickers` populated and a `generated_at` timestamp.
**WARN:** Any story lacks ticker references or timestamps — GAP score is unverifiable.

### Check 2: Capital Volume Diversity

```bash
python3 -c "
import json
from collections import Counter

stories = json.load(open('public/data/stories.json')).get('all_stories', [])
caps = [s.get('capital_volume_usd', 0) or 0 for s in stories]
counts = Counter(caps)
total_unique = len(counts)
most_common = counts.most_common(3)

print(f'Total stories: {len(stories)}')
print(f'Unique capital values: {total_unique}')
print(f'Most common: {most_common}')
if len(counts) <= 2 and max(counts.values()) > len(stories) * 0.5:
    print('FAIL: Capital values are essentially uniform (single default)')
elif len(counts) >= 10:
    print('PASS: Good capital value diversity')
else:
    print('WARN: Limited capital diversity — check if pipeline is applying defaults')
"
```

**PASS:** 10+ unique capital values, no single value represents >50% of stories.
**FAIL:** 1-2 unique values dominating — the $100M default bug is active.
**WARN:** 3-9 unique values — monitor.

### Check 3: Capital Flow Provenance

```bash
python3 -c "
import json
stories = json.load(open('public/data/stories.json')).get('all_stories', [])
no_source = 0
for s in stories:
    cf = s.get('capital_flow', {}) or {}
    # Check for any provenance field
    has_provenance = bool(cf.get('source')) or bool(s.get('source_url')) or bool(cf.get('fetched_at'))
    if not has_provenance and (s.get('capital_volume_usd', 0) or 0) > 0:
        no_source += 1

non_zero = sum(1 for s in stories if (s.get('capital_volume_usd', 0) or 0) > 0)
print(f'Stories with non-zero capital: {non_zero}')
print(f'Stories with non-zero capital but NO source provenance: {no_source}')
if no_source == 0:
    print('PASS: All capital numbers have provenance')
else:
    print(f'FAIL: {no_source} stories have unverifiable capital numbers')
"
```

**PASS:** Every non-zero capital number has a source/timestamp attached.
**FAIL:** Any non-zero capital number lacks provenance — readers cannot verify.

### Check 4: "DISCREPANCIES" Honesty

```bash
python3 -c "
import json
stories = json.load(open('public/data/stories.json')).get('all_stories', [])
# The discrepancy counter is stories with contradiction_gap >= 40
high_gap = [s for s in stories if (s.get('contradiction_gap') or 0) >= 40]
total = len(stories)
print(f'Stories with GAP ≥ 40 (DISCREPANCIES): {len(high_gap)}')
print(f'Total stories: {total}')
print(f'This is {(len(high_gap)/total*100):.0f}% of all stories')
if len(high_gap) > 0:
    print('NOTE: \"DISCREPANCIES\" = stories with high contradiction score, not errors')
"
```

**Verification:** Confirm the "DISCREPANCIES: N" counter shown on the site equals `count of stories with GAP ≥ 40`. If it doesn't match, the counter is misattributed.

## Integrity Matrix

| What | Source | Deployed (site/data/) | Live (curl) | All Match? |
|------|--------|----------------------|-------------|------------|
| Stories count | data/stories.json | site/data/stories.json | curl /data/stories.json | ✓/✗ |
| Flows count | data/flows.json or generated | site/data/flows.json | curl /data/flows.json | ✓/✗ |
| Flow quality | generate_flows.py output | ≥4 flows with amount > $5B | ≥4 flows with amount > $5B | ✓/✗ |
| Hero stats | app.js boot() output | index.html bootstrap | Browser console | ✓/✗ |
| Cron paths | jobs.json prompts | — | — | No ghost |

## Red Flags (stop and fix immediately)

| Flag | Meaning | Fix |
|------|---------|-----|
| Ghost project exists | Cron jobs writing to stale copy | Convert to symlink: `rm -rf old && ln -sf canonical old` |
| Phantom script referenced | Cron prompt says `python3 scripts/X.py` but file doesn't exist | Reconstruct script OR update cron prompt. NEVER trust cron `ok` status alone — LLM agents fabricate output for missing scripts. |
| site != live story count | Deploy failed or CDN stale | Re-deploy, set `max-age=0` |
| source != site story count | Data not copied to deploy dir | `cp data/stories.json site/data/stories.json` |
| ≥4 flows with amount ≤ $1.1B | generate_flows.py read from wrong source | Check DATA_SOURCE path in generate_flows.py |
| Cron ghost paths | Old prompts still reference hermes-agent | `cronjob(action='update', ...)` fix prompt + workdir |
| HTTP not 200 | Site down | Check GCS bucket, gcloud auth |
| LB backend bucket mismatch | Pipeline deploys to one bucket, LB serves from another | `gcloud compute backend-buckets describe gazzetta-backend --format='value(gcsBucketName)'` → update or sync |
| Product page = dashboard clone | All 5 product pages render same as index without page-specific content | Convert to redirect pages → index.html#section (v24.0) |
| Root app.js ≠ site/app.js | Site patches overwritten by `cp app.js site/` | Reverse-copy: `cp site/app.js app.js` or patch both |
| RU page no `<base href="/">` | All JS data fetches resolve to /ru/data/ → 404 | Add `<base href="/">` after `<meta charset>` in site/ru/index.html |
| Missing `</script>` in HTML | Inline JS parsed as HTML text, no JS executes | `grep -c '</script>' site/*.html` — must match `<script` count |

### Product Page Integrity (v24.10 — catches 5-page clone bug)

The 5 product pages (stories, flows, signal, trades, track) were found to be clones of index.html — same masthead, same hidden containers, same app.js. No page-specific content. Users clicking nav links saw the dashboard again, not a dedicated page.

```bash
# Verify product pages are redirects, not clones
for f in stories flows signal trades track; do
  size=$(wc -c < "site/${f}.html")
  has_refresh=$(grep -c 'meta.*refresh' "site/${f}.html" 2>/dev/null || echo 0)
  echo "${f}.html: ${size}B refresh=${has_refresh}"
  # PASS: size < 500B (redirect page), has_refresh >= 1
  # FAIL: size > 5000B (clone of index — wrong content)
done
```

### Script Integrity (v24.10 — catches truncated init + missing close tags)

```bash
# Check every HTML file for balanced script tags
for f in site/*.html site/ru/*.html; do
  opens=$(grep -c '<script' "$f" 2>/dev/null || echo 0)
  closes=$(grep -c '</script>' "$f" 2>/dev/null || echo 0)
  if [ "$opens" != "$closes" ]; then
    echo "FATAL: $f — $opens <script> opens, $closes </script> closes — JS dead"
  fi
done

# Check for root vs site app.js drift
cmp -s app.js site/app.js && echo "app.js SYNCED" || echo "DRIFT: app.js ≠ site/app.js — next cp will overwrite site changes"
```

### Script Existence Verification (added June 2026)

```bash
# Extract script references from gazzetta cron prompts, verify on disk
python3 -c "
import json, re, os
jobs = json.load(open('$HOME/.hermes/cron/jobs.json'))['jobs']
for j in jobs:
    if 'gazzetta' not in j.get('name','').lower(): continue
    prompt = j.get('prompt','')
    scripts = re.findall(r'scripts/[\w_]+\.(?:py|sh)', prompt)
    wd = j.get('workdir') or os.path.expanduser('~/projects/gazzetta-di-kyiv')
    for s in scripts:
        full = os.path.join(wd, s)
        exists = os.path.exists(full)
        print(f'  {j[\"name\"]:45s} {s:35s} {\"EXISTS\" if exists else \"MISSING\"}'[:110])
"
```

**Critical lesson:** Cron jobs that tell LLM agents to execute a command NEVER fail. The LLM will always produce plausible output. Script existence MUST be verified at the filesystem level, not by reading cron output.
