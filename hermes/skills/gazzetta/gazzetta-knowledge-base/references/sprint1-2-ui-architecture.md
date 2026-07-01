# Sprint 1-2 UI Architecture — June 2026

## Share Visibility (Sprint 1)

**Problem:** Share buttons were hidden inside the collapsed `.story-expanded` div (display:none). Users had to click a story card to expand it before seeing share options.

**Fix:** Moved `.share-row` from inside `.story-expanded` to the card body, immediately after `actionHTML`.

**Template (app.js ~line 1385):**
```
'\\n      ' + actionHTML +
'\\n      <div class="share-row">' +
'\\n        <button class="share-btn copy-link" ...><svg width="20" height="20"...</button>' +
'\\n        <button class="share-btn share-x" ...><svg width="20" height="20"...</button>' +
'\\n        <button class="share-btn share-telegram" ...><svg width="20" height="20"...</button>' +
'\\n      </div>' +
'\\n      <div class="story-expanded" style="display:none">' +   ← share-row is BEFORE this
```

**Verification:** `document.querySelector('.share-row') && !document.querySelector('.share-row').closest('.story-expanded')` → true

## Tap Target Enforcement — Guideline D9 (Sprint 1)

**Rule:** All interactive elements must have minimum 44×44px touch targets.

**CSS (styles.css ~line 1772):**
```css
.share-row {
  display: flex;
  gap: 6px;
  margin: 8px 0 0 0;
  padding: 4px 0 0 0;
  border-top: 1px solid var(--gray-200);
}
.share-btn {
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  /* ... additional flex/color styles ... */
}
```

**Compliance check:** `getComputedStyle(shareBtn).width` → "44px"

## Word-Break on Mobile Headlines (Sprint 1)

**CSS (styles.css ~line 2687):**
```css
.story-headline {
  overflow-wrap: break-word;
  word-break: break-word;
  hyphens: auto;
}
```

**Check:** `getComputedStyle(headline).overflowWrap` → "break-word"

## Hamburger Navigation Drawer (Sprint 2)

### Architecture
- **Template:** `templates/header.html` — hamburger button + drawer HTML appended after `</header>`
- **CSS:** `styles.css` lines 2850+ — nav drawer block (150 lines)
- **JS:** `app.js` `initNavDrawer()` function (50 lines), called from `boot()` after `wireCollapsibleContainers()`
- **Injection:** `build_site.py` injects header template into all 20 HTML pages via sentinel markers

### Desktop (≥601px)
- `.masthead-right` visible (INTEL/ALPHA/MENU links)
- `.nav-hamburger` hidden (`display: none`)
- `.nav-drawer` and `.nav-drawer-backdrop` rendered but off-screen (`translateX(-100%)`)

### Mobile (≤600px)
- `.masthead-right` hidden (`display: none`)
- `.nav-hamburger` visible (`display: flex`) — 3-line hamburger icon, 44×44px, dark red
- Click hamburger → drawer slides in from left, backdrop appears, body scroll locked
- Close via: backdrop click, close button (×), any nav link click, Escape key
- Hamburger animates to X on open (rotate lines 1 and 3, hide line 2)

### Drawer Contents (14 links, 4 sections)
```
INTEL       → Stories, Capital Flows, Home
ALPHA       → The Signal, Trade Ideas, Track Record
RESEARCH    → Event Horizon, Flow Nodes, Geopolitics, Markets
INFO        → About, Methodology, Contact
```

### CSS Key Rules
```css
.nav-drawer {
  position: fixed; top: 0; left: 0;
  width: 280px; max-width: 85vw;
  height: 100dvh;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  z-index: 999;
}
.nav-drawer.open { transform: translateX(0); }
.nav-drawer-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 998; }
.nav-drawer-link { min-height: 44px; display: flex; align-items: center; }
.nav-drawer-close { width: 44px; height: 44px; min-width: 44px; min-height: 44px; }
```

### JS Key Logic
```javascript
function initNavDrawer() {
  // Get elements; return if missing
  // openDrawer(): add 'open' class to hamburger, drawer, backdrop; body.overflow='hidden'
  // closeDrawer(): remove 'open' class; restore body.overflow
  // hamburger click → toggle
  // backdrop click → close
  // close button click → close
  // drawer link clicks → setTimeout(close, 150)
  // Escape key → close
}
```

### Verification
- Desktop: `getComputedStyle(hamburger).display` → "none"
- Open: `hamburgerBtn.click()` → drawer.classList="nav-drawer open", transform="translateX(0)"
- Close: `closeBtn.click()` → drawer.classList="nav-drawer", transform="translateX(-280px)"
- All 20 HTML pages contain `nav-hamburger` class

## Deploy Workflow (Current — June 2026)

### Standard pipeline (crontab every 10 min)
```
deploy_routine.sh → db_to_json.py → build_site.py → test_platform.py → gsutil rsync
```

### Rapid deploy (manual, bypasses edge cache)
```bash
export CLOUDSDK_CONFIG=/Users/alexstocchi/.config/gcloud
GSDIR=/Users/alexstocchi/lagazzettadikyiv/devvit/google-cloud-sdk/bin

# 1. Hash assets
AH=$(shasum -a 256 public/app.js | cut -c1-8)
CH=$(shasum -a 256 public/styles.css | cut -c1-8)

# 2. Upload hashed (immutable cache)
$GSDIR/gsutil -h "Cache-Control:public, max-age=31536000, immutable" cp public/app.js gs://BUCKET/app.$AH.js
$GSDIR/gsutil -h "Cache-Control:public, max-age=31536000, immutable" cp public/styles.css gs://BUCKET/styles.$CH.css

# 3. Update HTML refs
cd public && for f in *.html; do sed -i '' "s/app\.js/app.$AH.js/g; s/styles\.css/styles.$CH.css/g" "$f"; done

# 4. Upload HTML (no-cache)
for f in *.html; do $GSDIR/gsutil -h "Cache-Control:no-store, max-age=0" cp "$f" gs://BUCKET/"$f"; done
```

## Version Tags

| Tag | Contents |
|-----|----------|
| v28-pre-initiatives | Baseline before Initiatives 1-3 |
| v29-sprint1-share-tap | Share visibility, 44px tap targets, word-break |
| v30-sprint2-navigation | Hamburger drawer across all pages |
