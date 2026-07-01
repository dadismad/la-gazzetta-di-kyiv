# Data Migration Freeze Sequence (June 2026)

Complete 13-step protocol for applying schema changes to production stories.json without data loss or pipeline crashes.

## Prerequisites
- All migration scripts written and tested locally
- Scripts import canonical schema dynamically from `contradiction_synthesizer.assemble_story()`
- Scripts include `fix_ownership()` call and atomic write pattern

## Sequence

```
Step 1:  SSH: sudo systemctl stop gazzetta-governor.timer
Step 2:  Verify: systemctl status gazzetta-governor.timer | grep Active → "inactive"
Step 3:  Patch contradiction_synthesizer.py on VM (new assemble_story return dict)
Step 4:  SCP patched file from VM to local (keep local in sync)
Step 5:  SCP production stories.json from VM to local (VM: public/data/stories.json)
Step 6a: python3 scripts/backfill_narrative_ids.py  (classify into narratives)
Step 6b: python3 scripts/fix_source_names.py        (replace "RSS" with domains)
Step 6c: python3 scripts/align_tiers.py             (gap-based tier recomputation)
Step 7:  Validate: check all stories have narrative_id, data_fidelity, no "RSS" sources
Step 8:  SCP stories.json back to VM
Step 9:  Sync BOTH copies: data/stories.json AND public/data/stories.json
Step 10: sudo chown gazzetta:gazzetta on BOTH copies
Step 11: Manual build: venv/bin/python3 scripts/build_frontend.py
Step 12: SSH: sudo systemctl start gazzetta-governor.timer
Step 13: Wait for next cycle, verify journalctl for errors
```

## Critical Rules
- NEVER run migration while timer is active — 10-minute cycle overwrites changes
- ALWAYS use venv Python for scripts importing from contradiction_synthesizer (aiohttp dependency)
- ALWAYS chown gazzetta:gazzetta after any file write — alexstocchi-owned files crash the governor
- ALWAYS sync BOTH copies (data/ + public/data/) — GCS serves from public/data/
- ALWAYS validate before thawing — corrupt stories.json with timer active = extended outage
- Use `fix_ownership()` utility, not ad-hoc `sudo chown` commands

## Recovery from Permission Denied Crash
If governor crashes with `Permission denied: stories.json` after migration:
```bash
sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/data/stories.json
sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/public/data/stories.json
```
Next cycle will recover automatically.
