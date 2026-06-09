# Site Map — Gazzetta di Kyiv

> Every page, its purpose, URL path, navigation group, and data dependencies.

## 20 Pages Total

### Primary Product Pages (5)

1. **Stories** - /stories.html (priority 0.9, hourly) - Data: stories.json, stories_ru.json, living_stories.json, story_registry.json
2. **Flows** - /flows.html (priority 0.9, hourly) - Data: flows.json, flows_ru.json, stories.json
3. **Trades** - /trades.html (priority 0.9, hourly) - Data: stories.json, flows.json
4. **Signal** - /signal.html (priority 0.8, hourly) - Data: stories.json, intelligence_objects.json
5. **Track** - /track.html (priority 0.7, daily) - Data: stories.json, flows.json

### Home and Detail

6. **Home** - / (index.html, priority 1.0, hourly) - Masthead + hero + featured stories
7. **Story Detail** - /story.html (priority 0.8, hourly) - Loaded via JS from stories.json

### Content Pages

8. **Capital** - /capital.html (priority 0.6, weekly)
9. **About** - /about.html (priority 0.4, monthly)
10. **Research** - /research.html (priority 0.5, weekly)
11. **Data** - /data.html (priority 0.3, monthly)
12. **Geopolitics** - /geopolitics.html (priority 0.6, hourly)
13. **Markets** - /markets.html (priority 0.6, hourly)
14. **Wealth** - /wealth.html (priority 0.5, daily)
15. **Pleasure** - /pleasure.html (priority 0.4, weekly)

### Internal and Utility

16. **Operations** - /ops.html (priority 0.3, daily) - System health dashboard
17. **Dashboard** - /dashboard/index.html (priority 0.3, daily) - CEO management dashboard
18. **Contacts** - /contacts.html (priority 0.3, monthly)
19. **Cooperation** - /cooperation.html (priority 0.3, monthly)
20. **Privacy** - /privacy.html (priority 0.2, monthly)

### Special: variant-modern.html (experimental, not in nav)

## Navigation Structure

Masthead: Stories / Flows / Trades / Signal / Track
Footer: About / Research / Data / Contacts / Cooperation / Privacy
Sector sub-nav: Geopolitics / Markets / Wealth / Pleasure

## i18n Routes

en: /stories.html, /flows.html (default)
ru: /ru/stories/, /ru/flows/ (via i18n.js + i18n_ru.json + stories_ru.json)

## Static Assets

/styles.css (2143 lines), /styles-modern.css (25 lines)
/app.js (1713 lines), /i18n.js (103 lines), /story-app.js (218 lines), /sector.js (80 lines)
/media/*.jpg, /robots.txt, /sitemap.xml

## API Endpoints

/api/v1/home/*.json -> data/*.json (API-wrapped for external consumption)
