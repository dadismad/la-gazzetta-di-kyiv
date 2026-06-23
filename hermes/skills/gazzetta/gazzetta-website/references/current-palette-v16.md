# Gazzetta di Kyiv — Current Palette (Salon Privé, v16)

Adopted June 2026 after four iterations. The correct casino aesthetic: dark room, white surfaces, gold accents, burgundy danger.

```css
--paper:    #0F1629;   /* Midnight navy — the room background */
--white:    #FFFFFF;   /* Pure white — cards and content surfaces */
--bg-tertiary: #1A2240;

--gold:     #D4AF37;   /* 24K gold — all accents, borders, highlights */
--gold-dark:#B8960F;
--gold-pale:rgba(212,175,55,0.08);

--sky:      #2A3F6E;   /* Deep navy blue — secondary structural elements */
--sky-pale: rgba(42,63,110,0.08);

--red:      #8B0000;   /* Deep burgundy — danger, stops, VIP rope */
--red-hover:#A00000;
--green:    #2E7D32;   /* Emerald felt — success, inflows, conviction */

--ink:      #E8ECF2;   /* Platinum white — body text on dark surfaces */
--ink-light:#8899B4;
--ink-muted:#5A6A84;
--ink-card:       #1A1D28;  /* Deep ink — headings on white cards */
--ink-card-light: #5A5F6E;  /* Grey — card body text */

--divider:       #2D3555;  /* Navy divider for dark surfaces */
--divider-light: #E8E8EC;  /* Light divider for white card surfaces */
```

Masthead: dark navy (#1F3A5F) background, gold (#D4AF37) publication name, white secondary text, gold 2px bottom border. No fleur-de-lis. Bulava SVG in white.

## Palette Anti-Patterns (What Failed)

- ❌ Emerald green as primary accent — reads as eco/wellness, not wealth
- ❌ Chrome/metallic bright backgrounds — looks like a car showroom, not a casino
- ❌ White-dominant with red lines — lacks depth, feels like a hospital with red tape
- ❌ Teal-navy background — too close to dark-mode dashboard, not posh
- ❌ Brass/gold that's too muted (#C9A84C) — must be REAL gold (#D4AF37)
- ✅ Midnight navy + pure white cards + 24K gold accents = the formula

## Card Pattern (v16)

Cards are collapsed by default. Only the asset claim pill, category tag, and headline are visible. The entire card-body div has an onclick toggle that adds/removes `.expanded` on the parent `.card`. The `.card-detail-hidden` wrapper contains summary, detail (THEY SAY/REALITY), capital flow block, and THE PLAY — all hidden via `max-height: 0; overflow: hidden; opacity: 0` until expanded.

Layout kept dense (5px padding, 5px card gaps, 10px layout padding) to maximize stories above fold while the collapsed format prevents information overload.

## THE ANCHOR (v16)

Simplified to two lines per asset: ticker + price + directional arrow on line one, key level + conviction on line two. Removed: asset name, regime badge, ATR, volume percentile, gamma wall contracts, level notes. Crypto signal rows (stablecoin supply, exchange netflow, funding rate) remain as a single compact block below.

## Previous Palette History (for context)

- v12: Warm gold (#C8A44E) + cream (#FEFCF5) + sky blue (#4A8FCC) — original newspaper broadsheet. Too warm, not casino.
- v13: Teal-navy (#0F2027) + emerald (#00B894) — "Glass Floor." Too dark-mode, not posh.
- v14: Chrome (#E8EDF5) + brass (#C9A962) — too bright, not casino.
- v15: White dominant (#F8F9FA) + red (#C62828) + dark blue (#1F3A5F) — not sophisticated enough.
