# GCS Delete-Before-Reupload Pattern

## The Problem

`gsutil cp` with `Cache-Control:no-store` appears to succeed (reports correct byte count) but the live site continues serving the OLD file. This happens even with CDN disabled on the backend bucket — the GCS load balancer has an internal cache layer that `gsutil cp` alone doesn't invalidate.

## Detection

```bash
# Check what GCS actually stores (direct bucket access)
$GSDK/gsutil cat gs://www.lagazzettadikyiv.com/styles.css | grep 'EXPECTED_STRING'

# Check what the live site serves
curl -s 'https://www.lagazzettadikyiv.com/styles.css' | grep 'EXPECTED_STRING'

# Also compare byte counts
$GSDK/gsutil ls -l gs://www.lagazzettadikyiv.com/styles.css
curl -s 'https://www.lagazzettadikyiv.com/styles.css' | wc -c
```

If GCS has the new bytes but curl gets old bytes → LB cache is stale.

## Fix: Delete Then Upload

```bash
GSDK=~/lagazzettadikyiv/google-cloud-sdk/bin
$GSDK/gsutil rm gs://www.lagazzettadikyiv.com/styles.css
sleep 1  # let the delete propagate
$GSDK/gsutil -h "Cache-Control:no-store" cp styles.css gs://www.lagazzettadikyiv.com/styles.css
```

The delete breaks the LB's cache association. The re-upload creates a fresh object with no cached state.

## Session Incidents

- **June 11, 2026**: `styles.css` — `gsutil cp` with `Cache-Control:no-store` reported 55,673 bytes uploaded but curl returned 54,000 bytes with old content (`var(--φ-lg)` instead of `3em`). `gsutil cat` confirmed the new bytes were in GCS. Delete + re-upload fixed it immediately. Root cause: LB cache (CDN was disabled on backend bucket, but the load balancer itself cached the object metadata/bytes).
