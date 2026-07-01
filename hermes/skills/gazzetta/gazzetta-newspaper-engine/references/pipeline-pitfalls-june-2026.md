# Pipeline Execution Pitfalls — June 2026

Captured during the P0 data engine rebuild of La Gazzetta di Kyiv (June 21-22, 2026). These are operational patterns that caused multi-week silent failures.

---

## 1. gsutil Deploy Silently Fails When User Lacks gcloud Credentials

**Symptom:** `[deploy] OK` reports success, but GCS file timestamps never update. The pipeline appears healthy. The live site serves stale content indefinitely. We had this for ~2 weeks.

**Detection:** Check GCS timestamp after any deploy:
```bash
gsutil ls -la gs://www.lagazzettadikyiv.com/index.html
```
If the timestamp is >1h old despite pipeline cycles completing, the deploy is failing silently.

**Root cause:** The systemd service user (`gazzetta`) has no gcloud credentials. The `gsutil` in the system PATH falls back to anonymous access, which is denied on private GCS buckets, but `gsutil` returns exit code 0 anyway (it lists the file successfully but never uploads). The `gcloud compute url-maps invalidate-cdn-cache` also fails silently at the end, consumed by `2>/dev/null; true`.

**Detection hack:** The deploy time was ~2.9s when silently failing (just listing files) vs ~27s when actually uploading 560KB+. The time delta is a canary.

**Fix:** The VM's root user has service account credentials via GCP metadata (`397576418262-compute@developer.gserviceaccount.com`). Add `sudo` to the deploy command in governor.py STEPS:
```python
("deploy", ["sudo", "bash", "-c", "gsutil ..."], 120, False),
```
Ensure the `gazzetta` user has passwordless sudo for gsutil.

---

## 2. API Key Name Mismatch Between Governor and Subprocess Scripts

**Symptom:** Pipeline step fails with `ERROR: DEEPSEEK_API_KEY not set` despite the governor loading the key from GCP Secret Manager successfully.

**Root cause:** `governor.py` stores the key in a local variable `DEEPSEEK_KEY` (loaded via `_secret("gazzetta-deepseek-key")`). But subprocess scripts expect the environment variable `DEEPSEEK_API_KEY`. The governor's `run_cmd()` helper passes `os.environ` to child processes — which does NOT contain `DEEPSEEK_API_KEY` because it was loaded into a Python variable, not exported to the environment.

**Fix:** Explicitly add the key to the subprocess environment in `run_cmd()`:
```python
env={**os.environ, "PYTHONUNBUFFERED":"1", "DEEPSEEK_API_KEY": DEEPSEEK_KEY or ""}
```

**Lesson:** Always verify subprocess env propagation when adding new scripts to the pipeline. Any script that reads `os.environ.get("X")` needs X to be explicitly passed by the parent.

---

## 3. LLM Output Sanitization — Prompt Bans Are Insufficient

**Symptom:** Despite banning specific phrases in the system prompt (e.g., "NEVER use 'fails to move markets'"), the LLM at temperature 0.3 finds semantic loopholes: "fails to move tracked assets", "fails to move biotech ETFs", "fails to move global markets". The ban works for exact matches but not for variants.

**Lesson:** Prompt engineering alone cannot enforce hard output constraints on LLMs. The LLM will always find variants that bypass string-match bans because it processes semantics, not regex.

**Fix:** Add a hard code-level regex sanitizer in `assemble_story()` that runs AFTER the LLM returns:
```python
raw_headline = llm_story.get("headline", title)[:120]
banned_re = re.compile(r'\b(fails?\s+to\s+\w+|market\s+unmoved|markets?\s+shrug|markets?\s+unfazed|no\s+market\s+impact)\b', re.IGNORECASE)
if banned_re.search(raw_headline):
    raw_headline = banned_re.sub("leaves market pricing unchanged for", raw_headline)
    raw_headline = re.sub(r'\s+', ' ', raw_headline).strip()
sanitized_headline = raw_headline
```

This guarantees compliance regardless of what the LLM returns. The regex runs on the raw output before it enters the data pipeline. This is a 5-line Python block that eliminates the entire class of "LLM bypassed the ban" bugs.

**Pattern applies to:** Any LLM pipeline where output format/structure must be enforced. Prompt guidance is a suggestion; regex is a constraint.

---

## 4. Dual Data Structures (containers vs all_stories) Cause Display Mismatches

**Symptom:** Capital Flows table shows story counts that don't match the Stream. Sidebar capital values don't match the ledger. Container counts differ from all_stories counts by up to 48 stories.

**Root cause:** `stories.json` has BOTH a legacy `containers` dict AND a modern `all_stories` array. Some scripts read one, some read the other. `generate_flows.py` reads `containers` (wrong). `build_frontend.py` reads `all_stories` (right). The numbers diverge.

**Fix:** All new scripts MUST read `all_stories`. The `containers` section is vestigial v2.0 format and should never be the source of truth. Migrate `generate_flows.py` to use `all_stories`. Consider deleting or explicitly marking `containers` as `"deprecated": true` in the JSON.

---

## 5. Path Mismatch Between Scripts Writing to Different Directories

**Symptom:** Scripts read/write stories.json from different paths despite being in the same pipeline. `contradiction_synthesizer.py` writes to `public/data/stories.json` but `calculate_capital.py` and `classify_stories.py` originally read from `data/stories.json`.

**Root cause:** Each script defines its own `DATA_DIR` / `STORIES_FILE` paths independently. No shared path resolution. The original scripts used hardcoded `/opt/gazzetta-di-kyiv/data/` while the synthesis script used `PROJECT / "public" / "data"` (resolving via `__file__`).

**Fix:** Standardize all scripts to use `PROJECT = Path(__file__).resolve().parent.parent` as the base, then use `PROJECT / "public" / "data"` for stories.json (the deployed copy) and `PROJECT / "data"` for source data files (cftc_cot.json, fred_macro.json, coingecko_data.json, macro_baselines.json, narratives.json).
