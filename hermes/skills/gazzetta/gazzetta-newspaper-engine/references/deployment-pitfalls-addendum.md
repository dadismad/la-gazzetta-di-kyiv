# Additional Deployment Pitfalls — June 22, 2026 Session

## PITFALL 12: execute_code file corruption via read_file/write_file

**Symptom**: After using `execute_code` to read and modify `build_frontend.py`, `py_compile` reports `IndentationError: unexpected indent` on line 1. The file shows garbled content starting with `     1|`.

**Root cause**: `read_file()` from `hermes_tools` returns content with line-number prefixes (`     1|#!/usr/bin...`). Passing this content to `write_file()` writes the prefixes into the file as literal characters. The file is destroyed.

**Fix**: 
- Use `patch()` for targeted edits (preferred — auto-validates syntax)
- If programmatic string replacement is needed inside `execute_code`, use Python's built-in `open("file.py").read()` — NOT `hermes_tools.read_file()`
- Always verify after writing: `python3 -c 'import py_compile; py_compile.compile("file.py", doraise=True)'`
- If corrupted: `git checkout scripts/build_frontend.py` to restore, then re-apply patches

**Recovery**: Git checkout restores the last committed version (v3.1 in June 2026). All uncommitted Phase C visual features are lost and must be re-implemented. Commit frequently.

## PITFALL 13: CDN ignores origin Cache-Control — stale site despite correct GCS object

**Symptom**: `gsutil cat gs://www.lagazzettadikyiv.com/index.html | grep -c 'glass-panel'` returns 4 (correct), but `curl https://www.lagazzettadikyiv.com/ | grep -c 'glass-panel'` returns 0 (stale).

**Root cause**: Google Cloud CDN (gazzetta-url-map -> gazzetta-backend) overrides origin `Cache-Control` headers. Setting `max-age=0` or `no-cache` on the GCS object has NO effect on the CDN edge.

**Fix**: CDN invalidation requires `compute.urlMaps.invalidateCache` permission, which the VM service account lacks. Workaround: wait for CDN's own TTL to expire, or ask someone with Owner/IAM permissions to run the invalidation manually.

**Verification**: Always confirm GCS directly (`gsutil cat`) before trusting the live domain.

## PITFALL 14: SSH IP mismatch between memory and reality

**Symptom**: `ssh gazzetta@35.188.110.255` times out. Memory says one IP, reality says another.

**Root cause**: VM IPs cycle on GCP. The IP in memory (35.188.110.255) was stale. The SSH config file at `~/.ssh/config` has the correct alias `gazzetta-prod` pointing to `35.232.28.188`.

**Fix**: Always use the SSH alias (`ssh gazzetta-prod`), never hardcoded IPs. To verify: `grep -A3 gazzetta ~/.ssh/config`.
