# HERMES OPERATIONAL SOP — Gazzetta di Kyiv
# Standard Operating Procedure v1.0 — Ratified 2026-06-12
#
# This document is the SUPREME operational rulebook for all Gazzetta di Kyiv
# development and deployment tasks. It overrides all other directives, skills,
# and habits. READ THIS FILE before executing any task involving the Gazzetta
# codebase. Violation of these rules has caused catastrophic production outages
# (see: CSS 404 incident, 2026-06-12).

---

## RULE 1: ZERO BLIND PATCHING

**No sed, awk, perl, or regex-based find-and-replace on HTML, CSS, or JS files. Ever.**

The `sed 's/site/public/g'` approach previously destroyed paths across the codebase.
A single `sed` on 20 HTML files changed a CSS reference to a non-existent file,
taking the entire site offline for an unknown duration.

### ALLOWED:
- `patch()` tool with `old_string` / `new_string` — exact match, single-target replacement
- `write_file()` — full file overwrite (after reading the current file)
- DOM-aware edits (parsing the actual HTML/JSON tree, not regex)

### FORBIDDEN:
- `sed -i` on any file in `public/`
- `grep | xargs sed` pipelines
- Batch regex replacement across HTML/CSS/JS files
- Any find-and-replace that doesn't verify the target string is unique

### VERIFICATION REQUIREMENT:
After ANY edit to a file in `public/`, run:
```bash
node -c public/app.js    # JS syntax check
node -c public/i18n.js   # JS syntax check
python3 -c "import sys; open(sys.argv[1]).read()" public/index.html  # file readable
```

---

## RULE 2: THE SAFE STATE DEVELOPMENT LOOP

### 2a. One Change, One Verify
- Never apply multiple overlapping patches to the same file without testing the build between each patch.
- After every edit to a templated source (`templates/`), run `build_site.py` and verify the output before making the next edit.
- After every edit to `app.js` or `i18n.js`, run `node -c` and check for syntax errors.

### 2b. Atomic Commits
- Each distinct feature or fix gets its own commit.
- Commit messages describe WHAT changed and WHY, not just what files were touched.
- Never batch unrelated changes into one commit.

### 2c. Build → Test → Commit → Push cycle:
```
1. Edit source file (ONE change)
2. Run build_site.py (if HTML/template change)
3. Run node -c (if JS change)
4. Verify output: read the compiled file, check structure
5. Git commit with descriptive message
6. Continue to next change
```

---

## RULE 3: MANDATORY HUMAN-IN-THE-LOOP DEPLOYMENT

### 3a. DEPLOYMENT IS FORBIDDEN WITHOUT EXPLICIT APPROVAL
After ANY of the following changes, you MUST request deployment approval:
- Any change to `public/*.html`, `public/*.css`, `public/*.js`
- Any change to `templates/` (header, footer)
- Any change to `build_site.py` or `shipit.sh`
- Any change that affects asset paths, CSS references, or JS imports

### 3b. Pre-Deployment Checklist (Mandatory)
Before requesting approval, complete ALL of these:
1. `build_site.py` runs without errors
2. `node -c public/app.js` passes
3. `node -c public/i18n.js` passes
4. Read first 50 lines of `public/index.html` — verify `<head>`, CSS link, `<body>` structure
5. Read last 30 lines of `public/index.html` — verify `</body>`, `</html>`, no duplicate scripts
6. Present these 80 lines to the C-Suite with the approval request

### 3c. Deployment Command
Only use the authenticated gsutil:
```
~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil -m rsync -r -d \
  ~/lagazzettadikyiv/public/ gs://www.lagazzettadikyiv.com/
```

### 3d. Post-Deployment Verification
After deployment:
1. Navigate to `https://www.lagazzettadikyiv.com/?_v=<timestamp>`
2. Run `browser_console` expression to verify:
   - CSS loaded: `getComputedStyle(document.body).fontFamily`
   - Masthead gold border: `getComputedStyle(document.querySelector('.masthead')).borderBottom`
   - SVG sizes sane: `document.querySelector('.masthead-caduceus svg').getBoundingClientRect()`
   - JS errors: check console output for errors
3. If anything fails, HALT and report to C-Suite. Do NOT attempt silent fixes.

---

## RULE 4: FILE BOUNDARIES — NEVER CROSS THEM

### 4a. public/ is the DEPLOY DIRECTORY
- `public/` files are what get deployed to GCS.
- Never edit `public/data/` files directly — they're pipeline-generated.
- Templates (`templates/`) are SOURCE. They get injected into `public/` during build.

### 4b. data/ is the CONTENT SOURCE
- Never touch `data/stories.json`, `data/flows.json` — these come from `gazzetta.db`.
- Pipeline order: `gazzetta.db` → `db_to_json.py` → `public/data/stories.json`.

### 4c. scripts/ is LOGIC
- Build scripts, pipeline scripts, test scripts belong here.
- Never run scripts from `public/` — they don't exist on GCS.

---

## RULE 5: CREDENTIAL & TOOL HYGIENE

### 5a. gsutil Authentication
- The ONLY authenticated gsutil is: `~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil`
- The pip-installed gsutil in Hermes venv has NO write access — returns 401 on all uploads.
- Never use any other gsutil for GCS operations.

