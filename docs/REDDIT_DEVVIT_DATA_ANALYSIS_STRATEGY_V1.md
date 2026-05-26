# Reddit + Devvit Data Analysis Strategy (GitHub-Centric)

## Recommended method
Use GitHub as the analysis control plane:
- store raw snapshots (`data/raw/reddit/*.json`)
- store normalized tables (`data/normalized/*.json`)
- store interpretations (`data/insights/*.md`)
- publish derived reports to site + Reddit + Telegram from same payload object.

## Why this method
- versioned, auditable interpretations
- easy rollback and diff on narrative changes
- reproducible content generation pipeline

## Integration pattern
1. Devvit app collects subreddit and context signals.
2. Pipeline normalizes + scores + interprets.
3. Commit artifacts to repo on schedule.
4. Build compact post variants by placement:
   - Reddit short report
   - Telegram ~90-word post
   - Website narrative cards
5. Post via Devvit autonomous cycle (every 8h).

## Best-practice controls
- idempotent post lock
- freshness cutoff (skip stale payloads)
- contradiction lens mandatory
- asset-pricing projection + invalidation mandatory
- evidence links mandatory

## Next technical upgrades
- add `data/insights/reddit_analysis_latest.md` generator
- add `site/research.html` reader for latest interpretation artifacts
- add post-outcome feedback loop from Reddit comments
