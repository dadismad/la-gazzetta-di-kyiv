# Operational Governance — June 2026

This reference documents the operational and design governance framework
established on 2026-06-12 after the CSS 404 production outage.

## HERMES_OPERATIONAL_SOP.md (v1.2)

Repo root. Nine binding rules governing ALL Gazzetta work:

| Rule | Name | Summary |
|------|------|---------|
| R1 | Zero Blind Patching | No sed/regex on HTML/CSS/JS. Use patch() or write_file() |
| R2 | Safe State Dev Loop | One change, one verify, atomic commits |
| R3 | Human-in-the-Loop Deploy | NEVER deploy to GCS without C-Suite approval |
| R4 | File Boundaries | public/=deploy, data/=content, scripts/=logic |
| R5 | Credential Hygiene | gsutil from devvit SDK only (~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil) |
| R6 | SVG Failsafes | All SVGs must have explicit width/height matching viewBox |
| R7 | Verification Pyramid | browser_vision + getComputedStyle is gold standard |
| R8 | Zero-Symbol Communication | No emojis, unicode icons, or ASCII art. Plain alphanumeric + markdown only |
| R9 | Pre-Flight Cognitive Translation | Formal 4-section Self-Prompt (Intent, Architecture, Policy, Roadmap) required BEFORE any code execution |

## HERMES_DESIGN_AND_PRODUCT_GUIDELINES.md (v1.0)

Repo root. 18 binding rules from CPO + UX Architect + Managing Editor audit:

### Product Architecture (P1-P6)
- P1: Every page belongs to exactly one layer (INTEL or ALPHA)
- P2: Layer badges must appear prominently on every page
- P3: INTEL pages must link to related ALPHA products (cross-layer)
- P4: Story cards must surface the contradiction, not just the headline
- P5: Service cards (C-Suite/Quant/Execution) must appear on every page
- P6: Navigation must expose the full product hierarchy

### UI/UX Design System (D1-D8)
- D1: Every container follows the unified structural template
- D2: All spacing uses the 4px scale (4, 8, 12, 16, 24, 32, 48)
- D3: Typography follows the 7-level scale
- D4: Collapsible containers must show an arrow indicator
- D5-D7: Gold for masthead/CTAs, dark red for nav, near-black for body text
- D8: Container background always #FFFFFF with 1px #E5E7EB border

### Content Representation (C1-C6)
- C1: Every story card must include headline, contradiction, flow, action
- C2: Flow amounts must include sector context and velocity
- C3: Directional indicators must use color coding (green/red/gray)
- C4: No raw data without inline context
- C5: The "contradiction" line is mandatory
- C6: Breaking/live stories must be visually distinct

## deploy_routine.sh

Repo root. 10-minute refresh pipeline for cron execution:
- Skips nuclear_clean, git sync, hashed assets, deploy report
- Test gate is BLOCKING (aborts on failure)
- Uses devvit SDK gsutil for GCS deploy
- Concurrency lock: mkdir-based atomic lock (/tmp/gazzetta_deploy.lock)
- Log rotation: truncates to 10,000 lines after each run
- Python path: `python3` (system, not .venv — venv is broken with missing python3.13)
- Crontab: ACTIVE as of 2026-06-12 — `*/10 * * * * bash ~/lagazzettadikyiv/deploy_routine.sh >> ~/lagazzettadikyiv/logs/deploy_routine.log 2>&1`

### Mitigations Applied Before Activation
- Test gate: 551/551 pass (slug truncation removed, scale check tightened to headline-only)
- Lockfile: `mkdir /tmp/gazzetta_deploy.lock` (macOS bash 3.2 — no flock, no {varname}>)
- Log rotation: `tail -n 10000` after each run
- Python path fix: `.venv/bin/python` (broken, points to non-existent python3.13) → `python3`

## Pipeline Correction (shipit.sh)

GCLOUD_DIR corrected from non-existent `$HOME/lagazzettadikyiv/google-cloud-sdk` to `$HOME/lagazzettadikyiv/devvit/google-cloud-sdk`. The old path caused fallback to unauthenticated pip gsutil, resulting in silent 401 write failures and CSS 404 on production.

## CSS 404 Root Cause Pattern

The `styles.d0b7cbda.css` file was referenced in all 20 HTML files but never existed on GCS:
1. `build_hashed_assets.py` created the file locally and rewrote HTML references
2. `gsutil rsync` failed silently (wrong gsutil, no write auth)
3. Result: CSS 404 on all pages — SVGs exploded to viewport width, fonts fell back to Times
4. Detection: `getComputedStyle()` → fontFamily = "Times" (not "Source Serif 4")
5. Fix: Reverted all HTML to unhashed `styles.css` + deployed with authenticated gsutil
