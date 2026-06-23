# i18n Integration Pattern (June 2026)

## Use case
Add language translation to a static HTML + JS website deployed to GCS.

## Architecture
Three components, no build tools, no framework:

### 1. `i18n.js` — lightweight module
```javascript
// Detects language: localStorage > browser > default 'en'
// Loads i18n_ru.json on switch, applies via data-i18n attributes
// Dispatches 'languageChanged' event for app.js to reload data
window.i18n = {
  lang, translations, t(key, fallback),
  switchLang(lang), init()
};
```

### 2. `i18n_ru.json` — translations file
Flat key-value JSON. Every key maps to an English default in the HTML `data-i18n` attribute.
Example keys: `hero_headline`, `container_stories_title`, `flow_inflows`, `tension_max`

### 3. HTML integration
- `<html lang="en">` — language attribute
- `data-i18n="key"` on every translatable element
- `<button class="lang-switch" data-lang="ru" onclick="i18n.switchLang('ru')">RU</button>` — masthead switcher
- `<script src="./i18n.js"></script>` — MUST be before app.js
- Dynamic content (stories) loads language-specific JSON: `stories_ru.json`

### 4. Pipeline integration (future)
`translate_content.py` — reads `stories.json`, translates via LLM API, writes `stories_ru.json`.
Frontend loads `stories_ru.json` when `i18n.lang === 'ru'`.

## Common failure modes
- **i18n.js not loaded** — check `<script>` tag is before app.js
- **i18n_ru.json 404** — check GCS deploy synced the file
- **data-i18n elements not translating** — `i18n.init()` not called, or translations.json key mismatch
- **Dynamic content stays English** — app.js needs to listen for `languageChanged` event and reload data
- **⚠️ RU page loads but shows English/empty** — THREE stacked bugs to check:

### Stacked Bug #1: Path detection missing (i18n.js)
`detectLang()` checks localStorage then browser language — never the URL path.
Visiting `/ru/` detects `en` → i18n never activates.
**Fix:** Add path check FIRST in `detectLang()`:
```javascript
function detectLang() {
  if (window.location.pathname.match(/^\/ru(?:\/|$)/i)) return 'ru';
  // ... localStorage, browser, default 'en'
}
```

### Stacked Bug #2: Stale script hashes (shipit.sh ordering)
`ru_sync_gate` (Stage 2.6) copies EN index.html to `site/ru/` BEFORE the hash stage (Stage 3) rewrites script references. RU index gets OLD hashes — loads stale JS that doesn't have the path-detection fix.
**Fix:** Move `ru_sync_gate` to AFTER `build_hashed_assets` (new Stage 3.1).
**Detection:** `grep 'script src' site/ru/index.html site/index.html` — must show SAME hashes.

### Stacked Bug #3: Relative paths resolve to /ru/ (GCS deployment)
RU page serves from `/ru/`, so `./i18n.7dcc40be.js` → `/ru/i18n.7dcc40be.js` → **404**.
Also: `./i18n_ru.json` → `/ru/i18n_ru.json`, `./data/stories.json` → `/ru/data/stories.json`.
**Fix:** Deploy these files to GCS `/ru/` directory:
```bash
gsutil cp site/ru/index.html gs://BUCKET/ru/index.html
gsutil -h "Cache-Control:public, max-age=31536000, immutable" \
  cp site/ru/i18n.*.js site/ru/app.*.js site/ru/styles.*.css gs://BUCKET/ru/
gsutil cp site/ru/i18n_ru.json gs://BUCKET/ru/i18n_ru.json
gsutil -m -h "Cache-Control:private, no-store" rsync -d site/ru/data/ gs://BUCKET/ru/data/
```
**Permanent fix for shipit.sh:** Add RU asset rsync to Stage 4 (GCS deploy).

## Verification
```javascript
// Console check
JSON.stringify({
  i18nExists: typeof i18n !== 'undefined',
  lang: i18n?.lang,
  translations: Object.keys(i18n?.translations || {}).length
})
// Expected: {i18nExists: true, lang: "ru", translations: 61}
```
