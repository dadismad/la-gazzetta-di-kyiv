# CEO Design Upgrade Package — Gazzetta di Kyiv

## Objective
Create a self-managing website upgrade program that audits the site to fine detail, benchmarks against top financial/news competitors, and applies controlled iterative design refinements aligned with brand and usability constraints.

## Target Style
- Light / white base with metallic-blue cyberpunk accents.
- Thin typography (lighter weights), refined editorial feel.
- Smaller visual density:
  - Global typography scale reduced by ~40–60%.
  - Container paddings/margins reduced by ~40–65%.
  - Overall module footprint ~2–3x smaller than current baseline.
- Strict uniqueness:
  - No repeated wording across narrative containers.
  - Context/action text per card must be non-duplicative.
- Proportions guided by divine-ratio heuristics (~1.618):
  - Major layout split near 62/38.
  - Heading/body scale progression aligned to phi-like ratios.

## Color System (Golden-standard 4-color palette)
1. Base light: `#F7FAFF`
2. Primary metallic blue: `#3E6FAE`
3. Deep anchor navy: `#10233F`
4. Accent cyber-glow: `#6BB6FF`

Usage rules:
- Keep WCAG-friendly contrast.
- Reserve accent for interaction and highlights.
- Avoid adding extra decorative colors.

## Competitor Benchmark Set
Use benchmark references for typography rhythm, hierarchy, and container density:
- Financial Times (layout rhythm)
- Bloomberg (information hierarchy)
- Reuters Markets (clarity/compactness)
- The Economist (editorial seriousness)

## CEO Program Responsibilities
1. Audit current build artifacts and CSS/JS semantics.
2. Benchmark against competitor references (public HTML/CSS signals).
3. Generate machine-readable diff recommendations.
4. Apply safe transformations to local design tokens/CSS.
5. Re-run validation guards (retail language + no quant front-page drift).
6. Publish status JSON with score, blockers, fixes, ETA.

## Quality Gates
- Front page must remain narrative-first for retail users.
- No quant-heavy terminology on homepage.
- No duplicate context/action paragraphs in cards.
- Palette limited to approved 3–4 colors.
- Layout ratio and font density within target thresholds.

## Delivery Artifacts
- `data/design_upgrade_audit.json`
- `data/design_upgrade_plan.json`
- `data/design_upgrade_result.json`
- Updated `site/styles.css` and (if needed) `site/app.js`
