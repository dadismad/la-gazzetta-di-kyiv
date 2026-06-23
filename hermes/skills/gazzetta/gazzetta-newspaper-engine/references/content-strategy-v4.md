# Content Strategy v4.0 — Tactical Editor (June 23, 2026)

## Core Principles

1. **No fence-sitting.** Every trade call picks a direction. No bull/bear cases.
2. **Single-name instruments only.** ETFs are banned from primary_ticker. Fallback: narrative's whitelisted ticker.
3. **Conviction is data-driven, not LLM-assigned.** Python overrides LLM conviction grades.
4. **Headlines create tension.** 4 contrarian formulas replace descriptive summaries.
5. **Attention is scarce.** HOLD conviction stories are silently skipped from Telegram broadcast.

## Deterministic Conviction Grading

Located in `contradiction_synthesizer.py` → `assemble_story()`. Runs AFTER LLM extraction:

```python
is_directional = trade_direction in ("LONG", "SHORT")
if contradiction_gap >= 75 and is_directional:
    trade_conviction = "HIGH"
elif contradiction_gap >= 60 and is_directional:
    trade_conviction = "ELEVATED"
elif contradiction_gap >= 50 and is_directional:
    trade_conviction = "SPECULATIVE"
elif contradiction_gap >= 50 and not is_directional:
    trade_conviction = "SPECULATIVE"
else:
    trade_conviction = "HOLD"
```

**PITFALL:** The grading code must run AFTER `trade_direction` extraction but BEFORE the final story dict assembly. If placed before `trade_direction` is defined, it silently uses the wrong direction.

**PITFALL:** LLMs ignore numeric thresholds in prompts. Even explicit "HIGH only if GAP >= 75" prompts fail — the LLM treats numbers as semantic tokens, not constraints. Python override is the ONLY reliable method.

## Asset Whitelisting

Located in `assemble_story()`. Runs after trade_ticker extraction:

```python
_all_whitelisted = []
for _tlist in TICKER_WHITELIST.values():
    _all_whitelisted.extend(_tlist)
_narrative_tickers = TICKER_WHITELIST.get(narrative_tag, [])
_fallback_ticker = _narrative_tickers[0] if _narrative_tickers else "SPY"

if not trade_ticker or trade_ticker not in _all_whitelisted:
    trade_ticker = _fallback_ticker
```

**PITFALL:** TICKER_WHITELIST must be defined BEFORE the whitelist validation code. If defined after (e.g., in the AUM computation block further down), the validation silently references an undefined variable. In our case, the duplicate definition in the AUM block was harmless because Python's scoping allowed it, but the ordering was wrong — the validation ran before the definition.

**TICKER_WHITELIST (mirrors market_reality.py NARRATIVE_TICKERS):**

```python
TICKER_WHITELIST = {
    "energy_sovereignty": ["XOM", "CVX", "CCJ", "URNM"],
    "dollar_decline":     ["EURUSD=X", "GLD", "SLV"],
    "deglobalization":    ["CAT", "GE", "XLI"],
    "china_ascent":       ["BABA", "PDD", "FXI"],
    "space_economy":      ["RKLB", "ARKX"],
    "gene_editing":       ["CRSP", "ARKG", "XBI"],
    "tech_convergence":   ["AAPL", "MSFT", "QQQ"],
    "wealthy_sports":     ["BATRK", "MSGS", "MANU"],
    "ai_chips":           ["NVDA", "AMD", "SMH"],
    "crypto_reserve":     ["BTC-USD", "MSTR", "COIN"],
    "rate_cycle":         ["TLT", "IEF", "SHY"],
    "commodity_supercycle": ["XOM", "CAT", "DBC"],
}
```

This SAME map must exist in three places (keep in sync):
1. `market_reality.py` NARRATIVE_TICKERS (price fetching)
2. `contradiction_synthesizer.py` TICKER_WHITELIST (validation + AUM)
3. `data/narratives.json` tickers field (website sidebar)

**PITFALL:** Previous sessions updated market_reality.py but left a SHADOW ticker map in assemble_story() that still used old ETFs (URA, NLR, GLD, XLI, FXI, ROKT). This fed ETF tickers into the AUM computation, which fed them into the LLM's market context, which caused the LLM to generate ETF-based trade theses despite the prompt saying "use single-name instruments." The LLM can't pick what it can't see — the ticker universe in its context is all it knows.

## Contrarian Headline Friction Patterns

Injected into `contradiction_synthesizer.py` SYSTEM_PROMPT. Four mandatory patterns:

- **Pattern A:** [Unpopular Truth] + [Hidden Capital Divergence]
  - "Insiders are quietly dumping Lithium space while retail buys the Sodium hype."
- **Pattern B:** [Specific Number/Price Action] + [Narrative Contradiction]
  - "$214M exited XOM this week. The media's still running 'energy dominance' headlines."
- **Pattern C:** [Question Hook] + [The Data Answer]
  - "Why is NVDA down 3% while every analyst upgrades? The flow data knows."
- **Pattern D:** [Who's Wrong] + [Who's Right]
  - "CNBC calls it a tech rally. The capital ledger calls it a distribution event."

Every headline MUST contain EITHER a specific number, a specific ticker, OR a specific contradiction. No passive summaries. No "X meets Y" academic language.

## Telegram Broadcast — Dynamic Layout

In `telegram_broadcast.py` → `format_story_for_telegram()`. Three layout tiers:

**HIGH/ELEVATED → "THE PLAY" Execution Card:**
```
🔥 EVERYONE'S WRONG ABOUT ENERGY SOVEREIGNTY

[Curiosity gap headline]

The retail consensus is trading the narrative, but the capital 
ledger shows a massive divergence. GAP: 85/100.

[Alpha trigger — one sentence on what the market is pricing wrong]

🚀 THE PLAY: SHORT XOM | 2.5R
• Limit Entry: $138.47
• Stop Loss: $142.00
• Target: $130.00
• Strategy Window: 14 days | Conviction: HIGH 🔥

Why this edge exists: [alpha trigger repeated or expanded]

#GAP_ALERT #ENERGYSOVEREIGNTY #XOM
```

**SPECULATIVE → Signal Format (lighter, no fake bull/bear):**
```
🧪 SIGNAL: ENERGY SOVEREIGNTY | GAP 62/100

[Headline]

Media says: [they_say]
Capital says: [reality]

Alpha thesis: [alpha]

🎯 SHORT XOM | 1.8R | Conviction: SPECULATIVE
Entry: $138.47
Stop: $142.00
Target: $132.00
```

**HOLD → Skip (returns empty string).** The main() function checks and continues silently.

## Legacy Story Migration

When conviction grading rules change, existing stories retain their old (wrong) grades. Run a one-time migration:

```python
# regrade_convictions.py — updates data/stories.json + public/data/stories.json
for s in stories:
    gap = s.get("contradiction_gap", 0)
    direction = s.get("trade_thesis", {}).get("direction", "NEUTRAL")
    is_directional = direction in ("LONG", "SHORT")
    
    if gap >= 75 and is_directional:
        new_conv = "HIGH"
    elif gap >= 60 and is_directional:
        new_conv = "ELEVATED"
    elif gap >= 50 and is_directional:
        new_conv = "SPECULATIVE"
    elif gap >= 50 and not is_directional:
        new_conv = "SPECULATIVE"
    else:
        new_conv = "HOLD"
    
    if old_conv != new_conv:
        s["trade_thesis"]["conviction"] = new_conv
```

After migration: `sudo chown gazzetta:gazzetta` on BOTH copies of stories.json. The governor timer must be running (no freeze needed for read-only migration of non-pipeline-critical field).
