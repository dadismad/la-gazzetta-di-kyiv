# Russian Removal Checklist — June 2026

Complete checklist for scorched-earth removal of Russian language support. If Russian is ever needed again, reverse this checklist.

## Data Files (6 items)

- [x] `data/stories_ru.json` — deleted
- [x] `data/flows_ru.json` — deleted
- [x] `data/ru/` — directory deleted
- [x] `site/data/stories_ru.json` — deleted
- [x] `site/data/flows_ru.json` — deleted
- [x] `site/data/ru/` — directory deleted

## Scripts (1 item)

- [x] `scripts/translate_content.py` — deleted (DeepSeek EN→RU translation engine)

## Config (1 item)

- [x] `config.yaml` → `features.translate_russian: false`

## Test Platform (2 rounds removed)

- [x] `test_platform.py` — ROUND 6 (Translation Sync) function + call removed
- [x] `test_platform.py` — ROUND 7 (RU Zero-English Check) function + call removed

## Deploy Script (2 items)

- [x] `shipit.sh` — Stage 0: removed `site/ru/` and `site/data/ru/` from nuclear clean
- [x] `shipit.sh` — Stage 0: removed `site/ru/` and `site/data/ru/` from mkdir recreation

## Frontend JS (3 files)

- [x] `site/i18n.js` — rewritten to English-only (retained for data-i18n attribute support)
  - Removed `SUPPORTED` array, language detection, `switchLang()`, translation loading
  - Kept `i18n.t()` for dynamic label resolution
- [x] `site/app.js` — 3 RU references removed:
  - `getDataPath()`: removed `_ru` suffix logic
  - `getFlowsPath()`: removed `_ru` suffix logic
  - `nav-flows`: removed `?lang=ru` redirect
  - `lang-en` / `lang-ru` case handlers deleted
- [x] `site/story-app.js` — line 233: removed `lang === 'ru'` path selection

## HTML (13 files)

All `hreflang="ru"` link tags removed from:
- [x] `index.html`
- [x] `about.html`
- [x] `capital.html`
- [x] `event_horizon.html`
- [x] `flow-nodes.html`
- [x] `flows.html`
- [x] `methodology.html`
- [x] `signal.html`
- [x] `sources.html`
- [x] `stories.html`
- [x] `story.html`
- [x] `track.html`
- [x] `trades.html`

Command used: `sed -i '' '/hreflang="ru"/d' *.html`

## GCS (1 directory)

- [x] `site/ru/` — directory deleted. Not recreated during deploy.
