# JS Module: sector.js (80 lines)

> Sector photo roulette system for landing pages.

## Responsibilities

- SECTOR_PHOTOS map: sector -> Unsplash URL array
- Random photo selection on page load
- Lazy loading via Intersection Observer

## Sectors

geopolitics, markets, tech, wealth (each with 4 photo URLs)

## Implementation

```javascript
const SECTOR_PHOTOS = {
  geopolitics: [...],
  markets: [...],
  tech: [...],
  wealth: [...]
};
// Random selection + IntersectionObserver lazy loading
```
