# Reddit Access Resilience Playbook (Compliant, Production-Grade)

## Non-negotiable policy
This playbook avoids ban-evasion and terms circumvention. It is built for reliability **within** Reddit rules:
- official API auth
- rate-limit aware ingestion
- caching/retries/backoff
- graceful degradation when blocked

## Why direct scraping fails
- Cloudflare/bot challenges
- anonymous traffic reputation limits
- anti-automation controls on web HTML endpoints

## Correct architecture
1. **Use Reddit OAuth API** (script app credentials)
2. **Ingest via JSON API endpoints** using bearer token
3. **Persist normalized content** in local store
4. **Run enrichment pipeline** (summaries, scoring, extraction)
5. **Fallback paths** when unavailable

## Recommended data sources (priority order)
1. OAuth API: `/r/{sub}/hot`, `/new`, `/top`, comments, post bodies, metadata
2. Pushshift-like mirrors only if policy-approved (verify legality each use)
3. Manual analyst queue for blocked/high-value items

## Operational safeguards
- Unique User-Agent with contact
- Token refresh flow + secret rotation
- Exponential backoff on 429/403/5xx
- Local cache TTL to reduce repeated calls
- Circuit breaker: pause source after repeated denials
- Structured logs for block reason taxonomy

## Data model (minimum)
- post_id, subreddit, title, selftext, url
- score, num_comments, created_utc
- author (if available), flair, domain
- fetched_at, source_endpoint, fetch_status

## Captivation-scoring fields
- hook_strength (numerical specificity + tension)
- novelty_score
- contradiction_score
- actionability_score
- credibility_signal (outbound refs, evidence density)

## Block/ban adversary handling (legit)
- 401: refresh token
- 403: permission/scope check, app review
- 429: backoff + queue defer
- challenge/HTML block: switch to API path only

## Integration target for Gazzetta
- Daily ingestion cron job
- Top-N candidate post detector
- Editorial output in Gazzetta schema:
  - hook
  - actors
  - contradiction
  - 24–72h bet snippet
  - invalidation

## Deliverables implemented in this repo
- `scripts/reddit_ingest.py` OAuth ingestion scaffold
- `data/reddit_candidates.json` output artifact
- this playbook
