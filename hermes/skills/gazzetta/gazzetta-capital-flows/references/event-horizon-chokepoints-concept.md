# Event Horizon — Chokepoints, Situation Rooms & Markets Rooms

## Concept Origin

User read **"Chokepoints"** — a book about White House strategies using sophisticated cross-border economic pressure points (sanctions, export controls, financial infrastructure as weaponry) curated within situation rooms and markets rooms.

The insight: these pressure points create predictable capital flow reactions. If you can monitor the "rooms" — the places where geopolitical decisions meet market reactions — you can impose conviction on retail traders who lack this vantage point.

## Event Horizon Definition

The "event horizon" is the collision plane where:
- **Situation Room** (geopolitical events — sanctions, export controls, military movements, central bank interventions)
- **Markets Room** (capital flow reactions — FX, CDS, energy futures, sovereign bonds, equity rotations)

cross each other. This is the point of maximum information asymmetry — the pros monitor it, retail can't see it. Gazzetta's value proposition is making this visible.

## Page Architecture (6 Sections)

### 1. Chokepoint Barometer
SVG/CSS gauge needle on green→crisis gradient. Monitors 5 component indicators:
- Sanctions intensity (OFAC/BIS new designations, entities added)
- Export control escalations (technology bans, entity list additions)
- Financial infrastructure pressure (SWIFT access, correspondent banking)
- Military posture shifts (troop movements, exercises, alert levels)
- Energy corridor disruptions (pipeline attacks, shipping lane closures)

### 2. Active Chokepoints Grid
Responsive card grid, color-coded by alert level:
- 🔴 CRITICAL: Immediate capital flow impact (e.g., Taiwan Strait closure)
- 🟠 ELEVATED: Building pressure, 24-72h window
- 🟡 WATCH: Monitoring, low probability but high impact
- 🟢 DORMANT: Normalized, no current pressure

Each card: category badge, source countries, affected assets, price impact %, last event timestamp.

### 3. Transmission Matrix
Events × Assets heatmap: rows = chokepoint events, columns = affected asset classes (FX pairs, sovereign CDS, energy futures, defense stocks, crypto stablecoins). Cell intensity = directional impact strength (↑↓ with magnitude).

### 4. Event Timeline (The Waterfall)
Reverse-chronological feed: flag emoji + event description + impact tag + affected instruments + source link. Filterable by chokepoint category.

### 5. The Pros' Monitor
4-panel layout mimicking professional trading desk screens:
- **Alert Feed**: Real-time chokepoint event alerts (simulated)
- **Price Impact**: Live prices (via Yahoo Finance/CoinGecko APIs) for affected instruments
- **Scenario Runbook**: Pre-written "if this, then that" for each chokepoint escalation level
- **Risk Barometer**: Composite risk score from all 5 chokepoint indicators

### 6. Conviction Imposer
"The Signal" synthesis: what the chokepoints are saying → what smart money is doing → what you should trade. Telegram CTA.

## Data Architecture

`data/event_horizon.json` — updated via agent workflow (not static):
```json
{
  "generated_at": "ISO8601",
  "chokepoint_barometer": { "score": 0-100, "components": [...] },
  "active_chokepoints": [...],
  "events": [...],
  "scenarios": [...],
  "alerts": [...]
}
```

## Integration

- Page: `/event-horizon.html` on lagazzettadikyiv.com
- Nav: "Horizon" link in product nav (all 5 product pages + index masthead)
- Pipeline: Agent-generated event_horizon.json every 60m (or on significant chokepoint event)
- Focus group: Use Macro Analyst + Capital Flow Analyst personas when reviewing this page
