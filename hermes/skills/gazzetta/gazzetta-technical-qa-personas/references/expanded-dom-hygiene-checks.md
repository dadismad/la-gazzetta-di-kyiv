# QA Persona — Expanded DOM Hygiene Checks (v32.0+)

**Added:** June 2026 — from Phase 8 post-deploy focus group audit.
**Context:** 156/156 tests passed, pipeline flawless, but 17 UX bugs found. All were presentation-layer string leaks.

## New QA Checklist Items

Add these to the QA/Tester persona's scan after every deploy:

### Data Leak Scan
```js
JSON.stringify({
  // Raw DB keys in visible text
  feedSource: (document.body.innerHTML.match(/FEED_SOURCE/g)||[]).length,
  verifiedDispatch: (document.body.innerHTML.match(/VERIFIED_DISPATCH/g)||[]).length,
  // Icon accessibility
  exposedIcons: Array.from(document.querySelectorAll('.material-symbols-outlined'))
    .filter(s => !s.hasAttribute('aria-hidden') && s.textContent.trim()).length,
  // Light-mode classes on dark background (#0A0A0F)
  lightBg: document.querySelectorAll('.bg-gray-50, .bg-white, .bg-gray-100').length,
  lightText: document.querySelectorAll('.text-gray-400, .text-gray-500').length,
  // JS handler leakage
  jsLeaked: document.body.textContent.includes('setTimeout(function')
})
// PASS: all = 0 or false
```

### CSS Architecture Awareness

- The site has NO external stylesheet. ALL CSS is inline `<style>` in `build_frontend.py` → `index.html`.
- `public/styles.css` is a ghost file — never deployed.
- To verify CSS: `curl -sk $SITE | grep -c 'YOUR_RULE'` directly.
- Font sizes at desktop are controlled by Tailwind CDN defaults, not inline CSS media queries.
- Reference: `gazzetta-website/references/css-architecture-inline.md`

### Attribution Footer Visibility

- Check: `document.querySelector('.source-attribution-footer')?.getBoundingClientRect()`
- If height=0 or backgroundColor is transparent → invisible (light-mode classes on dark bg)
- Check computed style: `getComputedStyle(el).color` vs `getComputedStyle(el.parentElement).backgroundColor`
- Contrast ratio must be ≥4.5:1 for WCAG AA

### Capital Number Formatting

- All capital volume numbers must have `$` prefix
- Check: `Array.from(document.querySelectorAll('.capital-num')).filter(s => !s.textContent.startsWith('$')).length`
- PASS: 0

### Leaderboard Truncation

- No narrative names truncated mid-word
- Check: `Array.from(document.querySelectorAll('#gap-leaderboard span')).filter(s => /\w$/.test(s.textContent) && s.textContent.length > 3).map(s => s.textContent)`
- Names ending mid-word (e.g., "TECH CONVERGEN" instead of "TECH CONVERGENCE") indicate JS substring truncation
