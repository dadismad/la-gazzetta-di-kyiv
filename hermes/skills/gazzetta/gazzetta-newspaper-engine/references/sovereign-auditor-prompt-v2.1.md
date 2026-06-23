# Sovereign Auditor Prompt Architecture v2.1
>
> June 2026 — Prompt hardening, temperature calibration, and few-shot example injection for contradiction_synthesizer.py

## v2.0 → v2.1 Delta

| Component | v2.0 | v2.1 |
|---|---|---|
| Temperature | 0.3 | **0.5** |
| Few-shot examples | None | **2 full examples** (high-gap + low-gap) |
| JSON fields | 8 | **9** (+ cross_narrative_impact) |
| JSON sanitization | Basic markdown strip | **Fallback repair pass** (trailing commas, control chars) |
| Headline enforcement | Voice constraints only | **Mandatory ban + structural mandate** |
| Cross-narrative | Not present | **cross_narrative_impact array** |

## Prompt Hardening Technique

### The Problem: Temperature-0.3 Token Loop

At temperature 0.3, DeepSeek discovered the "X fails to Y" template as the highest-probability token path that satisfied the JSON schema constraint. It produced this pattern in ~90% of headlines across hundreds of stories. Few-shot examples ALONE did not break the loop -- the model still defaulted to its familiar pattern because 600+ existing stories in the dataset validated it as precedent.

### The Fix: Negative Constraint + Positive Structural Enforcement

Three components deployed simultaneously:

**1. Mandatory Ban (what NOT to do):**
```
You are strictly FORBIDDEN from using the syntactic template 
"[Event] fails to [lift/move/affect/halt] [Asset/ETF]" or any 
direct semantic equivalents (e.g., "leaves unchanged", 
"does not impact").
```

**2. Structural Mandate (what TO do):**
```
Headlines must lead directly with the macroeconomic friction, 
capital flow anomaly, or institutional divergence -- NOT the news 
event. The pricing anomaly is the subject, not the event.
```

**3. Agent-Driven Template (example of the target):**
```
BANNED: "Hong Kong burglary arrest fails to halt FXI slide below $33.5"
REQUIRED: "Institutional FXI Liquidation Drives Capital Past $33.5 
          Support as Retail Narrative Decouples"
```

### Results

| Metric | Before | After |
|---|---|---|
| Institutional headlines | 0/5 (0%) | 3/5 (60%) |
| "fails to" pattern | 5/5 (100%) | 2/5 (40%) |
| narrative_phase = None | 3/5 | 0/5 |
| asymmetry = "None" literal | 5/5 | 0/5 |
| cross_narrative_impact populated | 0/5 | 1/5 (first ever) |

### Few-Shot Examples (Injected After RULES Section)

**Example 1 (high gap, emerging narrative):**
- Narrative: china_ascent
- Headline: "Institutional flow absorbs every FXI dip below $34 as sell-side consensus warns of structural outflows"
- Gap: 88, Phase: Contradiction Emergence
- Demonstrates: named agents, price levels, probabilistic framing, historical anchoring, cross_narrative_impact

**Example 2 (low gap, mature narrative):**
- Narrative: tech_convergence
- Headline: "QQQ record highs confirm compute-stack consolidation thesis as institutional positioning reaches 92nd percentile"
- Gap: 18, Phase: Consensus Saturation
- Demonstrates: saturation detection, reflexivity alert, positioning-as-fundamental, historical drawdown reference

## Temperature 0.5 Calibration

### Why 0.5

Temperature 0.3 produced safe, repetitive output. Temperature 0.5 introduces lexical variance without sacrificing JSON schema compliance. The `response_format: {"type": "json_object"}` constraint keeps output structurally valid at higher temperatures.

### JSON Sanitization Fallback

Higher temperature risks: trailing commas after last array/object elements, unescaped control characters. The fallback repair pass handles these:

```python
try:
    story = json.loads(content)
except (json.JSONDecodeError, ValueError):
    repaired = re.sub(r',\s*}', '}', content)   # trailing comma in objects
    repaired = re.sub(r',\s*]', ']', repaired)   # trailing comma in arrays
    repaired = repaired.replace('\t', ' ').replace('\n', ' ')
    story = json.loads(repaired)
```

## Cross-Narrative Impact Schema

```json
{
  "cross_narrative_impact": [
    {
      "narrative": "energy_sovereignty",
      "direction": "complicates",
      "mechanism": "Strait closure threatens oil supply, potentially 
                    accelerating China's push for energy independence"
    }
  ]
}
```

- `narrative`: one of the 8 narrative tags (internal IDs, not display names)
- `direction`: "reinforces" | "complicates" | "neutral"
- `mechanism`: 1 sentence clinical macro vector description
- Max 3 entries. Empty array `[]` if no cross-narrative impact.

## f-string Escaping Pitfall

The `SYSTEM_PROMPT` is an f-string (to interpolate `_load_knowledge_base()`). The few-shot examples contain JSON with curly braces `{` and `}`. These MUST be double-escaped as `{{` and `}}` in the few-shot section. The KB prefix is already escaped.

**Fix workflow:**
1. Write the few-shot examples in normal JSON
2. After insertion into the `SYSTEM_PROMPT` f-string, replace all `{` with `{{` and `}` with `}}` ONLY in the few-shot section
3. Do NOT touch the KB section (already escaped) or the JSON schema section (already escaped via `{{` and `}}`)
4. Verify with `python3 -c "import ast; ast.parse(open('contradiction_synthesizer.py').read())"`
