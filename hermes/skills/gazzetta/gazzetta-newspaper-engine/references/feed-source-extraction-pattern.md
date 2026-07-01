# Feed Source Extraction — Pipeline Enrichment Pattern

How to add a new data field that survives from ingestion → synthesizer → stories.json → frontend. Implemented for `feed_source` (clean publication names like "ECB", "OilPrice.com") but the pattern generalizes to any upstream field.

## The Problem

`ingestion_triage.py` stores rich metadata (source URL, source type, feed name) in the `ingestion_hashes` DB table. `contradiction_synthesizer.py` reads from this table and sends data to DeepSeek. But the LLM's JSON response schema only includes analytical fields (headline, they_say, reality, gap). Source metadata MUST be re-attached at the `assemble_story()` layer — after the LLM response, before writing to stories.json.

## Pattern: Three-Step Enrichment

### Step 1: Helper Function

Add a deterministic transformation function that derives the desired field from existing data:

```python
from urllib.parse import urlparse

def extract_domain(url: str) -> str:
    """Derive a clean publication name from a source URL."""
    if not url:
        return ""
    try:
        netloc = urlparse(url).netloc
        domain = netloc.replace("www.", "").split(":")[0].lower()
        mapping = {
            "ecb.europa.eu": "ECB",
            "oilprice.com": "OilPrice.com",
            "statnews.com": "STAT News",
        }
        return mapping.get(domain, domain.upper())
    except Exception:
        return ""
```

**Key design decisions:**
- Returns empty string on failure (not None, not exception) — downstream consumers check `if not sourceData` to skip silently
- Mapping dict for high-conviction institutional names (ECB, IMF)
- Fallback to `domain.upper()` for unrecognized sources — always produces something human-readable
- Pure stdlib (no dependencies) — safe to run on VM without `pip install`

### Step 2: Assemble Story — Add Field

In `assemble_story()`, add the field to the output dict:

```python
def assemble_story(db_item, llm_story, prices):
    item_id, source_url, source_type, title, full_text, narrative_tag = db_item
    # ... existing assembly logic ...
    
    return {
        # ... existing fields ...
        "source_name": source_type.upper(),          # retained for legacy
        "source_url": source_url,                     # retained for reference
        "feed_source": extract_domain(source_url),    # NEW: clean publication name
        "generated_at": now_ts,
    }
```

The `db_item` tuple comes from `fetch_unprocessed()` which SELECTs `id, source_url, source_type, title, full_text, narrative_tag` from `ingestion_hashes`. Any column in that SELECT is available in `assemble_story()` without schema changes.

### Step 3: Retroactive Migration

New stories get the field. Existing stories in `stories.json` need retroactive injection. Write a one-shot migration script:

```python
import json
from urllib.parse import urlparse
from pathlib import Path

# ... extract_domain() ...

stories_path = Path("data/stories.json")
with open(stories_path) as f:
    data = json.load(f)

for container_name, container_data in data.get("containers", {}).items():
    for story in container_data.get("stories", []):
        if "feed_source" not in story:
            story["feed_source"] = extract_domain(story.get("source_url", ""))

with open(stories_path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

Run once. Idempotent — only adds to stories missing the field.

## Frontend Consumption

In `build_frontend.py`, stamp the field as a data attribute on the article element:

```javascript
return '<article data-story-id="' + s.story_id + 
       '" data-source-feed="' + (s.feed_source || '') + 
       '" class="...">' +
```

Then inject attribution footers via post-render DOM manipulation:

```javascript
function injectSourceAttribution() {
    var articles = document.querySelectorAll('article[data-story-id]');
    for (var i = 0; i < articles.length; i++) {
        var card = articles[i];
        if (card.querySelector('.source-attribution-footer')) continue;  // idempotent
        var sourceData = card.getAttribute('data-source-feed');
        if (!sourceData || sourceData.trim() === '') continue;          // skip empty
        // Build and append footer...
    }
}
```

**Guardrails:**
- Skip if footer already exists (idempotent re-renders)
- Skip if attribute is empty (no bad defaults)
- No dependency on custom events — use `DOMContentLoaded` or readyState check

## Pitfalls

1. **Field name mismatch between synthesizer and template** — Always run a schema audit before deploying: check the actual field name in stories.json, verify the template uses the same key.
2. **Generic source_type values** — `source_type` from the DB table may be "RSS" or "YOUTUBE" (ingestion channel), not the specific feed name. The domain extraction path uses `source_url` which is always specific.
3. **Mapping dict staleness** — New feeds won't be in the mapping dict and will fall through to `domain.upper()` (e.g., "BLOOMBERG.COM"). Acceptable until the next dict update.
4. **Migration script runs on local data** — The VM has its own stories.json. If the migration only runs locally, VM stories won't have the field. Either run on both, or let the automated synthesizer cycle populate it naturally (new stories only — old stories remain without the field until next manual migration).
