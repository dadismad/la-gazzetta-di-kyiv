# Live Price Frontend Merge (ANCHOR_ASSETS → _lastTickerMap)

## Pipeline Chain

```
fetch_live_prices.py  ──→  market_prices.json  ──→  window._lastTickerMap
       (CoinGecko)            (site/data/)              (app.js fetch)
                                                          ↓
                                                    Merge into ANCHOR_ASSETS
                                                          ↓
                                                    populateSidebar() reads
```

## Data Structure

`market_prices.json` structure (written by both `fetch_live_prices.py` and `db_to_json.py`):

```json
{
  "generated_at": "2026-06-11T...",
  "prices": {
    "BTC-USD": {"ticker": "BTC-USD", "price": 61875.98, "change_pct": 0.38, "direction": "up"},
    "SPY": {"ticker": "SPY", "price": 735.35, "change_pct": -0.23, "direction": "down"},
    "XAUUSD=X": {"ticker": "XAUUSD=X", "price": 2410, "change_pct": -1.87, "direction": "down"}
  },
  "asymmetry_scores": {...}, "total": 246
}
```

`window._lastTickerMap` is built by iterating `prices` entries:
```javascript
Object.entries(prices).forEach(([assetClass, p]) => {
    window._lastTickerMap[assetClass.toLowerCase()] = p;
    if (p.ticker) window._lastTickerMap[p.ticker.toLowerCase()] = p;
});
```

Result: each entry accessible by BOTH category key (`btc-usd`) and ticker key (`BTC-USD` lowered).

## Symbol Mapping

`ANCHOR_ASSETS` symbols → `_lastTickerMap` keys. ETF proxies need scale correction:

| ANCHOR_ASSETS | _lastTickerMap | Scale | Proxy Note |
|---|---|---|---|
| SPX | `spy` | ×10 | SPY ETF ≈ 1/10 SPX index |
| BRENT | `cl=f` | ×1 | Crude Oil Futures |
| GOLD | `gold` | ×1 | XAUUSD — direct match |
| BTC | `btc-usd` | ×1 | Bitcoin USD — direct match |
| NVDA | — | — | Not in feed → hardcoded fallback |
| DXY | — | — | UUP ETF ≠ USD Index (removed) |
| 10Y | — | — | TLT = ETF price, not yield (removed) |
| ETH | — | — | Not in feed → hardcoded fallback |
| SOL | — | — | Not in feed → hardcoded fallback |

## Merge Code (app.js, after `market_prices.json` fetch)

```javascript
const SYMBOL_MAP = {
  'SPX':  { key: 'spy',     scale: 10 },    // SPY ETF → S&P 500 index
  'BRENT':{ key: 'cl=f',    scale: 1  },    // Crude Oil Futures
  'GOLD': { key: 'gold',    scale: 1  },    // Gold via XAUUSD
  'BTC':  { key: 'btc-usd', scale: 1  },    // Bitcoin USD
};
ANCHOR_ASSETS.forEach(a => {
  const mapping = SYMBOL_MAP[a.symbol];
  if (!mapping) return;  // No live data → keep hardcoded
  const live = window._lastTickerMap[mapping.key];
  if (live && live.price) {
    const scaledPrice = live.price * mapping.scale;
    a.price = scaledPrice >= 1000 ? Math.round(scaledPrice).toLocaleString('en-US')
            : scaledPrice >= 1 ? scaledPrice.toFixed(2) : scaledPrice.toFixed(4);
    if (live.change_pct != null) {
      a.change = (live.change_pct >= 0 ? '+' : '') + live.change_pct.toFixed(1) + '%';
    }
    if (live.direction) {
      a.dir = live.direction === 'down' ? 'down' : live.direction === 'up' ? 'up' : a.dir;
    }
    a.stop = computeATRStop(a.entry, a.atr_pct, a.stop_atr_mult, a.bias);
  }
});
```

## Pitfalls

- **`SYMBOL_MAP` direction**: Map FROM ANCHOR_ASSETS symbol → TO _lastTickerMap key. NOT the reverse. 
  - ❌ `{ 'xau': 'GOLD' }` with `SYMBOL_MAP[a.symbol.toLowerCase()]` → `SYMBOL_MAP['gold']` = undefined
  - ✅ `{ 'GOLD': 'xau' }` → `SYMBOL_MAP['GOLD']` = 'xau'

- **Data structure changed**: CoinGecko raw had `{price, change_pct, source}`. Enriched format has `{ticker, price, change_pct, direction}`. Use `live.change_pct` and `live.direction` directly — don't recompute from price deltas.

- **ETF proxy scale mismatch (CRITICAL)**: SPY trades at ~1/10 of SPX. Without ×10 scale correction, sidebar shows "SPX 735" (87% apparent crash). Always verify scale factors when mapping ETF proxies to index symbols. For DXY and 10Y, no reliable scale factor exists → **remove from mapping entirely** (let them fall back to hardcoded).

- **Only map what can be accurate**: If a proxy can't represent the symbol accurately (UUP≠DXY, TLT≠10Y yield), remove it. It's better to show stale hardcoded values than live-but-wrong values.

- **Merge timing**: Must run AFTER `market_prices.json` fetch but BEFORE `populateSidebar()`. Current placement: right after the fetch's catch block, before `setInterval(fetchFlows, ...)`.
