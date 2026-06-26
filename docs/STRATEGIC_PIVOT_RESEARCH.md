# Strategic Pivot: Retail/Degen Evolution — Research Brief
# June 26, 2026

---

## 1. GAP Terminology Deprecation — Retail Alternatives

**Problem**: "GAP Score" is academic and abstract. It provides zero dopamine hit or intuitive understanding to a retail trader, crypto degen, or Gen Z investor. The term needs to instantly communicate: *the media is lying and there's money to be made from knowing the truth.*

### Research: What Do Retail Traders Respond To?

Analysis of terminology used on Robinhood, Binance, WallStreetBets, Discord trading servers, and crypto Twitter reveals a clear pattern:

| Term | Platform | Why It Works |
|------|----------|--------------|
| "Edge" | Universal trading | The holy grail. Everyone wants an edge. Implies information asymmetry. |
| "Squeeze" | WSB, crypto | Iconic post-GME. Compressed tension about to release violently. |
| "Alpha" | CT, fin-twitter | Excess returns. What everyone is chasing. Already used in our trade_thesis. |
| "Signal" | Trading desks | Clean, professional. "Signal vs Noise" is universally understood. |
| "Conviction" | Institutional | Already in our taxonomy. Familiar to the target demo. |
| "Divergence" | Technical analysis | RSI divergence, MACD divergence — traders already scan for it. |
| "Delta" | Options traders | Greeks are second nature to the target audience. |

### Proposed Replacements (3 Options)

**Option A: CONTRARIAN EDGE (recommended)**
- **Display**: "EDGE 94" instead of "GAP 94"
- **Phase labels**: "CRITICAL EDGE" / "ACTIVE EDGE" / "BUILDING EDGE"
- **Leaderboard**: "CONTRARIAN EDGE LEADERBOARD"
- **Why**: "Edge" is the single most powerful word in trading. Having a 94% edge means you're 94% more informed than consensus. Immediately communicates WHY someone should read this.
- **Risk**: Requires explaining what the number means (0-100 scale). Already solved by the tooltip.

**Option B: SIGNAL STRENGTH**
- **Display**: "SIGNAL 94" instead of "GAP 94"
- **Phase labels**: "MAX SIGNAL" / "STRONG SIGNAL" / "BUILDING SIGNAL"
- **Leaderboard**: "SIGNAL STRENGTH LEADERBOARD"
- **Why**: "Signal" implies actionable intelligence. Traders understand signal-to-noise ratio intuitively. Sounds like a trading desk, not an academic paper.
- **Risk**: Less dopamine than "Edge." More institutional.

**Option C: REALITY DELTA**
- **Display**: "Δ 94" or "R-DELTA 94"
- **Phase labels**: "EXTREME Δ" / "HIGH Δ" / "BUILDING Δ"
- **Leaderboard**: "REALITY DIVERGENCE"
- **Why**: "Delta" (Δ) is iconic in trading — options Greeks, price deltas. The symbol itself is visually distinctive and implies quantitative rigor. "Reality Delta" connects to our core thesis (media vs reality).
- **Risk**: May confuse non-options traders. Less intuitive than "Edge."

### Recommendation: Hybrid — "EDGE" as primary term, Δ symbol as visual accent

```
GAP 94 CRITICAL SHIFT  →  EDGE 94 ⚡ CRITICAL
GAP Leaderboard        →  CONTRARIAN EDGE
GAP Score (0-100)      →  EDGE Score (0-100): Media/Capital divergence
Phase: BUILDING TENSION →  Phase: BUILDING
Phase: ACTIVE DIVERGENCE →  Phase: HEATING UP
Phase: CRITICAL SHIFT   →  Phase: MAX EDGE ⚡
```

**Implementation scope**: ~30 search-replace operations in `build_frontend.py` (JS strings + Python template strings). No data model changes — the field name `contradiction_gap` stays in JSON. Frontend-only semantic shift.

---

## 2. Telegram 2.0 — From AI Summary to Trading Desk Signal

### Current State Analysis

Current `telegram_broadcast.py` produces 6 dispatch formats:
- THE PLAY, STRUCTURAL SHIFT, CONTRADICTION HOOK, CAPITAL VS MEDIA, MACRO BRIEFING, SIGNAL PULSE

**Issues identified**:
1. Template openers removed (June 23 fix), but format still reads like an AI wrote it
2. Same sentence structures repeated across dispatches
3. No risk/reward framing
4. No specific entry/exit levels visible in broadcast
5. GAP score displayed but not contextualized
6. Stylistic flaws: "fails to move markets" banned phrases still occasionally slip through
7. Missing: position sizing suggestion, time horizon emphasis, urgency language

