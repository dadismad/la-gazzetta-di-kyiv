# CEO Self-Execution Prompt V2

Objective: eliminate recurrence of UI/management defects and enforce strict quality gates.

Requirements:
1) Narrative Focus must not repeat Top Narratives text.
2) Enforce light metallic-blue palette globally with hard overrides.
3) Enforce font sizes in 8–10px range on homepage UI elements.
4) Add 3-day support metrics per narrative:
   - capital flow volume estimate
   - asset price % change projection (3d)
5) CEO governance:
   - pre-deploy contract checks must fail deployment on violations.
   - watchdog verifies live endpoint and content render state.

Implementation steps:
- Patch `site/app.js` to generate distinct focus content and inject new 3-day metrics.
- Patch `site/styles.css` with global 8–10px caps and palette hard overrides.
- Add `ops/ui_contract_check.py` to validate no repeated focus content, font caps, and palette tokens.
- Run build, checks, commit, push, dispatch deploy, verify live.
