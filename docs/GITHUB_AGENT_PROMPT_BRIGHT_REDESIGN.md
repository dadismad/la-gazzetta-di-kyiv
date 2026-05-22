# Prompt for GitHub Agent — Gazzetta di Kyiv Bright Redesign

You are upgrading the website for **Gazzetta di Kyiv**.

## Objective
Redesign the site into a **bright, premium, light-themed, sophisticated-cyberpunk** visual system while preserving data clarity and tactical readability.

## Design directives
1. **Color system**
   - Primary background: very light (off-white / pearl / mist)
   - Accent palette: light blue + gold
   - Optional cyberpunk edge accents: electric cyan micro-highlights (very restrained)
   - Keep contrast AAA for body text and data tables.

2. **Layout philosophy**
   - Use **divine proportions (golden ratio ~1:1.618)** for:
     - hero vs side summary width split
     - vertical rhythm for sections
     - card proportion and spacing scale
   - Target **info-to-emptiness ratio ≈ 1:3** (content occupies ~25%, whitespace ~75%).
   - Keep the page breathable and high-end editorial.

3. **Containers and components**
   - Containers should be **frameless** (no hard borders).
   - Use soft elevation, gradients, and subtle shadows.
   - Rounded corners medium-large.
   - Data cards should read as floating modules.

4. **Typography and hierarchy**
   - Elegant modern serif for headlines, clean sans-serif for body/data.
   - Distinct hierarchy for:
     - Narrative title
     - Numeric signal line
     - Dense analytical review
   - Improve line-length for long narrative reviews (optimal reading width).

5. **Pages to create**
   - Home page (narratives + source intelligence + methodology summary)
   - Contacts page
   - Cooperation page (partnership / institutional collaboration)
   - Privacy Policy page

6. **Data integration requirements**
   - Continue loading from:
     - `data/narratives.json`
     - `data/source_registry_ranked.json`
     - `data/representation_techniques.json`
   - Do not break existing automation pipeline.

7. **Narrative review visibility (critical)**
   - Written narrative reviews must be prominently visible on the home page.
   - Each narrative block must include:
     - mentions (24h)
     - intensity score
     - momentum
     - dense text interpretation
   - Make these readable and impossible to miss.

8. **Performance and maintainability**
   - Use semantic HTML/CSS and lightweight JS.
   - Keep dependencies minimal.
   - Keep build simple (static site output).

## Deliverables
- Updated `site/index.html` with new bright visual system.
- Additional pages:
  - `site/contacts.html`
  - `site/cooperation.html`
  - `site/privacy.html`
- Shared style file:
  - `site/styles.css`
- If needed, small JS helper file:
  - `site/app.js`
- Update nav links across all pages.
- Keep content and data fields aligned with current JSON schema.

## Acceptance criteria
- Visual style: bright, premium, light blue + golden sophisticated cyberpunk.
- Frameless containers, soft depth, strong readability.
- Narrative written reviews clearly visible and central to UX.
- Golden-ratio inspired structure evident in grid/spacing.
- Site remains auto-refresh compatible with existing cron/GitHub pipeline.
