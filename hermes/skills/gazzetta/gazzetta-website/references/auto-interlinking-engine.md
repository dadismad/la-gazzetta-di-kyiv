# Auto-Interlinking Engine — build_related_links.py

## Purpose

Generates related_stories and related_flows for every story in stories.json.
Enables cross-navigation between stories and from stories to flows on the story detail page.

## Algorithm

### Story→Story Links

For each story, compute a keyword overlap score against every other story.
Keywords extracted from:
- `entity_tags` (array of tag strings)
- `sector` (e.g., "tech", "crypto", "commodities")
- `paradigm` (e.g., "china_ascendancy", "blockchain_agentic")
- `capital_flow.asset_class`
- `capital_flow.direction`
- `severity`

Score = number of shared keywords. Take top 3 by score.
Output field: `related_stories` — array of `{story_id, headline, sector, score, shared_tags}`.

### Story→Flow Links

For each story, match flows by:
- Same `asset_class` = +2 score
- Same `direction` = +1 score

Take top 3 by score.
Output field: `related_flows` — array of `{flow_id, asset_class, direction, amount_formatted, confidence_pct, pace_multiplier, score}`.

## Integration

- **Pipeline stage:** Stage 1.1 in `shipit.sh` — runs after `db_to_json.py`, before `analyze_narratives.py`
- **Input:** `site/data/stories.json` + `site/data/flows.json`
- **Output:** Injects `related_stories` and `related_flows` directly into stories.json
- **Sync:** Also writes to `data/stories.json` for pipeline consistency

## Frontend Rendering

`story-app.js` function `renderRelated(story)`:
- Renders `<section class="intel-related">` with RELATED STORIES header
- 3-column grid: `.related-grid` → `.related-card` with sector badge + headline
- RELATED FLOWS section: `.related-card.flow-related` with asset class + amount + confidence + pace
- Responsive: collapses to single column at 768px

## CSS

```css
.related-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.related-card { padding: 14px; border: 1px solid var(--divider); background: var(--white); }
.related-card:hover { background: #F9FAFB; }
@media (max-width: 768px) { .related-grid { grid-template-columns: 1fr; } }
```

## Performance

- 59 stories × 58 comparisons = ~3,422 operations. Runs in <1 second.
- 177 story→story links + 177 story→flow links (3 avg/story each)
- 100% coverage — every story has 3 related stories and 3 related flows

## Script

`scripts/build_related_links.py` — standalone Python script, no external dependencies beyond stdlib.
Run via: `python scripts/build_related_links.py`
