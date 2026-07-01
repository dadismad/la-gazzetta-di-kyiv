# Onboarding Prohibition (v23.16)

## Rule

**No welcome modals, onboarding tooltips, first-visit overlays, or tutorial popups** on any Gazzetta di Kyiv page (EN or RU). Institutional traders and professional analysts find these degrading to credibility.

## What to remove on sight

- `<div id="onboardingOverlay">` — first-visit tooltip with "Welcome to La Gazzetta di Kyiv"
- Any `<div>` or `<section>` with class/matching: `onboarding`, `welcome-modal`, `getting-started`, `first-visit`, `dismiss-overlay`
- Any JS that triggers on `!localStorage.getItem('gazzetta_onboarded')`
- Any `setTimeout(() => showWelcome(), ...)` patterns

## The ONLY acceptable overlay

The **lead-gen gate** (blur filter + "🔓 Unlock Full Signal →" gold button on strategic recommendations) is acceptable — it's a monetization mechanism, not a welcome message. It gates actionable trade intelligence behind a Telegram subscription, which is a product feature, not a tutorial.

## Verification

```bash
# EN site
curl -sk https://www.lagazzettadikyiv.com/ | grep -ci 'onboarding\|welcome.*gazzetta\|getting.started\|dismiss.*modal'
# Must print: 0

# RU site
curl -sk https://www.lagazzettadikyiv.com/ru/ | grep -ci 'onboarding\|welcome.*gazzetta\|getting.started\|dismiss.*modal'
# Must print: 0
```

## History

- June 2026: Found "Welcome to La Gazzetta di Kyiv" tooltip in `site/ru/index.html` (lines 435-448). Removed. EN site was clean. Added to `gazzetta-verify-deploy` §9 as a permanent post-deploy check.
