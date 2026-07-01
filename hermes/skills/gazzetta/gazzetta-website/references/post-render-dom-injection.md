# Post-Render DOM Injection Pattern

## When to use

When `build_frontend.py` (or `build_frontend_staging.py`) renders story cards via inline JS string concatenation:

```javascript
cardsEl.innerHTML = STORIES.map(function(s) {
  return '<article class="...">' +
    '<div>' + s.headline + '</div>' +
    '</article>';
}).join('');
```

**DO NOT modify the concatenated string template.** Adding a new div, attribute, or closing tag to this fragile string chain frequently breaks the closing-tag sequence, producing silent rendering failures with no console errors.

## Pattern: Inject via post-render DOM manipulation

Add a standalone function that runs AFTER `cardsEl.innerHTML` assignment:

```javascript
function injectSourceAttribution() {
    var articles = document.querySelectorAll('article[data-story-id]');
    for (var i = 0; i < articles.length; i++) {
      var card = articles[i];
      if (card.querySelector('.source-attribution-footer')) continue;  // idempotent
      var sourceData = card.getAttribute('data-source-feed');
      if (!sourceData || sourceData.trim() === '') continue;  // skip empty
      var footer = document.createElement('div');
      footer.className = 'source-attribution-footer ...';
      footer.innerHTML = '...' + sourceData.toUpperCase() + '...';
      card.appendChild(footer);
    }
}
```

Call it immediately after the `innerHTML` assignment — no custom events needed:

```javascript
cardsEl.innerHTML = STORIES.map(...).join('');
injectSourceAttribution();
```

## Requirements for the pattern to work

1. The `<article>` tag must carry `data-*` attributes with the needed data (e.g., `data-story-id`, `data-source-feed`)
2. The Python template injection loop must stamp those attributes from the story dict
3. The JS function must validate the attribute is non-empty before injecting
4. The JS function must guard against duplicate injection

## JSON migration pattern (companion)

When adding a new field to the pipeline output schema, existing `stories.json` data won't have it. A one-shot migration script applies the same extraction logic retroactively:

```python
from urllib.parse import urlparse

def extract_domain(url):
    if not url: return ""
    netloc = urlparse(url).netloc
    domain = netloc.replace("www.", "").split(":")[0].lower()
    mapping = {"ecb.europa.eu": "ECB", "oilprice.com": "OilPrice.com", ...}
    return mapping.get(domain, domain.upper())

# Read, inject, write
data = json.load(open("data/stories.json"))
for container in data["containers"].values():
    for story in container["stories"]:
        if "feed_source" not in story:
            story["feed_source"] = extract_domain(story.get("source_url", ""))
json.dump(data, open("data/stories.json", "w"), indent=2)
```

This avoids a costly full pipeline re-run just to add one field.

## Real example (June 2026)

Added source attribution footers to story cards on Staging v9:

1. `contradiction_synthesizer.py`: Added `extract_domain()` helper + `feed_source` field to `assemble_story()`
2. Migration script: Injected `feed_source` into all 822 existing stories in `stories.json`
3. `build_frontend_staging.py`: Stamped `data-source-feed` on `<article>` tags, added `injectSourceAttribution()` after card render
4. `test_platform.py`: 102/102 passing after changes
