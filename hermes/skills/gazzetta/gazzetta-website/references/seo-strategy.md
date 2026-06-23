# SEO Strategy — Multi-Page Static GCS Site (June 2026)

## Required Artefacts

| Artefact | Required | Notes |
|----------|----------|-------|
| `robots.txt` | ✅ | `User-agent: *` → `Allow: /` → `Sitemap: https://www.lagazzettadikyiv.com/sitemap.xml` |
| `sitemap.xml` | ✅ | Pipeline-generated; includes all pages + stories + RU alternates |
| `<link rel="canonical">` | ✅ | Per-page canonical URL |
| `<link rel="alternate" hreflang="en/ru">` | ✅ | Static tags in `<head>`, not JS-only |
| Open Graph tags | ✅ | `og:title`, `og:description`, `og:url`, `og:image`, `og:type=website` |
| Twitter Card | ✅ | `twitter:card=summary` |
| Schema.org JSON-LD | ✅ | `Organization` on every page; `CollectionPage` per product |
| `<title>` + `<meta description>` | ✅ | Unique per page |

## URL Structure

Clean directory-style URLs via GCS `MainPageSuffix: index.html`:
```
/                    → index.html (hints lobby)
/stories/            → stories/index.html
/flows/              → flows/index.html
/trades/             → trades/index.html
/signal/             → signal/index.html
/track/              → track/index.html
/ru/                 → ru/index.html (Russian)
/ru/stories/         → ru/stories/index.html
```

## Pipeline Integration

Add to `pipeline_chain.sh` (after build_site, before deploy):
1. `python3 scripts/generate_sitemap.py` — reads stories.json, generates sitemap
2. `python3 scripts/add_seo_headers.py` — injects canonical, hreflang, OG, JSON-LD into HTML `<head>`
3. `python3 scripts/validate_seo.py` — validates artefacts; exit 1 if critical failures

## Free Validation Tools

- W3C Validator (validator.w3.org/nu/)
- html-validate (npm) — HTML best practices, meta, canonical
- broken-link-checker (npm) — internal link validation
- Google Rich Results Test — schema.org validity
