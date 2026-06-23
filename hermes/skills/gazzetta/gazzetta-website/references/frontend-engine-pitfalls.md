# Frontend Engine Pitfalls (June 2026)

Lessons from the index_v6 production hotfix cycle.

## Pitfall 1: Material Symbols Font URL Missing `opsz` Axis

**Symptom:** 343 Material Symbols icons render at 0x0 pixels. Icon codenames (`auto_stories`, `sync_alt`, `call_split`, `account_tree`, `arrow_forward`, `trending_down`, `bolt`, etc.) display as raw visible text across all navigation, alerts, and cards.

**Root cause:** The Google Fonts API URL is malformed — it specifies `wght,FILL@100..700,0..1` but omits the mandatory `opsz` (optical size) axis. Without `opsz`, the browser drops the font face and renders the raw ligature text.

**Correct URL:**
```
https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap
```

**Detection:** Check icon element dimensions. Working icons have `offsetWidth > 0` (typically 14-24px). Broken icons have `offsetWidth === 0`.
```js
Array.from(document.querySelectorAll('.material-symbols-outlined')).filter(s => s.offsetWidth === 0).length
```

## Pitfall 2: Missing `font-variation-settings` CSS Rule

**Symptom:** Even with the correct font URL, icons may still render at 0x0 if the CSS doesn't explicitly set variation axis values.

**Mandatory CSS rule:**
```css
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  display: inline-block;
  line-height: 1;
}
```

This rule MUST be in the `<style>` block, not just inline on individual elements. Inline `style="font-variation-settings:'FILL'1"` on filled icons still works — the CSS rule sets the default for outlined icons.

## Pitfall 3: DOM Order — Sidebar Before Masthead

**Symptom:** On mobile viewports, ticker-based narrative pills ("DXY RESERVE CURRENCY REALIGNMENT 258.9B") appear ABOVE the masthead as the first thing a visitor sees. "Incomprehensible information at the top."

**Root cause:** The `<aside id="desktop-sidebar">` is the first child of `<body>`. On desktop (`md:flex`), it's a fixed-position sidebar — acceptable. On mobile (where the `hidden` class should apply), it renders as inline block at the top of the page.

**Fix:** Move the sidebar inside the main content container, AFTER `<header>` (masthead), BEFORE tab navigation. The masthead must be the first visual element on every viewport.

**Correct DOM order:**
```
HEADER (masthead) → ASIDE (sidebar) → NAV (tabs) → MAIN (content)
```

## Pitfall 4: Desktop/Mobile Nav Breakpoint Leakage

**Symptom:** Both desktop tab bar AND mobile bottom nav visible simultaneously on desktop viewport.

**Root cause:** Desktop nav container lacks `hidden` class for mobile. Mobile nav correctly has `md:hidden` but desktop nav has no corresponding mobile-hide.

**Fix:**
- Desktop tab nav container: `hidden md:flex` (hidden on mobile, flex on desktop)
- Mobile bottom nav: `md:hidden flex` (hidden on desktop, flex on mobile)

Never use a bare nav without a breakpoint visibility class.

## Pitfall 5: Post-Promotion Path Leak

**Symptom:** After `cp build_frontend_staging.py build_frontend.py`, the governor compiles to `index_staging.html` instead of `index.html`. Production visitors see stale content.

**Root cause:** `build_frontend_staging.py` hardcodes the output path as `public/index_staging.html`. After promotion, this path must be changed to `public/index.html`.

**Post-promotion checklist:**
1. `cp build_frontend_staging.py build_frontend.py`
2. `sed -i 's/index_staging.html/index.html/g' build_frontend.py`
3. Restore staging path: `sed -i 's/index.html/index_staging.html/g' build_frontend_staging.py`
4. Run `test_platform.py` → must be 107+ PASS
5. Trigger governor or wait for next timer cycle

## Pitfall 6: Narrative Pill Onclick — Unquoted Variable References

**Symptom:** Clicking a narrative pill calls `setNarrativeFilter(dollar_decline)` — passing an undefined JavaScript variable instead of the string `'dollar_decline'`. The filter function receives `undefined` and fails silently.

**Root cause:** The template generates `onclick="setNarrativeFilter('+n.id+')"` which produces `onclick="setNarrativeFilter(dollar_decline)"` — no quote wrapping.

**Fix:** Template must produce quoted string: `onclick="setNarrativeFilter('dollar_decline')"`
```
onclick="setNarrativeFilter(\''+n.id+'\')"
```

**Detection:** Check the onclick attribute of a narrative pill:
```js
document.querySelector('#sidebar-nav a')?.getAttribute('onclick')
// Must show: setNarrativeFilter('dollar_decline')  ← WITH single quotes
// NOT:        setNarrativeFilter(dollar_decline)    ← variable reference
```

## Pitfall 7: CDN Cache vs GCS Origin Verification

**Symptom:** Changes applied to GCS origin, `gsutil cp` confirmed, but browser still shows old content.

**Root cause:** The GCP Load Balancer CDN caches HTML for up to 3600s. Even with `Cache-Control: no-cache` on the origin, the CDN may serve stale content.

**Verification sequence:**
1. Check GCS origin: `gsutil cp gs://www.lagazzettadikyiv.com/index.html - | grep '<expected-string>'`
2. Check CDN: `curl -s "https://www.lagazzettadikyiv.com/" | grep '<expected-string>'`
3. If origin has fix but CDN doesn't → CDN cache stale. Wait for expiry or force cache-bust with query param.

**Always verify both** — do not assume CDN propagation is instant.
