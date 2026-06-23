# Content Strategy v3.0 — Tactical Editor (June 23, 2026)

## Persona Shift: Sovereign Auditor → Tactical Editor

The `contradiction_synthesizer.py` system prompt was rewritten from an academic "financial contradiction analyst" to:

> "You are the Tactical Editor for La Gazzetta di Kyiv, an alpha-generation terminal that converts narrative-capital contradictions into executable trade setups. You do not write journalism. You write trade calls. Your reader is a professional trader who needs a specific asset, a specific direction, specific price levels, and a structural edge — not a balanced analysis."

## Prompt Engineering Rules Injected

### A. Curiosity Gap & Information Asymmetry
- Never write descriptive, literal RSS-style headlines
- Create tension by anchoring on the contradiction
- Do NOT reveal the full trade thesis in the headline
- When GAP > 60, frame media as "official story" and capital flow as "real story"
- Example: "While retail digests the headline, a $47M structural exit just triggered in NVDA."

### B. Structural Conviction Grading (Data-Tied)
```
HIGH:      GAP >= 75 AND directional capital flow AND ticker moved >3%
ELEVATED:  GAP 60-74 with directional capital flow
SPECULATIVE: GAP 50-65 but flows flat/mixed
HOLD:      Contradictory data or no tracked ticker movement → skip broadcast
```
Schema updated: conviction enum = "HIGH or ELEVATED or SPECULATIVE or HOLD"

### C. NER Constraint (Subject-Action-Object)
- Isolate prime moving entity from news text
- `primary_ticker` MUST match specific corporate victim/beneficiary, not sector ETF
- "White House restricts lithography exports" → ASML/AMAT/LRCX, not SMH
- "OPEC extends production cuts" → XOM/CVX/OXY, not CL=F

## Single-Name Ticker Strategy

All ticker maps replaced with liquid single-name equities (verified against yfinance):

| Narrative | Old (ETF) | New (Single-Name) |
|---|---|---|
| Dollar Decline | DXY, GLD | EURUSD=X, GLD |
| Energy Sovereignty | URA, NLR, CL=F | XOM, CVX, CCJ |
| Deglobalization | XLI, ITA | CAT, GE |
| China Ascent | FXI, KWEB | BABA, PDD |
| Space Economy | ROKT, UFO | RKLB |
| Gene Editing | ARKG, XBI | CRSP, ARKG |
| Tech Convergence | QQQ, SMH | AAPL, MSFT |
| AI Chips | SMH | NVDA, AMD |
| Crypto Reserve | BTC-USD | BTC-USD, MSTR, COIN |
| Rate Cycle | TLT | TLT, IEF |
| Commodity Supercycle | DBC | XOM, CAT |
| Wealthy Sports | BATRK | BATRK, MSGS |

Files changed:
- `market_reality.py` — NARRATIVE_TICKERS dict (12 narratives, single-name first)
- `data/narratives.json` — tickers field (sidebar display)
- `contradiction_synthesizer.py` — market_context now passes single-name tickers to LLM

## Dynamic Telegram Format

Replaced fixed 6-block GapFire Dispatch with conviction-adaptive layout:

### HIGH / ELEVATED → THE PLAY execution card
```
🔥 EVERYONE'S WRONG ABOUT ENERGY SOVEREIGNTY

[Curiosity gap headline]

The retail consensus is trading the narrative, but the capital
ledger shows a massive divergence. GAP: 85/100.

[Alpha trigger — one sentence on what market is pricing wrong]

🚀 THE PLAY: SHORT XOM | 2.5R
• Limit Entry: $114.30
• Stop Loss: $118.00
• Target: $106.00
• Strategy Window: 7 days | Conviction: HIGH 🔥

Why this edge exists: [alpha_trigger]
```

### SPECULATIVE → Signal format (lighter, no bull/bear cases)
```
🧪 SIGNAL: ENERGY SOVEREIGNTY | GAP 62/100

[Headline]

Media says: [they_say short]
Capital says: [reality short]

Alpha thesis: [alpha_trigger]

🎯 SHORT XOM | 1.8R | Conviction: SPECULATIVE
Entry: $114.30 | Stop: $118.00 | Target: $108.00
```

### HOLD → Empty string (skip broadcast entirely)
No weak setups pushed. The main() function skips empty returns.

## R-Multiple Auto-Calculation

Added to `telegram_broadcast.py` format function:
```python
e = float(entry_price)
s = float(stop_price)
t = float(target_price)
r = round(abs(t - e) / abs(e - s), 1)  # R-multiple
```

## Words to Use / Words to Kill

**Use:** positioning, flow, exiting, rotating into, setup, R-multiple, stop, window
**Kill:** bull case, bear case, MODERATE conviction, data pending, N/A, opportunity, return potential

## Ticker Resolution Priority

The broadcast uses this priority chain:
1. `trade_thesis.primary_ticker` (LLM-picked specific instrument)
2. `affected_tickers[0]` (from story data)
3. Narrative default (single-name, not ETF)
