# Masthead v2.1 — Machiavelli Sign + Crossed Bulavas

Enacted June 2026. Replaces the v2.0 caduceus + single bulava design.

## Layout

```
[Fox & Lion] La Gazzetta di Kyiv [Crossed Bulavas]
     ↑                                ↑
  .masthead-machiavelli          .masthead-bulavas
  20×40px SVG                    28×38px SVG
  color: var(--gold)             color: var(--gold)
```

## Left Symbol: Fox & Lion (Machiavelli Sign)

Machiavelli's most famous metaphor from The Prince, Chapter XVIII:
"A prince must be a fox to recognize traps, and a lion to frighten wolves."

The fox (cunning/prudence) and lion (strength/force) together represent the dual nature of effective rule — perfectly aligned with the contradiction-first editorial paradigm.

CSS class: `.masthead-machiavelli`
Container: 20×40px, flex-shrink: 0, color: var(--gold)

```html
<span class="masthead-machiavelli" title="Fox & Lion — prudence and strength" aria-hidden="true">
  <svg width="20" height="40" viewBox="0 0 20 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Fox (top) — facing right, cunning -->
    <path d="M3 16 Q3 8 7 7 L9 2 L11 7 Q11 10 11 12"
          stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M11 12 Q10 10 8 11 Q7 13 7 14" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
    <circle cx="8.5" cy="9" r="0.9" fill="currentColor" opacity="0.7"/>
    <path d="M11 13 Q14 14 14 16" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>
    <!-- Lion (bottom) — facing left, strength -->
    <path d="M16 30 Q16 23 12 22 Q8 21 6 24 Q4 26 3 28 Q2 30 4 32"
          stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="13.5" cy="25" r="4" stroke="currentColor" stroke-width="1.3"/>
    <circle cx="9.5" cy="26.5" r="1" fill="currentColor" opacity="0.7"/>
    <path d="M17 24 Q19 23 19 25" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>
    <path d="M6 27 Q4 26 3 28" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
    <line x1="10" y1="18" x2="10" y2="21" stroke="currentColor" stroke-width="0.8" stroke-linecap="round" opacity="0.4"/>
  </svg>
</span>
```

## Right Symbol: Crossed Bulavas

Two Hetman's ceremonial maces (bulavas) crossed at ±42° angles, symbolizing dual authority. A bulava (булава) is the traditional symbol of the Ukrainian Cossack Hetman — representing executive power and sovereignty.

CSS class: `.masthead-bulavas`
Container: 28×38px, flex-shrink: 0, color: var(--gold)

```html
<span class="masthead-bulavas" title="Crossed bulavas — Hetman's maces, dual authority" aria-hidden="true">
  <svg width="28" height="38" viewBox="0 0 28 38" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Bulava 1: bottom-left to top-right -->
    <g transform="translate(14,17) rotate(42) translate(-7,-19)">
      <line x1="7" y1="12" x2="7" y2="35" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
      <rect x="3" y="15" width="8" height="1.5" rx="0.75" fill="currentColor" opacity="0.45"/>
      <rect x="3.5" y="21" width="7" height="1.2" rx="0.6" fill="currentColor" opacity="0.35"/>
      <rect x="2" y="28" width="10" height="2.5" rx="1.25" fill="currentColor" opacity="0.35"/>
      <line x1="7" y1="8" x2="7" y2="12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
      <rect x="2.5" y="7" width="9" height="1.5" rx="0.75" fill="currentColor" opacity="0.45"/>
      <circle cx="7" cy="3" r="5" stroke="currentColor" stroke-width="1.4"/>
      <circle cx="7" cy="3" r="2" fill="currentColor" opacity="0.22"/>
      <line x1="3.5" y1="3" x2="10.5" y2="3" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>
      <circle cx="7" cy="-1.5" r="1.2" fill="currentColor"/>
    </g>
    <!-- Bulava 2: bottom-right to top-left -->
    <g transform="translate(14,17) rotate(-42) translate(-7,-19)">
      <line x1="7" y1="12" x2="7" y2="35" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
      <rect x="3" y="15" width="8" height="1.5" rx="0.75" fill="currentColor" opacity="0.45"/>
      <rect x="3.5" y="21" width="7" height="1.2" rx="0.6" fill="currentColor" opacity="0.35"/>
      <rect x="2" y="28" width="10" height="2.5" rx="1.25" fill="currentColor" opacity="0.35"/>
      <line x1="7" y1="8" x2="7" y2="12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
      <rect x="2.5" y="7" width="9" height="1.5" rx="0.75" fill="currentColor" opacity="0.45"/>
      <circle cx="7" cy="3" r="5" stroke="currentColor" stroke-width="1.4"/>
      <circle cx="7" cy="3" r="2" fill="currentColor" opacity="0.22"/>
      <line x1="3.5" y1="3" x2="10.5" y2="3" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>
      <circle cx="7" cy="-1.5" r="1.2" fill="currentColor"/>
    </g>
  </svg>
</span>
```

## CSS (v2.1)

```css
.masthead-bulavas {
  display: inline-flex; align-items: center;
  width: 28px; height: 38px;
  color: var(--gold);
  vertical-align: middle; flex-shrink: 0;
}
.masthead-bulavas svg { display: block; width: 28px; height: 38px; }

.masthead-machiavelli {
  display: inline-flex; align-items: center;
  width: 20px; height: 40px;
  color: var(--gold);
  vertical-align: middle; flex-shrink: 0;
}
.masthead-machiavelli svg { display: block; width: 20px; height: 40px; }
```

## Responsive Override (≤768px)

```css
.masthead-machiavelli svg, .masthead-bulavas svg { width: 12px; height: 22px; }
```

## Migration Notes

- Replaced `.masthead-caduceus` → `.masthead-machiavelli`
- Replaced `.masthead-bulava` → `.masthead-bulavas`
- Old CSS used absolute positioning + rotation tricks for crossed bulavas (two identical SVGs rotated ±32°). New approach uses a single SVG with two `<g transform="rotate()">` groups — cleaner, deterministic, no absolute positioning.
- The `templates/header.html` is the canonical source. `build_site.py` injects it into all `public/*.html` files. After updating the template, run `python3 scripts/build_site.py`.
- The RU version at `ru/index.html` is a static outlier — it had the old symbols baked into the HTML without sentinel markers. It was not updated by this change.
