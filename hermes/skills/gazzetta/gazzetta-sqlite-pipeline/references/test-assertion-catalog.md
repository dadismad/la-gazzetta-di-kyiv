# test_platform.py — Full Assertion Catalog

## Round 1: Poison Value Detection (44 assertions)

Scans 11 product pages for forbidden strings in body content:

| Forbidden | Label | Match Method |
|---|---|---|
| `undefined` | undefined JavaScript value | case-insensitive substring |
| `null` | null value | case-insensitive substring |
| `NaN` | NaN numeric value | word-boundary regex `\bNaN\b` |
| `[]` | empty array literal | substring |

Script/style tags are stripped before scanning. HTML tags are removed. Word-boundary match on NaN prevents false positives from words like "financial".

## Round 2: Flow Data Integrity (28 assertions)

For every story in `data/stories.json` that has `impacted_flows`:

- **amount_b non-zero**: `capital_flow.amount_b > 0`
- **pace_multiplier non-zero**: `capital_flow.pace_multiplier > 0`
- **Flow ID valid**: every ID in `impacted_flows` exists in `flows.json`
- **Cross-verification**: story's `capital_flow.amount_b` matches the linked flow's `amount_b` (tolerance ±0.01)

Plus aggregate checks:
- At least 1 story has linked flows
- `flows.json.total_flows_tracked > 0`
- `flows.json.aggregate_confidence` is a number

## Round 3: HTML Structure Validation (55 assertions)

For each of 11 product pages:

- `<html>` tag present
- `<body>` tag present
- Body text length > 100 characters
- Links to styles.css (checks `<link rel="stylesheet">` with "styles" in href)
- Has `<title>` or `<h1>` with non-empty content

## Round 4: Timestamp Freshness (4 assertions)

On `index.html` only:

- Freshness elements found: checks `#storyFreshness`, `#flowFreshness`, `#signalFreshness`, `.freshness-ago`, `.timestamp`, `[data-freshness]`
- Hero indicators present: checks `.hero-indicator`, `.hero-stats`, `.hero-stat`, `#heroIndicators`
- Services grid present: checks `.services-grid`, `.service-card`, `.persona-card`
- Teaser containers present: checks `.teaser-list`, `.teaser-container`, `[id$='TeaserContent']`

## Round 5: JSON Consistency (8 assertions)

For `stories.json` and `flows.json`:

- `data/` file exists
- `site/data/` file exists
- Story/flow counts match between data/ and site/data/
- `generated_at` timestamp is present
- `generated_at` is less than 24 hours old

## Usage

```bash
python3 scripts/test_platform.py           # full suite
python3 scripts/test_platform.py --quick   # skip Rounds 3-5 (HTML structure, timestamps, JSON)
python3 scripts/test_platform.py --strict  # exit on first failure
```

Exit codes: 0 = all pass, 1 = failures detected (abort deploy).
