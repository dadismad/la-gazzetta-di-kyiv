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

3. **Containers and components**
   - Containers should be **frameless** (no hard borders).
   - Use soft elevation, gradients, and subtle shadows.
   - Rounded corners medium-large.

4. **Pages to create**
   - Home page
   - Contacts page
   - Cooperation page
   - Privacy Policy page

5. **Data integration**
   - `data/narratives.json`
   - `data/source_registry_ranked.json`
   - `data/representation_techniques.json`

6. **Critical visibility**
   - Written narrative reviews must be prominent and central.

## Deliverables
- `site/index.html`
- `site/contacts.html`
- `site/cooperation.html`
- `site/privacy.html`
- `site/styles.css`
- optional `site/app.js`
