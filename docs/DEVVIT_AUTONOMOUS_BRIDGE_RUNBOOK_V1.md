# Devvit Autonomous Bridge Runbook (V1)

## What is automated now
- `scripts/reddit_autonomous_pipeline.py` runs end-to-end:
  1) Reddit ingest (or fallback)
  2) Phase2 scoring
  3) Draft generation
  4) Reddit payload creation
  5) Reddit submission attempt with idempotency lock
- `scripts/reddit_submit_post.py` prevents duplicate posts via payload hash lock.

## What still requires subreddit owner/mod action (cannot be done from this runtime)
1. Ensure Devvit app is installed in target subreddit and approved by mods.
2. Grant app moderator/admin-equivalent permissions needed for posting/mod actions in subreddit settings.
3. Provide Reddit OAuth credentials in environment for unattended posting.

## Required environment variables
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USERNAME
- REDDIT_PASSWORD
- REDDIT_USER_AGENT
- optional: REDDIT_TARGET_SUBREDDIT=lagazzettadikyiv

## Validation command
`python3 scripts/reddit_autonomous_pipeline.py`

Expected behavior without creds:
- pipeline still builds payload
- submit step exits gracefully with `skipped: missing_credentials`

Expected behavior with creds:
- submit step returns `{ok:true, subreddit:..., title:...}`

## Safety controls
- Duplicate lock file: `data/.last_reddit_payload_hash`
- Short, evidence-linked payload only
- Fallback data source when Reddit API unavailable
