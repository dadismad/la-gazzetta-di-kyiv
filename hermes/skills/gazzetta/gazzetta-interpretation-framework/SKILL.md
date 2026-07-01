---
name: gazzetta-interpretation-framework
description: Multi-perspective interpretation framework for decoding ambiguous user design requests. Use BEFORE implementing when user uses metaphorical/abstract language about design, layout, or visual identity — "constellation and star systems," "divine proportions," "not squared but without frames," etc. Run a 4-persona focus group to interpret the request before any code changes.
version: 1.0.0
category: gazzetta
---

# Gazzetta di Kyiv — User Request Interpretation Framework

## When to Use

Any time the user describes design/layout/visual changes using metaphorical, abstract, or poetic language. These requests are ambiguous by nature — the user is describing a *feeling* or *gestalt*, not a CSS specification. DO NOT implement directly. ALWAYS run the interpretation framework first.

## Step 0: Multi-Perspective Interpretation (MANDATORY)

Before implementing any design change, spawn a focus group with these 4 personas interpreting the user's words:

### Persona 1 — Mathematical Aesthetician
Translates "divine proportions," "fractal," "golden ratio" into specific CSS measurements. Produces exact pixel values using φ (1.618). Answers: what specific grid, spacing, and sizing?

### Persona 2 — Information Architect  
Translates "make the user open what he needs first," "user oriented one short sentence approach." Produces container names that are benefit-oriented sentences, not structural labels. Answers: what should each container be called?

### Persona 3 — Minimalist Purist
Translates "background colour white everywhere, other colours should only be used for other." Audits every element for color purity violations. Produces a revised palette and violation checklist.

### Persona 4 — Futurist/Innovator
Reads the entire message as a unified vision. Finds 2-3 external design references that match. Answers: what does this remind me of? What existing designs feel like this?

## Output Format

The focus group must produce:
1. Multi-perspective consensus: what the user ACTUALLY wants
2. Points of disagreement and resolution
3. Specific CSS/HTML changes needed
4. Ranked priority (MUST/SHOULD/COULD)
5. Risks and anti-patterns

## Anti-Patterns

- ❌ Accepting any design decision without focus group validation first. ALWAYS run the interpretation framework before implementing metaphorical/abstract requests.
- ❌ Dismissing the user as "wrong" when they insist on a direction the focus group rejected. The user can override any focus group consensus. When this happens, implement what the user asked for AND encode the specific override in the skill so future sessions know the corrected direction. Document: "Focus group said X, user overrode to Y, implement Y."
- ❌ Removing all sub-component fills — focus group validated this destroys card readability. Soften, never remove. Even on pure white backgrounds, subtle fills (0.02-0.06 alpha) maintain visual hierarchy.

## Proven Interpretations

| User Saying | Decoded Meaning |
|---|---|
| "divine proportions" | Golden ratio φ=1.618 for spacing, sizing, typography cascade |
| "constellation and star systems" | 2-column staggered grid, not rigid column. Organic spacing. Lead star (full-width) with orbiting bodies |
| "not squared but without frames" | No borders. φ-radius corners. Subtle box-shadow. Generous negative space for container differentiation |
| "white everywhere" | #FFFFFF body + #FFFFFF cards + #FFFFFF masthead + #FFFFFF containers. Pure white everywhere. No exceptions. Differentiate containers via thin 1px #E5E7EB borders and subtle box-shadows (0 2px 12px rgba(0,0,0,0.06)), not background color contrast. Directional colors (green/red/gold/blue) remain for signal encoding only. The user INSISTS on this — focus group veto on pure white is overridden. |
| "one short sentence approach" | Container names with verbs, benefit-first, user-oriented |
| "contemporary luxury crime way" | [PENDING INTERPRETATION — run focus group before implementing] |
