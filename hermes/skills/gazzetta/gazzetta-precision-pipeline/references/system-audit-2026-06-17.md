# System Audit Report — Gazzetta di Kyiv (2026-06-17)

Full SRE audit of the pipeline infrastructure. Key findings:

- Cloud Brain VM was provisioned (Jun 10) but never received pipeline scripts. All 4 systemd timers fail every interval with `code=exited, status=2/INVALIDARGUMENT` — approximately 672 cumulative failures.
- Hermes cron (`gazzetta-product-factory`) PAUSED since Jun 16 after error.
- shipit_cloud.py on VM gets 403 GCS auth errors (missing storage.objectAdmin role).
- auto_revert.py is misnamed — it's a notification + forward-halt, NOT a rollback.
- The "crash-rollback" user perception is pipeline failure masking: the pipeline never reaches processing, it fails at step zero.
- Local data is correct: 377 stories, 199 flows in v2.0 6-container format.
- GCS stories.json format mismatch was a query error (old field names on v2.0 data), not actual data corruption.
- Canonical pipeline chain: intel_to_stories → decay_stories → validate_stories → generate_flows → build_site
- Canonical orchestrator: scripts/pipeline_chain.sh (old gazzetta_pipeline_chain.sh removed)
- Working GCS SDK path: ~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/
- Project root: /Users/alexstocchi/lagazzettadikyiv (NOT projects/gazzetta-di-kyiv)

Duplicate files removed in cleanup:
- agents_build_rd/ (redundant Docker subset)
- gazzetta_v1_backup.db (stale DB)
- scripts/gazzetta_pipeline_chain.sh (old v1.x pipeline)
- devvit/google-cloud-cli-darwin-arm.tar.gz (86MB redundant archive)
- __pycache__/*.pyc (7 stale bytecode files)
