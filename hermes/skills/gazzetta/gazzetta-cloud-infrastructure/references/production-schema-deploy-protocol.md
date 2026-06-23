# Production Schema Deploy Protocol

Safe 11-step sequence for deploying schema changes to the VM pipeline without data loss or race conditions. Established June 2026 during the 31-field schema migration.

## When to Use

- Adding/removing fields from `contradiction_synthesizer.py` output
- Running backfill/migration scripts against production stories.json
- Any change where the VM governor could overwrite your work mid-migration

## The Protocol

```
0.  [PREREQUISITE] Write all backfill/migration scripts locally.
    Each script imports CANONICAL_FIELDS from synthesizer via dummy call.
    Each handles the {"containers": {...}, "all_stories": [...]} wrapper.

1.  SSH: systemctl stop gazzetta-governor.timer
    Verify: systemctl status gazzetta-governor.timer | grep Active
    Expected: "Active: inactive"

2.  Patch synthesizer on VM.
    Route through /tmp if file is owned by gazzetta user:
    scp file alexstocchi@VM:/tmp/ → ssh → sudo cp to /opt/gazzetta-di-kyiv/scripts/
    Verify: python3 -c "from contradiction_synthesizer import assemble_story; s=assemble_story((0,'','','','',''),{},{},{}); print(len(s))"

3.  scp VM synthesizer → local (keep local in sync)
    Verify: diff VM:file local:file → no diff

4.  scp VM:stories.json → local data/
    Pull PRODUCTION data, not your stale local copy.

5.  Run all backfill scripts in sequence.
    Each script: backup → read → modify → atomic write via os.replace()
    Verify after each: field coverage, no "unassigned" narrative_ids

6.  Validation gate. Minimum checks:
    - assert len(stories) == expected_count
    - assert all('narrative_id' in s for s in stories)
    - assert all('data_fidelity' in s for s in stories)
    - assert no source_name == "RSS"

7.  scp local:stories.json → VM:/opt/gazzetta-di-kyiv/public/data/

8.  SSH: manual build_frontend.py (optional, or skip and let governor fire)
    Verify: "wrote ... index.html" with no errors

9.  SSH: systemctl start gazzetta-governor.timer
    Verify: status shows "active (waiting)"

10. Wait for next cycle. Check governor log:
    journalctl -u gazzetta-governor.service -f
    Expected: no errors, N/N OK, stories.json written with new schema

11. Verify live site: browser_navigate → check source names, tiers, card count
```

## Dynamic Schema Extraction Pattern

Never hardcode field names in backfill scripts. Import from the synthesizer:

```python
sys.path.insert(0, str(Path(__file__).parent))
from contradiction_synthesizer import assemble_story

# Get canonical schema — 6-element tuple for db_item, empty dicts for llm_story + prices
CANONICAL_DEFAULTS = assemble_story((0, "", "", "", "", ""), {}, {})
CANONICAL_FIELDS = set(CANONICAL_DEFAULTS.keys())

# When backfilling: start from defaults, overlay existing data
for story in all_stories:
    hydrated = CANONICAL_DEFAULTS.copy()
    for key in CANONICAL_FIELDS:
        if key in story:
            hydrated[key] = story[key]
    # ... apply migration logic ...
```

This pattern ensures backfill scripts stay in sync with schema changes automatically.

## Critical Pitfalls

1. **Never skip the timer pause.** The governor fires every 10 minutes. It WILL overwrite your backfilled data with fresh synthesis output if you don't freeze it first.

2. **Always pull production data before backfilling.** Your local stories.json may be days stale. The VM has the canonical copy.

3. **SCP to VM files owned by gazzetta user.** Route through /tmp: `scp file VM:/tmp/` → `ssh VM "sudo cp /tmp/file /opt/... && sudo chown gazzetta:gazzetta /opt/.../file"`

4. **`db_item` is a tuple, not a dict.** The synthesizer's `assemble_story(db_item, llm_story, prices)` unpacks: `item_id, source_url, source_type, title, full_text, narrative_tag = db_item`. Backfill scripts calling it for schema extraction must pass a 6-element tuple.

5. **Validate before restarting timer.** A corrupted stories.json + resumed timer = governor crashes on next cycle. At minimum: JSON parse check + story count check + key field presence check.

6. **Backup before every script.** `shutil.copy(data_path, data_path.with_suffix('.json.bak'))` — if any script crashes mid-write, you can recover.
