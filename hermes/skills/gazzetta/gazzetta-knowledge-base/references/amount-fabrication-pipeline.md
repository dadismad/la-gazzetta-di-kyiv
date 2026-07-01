# Amount Fabrication Pipeline — Root Cause & Fix

Discovered June 2026. Stories like "UK court grants Allianz permission to sue" showed `$0.2B` — clearly fabricated. Traced through 3 scripts.

## The Fabrication Chain

### Step 1: `fetch_intel.py` — `extract_amount()`
Tries to find real `$XB` patterns in story text. Returns `None` when none found. This is correct.

### Step 2: `fetch_intel.py` — `context_amount()` (THE CULPRIT)
Called when `extract_amount()` returns `None`. Uses two-tier fallback:

1. **Entity keyword matching** — checks `entity_scales` from `config.yaml` for keywords like "fed", "nvidia", "bitcoin". Returns a hash-based amount in the entity's scale range. This is legitimate — if a story mentions the Fed, a $10-150B range is reasonable.

2. **Asset class fallback** (REMOVED) — when no entity matches, used `base_ranges` to fabricate a random amount based on MD5 hash: `amount = lo + (h % int((hi - lo) * 10)) / 10.0`. This is the root cause. A legal story about Allianz (insurance company, not in megacorps list) would get a random 0.01-0.5B because asset_class = "equities".

### Step 3: `approve_draft.py` — defaults to `5.0`
Line 96: `amount_b = suggested_flows.get("amount_b", 5.0)`
The 5.0 default triggered the scaling logic in `db_to_json.py`.

### Step 4: `db_to_json.py` — scaling logic
Detected the 5.0 sentinel value and scaled it down based on tier fractions:
- BREAKING → 12% of sector total
- DEVELOPING → 8%
- ACTIVE → 3%
- SETTLING → 0.5%

Result: a story with default 5.0 in a $300B sector at DEVELOPING tier → `$300B × 0.08 × uniqueness_mult` → produced random tiny amounts like 0.2, 0.3, 7.7.

## Fix Applied (June 2026)

### `fetch_intel.py` — `context_amount()`
Removed the asset class fallback. Now returns `None` when no entity keyword matches:
```python
# ── Asset class fallback (no entity matched) ──
# Return None — do NOT fabricate amounts for stories without real data.
return None
```

### `fetch_intel.py` — `generate_suggested_flows()`
Handles `None` amounts gracefully:
```python
if amount_b is None:
    claim = f"{direction} {asset_class}"  # No fake $XB prefix
else:
    claim = f"${amount_b}B {direction} {asset_class}"
```

### `approve_draft.py`
Changed defaults from `5.0` to no default (None):
```python
amount_b = suggested_flows.get("amount_b")  # None = no real amount extracted
```
Headline formatting handles None: `amt_str = f"${amount_b}B" if amount_b is not None else "—"`

### `db_to_json.py`
Explicit null check before scaling:
```python
has_explicit_null = ("amount_b" in cf and cf["amount_b"] is None)
if has_explicit_null:
    pass  # Leave as None — don't fabricate
elif not cf.get("amount_b") or is_default_amount:
    # ... existing scaling logic
```
`capital_at_stake` formatting handles None: `f"${amount}B" if amount is not None else "—"`

## Impact
- **Preventive only** — existing stories in `stories.json` still have old fabricated amounts. They'll age out as pipeline regenerates.
- **Entity-matched amounts still work** — stories mentioning "fed", "nvidia", "bitcoin" etc. still get scale-appropriate amounts.
- **Stories without real dollar figures** now show no amount prefix in teasers — just the headline. This is honest.
- **Teaser display in app.js already handles missing amounts** — `cf.amount_b ? ...` is falsy for `null`, so no `$XB` prefix is shown.

## Verification
After pipeline fix, run `db_to_json.py` and check:
```bash
python3 -c "
import json
d = json.load(open('data/stories.json'))
nulls = sum(1 for s in d['stories'] if s.get('capital_flow',{}).get('amount_b') is None)
print(f'{nulls}/{len(d[\"stories\"])} stories have null amount_b')
"
```
