# Frontend Engineering Patterns (Phase A/B, June 2026)

## Post-Render DOM Injection (Source Attribution Footers)

When adding features to inline JS card templates (string concatenation), do NOT modify the template string. The concatenated `' + '<div>...' + '` chains are fragile — one misaligned closing tag breaks the entire card render.

Instead, use post-render DOM injection:

1. **Stamp data attributes on the `<article>` during template render:**
```js
'<article data-story-id="' + (s.story_id || '') + '" data-source-feed="' + (s.feed_source || '') + '" class="...">'
```
2. **Write a separate injection function that appends the feature after cards are in the DOM:**
```js
function injectSourceAttribution() {
    var articles = document.querySelectorAll('article[data-story-id]');
    for (var i = 0; i < articles.length; i++) {
        var card = articles[i];
        if (card.querySelector('.source-attribution-footer')) continue;  // idempotent
        var sourceData = card.getAttribute('data-source-feed');
        if (!sourceData || sourceData.trim() === '') continue;  // skip empty
        var footer = document.createElement('div');
        footer.className = 'source-attribution-footer mt-4 pt-2 border-t ...';
        footer.innerHTML = '...' + sourceData.toUpperCase().trim() + '...';
        card.appendChild(footer);
    }
}
```
3. **Fire deterministically** — use `DOMContentLoaded` + `readyState` check, never a custom event that may not fire:
```js
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    injectSourceAttribution();
} else {
    document.addEventListener('DOMContentLoaded', injectSourceAttribution);
}
```

## WCAG Contrast Compliance (Surgical, Not Blanket)

Structural gold (#D4AF37) serves branding — masthead, borders, dividers. Interactive gold must meet 4.5:1 AA minimum on white backgrounds.

**Approach: add a new token, swap only interactive elements.**

**In styles.css `:root`:**
```css
--gold-accessible: #B45309;  /* WCAG AA compliant (>4.5:1 on white) */
```

**In Tailwind CDN config (build_frontend.py / build_frontend_staging.py):**
```js
"gold-accessible": "#B45309",
```

**Swap targets:**
- Tab nav active state: `text-gold` → `text-gold-accessible`, `border-gold` → `border-gold-accessible`
- Tab nav hover: `hover:text-gold` → `hover:text-gold-accessible`
- Nav pills (capital values, counts): `text-gold-dim` → `text-gold-accessible`
- Read Dispatch toggle: `text-gold-dim` → `text-gold-accessible`

**Leave untouched:** masthead text, structural borders, gold rules — they use `text-gold` / `--gold`.

**PITFALL:** This project uses custom Tailwind tokens, not standard utility classes. `text-amber-700` resolves to nothing. Always use the existing token system.

## Divergence Map 3-Tier Severity Rendering

The `contradiction_gap` field is **0-100**, not 0-10. Do NOT apply thresholds designed for a 0-10 scale. Use left-border accents (not filled capsules) to preserve the zero-radius terminal aesthetic:

| Gap Range | Tier | Border | Text Color | Badge |
|-----------|------|--------|------------|-------|
| >= 65 | BREAKING | `border-l-2 border-crimson` | `text-crimson` | `bg-crimson/10 text-crimson` |
| 40-64 | ACTIVE | `border-l-2 border-gold-accessible` | `text-gold-accessible` | `bg-gold-accessible/10 text-gold-accessible` |
| < 40 | SETTLING | `border-l-2 border-gray-300` | `text-gold-dim` | `bg-slate-100 text-slate-600` |

Keep directional flow arrows in neutral structural gray (`text-on-surface-variant`) — don't cross tier color with direction signal.

**Implementation:**
```js
var tierInfo = c.gap >= 65 ? {label:'BREAKING', border:'border-l-2 border-crimson', text:'text-crimson', badge:'bg-crimson/10 text-crimson'} :
               c.gap >= 40 ? {label:'ACTIVE', border:'border-l-2 border-gold-accessible', text:'text-gold-accessible', badge:'bg-gold-accessible/10 text-gold-accessible'} :
                             {label:'SETTLING', border:'border-l-2 border-gray-300', text:'text-gold-dim', badge:'bg-slate-100 text-slate-600'};
```

## Methodology Panel (About View)

Two-sentence honest disclosure. No name-dropping (Soros, Taleb, Druckenmiller), no empty math blocks. Place in the About view header, before the Lefevre Filter details block:

> This platform measures the structural gap between financial media reporting and actual institutional capital migration. Dispatches are analyzed and scored based on the magnitude of divergence between qualitative consensus narratives and quantitative asset-class flow volumes; large contradiction gaps receive priority visibility on the ledger.

## Article Card Structural Boundary

Add `border-l-2 border-gold/30` to the outer `<article>` tag. If an inner wrapper also has a left border, strip it to avoid double-line artifacts. One clean structural anchor per card.

## Build Script Promotion Checklist

When promoting staging features to production:
1. Copy `build_frontend_staging.py` → `build_frontend.py`
2. Fix output path: `index_staging.html` → `index.html`
3. Copy `contradiction_synthesizer.py` to VM (not just the build script)
4. Rebuild locally, verify feature markers in output
5. Run `test_platform.py` — must be 102/102
6. SCP scripts to VM home dir, `sudo mv` + `chown` to `/opt/gazzetta-di-kyiv/scripts/`
7. Rebuild on VM, `gsutil cp` to GCS
8. Curl live domain to verify feature markers

**PITFALL — missing synthesizer promotion:** If you promote the build script but not the synthesizer, new stories generated by the VM governor will lack the new fields and the feature silently disappears after the next pipeline cycle.

## PITFALL: File Truncation via read_file/write_file

`read_file()` with pagination returns formatted output with line numbers (e.g., `1|content`). If this formatted output is written back with `write_file()`, the file becomes corrupted with embedded line numbers. Recovery: copy from a known-good sibling file (e.g., production build script) and re-apply patches. Always verify file line count after writes.

## PITFALL: Patch Tool Escape Drift with JS-in-Python Strings

The `patch` tool's escape detection fires on `\"` sequences in files containing JS string templates inside Python strings. When it reports "Escape-drift detected", fall back to `execute_code` with raw byte manipulation (`open(path, 'rb')` → `.replace(old_bytes, new_bytes)` → `open(path, 'wb')`).
