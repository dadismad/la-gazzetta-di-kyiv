# Dual-Bucket Disconnect — Full Reproduction (v27.2 June 2026)

## Symptoms
- All pages return 200 OK from CDN
- `gsutil cat gs://lagazzettadikyiv.com/story.html` shows correct hashed scripts + story-app.js
- `curl https://lagazzettadikyiv.com/story.html` shows OLD cache-buster scripts, NO story-app.js
- Browser loads old app.js with `?t=...` cache busters instead of hashed filenames
- Hero stats show real data on homepage but story page stuck on "Loading intelligence report..."
- Fixes deployed and verified via gsutil never appear on live site

## Root Cause

```
Pipeline deploys → gs://lagazzettadikyiv.com/
LB backend bucket → gs://www.lagazzettadikyiv.com/  (WRONG)
```

Two independent GCS buckets. Pipeline writes to one, LB serves from the other. The buckets were 4 days out of sync (June 12 vs June 16).

## Detection Commands

```bash
# 1. Check which bucket the LB serves
gcloud compute backend-buckets describe gazzetta-backend --format='value(gcsBucketName)'

# 2. Compare file timestamps between buckets
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
echo "=== lagazzettadikyiv.com ===" 
$GSDK/gsutil ls -l gs://lagazzettadikyiv.com/story.html | grep -o '2026-0[0-9]-[0-9]*'
echo "=== www.lagazzettadikyiv.com ==="
$GSDK/gsutil ls -l gs://www.lagazzettadikyiv.com/story.html | grep -o '2026-0[0-9]-[0-9]*'

# 3. Compare script references (quick binary test)
$GSDK/gsutil cat gs://lagazzettadikyiv.com/story.html | grep -o 'script src="[^"]*"'
curl -s https://lagazzettadikyiv.com/story.html | grep -o 'script src="[^"]*"'
# If these differ → dual-bucket disconnect confirmed
```

## Fix

Option A (fastest): Switch LB backend bucket
```bash
gcloud compute backend-buckets update gazzetta-backend --gcs-bucket-name=lagazzettadikyiv.com
```

Option B: Sync both buckets
```bash
GSDK=~/lagazzettadikyiv/devvit/google-cloud-sdk/bin
$GSDK/gsutil -m rsync -r gs://lagazzettadikyiv.com/ gs://www.lagazzettadikyiv.com/
```

## SSL Certificate Check

Before switching backend buckets, verify the SSL cert covers the target domain:
```bash
gcloud compute ssl-certificates list
# gazzetta-ssl-cert-v2 covers BOTH lagazzettadikyiv.com AND www.lagazzettadikyiv.com
```

## Why This Happens Silently

- `gsutil` reads directly from the bucket — always shows correct content
- CDN curl may show updated content if CDN invalidation occurred
- Browser snapshots show header/footer (static HTML) which loads fine
- Only JS-populated content reveals the mismatch (different app.js versions)
- `browser_console` fetch to `/data/stories.json` may return 200 (data files exist in both buckets)

## Key Lesson

AFTER EVERY DEPLOY: verify the LB backend bucket matches the deployment target bucket. This is a one-command check that would have caught 4 days of stale deploys.
