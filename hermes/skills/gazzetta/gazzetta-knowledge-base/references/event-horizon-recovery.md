# Event Horizon — Standalone Page Recovery

Discovered June 2026. The Event Horizon page rendered blank (9 elements, no content) despite
no JS errors in console. Root cause: the inline `<script>` block was truncated — missing
the closing `})();</script></body></html>` and the `init()` call.

## Symptoms

- Page loads with 9 elements (masthead + heading only)
- `browser_console` shows no JS errors
- `typeof initEventHorizon` → `undefined`, all functions missing
- `document.querySelectorAll('script')` shows 1 inline script but truncated
- File ends mid-function: `const prices = await fetchPrices();` with no closing

## Root Cause

A previous `patch()` operation on the file (nav fix) caused truncation. The `patch` tool
can lose trailing content when the replacement is shorter than the original. Standalone
pages (event_horizon.html, flow-nodes.html) that contain all their logic in a single inline
`<script>` block are especially vulnerable — losing just a few closing lines breaks the
entire page silently.

## Recovery Procedure

### Step 1: Check if file is truncated
```bash
tail -5 event_horizon.html
# Should end with: })();</script>\n\n</body>\n</html>
# If it ends mid-function, the file is truncated.
```

### Step 2: Find the last good commit
```bash
git log --oneline event_horizon.html | head -5
# Check each commit for the closing tags:
git show <commit>:event_horizon.html | tail -5
```

### Step 3: Restore from git
```bash
git show <good_commit>:event_horizon.html > event_horizon.html
```

### Step 4: Re-apply your fixes
The restored file won't have your recent changes (nav unification, CORS proxy, etc.).
Re-apply them AFTER restoration using `patch()`.

### Step 5: Verify integrity before deploy
```bash
tail -6 event_horizon.html
# Must show:
#   }
# })();
# </script>
#
# </body>
# </html>
wc -l event_horizon.html  # Should be 1220+
```

## CORS Proxy Pattern

Event Horizon fetches live Yahoo Finance tickers from the browser. Yahoo Finance's
`query1.finance.yahoo.com` blocks browser CORS requests. Fix: prepend a CORS proxy.

```javascript
// BEFORE (broken — CORS blocked):
const url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + symbol + '?...';
const r = await fetch(url, { headers: { 'User-Agent': '...' } });

// AFTER (works via corsproxy.io free tier):
const yahooUrl = 'https://query1.finance.yahoo.com/v8/finance/chart/' + symbol + '?...';
const proxyUrl = 'https://corsproxy.io/?' + encodeURIComponent(yahooUrl);
const r = await fetch(proxyUrl);
```

Note: `corsproxy.io` is a free tier service. It may have rate limits. For production,
consider a server-side price fetcher that writes to `market_prices.json` and have the
page load from there as primary source, with live fetch as fallback.

## Verification Checklist

After deploying event_horizon.html:
1. `curl -sI https://www.lagazzettadikyiv.com/event_horizon.html` → HTTP/2 200
2. Browser console: `document.getElementById('ehBarometer')?.textContent?.slice(0,40)` → "Aggregate Geopolitical Pressure"
3. Browser console: `document.getElementById('ehChokepoints')?.innerHTML?.length` → >1000
4. Browser console: `document.getElementById('ehProMonitor')?.innerHTML?.length` → >1000
5. Browser console: `typeof initEventHorizon` should NOT be undefined