### Target Audience Psychographics

- **Primary**: Retail macro traders, self-directed, ages 22-40
- **Secondary**: Crypto natives, degens, WallStreetBets adjacent
- **Tertiary**: Family offices, sovereign individuals

**What they respond to**:
- Specificity: exact tickers, exact levels, exact direction
- Conviction: "I am betting X on Y" not "Y may possibly occur"
- Scarcity: "Edge window closing in 6 hours" not "EDGE DECAY: ~6H REMAINING"
- Social proof: "Institutional flows confirm" not "capital migration suggests"
- Urgency: Imperative mood — "Buy GLD calls" not "GLD presents a potential opportunity"

### Proposed Redesign: 3-Format System

**Format 1: THE SETUP (replaces THE PLAY / CONTRADICTION HOOK)**
```
🔴 $GLD — CONTRARIAN EDGE 94
Entry: 248.50 | Target: 262.00 | Stop: 242.00
R/R: 2.3:1 | Horizon: 24-48H

MEDIA SAYS: Bloomberg claims inflation fears are driving gold demand.
THE TAPE SAYS: Gold dropped 3% while bonds rallied 1.4%. Capital is fleeing the debasement trade, not entering it.

⚡ EDGE: The media narrative and capital flow are 94% contradictory. Someone is wrong. History says it's the media.

→ Full breakdown: lagazzettadikyiv.com
```

**Format 2: THE FLOW (replaces STRUCTURAL SHIFT / CAPITAL VS MEDIA)**
```
📊 $QQQ — INSTITUTIONAL FLOW DIVERGENCE
$6.3B net outflow this week | $11.2T narrative market cap

SMH -3.77% while Bloomberg prints "stocks climb on cooler CPI."
Chips are distributing. The tape knows. The headlines don't.

Direction: SHORT | Conviction: HIGH
Institutional OI: +2,986,992 BTC contracts | Retail: flat

→ Position details: lagazzettadikyiv.com
```

**Format 3: THE PULSE (replaces SIGNAL PULSE / MACRO BRIEFING)**
```
🌐 MACRO PULSE — 15:00 Kyiv
Regime: RISK-ON, THIN LIQUIDITY
187 discrepancies across 12 narratives

HOT: Sovereign Liquidity (EDGE 94), Decentralized Capital (EDGE 81)
COLD: Trophy Assets (EDGE 11), Industrial Reshoring (EDGE 25)

1. Gold -3%, bonds +1.4% → debasement trade unwinding
2. BTC OI at $178.5B, flat Δ → coiled, direction uncertain  
3. Biotech +7.8% on Ebola trial → rotation out of hedges into innovation

→ Live terminal: lagazzettadikyiv.com
```

### Key Design Principles

1. **Ticker-first**: Lead with WHAT to trade, not what happened
2. **Specific levels**: Entry, target, stop on every actionable signal
3. **Risk/Reward**: Quantified — traders need this
4. **Contrast structure**: "Media says X / The tape says Y" — our core IP
5. **Urgency language**: "Edge window" not "edge decay", "distributing" not "potential distribution"
6. **Call to action**: Every dispatch drives to the website
7. **Max 2 dispatches per cycle** (current behavior, keep)

### Implementation

**File**: `telegram_broadcast.py` — rewrite `format_story_for_telegram()` function (~260 lines)
**Effort**: 2-3 hours
**Risk**: Medium — the broadcast is the primary user acquisition channel. Must preserve the intent lock and throttle logic.

---

## 3. NMC Continuous Reassessment Note

The NMC engine is structurally sound after today's expansion (67 assets, $18.28T). However:

- **Weekly review cadence needed**: Asset purity weights should be reviewed against actual capital flows. If money is rotating out of an asset but it retains high purity weight, the NMC becomes misleading.
- **New narratives may emerge**: The 12-narrative taxonomy was built for June 2026 macro conditions. AI regulation, CBDC rollout, or a new commodity super-cycle could require new narratives.
- **Flag mechanism**: The proposal document's "flag" field (e.g., "very small fund assets", "low liquidity small-cap") should trigger periodic review of whether those assets still belong.
- **Recommendation**: Add a `last_reviewed` timestamp to `narrative_graph.json`. Flag assets with >30 day review gap in a maintenance cron job.

---

*Research brief compiled June 26, 2026 — awaiting Alex approval before implementation.*
