# Component Catalog — Gazzetta di Kyiv

> UI components, JS modules, HTML templates, and DOM interaction patterns.

## JavaScript Modules

### app.js (1713 lines) — Core Application

| Section | Lines | Function |
|---------|-------|----------|
| Data fetching | 1-80 | getJSON(), getDataPath(), DATA_BASE, FLOWS_BASE |
| Story caching | 81-120 | STORIES_CACHE, capturedStoryIds |
| Story card rendering | 121-450 | renderStoryCard(), renderCapitalFlow(), renderSignal() |
| Flow visualization | 451-700 | renderFlows(), aggregateFlows(), flowChart() |
| Navigation state | 701-800 | nav routing, active pill, history API |
| Sector photos | 801-850 | SECTOR_PHOTOS map |
| Hero section | 851-1000 | renderHero(), leadStory(), heroNumbers() |
| Polling/realtime | 1001-1100 | FLOWS_POLL_INTERVAL, setInterval fetchers |
| i18n integration | 1101-1200 | lang switch, text replacement |
| Story detail routing | 1201-1400 | story detail modal, share buttons |
| Trade ideas | 1401-1600 | renderTradeCards(), betAndBenefit() |
| Signal dashboard | 1601-1713 | renderSignalDashboard(), tensionMeter() |

### i18n.js (103 lines) — Internationalization Runtime

- Detects language from URL path (/ru/ prefix)
- Sets i18n.lang property on window
- Loads i18n_ru.json key-value pairs
- Provides translate(key) function
- Switches data file paths (stories vs stories_ru)

### story-app.js (218 lines) — Story Detail Page

- Single story rendering from stories.json
- Contradiction display (they_say vs reality)
- Capital flow box rendering
- Trade idea card with entry/exit
- Share buttons (X, Telegram, Reddit, Facebook)
- Timeline/updates section

### sector.js (80 lines) — Sector Photo Roulette

- SECTOR_PHOTOS map with sector -> Unsplash URL arrays
- Random photo selection per page load
- Lazy loading with intersection observer

## CSS Architecture

### styles.css (2143 lines)

| Section | Lines | Content |
|---------|-------|---------|
| CSS Custom Properties | 1-40 | :root token definitions |
| Reset and base | 41-100 | Box-sizing, body, typography |
| Masthead | 101-250 | Header, logo, nav, shimmer |
| Hero section | 251-450 | Lead story, stats, CTA |
| Story cards | 451-800 | Card grid, tension, capital flow |
| Flow visualization | 801-1000 | Flow bars, direction indicators |
| Signal section | 1001-1200 | Signal cards, tension meter |
| Track section | 1201-1400 | Trade tracker, win/loss |
| Sector pages | 1401-1600 | Geopolitics, markets, wealth |
| Footer | 1601-1700 | Site footer, links |
| Mobile responsive | 1701-1900 | Media queries, breakpoints |
| Animations | 1901-2100 | Transitions, shimmer, hover |
| Print/variant | 2101-2143 | Print styles, modern variant |

### styles-modern.css (25 lines) — Experimental variant overrides

## HTML Templates

Each HTML page follows a consistent structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Meta, title, fonts: Playfair Display + Source Serif 4 + Inter -->
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="masthead">  <!-- Site title + nav -->
  <main>
    <section class="hero">    <!-- Lead story / page title -->
    <section class="container">  <!-- Primary content -->
  </main>
  <footer>                    <!-- Links + copyright -->
  <script src="app.js"></script>
  <script src="i18n.js"></script>
</body>
</html>
```

## DOM Patterns

| Pattern | Implementation | Used In |
|---------|---------------|---------|
| Story card | div.story-card with data-story-id | stories.html, index.html |
| Flow bar | div.flow-bar with width=projected/amount | flows.html |
| Signal card | div.signal-card with tension class | signal.html |
| Trade idea | div.trade-card with bet/benefit | trades.html, index.html |
| Hero numbers | div.hero-stats with dynamic values | index.html |
| Sector photo | img.sector-photo with lazy loading | sector pages |
