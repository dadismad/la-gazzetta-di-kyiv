# JS Module: i18n.js (103 lines)

> Internationalization runtime for bilingual support.

## Responsibilities

1. Language detection from URL path (/ru/ prefix)
2. Setting window.i18n.lang property
3. Loading i18n_ru.json translation key-value pairs
4. Data path resolution (stories vs stories_ru)

## API

```javascript
window.i18n.lang          // 'en' or 'ru'
window.i18n['key']        // Translated string by key
getDataPath()             // Returns stories[_ru].json path
getFlowsPath()            // Returns flows[_ru].json path
```

## Assumptions

- Must load before app.js
- Language is determined by URL, not by user preference
- All translation keys exist in both EN (hardcoded) and RU (i18n_ru.json)
- Data files use _ru suffix pattern
