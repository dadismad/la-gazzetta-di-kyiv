# Hashed-Asset Auth-Failure → CSS 404 Cascade

**Date:** June 2026
**Commit fix:** `cbcb544`

## Pattern

When `build_hashed_assets.py` runs successfully (creates hashed CSS file locally + rewrites all 20 HTML references) but the hashed CSS file **never reaches GCS** (gsutil auth failure), the result is a silent CSS 404 that survives curl-based verification:

```
Local: styles.css → styles.d0b7cbda.css  (created ✓)
HTML:  href="./styles.d0b7cbda.css"     (written ✓)
GCS:   styles.d0b7cbda.css               (MISSING — auth 401)
```

## Cascade of Symptoms

Without CSS, these specific failures appear:

| Symptom | Detection | Normal |
|---------|-----------|--------|
| SVG explosion (caduceus: 1264×2528px) | `svg.getBoundingClientRect()` | 12×22px |
| SVG explosion (bulava: 1264×3430px) | `svg.getBoundingClientRect()` | 21.8×25px |
| Masthead gold border missing | `getComputedStyle(.masthead).borderBottom` | `2px solid rgb(212, 175, 55)` |
| Font fallback to Times | `getComputedStyle(body).fontFamily` | `"Source Serif 4", Georgia, serif` |
| Masthead badge/caduceus invisible | `currentColor` renders transparent | gold via CSS |

## Detection (works even when browser_vision is unavailable)

```js
// Quick CSS health check via browser_console
JSON.stringify({
  fonts: getComputedStyle(document.body).fontFamily,
  mastheadBorder: getComputedStyle(document.querySelector('.masthead')).borderBottom,
  caduceus: (()=>{var s=document.querySelector('.masthead-caduceus svg'); var b=s.getBoundingClientRect(); return {w:b.w, h:b.h};})(),
  cssLoaded: !!document.querySelector('link[href*="styles.css"]:not([href*="fonts"])')
})
// FAIL if: fonts="Times", mastheadBorder="0px none", caduceus.w > 100
```

## Fix Path

1. **Immediate:** Revert CSS references from hashed → unhashed (`sed -i '' 's|styles\.[a-f0-9]*\.css|styles.css|g' *.html`)
2. **Verify auth:** `gsutil ls gs://BUCKET/styles.css` — must succeed (read test). Then try `gsutil cp` — must succeed (write test)
3. **Use correct gsutil:** `~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil` (NOT the Hermes venv gsutil)
4. **Deploy:** `gsutil -m rsync -r -d public/ gs://BUCKET/`
5. **Verify:** Rerun JS health check above

## Prevention

- After every CSS hash rotation: `gsutil stat gs://BUCKET/styles.NEWHASH.css` → must return 200
- Shipit.sh GCLOUD_DIR must point to the **devvit** google-cloud-sdk (has write auth)
- Never deploy hashed HTML without confirming the hashed asset file exists on GCS
