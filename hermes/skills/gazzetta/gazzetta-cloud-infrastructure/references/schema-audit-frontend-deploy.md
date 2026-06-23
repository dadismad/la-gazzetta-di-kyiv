# Schema Audit Before Frontend Deployment

When deploying a frontend feature that reads a specific data field from stories.json (e.g., `feed_source` for attribution footers), the field may not exist in the pipeline output. Deploying without verification causes silent feature omission — the code runs, the feature renders nothing, and the deployment appears successful but is a false positive.

## Three-Branch Audit Pattern

Before deploying any frontend feature that depends on a data field:

**Step 1: Read the pipeline producer**

Find the script that writes the relevant field to the story dict. For stories.json, this is `assemble_story()` in `contradiction_synthesizer.py`. Read the dict-building code to see ALL fields being set.

**Step 2: Read the live data**

Check a few story objects in `data/stories.json` for the field name and value.

**Step 3: Branch on findings**

```
Field present with correct name?
  YES → Branch 1: Deploy. Template references match data.
  NO, but similar field exists (e.g., source_name vs feed_source)?
    → Branch 2: Rename in template to match the data key.
  NO, field absent entirely?
    → Branch 3: Add passthrough in the upstream producer, 
      regenerate data, then deploy.
```

### Branch 3: Upstream Passthrough (Example)

The synthesizer receives `source_url` from the DB but doesn't populate `feed_source`. Fix: add domain extraction in `assemble_story()` that derives a clean publication name from the URL, then add the field to the output dict. Regenerate stories.json (migrate existing + new stories will get it automatically).

```python
from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    if not url:
        return ""
    netloc = urlparse(url).netloc
    domain = netloc.replace("www.", "").split(":")[0].lower()
    mapping = {"ecb.europa.eu": "ECB", "oilprice.com": "OilPrice.com"}
    return mapping.get(domain, domain.upper())

# In assemble_story():
"feed_source": extract_domain(source_url),
```

### Migration for Existing Data

After adding the field to the producer, existing stories in stories.json still lack it. Run a one-shot migration script that iterates all stories and backfills the field. This ensures immediate feature visibility on the next build.

## Promotion Workflow

When promoting staging features to production:

1. Copy staging build script → production build script
2. Fix output path (staging = `index_staging.html`, production = `index.html`)
3. Rebuild production locally
4. Verify all feature markers in the output (grep for key strings)
5. Run `test_platform.py`
6. SCP updated scripts to VM: `gcloud compute scp file gazzetta-prod:~` then `sudo mv` + `chown`
7. Rebuild on VM
8. `gsutil cp` to GCS
9. Verify on live domain via `curl` for key markers

## PITFALL: File Truncation via read_file/write_file

`read_file()` with pagination returns formatted output with line numbers (e.g., `1|content`). If this formatted output is written back with `write_file()`, the file becomes corrupted with embedded line numbers. Recovery: copy from a sibling file (e.g., production build script) and re-apply patches.
