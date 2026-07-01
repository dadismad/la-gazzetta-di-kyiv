# Bulava SVG — Proportions & Heraldic Research (v22.5, June 2026)

## Historical Reference

- **Bohdan Khmelnytsky's bulava** (Hetman of Ukraine, 17th century): 902×2738px — ~1:3 head-to-handle ratio
- **Heraldic coat-of-arms** (Polish hetman crossed buławas): compact X-shaped display, heads outward
- Real bulavas have: spherical head, decorative collar, long slender shaft, handle bands, pommel base

## Current Implementation (site/index.html)

```html
<svg viewBox="0 0 14 38" fill="none">
  <!-- Handle shaft: y=18→35 (17 units) -->
  <line x1="7" y1="18" x2="7" y2="35" stroke="currentColor" stroke-width="1.8"/>
  <!-- Handle bands at y=21 and y=27 -->
  <!-- Pommel at y=34 -->
  <!-- Neck: y=14→18 -->
  <!-- Collar at y=13 -->
  <!-- Head sphere: cx=7, cy=8, r=5.5 -->
  <!-- Ornamental band at y=8 -->
  <!-- Spike: y=2.5→5 -->
  <!-- Finial at cy=1.5, r=1.5 -->
</svg>
```

Head ~14 units, handle ~22 units. Ratio ~1:1.6 (adapted for heraldic display).

## CSS

```css
.masthead-bulava { position: relative; width: 16px; height: 26px; }
.masthead-bulava svg { position: absolute; width: 12px; height: 26px; left: 2px; transform-origin: 50% 62%; }
.masthead-bulava svg:first-child { transform: rotate(-32deg); }
.masthead-bulava svg:last-child { transform: scaleX(-1) rotate(-32deg); }
/* Phone: width: 12px; height: 20px; svg width: 10px; height: 20px; */
```

## Anti-Pattern

DO NOT revert to old 20×24 viewBox with 4:1 head-dominant proportions. The user flagged this explicitly — mace head was too large, handle too short ("looks mixed up").
