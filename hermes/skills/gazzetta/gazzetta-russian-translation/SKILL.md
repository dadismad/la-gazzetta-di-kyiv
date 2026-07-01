---
name: gazzetta-russian-translation
description: Full Russian translation pipeline for Gazzetta di Kyiv — translate story content, inline labels, static HTML. Integrate i18n into app.js and deploy.
---

# Gazzetta Russian Translation Pipeline

## When to use
- User asks about Russian translation on the Gazzetta website
- After new stories are created — run translation to update `stories_ru.json`
- Labels or UI strings added to app.js need Russian equivalents

## Architecture

Three independent translation layers:

### Layer 1: Static HTML text (data-i18n)
- `index.html` elements have `data-i18n="key"` attributes
- `i18n.js` loads `i18n_ru.json` and applies to DOM
- **Always works** — no race condition, no API needed
- Keys: hero text, container titles, descriptions, footer

### Layer 2: Inline labels in app.js (i18n.t())
- app.js uses `i18n.t('key', 'fallback')` for all user-facing strings
- Translations come from `i18n_ru.json` (loaded by `i18n.js`)
- **Race condition (FIXED v20.29)**: app.js may render before i18n finishes loading translations. `i18n.js` dispatches `i18nReady` event after `_ready = true`. `boot()` MUST poll-wait for this:

```javascript
async function boot() {
  // Wait for i18n translations to finish loading before rendering
  if (window.i18n && !window.i18n._ready) {
    await new Promise(resolve => {
      const check = () => {
        if (window.i18n._ready) { resolve(); return; }
        setTimeout(check, 50);
      };
      window.addEventListener('i18nReady', resolve, { once: true });
      check();
      setTimeout(resolve, 5000); // hard safety
    });
  }
  // ... rest of boot
}
```

**Without this fix**: cards render with English fallbacks even though i18n.t() would return Russian after translations load. Symptom: `i18n.t('capital_flow_label')` returns `"ПОТОК КАПИТАЛА"` but DOM shows `"CAPITAL FLOW"`.

### Layer 3: Story content translation (stories_ru.json)
- `scripts/translate_content.py` translates story headlines, body, flows
- Uses DeepSeek API, batched in chunks of 20
- Output: `data/stories_ru.json` → copied to `site/data/stories_ru.json`
- **Requires**: DeepSeek API key in `DEEPSEEK_API_KEY` env var

## DeepSeek API: Chinese-Language Bug (CRITICAL — v23.7)

The DeepSeek API sometimes returns **Chinese (CJK) characters** instead of Russian Cyrillic when asked to translate, even when the prompt says "Russian." This is because DeepSeek is a Chinese company's model and defaults to Chinese for certain input patterns. The bug is silent — the API returns HTTP 200 with plausible-looking text, but it's the wrong language.

**Detection:**
```bash
python3 -c "
import json
with open('data/stories_ru.json') as f: d=json.load(f)
bad=[s['story_id'][:40] for s in d['stories'] if not any(0x0400<=ord(c)<=0x04FF for c in str(s.get('headline','')))]
print(f'Non-Cyrillic: {len(bad)}')"
```

**Fix: Explicit prompt** — add "NOT Chinese. NOT any other language. Russian only (русский язык, Cyrillic script)." to the translation prompt. Verify output contains Cyrillic before saving.

**Post-translation verification (v23.7+):**
```python
result = resp.json()['choices'][0]['message']['content'].strip()
if not any(0x0400 <= ord(c) <= 0x04FF for c in result):
    print(f'WARNING: Got non-Cyrillic response: {result[:60]}...')
    # Fall back to English or retry
```

## Checkpointing Pattern (translate_content.py v2.0)

To handle frequent API timeouts, the translation script uses incremental checkpointing:

- **Batch size:** 3 stories (avoids timeout on slow responses)
- **Checkpoint table:** `translation_checkpoint` in `gazzetta.db` — records `story_id` + `translated_at` + `status`
- **Resume:** `python3 scripts/translate_content.py --resume` picks up exactly where it left off
- **Dry-run:** `python3 scripts/translate_content.py --dry-run` shows what would be translated without API calls
- **Save after every batch** — if the process dies mid-run, only the current batch is lost, not all previous work

Never run the old monolithic translation approach (all stories in one API call). Always use checkpointing.

## Quick fix: Re-translate stories (v23.7+ checkpointing)

`translate_content.py v2.0` uses SQLite checkpointing — batches of 3, resumes on restart. **Always use `--resume` for incremental runs:**

