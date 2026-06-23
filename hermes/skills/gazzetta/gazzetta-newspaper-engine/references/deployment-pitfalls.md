# Gazzetta Deployment Pitfalls & Workarounds
## June 22, 2026

### PITFALL 1: Deploy silently fails — NoNewPrivileges blocks sudo
**Symptom**: Governor shows `[deploy] FAIL(1) in 0.0s`. Site never updates. `gsutil` and `gcloud` commands work as root but fail under systemd.
**Root cause**: `NoNewPrivileges=yes` in `/etc/systemd/system/gazzetta-governor.service` blocks `sudo` entirely.
**Fix**: Change to `NoNewPrivileges=no`, run `sudo systemctl daemon-reload`. Verify with `sudo gsutil ls gs://www.lagazzettadikyiv.com/index.html`.
**Note**: The deploy step in `governor.py` uses `sudo` because gcloud credentials are only configured for root (service account). Alternative fix: configure gcloud auth for the `gazzetta` user directly.

### PITFALL 2: Dark mode not applying — Tailwind overrides CSS
**Symptom**: Body background is `rgb(250, 249, 246)` (cream) despite `body{background:#0A0A0F}` in `<style>`.
**Root cause**: `<body class="bg-surface">` applies Tailwind's `bg-surface` utility which has higher specificity than the inline `<style>` tag. Tailwind config defines `surface: "#FAF9F6"`.
**Fix**: Use `body{background:#0A0A0F!important;color:#E6E4E0!important}`. The `!important` wins over Tailwind's class-based specificity.
**Alternative**: Change Tailwind config `surface` color to dark value, or use `dark:` variants. The `!important` approach is simplest.

### PITFALL 3: Patch tool escape-drift on JS strings
**Symptom**: `Escape-drift detected: old_string and new_string contain the literal sequence '\\"' but the matched region of the file does not.`
**Root cause**: The patch tool serializes quotes in transit. JS template literals with nested quotes (`'"' + variable + '"'`) confuse the serialization.
**Workaround**: Use `execute_code` with `from hermes_tools import patch` and pass raw Python strings directly. Example:
```python
result = patch(path, old_str, new_str)
```
**Alternative**: Use `write_file` for large changes, or `terminal` with Python inline scripts.

### PITFALL 4: Patch tool finds multiple matches
**Symptom**: `Found N matches for old_string. Provide more context to make it unique.`
**Root cause**: The `old_string` is too short or too generic (e.g., `"actionable_trade": ""`).
**Fix**: Use `read_file(offset=X, limit=Y)` to capture 5-10 lines of surrounding context. Include section comments, neighboring fields, and unique identifiers in `old_string`.

### PITFALL 5: Telegram Markdown parse_mode breaks Unicode
**Symptom**: `HTTP Error 400: Bad Request` when sending GapFire dispatch.
**Root cause**: `parse_mode: "Markdown"` in Telegram API call cannot handle Unicode box-drawing chars (━), emoji (💰📊🎯), or special symbols.
**Fix**: Remove `parse_mode` and `disable_web_page_preview: True`. Send as plain text. Telegram renders emoji natively without parse_mode.

### PITFALL 6: Sidebar shows $0M despite real data in flows.json
**Symptom**: Domain Intelligence sidebar shows "DX=F DOLLAR DECLINE 0M" even though flows.json has `total_capital_b: 244.4`.
**Root cause**: `build_frontend.py` `build()` function sums `capital_volume_usd` from individual stories (often 0 or $100M LLM default). It does not read flows.json aggregated numbers.
**Fix**: After computing story-level caps, check `flows_raw.get("narrative_flows", {}).get(cid, {}).get("total_capital_b", 0)`. If > 0, use that instead. Only fall back to story-level sum if flows.json doesn't have data.

### PITFALL 7: File reverted by git checkout mid-session
**Symptom**: Changes applied by patch tool disappear, file reverts to old state.
**Root cause**: Running `git checkout <file>` (e.g., to "reset" after a failed patch) pulls the last committed version, discarding ALL in-memory changes — including patches that succeeded before the failure.
**Fix**: When a patch fails, do NOT git checkout the file. Instead, pull the latest working version from the VM: `scp gazzetta-prod:/opt/gazzetta-di-kyiv/scripts/<file> .`. The VM always has the last successfully deployed version.

