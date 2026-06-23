# Gazzetta case: width-stretch nav image + live refresh verification

## Context
User requested:
1) Image integrated in top nav container (Geopolitics / Markets / Wealth / Pleasure).
2) Recalibration to stretch by width, not by height.
3) Site refresh with updated info visible in containers.

## Durable takeaways
- "Fill container" and "stretch by width" are different intents.
  - Fill/crop intent -> `background-size: cover`.
  - Width-stretch intent -> `background-size: 100% auto`.
- For text over patterned images, add subtle readability chips/backgrounds to avoid legibility regressions.
- Live verification must check deployed CSS and populated data containers, not local files only.

## Practical verification pattern
1. Confirm target container on live page is correct (same selector edited locally).
2. Confirm deployed CSS contains intended sizing rule (`100% auto` for width-stretch mode).
3. Confirm info containers are populated on live page (non-placeholder content visible).
4. If deployment lag exists, re-check until marker appears before declaring success.

## Related operational note
When scheduled website refresh pipeline is blocked by a quality gate, data container refresh may require explicitly rerunning payload preparation + audit steps before redeploy verification.
