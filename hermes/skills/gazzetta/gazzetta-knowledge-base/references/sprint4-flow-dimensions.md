# Sprint 4: Portfolio Manager Upgrades — Flow Dimensions

## Summary

Added three portfolio-manager-grade fields to every flow object in `flows.json`:
- **Duration** — holding horizon signal (intraday / positional / structural)
- **Counterparty** — who's on the other side (retail / institutional / sovereign / corporate / mixed)
- **Scale** — 1-10 normalized score (amount_b × confidence_pct × pace_multiplier)

## Files

| File | Change |
|------|--------|
| `scripts/compute_flow_dimensions.py` | NEW — reads `data/flows.json`, computes 3 fields, writes back |
| `deploy_routine.sh` | Added call after `build_track_record.py`, before `build_site.py` |
| `public/app.js` | Duration/Counterparty/Scale badges in collapse view, 3 detail sections, 3 helper functions |
| `public/styles.css` | Scale bar (monospace gold), Duration badge (color-coded), Counterparty badge |
| `scripts/test_platform.py` | 0 missing fields, valid enum values, scale 1-10 int, flow_dimensions metadata |

## Field Derivation

### Duration
```
pace_multiplier >= 1.5 → intraday
pace_multiplier >= 0.5 → positional
else                  → structural
```

### Counterparty
Mapped from `flow_sources` array via keyword mapping:
- institutional/funds/pension/endowment/family_office/hedge_fund → institutional
- sovereign/central_bank/government → sovereign
- retail/individual → retail
- corporate/banking/treasury → corporate
- mixed when ≥2 types present

### Scale
```
normalized = min(amount_b / sector_max, 1.0)
raw = normalized × (confidence_pct/100) × min(pace_multiplier, 2.0) × 10
result = clamp(round(raw), 1, 10)
```

## Results

199 flows enriched, 0 missing fields. Distribution:
- Duration: 10 intraday, 189 positional
- Counterparty: 190 institutional, 6 mixed, 2 retail, 1 corporate
- Scale: 1-10 range across all flows

## Test Gate

570 tests passed (was 553 before Sprint 4 — 17 new assertions).
