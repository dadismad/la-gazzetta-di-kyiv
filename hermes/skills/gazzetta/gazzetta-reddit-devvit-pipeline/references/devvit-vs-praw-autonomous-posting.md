# Devvit vs PRAW — Autonomous Posting Architecture Decision

Sprint 10, June 2026. Definitive answer to: can Devvit handle autonomous 30-minute
posting to r/LaGazzettadiKyiv, or is PRAW strictly required?

## Verdict

**Devvit CANNOT handle autonomous 30-minute posting. PRAW is strictly required
for sub-hour autonomous posting.**

## Devvit Limitation: `fetch()` Domain Allowlist

Devvit's server runtime `fetch()` only reaches domains allowlisted by Reddit.
`www.lagazzettadikyiv.com` (GitHub Pages / GCS static site) is NOT on the
allowlist. The Devvit app cannot fetch `data/stories.json` at runtime to get
fresh story data.

The bake pipeline (`bake_payload.py` → `_payload.ts` → `devvit upload`) bakes
content into the app at BUILD time — the payload is frozen until the next
`devvit upload` + `devvit install` cycle.

## Architecture Comparison

| Approach | Autonomy | Cadence | Latency | Complexity | Status |
|----------|----------|---------|---------|------------|--------|
| **Devvit bake** | Semi-autonomous (build-time payload) | 4h/8h via scheduler | Hours | Low (already deployed) | WORKS for curated posts |
| **PRAW + script** | Fully autonomous (live API polling) | 30 min | Minutes | Medium (needs credentials) | NOT YET built |
| **PRAW + Cloud Run** | Fully autonomous (serverless) | Event-driven | Minutes | Medium-High (new job) | NOT YET built |

## Recommended Two-Track Architecture

**Track 1 — Devvit (4h/8h curated):** Keep the existing Devvit app for
pre-baked, high-quality curated posts. Scheduler tasks:
- `autopost_curated_4h` — curated content from `reddit_latest.md`
- `autopost_multisource_feed_6h` — Reddit intelligence feed
- `autopost_short_report_8h` — Macro Radar

**Track 2 — PRAW + Cloud Run (30 min real-time):** New Cloud Run Job that:
1. Reads `data/stories.json` from GCS every 30 min
2. Formats top 3 stories via post_composer.py (human-detection-bypass layer)
3. Submits via `praw.Reddit().submit()` to r/LaGazzettadiKyiv
4. Records to `cco_drafts/posted_stories.jsonl` for idempotency

## PRAW Prerequisites (C-Suite Must Provision)

1. Create Reddit Script App at https://www.reddit.com/prefs/apps
   - Type: "script"
   - Name: LaGazzettadiKyiv
   - Redirect URI: http://localhost:8080
2. Copy `client_id` (14-char string under app name)
3. Copy `client_secret` (long hex string)
4. Register bot Reddit account (e.g., GazzettaBot) and note password
5. Store in Secret Manager:
   - `reddit-client-id`
   - `reddit-client-secret`
   - `reddit-username`
   - `reddit-password`
   - `reddit-user-agent`  ← REQUIRED by Reddit API policy (e.g. "GazzettaBot/1.0 by u/LaGazzettadiKyiv")

## Content Type Separation

To prevent duplicate content when both Devvit and PRAW post to the same
subreddit:
- **Devvit posts:** Curated, pre-baked "editor's picks" — longer form, multi-story
- **PRAW posts:** Real-time pipeline stories — single story, contradiction-first format
- Different cadences prevent overlap: Devvit at 4h/8h, PRAW at 30 min
