# P0 Data Engine Fix Protocol (June 2026)

## When to use
When the pipeline runs without errors but the live site shows flat/uniform data — all GAP scores identical, all capital volumes identical, or story counts mismatched.

## Diagnostic sequence

### Step 1: Verify the deploy actually reaches GCS
```bash
# On VM, check GCS timestamp vs last governor cycle
gsutil ls -la gs://www.lagazzettadikyiv.com/index.html
```
If timestamp doesn't match last cycle, deploy is failing silently. Root cause: `gazzetta` systemd user has no gcloud credentials. Fix: `sudo` prefix on deploy command.

### Step 2: Verify DEEPSEEK_API_KEY reaches subprocesses
```bash
# Check governor's run_cmd() env dict
grep -A3 "subprocess.run" /opt/gazzetta-di-kyiv/scripts/governor.py
```
Must contain `"DEEPSEEK_API_KEY": DEEPSEEK_KEY or ""`. If missing, synthesis fails with "key not set."

### Step 3: Audit governor STEPS array
```bash
python3 -c "from governor import STEPS; [print(s[0]) for s in STEPS]"
```
10 steps required: ingestion → market_data → synthesis → classify → calc_capital → gen_flows → build_frontend → test_platform → telegram_post → deploy. If classify/calc_capital missing, add them.

### Step 4: Check path consistency across scripts
```bash
grep -n "public/data/stories.json\|data/stories.json" /opt/gazzetta-di-kyiv/scripts/*.py
```
Synthesis writes to `public/data/stories.json`. Classify and calc_capital must read from the SAME path. If they point to `data/stories.json`, they read a different (empty/stale) file.

### Step 5: Verify capital volume is not LLM-fabricated
```bash
python3 -c "
import json
with open('/opt/gazzetta-di-kyiv/public/data/stories.json') as f:
    d = json.load(f)
caps = [s.get('capital_volume_usd',0) for s in d.get('all_stories',[])]
unique = len(set(caps))
print(f'{len(caps)} stories, {unique} unique capital values')
if unique <= 3 and len(caps) > 10:
    print('WARNING: capital values are uniform — LLM hallucination likely')
"
```
If unique ≤ 3 across >10 stories, the assembly logic is using LLM fallback. Check `contradiction_synthesizer.py` line: `capital_volume_usd = int(computed_aum) if computed_aum > 0 else 0` — must NOT include LLM fallback.

### Step 6: Check GAP score distribution for flatness
```bash
python3 -c "
import json
from collections import Counter
with open('/opt/gazzetta-di-kyiv/public/data/stories.json') as f:
    d = json.load(f)
gaps = Counter(s.get('contradiction_gap',0) for s in d.get('all_stories',[]))
print('GAP distribution:')
for gap, cnt in gaps.most_common(5):
    print(f'  {gap}: {cnt}')
"
```
If >50% of stories share a single GAP value, the numeric anchoring prompt is not effective. Check `contradiction_synthesizer.py` SYSTEM_PROMPT for the numeric anchoring formula: `GAP = floor(10 × sum of absolute percentage moves of all contradictory tickers)`.

## Quick fix reference

| Symptom | Root Cause | Fix Location |
|---------|-----------|-------------|
| Deploy "OK" but stale site | gcloud auth missing | governor.py deploy step: add `sudo` |
| Synthesis "key not set" | DEEPSEEK_API_KEY not in env | governor.py run_cmd(): add to env dict |
| All capital_at_stake = 0 | calc_capital.py not in STEPS | governor.py STEPS array: add step |
| All GAP = 15 | Prompt lacks numeric anchoring | contradiction_synthesizer.py SYSTEM_PROMPT |
| All capital = $100M | LLM fallback in assembly | contradiction_synthesizer.py line 416 |
| Classify fails on narratives.json | Path mismatch | classify_stories.py DATA_DIR |
| Capital from wrong path | public/data/ vs data/ mismatch | calc_capital.py STORIES_FILE path |
