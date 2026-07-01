# Systematic Data Pipeline Audit Methodology

Discovered June 2026 after user complained site was "static." The standard cron status check (all 17 `last_status=ok`) gave a false sense of health while the site hadn't produced new content in hours.

## The Problem

All 17 cron jobs reported `last_status=ok`. But the site was frozen — same stories, same flows, regenerated identically every cycle. The gaps:

1. **Phantom scripts** — 6 of 7 scripts referenced in cron prompts didn't exist on disk. LLM agents told to `python3 scripts/build_site.py` fabricated `{"ok":true}` instead of surfacing FileNotFoundError.
2. **Disconnected pipeline** — Telegram monitor collected real intel (Iran strikes Bahrain, BTC crash, SpaceX IPO) every 30m but saved to `telegram_intel/latest.json` — never fed into stories.json.
3. **Identical regeneration** — `generate_flows.py` parsed the same 18 stories every hour, producing the same 11-12 flows with identical confidence scores.
4. **No freshness indicators** — Stories had no timestamps, no "breaking" badges, no way to tell if content was minutes or days old.

## The Audit Method

### Phase 1: File Timestamp Audit
```bash
for f in data/*.json data/*.md; do
  name=$(basename "$f")
  ts=$(stat -f '%m' "$f")
  echo "$name|$ts"
done
```
**Red flag:** All 15+ files with identical timestamp = bulk copy, not genuine generation. Individual files should have distinct ages.

### Phase 2: Script Existence Audit
```bash
# Extract all script references from cron prompts
python3 -c "import json,re; j=json.load(open('~/.hermes/cron/jobs.json'));
scripts=set(); [scripts.update(re.findall(r'scripts/\S+\.py', x.get('prompt',''))) for x in j['jobs']];
[print(s) for s in sorted(scripts)]"

# Verify each exists
for s in $SCRIPTS; do test -f "$s" && echo "✓ $s" || echo "✗ MISSING: $s"; done
```
**Red flag:** Any script referenced but not on disk = cron output is fabricated.

### Phase 3: Cron Actual Output Audit
Don't check `last_status` — read the actual output files:
```bash
for d in ~/.hermes/cron/output/*/; do
  id=$(basename "$d")
  latest=$(ls -t "$d" | head -1)
  echo "=== $id : $latest ==="
  grep -A10 'Response' "$d/$latest" | head -15
done
```
**Red flags:**
- Empty Response section (agent produced no output)
- Generic `{"ok": true}` without actual data
- Claims of "added 1 story" but stories.json hasn't changed

### Phase 4: Data Flow Trace
Trace every data source to its destination:
```
telegram_monitor → telegram_intel/latest.json → ??? → stories.json → flows.json → deploy
                                                    ↑
                                              MISSING LINK
```
**Red flag:** Any data source with no consumer, or any consumer reading stale/identical input.

### Phase 5: Live vs Local Comparison
```bash
# Local
python3 -c "import json; s=json.load(open('data/stories.json')); print(len(s['stories']))"

# Live
curl -s https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "import json,sys; s=json.load(sys.stdin); print(len(s['stories']))"
```
**Red flag:** Mismatch = deploy stale or broken.

## The Fix Pattern

When the pipeline is disconnected:

1. **Create the bridge** — script that reads producer output → converts format → writes to consumer input
2. **Chain it** — single shell script: bridge → generate → build (idempotent)
3. **Convert to no_agent** — change cron from LLM-agent to `no_agent=true, script=<chain>`. No more hallucination.
4. **Verify end-to-end** — run chain, check counts increased, verify live site updated

## Anti-Patterns Caught

- **Trusting `last_status=ok`** — means the cron scheduler ran, not that it produced valid output
- **LLM agents as script runners** — LLMs told to execute Python scripts will fabricate output when scripts don't exist
- **Isolated crons** — each doing their own thing, nobody checking if data actually flows between them
- **Missing timestamps** — stories with `generated: ?` are silently broken
- **Identical regeneration** — same input → same output every cycle is functionally static