```bash
cd /Users/alexstocchi/projects/gazzetta-di-kyiv

# First run — check what needs translation (dry-run)
.venv/bin/python scripts/translate_content.py --dry-run

# Run translation with checkpointing
.venv/bin/python scripts/translate_content.py

# If timeout — resume exactly where it left off
.venv/bin/python scripts/translate_content.py --resume

# Verify coverage
.venv/bin/python -c "
import json
with open('data/stories.json') as f: en=json.load(f)
with open('data/stories_ru.json') as f: ru=json.load(f)
en_ids={s['story_id'] for s in en['stories']}
en_ids.add(en.get('lead',{}).get('story_id',''))
ru_map={s['story_id']:s for s in ru['stories']}
cyr=sum(1 for sid in en_ids if sid in ru_map and any(0x0400<=ord(c)<=0x04FF for c in str(ru_map[sid].get('headline',''))))
print(f'EN with Cyrillic RU: {cyr}/{len(en_ids)}')
"
```

## Deploying (CRITICAL — VERIFY THE WEBSITE, NOT GITHUB)

**User evaluates work by the live website state, not commits or GitHub Pages.** Every deployment must end with a live verification on `www.lagazzettadikyiv.com`.

**www.lagazzettadikyiv.com → GCS bucket, NOT GitHub Pages.** The custom domain is served from a Google Cloud Storage bucket behind an HTTPS load balancer. `pureciclismo.github.io/gazzetta-di-kyiv` is the GitHub Pages build — useful for quick sanity checks but NOT the live site the user sees.

Every deploy:
1. **Bump both cache-busters in `index.html`**: `<script src="./i18n.js?v=X.YY">` AND `<script src="./app.js?v=X.YY">` — both scripts need version params. Without bumping i18n.js, browsers keep loading old i18n.js without `_ready` flag → boot() race condition.
2. **Sync to GCS with max-age=0**: `gsutil -m -h "Cache-Control:public, max-age=0, must-revalidate" rsync -r site/ gs://www.lagazzettadikyiv.com/`
3. **Verify on live site**: Navigate to `https://www.lagazzettadikyiv.com/?nocache=<timestamp>`, check DOM for correct labels/text. Use `browser_console` to check `i18n._ready`, `document.querySelectorAll('.card').length`, and label text.
4. **Set metadata on all existing files once**: `gsutil -m setmeta -r -h "Cache-Control:public, max-age=0, must-revalidate" gs://www.lagazzettadikyiv.com/*.html gs://www.lagazzettadikyiv.com/*.js gs://www.lagazzettadikyiv.com/*.json gs://www.lagazzettadikyiv.com/*.css gs://www.lagazzettadikyiv.com/data/*.json`

All files now use `max-age=0, must-revalidate` — changes go live instantly. No more 3600-second waits.

## Professional RU Terminology (v23.6+)

RU translations must sound like professional financial telegram/trading-desk terminology. Replace literal machine translations with fintech-standard terms: "История" → "Интел-Репорт", "Потоки" → "Телеметрия Потоков", "Трек-Рекорд" instead of "Послужной список". Full terminology guide: `references/ru-professional-terminology.md`.

## Atomic EN/RU Output (v23.6+)

`scripts/db_to_json.py` now writes atomically to `data/en/` and `data/ru/` directories, then syncs to `site/data/en/` and `site/data/ru/` for deployment. The `data/` root retains backward-compatible copies. Translation gap detection runs during compilation — warns when RU coverage < EN.

## Adding new i18n keys

1. Add key to `site/i18n_ru.json` with Russian value
2. Use in app.js: `i18n.t('new_key', 'English fallback')`
3. Deploy both files

## Pitfalls

### Silent boot crash: `extremum` object format (CRITICAL — v20.27)
Newer stories store `extremum` as an object `{type, description}`, not a pipe-delimited string. The `extremumLineHTML()` function calls `.split()` → `TypeError: extremumStr.split is not a function` → boot() crashes → ZERO story cards render. 5 empty JS errors in console, no readable message. **Always check extremum format before rendering.** Fix: add `typeof extremumStr === 'object'` guard. Check with:
```bash
python3 -c "import json; d=json.load(open('site/data/stories.json')); print([type(s.get('extremum')).__name__ for s in d['stories']])"
```

### Missing `data-i18n` attributes on HTML elements → silent English (CRITICAL)
All 108 Russian translations exist in `i18n_ru.json`. But the i18n engine (`i18n.js`) only translates elements that carry `data-i18n="key"` attributes. If an HTML element has hardcoded English text without the attribute, it STAYS English when the user clicks Русский — no error, no console warning, just silently wrong.

**Symptom:** Hero + stories translate correctly, but containers 2-5 (Flows, Trades, Signal, Track Record) show English titles/descriptions. Users see "Your trades this week" instead of "Ваши сделки на этой неделе."

