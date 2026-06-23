# UTM Telemetry Pattern

## Problem

How do you track which Telegram tier/broadcast drives clicks to the website without adding cookie banners, third-party analytics, or any new infrastructure?

## Solution

Inject UTM parameters into every Telegram link. CDN access logs natively record query strings — no new code, no cookies, no PII.

## Implementation

### Links by Tier

| Tier | UTM Tag | Where |
|---|---|---|
| Tier 1 (Tactical Bets) | `?utm_source=telegram&utm_medium=tier1` | `telegram_broadcast.py` format_story_for_telegram() HIGH/ELEVATED block |
| Tier 2 (Radar Alerts) | `?utm_source=telegram&utm_medium=tier2` | `telegram_broadcast.py` main() Tier 2 handling |
| Tier 3 (Macro Lens) | `?utm_source=telegram&utm_medium=tier3` | Hermes cron job prompt — appended to closer link |
| Standard signals | `?utm_source=telegram&utm_medium=signal` | `telegram_broadcast.py` SPECULATIVE block |

### Code Pattern

In `telegram_broadcast.py`, replace the static `link` variable with inline UTM URLs per tier:

```python
# HIGH/ELEVATED block
lines.append(f"Full brief: https://www.lagazzettadikyiv.com?utm_source=telegram&utm_medium=tier1")

# SPECULATIVE block
lines.append(f"Full brief: https://www.lagazzettadikyiv.com?utm_source=telegram&utm_medium=signal")

# Tier 2 radar alerts (in main())
radar_text = alert["text"] + "\n\nFull brief: https://www.lagazzettadikyiv.com?utm_source=telegram&utm_medium=tier2"
```

### Reading the Data

Parse CDN access logs (GCS or Cloud CDN logs) for UTM-tagged requests. Group by `utm_medium` to measure which tier drives the most clicks. No real-time dashboard needed — weekly manual review is sufficient for a channel at this scale.

## When to Upgrade

When UTM data consistently shows strong Telegram → web conversion over 2+ weeks, invest in Plausible or Umami for deeper behavioral analytics (time on page, scroll depth, return visits). Don't build the observatory before you know there are stars to observe.
