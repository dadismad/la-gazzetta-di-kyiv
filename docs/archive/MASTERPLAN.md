# LA GAZZETTA DI KYIV — SYSTEM MASTERPLAN
## Full Audit & Review Framework — Do Not Execute Without Approval

---

## WHY THIS EXISTS

The system has accumulated technical debt across four domains:
1. **Local files** — poisoned artifacts (old hashed CSS, stale HTML references)
2. **VM state** — permission mismatches, service user conflicts, orphaned files
3. **GCS bucket** — multiple CSS versions, CDN caching defeating updates
4. **Pipeline data** — uniform contradiction gaps, synthetic capital volumes

Every previous "fix" addressed one layer without auditing the others. This created whack-a-mole: fix CSS → CDN reverts → fix CDN → local files overwrite → fix local → VM rebuilds old hash.

This masterplan audits ALL layers in dependency order, so a fix at layer N doesn't get undone by layer N+1.

---

## LAYER 0: LOCAL SOURCE OF TRUTH
### `/Users/alexstocchi/lagazzettadikyiv/public/`

**Audit checklist:**
- [ ] `styles.css` — verify header says v28.0 Diplomatic Ledger (not v27)
- [ ] `index.html` — verify `<link>` references `styles.css?v=28.0` (not a hashed filename)
- [ ] All `.html` files — grep for `styles.XXXXXXXX.css` pattern → must return ZERO results
- [ ] All `.html` files — grep for `styles.css` → must return matches on every page
- [ ] `public/styles.*.css` — must have ZERO hashed CSS files. Delete any found.
- [ ] `public/data/stories.json` — exists, valid JSON, `all_stories` array present
- [ ] Git status — are there uncommitted changes that represent the "last known good" state?

**Known poison to eliminate:**
- Any file matching `styles.[a-f0-9]{8}.css` in `public/`
- Any `.html` reference to a hashed CSS filename

---

## LAYER 1: GCS BUCKET
### `gs://www.lagazzettadikyiv.com`

**Audit checklist:**
- [ ] `gsutil ls gs://www.lagazzettadikyiv.com/styles*` — only ONE result: `styles.css`
- [ ] `gsutil cat gs://www.lagazzettadikyiv.com/styles.css | head -3` — says v28.0 Diplomatic Ledger
- [ ] `gsutil cat gs://www.lagazzettadikyiv.com/index.html | grep stylesheet` — references `styles.css?v=28.0`
- [ ] All hashed CSS files deleted: `styles.15cf53ec.css`, `styles.ab6de8dd.css`, `styles.24aab30b.css`, etc.
- [ ] Cache-Control metadata on index.html: `no-store, max-age=0`
- [ ] Cache-Control metadata on styles.css: `no-store, max-age=0`
- [ ] `_audit_test.txt` and `_vm_test.txt` — delete these test artifacts
- [ ] File count — all pages present (index, about, archive, capital, methodology, privacy, sources, terms)

**Known poison:**
- CDN edge caches last up to 3600s. After deploy, verify via `curl -H "Cache-Control: no-cache" https://www.lagazzettadikyiv.com/styles.css | head -3`

---

## LAYER 2: VM FILESYSTEM
### `gazzetta-prod (35.188.110.255) /opt/gazzetta-di-kyiv/`

**Audit checklist:**
- [ ] `public/styles.css` — v28.0 Diplomatic Ledger (same as local)
- [ ] `public/` directory — any hashed CSS files? Delete them.
- [ ] `public/index.html` — what CSS reference does it contain? (VM pipeline may regenerate)
- [ ] `scripts/build_hashed_assets.py` — is it still active? Should be disabled.
- [ ] `scripts/shipit_cloud.py` — references `public/` (not `site/`)
- [ ] `site/` directory — deprecated, should be empty or removed
- [ ] `data/gazzetta.db` — permissions (gazzetta:gazzetta, 775, alexstocchi in group)
- [ ] `gazzetta.lock` — should NOT exist. Delete if present.
- [ ] `config.json` — permissions. Should be writable by alexstocchi.
- [ ] `.env` — DeepSeek key present, valid format. Gemini key (depleted) — remove or mark.
- [ ] `mailbox/inbox.json` — clean up old directives older than 7 days

