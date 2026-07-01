# Frontend Hardening — June 11, 2026

Patterns and fixes applied during the post-audit frontend hardening pass. All changes deployed to production.

## 1. RU Nav i18n — Hardcoded Group Labels

**Problem:** The product nav's INTEL/ALPHA group labels were hardcoded HTML:
```html
<span class="nav-group-label">INTEL</span>
<span class="nav-group-label">ALPHA</span>
```

They lacked `data-i18n` attributes, so the Russian page always showed English labels.

**Fix:**
```html
<span class="nav-group-label" data-i18n="nav_intel">INTEL</span>
<span class="nav-group-label" data-i18n="nav_alpha">ALPHA</span>
```

**i18n_ru.json additions:**
```json
"nav_intel": "ИНТЕЛ",
"nav_alpha": "АЛЬФА",
"layer_intel": "ИНТЕЛ",
"layer_alpha": "АЛЬФА"
```

**Rule:** ALL text content in the masthead/nav that has an i18n_ru.json key MUST use `data-i18n` attributes. Audit with: `grep -n '<span class="nav-group-label">' index.html` — any span without `data-i18n` is a hardcoded label bug.

## 2. onclick → data-action Delegation

**Problem:** 5 inline `onclick` handlers remained in the HTML despite `app.js` having a global data-action delegation system (lines 24-59). The handlers were:
- 2× `onclick="i18n.switchLang('en')"` / `onclick="i18n.switchLang('ru')"`
- 3× `onclick="location.href='./flows.html'"`

**Fix:** Replace with `data-action` attributes:
```html
<button data-action="lang-en" data-lang="en">EN</button>
<button data-action="lang-ru" data-lang="ru">RU</button>
<div data-action="navigate" data-href="./flows.html">
```

**Added `navigate` case to app.js delegation:**
```javascript
case 'navigate':
  if (btn.hasAttribute('data-href')) {
    window.location.href = btn.getAttribute('data-href');
  }
  break;
```

**Rule:** Zero `onclick` in HTML. All interactions through the global delegation switch in `app.js` line 27. Audit with: `grep -c 'onclick' index.html` → must be 0.

## 3. Duplicate DOM IDs — Freshness Panels

**Problem:** The sidebar had two freshness panels using the same IDs:
- `id="sideFreshness"` (lines 364, 390)
- `id="freshStories"` (lines 365, 391)
- `id="freshFlows"` (lines 366, 392)

`document.getElementById()` returns only the first match — the second panel was permanently unreachable.

**Fix:** Rename second panel IDs with a dashboard prefix:
```html
<div id="sideDashboard">       <!-- was sideFreshness -->
<span id="dbStories">—</span>   <!-- was freshStories -->
<span id="dbFlows">—</span>     <!-- was freshFlows -->
<span id="dbTrades">—</span>    <!-- was freshTrades -->
<span id="dbSignal">—</span>    <!-- was freshSignal -->
```

**Note:** These IDs aren't referenced in app.js — they're CSS-targeted via classes. The `byId()` function (line 64) already has a fallback for `.product-page` scoped queries. So duplicates were cosmetic but prevented future JS usage.

**Rule:** After adding new ID-bearing elements, run: `grep -on 'id="[^"]*"' index.html | sort | uniq -d` — any output = duplicate bug.

## 4. Retry Logic in getJSON

**Before:** Single attempt, no retry. Any transient CDN/network error caused silent failure.

**After:** 2 retries with exponential backoff (1s, 2s, 4s — capped at 8s):
```javascript
async function getJSON(path, fallback, retries = 2) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const r = await fetch(`${path}?t=${Date.now()}`, {
        cache: 'no-store', signal: _fetchAC.signal
      });
      if (!r.ok) throw new Error(String(r.status));
      return await r.json();
    } catch (e) {
      if (e.name === 'AbortError') { /* stale fetch — intentional */ return fallback; }
      if (attempt < retries) {
        const delay = Math.min(1000 * Math.pow(2, attempt), 8000);
        console.warn(`retry ${attempt + 1}/${retries} for ${path} in ${delay}ms`);
        await new Promise(r => setTimeout(r, delay));
      } else {
        console.error('fetch failed after retries:', path, e);
        return fallback;
      }
    }
  }
  return fallback;
}
```

**Impact:** The 3 data endpoints (`market_prices.json`, `market_regime.json`, `track_record.json`) fetched by `app.js` now survive transient CDN blips.

## 5. -webkit- CSS Vendor Prefixes

**Problem:** 0 -webkit- prefixes on 65 `display:flex` / `display:grid` declarations. Safari <9, iOS <9.3, and older Android browsers require these.

**Fix:** Python script added `display: -webkit-box; display: -webkit-flex;` before every unprefixed `display: flex` (and `-ms-grid` before `display: grid`). Result: 57 prefix pairs added to `styles.css` (8 already had prefixes).

