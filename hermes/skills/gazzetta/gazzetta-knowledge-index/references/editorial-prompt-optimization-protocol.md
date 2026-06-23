# Editorial Prompt Optimization Protocol (June 2026)

## When to use
When DeepSeek-powered editorial content shows template repetition, straw-man constructions, flat scoring, or boilerplate text. This protocol covers prompt-level fixes — NOT code-level assembly fixes (those are in `p0-data-engine-fix-protocol.md`).

## The Four-Axis Editorial Prompt Architecture

### Axis 1: Quote Anchoring (anti-straw-man)
**Problem:** LLM paraphrases generic media consensus instead of citing specific claims. Creates straw-man "They Say" that no journalist would recognize.

**Fix:** Three-part enforcement in SYSTEM_PROMPT:
```
QUOTE ANCHOR (they_say):
- MUST begin with the EXACT source name from SOURCE field
- After source prefix, cite a SPECIFIC verifiable claim from the article
- A journalist reading your they_say must recognize their own reporting
- Never begin with vague generalities like "The media reports..."
```

**Code support:** Pass source domain explicitly in user prompt via `source_domain` parameter to `build_user_prompt()`. Add `SOURCE: {domain}` line before article text. The LLM needs the source name in-context to cite it.

### Axis 2: Template Anti-Rot (anti-boilerplate)
**Problem:** LLM defaults to repetitive syntactic patterns. "fails to move markets" appears 16+ times. "market unmoved" appears 15+ times. These betray the procedural nature of the platform.

**Fix:** Explicit banned-phrase list with required structural alternatives:
```
TEMPLATE ANTI-ROT (BANNED PHRASES):
- NEVER use: "fails to", "market unmoved", "markets shrug", "markets unfazed",
  "no market impact", "fails to ignite/dent/boost/lift"
- "Fails to" banned in ANY context — all variants of "fails to [verb]"
- "Unmoved" banned in ANY context
- Instead use: "Market pricing fully absorbed...", "Capital flows unchanged despite...",
  "Price action shows no reaction to...", "Asset prices held steady through..."
```

**HARD FALLBACK (critical):** Prompt bans alone are insufficient — the LLM at temperature 0.3 will occasionally bypass them. Add a Python-level regex filter in `assemble_story()` as a hard guard:
```python
# Post-process headline to strip banned patterns
BANNED_STEMS = ['fails to', 'market unmoved', 'markets shrug', 'markets unfazed', 'no market impact']
ALT_MAP = {
    'fails to': 'shows no',
    'market unmoved': 'price action unchanged',
    'markets shrug': 'markets absorb',
    'markets unfazed': 'markets steady despite',
    'no market impact': 'zero capital signal',
}
headline = story.get('headline', '')
for stem, alt in ALT_MAP.items():
    if stem in headline.lower():
        headline = headline.lower().replace(stem, alt)
        story['headline'] = headline[0].upper() + headline[1:]
```

### Axis 3: Numeric Anchoring (anti-flat-scores)
**Problem:** LLM defaults to GAP=15 for 98.9% of stories because scoring guide uses qualitative descriptors ("Minor tension", "Moderate contradiction").

**Fix:** Replace qualitative with quantitative formula:
```
GAP = floor(10 × sum of absolute percentage moves of all contradictory tickers)

NUMERIC ANCHORING TABLE:
- 0-15: No tracked ticker moved >0.5% OR no material connection
- 16-30: Ticker(s) moved 0.5-1.5% against narrative
- 31-50: Ticker(s) moved 1.5-3% against narrative
- 51-75: Ticker(s) moved 3-5% or 2+ tickers moved 2%+
- 76-100: Broad index moved 2%+ or sector ETF moved 5%+

CRITICAL: Before scoring, identify WHICH specific ticker(s) moved and by what MAGNITUDE.
If no tracked ticker shows meaningful movement (<0.5%), GAP MUST be 0-15.
```

### Axis 4: GAP-5 Framing Rotation (anti-boilerplate for low-signal stories)
**Problem:** Low-GAP stories get identical "No tracked ticker moved more than 0.5%" reality text.

**Fix:** 5-frame rotation that the LLM must cycle through:
```
(a) "Market indifference confirms this news was already priced in."
(b) "Low gap signals market efficiency — fully reflected in current prices."
(c) "Price action fully aligned with the narrative — no divergence detected."
(d) "No material connection between this event and the tracked assets."
(e) "[Ticker] moved only [X]% — well within normal noise."
```

## Verification after prompt change

1. Deploy and wait for next governor cycle (10 min)
2. Check 3 newest stories for quote format: `grep -A1 "they_say"` should show specific source + claim
3. Check headline variety: scan 20 most recent headlines for banned stems (`grep -ci 'fails to\|unmoved\|shrugs'`)
4. Check GAP distribution: should show natural variance, not >50% at single value
5. If banned patterns still appear, add hard regex fallback — prompt tuning alone won't reach 100% compliance
