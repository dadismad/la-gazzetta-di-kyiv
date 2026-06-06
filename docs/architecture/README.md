# Gazzetta di Kyiv — Website Architecture

> Single source of truth for site structure, component model, data schemas, pipeline design, and design tokens.
> Part of GOS layer under docs/architecture/.

## Document Hierarchy

docs/architecture/
+-- README.md                          <- YOU ARE HERE
+-- site-map.md                        <- Every page, URL, route, navigation
+-- component-catalog.md               <- UI components, JS modules, DOM patterns
+-- css-token-reference.md             <- CSS custom properties, typography, spacing, color
+-- pipeline-diagram.md                <- Pipeline chain: data flow, scripts, cron ownership
+-- cron-registry.md                   <- All 17 cron jobs: schedule, type, script/prompt
+-- deployment.md                      <- GCS deployment, CI/CD, repo structure
+-- data-schemas/
|   +-- stories.md                     <- stories.json schema + fields
|   +-- flows.md                       <- flows.json schema + fields
|   +-- i18n.md                        <- i18n_ru.json + i18n.js contract
|   +-- site-data-manifest.md          <- All 13 sync files in build_site.py
|   +-- intelligence-object.md         <- intelligence_object.schema.json
+-- js-modules/
|   +-- app-js.md                      <- app.js (1713 lines) core logic
|   +-- i18n-js.md                     <- i18n.js (103 lines) multi-language runtime
|   +-- story-app-js.md               <- story-app.js (218 lines) story detail page
|   +-- sector-js.md                  <- sector.js (80 lines) sector photo system
+-- components/
|   +-- README.md                      <- Component index stub
+-- references/
    +-- design-tokens-source.md        <- Maps CSS tokens to design decisions

## Quick Reference

| Layer       | Document                   | Audience                |
|-------------|----------------------------|-------------------------|
| Pages       | site-map.md                | Developers, operators   |
| UI Code     | component-catalog.md + js-modules/ | Frontend devs    |
| Styles      | css-token-reference.md     | Designers, frontend     |
| Data        | data-schemas/              | Pipeline devs, data eng |
| Pipeline    | pipeline-diagram.md        | SRE, operators          |
| Automation  | cron-registry.md           | Operators, governance   |
| Infrastruct | deployment.md              | SRE, operators          |

## Related Documents

- docs/GOS.md — Operating system meta-framework
- docs/process-registry.md — All processes catalogued with failure modes
- docs/strategy.md — Strategic pillars, KPIs, competitive positioning
- docs/runbooks/operations.md — SOPs for incident response

## Auto-Generation Rules

| Document | Source | Trigger |
|----------|--------|---------|
| cron-registry.md | ~/.hermes/cron/jobs.json | On cron change |
| site-map.md | generate_sitemap.py + file listing | On page add/remove |
| pipeline-diagram.md | pipeline_chain.sh + cron defs | On pipeline change |

| Document | Update Cadence | Method |
|----------|---------------|--------|
| css-token-reference.md | On CSS :root change | Manual |
| component-catalog.md | On JS module change | Manual |
| data-schemas/* | On data format change | Manual |
| deployment.md | On infra change | Manual |
