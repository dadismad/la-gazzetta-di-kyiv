# Executed Research Synthesis — Reddit/Devvit Autonomous Bundle Best Practices (V1)

## Executive summary
- Use a **dual-lane pipeline**: deterministic data lane + editorial inference lane.
- Keep Devvit as trusted subreddit-native execution surface; keep external bridge for failover.
- Enforce idempotent posting and cooldown windows.
- Rank content by blended score: captivation + capital-flow + novelty + contradiction.
- Keep platform-specific compression (Reddit 120–180 words, Telegram ~90 words).
- Build interlink mesh: each placement links the other two.
- Add lifecycle states: DRAFT -> READY -> POSTED -> REVIEWED.
- Measure both attention and decision quality (invalidations hit-rate).
- Prefer explicit actor-claim-cause-effect format.
- Treat maintenance as product: runbooks, alerts, and schema checks.

## Best-practice architecture
- Ingest: Reddit + internal setups; normalize to common schema.
- NLP: claim extraction, contradiction map, narrative cluster, attention decay.
- Decision: rank top opportunities; generate single-source payload objects.
- Publish: Devvit menu/trigger plus unattended bridge fallback.
- Observe: logs, post ids, duplicate lock hash, freshness timestamps.

## Placement integration checklist
- Website: show capital leader + contradiction lens + source links + Reddit/Telegram links.
- Reddit: pin welcome + daily concise brief + one invalidation trigger.
- Telegram: shorter post variant from same payload object.

## Immediate implementation actions (executed)
- Added interlinking links on homepage to Reddit and Telegram.
- Added modernized dark visual layer for current site.
- Deployed Devvit app welcome-post logic and branding updates.
- Kept unattended bridge with idempotency lock and payload override.

## 30/60/90 direction
- 30d: schema hardening + post outcome tracking.
- 60d: comment-level semantic feedback loop.
- 90d: adaptive cadence optimization by topic/market regime.
