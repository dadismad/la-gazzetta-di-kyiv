# Cron Job Recovery Procedure

**Date:** June 11, 2026  
**Trigger:** Scheduler restart wiped all 12 Gazzetta cron jobs from `~/.hermes/cron/jobs.json`

## Symptoms

- `hermes cron status` shows: `✓ Gateway is running — cron jobs will fire automatically` + `No active jobs`
- `cat ~/.hermes/cron/jobs.json | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('jobs',[])))"` → `0`
- Site frozen — `stories.json` `generated_at` timestamp is hours old
- `ps aux | grep hermes` shows gateway PID still alive
- Script files survive at `~/.hermes/scripts/gazzetta_*`

## Recovery Steps

### 1. Verify scripts exist
```bash
ls ~/.hermes/scripts/gazzetta_product_factory.sh
ls ~/.hermes/scripts/gazzetta_health_check.sh
ls ~/.hermes/scripts/gazzetta_pipeline_chain.sh
```

### 2. Recreate critical cron jobs

**Product Factory (most critical — unified pipeline):**
```
cronjob(action='create', name='gazzetta-product-factory', schedule='every 60m',
  script='gazzetta_product_factory.sh', no_agent=true,
  workdir='/Users/alexstocchi/projects/gazzetta-di-kyiv', deliver='origin')
```

**Health Check:**
```
cronjob(action='create', name='gazzetta-health-check', schedule='every 30m',
  script='gazzetta_health_check.sh', no_agent=true,
  workdir='/Users/alexstocchi/projects/gazzetta-di-kyiv', deliver='origin')
```

**CEO Overseer:**
```
cronjob(action='create', name='gazzetta-ceo-overseer', schedule='every 15m',
  skills=['gazzetta-ceo-overseer'], model={provider:'deepseek', model:'deepseek-v4-flash'},
  prompt='Load skill gazzetta-ceo-overseer. Run the CEO oversight cycle...',
  workdir='/Users/alexstocchi/projects/gazzetta-di-kyiv', deliver='origin')
```

**Market Data:**
```
cronjob(action='create', name='gazzetta-market-data', schedule='every 6h',
  script='gazzetta_pipeline_chain.sh', no_agent=true,
  workdir='/Users/alexstocchi/projects/gazzetta-di-kyiv', deliver='origin')
```

**Daily Session Review:**
```
cronjob(action='create', name='daily-session-review', schedule='0 22 * * *',
  skills=['daily-session-review'], model={provider:'deepseek', model:'deepseek-v4-pro'},
  prompt='Run the daily session review workflow...',
  deliver='origin')
```

### 3. Trigger immediate pipeline run
```bash
# Manual run to freshen the site NOW (don't wait for next cron tick)
cd ~/projects/gazzetta-di-kyiv && bash ~/.hermes/scripts/gazzetta_product_factory.sh
```

### 4. Verify recovery
```bash
hermes cron status  # Should show 5+ active jobs
curl -s https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "import sys,json; print(json.load(sys.stdin)['generated_at'])"
```

## Post-Recovery Checklist

- [ ] All product pages return HTTP 200: homepage, /ru/, /stories.html, /flows.html, /signal.html, /trades.html, /track.html
- [ ] `data/stories.json` `generated_at` is <1h old
- [ ] `data/market_regime.json` returns 200 (not 404)
- [ ] `site/ru/index.html` exists (nuclear clean deletes it)
- [ ] Redirect stubs not present in `site/` (product pages >1000 bytes)
- [ ] No `date -Iseconds` errors in cron scripts (macOS incompatibility)
- [ ] Deploy report on GCS shows current timestamp

## Prevention

- The wipe occurred during a scheduler restart — jobs.json was cleared but the gateway PID survived
- No known prevention other than: keep the knowledge base's cron job list current so recovery is fast
- Consider exporting a backup: `cp ~/.hermes/cron/jobs.json ~/.hermes/cron/jobs.json.bak` periodically
