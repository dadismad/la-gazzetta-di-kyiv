# i18n CI/CD Validation Pipeline (v22.15+)

## Problem

Translation coverage degrades silently after every container label change. HTML elements without `data-i18n` attributes stay English in Russian mode with zero console errors. JS `i18n.t()` keys can be added to app.js without corresponding RU translations. The deploy pipeline has no gate.

## Solution

`scripts/validate_i18n.py` — pre-deploy validation that:
1. Extracts all `data-i18n` keys from HTML files
2. Extracts all `i18n.t('key', ...)` keys from JS files  
3. Diffs canonical keys against each locale JSON file
4. Fails (exit 1) if any key is missing from any locale
5. Warns about orphaned keys in locale files (extra keys with no canonical match)

## Integration

Added as step 5/5 in `gazzetta_pipeline_chain.sh` (runs after build_site):

```bash
echo "[5/5] validate_i18n..."
python3 scripts/validate_i18n.py || { echo "❌ i18n validation FAILED — deploy blocked"; exit 1; }
```

The deploy step only runs if validation passes. If validation fails, the entire pipeline exits with error — no broken translations reach production.

## Runtime

```bash
GAZZETTA_ROOT=/path/to/site python3 scripts/validate_i18n.py
```

Default GAZZETTA_ROOT: `~/projects/gazzetta-di-kyiv/site`

## What it catches

| Failure mode | Caught? |
|---|---|
| `data-i18n` attribute added to HTML, missing from RU | ✅ Fail |
| `i18n.t('new_key')` added to JS, missing from RU | ✅ Fail |
| Orphaned keys in RU (safe to remove) | ⚠️ Warn |
| Translation value still English (`"buy": "BUY"`) | ❌ NOT caught — manual review needed |
| Key exists in RU but value is wrong/truncated | ❌ NOT caught — manual review needed |

## Gap: Untranslated value detection

The validator checks key EXISTENCE, not key VALUES. A key like `"buy": "BUY"` passes validation because the key exists, but the value is the English fallback. Detection: after validation, run a value-quality check:

```bash
python3 -c "
import json
ru = json.load(open('site/i18n_ru.json'))
en_keys = ['buy','sell','watch','confidence_high','confidence_low']
for k in en_keys:
    if ru.get(k, '').upper() == k.upper():
        print(f'UNTRANSLATED: {k} -> {ru[k]}')
"
```

## Force-overwrite pitfall

When adding translations, avoid `if k not in ru: ru[k] = v` — this skips existing keys with wrong values. Always use unconditional `ru[k] = v` for corrections. Verify with the value-quality check above.
