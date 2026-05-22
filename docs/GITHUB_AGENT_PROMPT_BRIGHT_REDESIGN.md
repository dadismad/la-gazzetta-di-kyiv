# GitHub Agent Prompt — Full Bright Redesign (Gazzetta di Kyiv)

You are the GitHub coding agent responsible for redesigning and hardening the production website for **Gazzetta di Kyiv**.

## 1) Brand + strategic intent
Gazzetta di Kyiv is a narrative intelligence publication for mature, socially engaged professionals and investors who need short-to-medium horizon tactical context from geopolitical, macro, policy, and market narratives.

The site must project:
- clarity under noise
- institutional confidence
- analytical sophistication
- restrained cyberpunk edge (not gamer aesthetics)

## 2) Mandatory visual direction
Create a **bright, light-colored** interface with:
- base tones: pearl white / cloud / mist
- primary accents: light blue family
- premium accents: soft gold family
- tiny restrained hints: electric cyan accents

Design language:
- frameless containers (no hard borders)
- soft elevation and atmospheric shadows
- rounded cards with elegant spacing
- subtle gradients and highlights
- high readability over ornamentation

## 3) Composition constraints (strict)
- Use divine proportions (golden ratio 1:1.618) for major layout splits and card rhythm.
- Global information-to-emptiness ratio target: **1:3**.
- Keep line lengths readable for analytical text.
- Preserve fast scan path from top-level regime snapshot to deep narrative interpretation.

## 4) Required pages
Implement/upgrade these static pages:
1. `site/index.html` — primary intelligence dashboard
2. `site/contacts.html`
3. `site/cooperation.html`
4. `site/privacy.html`

All pages must share:
- unified header/nav/footer
- responsive layout
- consistent typographic scale
- same color and token system

## 5) Data integration (must not break)
The site must continue consuming:
- `data/narratives.json`
- `data/source_registry_ranked.json`
- `data/representation_techniques.json`

Do not break current automation pipeline that regenerates these files.

## 6) Critical product UX requirements
### A) Written narrative reviews are first-class
On homepage, make written reviews highly visible and central.
Every narrative module must include:
- narrative name
- mentions (24h)
- intensity score
- momentum
- dense analytical text review

Do not hide this in a collapsed area by default.

### B) Source intelligence table
Render sources sorted by accessibility class (e.g. `public_json`, `public_rss`, others), then by descending score.
Keep source description visible.

### C) Representation techniques section
Show top techniques with:
- technique name
- evidence count
- adoption priority
- implementation note

## 7) Technical constraints
- Static site only (simple HTML/CSS/JS).
- Keep dependencies minimal or zero.
- Maintain performance and readability.
- Keep code modular:
  - `site/styles.css`
  - `site/app.js`
  - semantic HTML pages

## 8) Accessibility + quality bar
- Strong contrast for body text and table content.
- Keyboard navigable nav links.
- Avoid tiny text below 14px for critical content.
- Responsive from mobile to desktop.

## 9) Deliverables
- Updated files for all required pages.
- A polished `styles.css` implementing the visual system.
- Updated `app.js` integrating all live data sections.
- Nav consistency and cross-linking.
- No regression in live data rendering.

## 10) Acceptance checklist
- [ ] Bright light theme with blue-gold palette implemented
- [ ] Frameless sophisticated containers with subtle cyberpunk feel
- [ ] Golden-ratio-informed structure clearly present
- [ ] 1:3 information-to-emptiness feel achieved
- [ ] Written narrative reviews prominently visible
- [ ] Contacts/Cooperation/Privacy pages complete
- [ ] Source table sorted by accessibility
- [ ] Representation techniques visible
- [ ] Compatible with current automation and data JSON files

If tradeoffs are required, prioritize: readability > trustworthiness > elegance > novelty.
