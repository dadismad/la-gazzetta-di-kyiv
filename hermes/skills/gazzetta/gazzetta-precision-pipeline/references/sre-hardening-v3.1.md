# SRE Hardening (v3.1, commit cc002e9)

Ratified June 2026. Three SRE patterns injected into the core pipeline scripts
to prevent site crashes from concurrent access, partial writes, or API failures.

## 1. SQLite WAL Mode + Busy Timeout

**Problem:** When `fetch_intel.py` writes to `gazzetta.db` while `db_to_json.py`
reads from it, SQLite returns "database is locked" (SQLITE_BUSY). This kills
the pipeline.

**Fix (injected into `db_to_json.py` and `intel_to_stories.py`):**
```python
conn = sqlite3.connect(str(DB_PATH))
conn.execute("PRAGMA journal_mode=WAL")       # Writers don't block readers
conn.execute("PRAGMA busy_timeout=5000")       # Wait 5s before giving up
conn.row_factory = sqlite3.Row
```

WAL mode allows concurrent reads during writes. `busy_timeout` makes writers
retry for 5 seconds instead of failing immediately.

## 2. Atomic JSON Writes

**Problem:** If `db_to_json.py` dies mid-write, the live site serves a
half-written `stories.json`. The browser parses corrupted JSON, the site
goes blank, and CDN caches the broken file.

**Fix (injected into `db_to_json.py` `compile_containers()`):**
```python
out_path = DATA / "stories.json"
tmp_path = DATA / "stories.tmp.json"

# Write to temp file
with open(tmp_path, "w") as f:
    json.dump(doc, f, indent=2, ensure_ascii=False)

# Validate: re-read and verify structure
with open(tmp_path, "r") as f:
    validated = json.load(f)

required_keys = ["generated_at", "containers", "all_stories", "total_stories"]
for key in required_keys:
    if key not in validated:
        raise ValueError(f"VALIDATION FAILED: missing key '{key}'")

# Atomic rename — instant, no partial read possible
os.replace(tmp_path, out_path)
```

`os.replace()` is atomic on the same filesystem. The live site never sees the
`.tmp` file. It either serves the old `stories.json` (if validation fails) or
the new one (atomically swapped in). There is no in-between state.

## 3. API Circuit Breaker

**Problem:** `yfinance` or RSS feeds timeout. Previously, the entire pipeline
crashed because `fetch_market_data.py` raised an unhandled exception. One bad
ticker killed the whole run.

**Fix (new file: `scripts/circuit_breaker.py`, injected into both API scripts):**
```python
import time, random

MAX_RETRIES = 3
BASE_DELAY = 2.0   # seconds
MAX_JITTER = 1.0    # seconds

def api_call_with_retry(fn, name="API", max_retries=MAX_RETRIES):
    for attempt in range(1, max_retries + 1):
        try:
            result = fn()
            return result, True
        except Exception as e:
            delay = BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, MAX_JITTER)
            if attempt < max_retries:
                time.sleep(delay)
            else:
                return None, False
    return None, False
```

**Usage in `fetch_market_data.py`:**
```python
def fetch_24h_change(ticker_symbol):
    def _fetch():
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="5d")
        if hist.empty or len(hist) < 2:
            raise ValueError(f"No price data for {ticker_symbol}")
        return hist
    
    result, ok = api_call_with_retry(_fetch, name=f"yfinance:{ticker_symbol}")
    if not ok:
        return {"ticker": ticker_symbol, "error": "circuit breaker: exhausted retries", ...}
    # process result...
```

**Usage in `fetch_intel.py`:**
```python
def fetch_feed(feed_cfg):
    def _fetch():
        req = urllib.request.Request(url, headers={...})
        resp = urllib.request.urlopen(req, timeout=20, context=ctx)
        ...
        return parsed.entries
    
    result, ok = api_call_with_retry(_fetch, name=f"feed:{feed_cfg['name']}")
    if not ok:
        print(f"  {feed_cfg['name']}: circuit breaker exhausted — skipping feed")
        return []
    return result
```

## Updated Pipeline Chain

The canonical pipeline chain (defined in `config.yaml`, executable via `scripts/pipeline_chain.sh`):

```
fetch_intel.py          → Raw news → SQLite drafts table
intel_to_stories.py     → Drafts → Stories table with time decay + confidence
decay_stories.py        → Archive old, promote fresh
validate_stories.py     → Check required fields, repair missing
generate_flows.py       → Stories → Capital flow extraction
db_to_json.py           → Compile all → 6-container stories.json (atomic write)
test_platform.py        → QA gate (BLOCKING — deploy only if pass)
```

All scripts resolve paths relative to project root via `config.yaml`.
No hardcoded `/Users/alexstocchi` paths remain.