### PITFALL 8: CDN serves stale content despite GCS update
**Symptom**: `gsutil cat gs://www.lagazzettadikyiv.com/index.html | grep -c 'new-feature'` returns expected count, but `curl -s https://www.lagazzettadikyiv.com/ | grep -c 'new-feature'` returns 0. The live site doesn't show changes deployed minutes ago.
**Root cause**: Google Cloud CDN caches objects independently of GCS origin. The CDN's default TTL overrides the `Cache-Control` header set by `gsutil -h`. The VM service account lacks `compute.urlMaps.invalidateCache` permission (`ERROR: Required 'compute.urlMaps.invalidateCache' permission`).
**Fix (two-tier verification)**: Always verify deployments at BOTH layers:
  1. **GCS layer**: `ssh gazzetta-prod "sudo bash -c 'gsutil cat gs://www.lagazzettadikyiv.com/index.html | grep -c <feature>'"` — confirms upload succeeded.
  2. **CDN layer**: `curl -s https://www.lagazzettadikyiv.com/ | grep -c <feature>` — confirms end users see it.
  If GCS shows correct but CDN doesn't: the deploy succeeded but CDN cache hasn't refreshed. Report both states honestly. The CDN will refresh on its own TTL cycle (typically 5-60 min).
**Prevention**: Ask Alex to grant the VM service account `compute.urlMaps.invalidateCache` role, or configure the CDN backend to respect origin Cache-Control headers.

### PITFALL 9: SSH/SCP connection failures — wrong IP or user
**Symptom**: `ssh gazzetta@35.188.110.255` times out. `scp file gazzetta@35.232.28.188:/opt/...` returns `Permission denied (publickey)`.
**Root cause**: The VM IP can change (GCP ephemeral IPs). The SSH config at `~/.ssh/config` has the canonical alias `gazzetta-prod` with correct HostName, User (`alexstocchi`), and IdentityFile (`~/.ssh/google_compute_engine`). Raw IP connections fail when the IP is stale or when using wrong username (`gazzetta` instead of `alexstocchi`).
**Fix**: Always use `gazzetta-prod` alias: `ssh gazzetta-prod`, `scp file gazzetta-prod:/tmp/`. Never use raw IPs.
**To find current IP**: `cat ~/.ssh/config | grep -A3 gazzetta-prod` or `gcloud compute instances describe gazzetta-prod --zone=us-central1-a --format='value(networkInterfaces[0].accessConfigs[0].natIP)'`.

### PITFALL 10: scp permission denied — file ownership mismatch
**Symptom**: `scp file gazzetta-prod:/opt/gazzetta-di-kyiv/scripts/build_frontend.py` returns `Permission denied` even with correct SSH alias.
**Root cause**: VM files under `/opt/gazzetta-di-kyiv/` are owned by user `gazzetta`, but SSH connections use user `alexstocchi` (per SSH config). Direct scp to the gazzetta-owned directory is blocked.
**Fix**: Two-step deploy:
  1. `scp local_file gazzetta-prod:/tmp/` — scp to world-writable /tmp
  2. `ssh gazzetta-prod "sudo cp /tmp/local_file /opt/gazzetta-di-kyiv/scripts/ && sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/scripts/local_file"`
  Then trigger rebuild: `ssh gazzetta-prod "cd /opt/gazzetta-di-kyiv && sudo -u gazzetta python3 scripts/build_frontend.py"`
  Then deploy to GCS: use the gsutil command from governor.py's deploy step.

