# Asset Icon System (v23.21)

## ASSET_ICONS Map

Defined in `site/app.js` after `ASSET_BADGE_LABELS`. Each asset class maps to a Unicode symbol, an institutional color token, and a label.

```javascript
const ASSET_ICONS = {
  fx:           { symbol: '💱', color: '#B8860B', label: 'FX' },
  commodities:  { symbol: '🛢', color: '#059669', label: 'COMMODITIES' },
  crypto:       { symbol: '₿',  color: '#DC2626', label: 'CRYPTO' },
  equities:     { symbol: '📈', color: '#2563EB', label: 'EQUITIES' },
  fixed_income: { symbol: '🏛', color: '#6D28D9', label: 'SOVEREIGN' },
  defense:      { symbol: '🛡', color: '#374151', label: 'DEFENSE' },
  tech:         { symbol: '⚙',  color: '#7C3AED', label: 'TECH' },
  spx:          { symbol: '📊', color: '#2563EB', label: 'SPX' },
  btc:          { symbol: '₿',  color: '#F59E0B', label: 'BTC' },
  oil:          { symbol: '🛢', color: '#DC2626', label: 'OIL' },
  gold:         { symbol: '🥇', color: '#B8860B', label: 'GOLD' },
  bonds:        { symbol: '📜', color: '#6D28D9', label: 'BONDS' },
};
```

## Usage

```javascript
function assetIcon(ac) {
  const a = ASSET_ICONS[(ac || '').toLowerCase()] || ASSET_ICONS['equities'];
  return `<span class="asset-icon" style="color:${a.color}" title="${a.label}">${a.symbol}</span>`;
}
```

Returns an empty string fallback if no asset_class. Safe to call unconditionally.

## Teaser Card Integration

In `populateTeasers()` → story teaser rendering (line ~2274 of app.js):

```javascript
const cf2 = s.capital_flow || {};
const iconHtml = cf2.asset_class ? assetIcon(cf2.asset_class) : '';
return `<a href="..." class="teaser-item">${iconHtml}${probHtml}${amtHtml}${headline}...</a>`;
```

Icon appears before the conviction probability badge and amount. Color-coded per institutional token.

## Color Token Rationale

- `#B8860B` (gold) — sovereign/fiat value stores (FX, gold)
- `#059669` (green) — physical/real assets (commodities, oil)
- `#DC2626` (red) — high-volatility speculative (crypto, oil)
- `#2563EB` (blue) — broad equity markets
- `#6D28D9` (violet) — fixed income, sovereign debt
- `#374151` (slate) — defense, government-adjacent
- `#7C3AED` (purple) — tech, innovation sector

These colors are distinct from both the ALPHA gold (#B8860B) and INTEL slate (#0F172A) layer colors. They identify the asset class, not the editorial layer.

## Pitfalls

- The `asset_class` field must be populated in `capital_flow_raw` for the icon to render. Editorial writer stories may lack this field unless enriched at Stage 1.5.
- Never use `asset_class.toUpperCase()` as a fallback label in teasers — it produces raw uppercase strings that look unpolished. Use `ASSET_ICONS[ac].label` or `ASSET_BADGE_LABELS[ac]`.
- Adding a new asset class requires entries in BOTH `ASSET_ICONS` (icon + color + label) and `ASSET_BADGE_LABELS` (badge text). Keep them in sync.
