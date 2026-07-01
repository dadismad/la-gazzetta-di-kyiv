---
name: gazzetta-post-deploy-verification
description: Mandatory post-deploy verification for lagazzettadikyiv.com. Run after EVERY deploy — CSS change, HTML change, pipeline rebuild, or content update.
category: gazzetta
triggers:
  - After any gsutil rsync to GCS
  - After any deploy command
  - After CEO rebuild_site
  - After design/CSS changes
  - User asks "is it live?"
---

# Post-Deploy Verification — La Gazzetta di Kyiv

## Why This Exists

We repeatedly pushed changes, declared them "done," and they weren't actually live because:
- CDN caches HTML and CSS (1-hour default)
- Hashed CSS filenames break when gsutil rsync -d deletes old hashes
- Nobody opened the browser to check
- Local stale files (`public-live/`, old hashes) kept re-poisoning every deploy
- Two competing deploy paths (Hermes cron + VM shipit) overwrote each other
- `deploy_routine.sh` kept setting `Cache-Control: immmutable, max-age=31536000` over our `no-cache`

This protocol runs after EVERY deploy. It is non-negotiable. Do not tell the user something is "done" or "live" without passing this verification.

## HARD GATE (read before ANY response to user about deploy status)

You MUST complete ALL verification steps and ALL success criteria checks before telling the user the site is "live," "deployed," "updated," or "done." If any check fails, you are still working on it. Do not summarize progress. Do not say "partially done." The only valid status messages are:

- "Still deploying — [N]/[total] checks passing, fixing [X]" (while working)
- "Design verified: all [N] checks passing" (only when ALL pass)

Never: "Design is live but [issues]" — if there are issues, it's not done. Keep working.

## Pre-Deploy Cleanup (MANDATORY before every deploy)

**The #1 cause of design regression: stale hashed CSS files in local `public/`.**

Every `gsutil rsync -d public/ gs://BUCKET/` uploads ALL local files. If old hashed CSS files (`styles.XXXXXXXX.css`) exist in `public/`, they get re-uploaded and the CDN may serve them instead of the correct CSS. This poisoned every deploy for weeks.

Before ANY deploy:
```bash
# Check for hashed CSS files
ls /Users/alexstocchi/lagazzettadikyiv/public/styles.*.css
# If ANY exist, DELETE them
rm -f /Users/alexstocchi/lagazzettadikyiv/public/styles.*.css
# Verify only styles.css remains
ls /Users/alexstocchi/lagazzettadikyiv/public/styles*
# Expected output: /Users/alexstocchi/lagazzettadikyiv/public/styles.css  (ONE file only)
```

Then sync:
```bash
devvit/google-cloud-sdk/bin/gsutil -m rsync -d -r public/ gs://www.lagazzettadikyiv.com/
```

Then set aggressive cache headers (no-store, not just no-cache):
```bash
devvit/google-cloud-sdk/bin/gsutil setmeta -h "Cache-Control:no-store, max-age=0" \
  gs://www.lagazzettadikyiv.com/index.html \
  gs://www.lagazzettadikyiv.com/styles.css
```

## Verification Steps

### Step 1: Navigate to the live site with a cache buster
```
browser_navigate(url="https://www.lagazzettadikyiv.com/?verify=<timestamp>")
```

### Step 2: Check which CSS is actually loading
```
browser_console(expression="Array.from(document.styleSheets).filter(s=>s.href && s.href.includes('styles')).map(s=>s.href.split('/').pop())[0]")
```

**Expected:** `styles.css` or `styles.css?v=...` (not a hashed filename like `styles.XXXXXXXX.css`)

### Step 3: Check computed colors (DOM — trust this, not vision models)
```javascript
browser_console(expression="JSON.stringify({
  bg: getComputedStyle(document.body).backgroundColor,
  gold: getComputedStyle(document.documentElement).getPropertyValue('--gold').trim(),
  bgVar: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()
})")
```

**Expected (Sovereign Terminal v32.0 — Phase C dark mode):**
- `bg`: `rgb(10, 10, 15)` — #0A0A0F dark terminal
- `gold`: `#D4AF37`
- `color`: `rgb(230, 228, 224)` — #E6E4E0 body text

**If background is `rgb(255, 255, 255)`:**
- The old CSS (v27.0) is loading
- Check if HTML references hashed CSS filename → fix to `styles.css?v=28.0`
- If loading `styles.css` but getting white → GCS has old content → check source and re-sync

### Step 4: Take a screenshot
```
browser_vision(question="What colors and design style do you see? Is the background warm paper/off-white or pure white?")
```

### Step 5: If anything is wrong
1. Check GCS origin: `gsutil cat gs://www.lagazzettadikyiv.com/styles.css | head -5`
2. Check local source: `head -5 /Users/alexstocchi/lagazzettadikyiv/public/styles.css`
3. Check HTML reference on GCS: `gsutil cat gs://www.lagazzettadikyiv.com/index.html | grep stylesheet`
4. Set no-cache if CDN is stale: `gsutil setmeta -h "Cache-Control:no-cache" gs://www.lagazzettadikyiv.com/index.html`
5. Force re-sync: `gsutil -m rsync -d -r public/ gs://www.lagazzettadikyiv.com/`
6. Re-verify from Step 1

