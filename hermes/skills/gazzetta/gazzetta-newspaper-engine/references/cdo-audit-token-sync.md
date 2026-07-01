# CDO Audit Design Token Sync — Fix Pattern

## Failure Mode

CDO auditor (`cdo-auditor` Cloud Run job, runs every 2h) fails with exit code 1. The job shows `FAIL` for hours/days. The site itself is fine — the audit tokens are just stale.

## Detection

```bash
gcloud run jobs executions list --job=cdo-auditor --region=europe-west1 --limit=5
```

If ALL recent executions show `status: False` / "container exited with an error" — token staleness is likely.

## Diagnosis

Read the latest audit log:

```bash
gcloud logging read 'resource.type="cloud_run_job" AND resource.labels.job_name="cdo-auditor" AND textPayload:"VIOLATION"' \
  --limit=20 --format='table(timestamp,textPayload)' --freshness=4h
```

Look for patterns — if the same 2-3 violations repeat across all breakpoints, the tokens are checking wrong values.

## Root Cause Catalog

| Violation pattern | Root cause | Fix |
|---|---|---|
| `Masthead color: rgb(17, 24, 39) (expected rgb(212, 175, 55))` | DESKTOP token set to gold but masthead uses var(--ink) | Update `DESIGN_TOKENS["masthead"]["color"]` to `"rgb(17, 24, 39)"` |
| `Masthead font: "Source Serif 4"... (expected contains 'DM Serif Display')` | Token expects DM Serif Display but .masthead inherits body font; actual masthead name uses Playfair Display | Update `DESIGN_TOKENS["masthead"]["fontFamily_contains"]` to `"Playfair Display"` AND change the audit selector from `.masthead` to `.masthead-name` |
| `Nav background: rgb(255,255,255) (expected contains '15, 23, 42')` | Audit checks `document.querySelector('nav')` which selects the mobile slide-out drawer (white bg on small viewports) | Change audit selector to `.masthead-right` (for masthead nav bar) or `.nav-dropdown-panel` (for dropdown background); update token to match |
| `Card count: 0` or `No .card element found` | Audit checks homepage for `.card` elements but homepage uses teasers; cards only exist on `/stories.html` | Navigate audit to `SITE_URL + "/stories.html"` for card checks |

## Fix Steps (full cycle)

1. **Update `DESIGN_TOKENS`** in `scripts/cdo_audit.py`
2. **Fix any wrong element selectors** in `run_audit()` (e.g., `.masthead` → `.masthead-name` for font check)
3. **Rebuild agents Docker image** (CDO auditor uses `gazzetta-agents:latest`):
   ```bash
   gcloud builds submit --config=cloudbuild.agents.yaml
   ```
4. **Update CDO auditor job**:
   ```bash
   gcloud run jobs update cdo-auditor --region=europe-west1 --image=...gazzetta-agents:latest
   ```
5. **Execute and verify**:
   ```bash
   gcloud run jobs execute cdo-auditor --region=europe-west1 --wait
   ```
6. **Confirm**: `gcloud run jobs executions list --job=cdo-auditor --region=europe-west1 --limit=1`

## Prevention

After any design-changing deploy (CSS edits, template changes, new components), run the CDO auditor immediately to verify tokens are still in sync. Don't wait for the scheduled 2h cycle to discover the problem.