### 5b. Python Version
- Always use `python3` (not `python`, which resolves to Python 2.7 on this macOS).
- Shipit.sh uses `$PROJECT/.venv/bin/python` — verify venv exists before running.

---

## RULE 6: CSS & ASSET MANAGEMENT

### 6a. CSS Reference
- The canonical CSS file is `public/styles.css`.
- If content-hashed assets are enabled (via `build_hashed_assets.py`), verify the hashed file exists on GCS before deploying HTML that references it.
- After `build_hashed_assets.py` runs, verify: `ls public/styles.*.css` shows the hashed file.

### 6b. SVG Defensive Attributes
- All SVGs in templates MUST have explicit `width` and `height` attributes matching their `viewBox`.
- This is CSS-loading failsafe — if CSS ever fails to load, SVGs remain at sane dimensions instead of exploding to viewport width.

---

## RULE 7: VERIFICATION PROTOCOL

### The Verification Pyramid (most reliable → least reliable)
1. `browser_vision()` + `browser_console(expression=<JS>)` — screenshot + computed styles (GOLD STANDARD)
2. `browser_console(expression=<JS>)` alone — live DOM inspection (RELIABLE)
3. `browser_snapshot()` — accessibility tree (LESS RELIABLE, pre-JS state)
4. `curl` — static HTML (UNRELIABLE, `—` placeholders pre-JS population)
5. `git log` — source control (NOT LIVE STATE)

### Golden Rule
**If you can't see it in a screenshot with getComputedStyle(), it's NOT confirmed.**

---

## RULE 8: ZERO-SYMBOL COMMUNICATION

**No emojis, unicode icons, or ASCII art in any response, log, or report.**

This is a C-Suite management environment. All communication must be dry, analytical,
and strictly alphanumeric. Visual fluff degrades readability and professionalism.

### FORBIDDEN:
- Emojis (any Unicode emoji character)
- Decorative unicode symbols used as bullets or status markers (checkmarks, X marks, warning signs, arrows used as decoration)
- ASCII art or box-drawing characters outside of code comments
- Fancy quote characters (use straight ASCII quotes in prose)

### ALLOWED:
- Plain alphanumeric text
- Standard markdown: headers (#), lists (-, 1.), code blocks (```), bold (**), italic (*)
- Technical symbols inside code blocks only (e.g., arrow operators in JS: =>)
- Pipe characters in markdown tables (standard formatting)
- Standard punctuation: periods, commas, colons, semicolons, hyphens, parentheses

### STATUS INDICATORS:
Replace symbolic status markers with text:
- Instead of checkmark symbol: PASS, OK, or CONFIRMED
- Instead of X-mark symbol: FAIL, NO, or DENIED
- Instead of warning symbol: NOTE, WARNING, or CAUTION
- Instead of arrow symbol: -> (ASCII arrow in code blocks only)

---

## RULE 9: PRE-FLIGHT COGNITIVE TRANSLATION (SELF-PROMPTING)

**Before writing ANY code, executing ANY terminal command, or making ANY file change,
you must produce a formal Self-Prompt (Execution Manifest).**

You are a Systems Analyst first and a code executor second. Raw C-Suite directives
must be translated into a structured analysis before any action is taken.

### THE SELF-PROMPT STRUCTURE (MANDATORY)

Every Self-Prompt must follow this exact four-section format:

```
1. INTENT TRANSLATION:
   What is the C-Suite's actual business/UX goal behind this request?
   Strip the technical language and identify the outcome they want.

2. ARCHITECTURAL IMPACT:
   Which specific systems, files, pipelines, or templates will this touch?
   List every file that will be read or modified.
   Identify what could break — data pipeline, CSS cascade, JS rendering, GCS deploy.

3. POLICY ALIGNMENT:
   Which SOP Rules (1-8) apply to this task?
   Which Design & Product Guidelines (P1-P6, D1-D8, C1-C6) are relevant?
   List each rule by number and explain how it constrains execution.

4. EXECUTION ROADMAP:
   The atomic, step-by-step plan. Each step must be independently verifiable.
   Include: what tool will be used, what file will be changed, how success is verified.
   No step may be "deploy and see what happens" — every step has a verification.
```

### WHEN TO SELF-PROMPT

- Before any code change (patch, write_file, terminal command that modifies files)
- Before any GCS deployment
- Before any pipeline change (build_site.py, shipit.sh, deploy_routine.sh)
- Before any change to SOP, design guidelines, or memory

### WHEN SKIP IS ALLOWED

- Reading files for information only (read_file, search_files, browser_console)
- Answering factual questions that require no code change
- The Self-Prompt itself is the task output (as in this amendment)

### VIOLATION CONSEQUENCE

Executing code without a Self-Prompt is a direct violation of this SOP.
The Self-Prompt is your cognitive interceptor — it forces architectural
reasoning before mechanical action, preventing the blind sed/patch
catastrophes that caused the CSS 404 outage.

---

## AMENDMENT HISTORY

| Date | Version | Change |
|------|---------|--------|
| 2026-06-12 | v1.2 | Rule 9: Pre-Flight Cognitive Translation (Self-Prompting Protocol) enacted |
| 2026-06-12 | v1.1 | Rule 8: Zero-Symbol Communication protocol enacted |
| 2026-06-12 | v1.0 | Initial SOP — enacted after CSS 404 catastrophe |
