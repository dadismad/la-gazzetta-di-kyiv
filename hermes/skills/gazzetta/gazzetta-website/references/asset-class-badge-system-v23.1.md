# Asset Class Badge System (v23.1)

**Deployed: 2026-06-10. Color-coded per Bloomberg terminal standard.**

## Implementation

### JS (app.js — ASSET_BADGE_LABELS)
```js
const ASSET_BADGE_LABELS = {
  fx: 'FX', equities: 'EQUITIES', commodities: 'COMMODITIES',
  crypto: 'CRYPTO', fixed_income: 'SOVEREIGN', defense: 'DEFENSE', tech: 'TECH',
};
```

### Card template injection (livingCardHTML)
Insert before the sector category-tag:
```js
${cf && cf.asset_class ? `<span class="asset-badge ${cf.asset_class}">${ASSET_BADGE_LABELS[cf.asset_class] || cf.asset_class.toUpperCase()}</span>` : ''}
```

### CSS (styles.css)
```
.asset-badge { font-family: var(--sans); font-size: 8px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 1px 6px; border: 1px solid; }
.asset-badge.fx            { color: #1D4ED8; border-color: #1D4ED8; }  /* Blue */
.asset-badge.equities      { color: #059669; border-color: #059669; }  /* Green */
.asset-badge.commodities   { color: #B8860B; border-color: #B8860B; }  /* Gold */
.asset-badge.crypto        { color: #7C3AED; border-color: #7C3AED; }  /* Purple */
.asset-badge.fixed_income  { color: #DC2626; border-color: #DC2626; }  /* Red (Sovereign) */
.asset-badge.defense       { color: #B45309; border-color: #B45309; }  /* Amber */
.asset-badge.tech          { color: #0891B2; border-color: #0891B2; }  /* Cyan */
```

## Verification
```js
document.querySelectorAll('.asset-badge').length  // should match story count
```

## Anti-Patterns
- ❌ Do NOT use emoji in badges
- ❌ Do NOT show badge if capital_flow.asset_class is missing
- ❌ Do NOT use sector for badge color — always asset_class
