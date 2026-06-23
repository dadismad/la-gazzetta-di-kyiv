# Shimmering Masthead — CSS Technique (v22.3+)

The canonical masthead name treatment for Gazzetta di Kyiv. Replaces flat color fill + visible stroke with a breathing gradient interior and a nearly invisible gold hairline.

## Core CSS

```css
.masthead-name {
  font-family: var(--display);
  font-size: var(--φ-lg);
  /* Shimmering Tyrian purple — 5-stop gradient with lustre */
  background: linear-gradient(
    135deg,
    #990024 0%,        /* Deep Tyrian — imperial base */
    #B8305A 28%,       /* Burgundy lustre — the "shimmer" highlight */
    #990024 50%,       /* Return to base at midpoint */
    #7B2D5E 72%,       /* Violet shadow — depth */
    #990024 100%       /* Full cycle back to Tyrian */
  );
  background-size: 200% 200%;      /* Double-size for animation range */
  -webkit-background-clip: text;    /* Clip gradient to text shape */
  background-clip: text;
  color: transparent;               /* Hide flat color, show gradient fill */
  /* Hairline gold — 0.4px at 45% opacity. Deliberately nearly invisible. */
  -webkit-text-stroke: 0.4px rgba(245, 215, 110, 0.45);
  text-stroke: 0.4px rgba(245, 215, 110, 0.45);
  white-space: nowrap;
  animation: shimmer 8s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

## Design Rationale

- **Shimmering interior**: The gradient cycles through 3 tones of Tyrian purple (deep base, burgundy lustre, violet shadow) diagonally. The 8-second animation shifts background position so the purple "breathes" — like light moving across velvet. Not flashy, not obvious. Someone glancing at it sees "purple." Someone looking twice notices the depth.
- **Invisible gold lining**: At 0.4px with 45% opacity, the gold stroke is below conscious perception for most viewers. But the eye *feels* warmth at the edges — a glow without a visible source. This is the sophistication: the gold is registered, not seen. "Only a greedy eye can spot it."
- **No drop shadow, no glow filter**: The effect comes from the gradient's internal contrast, not from layered CSS effects. Keeps rendering light and avoids the "Photoshop bevel" look.

## Iteration History

| Version | Fill | Stroke | Issue |
|---------|------|--------|-------|
| v20.4 | `#C8ECF8` (sky blue) | None | User: too generic |
| v20.21 | `#C8ECF8` (sky blue) | `1.5px #F5D76E` | Brighter blue, gold lining added |
| v22.2 | `#990024` (flat Tyrian) | `1.5px #F5D76E` | Fiorentina Viola-inspired. User: good direction |
| v22.3 | Gradient (5-stop) | `0.4px rgba(245,215,110,0.45)` | User: "shimmering purple, lining so thin only a greedy eye" |

## Pitfalls

- **Sub-pixel stroke rendering**: 0.4px strokes render differently across browsers. Chrome rounds up to 0.5px; Safari may alias. The 0.5px fallback is acceptable — the key is that it's a hairline, not a border.
- **`background-clip: text` + animation performance**: The 8-second shimmer is GPU-light (only `background-position` shifts) but avoid shorter cycles — faster animations with `background-clip: text` can trigger repaint storms on low-power devices.
- **Do NOT add `text-shadow`**: It competes with the gradient's internal depth and creates a muddy "glow" effect. The luminosity comes from the gradient's own highlight stops, not from a shadow.
