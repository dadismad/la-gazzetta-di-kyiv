# Prompt Modification Guardrails

Mandatory checklist before modifying any LLM prompt in the Gazzetta pipeline.

## Pre-Modification

1. **Identify the correct file**: Cross-reference with `gazzetta-backend-audit` → LLM Prompts table. Do NOT assume — verify on the VM.
2. **Identify the output format**: Is the LLM expected to produce JSON? Free text? A specific template? Downstream parsers depend on this.
3. **If JSON output**: List every key the downstream parser reads. The new prompt MUST include the same schema.

## Common File-Mapping Errors (all occurred in production)

| Wrong target | Correct target | Why |
|---|---|---|
| `telegram_broadcast.py` | `contradiction_synthesizer.py` | `telegram_broadcast.py` has no LLM calls — it only formats and routes |
| `governor.py` | `contradiction_synthesizer.py` | Governor orchestrates, doesn't synthesize |

## Common Field-Name Errors (all caused silent failures)

| Wrong field | Correct field | Context |
|---|---|---|
| `story['trade_conviction']` | `story['trade_thesis']['conviction']` | Conviction is nested inside trade_thesis |
| `story['narrative_tag']` | `story['narrative_id']` (fallback: `container`) | narrative_tag is SQLite column, not JSON field |
| `trade_thesis['gap']` | `story['contradiction_gap']` | contradiction_gap is top-level, not in trade_thesis |
| `story['id']` | `story['story_id']` | The primary key field is story_id |
| `trade_thesis['entry']` | `trade_thesis['limit_entry_price']` | Entry field name is limit_entry_price |

## Post-Modification Verification

1. **Compile check**: `python3 -c "import py_compile; py_compile.compile(path, doraise=True)"`
2. **Pipeline dry run**: Run governor.py and check each step's output
3. **Parser check**: Verify downstream readers get expected values (not None)
4. **Broadcast check**: Verify Telegram posts format correctly
5. **Deploy**: `build_frontend.py` + `deploy_to_gcs.py` + CDN invalidation

## Shell Escaping: Use Python, Not Sed

**Pitfall**: Using `sed` to patch files on the VM fails silently when the replacement string contains `&`. In sed, `&` in the replacement is a special character meaning "the matched text" — it does NOT insert a literal ampersand. This is especially dangerous for URLs with query parameters.

```bash
# WRONG — & gets expanded to the matched text, mangling the URL
sudo sed -i 's|old|https://example.com?utm_source=telegram&utm_medium=tier1|g' file.py

# CORRECT — use Python for all file patches
sudo python3 -c "
content = open('file.py').read()
content = content.replace('old', 'https://example.com?utm_source=telegram&utm_medium=tier1')
open('file.py', 'w').write(content)
"
```

**Always prefer Python `str.replace()` over `sed` for file patching on the VM.** The escaping rules for shell → sed → regex are three layers deep and every layer introduces failure modes. Python has one layer: the string.

## SQLite Access Pattern

Querying `gazzetta.db` requires `sudo -u gazzetta` — the `alexstocchi` user doesn't own the file and SQLite creates journal files in the DB directory even for reads:

```bash
# WRONG — fails with "attempt to write a readonly database"
sqlite3 /opt/gazzetta-di-kyiv/data/gazzetta.db "SELECT ..."

# CORRECT
sudo -u gazzetta sqlite3 /opt/gazzetta-di-kyiv/data/gazzetta.db "SELECT ..."
```
