# Content Strategy & Editorial Direction (June 2026)

## Core Principle

**This is a bet-driven intelligence product, not an academic research journal.** Every piece of content must answer: "What's the trade?" If it can't, don't publish it.

## What's Broken in Current Output

### Telegram Messages
- Fixed 6-block template (GAP → HEADLINE → CAPITAL FLOW → CONTRADICTION → TWO VIEWS → THE BET) — every message is structurally identical, zero surprise
- Academic "bull case / bear case" framing — fence-sitting, not committing to a trade direction
- Broad ETF tickers (DXY, QQQ, XLI, FXI, ROKT, ARKG, TLT, DBC) — these are indices and sector ETFs, not tradeable bets
- Headlines are RSS verbatim — no editorial rewrite, no hook
- Conviction is always MODERATE or SPECULATIVE — never HIGH, never urgent
- `N/A — data pending` appears when flows.json is empty — amateur presentation
- `TWO VIEWS` is template-generated boilerplate, not editor-written analysis

### Website Ticker Exposure
- Sidebar navigation renders ETF tickers with N/A values (DX=F, QQQ, XLI, ROKT)
- Story cards peg `data-ticker` to narrative default ETF, not the specific trade instrument
- GAP Leaderboard shows broad ETFs, not individual names
- Every element screams "sector ETF exposure" — nothing says "here's your bet"

## Target Content Standards

### Telegram: Hook-First, Bet-Driven

**Format should adapt to content, not the other way around.** Variable structure:
- Hook-first opening (not GAP score header)
- Single trade direction — pick LONG or SHORT, commit
- Specific entry/stop/target with real prices (never "current levels")
- R-multiple calculation (risk-reward)
- Urgency window in hours, not days
- Contrarian angle when GAP > 60

**Example target format:**
```
🔥 EVERYONE'S WRONG ABOUT ENERGY

The media's running "Iran peace deal" headlines while 
$47M in institutional flow just exited XOM in 72 hours.

The contradiction: Sanctions relief narrative vs. real 
money exiting the sector. GAP: 85/100.

THE PLAY: SHORT XOM
Entry: $114.30 | Stop: $118.00 | Target: $106.00
Risk: 1R for 2.5R | Window: 7-10 days

Why this matters: If the peace narrative was real, energy 
majors wouldn't be seeing this velocity of outflows.

#GAP_ALERT #ENERGY
```

### Ticker Resolution Priority
1. `trade_thesis.primary_ticker` — DeepSeek-generated specific instrument
2. `affected_tickers[0]` from story — most relevant single name
3. Narrative default ticker — LAST RESORT, never the primary display

### Writing Style Rules

**Hooks to deploy (pick one per message):**
- **Curiosity Gap** — Don't give the answer in the headline. Create tension.
- **Urgency Anchoring** — "This setup expires in 48 hours" not "14 day horizon"
- **Contrarian Framing** — Position against consensus: "While CNBC talks tech rally, $214M just exited semiconductors"
- **Specificity** — Always exact numbers. "$147.30" not "current levels." Specific numbers create authority.
- **Social Proof** — "Institutional flow data shows..." beats "Our analysis suggests..."
- **Risk-Reward Language** — "2.5R setup" not "moderate conviction." Traders think in R-multiples.

**Vocabulary: USE these words:**
- `positioning` not `allocation`
- `flow` not `capital movement`
- `exiting` / `rotating into` not `outflow / inflow`
- `setup` not `opportunity`
- `R-multiple` not `return potential`
- `stop` not `invalidation level`

**Vocabulary: KILL these words/phrases:**
- `bull case / bear case` — pick a side or don't publish
- `MODERATE conviction` — commit or spike the story
- `data pending` — never ship unfinished content
- `N/A` anywhere in the UI
- `TWO VIEWS` section entirely — this is fence-sitting

### Editorial Triggers

Apply these framing hooks based on story properties:
- GAP > 70 + capital > $100M → "EVERYONE'S WRONG ABOUT X" (contrarian framing)
- Capital flow > $100M direction change → "INSTITUTIONAL ROTATION DETECTED"
- Story generated < 4h ago → "FRESH SIGNAL — window is open"
- Multiple stories same narrative same direction → "CONVICTION BUILDING"

### Website Ticker Changes

- Sidebar: Replace narrative default ETF with primary tradeable instrument
  - DX=F → EUR/USD or specific FX pair
  - QQQ → NVDA or specific semi name
  - XLI → CAT or specific industrial
  - ROKT → RKLB or specific space stock
  - FXI → BABA or specific China ADR
- Story cards: `data-ticker` = `trade_thesis.primary_ticker` if available, else `affected_tickers[0]`
- GAP Leaderboard: Show narrative + primary instrument, not ETF
- Card rendering: When `affected_tickers` has individual names, show those — never collapse to narrative ETF

### Synthesis Prompt Changes (contradiction_synthesizer.py)

The DeepSeek persona needs to shift from "Sovereign Auditor" (clinical, detached) to "Tactical Editor" (committed, bet-focused). Required additions:
- Generate `trade_thesis` for every story with GAP > 40
- `primary_ticker` must be a single-name instrument when possible (not an ETF)
- Include specific entry price, stop, target in the trade_thesis
- Headlines must be rewritten with hooks, not RSS verbatim
- Calculate R-multiple where price data exists
- Pick a direction — if the data doesn't support LONG or SHORT, the story isn't ready
