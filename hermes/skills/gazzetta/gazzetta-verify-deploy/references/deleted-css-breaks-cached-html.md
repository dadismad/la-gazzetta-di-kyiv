# Deleted CSS Hashes Break Cached HTML (v26.6)

## The Chain

1. Agent edits `styles.css`, generates new hash (`styles.NEW.css`), updates all 20 HTML files, deploys everything to GCS.
2. Agent cleans up: `gsutil rm gs://BUCKET/styles.OLD.css` (the previous hash).
3. GCS edge cache still serves **old HTML** referencing `styles.OLD.css` for up to 1 hour (`cache-control: max-age=3600`).
4. User opens the site → old HTML loads → tries to fetch `styles.OLD.css` → **404** → page has zero CSS.
5. Page renders unstyled: browser-default black borders, no gold accents, broken layout. User sees garbage.

## Why It Happens

- `gsutil setmeta` changes object metadata but does NOT invalidate the edge cache.
- `gsutil cp` with new `Cache-Control` headers updates the object, but the edge cache may have already cached the old bytes.
- The `age:` response header tells you how many seconds the edge cache has held the current bytes. When `age > 0`, you're seeing cached content.

## Detection

```bash
# Step A: Verify ALL pages reference the same NEW hash
for f in index.html stories.html flows.html signal.html trades.html track.html about.html \
         privacy.html methodology.html event_horizon.html flow-nodes.html; do
  HASH=$(curl -s "https://www.lagazzettadikyiv.com/$f?t=$(date +%s)" | grep -o 'styles\.[a-f0-9]*\.css' | head -1)
  echo "$f → $HASH"
done
# ALL must return the same new hash. If ANY returns the old hash, the edge cache is stale.
```

```bash
# Step B: Verify GCS itself has the correct HTML
GSDK=~/lagazzettadikyiv/google-cloud-sdk/bin
for f in index.html stories.html flows.html signal.html; do
  HASH=$($GSDK/gsutil cat "gs://www.lagazzettadikyiv.com/$f" | grep -o 'styles\.[a-f0-9]*\.css' | head -1)
  echo "GCS $f → $HASH"
done
```

## Fix

1. **NEVER delete old CSS/JS hashes until Step A passes for ALL pages.**
2. If old hash already deleted → redeploy ALL HTML files with new cache headers:
   ```bash
   GSDK=~/lagazzettadikyiv/google-cloud-sdk/bin
   $GSDK/gsutil -m -h "Cache-Control:no-cache, max-age=0" cp site/*.html gs://www.lagazzettadikyiv.com/
   ```
3. Re-verify Step A — all pages must return the new hash.
4. Only then delete old hashes from GCS.

## Prevention

After every CSS hash rotation:
1. Deploy new CSS + all HTML
2. Run `gsutil setmeta -h "Cache-Control:no-cache, max-age=0"` on all HTML+CSS objects
3. Wait 60 seconds
4. Run Step A verification
5. Only then delete old hashes

## Real-World Impact

June 12, 2026: Agent deployed `styles.03311fab.css`, updated all HTML locally, deployed to GCS, then deleted `styles.96c672e4.css` and `styles.b3d2ae91.css` from GCS. The edge cache served old HTML referencing deleted CSS files. User saw black borders instead of gold, broken layout, and screamed "Are you fucking retarded? Delete this bullshit, it never works." The fix was redeploying all 21 HTML files and waiting for edge cache to refresh.
