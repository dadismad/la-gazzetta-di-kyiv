# Gazzetta CSS Architecture (v32.0+)

**Discovered:** June 2026 — Focus group audit revealed Phase 8 CSS rules deployed but not applying.
**Root Cause:** The site has NO external stylesheet. ALL CSS is inline.

## The Architecture

```
build_frontend.py (Python template)
  ├── <style> (line ~340) — ALL CSS rules live here
  ├── <script src="cdn.tailwindcss.com"> (line ~300) — utility classes at runtime
  ├── <script> (line ~814) — ALL JS logic, card rendering, injectSourceAttribution()
  └── Generates → public/index.html (single SPA, ~600KB)
                    │
                    └── gsutil cp → gs://www.lagazzettadikyiv.com/index.html
```

## Key Facts

1. `public/styles.css` is a GHOST FILE — exists locally but NEVER referenced by any HTML tag, NEVER deployed to GCS. Editing it has zero effect on the live site.

2. The CSS chain is: edit `build_frontend.py` → run `build_frontend.py` → deploy `public/index.html`. Single file. No hashes. No multi-file sync.

3. Tailwind CDN (`cdn.tailwindcss.com`) generates utility classes at runtime from the HTML class attributes. The inline `<style>` block overrides Tailwind defaults where needed.

4. **Desktop font-size trap:** The inline CSS only sets font sizes inside `@media (max-width:390px)`. At larger viewports, Tailwind CDN defaults win:
   - `.font-body-md` → Tailwind default ~16px (not the desired 13px)
   - `h3, .font-headline-md` → Tailwind default ~10px (not the desired 14px)
   - **Fix:** Add global-level font-size rules OUTSIDE any `@media` block

5. **Light-mode residue:** Line 342 has `body{background:#FAF9F6}` (light cream) but line 455 overrides with `style="background:#0A0A0F!important"`. This creates confusion — always use dark-theme tokens in new CSS rules.

6. **All hashed-asset procedures in `gazzetta-verify-deploy` are irrelevant** for CSS changes. No CSS hash chain, no multi-page CSS sync, no old hash cleanup. Just verify: `curl -sk $SITE | grep -c 'YOUR_CSS_RULE'`.

## Phase 8 CSS Rules (in inline `<style>`)

The following Phase 8 rules ARE deployed in the inline CSS (verified June 22, 2026 via CDN curl):
- `#7F1D1D` (burgundy) — 5 occurrences: border-left-color on BREAKING cards, decay-critical, gapPulse keyframes
- `gapPulse` animation — 6s ease-in-out on `article[data-gap-high="true"]`
- `JetBrains Mono` — 3 occurrences: `.font-mono-data`, `.gap-score`, `.capital-num`, `.ticker-mono`, `.price-mono`
- `decayPulse` — 4s on decay-critical fill

Rules that exist but don't target intended elements:
- Pulse on `article[data-gap-high="true"]` — individual cards pulse, but the BREAKING ZONE header div does not (user sees static zone header)
- JetBrains Mono classes defined but card HTML doesn't add them to data elements consistently

Rules that were never added:
- Emerald `#10B981` for allocation percentages — class defined nowhere
- Sticky radar at 768px — only at `@media (max-width:480px)`
- Desktop font-size overrides for body (13px) and h3 (14px)

## Verification Pattern

```bash
# Verify CSS rules are in the CDN HTML (NOT in a separate CSS file)
curl -sk "https://www.lagazzettadikyiv.com/" | grep -c "YOUR_TARGET_CSS_RULE"

# Verify font sizes are computed correctly (browser tool)
browser_console: JSON.stringify({
  bodyFont: getComputedStyle(document.body).fontSize,
  h3Font: getComputedStyle(document.querySelector('h3')).fontSize,
  monoUsed: getComputedStyle(document.querySelector('.gap-score')).fontFamily
})
```

## Common Mistakes

- Editing `public/styles.css` instead of `build_frontend.py` → no effect
- Adding font-size rules inside `@media (max-width:390px)` only → desktop stays on Tailwind defaults
- Using light-mode Tailwind classes (`bg-gray-50`, `text-gray-400`, `border-gray-100`) on #0A0A0F dark background → element becomes invisible
- Expecting hashed CSS deployment → there is no CSS file to hash
