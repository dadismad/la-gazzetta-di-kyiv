# Mobile CSS Compatibility Policy (v23.16)

## Target browsers

Safari 14+, Chrome 90+, Firefox 88+. No IE11 support required, but `@supports` fallback blocks must exist.

## Required `@supports` blocks in styles.css

```css
/* ── MOBILE COMPATIBILITY ──
   Vendor prefixes for older iOS Safari (8-14), Android Browser,
   and IE10/11. Full autoprefixer pass recommended for build pipeline. */
@supports not (display: grid) {
  /* Grid fallback for IE11 / old Edge */
  .product-grid, .teaser-list, .flow-sector-grid,
  .side-hooks, .side-freshness, .side-tickers {
    display: -ms-flexbox;
    display: -webkit-flex;
    display: flex;
    flex-wrap: wrap;
  }
}
@supports not (display: flex) {
  /* Ancient browser fallback */
  .product-nav, .teaser-list, .side-hooks,
  .side-freshness, .masthead-inner {
    display: block;
  }
}
```

## Viewport meta tag

Must be present on all pages:
```html
<meta name="viewport" content="width=device-width,initial-scale=1"/>
```

## Touch targets

Minimum 40px, 44px recommended for mobile nav elements and product buttons.

## ES6+ usage

App.js uses ~692 ES6+ features (arrow functions, const/let, template literals, async/await). This is acceptable for Safari 14+ — no polyfills needed for the target range. Full autoprefixer pass on the build pipeline is the long-term solution for broad mobile support; manual `@supports` blocks cover the critical layout fallbacks until then.

## Usage

Ensure these blocks are present in `site/styles.css` before any deploy. They're verified via the `gazzetta-verify-deploy` structural checks (§4.5b).
