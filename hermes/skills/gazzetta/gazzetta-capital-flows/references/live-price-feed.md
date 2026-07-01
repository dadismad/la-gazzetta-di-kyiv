# Live Price Feed — CoinGecko + Alpha Vantage

## Purpose

Fetches real-time asset prices for display on the Gazzetta di Kyiv site.
Powers live ticker sidebar and stop-level settlement on trade cards.

## Script

`scripts/fetch_live_prices.py`

## Data Sources

### CoinGecko (free tier, no API key)

Endpoint: `https://api.coingecko.com/api/v3/simple/price`

Assets tracked:
- BTC → `bitcoin`
- ETH → `ethereum`
- SOL → `solana`
- XAU (gold proxy) → `tether-gold`

Returns: `{price: USD, change_24h: pct, source: "CoinGecko"}`

Rate limit: ~10-30 calls/minute on free tier. Use `time.sleep(0.5)` between calls
if batching multiple endpoints.

### Alpha Vantage (free tier, API key required)

Requires `ALPHA_VANTAGE_KEY` env var or parsing from `custom_providers` JSON.

Endpoint: `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SYM&apikey=KEY`

Assets: SPX (^GSPC), VIX (^VIX), DXY (DX-Y.NYB), US10Y (^TNX), WTI (CL=F), QQQ

Returns: `{price: USD, change_pct: pct, source: "Alpha Vantage"}`

Rate limit: 5 calls/minute on free tier. Script sleeps 0.3s between calls.

## Output

`site/data/market_prices.json`:

```json
{
  "generated_at": "2026-06-10T20:31:00Z",
  "assets": {
    "BTC": {"price": 87500.50, "change_24h": 2.1, "source": "CoinGecko"},
    "SPX": {"price": 5780.25, "change_pct": -0.3, "source": "Alpha Vantage"}
  },
  "total": 4
}
```

## Pipeline Integration

Stage 1.05 in `shipit.sh` — runs after multi-persona enrichment, before related links.

```bash
$PYTHON "$PROJECT/scripts/fetch_live_prices.py" || echo "  ⚠ Live prices skipped (non-critical)"
```

Non-critical — site operates normally without live prices (uses cached last-known values).

## API Key Extraction

Same pattern as multi-persona enrichment. Falls back to `custom_providers` JSON:

```python
key = os.environ.get("ALPHA_VANTAGE_KEY", "")
if not key:
    providers = json.loads(os.environ.get("custom_providers", "[]"))
    for p in providers:
        if "alpha" in p.get("name", "").lower():
            key = p.get("api_key", "")
            break
```

## Session Reference

June 10, 2026: Built `fetch_live_prices.py`. CoinGecko working (4 assets).
Alpha Vantage needs API key configuration. Integrated as Stage 1.05 in shipit.sh.
