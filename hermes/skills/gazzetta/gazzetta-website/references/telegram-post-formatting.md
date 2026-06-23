# Telegram Post Formatting (v27.1 — June 2026)

## Problem: Wall of text, no paragraphs, broken scores

The `cco_telegram.py` `format_story()` function produced unreadable Telegram messages:

```
<b>Iran denies Trump's claims...</b>
INFLOW | Contradiction: 5000% | Confidence: 5000%
They Say: Iran denies...
Reality: 
Reuters — lagazzettadikyiv.com
```

### Root Causes

1. **Contradiction score as percentage**: `{contradiction:.0%}` on score 50 → displayed "5000%" instead of "50/100". The Python `:.0%` format multiplies by 100 — but scores are already on a 0-100 scale.

2. **Confidence same bug**: `{confidence:.0%}` on 50 → "5000%" instead of "50%". The confidence is already a percentage.

3. **No paragraph breaks**: Everything joined with `\n` (single newlines) — no empty lines between sections.

4. **Empty sections still shown**: "They Say:" and "Reality:" headers rendered even when the field was empty (70 stories have no reality text).

5. **No visual hierarchy**: Single blob of text with pipes `|` between unrelated metrics.

## Fixed Format

```
🔴 **Medicare Advantage plans denied prior authorization...**
📈 INFLOW · $0.1B · TECH
Contradiction: 75/100 · Confidence: 50%

**THEY SAY**
[consensus narrative text]

**REALITY**
[contradiction evidence text]

🎯 **THE PLAY**
[trade implication]

osint_reuters_business · lagazzettadikyiv.com/story.html?id=...
```

### Key Changes

| Aspect | Before | After |
|--------|--------|-------|
| Tier indicator | 🚨 CONTRADICTED in text | 🔴/🟡/🟢 color emoji only |
| Score display | `5000%` | `75/100` |
| Confidence | `5000%` | `50%` |
| Section breaks | Single `\n` | Double `\n` (paragraphs) |
| Empty sections | Headers shown with no text | Entirely omitted |
| They Say/Reality | `They Say: [text]` | `**THEY SAY**` header + text below |
| Play | Inline text | `**🎯 THE PLAY**` section |
| Footer | `source — lagazzettadikyiv.com` | `source · lagazzettadikyiv.com/story.html?id=...` |
| Flow data | In meta line | Separate row with emoji direction |
| Velocity | Always shown | Only shown if `pace != 1.0` |

### Files Changed

- `scripts/cco_telegram.py` — `format_story()` function (primary posting path, parse_mode=HTML)
- `scripts/generate_broadcasts.py` — `generate_telegram_post()` function (draft generation, Markdown format)
- `agents_build/cco_telegram.py` — Cloud Run build copy (must be kept in sync with scripts/)

### Pitfall: Two code paths

`cco_entrypoint.py` calls `cco_telegram.py` (HTML parse mode). `generate_broadcasts.py` has its own `generate_telegram_post()` (Markdown/plain text). Both must produce the same structure. When changing one, change both.

### Dry-Run Test

```bash
cd ~/lagazzettadikyiv
python3 -c "
import json, sys
sys.path.insert(0, 'scripts')
from cco_telegram import format_story
data = json.load(open('data/stories.json'))
s = data['stories'][0]
print(format_story(s))
"
```
