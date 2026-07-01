# Live Data Format — stories-v4.json and flows.json

## stories-v4.json

Deployed to: `gs://www.lagazzettadikyiv.com/data/stories-v4.json`
Produced by: `contradiction_synthesizer.py v1.0`
Refreshes: every 10 min via governor systemd timer

### Top-level structure
```json
{
  "generated_at": "2026-06-20T14:10:39.992121+00:00",
  "generated_by": "contradiction_synthesizer.py v1.0",
  "containers": {
    "<narrative_key>": {
      "title": "Narrative Title",
      "subtitle": "Description",
      "count": 108,
      "stories": [ ... ]
    }
  }
}
```

### 8 Narrative Keys
`dollar_decline`, `energy_sovereignty`, `deglobalization`, `china_ascent`, `space_economy`, `gene_editing`, `tech_convergence`, `wealthy_sports`

### Story Object Fields
| Field | Type | Example | Notes |
|-------|------|---------|-------|
| story_id | int | 10043 | Unique ID |
| headline | string | "ECB Data Fails to Dent Dollar Strength" | Title |
| they_say | string | "The ECB's data suggests..." | Media consensus narrative |
| reality | string | "The UUP rose 0.43%..." | What markets actually did |
| container | string | "dollar_decline" | Narrative key |
| contradiction_score | int | 85 | 0-100, higher = more divergence |
| contradiction_gap | int | 85 | Same as score (legacy alias) |
| capital_volume_usd | int | 5000000000 | $5B |
| confidence_pct | int | 65 | DeepSeek confidence |
| tier | string | "BREAKING" | Tier classification |
| pillar | string | "dollar_decline" | Legacy field |
| thesis | string | "" | Optional thesis statement |
| capital_flow | object | See below | Direction + amount |
| tags | string[] | ["dollar_decline"] | Tag list |
| multi_persona | object | {} | Persona analysis |
| sector | string | "currencies" | Asset sector |
| source_name | string | "RSS" | Source type |
| source_url | string | "https://..." | Original URL |
| generated_at | string | ISO timestamp | When this story was generated |

### capital_flow Object
```json
{
  "direction": "inflow",
  "amount_b": 5.0,
  "asset_class": "currencies",
  "projected": "The UUP rose 0.43%..."
}
```

---

## flows.json

Deployed to: `gs://www.lagazzettadikyiv.com/data/flows.json`
Produced by: `flow_generator.py v1.0`
Refreshes: every 10 min via governor systemd timer

### Top-level structure
```json
{
  "generated_at": "2026-06-20T15:00:38.592376+00:00",
  "generated_by": "flow_generator.py v1.0",
  "regime": "risk-on momentum with thin liquidity",
  "regime_drivers": [ ... ],
  "cross_asset": { ... },
  "narrative_flows": {
    "<narrative_key>": {
      "title": "Narrative Title",
      "ticker": "TICKER",
      "total_capital_b": 258.9,
      "dominant_direction": "inflow",
      "direction_split": {
        "inflow": 57,
        "outflow": 17,
        "neutral": 34
      },
      "avg_contradiction_gap": 31.1,
      "story_count": 108
    }
  },
  "top_signals": [ ... ]
}
```

### narrative_flows Fields (per narrative)
| Field | Type | Description |
|-------|------|-------------|
| title | string | Display name |
| ticker | string | Primary ticker for this narrative (e.g., "DXY", "FXI", "QQQ") |
| total_capital_b | float | Aggregate capital volume in billions USD |
| dominant_direction | string | "inflow" / "outflow" / "neutral" |
| direction_split | object | Count of stories per direction |
| avg_contradiction_gap | float | 0-100, average gap across all stories |
| story_count | int | Number of stories in this narrative |

### Current Ticker Mapping (8 narratives)
| Narrative | Ticker |
|-----------|--------|
| Dollar Decline | DXY |
| Energy Sovereignty | Brent |
| Deglobalization | XLI |
| China's Ascent | FXI |
| Space Economy | ROKT |
| Gene Editing | ARKG |
| Tech Convergence | QQQ |
| Wealthy Sports | BATRK |