**Bulk-add pattern (for future CSS passes):**
```python
import re
for line in css.split('\n'):
    if re.search(r'display\s*:\s*flex\b', stripped) and '-webkit-' not in stripped:
        output.append(f'{indent}display: -webkit-box;')
        output.append(f'{indent}display: -webkit-flex;')
```

**Rule:** Every `display:flex` and `display:grid` in styles.css must have -webkit- prefix on the preceding line. Audit with: `grep -c 'display:\s*flex' styles.css` minus `grep -c '\-webkit-flex' styles.css` — gap must be 0.

## 6. Nav Dropdowns — Missing JavaScript Toggle + Invalid HTML

**Problem:** The INTEL/ALPHA dropdown buttons had zero JavaScript. CSS defines `.nav-dropdown.open .nav-dropdown-panel { display: block; }` and `.nav-dropdown.open .nav-dd-arrow { transform: rotate(180deg); }` — but nothing in `app.js` toggled the `.open` class. Compounding: the masthead template (`templates/header.html`) had `<a href="./stories.html">INTEL</a>` nested inside `<button class="nav-dropdown-trigger">` — structurally invalid HTML where the `<a>` click always wins and navigates away.

**Fix — `wireNavDropdowns()` in `app.js`:**
```javascript
function wireNavDropdowns() {
  document.querySelectorAll('.nav-dropdown-trigger').forEach(trigger => {
    trigger.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const dropdown = this.closest('.nav-dropdown');
      if (!dropdown) return;
      document.querySelectorAll('.nav-dropdown.open').forEach(dd => {
        if (dd !== dropdown) dd.classList.remove('open');
      });
      dropdown.classList.toggle('open');
    });
  });
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.nav-dropdown')) {
      document.querySelectorAll('.nav-dropdown.open').forEach(dd => dd.classList.remove('open'));
    }
  });
}
```
Called from `boot()` after `wireCollapsibleContainers()`.

**Fix — Template (`templates/header.html`):** Replace `<a href="...">INTEL</a>` with `<span>INTEL</span>` inside the `<button>`. Same for ALPHA. Then run `build_site.py` to inject into all 21 HTML pages.

**Rule:** After any template edit (`templates/header.html` or `templates/footer.html`), run `python3 scripts/build_site.py` then the full hash→manifest→HTML-ref→deploy chain. Audit with: `grep -n '<a href' templates/header.html` — no `<a>` should appear inside a `<button>`.

## 7. HTML Entity Decoding for JS-Populated innerHTML

**Problem:** Story data contains HTML entities (`&nbsp;`, `&#039;`, `&amp;`) in `thesis` and `they_say` fields. When inserted into DOM via `innerHTML`, some are rendered but others (especially `&nbsp;`) appear as raw text. The `populateTeasers()` function was setting summary text directly from the raw data without decoding.

**Fix — `decodeHTMLEntities()` in `app.js`:**
```javascript
function decodeHTMLEntities(text) {
  if (!text) return '';
  const txt = document.createElement('textarea');
  txt.innerHTML = text;
  return txt.value;
}
```
Applied in `populateTeasers()`: `const summary = decodeHTMLEntities((s.thesis || s.they_say || '')...)`

**Rule:** Any story text that goes into `innerHTML` and originates from JSON data files (stories.json, flows.json) should pass through `decodeHTMLEntities()`. Headlines rendered in `<a>` tags decode natively by the browser, but text set via JS string interpolation needs explicit decoding.

## 8. Browser Console DOM Verification (vs Snapshot Blindness)

**Pattern:** Browser snapshots capture the accessibility tree at a point in time — they may miss JS-populated content that loads asynchronously. For verifying collapsed/expanded state, content population, or computed styles, use `browser_console` with JS expressions:

```javascript
// Check if element expanded
JSON.stringify({flowsExpanded: document.getElementById('flowsTeaser')?.classList.contains('expanded')})

// Check if content populated
document.getElementById('flowsTeaserContent')?.innerHTML?.slice(0, 200)

// Check computed style
getComputedStyle(document.querySelector('#flowsTeaser .container-body')).display

// Force-click header (bypasses browser_click ref targeting issues)
document.querySelector('#flowsTeaser .container-header').click()
```

**Pitfall:** **Pitfall:** `browser_click` with element refs can target the wrong DOM node (wrapping generic elements vs the actual clickable header). When a click doesn't produce expected results, fall back to `browser_console` with `.click()` on the specific selector.

## Deployment After These Changes

After editing source files:
```bash
cd ~/lagazzettadikyiv && python3 scripts/build_site.py
# Hash JS: cd public && shasum -a 256 app.js | cut -c1-8
# Copy + update manifest + sed all HTML refs
gsutil -m -h "Cache-Control:no-store, max-age=0" rsync public/ gs://www.lagazzettadikyiv.com/
```

Verify:
```bash
curl -sI https://www.lagazzettadikyiv.com/  # → 200
grep -rn 'app\.[a-f0-9]\{8\}\.js' public/*.html  # → all must point to latest hash
```
