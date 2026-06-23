# Vision Hallucination — Dark Bar (June 2026)

## Reproduction

Three consecutive vision calls (2× `browser_vision` + 1× `vision_analyze`) all hallucinated a "dark navigation bar at the top" with "white text" for INTEL/ALPHA/MENU links.

## DOM Ground Truth (browser_console — never lies)

```js
JSON.stringify({
  mastheadBg: getComputedStyle(document.querySelector('.masthead')).backgroundColor,
  // → "rgb(255, 255, 255)" — WHITE
  masterNavDisplay: getComputedStyle(document.querySelector('.master-nav')).display,
  // → "none" — HIDDEN
  navLinkColor: getComputedStyle(document.querySelector('.masthead-nav-link')).color,
  // → "rgb(139, 0, 0)" — DARK RED
  mastheadFlexWrap: getComputedStyle(document.querySelector('.masthead')).flexWrap,
  // → "nowrap"
  navOnSameLine: Math.abs(
    document.querySelector('.masthead-right').getBoundingClientRect().top -
    document.querySelector('.masthead-left').getBoundingClientRect().top
  ) < 5
  // → true — nav links in same row as title
})
```

## What Vision Models Said

| Call | Tool | Claim |
|------|------|-------|
| 1 | browser_vision | "dark navigation bar at the top... white text" |
| 2 | browser_vision | "dark-colored bar at the very top" |
| 3 | vision_analyze | "background color that is dark... links in white text" |

## Root Cause Hypothesis

The vision models appear to conflate:
- Browser chrome (address bar) with page content
- Thin gold borders (`2px solid #D4AF37`) as dark backgrounds at low resolution
- The `banner` ARIA role (which contains nav links) as a visually distinct bar

## Resolution

**NEVER trust vision tools for color or element presence claims.** Always supplement every `browser_vision` call with a `browser_console` `getComputedStyle()` check. The DOM is deterministic — vision is stochastic.
