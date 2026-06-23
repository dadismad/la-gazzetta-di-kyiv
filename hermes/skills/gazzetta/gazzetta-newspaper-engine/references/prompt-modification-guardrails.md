# Prompt Modification Guardrails
## For La Gazzetta di Kyiv Pipeline

> **TRIGGER**: Any time someone proposes changing an LLM prompt in the Gazzetta pipeline, apply these checks BEFORE touching code.

---

## The Pattern (observed 3× in one session)

Proposed changes repeatedly targeted wrong files or wrong data structures because work was done from memory rather than from the actual codebase on the VM.

### Incident 1: Tier 1 prompt targeted wrong file
- **Proposed**: Replace system prompt in `telegram_broadcast.py`
- **Reality**: Synthesis prompt lives in `contradiction_synthesizer.py:283`. `telegram_broadcast.py` has NO LLM calls — it only formats and routes.
- **Why**: Caller assumed "Tier 1 = Telegram = telegram_broadcast.py"

### Incident 2: Tier 1 prompt would have broken JSON parser
- **Proposed**: Replace JSON-structured system prompt with free-text "trade card" output format
- **Reality**: The pipeline parses JSON with specific keys (`direction`, `primary_ticker`, `limit_entry_price`, `stop_loss`, `take_profit`, `conviction`, `alpha_trigger`). Free-text output → `json.loads()` crash → pipeline dark.
- **Fix**: Surgical persona injection — replace ONLY the opening paragraph, preserve the full JSON schema and scoring guide.

### Incident 3: Conflated synthesis engine with presentation layer
- **Proposed**: Change synthesis prompt to output markdown trade card format
- **Reality**: Trade card formatting belongs in `format_story_for_telegram()` in `telegram_broadcast.py`. The synthesis engine (`contradiction_synthesizer.py`) must output JSON.
- **Separation**: `contradiction_synthesizer.py` = DATA generation (JSON). `telegram_broadcast.py` = PRESENTATION formatting (markdown for Telegram).

---

## Mandatory Checklist Before Any Prompt Change

### 1. Verify the target file
Run: `ssh gazzetta-prod 'grep -n "SYSTEM_PROMPT\|system_prompt\|DeepSeek\|deepseek" <file>'`
Never assume which file contains the prompt. Load `gazzetta-backend-audit` skill for the canonical prompt map.

### 2. Check downstream parser
For Tier 1 (`contradiction_synthesizer.py`): The output is parsed as JSON. The parser expects specific keys:
- `trade_thesis.direction`, `trade_thesis.primary_ticker`, `trade_thesis.conviction`, etc.
- `contradiction_gap` (int), `narrative_scores` (dict of floats)
- Do NOT change output format. Do NOT remove the JSON schema from the prompt.

### 3. Know which layer you're modifying
| Change type | Target file |
|---|---|
| How stories are generated (persona, editorial voice) | `contradiction_synthesizer.py` (Tier 1), `narrative_pulse.py` (Tier 2), Cron prompt (Tier 3) |
| How stories appear on Telegram (card layout, headers, what fields to show) | `telegram_broadcast.py` → `format_story_for_telegram()` |
| Pipeline orchestration (order, timeouts, dependencies) | `governor.py` → `STEPS` list |

### 4. Use surgical injection when possible
For Tier 1: Replace only the opening persona paragraph. Leave the JSON schema, scoring guide, and output format instructions untouched.

### 5. Test after deploying
Run: `ssh gazzetta-prod 'sudo -u gazzetta /opt/gazzetta-di-kyiv/venv/bin/python -c "import py_compile; py_compile.compile(\"<file>\", doraise=True); print(\"OK\")"'`

---

## Canonical Prompt Locations

| Tier | File | Variable | Line | Output format |
|---|---|---|---|---|
| Tier 1 (synthesis) | `contradiction_synthesizer.py` | `SYSTEM_PROMPT` | ~283 | JSON (parsed by pipeline) |
| Tier 2 (radar) | `narrative_pulse.py` | `system_prompt` (in `generate_radar_alert()`) | ~60 | Free text (queued, sent as-is) |
| Tier 3 (macro lens) | Hermes cron job `6c7645ee6430` | prompt field | — | Free text (posted via SSH+Python) |

⚠️ `telegram_broadcast.py` has NO LLM prompts — it only formats and routes.
