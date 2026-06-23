# Contextual Scaling & Sentiment Meter (v23.0)

**Deployed: 2026-06-10. Replaces incomprehensible "100% indicator" with capital flow sentiment.**

## Sentiment Meter (in flows.json)
```json
"sentiment_meter": {
  "inflow_ratio": 75,
  "outflow_ratio": 25,
  "total_inflows_b": 438.3,
  "total_outflows_b": 145.2,
  "net_flow_b": 293.1,
  "scale": "systemic"
}
```

## Contextual Scale
- **Speculative** ($10M–$2B): Crypto, defense, tech, small-cap flows
- **Systemic** ($2B–$500B): Sovereign, institutional, central bank flows

## Implementation (db_to_json.py)
```python
"sentiment_meter": {
    "inflow_ratio": round(total_inflows / max(total_inflows + total_outflows, 1) * 100),
    "outflow_ratio": round(total_outflows / max(total_inflows + total_outflows, 1) * 100),
    "scale": "systemic" if (total_inflows + total_outflows) >= 5 else "speculative",
}
```

## COALESCE Protection
- Never allow $0.0 in amount_b — validate at db_to_json Stage 1
- Never allow hardcoded $5.0B — derive from entity_scales in config.yaml
- `test_platform.py` Round 2 checks for 0-amount flows and $5B uniformity