**Diagnosis:**
```bash
# Check all data-i18n attributes on the live page
curl -s https://www.lagazzettadikyiv.com | grep -oP 'data-i18n="[^"]*"' | sort

# Find container titles/subtitles/descs WITHOUT data-i18n
curl -s https://www.lagazzettadikyiv.com | grep -E 'container-title|container-subtitle|container-desc|asset-note' | grep -v 'data-i18n'
```

**Fix:** Add `data-i18n="<key>"` to every hardcoded English element. All keys already exist in `i18n_ru.json` — no translation work needed, just HTML attributes. The full list of elements needing attributes:

| Element | Missing key | Russian already exists? |
|---------|------------|------------------------|
| Flows container title | `container_flows_title` | ✓ "Куда идут умные деньги" |
| Flows container desc | `container_flows_desc` | ✓ |
| Flows footer note | `container_flows_footer` | ✓ |
| Anchors container title | `container_anchors_title` | ✓ "Ваши сделки на этой неделе" |
| Anchors container subtitle | `container_anchors_subtitle` | ✓ "Торговые идеи" |
| Anchors container desc | `container_anchors_desc_prefix` | ✓ |
| Signal container title | `container_signal_title` | ✓ "Сигнал" |
| Signal container subtitle | `container_signal_subtitle` | ✓ |
| Signal container desc | `container_signal_desc` | ✓ |
| Signal footer note | `container_signal_footer` | ✓ |
| Track container title | `container_track_title` | ✓ "Послужной список" |
| Track container subtitle | `container_track_subtitle` | ✓ |
| Track container desc | `container_track_desc` | ✓ |
| PDR label | `pdr_label` | ✓ |
| Anchor key levels note | `anchor_note_key_levels` | ✓ |
| Anchor PDR note | `anchor_note_pdr` | ✓ |

**Text duplication pitfall:** When the element contains a child (e.g., `<span id="anchorCount">`), wrapping the trailing text in `<span data-i18n>` MUST capture the ENTIRE text node. If the replace only matches the prefix, the original text suffix survives outside the span and duplicates. Use regex with `.*?(?=</div>)` to capture the full text, or verify the fix by checking for duplicated StaticText in the browser snapshot after deploy.

### Template literal escape bug
When converting hardcoded strings to `i18n.t()` inside backtick template literals, use `${i18n.t(...)}`, NOT `' + i18n.t(...) + '`. The latter is a literal string inside backticks, not JS code. `node --check` passes (syntax is valid as a string), but at runtime the template literal contains literal `' +` characters. **Bulk replacements**: use Python scripts via terminal — the patch tool escapes `\"` incorrectly in JS.

### GCS deployment (see gazzetta-website for full details)
- `www.lagazzettadikyiv.com` → GCS bucket. NOT GitHub Pages.
- **All files now use `max-age=0, must-revalidate`** — no more 3600-second waits.
- Every deploy: bump BOTH `i18n.js?v=X.YY` AND `app.js?v=X.YY` in `index.html`, then `gsutil -m -h "Cache-Control:public, max-age=0, must-revalidate" rsync -r site/ gs://www.lagazzettadikyiv.com/`
- `getJSON()` appends `?t=Date.now()` as defense-in-depth against CDN caching.
- Verify: `curl -s "https://www.lagazzettadikyiv.com/data/stories_ru.json?t=$(date +%s)" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['lead']['headline'][:60])"`

## Creating a `/ru/` Subdirectory for Direct URL Access (v23.0 — June 2026)

The i18n language toggle works for users who visit the root page and switch languages. But `/ru/` returns 404 unless you create a `site/ru/` subdirectory with copies of all product pages that auto-detect Russian.

### Recipe: RU subdirectory pages

```bash
cd /Users/alexstocchi/projects/gazzetta-di-kyiv
mkdir -p site/ru

# Copy all product pages
for f in index.html stories.html flows.html signal.html trades.html track.html event_horizon.html flow-nodes.html story.html; do
  cp site/$f site/ru/$f
done
```

Each RU page needs three modifications:

**1. `<base href="/">`** — ensures all relative URLs (`./app.js`, `./styles.css`, `./data/stories.json`) resolve from the bucket root, not from `/ru/`. Without this, `./app.js` resolves to `/ru/app.js` (404).

```html
<head>
  <base href="/">
```

**2. Pre-i18n language detection script** — insert BEFORE the first `<script src>` tag. This sets `localStorage` before `i18n.js` loads, so `detectLang()` returns `'ru'` immediately:

```html
<script>window.__GAZZETTA_LANG="ru";localStorage.setItem("gazzetta_lang","ru");</script>
<script src="./i18n.XXXXXXXX.js"></script>
```

**3. hreflang alternate + canonical links** — insert inside `<head>` for SEO:

