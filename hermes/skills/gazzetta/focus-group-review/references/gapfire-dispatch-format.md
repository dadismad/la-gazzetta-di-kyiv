# GapFire Dispatch — Telegram Broadcast Format

Prescribed by the Chief Editor persona (FT/Economist, 25yr) during the June 22, 2026 Institutional Betting Readiness Audit of La Gazzetta di Kyiv.

## Problem

The Telegram channel posts headlines only. This forces the user to: open link → wait for load → read dispatch → synthesize GAP → recall portfolio context → attempt to construct thesis. Each friction point loses 40-50% of users. The user receives *information*, not *intelligence*.

## Solution: The 6-Block Format

```
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
GAP 85 | TECH CONVERGENCE
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

Ukraine war escalates but markets pour $28.8B into QQQ — 
tech rally accelerates as media screams risk-off. 
This is capital betting the war ends faster than consensus expects.

💰 CAPITAL FLOW: $28.8B net into Tech Convergence (QQQ)
   Inflows: $28.8B | Pace: 2.1x normal | Flow conviction: HIGH

⚡ CONTRADICTION: Media consensus = "geopolitical fear dominates." 
   Capital reality = "buy tech, short volatility, ignore headlines."

📊 TWO VIEWS:
   Bull case (capital side): QQQ to $520 — markets pricing early 
     ceasefire, Lagarde dovish pivot, semis supercycle (SMH +5.3%)
   Bear case (narrative side): QQQ back to $470 — escalation widens, 
     energy shock hits, duration trade unwinds

🎯 THE BET:
   LONG QQQ calls Jul expiry / SHORT VIX futures
   Conviction: HIGH | Horizon: 14 days | Max risk: 3% of portfolio

#GAP85 #TechConvergence #UkraineMarkets
```

## Block Breakdown

| Block | Purpose | Must Include |
|-------|---------|-------------|
| **HEADER** | Instant framing | GAP score + narrative name, bold separator |
| **HEADLINE** | The contradiction in 3 lines max | Specific actors, specific numbers, specific direction |
| **CAPITAL FLOW** | Raw numbers for quant brain | Dollar amount, direction, pace multiplier, flow conviction |
| **CONTRADICTION** | Two-sentence thesis | "Media says X. Capital does Y." format |
| **TWO VIEWS** | Multi-perspective with prices | Bull case WITH price target, Bear case WITH price target, specific tickers |
| **THE BET** | Specific trade recommendation | Ticker, direction, instrument type, conviction, horizon, max risk |
| **TAGS** | Searchable/filterable | #GAP score, #narrative, #geography |

## Rules

- Total length: 280-320 words (Telegram readability sweet spot)
- Every number must have a unit ($B, %, x)
- Every trade must have: ticker + direction + horizon + max risk
- No "may," "could," "might" — use "markets are pricing," "capital is flowing"
- Tags use PascalCase for narratives, CamelCase for geographies
- The contradiction block is the "speed reader" test — if someone reads only those 2 lines, they should understand the thesis

## Implementation

This format should be the output of `telegram_broadcast.py`. Replace headline-only posts with GapFire Dispatch generation. The data for each block already exists in the pipeline:

- **HEADER**: `story.contradiction_score` + `story.narrative_id`
- **HEADLINE**: `story.headline` (or synthesize from they_say + reality)
- **CAPITAL FLOW**: `story.capital_at_stake_usd` + flows.json pace data
- **CONTRADICTION**: `story.they_say` + `story.reality` (compressed)
- **TWO VIEWS**: Synthesized from `story.reality` + narrative context (LLM generation)
- **THE BET**: New field — add to contradiction_synthesizer.py DeepSeek prompt
- **TAGS**: Derived from narrative_id + geography extraction

The DeepSeek synthesis step can generate the full GapFire Dispatch as a single LLM call, or individual blocks can be assembled from existing JSON fields with minimal LLM stitching for the TWO VIEWS and THE BET sections.
