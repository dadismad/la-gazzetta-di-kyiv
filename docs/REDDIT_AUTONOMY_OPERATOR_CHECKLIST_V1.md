# Reddit Autonomy Operator Checklist (Devvit-first)

## What is already autonomous
- Devvit app installed on r/lagazzettadikyiv (v0.0.3).
- External unattended bridge is active (`gazzetta-reddit-autonomous-bridge`, every 8h).
- Pipeline has idempotency lock to prevent duplicate posts.
- Fallback generation keeps workflow alive when Reddit ingest is unavailable.

## What ONLY a subreddit owner/mod can do in Reddit UI
1. Ensure app install remains approved in subreddit.
2. Keep app/mod permissions enabled for posting and moderation surfaces.
3. Confirm automation actions are visible in mod menu after upgrades.

## 60-second manual verification in Reddit UI
1. Open r/LaGazzettadiKyiv mod tools.
2. Confirm app `lagazzettadikyiv` appears in installed apps.
3. Confirm app has moderator action scope for posting.
4. Trigger “Create a new post” once and verify post appears.

## Runtime secrets required for fully unattended posting
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USERNAME
- REDDIT_PASSWORD
- REDDIT_USER_AGENT

Without these, bridge safely skips submit but still generates payload.

## Dry-run command
`python3 scripts/reddit_autonomous_pipeline.py`

## Live-post command (welcome)
`REDDIT_POST_PAYLOAD=data/reddit_welcome_post.md REDDIT_TARGET_SUBREDDIT=lagazzettadikyiv python3 scripts/reddit_submit_post.py`

## Safety controls
- Duplicate lock: `data/.last_reddit_payload_hash`
- Short-form post template
- Evidence-link requirement
- Invalidation trigger requirement
