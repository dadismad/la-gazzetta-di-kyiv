#!/usr/bin/env python3
import os, subprocess, sys

repo = '/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv'
collector = '/Users/alexstocchi/.hermes/scripts/social_umbrella_collector.py'
source_updater = '/Users/alexstocchi/.hermes/scripts/gazzetta_source_strategy_update.py'
pipeline_audit = '/Users/alexstocchi/.hermes/scripts/gazzetta_pipeline_audit.py'
repr_research = '/Users/alexstocchi/.hermes/scripts/gazzetta_representation_research.py'
builder = os.path.join(repo, 'scripts', 'build_site.py')
envfile = os.path.expanduser('~/.hermes/.env')

def sh(cmd, cwd=None, env=None):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        raise SystemExit(r.returncode)
    return r.stdout.strip()

# 1) update source strategy
sh([sys.executable, source_updater])
# 2) collect fresh data
sh([sys.executable, collector])
# 3) pipeline audit
sh([sys.executable, pipeline_audit])
# 4) representation-techniques research
sh([sys.executable, repr_research])
# 5) copy operational snapshots into repo data dir
for p in [
    '/Users/alexstocchi/.hermes/data/social_umbrella/sources.json',
    '/Users/alexstocchi/.hermes/data/social_umbrella/pipeline_audit.json',
    os.path.join(repo, 'data', 'representation_techniques.json'),
]:
    if os.path.exists(p):
        if '/.hermes/data/social_umbrella/' in p:
            import shutil
            shutil.copy2(p, os.path.join(repo, 'data', os.path.basename(p)))
# 6) build site + narratives
sh([sys.executable, builder])

# 3) git publish via configured origin remote
# Uses existing git credential helper / gh auth rather than embedding tokens.
sh(['git','add','data','site'], cwd=repo)
subprocess.run(['git','commit','-m','chore: scheduled refresh data+site'], cwd=repo, capture_output=True, text=True)
sh(['git','pull','--rebase','origin','main'], cwd=repo)
sh(['git','push','origin','main'], cwd=repo)
print('OK: published refresh to GitHub via origin')
