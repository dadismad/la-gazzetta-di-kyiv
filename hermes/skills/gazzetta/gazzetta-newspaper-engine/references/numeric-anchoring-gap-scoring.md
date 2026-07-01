# Numeric Anchoring — GAP Scoring Fix (June 2026)

## Problem
The Sovereign Auditor DeepSeek prompt produced flat GAP=15 for 189/191 stories (98.9%). The LLM defaulted to a baseline score because it lacked hard quantitative anchors to calculate against.

## Root Cause
The old scoring guide used vague qualitative bands ("narrative under real pressure", "mixed signals") without requiring the LLM to tie scores to specific market data points.

## Fix: Numeric Anchoring Prompt

Replace qualitative scoring with quantitative anchoring:

```text
SCORING GUIDE — Use the ENTIRE 0-100 range with NUMERIC ANCHORING:

CRITICAL: Before scoring, you MUST identify which SPECIFIC ticker(s) moved and by what MAGNITUDE.
If no tracked ticker shows meaningful movement (<0.5%), the contradiction_gap MUST be 0-15.

NUMERIC ANCHORING TABLE:
- 0-15: No tracked ticker moved >0.5%, OR no material connection. Reality must state why.
- 16-30: Minor tension — ticker(s) moved 0.5-1.5% against narrative. Name the ticker.
- 31-50: Moderate contradiction — ticker(s) moved 1.5-3%. Cite specific change_pct.
- 51-75: Significant — ticker(s) moved 3-5% or 2+ tickers 2%+. Cite ALL.
- 76-100: Extreme — broad index 2%+ or sector ETF 5%+ directly opposing narrative.

GAP = floor(10 × sum of absolute percentage moves of contradictory tickers).
Example: URA +2.31% and NLR +2.44% contradict → GAP = floor(10 × (2.31+2.44)) = 47.
```

## Result
Before: 189 flat GAP=15, 2 stories at GAP=65/70. Zero differentiation.
After: Natural distribution from GAP=5 (no connection) to GAP=85 (extreme contradiction). 78 stories at GAP=5 (correctly filtered), 70 at GAP=65, 44 at GAP=75, 21 at GAP=85.

## Code Location
`scripts/contradiction_synthesizer.py` — SYSTEM_PROMPT variable, lines ~234-285.