**Known poison:**
- `site/` directory still exists (legacy from June 10). The shipit may reference it.
- `build_hashed_assets.py` regenerates hashed CSS on every rebuild — root cause of hash rot
- Lock file permission errors (alexstocchi can't write to gazzetta-owned root dir)

---

## LAYER 3: VM SERVICES & TIMERS
### systemd on gazzetta-prod

**Audit checklist:**
- [ ] `gazzetta-intel.service` — user=alexstocchi, runs fetch_intel.py, feedparser installed
- [ ] `gazzetta-intel.timer` — enabled, active, every 30min
- [ ] `gazzetta-marketdata.service` — user=?, runs market_reality.py, yfinance+AlphaVantage working
- [ ] `gazzetta-marketdata.timer` — enabled, active
- [ ] `gazzetta-governor.service` — user=?, runs governor.py, Sovereign Auditor prompt active
- [ ] `gazzetta-governor.timer` — enabled, active
- [ ] `gazzetta-pipeline.service` — user=alexstocchi, runs db_to_json+build_site+test_platform
- [ ] `gazzetta-pipeline.timer` — enabled, active
- [ ] `gazzetta-shipit.service` — user=alexstocchi, runs shipit_cloud.py, GCS write tested
- [ ] `gazzetta-shipit.timer` — enabled, active
- [ ] All services: journalctl last 3 runs — any EXEC errors, permission errors, timeouts?
- [ ] All services: `User=` lines match the user who owns the files they need to write

**Known poison:**
- Services run as `alexstocchi` but files owned by `gazzetta` — group membership was fixed but may regress
- `gazzetta-pipeline` last run showed lock file PermissionError — verify fix held

---

## LAYER 4: PIPELINE DATA INTEGRITY
### The actual content quality

**Audit checklist:**
- [ ] `stories.json` — `all_stories` count (was 376). Growing or static?
- [ ] Contradiction gaps — min, max, avg. If all at 15, market_reality is returning defaults.
- [ ] Capital volumes — if all at $100M, volume aggregator is broken.
- [ ] `market_reality.py` — test with `python scripts/market_reality.py --all`. Fresh ticker data?
- [ ] Last ticker pull timestamp — when did UUP, VIX, WTI last update?
- [ ] AlphaVantage fallback — is yfinance failing silently, falling back to AlphaVantage defaults?
- [ ] `contradiction_synthesizer.py` — DeepSeek API key (Key 2) working? Test with one story.
- [ ] Narrative distribution — are all 8 narratives getting stories? (gene_editing: 8, wealthy_sports: 5 were starving)

**Known poison:**
- CEO reported all gaps at 15, all volumes at $100M — this is synthetic uniform data
- yfinance may be rate-limited or returning stale data
- AlphaVantage fallback may use default/placeholder values

---

## LAYER 5: LIVE SITE VERIFICATION
### lagazzettadikyiv.com — visual + functional

**Audit checklist (use gazzetta-post-deploy-verification skill):**
- [ ] Browser navigate + cache buster
- [ ] `getComputedStyle` — background `#FAF9F6`, text `#1A1C1A`, font Inter
- [ ] CSS variables — gold `#D4AF37`, crimson `#8B0000`, red `#8B0000` (not casino)
- [ ] Only ONE CSS file loaded (styles.css, not hashed)
- [ ] Masthead gold separator visible (1px solid gold border-bottom)
- [ ] Navigation dropdown — dark navy `#1A1F2E`, 0px radius, no shadow
- [ ] Story cards — gold left border + gold bottom separator, paper background
- [ ] All pages load (index, about, archive, capital, methodology, privacy, sources, terms)
- [ ] 94/94 tests pass (test_platform.py)
- [ ] Mobile viewport — 16px margins, single column, readable at 375px width

---

## LAYER 6: CEO / GOVERNOR HEALTH
### The Sovereign Auditor

**Audit checklist:**
- [ ] System prompt — verify it's the Sovereign Auditor (not the old CEO prompt)
- [ ] DeepSeek API key — valid, not expired, not rate-limited
- [ ] Mailbox system — inbox processing, outbox responses within 60s
- [ ] Execution commands — test: trigger_pipeline, rebuild_site, status
- [ ] Telegram notifications — channel ID correct, token active
- [ ] Cloud Function bridge — code written but NOT deployed. Should we deploy?

---

## LAYER 7: CROSS-CUTTING CONCERNS

**Never regress on:**
- No hashed CSS filenames in any directory, any bucket, any reference
- gazzetta-post-deploy-verification skill MUST run after every deploy
- One CSS file, one reference — no exceptions
- alexstocchi must remain in gazzetta group on VM
- Cache-Control: no-store on index.html and styles.css

**To add:**
- Post-deploy verification as a cron job (automated, not manual)
- VM health check endpoint or Telegram heartbeat
- Data quality alert if all gaps are identical (uniform data = blind pipeline)
- Git tracking of "last known good" state for each layer

---

## EXECUTION ORDER

If approved, execute in this sequence (each layer verified BEFORE moving to next):

1. Layer 0 — local cleanup (nothing deploys until local is clean)
2. Layer 1 — GCS cleanup + cache headers
3. Layer 2 — VM filesystem fix
4. Layer 3 — VM services verify
5. Layer 5 — live site verify (can't verify data without site working)
6. Layer 4 — pipeline data (deepest, takes longest)
7. Layer 6 — CEO health
8. Layer 7 — prevent regressions

**Each layer gates the next. No skipping.**
