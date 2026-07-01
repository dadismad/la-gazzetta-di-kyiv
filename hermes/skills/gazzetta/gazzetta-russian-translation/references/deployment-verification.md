# Deployment Verification Checklist

**CRITICAL**: User evaluates work by live website state, not commits or GitHub.

## Before deploying
1. Bump BOTH `i18n.js?v=X.YY` AND `app.js?v=X.YY` in `site/index.html`
2. `node --check site/app.js` — no syntax errors
3. If new stories: regenerate `stories_ru.json` via `translate_content.py`

## Deploy
```bash
export PATH="$HOME/lagazzettadikyiv/google-cloud-sdk/bin:$PATH"
gsutil -m -h "Cache-Control:public, max-age=0, must-revalidate" rsync -r site/ gs://www.lagazzettadikyiv.com/
```

## Verify (mandatory — do NOT skip)
1. Navigate to `https://www.lagazzettadikyiv.com/?nocache=<timestamp>`
2. Check console: `browser_console(clear=true)` — should have 0 errors
3. Verify rendering: `document.querySelectorAll('.card').length` — should be > 0
4. Verify i18n: `window.i18n?._ready` — should be `true`
5. Click Русский button, wait for reload
6. Verify Russian labels: `document.querySelector('.cf-label')?.textContent` — should be `"ПОТОК КАПИТАЛА"`
7. Verify Russian headline: `document.querySelector('.card h3')?.textContent` — should contain Cyrillic

## Common failures
- **0 cards, 5 empty JS errors**: extremum field is object not string → fix `extremumLineHTML()` with `typeof` guard
- **Cards render English labels in Russian mode**: i18n.js not version-bumped → browser loaded old i18n.js without `_ready` flag
- **CDN stale content**: `curl -sI` to check `cache-control` and `age` headers
