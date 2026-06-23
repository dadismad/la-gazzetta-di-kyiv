# Bug Patterns — v22.42

## Editorial Writer → Site Bridge Gap
**Symptom:** Website shows stale stories (hours/days old) while editorial writer generates fresh content.
**Root cause:** Editorial writer outputs to `data/publish/stories.json` (narrative format, no capital_flow dicts). `intel_to_stories.py` outputs to `data/stories.json` (with capital_flow dicts). `build_site.py` copies `data/` → `site/data/` → GCS. The editorial output was NEVER copied to `data/`, so it never deployed.
**Fix:** `scripts/sync_publish_to_site.py` as step 0.5 in `pipeline_chain.sh`. Copies `data/publish/*.json` → `data/` if publish version is newer.
**Detection:** `diff <(stat -f '%m' data/publish/stories.json) <(stat -f '%m' data/stories.json)` — if publish is newer, bridge is broken.

## Capital Flow Dict Mismatch
**Symptom:** `generate_flows.py` fails with `ValueError: max() arg is empty sequence`. Zero flows generated from fresh editorial stories.
**Root cause:** Editorial writer produces stories with `story_id, headline, they_say, reality, paradigm_pillar` but NO `capital_flow` dict. `generate_flows.py` requires `capital_flow` fields (direction, amount_b, asset_class, projected, pace_multiplier, confidence_pct). Editorial stories produce 0 flows.
**Fix:** Pipeline chain runs `intel_to_stories.py` after `sync_publish_to_site.py` — adds `capital_flow` dicts to stories before `generate_flows.py` consumes.
**Detection:** After pipeline, verify: `python3 -c "import json; d=json.load(open('data/stories.json')); print(d['stories'][0].get('capital_flow',{}).get('amount_b','MISSING'))"` — must return a number.

## fetchFlows() Homepage Guard
**Symptom:** Homepage `flowFreshness` empty, `heroConfidence` not populated, flow teaser shows "—".
**Root cause:** `if (byId('flowsList')) await fetchFlows()` at boot() line 1909. Homepage has `#flowsTeaserContent` not `#flowsList`. Guard fails → flows never load on initial page.
**Fix:** Remove guard — `await fetchFlows()` always runs. Render functions inside fetchFlows() check for own target elements.
**Detection:** Homepage must show "updated Xm ago" in flow teaser within 5s of page load.

## Duplicate hint* Teaser Code
**Symptom:** Homepage teaser containers showed "—" for all stats despite correct `populateTeasers()` existing.
**Root cause:** Two populator paths existed: (1) broken inline code targeting `hintStoriesCount`, `hintFlowsAmount` etc. — none of these IDs exist in HTML, (2) correct `populateTeasers()` targeting `teaserStoryCount`, `teaserFlowSub` etc. The broken code was a dead duplicate that silently failed.
**Fix:** Removed broken `hint*` code. Correct `populateTeasers()` called via `setTimeout(populateTeasers, 1500)`.
**Detection:** `document.getElementById('teaserStoryCount').textContent` must not be "—".

## SVG Mobile Scaling — Touch + Font
**Symptom:** SVG nodes unclickable at mobile, edge labels invisible, sub-labels illegible.
**Root cause:** `viewBox="0 0 1200 770"` scaled to 390px → nodes ~26×16px. Fonts at 7-8px. Single 768px media query.
**Fix:** 3-tier responsive breakpoints. `@media (hover:hover)` for hover. `:active` for touch. SVG text scaled up at mobile. Mobile filter bar replaces keyboard shortcuts. See `references/flow-nodes-mobile-audit-v22.42.md`.

## CSS-vs-HTML-Rewrite for JS-Populated Product Pages (June 2026)

**Pattern:** When restyling product pages where JS dynamically populates content (`.container-body`), prefer CSS class targeting over HTML rewrites.

**Why:** Product pages use JS functions (`appendStoryCard()`, `renderFlows()`, `renderTriangulation()`) that depend on specific element IDs, class names, and data attributes. Rewriting the HTML template risks breaking these bindings — orphaned function calls, missing target elements, silent render failures.

**Approach — CSS-only restructuring:**
1. Add `data-layer="intel"` or `data-layer="alpha"` to `<main class="product-page">` (low-risk attribute addition, no JS impact)
2. Write CSS rules targeting `.product-page[data-layer="intel"] .container` and `.product-page[data-layer="alpha"] .container`
3. Style existing classes (`.container`, `.container-header`, `.container-subtitle`, `.container-desc`, `.container-body`) rather than introducing new classes
4. The JS continues to work unchanged — it populates `.container-body` and the CSS handles the visual layer

**Result:** All 7 product pages restructured with a single CSS block + one-attribute HTML patch each. Zero JS breakage. Verified via `getComputedStyle()` showing `border-left: 3px rgb(59, 130, 246)` (Intel blue) and `3px rgb(212, 175, 55)` (Alpha gold).

**When to use HTML rewrites instead:** Only when the content structure changes (adding/removing elements, changing ID names, adding new interactive widgets). Pure visual restyling should always be CSS-only.

## Hover States on Touch Devices
**Symptom:** Node hover effects don't work on mobile. Legend hover doesn't fire on tap.
**Root cause:** All interactive states were `:hover`-only. Touch devices don't fire `:hover` reliably.
**Fix:** Wrap all hover rules in `@media (hover: hover) { ... }`. Add `:active` pseudo for touch feedback.
**Pattern:**
```css
.cn-node-group:active .cn-node-shape,
.cn-node-group.active .cn-node-shape { stroke-width: 2.5; }
@media (hover: hover) {
  .cn-node-group:hover .cn-node-shape { stroke-width: 2.5; }
}
```
