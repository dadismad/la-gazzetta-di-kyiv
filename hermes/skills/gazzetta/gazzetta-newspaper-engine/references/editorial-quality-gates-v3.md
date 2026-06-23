# Editorial Quality Gates v3 — Chief Editor Evaluation Framework

Applied during the June 22, 2026 evaluation. Codifies the 4-lens editorial audit methodology and the resulting quality rules.

## The 4-Lens Audit Framework

Use this for any editorial product evaluation (not just Gazzetta):

### LENS 1 — Top-Down: Editorial Architecture for Betting Intentions
Does the architecture lead the reader toward a betting intention? Check:
- **Contradiction detection** → is there a GAP score or equivalent?
- **FORWARD DECLARATION** → between GAP and end of story, is there:
  - (a) Bias statement — "Markets have priced X. We believe they are correct/wrong because Z."
  - (b) Instrument selection — specific ticker + direction
  - (c) Conviction sizing — core/satellite/speculative + portfolio weight
- If (b) or (c) missing, score max 4/10 on this lens

### LENS 2 — Bottom-Up: Headline & Content Quality
Spot template rot. Common detection patterns:
- **LLM passive constructions**: "leaves market pricing unchanged", "as markets rally", "as [sector] surge(s)"
- **Generic contradiction framing**: "but markets diverge", "but [X] rally overshadowed"
- **GAP-5 noise**: stories where "nothing happened" are dressed as journalism
- **Run the template rot regex check**: search all headlines for the banned phrases below

### LENS 3 — Source Trust: Distribution Format
- Headline-only posts in primary channel = zero betting intention conversion
- Evaluate: does the format pre-construct the thesis or require the user to synthesize?
- Required elements: capital flow data, contradiction angle, two-view perspective, specific bet

### LENS 4 — Intellectual Intrusion
Does the content create "aha" moments? Check for:
- **Historical analogs**: past similar events and their market outcomes
- **Cross-asset correlations**: connecting price movements across unrelated instruments
- **Trajectory**: GAP widening or compressing over time
- **Implied probabilities**: what the price tells us about market-implied odds

## Quality Rules (Hard Gates)

### Rule 1: FORWARD DECLARATION — Every story MUST end with a tradeable thesis

The editorial pipeline between GAP score and story close MUST include three fields rendered as the final block of every dispatch:

```text
BIAS: [BULL/BEAR/NEUTRAL] [TICKER]
ENTRY: [$X.XX] | TARGET: [$Y.YY] | STOP: [$Z.ZZ]
CONVICTION: [HIGH/MED/LOW] | WEIGHT: [X% of portfolio] | HORIZON: [N days]
```

Implementation: the contradiction_synthesizer.py prompt must generate `actionable_trade` as a structured dict (not empty string). The frontend must render it as a distinct "THE BET" block below "Market Reality".

### Rule 2: GAP < 15 stories are NOISE — must be filtered from main Stream

Any story with `contradiction_gap < 15` MUST NOT appear in the main Stream feed. Rationale:
- GAP-5 means "headline has no measurable market impact" — this is not a contradiction, it's a non-event
- GAP-5 stories are the single biggest drag on editorial credibility
- They consume visual attention that should go to GAP 40+ stories
- Implementation: create a "NOISE MONITOR" tab for sub-15 stories if data completeness is required, but never surface in primary feed

Additionally: signal a GAP < 15 event to the LLM pipeline as feedback so similar non-events are skipped at ingestion (raise the triage threshold).

### Rule 3: Template Rot Hard Ban — Python-level regex guard, not prompt-level

The following patterns MUST be caught by a Python regex sanitizer in `assemble_story()` before story write, NOT by LLM prompt compliance:

```python
BANNED_HEADLINE_PATTERNS = [
    r'leaves? market pricing unchanged',
    r'leaves? market pricing unchanged for tracked assets?',
    r'as markets? rally',
    r'as markets? focus on',
    r'as markets? diverge',
    r'as .+ surging?',
    r'shadowed by .+ rally',
    r'overshadowed by',
    r'draws? no market reaction',
    r'markets? shrug',
    r'fails? to move markets?',
    r'pricing unchanged for',
]
```

On match, the story should be either (a) dropped or (b) flagged for editorial rewrite with a specific instruction: "Rewrite headline without passive 'leaves market pricing unchanged' construction. Use active voice. Add a number. Identify the specific actor who is wrong."