## Pitfalls

- **LOCAL HASHED CSS POISONING** — The #1 cause of repeated design regression. Old hashed CSS files (`styles.15cf53ec.css`, `styles.ab6de8dd.css`) sitting in the local `public/` directory get re-uploaded by EVERY `gsutil rsync`. Even after deleting them from GCS, they come back because rsync syncs local→remote. The local files contained v27.0 (white background) and silently overwrote the correct v28.0 CSS on GCS. This went undetected for weeks because the CDN randomly served different hashed files. **Fix: delete ALL `styles.*.css` files from local `public/` before every deploy. Only `styles.css` should exist.**

- **`gazzetta.lock` STALE LOCK FILE** — A zero-byte file at the project root that blocks `db_to_json.py`. The script calls `open(lock_path, 'w')` and gets `PermissionError: [Errno 13]` when owned by a different user. **Fix: delete from both `/opt/gazzetta-di-kyiv/gazzetta.lock` (VM) and `/Users/alexstocchi/lagazzettadikyiv/gazzetta.lock` (local).**

- **`public-live/` DIRECTORY** — A SECOND local directory that also contained `styles.15cf53ec.css` (v27 poison). It was a staging/copy directory whose purpose was unclear. Any deploy script referencing this path would reintroduce the old design. **Fix: the entire `public-live/` directory was deleted. Verify it stays gone.**

- **DEPLOY PATH CONFLICT** — Two competing deploy sources. The active Hermes cron `gazzetta-deploy` (every 10 min, deploys local `public/` with `-d` flag) and the now-DISABLED VM `gazzetta-shipit` (every ~60 min, deployed VM `site/` which contained only `data/` — no HTML or CSS, and the `-d` flag would DELETE them from GCS). They fought. The VM shipit timer is disabled. **Only ONE deploy path must exist. Currently: Hermes cron only.**

