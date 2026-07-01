# Deploy & Systemd Pitfalls — June 2026

## P0: NoNewPrivileges=yes Blocks sudo Silently

**Symptom:** `[deploy] FAIL(1) in 0.0s` every governor cycle.
STDERR: "sudo: The 'no new privileges' flag is set, which prevents sudo from running as root."

**Root cause:** `/etc/systemd/system/gazzetta-governor.service` has `NoNewPrivileges=yes`
which blocks ALL privilege escalation including sudo. The deploy step in governor.py uses
`sudo gsutil ...` and `sudo gcloud ...` — these fail silently.

**Impact:** Site served stale content for weeks. None of the Phase A/B frontend changes
reached CDN. Sidebar showed $0M for 6 narratives despite flows.json having real data.
trade_thesis fields existed in JSON but never rendered on the site. GAP filter and mobile
CSS patches never deployed. This was the silent root cause behind the "nothing changed"
user frustration.

**Fix:**
```
sudo sed -i 's/NoNewPrivileges=yes/NoNewPrivileges=no/' /etc/systemd/system/gazzetta-governor.service
sudo systemctl daemon-reload
```

The timer will pick up the change on next tick. Alternatively: `sudo systemctl restart gazzetta-governor.service`
but this may time out because the governor takes 60-90s.

**Verification after deploy:**
Run in `browser_console` on the live site:
```js
JSON.stringify({
  renderedArticles: document.querySelectorAll('#story-cards article').length,
  hasTradeThesis: STORIES[0].trade_thesis !== undefined,
  sidebarZeroM: Array.from(document.querySelectorAll('nav a')).filter(a => a.textContent.includes('0M')).length
})
```
- `hasTradeThesis` must be `true` (confirms B1 deployed)
- `sidebarZeroM` should be 0 when sidebar fix is deployed (C1)
- Article count should match VM stories.json count minus GAP<15 filtered

## P1: Telegram Unicode + parse_mode Conflict

**Symptom:** HTTP 400 from Telegram API.
**Root cause:** `parse_mode: "Markdown"` + Unicode box-drawing chars (━) + emoji (⚡💰📊🎯■)
break Telegram's Markdown parser.
**Fix:** Remove `parse_mode` from POST payload entirely. Set `disable_web_page_preview: True`.
Telegram renders Unicode natively in plain text mode.

## P2: Sidebar Data Desync

**Symptom:** Sidebar Domain Intelligence shows $0M for 6 narratives while flows.json has real
non-zero capital for ALL narratives.
**Root cause:** `build_frontend.py` sidebar JS reads from stories.json narrative aggregation,
not from flows.json which has `calculate_capital.py` computed values.
**Fix (C1):** Sidebar must read from flows.json `narrative_flows` dict (`total_capital_b`).

## Deploy Verification Checklist

After any deploy:
1. `ssh gazzetta-prod "wc -l /opt/gazzetta-di-kyiv/public/data/stories.json"` → note story count
2. Deploy to GCS: `sudo gsutil cp public/index.html gs://www.lagazzettadikyiv.com/`
3. CDN cache bust: `gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path='/*' --async`
4. Verify live: `curl -sI "https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html" | grep content-length`
5. Check browser: navigate with `?_v=RAND` and verify story count / features
