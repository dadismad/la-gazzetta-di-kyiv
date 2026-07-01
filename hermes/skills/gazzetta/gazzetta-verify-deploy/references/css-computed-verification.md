# Browser Computed-Style Verification (v32.1, June 2026)

## When to Use

After EVERY CSS or typography deploy. The Gazzetta site uses `cdn.tailwindcss.com` which injects styles AFTER the inline `<style>` block. Curl and grep see your CSS rules in the static HTML. The browser may see Tailwind's overrides. Only `getComputedStyle()` tells the truth.

## Mandatory Verification Block

Run this via `browser_console` after every CSS deploy:

```js
JSON.stringify({
  // Phase 8 typography
  bodyBg: getComputedStyle(document.body).backgroundColor,
  bodyFontSize: getComputedStyle(document.body).fontSize,
  bodyColor: getComputedStyle(document.body).color,

  // Card headlines (target article h3 specifically — sidebar h3s use different classes)
  cardH3FontSize: (function(){
    var el = document.querySelector('article h3.font-headline-md');
    return el ? getComputedStyle(el).fontSize : 'NO CARD H3 FOUND';
  })(),

  // Data font enforcement
  gapScoreFont: (function(){
    var el = document.querySelector('.gap-score');
    return el ? getComputedStyle(el).fontFamily : 'NO .gap-score';
  })(),

  // Pulse animation on high-GAP cards
  breakingPulse: (function(){
    var el = document.querySelector('article[data-gap-high="true"]');
    return el ? getComputedStyle(el).animationName : 'NO HIGH-GAP';
  })(),

  // Data leaks
  feedSourceLeaks: (document.body.innerHTML.match(/FEED_SOURCE/g)||[]).length,
  undefinedLeaks: (document.body.innerHTML.match(/undefined/g)||[]).length,

  // Share buttons
  totalShareButtons: document.querySelectorAll('[aria-label="Share intelligence setup"]').length,

  // Verified badges
  verifiedBadges: document.querySelectorAll('.text-emerald-400').length
})
```

## PASS Criteria

| Metric | Expected | Critical? |
|--------|----------|-----------|
| `bodyBg` | `rgb(10, 10, 15)` = #0A0A0F | YES |
| `bodyFontSize` | `13px` | YES |
| `bodyColor` | `rgb(230, 228, 224)` = #E6E4E0 | YES |
| `cardH3FontSize` | `14px` | YES |
| `gapScoreFont` | contains `JetBrains Mono` | YES |
| `breakingPulse` | `gapPulse` or contains `pulse` | YES |
| `feedSourceLeaks` | `0` | YES — raw DB key leak |
| `undefinedLeaks` | `0` | YES |
| `totalShareButtons` | matches card count | NO — informational |
| `verifiedBadges` | ≥ 2 (only cards with feed_source) | NO — depends on data pipeline |

## curl Blindness Trap

Curl verification (`grep -c "font-size:13px"`) WILL show the rule in the static HTML. This is a false positive if Tailwind CDN overrides it. The rule exists in the file, but the browser never applies it. Only `getComputedStyle()` reveals the override.

## Selector Precision Trap

`document.querySelector('h3')` picks the FIRST h3 on the page — which may be a sidebar label with class `font-label-xs` (11px), not a card headline with class `font-headline-md` (14px). Always target card h3s specifically: `document.querySelector('article h3.font-headline-md')`.