- **`deploy_routine.sh` CACHE SABOTAGE** — Line 111 sets `Cache-Control:public, max-age=31536000, immutable` on `styles.css`. One-year cache. After every manual `no-cache` fix, if this script ran (which it didn't, as no crontab entry existed), it would overwrite. **The script is dormant but still present. Do NOT run it. The Hermes cron handles deploy now.**

**Vision models hallucinate colors.** Trust getComputedStyle() in browser_console, not vision analysis. The DOM is deterministic; vision is not. browser_console is the only reliable verification tool.

**TEMPLATE-PATCH CORRUPTION: backslash-n literal insertion (June 2026).** When patching Python template files that generate JavaScript (e.g., build_frontend.py), the patch tool may insert a literal backslash-n character sequence instead of a newline. Python ast.parse() passes because backslash-n is syntactically valid Python (line continuation). The build succeeds. But the literal backslash-n gets emitted verbatim into generated JavaScript, where it causes a syntax error that silently kills the entire inline script block. The page loads with zero JS execution. Detection: after any template patch, grep the generated HTML for backslash-n outside string contexts. Also check that key JS functions exist in the output: grep -c 'STORIES.map\|cardsEl.innerHTML' public/index.html must return at least 1. Fix: replace the literal backslash-n in the Python source with a true newline (split across two physical lines).
- **CDN caches HTML too**, not just CSS. Setting cache-control on the CSS file doesn't help if the HTML itself is cached and references the wrong CSS file. Google Cloud CDN default `max-age=3600` applies to all objects. **`Cache-Control: no-store, max-age=0` is required — `no-cache` alone is insufficient** and still allows CDN to serve stale copies. After setting headers, verify immediately with a fresh cache-buster query param.
- **Query params don't reliably break CDN cache.** The CDN may serve the same cached bytes regardless of query string. The proven fix: `gsutil setmeta -h "Cache-Control:no-cache, max-age=0" gs://BUCKET/index.html gs://BUCKET/styles.css`. This forces the CDN edge to revalidate on every request. Verify with `getComputedStyle()` — if background is still wrong, the CDN hasn't revalidated yet.
- **Hashed CSS filenames** are DEPRECATED but the VM pipeline still generates them via `build_hashed_assets.py`. Every pipeline rebuild creates a new hash. If the source `styles.css` is v28.0 Diplomatic Ledger, the hashed copy will be correct. BUT if the CDN-cached HTML references an old hash that was deleted by `gsutil rsync -d`, the page loads zero CSS. Workaround: fill ALL old hashed CSS files with v28 content so whichever the CDN serves, it's correct. Long-term fix: disable CSS hashing in `build_hashed_assets.py` on the VM.
- **Declaring "done" without browser verification** is the #1 trust-breaking failure. The user sees a white site, you see "deploy succeeded." The `gazzetta-post-deploy-verification` skill MUST run after every deploy. No exceptions. The browser_console `getComputedStyle()` check is the only gate.

## Success Criteria — Sovereign Terminal v32.0 (Phase C Dark Mode)

**Colors (all must pass):**
- [ ] Background: `rgb(10, 10, 15)` — #0A0A0F dark terminal
- [ ] Body text: `rgb(230, 228, 224)` — #E6E4E0 light terminal text
- [ ] Gold accent: `#D4AF37` — restricted to GAP>50, navigation, masthead
- [ ] Crimson: `#8B0000` — BREAKING tier, GAP>70
- [ ] Green: `#22C55E` — confirmation signals

**Typography (all must pass):**
- [ ] Body font: `Inter` — NOT `Source Serif 4`, NOT `Times`
- [ ] Headlines: `Playfair Display` — verify on h1/h2 elements

**Structure (all must pass):**
- [ ] Masthead separator: `1px solid gold` bottom border
- [ ] GAP Leaderboard present: `document.getElementById('gap-leaderboard')` returns element
- [ ] Leaderboard items: 5 cards with GAP scores + tickers + directional arrows
- [ ] Sidebar: all 12 narratives show non-zero capital (no $0M ghost data)
- [ ] Cards box-shadow: `none`
- [ ] No hashed CSS filename — only `styles.css`

## Post-Verification Action Rule (CRITICAL)

**If gaps are found, FIX them immediately. Do NOT ask the user "want me to implement?"**

The user asked for the design to be integrated. You verified it's not fully integrated. The next action is implementation, not another question. Asking permission to do what was already requested is a trust-breaking failure pattern. The user experiences it as "I already told you to do this three times — why are you asking again?"

After every verification:
- If all checks pass → report "Design verified: all #[N] checks passing"
- If checks fail → state what failed, THEN IMMEDIATELY BEGIN FIXING. No questions. No prompts. No "want me to."

The only exception: if fixing requires a decision only the user can make (which provider, which API key, which narrative priority). CSS fixes, HTML fixes, and deploy fixes never qualify — just execute.

## The Four-Layer Sabotage Pattern

Every design regression on lagazzettadikyiv.com traces to four independent failure mechanisms. Fixing any three isn't enough — all four must be addressed together.

### Layer 1: Local poison — stale hashed CSS in `public/` or `public-live/`

Files like `styles.15cf53ec.css` and `styles.ab6de8dd.css` containing v27.0 (white background) sit in local directories. Every `gsutil rsync` re-uploads them to GCS.

**Detection:** `find /Users/alexstocchi/lagazzettadikyiv -name 'styles.*.css' -not -path './node_modules/*'`

**Also check `public-live/`** — a mystery directory with its OWN `styles.15cf53ec.css`. If used as deploy source, it reintroduces poison even after `public/` is cleaned.

### Layer 2: VM hashing — `build_hashed_assets.py` creates new hashed filenames every cycle

Takes `styles.css`, computes SHA-256, creates `styles.XXXXXXXX.css`, REWRITES ALL HTML to reference the hash. The VM's `public/index.html` currently references `styles.24aab30b.css` — not the direct file.

**Fix:** Disable `build_hashed_assets.py` on the VM. Make `public/index.html` reference `styles.css` directly.

### Layer 3: Two competing deploy paths

| Path | Source | Frequency | Command |
|---|---|---|---|
| Hermes cron `gazzetta-deploy` | Local `public/` | Every 10 min | `gsutil -m rsync -d -r public/ gs://...` |
| VM `gazzetta-shipit` | VM `site/` | Every ~60 min | `gsutil -m rsync -d -r site/ gs://...` |

They overwrite each other. The VM shipit deploys from `site/` which contains ONLY `data/` — no HTML or CSS. The `-d` flag would DELETE HTML/CSS from GCS if shipit succeeded. Currently failing with PermissionError.

**Fix:** Single deploy path. Either Hermes cron OR VM shipit, not both. If VM: make it deploy `public/` not `site/`.

### Layer 4: Cache-Control sabotage

`deploy_routine.sh` sets `Cache-Control:public, max-age=31536000, immutable` on `styles.css`. One-year cache. Overwrites any `no-cache` setting.

**Detection:** `curl -sI "https://www.lagazzettadikyiv.com/styles.css" | grep -i cache`

**Fix:** After every deploy, set `Cache-Control:no-store, max-age=0` on `index.html` AND `styles.css`. Verify immediately.

## Related Skills

- **`gazzetta-verify-deploy`** — Older, more comprehensive post-deploy verification. Contains golden rules (CDN blindness, DOM vs vision, hashed asset traps). These two skills overlap. `gazzetta-post-deploy-verification` is the concise, mandatory protocol. `gazzetta-verify-deploy` is the exhaustive reference with 25+ pitfall patterns. Consolidation recommended — curator task.

## Reference Files

- **`references/design-spec-diplomatic-ledger.md`** — Complete Diplomatic Ledger v28.0 design specification (colors, typography, layout, components, shapes). The canonical source for what the site SHOULD look like. Load this when verifying design compliance. Covers: all color tokens, typography scale, spacing system, shape rules (0px), component specifications, navigation overlay rules.
