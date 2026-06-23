# Devvit App Architecture — Full Reference

Project: `~/lagazzettadikyiv`
Subreddit: `r/LaGazzettadiKyiv`

## File Map

```
~/lagazzettadikyiv/
├── devvit.json              → App config: triggers, menus, scheduler, permissions
├── tools/
│   └── bake_payload.py      → Reads reddit_latest.md → writes _payload.ts
├── src/server/
│   ├── index.ts             → Hono app entry point, routes registration
│   ├── core/
│   │   ├── _payload.ts      → AUTO-GENERATED: LATEST_TITLE + LATEST_BODY exports
│   │   ├── post.ts          → createPost() — reads _payload.ts, submits post
│   │   ├── reddit-ops.ts    → collectAndInterpretSubreddit(), publishShortNow(),
│   │   │                      publishMultiSourceFeed(), getPostingStatus()
│   │   └── .autopost_tick.ts→ Timestamp file to force version bumps
│   └── routes/
│       ├── triggers.ts      → on-app-install: tries createPost() → Macro Radar → heartbeat
│       ├── menu.ts          → post-curated, post-now-short-report, multi-source-feed, etc.
│       ├── forms.ts         → Form handlers
│       └── api.ts           → Public API endpoints
```

## Autonomous Pipeline (runs on Reddit's cloud)

| Scheduler Task | Cron | Endpoint | What It Does |
|---------------|------|----------|--------------|
| autopost_curated_4h | 0 */4 * * * | /internal/menu/post-curated | Posts baked payload content |
| autopost_multisource_feed_6h | 0 */6 * * * | /internal/menu/multi-source-feed | Collects from 6 subreddits, posts consolidated feed |
| autopost_short_report_8h | 0 */8 * * * | /internal/menu/post-now-short-report | Generates Macro Radar from subreddit data |
| autopost_status_ping_8h | 5 */8 * * * | /internal/menu/post-status | Status heartbeat |

## Multi-Source Subreddit Monitoring

Source subreddits (hardcoded in reddit-ops.ts):
- worldnews, geopolitics, economics, cryptocurrency, investing, stockmarket

The `collectFromMultipleSubreddits()` function pulls top 15 posts from each, sorts by engagement (score + comments×2), and `buildGazzettaFeedPost()` formats a consolidated "Reddit Intelligence Feed" with per-source breakdowns, cross-subreddit theme analysis, and top-5 stories.

## Known Bug (Fixed in v0.0.42)

**Symptom:** Every post appeared as just "hi" — title "hi", body "hi".
**Root cause:** Two files had hardcoded strings from initial scaffolding:
- `src/server/core/post.ts` line 6-7: `title: 'hi', text: 'hi'` — ignored `_payload.ts`
- `src/server/routes/triggers.ts` line 16-17: `title: 'hi', text: 'hi'` — ignored `createPost()`

**Fix:** `post.ts` now imports `LATEST_TITLE` and `LATEST_BODY` from `_payload.ts`. `triggers.ts` now calls `createPost()` with fallback chain: curated → Macro Radar → heartbeat.

## Verification Checklist

After `devvit install`, always verify:
1. Check the subreddit — the post should appear within 30 seconds
2. If only "hi" appears, check `post.ts` and `triggers.ts` for hardcoded strings
3. If nothing appears, check Reddit's mod queue / spam filter
4. The `onAppUpgrade` trigger fires asynchronously — wait 30s before checking
