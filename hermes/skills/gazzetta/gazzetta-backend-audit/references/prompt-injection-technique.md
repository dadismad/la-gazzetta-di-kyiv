# Surgical Prompt Injection Pattern

## Problem

When modifying an LLM prompt that feeds into a downstream JSON parser (e.g., `json.loads()` on DeepSeek output), replacing the entire prompt will break the pipeline because the LLM stops producing the expected JSON schema.

## Pattern

**Replace ONLY the "who you are" paragraph** — the persona description. Leave the JSON schema, scoring guide, and output format instructions completely untouched.

## Example: Tier 1 (contradiction_synthesizer.py:283)

### Before (original persona paragraph)
```
You are the Tactical Editor for La Gazzetta di Kyiv, an alpha-generation terminal
that converts narrative-capital contradictions into executable trade setups. You do
not write journalism. You write trade calls. Your reader is a professional trader who
needs a specific asset, a specific direction, specific price levels, and a structural
edge — not a balanced analysis. Every output must answer one question: "Where do I
put my money RIGHT NOW and why is the consensus wrong?"
```

### After (Pal/Visser persona injected, rest preserved)
```
You are an institutional-grade macro strategist and quantitative trader. Your
structural worldview is shaped by Raoul Pal (The "Everything Code" — liquidity cycles,
fiat debasement, assets repricing against a declining denominator) and Jordi Visser
(structural asymmetry, technological disruption, demographic shifts, ignoring noise).
However, your primary edge is as a CONTRADICTION ENGINE. GUARDRAIL: Use the Pal/Visser
frameworks strictly as lenses for interpreting the data, not as predetermined conclusions.
If the capital flows contradict the Everything Code thesis, explicitly state it. The
contradiction IS the signal. You do not write journalism. You write trade calls. Your
reader is a professional trader who needs a specific asset, a specific direction,
specific price levels, and a structural edge — not a balanced analysis. Every output
must answer one question: "Where do I put my money RIGHT NOW and why is the consensus
wrong?"
```

### What was preserved (untouched)
- The full JSON schema with all keys (`direction`, `primary_ticker`, `limit_entry_price`, `stop_loss`, `take_profit`, `conviction`, `alpha_trigger`, etc.)
- The scoring guide (0-100 range with numeric anchoring)
- The output format instruction ("Respond with ONLY valid JSON. No markdown fences.")
- The narrative_scores dictionary with 12 narrative keys

## Anti-Patterns (DO NOT DO)

1. **Replacing the entire prompt with free-text output instructions** — the LLM will produce prose, not JSON, and `json.loads()` will crash.
2. **Writing a new JSON schema that differs from what the pipeline expects** — even if it's valid JSON, field name mismatches (`direction` vs `bias`, `limit_entry_price` vs `entry`) cause silent `None` returns throughout downstream code.
3. **Targeting the wrong file** — `telegram_broadcast.py` has no synthesis prompt. The synthesis prompt lives in `contradiction_synthesizer.py`.

## Verification Checklist

After any prompt change:
1. Verify the JSON schema keys match exactly what the pipeline reads (cross-reference with `gazzetta-backend-audit` story object schema)
2. Run a pipeline cycle and check the governor log for synthesis step success
3. Check that `format_story_for_telegram()` receives expected field values (not None)
4. Verify conviction routing still works (TIER 1 vs TIER 2 detection)
