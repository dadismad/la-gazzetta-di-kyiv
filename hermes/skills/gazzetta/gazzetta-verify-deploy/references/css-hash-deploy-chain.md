# CSS Hash → Full Deploy Chain (v26.6)

## Why This Matters

The browser does NOT load `styles.css` — it loads the HASHED file (`styles.HASH.css`) referenced in each HTML page. If you update `styles.css` but forget to update the hash reference in even ONE sub-page, that page loads old CSS. The user sees a broken site and loses trust.

This happened multiple times in June 2026. The user screamed "are you fucking retarded" and nearly abandoned the project.

## The Full Chain (do not skip any step)

```bash
cd ~/projects/gazzetta-di-kyiv/site

# 1. Edit styles.css (make your changes)

# 2. Generate new hash
HASH=$(shasum -a 256 styles.css | cut -c1-8)

# 3. Copy to hashed file
cp styles.css "styles.${HASH}.css"

# 4. Update reference in ALL 20 HTML files
sed -i '' "s/styles\.[a-f0-9]*\.css/styles.${HASH}.css/g" *.html

# 5. Verify all 20 files updated (must return exactly ONE hash)
grep -oh 'styles\.[a-f0-9]*\.css' *.html | sort -u
# Must output: styles.NEWHASH.css  (one line ONLY)

# 6. Deploy ALL HTML + CSS to GCS
GSDK=~/lagazzettadikyiv/google-cloud-sdk/bin
$GSDK/gsutil -m -h "Cache-Control:no-cache, max-age=0" \
  cp *.html styles.css "styles.${HASH}.css" \
  gs://www.lagazzettadikyiv.com/

# 7. Delete OLD hashed CSS from GCS (NOT before step 8!)
OLD_HASH="previous"  # the hash you replaced
# DO NOT delete yet — verify first

# 8. Verify ALL pages load new CSS
for f in index.html stories.html flows.html signal.html trades.html \
         track.html about.html event_horizon.html flow-nodes.html; do
  echo -n "$f: "
  curl -s "https://www.lagazzettadikyiv.com/$f?t=$(date +%s)" \
    | grep -o 'styles\.[a-f0-9]*\.css'
done
# Must return the SAME new hash for every page

# 9. Only NOW delete old CSS from GCS + local
$GSDK/gsutil rm gs://www.lagazzettadikyiv.com/styles.${OLD_HASH}.css
rm styles.${OLD_HASH}.css
```

## Verification Checklist

- [ ] `grep -oh 'styles\.[a-f0-9]*\.css' *.html | sort -u` returns ONE hash
- [ ] All 20 pages deployed to GCS
- [ ] `curl` every page → all return the same new hash
- [ ] Old hash deleted from GCS only AFTER verification
- [ ] `browser_console` → `getComputedStyle(document.querySelector('.masthead')).borderBottom` shows gold, not black

## The 20 HTML Files

index.html, stories.html, flows.html, signal.html, trades.html, track.html,
event_horizon.html, flow-nodes.html, about.html, privacy.html, methodology.html,
story.html, capital.html, data.html, geopolitics.html, markets.html, pleasure.html,
sources.html, terms.html, wealth.html

## Common Failure Modes

1. **sed only matches the old hash, but some files had a different old hash** → use `[a-f0-9]*` wildcard, not a specific hash
2. **Delete old CSS before verifying all pages** → cached HTML still references deleted file → pages have ZERO CSS → user sees garbage
3. **Forget sub-pages** → only index.html gets new hash → user navigates and sees broken layout
4. **GCS edge cache** → even after correct deploy, `curl` may return old hash for up to 1 hour. Use `cache-control: no-cache` header.