### PITFALL 11: Synthesis fails — DEEPSEEK_API_KEY not set (systemd EnvironmentFile missing)
**Symptom**: Governor log shows `[synthesis] FAIL(1): DEEPSEEK_API_KEY not set`. Every new API key works briefly then "disappears." Alex burns through keys.
**Root cause**: The systemd service at `/etc/systemd/system/gazzetta-governor.service` declares `EnvironmentFile=/opt/gazzetta-di-kyiv/.env` but that file **does not exist**. Keys set in SSH shell sessions (`export DEEPSEEK_API_KEY=...`) are lost on disconnect or reboot — they were never persisted to disk.
**Fix**: Create the persistent env file once:
```bash
cat > /tmp/gazzetta.env << 'EOF'
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF
scp /tmp/gazzetta.env gazzetta-prod:/tmp/
ssh gazzetta-prod "sudo cp /tmp/gazzetta.env /opt/gazzetta-di-kyiv/.env && sudo chown gazzetta:gazzetta /opt/gazzetta-di-kyiv/.env && sudo chmod 600 /opt/gazzetta-di-kyiv/.env"
```
Then reload systemd: `ssh gazzetta-prod "sudo systemctl daemon-reload"`. The governor reads this file on every timer tick. Survives reboots.
**Verification**: Trigger a full governor cycle manually:
```bash
ssh gazzetta-prod "sudo -u gazzetta bash -c 'export \$(cat /opt/gazzetta-di-kyiv/.env | xargs) && cd /opt/gazzetta-di-kyiv && /opt/gazzetta-di-kyiv/venv/bin/python scripts/governor.py --once'"
```
All 11 steps should show OK. The `[synthesis]` step must not fail.
**Note on manual testing**: `sudo -u gazzetta` strips environment. When testing synthesis in isolation, always export from the .env file inside the sudo subshell:
```bash
sudo -u gazzetta bash -c 'export $(cat /opt/gazzetta-di-kyiv/.env | xargs) && cd /opt/gazzetta-di-kyiv && /opt/gazzetta-di-kyiv/venv/bin/python scripts/contradiction_synthesizer.py'
```

### PITFALL 12: execute_code read_file → write_file corrupts Python files
**Symptom**: After using `execute_code` with `read_file(path, offset=X, limit=Y)` followed by `write_file(path, content)`, the file fails with `IndentationError: unexpected indent` on line 1. `xxd` shows the file starts with `2020 2020 2020 317c` (spaces + `1|` prefix).
**Root cause**: `read_file()` returns content formatted with `LINE_NUMBER|CONTENT` prefixes (e.g., `     1|#!/usr/bin/env python3`). Passing this directly to `write_file()` embeds those prefixes into the file, corrupting every line.
**Fix**: NEVER chain `read_file()` → `write_file()` inside `execute_code`. Use one of these safe alternatives:
  1. **`patch` tool** — preferred for targeted edits. Works from the agent context, not inside execute_code.
  2. **Direct Python `open()` in execute_code** — `with open(path, "r") as f: content = f.read()` gives clean content. `with open(path, "w") as f: f.write(content)` writes clean.
  3. **`execute_code` with `from hermes_tools import patch`** — the hermes_tools patch function inside execute_code uses the same patch engine but without serialization issues.
**Recovery**: If the file is already corrupted, `git checkout <file>` restores the last committed version. WARNING: this discards ALL uncommitted changes. Safer: `scp gazzetta-prod:/opt/gazzetta-di-kyiv/scripts/<file> .` if the VM has a working copy. Check VM file integrity first: `ssh gazzetta-prod "python3 -c 'import py_compile; py_compile.compile(chr(47)+chr(111)+chr(112)+chr(116)+chr(47)+chr(103)+chr(97)+chr(122)+chr(122)+chr(101)+chr(116)+chr(116)+chr(97)+chr(45)+chr(100)+chr(105)+chr(45)+chr(107)+chr(121)+chr(105)+chr(118)+chr(47)+chr(115)+chr(99)+chr(114)+chr(105)+chr(112)+chr(116)+chr(115)+chr(47)+chr(98)+chr(117)+chr(105)+chr(108)+chr(100)+chr(95)+chr(102)+chr(114)+chr(111)+chr(110)+chr(116)+chr(101)+chr(110)+chr(100)+chr(46)+chr(112)+chr(121), doraise=True); print(chr(79)+chr(75))'"`.

### PITFALL 13: Session search returns empty — Telegram sessions not indexed
**Symptom**: `session_search(query="Phase C build_frontend")` returns 0 results despite extensive Phase C development work having occurred in this session.
**Root cause**: The session DB only indexes CLI sessions (`source: "cli"`). Telegram gateway sessions may not be persisted or indexed. As of June 22, only 3 sessions are in the DB, all from June 20 CLI.
**Workaround**: Do not rely on session_search for recovery. Instead:
  1. Commit working code to git after each feature deploy.
  2. Keep the VM as a backup source: `scp gazzetta-prod:/opt/gazzetta-di-kyiv/scripts/<file> .` before making risky changes.
  3. The conversation compaction summary in long sessions contains a detailed changelog — use it as a reconstruction spec.
