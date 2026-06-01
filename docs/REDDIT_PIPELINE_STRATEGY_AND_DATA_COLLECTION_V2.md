# Reddit Pipeline Strategy & Data Collection Plan (V2)

## Objective
Integrate Reddit intelligence + publishing into the Gazzetta master workflow with production reliability and short-form narrative quality.

## Target Subreddit
- r/LaGazzettadiKyiv (installed as lowercase slug on Reddit APIs: `lagazzettadikyiv`)

## Pipeline Architecture
1. **Ingestion**
   - Source: Reddit OAuth API (`/r/{subreddit}/{hot|new|top}.json`)
   - Script: `scripts/reddit_ingest.py`
   - Output: `data/reddit_candidates.json`

2. **Scoring**
   - Script: `scripts/phase2_scoring.py`
   - Scores: captivation, capital_flow, beneficiary
   - Output: `data/phase2_scores.json`

3. **Drafting**
   - Script: `scripts/reddit_to_gazzetta_draft.py`
   - Output: `data/reddit_gazzetta_drafts.json`

4. **Posting payload generation**
   - Script: `scripts/reddit_post_payload.py`
   - Output: `data/reddit_post_payload.md`

5. **Publishing layer**
   - Devvit app menu endpoint in `lagazzettadikyiv` app handles moderated posting flows.
   - App command: `devvit install <subreddit> lagazzettadikyiv@latest`

## Collection Strategy
- Cadence:
  - hourly ingestion
  - daily synthesis for posting
- Subreddit coverage tiers:
  - Tier 1: geopolitics, economics, markets, technology
  - Tier 2: niche domains linked to active narratives
- Data quality filters:
  - minimum score/comments thresholds
  - duplicate-title collapse
  - source domain diversity checks

## Operational Controls
- Fail-safe when Reddit creds missing: fallback generation from in-house setups
- Explicit invalidation text in each generated post
- Keep Reddit post body concise and scannable

## Readiness Checklist
- [x] Devvit CLI available locally in app workspace
- [x] Logged in Devvit account
- [x] App exists and listed
- [x] App installed on target subreddit slug
- [ ] Automated publish trigger wired from Gazzetta cron to Devvit endpoint (next step)

## Known Gap
Devvit app posting is currently menu-driven (moderator action). Direct unattended API trigger from Gazzetta cron is not yet wired; workflow now prepares post payload automatically for one-click moderator post.