### Rule 4: THEY SAY must quote a NAMED source, not "the article reports"

A "they say" block that begins with "The article reports that..." or "Media consensus holds that..." is a straw-man. The real contradiction requires:

```text
THEY SAY (Source, HH:MM UTC): "Quoted claim" — Named Person, Title/Organization
```

Implementation: the synthesis prompt must require:
- A specific quote from the source article (not a paraphrase)
- The source domain or outlet name
- The timestamp of the claim if available
- A named individual or identifiable institutional author

### Rule 5: Historical Analog Required — every significant contradiction (GAP 65+)

The synthesis prompt for GAP 65+ stories must include a `historical_analog` section:

```text
HISTORICAL ANALOG: [Event year] [event name] → [market reaction in time window]
[1-2 sentence lesson about what happened and when it reversed]
```

Examples:
- "2015 JCPOA → Iranian equities +40% in 6 months, energy -8%"
- "2020 Soleimani → oil +4% intraday, fully reversed in 72 hours"
- "Crimea 2014 → semis sold off 6 hours, then rallied 12% in 2 weeks"

### Rule 6: Cross-Asset Synthesis — not just ticker listing

The Reality block must not just list tickers and percentages. It must connect them:

```
WRONG: "URA +2.3%, NLR +2.4%, QQQ +2.1%, SMH +5.3%"
RIGHT: "SMH +5.3% alongside URA +2.3% is the real signal. Semis and energy simultaneously rallying in a geopolitical crisis means the market has flipped to 'this is an opportunity' — a pattern seen in Crimea 2014 (6h), Soleimani 2020 (2h), Ukraine 2022 (48h)."
```

## Telegram GapFire Dispatch Format (replaces v3.0 3-block for top-2 stories)

This is the PRIMARY distribution format for Telegram. It replaces both the "Sovereign Auditor 3-Block" (90 words, no emoji) and the "Rapid Intelligence Terminal 6-block" (50-160 words) for the top-2 stories per cycle.

```text
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
🔥 GAP [SCORE] | [NARRATIVE LABEL]
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

[2-3 sentence contradiction: what media says vs what capital is pricing]
[First sentence = visual, specific claim. Second = market move. Third = the meaning.]

💰 CAPITAL FLOW: $XB moving [direction] [asset]
   ■ Inflows: $XB | Outflows: $XB
   ■ Pace: Nx normal | Flow conviction: X%

⚡ CONTRADICTION: [One-line: "Media says X — capital says Y"]

📊 TWO VIEWS:
   Bull case (capital side): [ticker + price target] — [one-sentence rationale]
   Bear case (narrative side): [ticker + price target] — [one-sentence rationale]

🎯 THE BET:
   [DIRECTION] [TICKER] [instrument/expiry if options]
   Entry: [$X] | Target: [$Y] | Stop: [$Z]
   Conviction: [HIGH/MED/LOW] | Horizon: [N days] | Max risk: [X%]

#GAP[score] #[narrative] #[ticker]
```

**Constraints:**
- 280-320 words (longer than existing formats — this is for the trading audience)
- Emojis allowed: 🔥💰⚡📊🎯 (5-emoji palette only)
- Tags (3-5) for searchability
- Must include hard numbers in every block
- THE BET block must be the FINAL substantive block (before tags)
- This is for the TOP 2 stories per cycle only (existing format can serve lower-priority stories)

## Implementation Priority

1. FORWARD DECLARATION — highest impact (fixes Lens 1 gap)
2. GAP < 15 filter — quickest fix (deletes noise, raises avg quality instantly)
3. Telegram GapFire Dispatch — highest distribution leverage
4. Template rot regex guard — prevents regression
5. THEY SAY named quoting — fixes straw-man journalism
6. Historical analogs — differentiator, hardest to implement

## Scoring Rubric (for automated evaluations)

| Lens | Max Score | Passing |
|------|-----------|---------|
| Top-Down (Betting Pipeline) | 10 | ≥6 |
| Bottom-Up (Content Quality) | 10 | ≥7 |
| Source Trust (Distribution) | 10 | ≥7 |
| Intellectual Intrusion | 10 | ≥5 |

Combined: PASS (all ≥ pass threshold), CONDITIONAL PASS (any 1 below), FAIL (2+ below).
