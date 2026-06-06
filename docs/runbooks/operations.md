# Operations Runbook

**Standard operating procedures for Gazzetta di Kyiv.**

---

## INCIDENT RESPONSE

### P0: Site Down / Deploy Failing

1. **Check deploy status**: `tail ~/.hermes/cron/output/f9a24ed64aa5/$(ls -t ~/.hermes/cron/output/f9a24ed64aa5/ | head -1)`
2. **Manual deploy**: `bash ~/.hermes/scripts/gazzetta_deploy_to_gcs.sh`
3. **Check gcloud auth**: `CLOUDSDK_CONFIG=/Users/alexstocchi/.config/gcloud ~/lagazzettadikyiv/google-cloud-sdk/bin/gcloud auth list`
4. **Check GCS bucket**: `curl -sI https://www.lagazzettadikyiv.com/`
5. **If all fails**: Check network, disk space (`df -h`), GCS billing

### P1: Pipeline Chain Failing

1. **Check last chain output**: `ls -t ~/.hermes/cron/output/51c1bb776729/ | head -1`
2. **Run manually**: `cd ~/projects/gazzetta-di-kyiv && bash scripts/pipeline_chain.sh`
3. **Check which step fails**: Each step prints output. Find the error.
4. **Common fixes**:
   - `intel_to_stories.py` fails: Check `data/telegram_intel/latest.json` exists
   - `decay_stories.py` fails: Check `data/stories.json` is valid JSON
   - `validate_stories.py` fails: Check stories have required fields
   - `generate_flows.py` fails: Check stories have `capital_flow` dicts
   - `build_site.py` fails: Check `data/` directory has required files

### P2: Data Stale (>4h no updates)

1. **Check telegram intel freshness**: `stat -f '%m' ~/projects/gazzetta-di-kyiv/data/telegram_intel/latest.json`
2. **Run pipeline manually**: `cd ~/projects/gazzetta-di-kyiv && bash scripts/pipeline_chain.sh`
3. **If intel is stale**: Check telegram monitor cron output
4. **Force intel refresh**: Trigger `gazzetta-telegram-monitor` cron manually

### P3: Individual Cron Failure

1. **Check cron status**: `python3 -c "import json; j=json.load(open('$HOME/.hermes/cron/jobs.json')); [print(x['name'], x['last_status'], x.get('last_error','')) for x in j['jobs']]"`
2. **Run manually**: Use `hermes cron run <job_id>`
3. **Check output**: `~/.hermes/cron/output/<job_id>/`

---

## ROUTINE OPERATIONS

### Daily Health Check

```bash
# Run every morning
cd ~/projects/gazzetta-di-kyiv

# 1. Pipeline status
echo "=== PIPELINE ==="
python3 -c "
import json
f = json.load(open('data/flows.json'))
s = json.load(open('data/stories.json'))
print(f'Stories: {len(s.get(\"stories\",[]))} | Flows: {len(f.get(\"flows\",[]))} | Conf: {f.get(\"aggregate_confidence\")}%')
"

# 2. Site status
echo "=== SITE ==="
curl -sI https://www.lagazzettadikyiv.com/ | head -1

# 3. Deploy status
echo "=== DEPLOY ==="
ls -t ~/.hermes/cron/output/f9a24ed64aa5/ | head -1

# 4. Cron health
echo "=== CRON ==="
python3 -c "
import json
j = json.load(open('$HOME/.hermes/cron/jobs.json'))
for x in j['jobs']:
    status = x.get('last_status','?')
    name = x['name']
    print(f'  {status:5s} {name}')
"
```

### Weekly Strategic Review

1. **Review KPIs** against targets in `docs/strategy.md`
2. **Check pillar coverage**: are all 6 pillars represented?
3. **Review orphan skills**: any not used in 2 weeks → consider archiving
4. **Check content quality**: spot-check 3 random stories for contradiction depth
5. **Review pipeline performance**: any failures > 4h?

### Monthly System Audit

1. **Run 3-persona focus group**: Systems Architect, Data Engineer, SRE
2. **Review against GOS.md**: any framework drift?
3. **Update process registry**: any new processes? any removed?
4. **Clean up**: archive old data, remove dead code, update docs
5. **Push to GitHub**: ensure version control is current

---

## COMMON TASKS

### Add a New Data Source

1. Edit `data/config/data_sources_v2.json`
2. Add source entry with: `id`, `name`, `type`, `priority`, `frequency`, `queries`, `pillars`
3. Update `data/source_registry_ranked.json` if needed
4. Test: run source monitor cron manually

### Add a New Paradigm Pillar

1. Add pillar definition to `docs/strategy.md`
2. Add to `PILLAR_KEYWORDS` in `scripts/intel_to_stories.py`
3. Add to `pillar_definitions` in `data/config/data_sources_v2.json`
4. Add web_search sources for the new pillar
5. Run pipeline to verify pillar detection

### Deploy a Site Update

1. Make changes to `site/` files
2. Test locally: `open site/index.html` in browser
3. Run `python3 scripts/build_site.py`
4. Deploy: `bash ~/.hermes/scripts/gazzetta_deploy_to_gcs.sh`
5. Verify: `curl -sI https://www.lagazzettadikyiv.com/`

### Create a New Skill

1. Create directory: `~/.hermes/skills/gazzetta/<skill-name>/`
2. Create `SKILL.md` with YAML frontmatter: name, description, version, category
3. Register in GOS.md if operational
4. Wire into appropriate cron job if automated

---

## EMERGENCY CONTACTS

| Role | Contact |
|------|---------|
| **Operator** | Alexander (Telegram: Stocchi Labs) |
| **Infrastructure** | GCS: `pureciclismo@gmail.com` |
| **Domain** | Google Domains: `lagazzettadikyiv.com` |
| **LLM Provider** | DeepSeek API (primary), fallback: none configured |

---

## FILE RECOVERY

### If project directory is deleted:
```bash
# Recover from GCS (last deploy)
mkdir -p ~/projects/gazzetta-di-kyiv/site
gsutil -m cp -r gs://www.lagazzettadikyiv.com/* ~/projects/gazzetta-di-kyiv/site/

# Recover scripts from hermes
cp ~/.hermes/scripts/gazzetta_*.sh ~/projects/gazzetta-di-kyiv/scripts/
cp ~/.hermes/scripts/gazzetta_*.py ~/projects/gazzetta-di-kyiv/scripts/

# Rebuild data
cd ~/projects/gazzetta-di-kyiv
bash scripts/pipeline_chain.sh
```

### If GCS bucket is deleted:
```bash
# Recreate bucket
gsutil mb gs://www.lagazzettadikyiv.com

# Redeploy from local
bash ~/.hermes/scripts/gazzetta_deploy_to_gcs.sh
```
