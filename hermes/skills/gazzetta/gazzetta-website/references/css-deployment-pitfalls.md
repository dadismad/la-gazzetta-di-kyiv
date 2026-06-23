# CSS Deployment Pitfalls (v26.2)

## CSS Duplicate Rule Trap

When a property is defined TWICE on the same selector — once early, once late in the stylesheet — the later rule wins by CSS cascade. The second occurrence may have leaked out of an `@media` block due to an orphaned `}`.

**Real case (June 2026):** `.masthead-name { font-size: 1.8em }` at line 116 was overridden by `.masthead-name { font-size: 3em }` at line 1080. The second rule was originally inside `@media (max-width: 600px)` but the `}` at line 1018 closed the block early, leaking the rule to global scope. Result: title was 45px instead of 27px, forcing nav links to wrap to a second line.

**Detection:**
```bash
# Find duplicate property assignments for any selector
grep -n '\.masthead-name\b.*font-size' site/styles.css
# If two lines appear → the later one wins. Fix: match values or scope properly.

# Check for orphaned } that prematurely close @media blocks
grep -n '^}' site/styles.css
# Trace brace matching near any suspicious global rules.
```

## CSS Hash → ALL HTML Files Chain

When editing `styles.css`, the browser loads the HASHED file referenced in each HTML page. The chain must be complete:

1. Edit `styles.css`
2. Hash: `shasum -a 256 styles.css | cut -c1-8`
3. Copy: `cp styles.css styles.NEWHASH.css`
4. Update reference in **ALL 20 HTML files** (not just index.html):
   `sed -i '' 's/styles\.OLDHASH\.css/styles.NEWHASH.css/g' *.html`
5. Deploy all HTML + both CSS files to GCS

**Skipping sub-pages means those pages load old CSS.** The user explicitly flagged this as a trust-breaking failure: "the site doesn't change even after you say you changed it."

**Verify post-deploy:**
```bash
# Must return exactly one hash, matching the latest deployed file
curl -s https://www.lagazzettadikyiv.com/stories.html | grep -o 'styles\.[a-f0-9]*\.css' | sort -u
```

Full list of HTML files currently using styles.css: index.html, stories.html, flows.html, signal.html, trades.html, track.html, event_horizon.html, flow-nodes.html, about.html, privacy.html, methodology.html, story.html, capital.html, data.html, geopolitics.html, markets.html, pleasure.html, sources.html, terms.html, wealth.html.

## Masthead Nav Link Wrapping

When nav links (INTEL/ALPHA/MENU) appear on a SEPARATE line below the title despite being in `.masthead-right` inside the masthead `<header>`:

**Checklist:**
1. `.masthead` has `flex-wrap: nowrap` (not `wrap`)
2. `.masthead-name` font-size is ≤ 1.8em (3em = 45px fills the entire width, forcing nav to wrap)
3. `.masthead-right` does NOT have `width: 100%` (which would force wrapping to a new line)
4. `.master-nav` has `display: none` — nav links should live in `.masthead-right` inside the masthead

**Verify with console (NEVER trust vision tools for layout):**
```js
JSON.stringify({
  mastheadFlexWrap: getComputedStyle(document.querySelector('.masthead')).flexWrap,
  mastheadNameFontSize: getComputedStyle(document.querySelector('.masthead-name')).fontSize,
  navOnSameLine: Math.abs(
    document.querySelector('.masthead-right').getBoundingClientRect().top -
    document.querySelector('.masthead-left').getBoundingClientRect().top
  ) < 5,
  mastheadBg: getComputedStyle(document.querySelector('.masthead')).backgroundColor
})
// Must show: nowrap, 27px (1.8em), true, rgb(255, 255, 255)
```
