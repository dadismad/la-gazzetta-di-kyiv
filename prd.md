# Gazzetta di Kyiv — Product Requirements Document

> Version: 1.0 · Updated: 2026-06-09
> Target: lagazzettadikyiv.com

## Target Personas

### 1. The Quant (Professional Investor)
- **Needs:** Data-driven signals, statistical edge, verifiable track record, API access
- **Features:** Flow Nodes (capital decomposition), Signal triangulation, Trade ideas with entry/stop/target, Track record with realized P&L
- **UX:** High information density, numbers-first, dark theme for extended screen time
- **Pain point:** Free data sources feel unserious — needs provenance badges

### 2. The C-Suite / Macro Strategist
- **Needs:** Narrative intelligence, geopolitical context, capital flow direction, trend identification
- **Features:** Stories (who benefits, who loses), Event Horizon (chokepoint intel), Capital Flows dashboard, Living Stories (evolving narratives)
- **UX:** Scannable headlines, clear directional conviction, time-value indicators
- **Pain point:** Can't tell if data is current — needs freshness timestamps on every component

### 3. The Degen / Retail Trader
- **Needs:** Actionable trade ideas, simple directional signals, "what do I do with this?"
- **Features:** Trade ideas with BUY/SELL badges, BULLISH/BEARISH regime indicators, Flow heat scores, Contradiction signals
- **UX:** Emoji-rich signals, color-coded direction (green/red), plain-language explanations, onboarding overlay
- **Pain point:** Jargon is impenetrable — every term needs a plain-language equivalent

## Feature Map (Persona × Feature)

| Feature | Quant | C-Suite | Degen |
|---|---|---|---|
| Capital Flow Nodes | ✓✓✓ | ✓✓ | ✓ |
| Flow Dashboard | ✓✓ | ✓✓✓ | ✓✓ |
| Stories / Narratives | ✓ | ✓✓✓ | ✓✓ |
| Signal Triangulation | ✓✓✓ | ✓✓ | ✓✓ |
| Trade Ideas | ✓✓✓ | ✓ | ✓✓✓ |
| Track Record | ✓✓✓ | ✓ | ✓✓ |
| Event Horizon | ✓ | ✓✓✓ | ✓ |
| Living Stories | ✓ | ✓✓✓ | ✓ |
| Onboarding Overlay | — | — | ✓✓✓ |
| Timestamp Freshness | ✓✓✓ | ✓✓✓ | ✓✓ |

## Data Pipeline Architecture

```
Telegram Monitor (30m) → intel_to_stories.py → stories.json
                                                    ↓
                                           generate_flows.py → flows.json
                                                    ↓
Source Monitor (60m) → editorial writer → stories_in_play.json
                                                    ↓
                                           build_site.py → site/data/ + API
                                                    ↓
Market Data Fetch (4h) → fetch_cot.py, fetch_ici.py, fetch_fred.py → market_data/
                                                    ↓
                                           shipit.sh → GCS deploy
```

## Design Contract

| Rule | Value |
|---|---|
| Border radius | 0 everywhere (frameless) |
| Box shadow | none |
| Dividers | 1px, var(--divider) |
| Font families | Playfair Display (serif), Inter (sans), Source Serif 4 (body) |
| Green (buy/inflow) | #047857 (WCAG AA) |
| Red (sell/outflow) | #DC2626 |
| Gold (accent) | #B8860B (WCAG AA) |
| Mobile-first | min tap target 44px, no min-width below 390px |
| Cache policy | Hashed assets: immutable 1y · HTML: must-revalidate · JSON: no-store |

## Quality Gates (Pre-Deploy)

- [ ] refresh_context.py §4.5 passes — all critical HTML elements present
- [ ] No uncommitted files (or backed up via safe_git.py)
- [ ] Live site returns HTTP 200 on all product pages
- [ ] Signal/Track/Flows/Stories teasers contain non-empty content
- [ ] Timestamps present on all data components
- [ ] WCAG AA contrast verified (#047857 green, #B8860B gold)

## Current Gaps (from Persona Lens)

| Gap | Persona | Severity |
|---|---|---|
| No API for programmatic access | Quant | High |
| Trade ideas are hardcoded (ANCHOR_ASSETS) | Quant, Degen | High |
| Track record empty for new users | Degen | Medium |
| Event Horizon page not integrated with flows | C-Suite | Medium |
| No Russian translation for flow-nodes | C-Suite, Degen | Low |
| Mobile masthead overflows on 390px | All | Medium |
