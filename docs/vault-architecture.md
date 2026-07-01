# Sovereign Vault — Phase 2 & 3 Architecture Plan

Date: June 23, 2026 | Status: Phase 1 deployed, Phases 2-3 designed

---

## Phase 2: Deep Institutional Paper Trail

### Targets

| Source | Access Method | Format | Frequency |
|---|---|---|---|
| **Goldman Sachs Top-of-House** | Public research portal | HTML → text extraction | Weekly |
| **BlackRock Investment Institute** | Public blog + PDF briefs | HTML + PDF → text | Weekly |
| **Bridgewater Daily Observations** | Public summaries | HTML → text | Daily |
| **USPTO Patents** | USPTO Public API (free key) | JSON | Weekly |
| **WIPO Patents** | WIPO PATENTSCOPE API | JSON | Weekly |
| **J.P. Morgan Research** | Public briefs | HTML → text | Weekly |
| **Morgan Stanley Research** | Public briefs | HTML → text | Weekly |

### Architecture

```
scripts/
├── fetch_institutional.py    ← single script, per-source config
└── extract_pdfs.py           ← async PDF → text (pypdf or pdfplumber)

data/vault/pdfs/YYYY-MM/      ← raw PDFs + hashes
data/vault/patents/YYYY-MM/   ← patent JSON
```

**Script**: `fetch_institutional.py` — config-driven. Each source has a URL template + CSS selector for content. Headless requests via `requests` + `BeautifulSoup`. If blocked, falls back to ScraperAPI (free tier: 5,000 requests/month).

**Dedup**: SHA-256 hash of raw content before storage. Duplicate hashes are skipped.

**PDF extraction**: `extract_pdfs.py` runs asynchronously (background subprocess). Uses `pdfplumber` for text extraction. Writes clean text to `data/vault/pdfs/YYYY-MM/extracted/`. The ingestion pipeline reads these text files as new source items with `source_name: BLACKROCK` or `source_name: USPTO`.

**Patent classification**: CPC codes mapped to Gazzetta narratives:
- G06N → Compute Hegemony
- A61K → Longevity & Bioreality
- G06Q 40/00 → all finance-adjacent narratives
- C12N → Longevity & Bioreality

### Accounts Needed

| Account | Cost | Purpose |
|---|---|---|
| USPTO API Key | Free | Patent search (no rate limit issues) |
| ScraperAPI | Free tier (5K req/mo) | Fallback when institutional sites block VM IP |

---

## Phase 3: Dark Data — SEC Filings & Options Flow

### Targets

| Source | Access Method | Format | Frequency |
|---|---|---|---|
| **SEC Form 4** (Insider Trading) | SEC EDGAR Public API | JSON/XML | Daily |
| **SEC Form 13F** (Institutional Holdings) | SEC EDGAR Public API | JSON/XML | Quarterly (with daily check for new filings) |
| **SEC Form 8-K** (Material Events) | SEC EDGAR Public API | JSON/XML | Daily |
| **Dark Pool Prints** | Finra ATS data (free, delayed) | CSV | Daily |
| **Options Flow** | CBOE delayed quotes or Polygon.io free tier | JSON | Daily |

### Architecture

```
scripts/
├── fetch_sec_edgar.py        ← SEC EDGAR API client
└── fetch_options_flow.py     ← Options + dark pool data

data/vault/sec/YYYY-MM/       ← EDGAR filings JSON
data/vault/options/YYYY-MM/   ← Options flow data
```

**SEC EDGAR**: Full-text search API + CIK lookup. No API key required (public). Rate limit: 10 requests/second.

**Insider → Narrative matching**: Cross-reference Form 4 filings against tickers in `narratives.json`. If a narrative shows negative media sentiment but insiders are buying → spike GAP score.

**Options flow**: Track unusual options activity (volume/Open Interest ratio) on narrative tickers. High put/call ratio divergence against media consensus → GAP signal.

### Accounts Needed

| Account | Cost | Purpose |
|---|---|---|
| Polygon.io | Free tier (5 calls/min) | Options flow data (or use CBOE delayed) |
| — | Free | SEC EDGAR (no key required) |

---

## Integration Flow

```
┌───────────────────────────────────────────────────────────────┐
│                    GOVERNOR PIPELINE                          │
│                                                               │
│  [youtube]  [arxiv]  [bis]  [imf]  [fed]  [inst]  [patents]  │
│      │         │       │      │      │       │        │       │
│      └─────────┴───────┴──────┴──────┴───────┴────────┘       │
│                           │                                   │
│                    data/vault/                                │
│                    data/*_intel/                              │
│                           │                                   │
│                    [ingestion_triage.py]                       │
│                           │                                   │
│                    [contradiction_synthesizer.py]              │
│                           │                                   │
│                    stories.json                               │
│                           │                                   │
│              ┌────────────┼────────────┐                      │
│              │            │            │                      │
│        [build]    [telegram]     [deploy]                      │
└───────────────────────────────────────────────────────────────┘
```

All collectors: store raw → ingestion reads → synthesis scores → frontend renders. Decoupled. No collector failure blocks the pipeline.

---

## Implementation Sequence

| Order | Script | Effort | Depends On |
|---|---|---|---|
| 1 | `fetch_youtube.py` | ✅ Deployed | `YOUTUBE_API_KEY` |
| 2 | `fetch_arxiv.py` | ✅ Deployed | None |
| 3 | `fetch_bis.py` | 40 lines | None (public RSS) |
| 4 | `fetch_imf.py` | 40 lines | None (public RSS) |
| 5 | `fetch_fed_papers.py` | 40 lines | None (public RSS) |
| 6 | `fetch_institutional.py` | 120 lines | ScraperAPI key (optional) |
| 7 | `fetch_patents.py` | 80 lines | USPTO API key |
| 8 | `extract_pdfs.py` | 60 lines | None (pdfplumber) |
| 9 | `fetch_sec_edgar.py` | 100 lines | None (public) |
| 10 | `fetch_options_flow.py` | 80 lines | Polygon.io key (optional) |
