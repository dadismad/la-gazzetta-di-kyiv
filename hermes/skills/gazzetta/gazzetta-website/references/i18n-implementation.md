# i18n Implementation Recipe — Static GCS Site

Pattern for adding multi-language support to a static HTML+JS site deployed to GCS with JSON data files.

## Architecture

```
User clicks lang button → localStorage.set → page reloads
  → i18n.init() reads localStorage → loads i18n_XX.json
  → app.js getDataPath() returns language-specific JSON file
  → app.js render functions use i18n.t() for inline labels
  → Static HTML gets data-i18n attributes processed
```

## Files Needed

| File | Purpose |
|------|---------|
| `i18n.js` | Lightweight i18n module: detectLang, loadTranslations, applyTranslations, switchLang |
| `i18n_ru.json` | Translation key-value pairs (122 keys for full coverage — v22.15) |
| `index.html` | Add `<script src="./i18n.js"></script>` BEFORE app.js. Add `data-i18n="key"` to all static text elements. Add `onclick="i18n.switchLang('XX')"` to language buttons. |
| `app.js` | Dynamic data paths: `getDataPath()` returns `_ru` suffix when lang=ru. All inline labels use `i18n.t('key', 'fallback')`. |
| `translate_content.py` | Pipeline script: reads stories.json → translates key fields via LLM API → writes stories_ru.json |
| `pipeline_chain.sh` | Add translate step after generate_flows, before build_site |

## i18n.js Key Design

- IIFE pattern: `(function() { ... })()`
- `detectLang()`: localStorage → navigator.language → 'en' default
- `loadTranslations(lang)`: fetch `i18n_XX.json` (skip for 'en')
- `applyTranslations()`: walks `[data-i18n]` elements, sets textContent
- `switchLang(lang)`: sets localStorage, loads translations, applies, reloads page
- Exposes: `window.i18n = { lang, translations, t(key, fallback), switchLang, init }`
- Auto-init: `i18n.init()` called at end of file

## app.js Integration Points

1. **Data paths**: `const DATA_BASE = './data/stories'; function getDataPath() { return DATA_BASE + (window.i18n && i18n.lang === 'ru' ? '_ru' : '') + '.json'; }`
2. **Inline labels**: Replace ALL hardcoded English strings with `i18n.t('key', 'fallback')`. Must cover: CAPITAL FLOW, THE PLAY, tension tiers, share buttons, flow descriptors, story count.
3. **Data loading**: Use `getDataPath()` and `getFlowsPath()` in fetch calls instead of hardcoded paths.

## i18n_ru.json Required Keys

Static HTML keys: site_title, site_description, masthead_tagline, hero_headline, hero_subtitle, hero_cta, hero_stories, hero_capital_tracked, hero_active_positions, hero_open_exposure, hero_flow_confidence, container_stories_title, container_stories_desc, container_flows_title, container_flows_desc, container_flows_footer, container_anchors_title, container_anchors_subtitle, container_anchors_desc_prefix, container_signal_title, container_signal_subtitle, container_signal_desc, container_signal_footer, container_track_title, container_track_subtitle, container_track_desc, footer_kyiv.

App.js inline keys: flow_inflows, flow_outflows, flow_projected, flow_further_inflow, flow_further_outflow, flow_confidence_pct, flow_normal_pace, capital_flow_label, the_play_label, share_copy, share_x, share_facebook, share_telegram, share_reddit, tension_max, tension_high, tension_building, tension_consensus, confidence_high, confidence_medium, confidence_low, pdr_label, pdr_regime_passive, pdr_regime_active, pdr_regime_neutral, anchor_note_key_levels, anchor_note_pdr, story_status_breaking, story_status_new, story_status_active, story_status_developing, story_status_background, buy, sell, watch, conviction_HIGH, conviction_MED, conviction_LOW, pos_accumulating_1, pos_accumulating_2, pos_accumulating_3, pos_distributing_1, pos_distributing_2, pos_distributing_3, pos_hedging_1, pos_hedging_2, pos_hedging_3, pdr_regime_passive, pdr_regime_active, pdr_regime_neutral.

## Common Pitfalls

1. **Missing script tag**: `<script src="./i18n.js"></script>` must appear BEFORE `<script src="./app.js">` in index.html
2. **i18n.init() never called**: The IIFE must end with `i18n.init();` — without this, no translations load
3. **CDN caches old i18n.js**: After deploy, verify with `curl -s 'https://storage.googleapis.com/BUCKET/i18n.js' | grep 'i18n.init'`. If missing, delete from GCS and re-upload with `Cache-Control: no-store`.
4. **Race condition**: app.js renders before i18n finishes loading translations. Inline labels show English on first paint, Russian on subsequent loads. Minor UX issue for static sites.
5. **Missing translation keys**: If `i18n_ru.json` doesn't have a key used by `i18n.t()`, the English fallback shows. Always verify key coverage.
7. **i18n.t() evaluated at definition time (v22.15)**: Calling `i18n.t()` inside const declarations (e.g., `const LABELS = { x: i18n.t('key','fallback') }`) evaluates once at script parse time. The const never updates on language switch. Store `{key, fallback}` objects instead and translate at render time. See `positionLabel()` — translates `POSITION_VARIANTS[idx].key` at every call via `i18n.t(v.key, v.fallback)`.
8. **Missing data-i18n attributes**: The i18n system only replaces text on elements with `data-i18n="key"`. Missing attributes = permanent English. The v22.15 audit found 16 elements without attributes. Verify with: compare `(await fetch(url, {cache:'reload'}).then(r=>r.text())).match(/data-i18n=/g).length` vs expected count for the HTML.

## Verification Checklist

- [ ] `i18n.js` on GCS has `i18n.init()` call at end of file
- [ ] `i18n_ru.json` on GCS is valid JSON with 61+ keys
- [ ] `index.html` has `<script src="./i18n.js"></script>` before app.js
- [ ] `index.html` has EN/RU buttons with `onclick="i18n.switchLang('XX')"`
- [ ] `index.html` has `data-i18n` attributes on all static text elements
- [ ] `app.js` uses `getDataPath()` and `getFlowsPath()` in fetch calls
- [ ] `app.js` uses `i18n.t()` for ALL inline labels (no bare English strings in HTML templates)
- [ ] Click RU → page reloads → hero headline in Russian
- [ ] Click RU → page reloads → container titles in Russian
- [ ] Click RU → page reloads → `i18n.t('capital_flow_label')` returns Russian
- [ ] `stories_ru.json` exists on GCS
- [ ] `translate_content.py` integrated into `pipeline_chain.sh`
