# Dual Pipeline Field Mismatch — Story Architecture (v22.38)

The site has TWO story generation pipelines with different field sets. This mismatch silently breaks the story detail page time badge and causes URL overflow.

## Two Pipelines

| Pipeline | Script | Output | Has `generated_at` | Has `capital_flow` dict |
|----------|--------|--------|---------------------|------------------------|
| Intel Pipeline | `scripts/intel_to_stories.py` | `data/stories.json` | ✓ (per story) | ✓ (direction, amount_b, asset_class, projected, pace_multiplier, confidence_pct) |
| Editorial Writer | cron `011c8be0b17c` (LLM agent) | `data/publish/stories.json` | ✗ | ✗ (only `capital_flow_implication` string) |

Both pipelines feed into `data/stories.json` via `scripts/sync_publish_to_site.py`.

## Symptom 1: Empty Time Badge on Story Detail Page

**Root cause:** `story-app.js` renders time via `formatDate(story.timestamp || story.date || story.generated_at)`. Editorial writer stories have NONE of these fields. `formatDate(undefined)` → `""` → `<time class="intel-date"></time>` empty.

**Detection:**
```bash
python3 -c "
import json
d = json.load(open('site/data/stories.json'))
missing = [s['story_id'][:40] for s in d['stories'] if 'generated_at' not in s]
print(f'Missing generated_at: {len(missing)}') if missing else print('All stories have generated_at ✓')
"
```

**Fix:** Run `scripts/ensure_generated_at.py` — copies document-level `generated_at` to every story missing it. Add to pipeline chain.

## Symptom 2: story-app.js Scope Fragility

**Root cause:** `story-app.js` uses a monolithic `init()` function with a massive template literal. Adding any new variable or function to the file's global scope silently breaks rendering. `catch(e){}` blocks swallow all errors with zero console messages.

**Safe operations:**
- Extending existing `||` fallback chains (e.g., `story.timestamp || story.date || story.generated_at`)
- NEVER adding new `const`/`let`/`function` declarations
- NEVER changing template literal expressions beyond existing variable references

**What breaks (proven v22.38):**
- Adding `const dataGenAt = data.generated_at || '';` → page stuck at "Loading…"
- Adding `function formatTimeAgo() { ... }` → page stuck at "Loading…"
- Changing `<time>${date}</time>` to `<time datetime="...">${formatTimeAgo(...)}</time>` → page stuck at "Loading…"

**Fix strategy:** Fix data at the pipeline level — add missing fields to stories.json rather than modifying story-app.js scope.

## Symptom 3: Story IDs Exceed URL Limits

**Root cause:** Telegram intel monitor (`cron 4e973ff20bf3`) generates story IDs from headlines, producing IDs 100+ characters. Example: `n21_multi_pillar__eu_21st_sanctions_package_90_banks_11_crypto_platforms_banned_lng_tanker_prohibition` — browsers truncate URLs, story page returns 404.

**Fix:** Added `[:80]` truncation in `intel_to_stories.py` at both story_id assignment points:
```python
story_id = (intel_story.get("story_id") or generate_story_id(headline, pillar))[:80]
```

## Symptom 4: Synthetic Flow Data ($5.0B defaults)

**Root cause:** `intel_to_stories.py` line 74: `amount_b = 5.0  # default`. Amount extraction regex `/\$(\d+\.?\d*)\s*[Bb]/` matches nothing in editorial bet text (which uses tickers, not dollar amounts).

**Fix:** Added asset-class-based amount mapping as fallback when no `$XB` pattern found:
```python
amount_map = {
    'defense': 12.0, 'commodities': 15.0, 'energy': 18.0,
    'tech': 25.0, 'equities': 20.0, 'crypto': 3.5,
    'bonds': 8.0, 'gold': 6.0, 'real_estate': 10.0,
}
```
