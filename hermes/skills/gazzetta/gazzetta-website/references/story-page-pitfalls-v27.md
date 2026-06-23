# Story Detail Page Pitfalls (v27.2, June 2026)

Discovered during the June 12, 2026 full audit focus group.

## story-app.js Missing Script Tag

**Symptom:** Story detail page (`story.html?id=N`) stuck on "Loading intelligence report…" forever. Body length ~11KB.

**Root cause:** `story.html` had no `<script src="./story-app.HASH.js"></script>` tag. The story rendering logic lives in `story-app.js`, but the HTML never loaded it.

**Fix:** Add `<script src="./story-app.HASH.js"></script>` to `story.html` (after `app.HASH.js`). The `build_hashed_assets.py` script handles hash rewriting.

**Verification:** `grep 'story-app' story.html` must show the current hashed filename.

---

## renderMultiPersona() Scope Bug

**Symptom:** Story detail page shows "Failed to load intelligence report." No visible JS error in console (error caught by try/catch wrapper).

**Root cause:** `renderMultiPersona()` (line 145 in story-app.js) references `t` (i18n translator function), but `t` is defined as a `const` inside `buildHTML()` — not accessible from the sibling function. Calling `t('multi_persona_label', ...)` throws `ReferenceError: t is not defined`.

**Diagnosis technique:** Manually replicate the init() logic step by step via `browser_console`. If each step succeeds in isolation but the full init fails, the bug is in the template rendering (`buildHTML` or `renderMultiPersona`).

**Fix:** Pass `t` as a parameter:
```js
function renderMultiPersona(story, t) { ... }
// Call site:
${renderMultiPersona(story, t)}
```

**Verification:** Navigate to `story.html?id=ANY_VALID_ID` and check `bodyLen > 15000` and `!!document.querySelector('.intel-report')`.

---

## Inline Script Missing Opening Tag

**Symptom:** Raw JavaScript code visible as text on the rendered page.

**Root cause:** The `patch()` tool can silently drop `<script` opening tags during batch file operations. The closing `</script>` remains, but without the opening tag, all JS code between renders as visible text.

**Fix:** Always `tail -10` HTML files after patching. If inline JS code blocks are missing `<script>` openers, add them back.

---

## calcContradictionScore Using Wrong Data Source

**Symptom:** All 317 stories show identical "CONSENSUS 30/100" or "BUILDING 50/100" regardless of actual contradiction.

**Root cause:** `calcContradictionScore()` recalculates from `they_say`/`reality`/`capital_flow` fields. When those fields are empty (70 stories have no reality text), the baseline score of 30 stays unchanged.

**Fix:** Use the JSON `contradiction_score` field directly — it contains pipeline-authored scores (47-75 range) from the database:
```js
const jsonScore = story.contradiction_score;
if (typeof jsonScore === 'number' && jsonScore >= 0 && jsonScore <= 100) {
  return jsonScore;
}
// Fall back to recalculation only when field is absent
```

**Verification:** On stories page, `document.querySelector('.tier-badge')?.textContent` should show varied scores like "BUILDING 50/100", "HIGH TENSION 63/100", "MAX TENSION 75/100" — not all identical.
