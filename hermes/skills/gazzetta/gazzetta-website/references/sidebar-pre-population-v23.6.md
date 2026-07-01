# Sidebar Pre-Population Pattern (v23.6)

## Pattern
Inject live data (sector heatmaps, trade hooks, sentiment gauges) into the static `index.html` at build time using Python string replacement. This avoids JS-rendered placeholders (`—`) and delivers populated sidebars on first paint.

## Why
The 3-column grid sidebars contain data-driven elements (trade hooks, velocity, sentiment, sector heatmaps) that would normally require JS to populate. Pre-populating them at build time eliminates the `—` placeholder flash and removes the need for fragile JS populator scripts that depend on `CAPITAL_FLOWS_DATA` being available.

## Recipe

```python
import json

with open('data/flows.json') as f: flows_data = json.load(f)
with open('index.html') as f: html = f.read()

# ── Trade Hooks: top 3 flows by pace ──
flows = sorted(flows_data['flows'], key=lambda f: f.get('pace_multiplier', 1), reverse=True)
hooks_html = ''
for fl in flows[:3]:
    ac = (fl.get('asset_class', '?')).upper()[:8]
    direction = fl.get('direction', '')
    pct = fl.get('confidence_pct', 50)
    sym = '↑' if direction == 'inflow' else '↓'
    cls = 'bullish' if direction == 'inflow' else 'bearish'
    hooks_html += f'<div class="side-hook-item" onclick="location.href=\'./flows.html\'">\n'
    hooks_html += f'  <span class="side-hook-symbol">{ac}</span>\n'
    hooks_html += f'  <span class="side-hook-dir {cls}">{sym} {direction.upper()[:3]}</span>\n'
    hooks_html += f'  <span class="side-hook-conv">{pct}%</span>\n</div>\n'

# Replace placeholder hooks with real data
old_hooks = '<div class="side-hooks" id="sideHooks">\n        <div class="side-hook-item"><span class="side-hook-symbol">—</span>...'
# → new_hooks = f'<div class="side-hooks" id="sideHooks">\n{hooks_html}      </div>'

# ── Sector Heatmap ──
sector_summary = flows_data.get('sector_summary', {})
sectors_html = ''
for sector, data in sorted(sector_summary.items(), key=lambda x: x[1]['total_b'], reverse=True):
    color = '#059669' if data['direction'] == 'inflow' else '#DC2626'
    sectors_html += f'<div class="fresh-item"><span class="fresh-dot" style="background:{color}"></span><span>{sector[:12]}</span><span class="fresh-age">${data["total_b"]:.1f}B</span></div>\n'

# ── Sentiment Gauge ──
inflow_count = sum(1 for f in flows_data['flows'] if f.get('direction') == 'inflow')
total = len(flows_data['flows'])
pct = round(inflow_count / max(total, 1) * 100)
sent_class = 'bullish' if pct >= 70 else 'bearish' if pct <= 30 else 'neutral'

old_sent = '<span class="side-sent-value">—</span>'
new_sent = f'<span class="side-sent-value {sent_class}">{pct}%</span>'

# ── Top Velocity ──
top = flows[0] if flows else {}
vel = top.get('pace_multiplier', 1)
old_vel = '<span class="side-vel-value">—</span>'
new_vel = f'<span class="side-vel-value">{vel:.1f}×</span>'

# Apply all replacements
html = html.replace(old_hooks, new_hooks)
html = html.replace(old_sent, new_sent)
html = html.replace(old_vel, new_vel)
# ... etc

with open('index.html', 'w') as f: f.write(html)
```

## When to run
- After `db_to_json.py` compiles new flows.json
- Before `shipit.sh` Stage 3 (hash_assets)
- Integrated into the build pipeline: the pre-population should happen as part of the standard deploy cycle

## Trade-offs
- **Pro**: Instant render, no JS required, no flash of `—` placeholders
- **Con**: Data is frozen at build time — flows update every 60min via cron, so sidebar data lags between deploys. Mitigated by the deploy cron running every 60min.
- **Alternative**: JS populator (used in v23.5) works but depends on `CAPITAL_FLOWS_DATA` being available before DOM render. The pre-population approach is preferred for reliability.
