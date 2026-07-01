# CCO + CDO Agent Architecture — June 2026

Executive Board Expansion (Sprints 7-9): Multi-agent omni-channel distribution
and design compliance auditing on GCP Cloud Run.

## Architecture

```
                        gazzetta.db
                            |
                    db_to_json.py (every 10m)
                            |
            +---------------+---------------+
            |               |               |
     stories.json      flows.json    market_prices.json
            |               |               |
            +-------+-------+-------+-------+
                    |               |
              CCO Agent        CDO Agent
         (distributor)     (design auditor)
                    |               |
        +---+---+---+---+       +---+---+
        |   |   |   |           |       |
       TG  X  Rdt NL        Audit    Screenshots
```

**Agents consume, never produce.** They read from GCS bucket artifacts,
never write to `stories.json`, `flows.json`, or `gazzetta.db`.

## CCO Agent (Chief Content Officer)

### Cloud Run Jobs

| Job | Schedule | Memory | Entrypoint | Status |
|-----|----------|--------|------------|--------|
| cco-distributor | */30 min | 512MiB | cco_entrypoint.py | LIVE |
| cco-newsletter-daily | Daily 06:00 UTC | 512MiB | cco_newsletter.py --mode daily | LIVE |
| cco-newsletter-weekly | Monday 06:00 UTC | 512MiB | cco_newsletter.py --mode weekly | LIVE |

### Curation Engine (`cco_curate.py`)

Impact formula: `impact_score = contradiction_score * (confidence / 100)`

The `contradiction_score` field is on a 0-100 scale (from the DB). The `confidence`
field is **qualitative** ("low"/"medium"/"high"), not numeric. Must map:

```python
QUALITATIVE_MAP = {
    "high": 85, "medium_high": 75, "medium": 65,
    "medium_low": 50, "low": 35, "very_low": 15, "none": 5,
}
```

**Platform thresholds:**

| Platform | Top N | Min Score | Max Age | Mode |
|----------|-------|-----------|---------|------|
| Telegram | 3 | 0.15 | 24h | LIVE POST |
| Reddit | 1 | 0.25 | 24h | Draft (pending OAuth) |
| X.com | 3 | 0.10 | 12h | Draft (pending $5 credit) |
| Newsletter | 5 | 0.10 | 24h | Draft (pending API key) |

### Distribution Pipeline

1. `cco_curate.py` reads `stories.json` from GCS, ranks by impact
2. `cco_telegram.py` formats in THE BRIEF/THE CLAIM register, posts via Bot API
3. `cco_reddit.py` formats in THE DISPATCH register, saves to `cco_drafts/reddit/`
4. `cco_x.py` formats 3-5 tweet threads (280 chars), saves to `cco_drafts/x/`
5. `cco_newsletter.py` formats daily/weekly briefs, saves to `cco_drafts/newsletter/`
6. `cco_drafts/posted_stories.jsonl` — idempotency log (story_id, platform, posted_at)

### Telegram Formatting

**Use HTML parse_mode, not Markdown.** Story content contains special characters
(`$`, `%`, `+`, `_`) that break Markdown parsing, producing HTTP 400 errors.

```python
# CORRECT:
escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
payload = {"chat_id": CHAT_ID, "text": escaped, "parse_mode": "HTML"}

# WRONG (causes 400):
payload = {"parse_mode": "Markdown"}
```

**Chat IDs:**
- @LaGazzettadiKyiv channel: `-1003990434181`
- Stocchi Labs group: `-1003796560949`

### Platform Formatter Pitfall: `--body` Arg Mismatch

The entrypoint (`cco_entrypoint.py`) passes `--body` to all platform formatters.
But `cco_x.py` does not accept `--body` — its argparser only has `--headline`,
`--they-say`, `--reality`, `--source`, `--contradiction`, `--confidence`, `--asset`.

**Symptom:** X drafts fail silently with empty stderr. The subprocess crashes on
unrecognized argument before producing output.

**Fix:** Remove `--body` from the base args list in `process_drafts()` and only
add it for platforms that accept it (Reddit). Pass `--asset` for X only.

## CDO Agent (Chief Design Officer)

### Cloud Run Job

| Job | Schedule | Memory | Entrypoint | Status |
|-----|----------|--------|------------|--------|
| cdo-auditor | Every 2h | 1GiB | cdo_entrypoint.py | DEPLOYED |

### Verification Pyramid (SOP R7 enforced)

1. **`page.evaluate(getComputedStyle())`** — PRIMARY (computed styles, DOM state)
2. **`page.screenshot()`** — SECONDARY (visual confirmation, never color verification)

Seven audit dimensions at three breakpoints (desktop 1280px, tablet 768px, mobile 400px):
masthead color, masthead font, card background, card count (>=30), nav background,
horizontal overflow (mobile only), JS console errors.

Reports saved to `cdo_audits/audit_{timestamp}.json` in GCS. Auto-cleaned after 7 days.

### Docker Image (gazzetta-agents)

Separate from pipeline image — includes Playwright + Chromium for CDO browser audits.

```dockerfile
FROM python:3.11-slim
RUN apt-get install -y libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
RUN pip install google-cloud-storage google-cloud-secret-manager playwright
RUN playwright install chromium && playwright install-deps chromium
```

Build from `agents_build/` subdirectory (standard Dockerfile name, not `-f` flag).

## gcloud Secret Mount — `:latest` Redaction Workaround

The terminal tool redacts the `:latest` suffix from `--set-secrets` flags.
Workaround: use `gcloud run jobs replace` with a YAML config containing:

```yaml
env:
- name: TELEGRAM_BOT_TOKEN
  valueFrom:
    secretKeyRef:
      name: telegram-bot-token
      key: latest
```

Apply: `gcloud run jobs replace /tmp/job.yaml --region=REGION --project=PROJECT`

## Secret Manager Keys

| Secret | Platform | Status |
|--------|----------|--------|
| deepseek-api-key | Pipeline LLM | PROVISIONED |
| telegram-bot-token | Telegram alerts + CCO posting | PROVISIONED |
| reddit-client-id | Reddit OAuth | AWAITING C-SUITE |
| reddit-client-secret | Reddit OAuth | AWAITING C-SUITE |
| reddit-username | Reddit account | AWAITING C-SUITE |
| reddit-password | Reddit account | AWAITING C-SUITE |
| newsletter-api-key | SendGrid/Mailchimp | AWAITING C-SUITE |
