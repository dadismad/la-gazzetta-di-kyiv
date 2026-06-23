# Data Layer Scripts v1.0 — traffic_cop, ingestion_triage, market_reality, contradiction_synthesizer

Four new Python scripts forming the complete autonomous data layer for Gazzetta di Kyiv. All use WAL-mode SQLite, atomic file writes, and integrate via the `traffic_cop` concurrency lock.

## Architecture

```
ingestion_triage.py ──→ ingestion_hashes table (SHA-256 dedup)
market_reality.py  ──→ data/market_prices.json (yfinance → AlphaVantage)
       ↓                        ↓
contradiction_synthesizer.py ──→ DeepSeek API ──→ public/data/stories.json
       ↑
traffic_cop.py (concurrency lock shared by all three)
```

## traffic_cop.py (159 lines)

SQLite-backed singleton concurrency lock. Prevents concurrent pipeline runs across systemd-managed processes.

- Table: `pipeline_state(id=1, state, started_at, pid, hostname, updated_at)`
- `PipelineLock.acquire()`: reads state row, returns False if PROCESSING
- WAL mode, 5000ms busy timeout
- Context-manager safe: `with PipelineLock() as lock:`
- CLI test mode: `python3 traffic_cop.py` runs 3s dummy sleep

## ingestion_triage.py (239 lines)

RSS + YouTube transcript ingestion with SHA-256 deduplication. The cost-control gate — duplicates never reach the LLM enrichment layer.

- Table: `ingestion_hashes(hash UNIQUE, source_url, source_type, title, text_preview, full_text, narrative_tag, processed, created_at)`
- 7 RSS feeds mapped to narratives: ECB, WNN, Reuters, SCMP, MIT Tech Review, SpaceNews, FierceBiotech
- YouTube transcript extraction via `youtube-transcript-api` with oEmbed title fallback
- Partial index: `WHERE processed = 0` for fast unprocessed-item queries
- CLI flags: `--rss-only`, `--youtube-only`, `-v VIDEO_ID`
- Duplicate check by URL before fetching transcript (saves API calls)
- Dependencies: `feedparser`, `youtube-transcript-api`, `requests`

## market_reality.py (250 lines)

Financial price fetcher with yfinance primary → AlphaVantage fallback. When yfinance times out or rate-limits, seamlessly cascades to AlphaVantage.

- 34 tickers mapped to 8 narratives + 5 benchmarks
- Tier 1: `yfinance` fast_info with `t.history(period="2d")` fallback
- Tier 2: `AlphaVantage` GLOBAL_QUOTE REST (requires `ALPHAVANTAGE_API_KEY`)
- Smart fallback: only rate-limits AlphaVantage when previous call used it (13s delay on AV, 0.5s otherwise)
- Output: `data/market_prices.json` with price, previous_close, change_pct, source, narrative
- CLI: `--ticker URA GLD ITA` for spot checks, `--all` for full sweep

## contradiction_synthesizer.py (568 lines)

DeepSeek-powered contradiction analysis pipeline. Bridges raw ingestion data to the frontend via atomic stories.json writes.

- Reads unprocessed items from `ingestion_hashes WHERE processed=0`
- Loads `data/market_prices.json` for market context
- Async batch: max 5 concurrent DeepSeek API calls with 1-3s jitter
- DeepSeek prompt demands: `headline, narrative_tag, they_say, reality, contradiction_gap (0-100), capital_volume_usd (integer)`
- `response_format: {"type": "json_object"}` for strict JSON output
- Story assembly: narrative_tag → container, contradiction_gap → tier, reality text → direction
- Atomic write: `stories.tmp.json` → validate → `os.replace()`
- Rate-limited items left unprocessed for next run; errors marked `processed=-1`
- Resilience: handles missing market_prices.json, corrupt existing stories.json, malformed API responses

## Integration

All three scripts self-lock via `traffic_cop` and can be chained in a cron job or systemd timer:

```bash
python3 scripts/ingestion_triage.py       # every 30min
python3 scripts/market_reality.py --all   # every 10min
python3 scripts/contradiction_synthesizer.py  # whenever unprocessed items exist
```

## DB Tables Created

- `pipeline_state(id, state, started_at, pid, hostname, updated_at)` — singleton concurrency row
- `ingestion_hashes(id, hash UNIQUE, source_url, source_type, title, text_preview, full_text, narrative_tag, processed, created_at)` — dedup store with partial index
- Both tables are created idempotently on first script run. `processed` column is added via ALTER TABLE if missing.
