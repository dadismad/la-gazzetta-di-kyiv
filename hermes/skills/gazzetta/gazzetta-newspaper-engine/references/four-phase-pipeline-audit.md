# Four-Phase Pipeline Audit Methodology

Established 2026-06-16. This is THE methodology for comprehensive Gazzetta system debugging.

## When to Use
- User says "debug the system," "audit everything," "check all choke points"
- Site is broken in a way that suggests systemic issues, not a single-file bug
- After a major architectural change (migration, redesign, new pipeline)

## The Four Phases

### Phase 1: DATA COLLECTION
**Question:** How do stories enter the system? Where does it break?

Check:
1. `link_processor.py` — full_json format, classification logic, DB write
2. Cloud Scheduler — which cron jobs are ENABLED vs PAUSED
3. CCO pipeline — story generation, curation, distribution
4. Ingestion path — URL → story → DB → JSON → site

Delegate prompt:
```
Audit the DATA COLLECTION phase. Check link_processor.py full_json format, 
Cloud Scheduler job states (gcloud scheduler jobs list), CCO pipeline status, 
and the complete story ingestion path from URL to DB to site. Find all choke points.
```

### Phase 2: DATA PROCESSING
**Question:** Do the pipeline scripts handle all edge cases?

Check:
1. `db_to_json.py` — HTML entity handling, source_name extraction, field completeness
2. `build_site.py` — component injection coverage, cache busting, glob patterns
3. `build_hashed_assets.py` — regex patterns, HTML file coverage
4. `test_platform.py` — test coverage, edge cases
5. `deploy_routine.sh` — cleanup order, GCS sync
6. `cloud_entrypoint.py` — upload integrity

Delegate prompt:
```
Audit the DATA PROCESSING phase. Check all pipeline scripts for edge cases, 
missing error handling, regex bugs, and correctness. Include db_to_json, 
build_site, build_hashed_assets, test_platform, deploy_routine, cloud_entrypoint.
```

### Phase 3: INTERPRETATION
**Question:** Is the analysis quality real or fake?

Check:
1. Classification — how many classifiers exist? Are they consistent?
2. Contradiction scores — distribution (placeholders vs meaningful)
3. Capital flow data — collected vs actually emitted in JSON
4. Tags — coverage percentage, correctness
5. Sample stories from each container for misclassifications

Delegate prompt:
```
Audit the INTERPRETATION phase. Check classification quality across all 
containers, contradiction score distribution, capital flow data coverage, 
and tag accuracy. Sample stories from each container and flag misclassifications.
```

### Phase 4: REPRESENTATION
**Question:** Does the site actually show what the data contains?

Check (agent does this directly, not via delegate):
1. Front page — container counts, story cards, source names, tier badges, tags
2. Archive — URL params, filtering, search, HTML entities
3. i18n — locale file deployed, translations working
4. CSS — hashed files loading, gold borders, contrast
5. About/methodology/sources pages — footer, navigation
6. JS errors — console exceptions

## Execution Pattern

```
1. Spawn 3 parallel delegates (Phases 1-3)
2. Agent runs Phase 4 directly in browser
3. Synthesize findings from all 4 phases
4. Prioritize: BLOCKING (deploy/rendering broken) > HIGH (data quality) > LOW (dead code)
5. Fix blocking bugs first
6. Rebuild pipeline (all stages)
7. Run test_platform.py
8. Deploy to GCS
9. Verify in browser
```

## Key Discoveries (2026-06-16 Audit)

This methodology found 30+ bugs including:
- `cache_bust_assets()` was a complete no-op (replacer always returned original)
- Locale files never deployed to GCS (i18n silently broken)
- `link_processor.py` full_json missing 17 of 28 required fields
- 6 of 7 Cloud Scheduler jobs PAUSED (no content distribution)
- `build_hashed_assets.py` regex missed `?t=` query strings
- 4 HTML pages missing FOOTER sentinel markers
- Subdirectory HTML files skipped by `glob("*.html")`
- 87% of contradiction scores are placeholder (score=75)
- Capital flow data collected but never emitted in JSON output
- 3 conflicting classifiers operating simultaneously

## Anti-Pattern (DO NOT DO)

Do NOT respond to "debug the system" with:
- A single browser_snapshot check
- "Let me look at the site" + one curl
- Ad-hoc terminal commands checking one file at a time
- Summarizing what you THINK is wrong without delegate verification

These miss systemic bugs. The no-op `cache_bust_assets()` survived for months because nobody read the function body line-by-line. Only a delegate reading every script file catches these.
