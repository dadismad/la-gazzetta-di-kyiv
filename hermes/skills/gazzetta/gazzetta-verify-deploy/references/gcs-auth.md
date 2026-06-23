# GCS Deploy Authentication

## Working Configuration

- **SDK path:** `~/lagazzettadikyiv/google-cloud-sdk/bin/`
- **gsutil:** `~/lagazzettadikyiv/google-cloud-sdk/bin/gsutil`
- **gcloud:** `~/lagazzettadikyiv/google-cloud-sdk/bin/gcloud`
- **Account:** `pureciclismo@gmail.com`
- **Project:** `project-e5e0244c-b94d-41a1-810`

## Known Issues

### Hermes venv gsutil returns 401
The gsutil in `~/.hermes/hermes-agent/venv/bin/gsutil` has no boto config and no gcloud credentials bridge. It can read public buckets but cannot write. Always use the lagazzettadikyiv SDK path for deploys.

### Root bucket is read-only
`gs://lagazzettadikyiv.com` accepts reads/list but not writes — returns 401 on `gsutil cp` or `gsutil setmeta`. The `www` bucket (`gs://www.lagazzettadikyiv.com`) accepts full read/write. Both buckets serve the same content via GCS Load Balancer, so deploying to www covers both domains.

### Cache-Control headers
Set `Cache-Control: public, max-age=0, must-revalidate` on all .html and .json files to prevent CDN staleness:
```bash
GSDK=~/lagazzettadikyiv/google-cloud-sdk/bin
$GSDK/gsutil -h "Cache-Control:public,max-age=0,must-revalidate" cp site/index.html gs://www.lagazzettadikyiv.com/index.html
```

For bulk sync, apply cache headers post-sync:
```bash
$GSDK/gsutil -m setmeta -h "Cache-Control:public,max-age=0,must-revalidate" \
  gs://www.lagazzettadikyiv.com/index.html \
  gs://www.lagazzettadikyiv.com/data/stories.json \
  gs://www.lagazzettadikyiv.com/data/flows.json
```

### Multiprocessing on macOS
The `-m` flag (parallel operations) triggers macOS multiprocessing bugs (Python issue 33725). If gsutil hangs, add `-o "GSUtil:parallel_process_count=1"`:
```bash
$GSDK/gsutil -o "GSUtil:parallel_process_count=1" -m rsync -d -r site/ gs://www.lagazzettadikyiv.com/
```

## Authentication Recovery

If credentials expire:
```bash
~/lagazzettadikyiv/google-cloud-sdk/bin/gcloud auth login
```
This opens a browser for OAuth. Use `pureciclismo@gmail.com`.

For service account key auth (headless):
```bash
~/lagazzettadikyiv/google-cloud-sdk/bin/gcloud auth activate-service-account --key-file=/path/to/key.json
```
