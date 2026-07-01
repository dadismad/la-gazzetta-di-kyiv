# Telegram Post Format v4.0 — Sovereign Auditor 3-Block

> **⚠️ SUPERSEDED for top-2 stories per cycle (June 22, 2026):** The Chief Editor evaluation prescribed a new GapFire Dispatch format (280-320 words, 6-block, emoji palette, THE BET block) for the top 2 Telegram stories. See `references/editorial-quality-gates-v3.md` for the new format. This 3-block format (and the Rapid Intelligence Terminal 6-block from `gazzetta-paradigm-and-strategy`) may still serve lower-priority stories.

Supersedes v3.0 HOOK/STORY/LINK (HTML) and earlier 3-line psychological hook engine (HTML).

## Format

Three blocks, clean Markdown (no HTML tags). ~90 words. No emojis.

```
**RISK REGIME:** [1-line macro assessment with ticker anchoring and driving factor]

**ASSET REPRICING MAP:**
- [TICKER]: [Direction] at [amount] — [momentum/mean-reversion cue]
- Consensus: [short they_say excerpt]
- [Volume/velocity anomaly signal]

**MOST PROBABLE 24-72H PATH:**
- [TICKER] [bias] bias continues ([confidence]%): [rationale]
- Flip trigger: [price level or condition]. [Invalidation criteria]

Full data: https://www.lagazzettadikyiv.com/stories.html#story-[id]
```

## Constraints

- ~90 words, max 110
- One explicit probability % (confidence or contradiction score)
- One explicit invalidation/flip trigger with price level or concrete condition
- Parse mode: Markdown (NOT HTML)
- No emojis, unicode icons, or decorative formatting
- Ticker anchoring via TICKER_MAP (dollar_decline→DXY, energy_sovereignty→Brent, china_ascent→FXI, etc.)

## TICKER_MAP

```python
TICKER_MAP = {
    "dollar_decline": "DXY",
    "energy_sovereignty": "Brent",
    "deglobalization": "XLI",
    "china_ascent": "FXI",
    "space_economy": "ROKT",
    "gene_editing": "ARKG",
    "tech_convergence": "QQQ",
    "wealthy_sports": "BATRK",
}
```

## Hook/Story/Link (v3.0 — DEPRECATED)

The old v3.0 format used HTML tags:

```
<b>HOOK</b> (50-80 chars, notification-optimized)
<b>Consensus:</b> [they_say]
<b>Reality:</b> [reality]
<b>Capital flow impact:</b> [direction]: $XB in [asset]
<a href="...">Read the full report</a>
```

This is superseded. The Markdown blocks render cleaner in Telegram notifications and convey institutional weight without HTML formatting artifacts.

## Implementation

Script: `scripts/cco_telegram.py` (deployed to VM at `/opt/gazzetta-di-kyiv/scripts/cco_telegram.py`)

Key functions:
- `format_story(story: dict) -> str` — main formatter
- `_build_regime(headline, contradiction, direction, amount_b, ticker) -> str` — block 1
- `_build_repricing(ticker, direction, amount_b, pace, asset, contradiction, they_say, reality) -> str` — block 2 (max 3 bullets)
- `_build_path(direction, amount_b, ticker, contradiction, confidence) -> str` — block 3 (2 bullets)

Freshness filter: blocks posts older than 12h (exit code 2).
Idempotency: checked via `posted_stories.jsonl`.

## Example Output

```
**RISK REGIME:** Sharp FXI divergence from consensus narrative. $2.2T outflows accelerating.

**ASSET REPRICING MAP:**
- FXI: Outflows from FXI at $2.2T — momentum extending
- Consensus: Beijing plans routine maritime surveys east of Taiwan to assert sovereignty...
- Volume anomaly: 75% divergence between media framing and capital positioning

**MOST PROBABLE 24-72H PATH:**
- FXI depreciation bias continues (75%): capital outflows suggest positioning for further downside
- Flip trigger: FXI reversal on consensus realignment. Gap closing below 45 invalidates divergence thesis

Full data: https://www.lagazzettadikyiv.com/stories.html#story-10042
```
