# Pipeline Data-First Diagnosis (June 2026)

## The Rule

**Before theorizing about prompt engineering or LLM behavior as the cause of a pipeline bug, always check the actual output data first.**

## What Happened

The frontend showed 191 stories with "No active thesis" on every card. The initial diagnosis blamed the system prompt's redundancy rule (line 388 of `contradiction_synthesizer.py`) — theorizing that DeepSeek was defaulting to NEUTRAL to avoid duplication.

This diagnosis was **completely wrong**. The actual data told a different story:

```bash
curl -sk https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
stories = d.get('all_stories', [])  # NOTE: key is 'all_stories', NOT 'stories'
active = sum(1 for s in stories if (s.get('trade_thesis') or {}).get('direction','') not in ('NEUTRAL','MISSING',''))
neutral = sum(1 for s in stories if (s.get('trade_thesis') or {}).get('direction','') == 'NEUTRAL')
empty = sum(1 for s in stories if not s.get('trade_thesis') or not isinstance(s.get('trade_thesis'), dict))
print(f'{len(stories)} total, {active} active, {neutral} NEUTRAL, {empty} empty/missing')
"
# Result: 401 total, 33 active, 35 NEUTRAL, 368 empty/missing
```

368 of 401 stories (92%) had NO `trade_thesis` field at all — the field was simply absent from the JSON. Only 35 stories had NEUTRAL (9%). The problem was NOT the redundancy rule pushing to NEUTRAL — it was that the trade_thesis field wasn't being generated.

The root cause: `max_tokens=1200` was too tight for the full JSON schema. DeepSeek generated valid JSON but ran out of tokens before reaching the `trade_thesis` field (which was the LAST field in the schema). `json.loads()` accepted the partial output because it was structurally valid.

## The Pattern

When a field is missing from pipeline output STORIES:

1. **Query the actual data endpoint first.** Use curl + python one-liner to count field presence.
2. **Check which key the data lives under.** Gazzetta uses `all_stories` not `stories` in the JSON envelope. Querying the wrong key returns 0 results, leading to false conclusions.
3. **Classify the failure mode.** Is the field missing entirely (empty), set to a default value (NEUTRAL), or populated but wrong?
4. **Only then theorize about cause.** If 92% are missing and 9% are NEUTRAL, the problem is token budget, not prompt logic.

## Why This Matters for QA Personas

When a QA persona reports "0 active trade theses on all cards," the first follow-up is NOT "let me check the prompt." It's:

```bash
curl -sk $SITE/data/stories.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
all_s = d.get('all_stories', [])
tt = [(s.get('trade_thesis') or {}).get('direction','MISSING') for s in all_s]
from collections import Counter
print(Counter(tt))
"
```

This gives you the exact distribution in 5 seconds and prevents multi-hour wild goose chases into prompt engineering when the real issue is a 2-character config change (`max_tokens: 1200` → `2400`).
