# cloud_entrypoint.py DB Persistence Fix — Sprint 4

## Bug

`cloud_entrypoint.py` `ensure_db_ready()` read from wrong path in container:
- **Wrong:** `APP_DIR / "public" / "data" / "stories.json"` → `/app/public/data/stories.json`
- **Correct:** `APP_DIR / "data" / "stories.json"` → `/app/data/stories.json`

Dockerfile copies: `COPY data/ /app/data/` and `COPY public/ /app/public/`. The data files live at `/app/data/` — NOT under `public/data/` at container start. `build_site.py` later copies them to `public/data/`, but that runs later in the pipeline.

## Symptom

Cloud Run pipeline log: "No stories.json to seed from — DB initialized empty". The DB stays 0 bytes, `db_to_json.py` has no stories to compile, `test_platform.py` fails because `public/data/stories.json` doesn't exist.

## Fix

```python
# In cloud_entrypoint.py ensure_db_ready():
stories_json = APP_DIR / "data" / "stories.json"   # was: public/data/stories.json
flows_json = APP_DIR / "data" / "flows.json"        # was: public/data/flows.json
```

## Pipeline Flow (corrected)

1. `download_db()` — downloads `gazzetta.db` from GCS (or detects 0 bytes → fresh)
2. `ensure_db_ready()` — init schema via `init_db.py --force`, seed from `/app/data/stories.json`
3. `deploy_routine.sh` — runs db_to_json (populated DB as source), build_site, test_gate
4. `import_json_to_db.py` — re-syncs pipeline output back to DB
5. `upload_db()` + `sync_public()` — uploads 2.9MB DB + 57 public files to GCS

## Verification

After fix: DB 2,932,736 bytes, 246 stories, 570 tests passed, 0 failed.