```html
<link rel="alternate" hreflang="en" href="/index.html">
<link rel="alternate" hreflang="ru" href="/ru/index.html">
<link rel="canonical" href="/ru/index.html">
```

### Verification

```bash
# RU page returns 200 (was 404 before)
curl -sI https://www.lagazzettadikyiv.com/ru/ | head -3

# RU page shows Russian text
curl -s https://www.lagazzettadikyiv.com/ru/ | grep -o 'Капитал движет'

# Browser: document.querySelector('html').lang === 'ru'
```

### shipit.sh integration

No changes needed — `shipit.sh` Stage 4 (`gsutil -m rsync -r site/`) automatically syncs `site/ru/` to GCS. The RU pages are built once (above) and then carried forward by every deploy.

### Known gaps (v23.6 status)

**✅ FIXED — Nav links (7 items):** Navigation links now carry `<span data-i18n="nav_stories">Stories</span>` wrappers. RU renders: Интел-Репорты, Потоки, Горизонт, Узлы, Сигнал, Сделки, Трек. Recipe: regex-replace `<a class="nav-link">Stories</a>` → `<a class="nav-link"><span data-i18n="nav_stories">Stories</span></a>` for each link, then add keys to `i18n_ru.json`.

**✅ FIXED — Layer labels (2 items):** INTEL/ALPHA layer labels now have `data-i18n="layer_intel"` and `data-i18n="layer_alpha"`. Layer descriptions also translated.

**✅ FIXED — Sidebar labels (6 items):** TRADE HOOKS→СИГНАЛЫ, TOP VELOCITY→СКОРОСТЬ, SENTIMENT→НАСТРОЕНИЕ, FRESHNESS→СВЕЖЕСТЬ, NAVIGATE→НАВИГАЦИЯ, GAZZETTA→ГАЗЕТТА.

**⚠ REMAINING — Services grid + hero indicators:** "HOW WE SERVE YOU", "C-SUITE", "QUANTITATIVE", "EXECUTION" and hero indicator labels (Contradictions, Top Velocity, Freshness) are JS-populated or hardcoded without data-i18n. Services grid needs `data-i18n` attributes added to HTML templates. Hero indicators need app.js changes (scope-fragile — avoid for now).

### DeepSeek API Chinese-output bug (CRITICAL — v23.7)

DeepSeek sometimes outputs **Chinese (CJK)** instead of Russian even when explicitly asked for Russian. This is a known issue with the DeepSeek model — it defaults to its training language. **Always verify the output contains Cyrillic before accepting it:**

```python
def tr(text):
    result = api_call(text)
    if not any(0x0400 <= ord(c) <= 0x04FF for c in result):
        print(f'WARNING: Got non-Cyrillic: {result[:60]}...')
        # Retry with explicit language instruction
        result = api_call(f"Translate to RUSSIAN (русский язык, Cyrillic script). NOT Chinese. NOT any other language. Russian only:\n\n{text}")
    return result
```

**Fix prompt:** Replace `"Russian translation"` with `"Translate to RUSSIAN (русский язык, Cyrillic script). NOT Chinese. NOT any other language. Russian only. Keep numbers and symbols intact:"`. Lower temperature (0.2 vs 0.3) also helps.

### DeepSeek API batch size pitfall (v23.6)

The `translate_content.py` batches of 20 routinely time out (180s+). **Working batch size: 3-4 stories.** Each story takes ~8-15s via the API. Use a small inline Python script rather than the full `translate_content.py` for incremental translation:

```python
# Inline translation pattern (3-4 stories, reliable):
batch = untranslated[:4]
for story in batch:
    story['headline'] = tr(story.get('headline',''))
    story['summary'] = tr(story.get('summary',''))
    time.sleep(0.3)
```

Track translation coverage via RU story_id set intersection, not raw array length. The `_untranslated` flag marks English fallbacks in `stories_ru.json`.

## Verification

**Full checklist**: `references/deployment-verification.md`

Quick checks:
# Check stories_ru.json has Cyrillic
python3 -c "import json; d=json.load(open('site/data/stories_ru.json')); print(any(0x0400<=ord(c)<=0x04FF for c in str(d['stories'][0])))"
# Should print: True

# Check live site
curl -s "https://www.lagazzettadikyiv.com/data/stories_ru.json?t=$(date +%s)" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['stories'][0]['headline'][:80])"
```

## Files involved
- `site/i18n.js` — language detection, switching, translation loader
- `site/i18n_ru.json` — 122+ Russian translations (keys only, no nesting)
- `site/app.js` — uses `i18n.t()` for inline labels, `getDataPath()` for language-specific data
- `scripts/translate_content.py` — DeepSeek-powered story content translation (batched)
- `data/stories_ru.json` — translated story data (generated)
- `site/data/stories_ru.json` — deployed copy
