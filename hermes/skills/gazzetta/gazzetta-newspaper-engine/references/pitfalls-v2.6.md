# Pitfalls — v2.6.0 (June 22, 2026)

## Fatal: read_file → write_file Corruption

**Problem:** The `read_file` tool (from `hermes_tools`) returns content with line-number prefixes:
```
     1|#!/usr/bin/env python3
     2|"""docstring"""
```

Writing this content back with `write_file` embeds those prefixes into the file, corrupting it. Python sees `     1|#!/usr/bin/env python3` on line 1 and throws `IndentationError: unexpected indent`. The entire file becomes unparsable.

**This happened to `build_frontend.py` on June 22, 2026.** The Phase C code (all 8 visual features) was lost when `git checkout` had to revert to v3.1. Recovery required a full 3-phase rebuild (~110 lines, ~2 hours).

**Prevention:**
- **Never** use `read_file()` + `write_file()` in the same execute_code.
- **Safe pattern:** Use Python's built-in `open().read()` inside execute_code:
  ```python
  with open("/path/to/file.py", "r") as f:
      content = f.read()
  # ... modify content ...
  with open("/path/to/file.py", "w") as f:
      f.write(content)
  ```
- The `patch` tool is also safe — it reads the file directly.
- **Before any risky edit:** `cp file.py file.py.bak`.

## CDN Cache-Control Override

**Problem:** Google Cloud CDN ignores origin `Cache-Control` headers when the load balancer has a default TTL configured. Setting `max-age=60` on GCS objects had no effect — CDN served stale content for hours.

**Mitigation:**
- Governor deploy step uses: `Cache-Control: no-cache,no-store,must-revalidate,max-age=0`
- This is the most aggressive cache-busting available at the object level
- CDN may still override — the VM service account lacks `compute.urlMaps.invalidateCache` permission
- If CDN stays stale: someone with project owner permissions must run `gcloud compute url-maps invalidate-cdn-cache gazzetta-url-map --path='/*'`

## Session Search Gaps for Telegram Sessions

**Problem:** `session_search` only indexes CLI sessions. Telegram gateway sessions are NOT persisted to the session DB. When you need to recover previous work done in a Telegram session, session search returns nothing. This was discovered June 22 when trying to recover Phase C patches after file corruption.

**What works:** The conversation compaction summary at the top of each context window contains the session's full history. Use that as the source of truth for recovery.

## Patch Tool Escape Sequences

**Problem:** The `patch` tool fails on JS-in-Python strings with nested quotes. The build_frontend.py file has heavily escaped JavaScript template literals (e.g., `\\\\'` for `\'`). The patch tool's fuzzy matching can't always find the right string.

**Workaround hierarchy:**
1. **First choice:** `patch` with short unique substrings (no quotes) — e.g., `substring(0,12)` → `substring(0,14)`
2. **Second choice:** `patch` with `replace_all=True` for identical occurrences
3. **Third choice:** Use Python `open().read()` in execute_code for complex multi-line replacements
4. **Last resort:** `git checkout` the file and re-apply from scratch

## SSH Config for Gazzetta VM

The VM uses the SSH config alias `gazzetta-prod`:
```
Host gazzetta-prod
    HostName 35.232.28.188
    User alexstocchi
    IdentityFile ~/.ssh/google_compute_engine
```

**Important:** Files on the VM are owned by `gazzetta` user, not `alexstocchi`. Always deploy via:
```bash
scp file.py gazzetta-prod:/tmp/file.py
ssh gazzetta-prod "sudo cp /tmp/file.py /opt/gazzetta-di-kyiv/scripts/file.py && sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/scripts/file.py"
```

Direct `scp` to `/opt/gazzetta-di-kyiv/` fails with "Permission denied" — the alexstocchi user can't write there.
