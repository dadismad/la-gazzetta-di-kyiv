# System Audit Layers — La Gazzetta di Kyiv

## When to Use

When the user reports "something is broken" or "the system isn't working," audit ALL layers in dependency order. Do not stop at layer 1. Each layer can independently sabotage fixes at the layer below.

## Layer 0: Local Source of Truth
**Directory:** `/Users/alexstocchi/lagazzettadikyiv/`

Checklist:
- `public/styles.css` — header says v28.0 Diplomatic Ledger (not v27)
- `public/index.html` — `<link>` references `styles.css?v=28.0` (not a hash)
- ALL `.html` files — grep `styles.XXXXXXXX.css` → must return ZERO
- `public/styles.*.css` — must have ZERO hashed files. Delete any found.
- `public-live/` — check for poison. This directory exists and may contain old CSS.
- `gazzetta.lock` — stale lock file. Delete if present.

## Layer 1: GCS Bucket
**Bucket:** `gs://www.lagazzettadikyiv.com`

Checklist:
- `gsutil ls gs://www.lagazzettadikyiv.com/styles*` — ideally ONE result: `styles.css`
- `gsutil cat gs://www.lagazzettadikyiv.com/styles.css | head -3` — v28.0
- `gsutil cat gs://www.lagazzettadikyiv.com/index.html | grep stylesheet` — references `styles.css`
- `curl -sI https://www.lagazzettadikyiv.com/styles.css | grep -i cache` — must be `no-store`, NOT `max-age=31536000`
- Delete all `styles.XXXXXXXX.css` files from GCS (old hashes that accumulate)

## Layer 2: VM Filesystem
**Host:** `gazzetta-prod` (check IP with `gcloud compute instances list`)
**Path:** `/opt/gazzetta-di-kyiv/`

Checklist:
- `public/styles.css` — v28.0? If v27, sync from local.
- `public/index.html` — references `styles.XXXXXXXX.css` (hash) or `styles.css` (correct)?
- `scripts/build_hashed_assets.py` — STILL EXISTS. Must be disabled.
- `site/` — deprecated. Only has `data/`. Should be removed or shipit should deploy `public/`.
- `gazzetta.lock` — delete if present.
- `config.json` — permissions. Must be writable by service user.
- `.env` — DeepSeek key present. Gemini key (depleted) — mark or remove.

## Layer 3: VM Services & Timers

Checklist:
- All 5 timers: `systemctl list-timers | grep gazzetta` — enabled, active
- All 5 services: `journalctl -u <name> --no-pager -n 5` — check last run for errors
- `gazzetta-pipeline` — last run showed PermissionError on lock file. Verify fix held.
- `gazzetta-shipit` — last run showed PermissionError on `site/data/stories.json`. Fix or disable.
- User mismatch: services run as `alexstocchi` but files owned by `gazzetta`. Verify alexstocchi is in gazzetta group.

## Layer 4: Pipeline Data Integrity

Checklist:
- `stories.json` — `all_stories` count. Growing or static?
- Contradiction gaps — min, max, avg. If all identical (all=15), market data is dead.
- Capital volumes — if all=$100M, volume aggregator is broken.
- `market_reality.py` — test with `--all`. Fresh ticker data?
- `contradiction_synthesizer.py` — DeepSeek API key (Key 2) working?
- Narrative distribution — all 8 getting stories? gene_editing and wealthy_sports were starving.

## Layer 5: Live Site Verification

Run `gazzetta-post-deploy-verification` skill. Full spec check:
- Colors: bg #FAF9F6, text #1A1C1A, gold #D4AF37, crimson #8B0000
- Typography: body Inter, headlines Playfair Display
- Structure: masthead gold separator, story card separators, nav dropdown 0px/shadow-none
- Only ONE CSS file loading (styles.css, not hashed)
- 94/94 tests pass

## Layer 6: CEO / Governor Health

Checklist:
- System prompt — Sovereign Auditor (not old CEO prompt)
- DeepSeek API key — valid, not expired
- Mailbox — inbox processing, outbox responses within 60s
- Execution commands — test trigger_pipeline, rebuild_site, status
- Telegram — channel correct, token active
- Cloud Function bridge — code written, NOT deployed

## Layer 7: Cross-Cutting

Never regress on:
- No hashed CSS filenames anywhere
- One deploy path, one CSS reference
- alexstocchi in gazzetta group on VM
- Cache-Control: no-store on index.html and styles.css
- Post-deploy verification after every deploy

## Dependency Order

Audit MUST follow this order (each layer gates the next):
1. Local cleanup → 2. GCS cleanup → 3. VM filesystem → 4. VM services → 5. Live site → 6. Pipeline data → 7. CEO health → 8. Prevent regressions
