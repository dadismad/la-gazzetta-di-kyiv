# Ghost Reversion: Detection & Recovery

## What happened (June 6, 2026)

A ghost project at `~/.hermes/hermes-agent/gazzetta-di-kyiv/` (108MB) was created by cron jobs ignoring their `workdir` setting. The ghost had its own `.git` repo. Cron jobs committed to the ghost, then `git push origin main` — overwriting the real project's git history with older file versions.

**Timeline of damage:**
1. May 26: Ghost project created (earliest file timestamps)
2. June 5: `gazzetta-continuous-source-monitor` runs from ghost, pushes commit `dfc74db` that reverts index.html to DM Serif Display font + fox emblem
3. June 5: `gazzetta-continuous-capital-flows` writes generic flows to ghost's `site/data/flows.json`, pushes — live site shows all $1B flows
4. June 5: `gazzetta-telegram-monitor` writes intel to ghost's `data/telegram_intel/`
5. June 5-6: git conflicts emerge as ghost commits collide with real project commits (`UU site/data/stories.json`)

**Root cause:** Cron job prompts referenced absolute paths including `hermes-agent/gazzetta-di-kyiv`. Even with workdir correctly set, agents default to paths in their prompts.

## Detection

### Quick check (5 seconds)
```bash
# Ghost presence
ls ~/.hermes/hermes-agent/gazzetta-di-kyiv/ 2>&1
# Must: "No such file or directory"

# Font reversion
curl -sk https://www.lagazzettadikyiv.com/ | grep -o "Playfair" | head -1
# Must: "Playfair" (NOT "DM Serif")

# Emblem reversion
curl -sk https://www.lagazzettadikyiv.com/ | grep -o "masthead-caduceus" | head -1
# Must: "masthead-caduceus" (NOT "masthead-fox")
```

### Full integrity scan (30 seconds)
See `gazzetta-integrity-check` skill for the complete cross-reference matrix.

## Recovery Procedure

### If ghost project exists:
1. `rm -rf ~/.hermes/hermes-agent/gazzetta-di-kyiv/`
2. Fix ALL cron jobs referencing the ghost path:
   ```bash
   python3 -c "
   import json, re
   jobs = json.load(open('$HOME/.hermes/cron/jobs.json'))['jobs']
   for j in jobs:
       if 'hermes-agent/gazzetta' in j.get('prompt',''):
           print(f'GHOST: {j[\"name\"]} ({j[\"id\"]})')
   "
   ```
3. For each flagged job: use `cronjob(action='update', job_id=..., prompt=clean_prompt, workdir='/Users/alexstocchi/projects/gazzetta-di-kyiv')`
4. Add workdir to ALL gazzetta cron jobs that lack it

### If font/emblem reverted:
The reversion was caused by a ghost commit being pushed to git and then deployed. Recovery:

1. Restore the correct versions from the last good state:
   - Font: `--display: 'Playfair Display', Georgia, serif;` in styles.css
   - Font link: `Playfair+Display:ital,wght@0,400;0,600;1,400` in index.html
   - Emblem class: `masthead-caduceus` (NOT `masthead-fox`)
   - Caduceus SVG with staff, wings, serpents (viewBox="0 0 20 40")
   - Crossed bulavas: two `<svg viewBox="0 0 14 38">` elements
   - Emblem sizes: 28×40px

2. Copy to site/ and deploy:
   ```bash
   cp index.html styles.css app.js site/
   # Deploy via gcloud (see deploy_to_gcs.sh)
   ```

3. Verify immediately:
   ```bash
   curl -sk https://www.lagazzettadikyiv.com/ | grep -o "Playfair\|masthead-caduceus"
   ```

### If flows went generic:
Ghost cron ran `generate_flows.py` against stale `site/data/stories.json`. Recovery:
1. Delete ghost project
2. Run `python3 scripts/generate_flows.py` from the real project
3. Verify rich flows: `python3 -c "import json; d=json.load(open('site/data/flows.json')); print(sum(1 for f in d['flows'] if f['amount_b'] >= 5))"` — must be ≥ 4

## Prevention (integrated)

- **Health check cron** (`gazzetta-health-check`, every 30m): curls live site, verifies flows quality and story count
- **Session start check**: load `hermes-truthfulness-protocol` + this reference
- **Cron integrity**: all gazzetta cron jobs must have workdir + no ghost paths in prompts
- **Git discipline**: never `git stash pop` from ghost commits — drop stashes from unknown sources
