# RSS Feed Registry — Gazzetta OSINT Collector

Last tested: 2026-06-09. All tested via `feedparser` with SSL verification disabled
(User-Agent: Mozilla/5.0 GazzettaBot/1.0).

## Working Feeds

| Feed | URL | Entries | Quality |
|------|-----|---------|---------|
| ECB Press Releases | `https://www.ecb.europa.eu/rss/press.html` | 15 | High — official central bank announcements, Lagarde speeches, financial stability reviews |
| Reuters Business (Google News) | `https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB` | 55 | High volume — broad financial coverage, but mixed with non-market news |

## Defunct / Empty Feeds

| Feed | URL | Issue |
|------|-----|-------|
| IMF News | `https://www.imf.org/en/News/RSS` | Parses but returns 0 entries |
| IMF Blog | `https://www.imf.org/en/Blogs/RSS` | Parses but returns 0 entries |
| Federal Reserve | `https://www.federalreserve.gov/feeds/pressreleases.xml` | HTTP 404 |
| World Bank | `https://blogs.worldbank.org/en/voices/feed` | HTTP 404 |
| BIS | `https://www.bis.org/press/rss.htm` | HTTP 404 |

## Notes

- Google News RSS is the most reliable general financial feed but its content varies — not all entries are market-relevant (celebrity news, general business, etc.)
- ECB is the only official institutional feed that works reliably
- IMF/Fed/BIS feeds appear to have moved or changed URL structure — worth re-checking periodically
- SSL verification is disabled in the collector (`ctx.check_hostname = False`) because some RSS endpoints have certificate mismatches
