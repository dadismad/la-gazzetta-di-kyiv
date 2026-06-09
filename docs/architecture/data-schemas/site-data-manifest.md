# Site Data Manifest

> All 13 files synced by build_site.py from data/ -> site/data/.

## Sync Files

| # | File | Source | Purpose |
|---|------|--------|---------|
| 1 | narratives.json | data/ | Narrative framework definitions |
| 2 | stories.json | data/ | Canonical story data (smart merge) |
| 3 | stories_in_play.json | data/ | Currently active stories subset |
| 4 | living_stories.json | data/ | Enriched story threads |
| 5 | story_registry.json | data/ | Story ID registry |
| 6 | intelligence_objects.json | data/ | Intelligence signal objects |
| 7 | asset_claims_latest.json | data/ | Latest asset claims data |
| 8 | representation_techniques.json | data/ | AI representation methods |
| 9 | source_registry_ranked.json | data/ | Ranked source reliability |
| 10 | ops_status.json | data/ | Operations health status |
| 11 | publish_manifest.json | data/ | Publishing state manifest |
| 12 | flows.json | data/ | Capital flow data |
| 13 | website_stories_latest.json | data/ | Latest website stories |

## Smart Merge Logic (stories.json)

build_site.py performs a smart merge when syncing stories.json:
1. Loads source (data/) and destination (site/data/) stories
2. Identifies site-only stories (added by source monitor)
3. Preserves site-only stories in merged output
4. Prevents data pipeline from overwriting site-only additions

## API Endpoints

After sync, site/api/v1/home/*.json are generated for external API consumption.
