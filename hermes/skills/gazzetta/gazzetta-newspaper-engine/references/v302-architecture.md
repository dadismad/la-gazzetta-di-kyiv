# v30.2 Architecture — Single-Page SPA Compiler

## build_frontend.py replaces build_site.py (June 2026)

The old multi-page HTML + hashed JS + dashboard.js + styles.css architecture was replaced by a single Python compiler that generates one responsive `index.html` with all content embedded at build time.

### Architecture

```
build_frontend.py (runs on VM every 10 min via governor)
  Reads: data/stories.json + public/data/flows.json
  Computes: narrative summaries, capital flow ledger, contradiction matrix, lifecycle phases
  Injects: data as <script>const STORIES = [...];</script> — no fetch() calls
  Output: public/index.html (single file, ~630KB)
```

### Multi-View SPA

Four tabs with hash-based routing:
1. **Stream** — story feed with progressive disclosure accordions
2. **Capital Flows** — macro ledger table with discrepancy markers
3. **Contradictions** — sortable matrix with reflexivity alerts
4. **About** — Lefevre Filter + Narrative Lifecycle Phases + Invalidation Thresholds

### Design System (Stitch DESIGN.md + Banani desktop sidebar)

- Tailwind CDN with DESIGN.md tokens baked into tailwind.config
- 0px border-radius everywhere, no box-shadows
- Playfair Display (headlines) + Inter (body)
- Gold (#D4AF37) 1px structural rules
- Surface background #FAF9F6
- Masthead: roman purple (#66023C) with gold strikethrough
- Desktop: dark sidebar (#000000, 320px) with narrative navigation (Banani)
- Mobile: bottom nav, horizontal-scroll narrative pills (Stitch)

### Progressive Disclosure Pattern

Using native `<details>` + `<summary>` with Material Symbols icons:
- Browser disclosure triangles hidden: `summary::-webkit-details-marker{display:none}`
- Expand icon: `<span class="material-symbols-outlined expand-icon">expand_more</span>`
- 180-degree rotation on open: `details[open] .expand-icon{transform:rotate(180deg)}`
- Zero layout shift: fade-in animation, no grid breaks
- No open states hardcoded in data — all state local to browser runtime

### Tab Clickability Pattern

Delegated event listener on `#tab-nav`:
```javascript
document.getElementById('tab-nav').addEventListener('click', function(e) {
  var btn = e.target.closest('[data-tab]');
  if (!btn) return;
  switchTab(btn.getAttribute('data-tab'));
});
```
Buttons use `data-tab="stream"` attributes. Inline onclick works for mobile bottom nav.

### Deploy Architecture (v2.0 — Governor-Only)

**CRITICAL**: The deploy step uses `gsutil rsync -r -d public/ GCS` which DELETES any file on GCS not in VM's public/. Never deploy to GCS directly from local — the governor's rsync will delete it within 10 minutes. All frontend changes must flow through the VM: edit locally → scp to VM scripts/ → governor picks up next cycle → rsync to GCS.

### CDN Load Balancer Caching (even with enableCdn=false)

The GCS load balancer caches responses even when CDN is disabled. Old files had `cache-control: public, max-age=3600`. Fix: always upload with `gsutil -h 'Cache-Control:no-cache,no-store,max-age=0' cp ...`. Detection: compare `curl -sI https://www.lagazzettadikyiv.com/ | grep content-length` with direct GCS stat. If different, CDN is stale. Invalidation: `gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path "/*"`. Can also wait for TTL expiry (up to 1 hour).

### SSH Access

VM: gazzetta-prod (35.188.110.255). Login user: **alexstocchi** (NOT gazzetta). Key: `~/.ssh/google_compute_engine`. Systemd service runs as gazzetta user inside VM. File operations requiring gazzetta ownership: `sudo cp ... && sudo chown gazzetta:gazzetta ...`.

### Deleted Architecture (do NOT restore)

- build_site.py (replaced by build_frontend.py)
- dashboard.js + all hashed JS files (app.*.js, i18n.*.js, sector.*.js, story-app.*.js)
- styles.css (replaced by Tailwind CDN)
- Heat map / imperial overlay (deleted — violates 0px radius spec)
- All multi-page HTML (about.html, archive.html, capital.html, etc. — replaced by SPA tabs)
- stories-v2/v3/v4.json copies (no longer needed)

### Test Platform

`test_platform.py` validates stories.json structure only — not HTML. Must return 101 PASS / 0 FAIL. Duplicate story_ids show as WARN (not FAIL). Run before deploy: `python3 scripts/test_platform.py`.
