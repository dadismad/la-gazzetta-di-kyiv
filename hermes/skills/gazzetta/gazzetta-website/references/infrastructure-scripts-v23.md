# Infrastructure Scripts (v23.0 — June 2026)

## gcp_monitor.py

Monitors Gazzetta di Kyiv GCP health:
- SSL certificate validity (openssl s_client)
- Site reachability (HTTP 200 + headers)
- Deploy freshness (deploy_report.txt check)
- Anti-lying protocol ($5.0B/undefined scan on public HTML)
- GCS storage usage (Always Free tier: 5GB limit, reports % used)

Output: `data/gcp_monitor_status.json`
Log: `data/gcp_monitor.log`
Run: `.venv/bin/python scripts/gcp_monitor.py`

## marketing_bot.py

Reddit marketing engine:
- 10 target subreddits: r/quant, r/finance, r/geopolitics, r/investing, r/economics, r/CryptoCurrency, r/stocks, r/wallstreetbets, r/Forex, r/Commodities
- Keyword scoring per subreddit (maps subreddit → relevant keywords)
- Matches stories to subreddits by entity_tags + headline/body keyword overlap
- Generates alpha-point posts (headline + cf_line + summary + THE PLAY + URL)
- Capped at 500 chars for Reddit-friendliness

Output: `data/marketing_candidates.json`
Run: `.venv/bin/python scripts/marketing_bot.py`

## SEO & Trust Pages

All deployed via `shipit.sh` Stage 4 to GCS:

| File | Purpose |
|------|---------|
| `site/robots.txt` | All routes, 5s crawl-delay, sitemap ref |
| `site/sitemap.xml` | 18 URLs, hreflang alternates |
| `privacy.html` | No cookies, no tracking, no PII |
| `terms.html` | Not financial advice, IP, liability |
| `contacts.html` | Telegram/X/Reddit, partnerships |

## Font Size Floor (v23.0)

| Size | Before | After |
|------|--------|-------|
| 7px | 11 occurrences | 0 |
| 8px | 14 occurrences | 0 |
| 9px | 47 occurrences | 47 (intentional) |

Detection: `grep -c 'font-size: [7-8]px' styles.css` must return 0.
