# La Gazzetta di Kyiv — Monetisation Plan & Integration Strategy

Date: June 23, 2026 | Status: Pre-launch | Target launch: July 2026

---

## 1. Revenue Architecture

### Revenue Streams

| # | Product | Pricing | Target Segment | Est. ARPU |
|---|---|---|---|---|
| 1 | **Gazzetta Pro** | $199/mo or $1,990/yr (17% discount) | Professional macro traders, family offices | $2,000/yr |
| 2 | **Institutional License** | $2,500–$5,000/mo per firm (up to 10 seats) | Hedge funds, macro desks, sovereign wealth teams | $30,000–$60,000/yr |
| 3 | **API Access** | $999/mo | Quantitative funds, systematic macro, risk desks | $12,000/yr |
| 4 | **Telegram Premium** | $49/mo | Retail-adjacent macro traders, Telegram-native users | $588/yr |
| 5 | **Weekly Contradiction Briefing** | Free | All — lead generation, email capture, Pro funnel | $0 (lead gen) |

### Freemium Feature Matrix

| Feature | Free | Pro ($199/mo) | Institutional ($2,500/mo) |
|---|---|---|---|
| **The Stream** | 24h delayed, GAP scores visible, trade setups blurred | Real-time, full trade setups, all tiers visible | Real-time, full access |
| **The Gap (Contradictions)** | GAP scores visible, analysis collapsed | Full Media vs Market analysis expanded | Full + raw data export |
| **Tactical Bets** | Narrative names + GAP only | Full panels: catalyst, flow, vectors, spillover graph | Full + spillover API endpoint |
| **The Ledger** | Top 5 capital flows only | Full sortable table + CSV export | Full + API access |
| **Macro Dossiers** | Structural thesis text only | Thesis + live FRED/CFTC data embeds | Thesis + data + analyst annotation layer |
| **Telegram Broadcast** | Tier 3 Macro Lens only | Tier 2 Radar + Tier 3 Macro Lens | Tier 1 Tactical Bets + Tier 2 + 3 |
| **Method / About** | Full access | Full access | Full access |
| **Spatial Canvas (v3)** | — | — | Exclusive |

### Revenue Projection (Conservative, Year 1)

| Tier | Subscribers | Annual Revenue |
|---|---|---|
| Pro | 50 | $100,000 |
| Institutional | 5 firms | $150,000 |
| API | 10 | $120,000 |
| Telegram Premium | 100 | $58,800 |
| **Total ARR** | | **$428,800** |

Break-even on infrastructure (~$200/mo GCS + LLM API) requires 2 Pro subscribers. All tiers are high-margin (cost is fixed infrastructure, not per-user).

---

## 2. Technical Architecture: Client-Side Feature Gating

### Principle

The frontend is served as static HTML from GCS + Cloud CDN. There is no application server. Feature gating happens entirely client-side via JavaScript, with a thin authenticated Cloud Run function for premium content delivery.

### Why Client-Side?

- **No SSR required**: The platform is a static SPA. Adding server-side rendering would require migrating off GCS or adding a compute layer in front — both unnecessary at this scale.
- **Lean**: Clerk + Stripe are drop-in SaaS. Cloud Run is one 50-line Python function. No database migrations, no session state, no Redis.
- **Secure enough for the threat model**: The primary concern is free users accessing Pro trade setups. Premium content is truncated in the static HTML; full content is fetched via authenticated API call.

### Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│ build_frontend│────▶│  GCS / CDN   │────▶│  User Browser  │
│   .py        │     │ (static HTML) │     │  (client JS)   │
└──────────────┘     └──────────────┘     └───────┬────────┘
                                                   │
                                    ┌──────────────┴──────────────┐
                                    │                             │
                              Free User                     Pro User
                                    │                             │
                          Truncated preview                Fetch full content
                          + "Upgrade to Pro" CTA           from /api/pro/
                                    │                             │
                                    │                    ┌────────┴────────┐
                                    │                    │  Cloud Run      │
                                    │                    │  /api/pro/      │
                                    │                    │  Validates JWT  │
                                    │                    │  Reads GCS      │
                                    │                    │  Returns full   │
                                    │                    │  trade setup    │
                                    │                    └────────────────┘
```

### Paywall Surface Area

| Page / Element | Free Experience | Pro Experience |
|---|---|---|
| **Hero section** | "Start your 7-day free trial" CTA (burgundy button) | No CTA. Pro badge in header. |
| **TIER 1 story cards** | Headline + GAP score visible. Trade setup replaced with: "GAP 82 — Contradiction detected. Upgrade to Pro to unlock trade setup." | Full trade setup: Entry, Stop, Target, conviction, alpha trigger. |
| **Contradiction Alert cards (GAP ≥ 80)** | Headline + GAP score + first sentence of thesis. Remainder truncated: "Upgrade to Pro for full Contradiction Alert analysis." | Full Media vs Market comparison, trade setup, dossier context links. |
| **Tactical Bets panels** | Collapsed state only — narrative name + GAP + story count. No expand. | Full expand: catalyst, flow, trade vectors, spillover map. |
| **The Ledger table** | Top 5 rows visible. Rows 6+ replaced with blurred overlay: "Unlock full Capital Ledger — $199/mo." | Full table, sortable, searchable, CSV export. |
| **Macro Dossier pages** | Structural thesis text. Data sections (FRED/CFTC) replaced with: "Upgrade to Pro for live institutional data." | Thesis + live data + auto-updating charts. |
| **Navigation header** | Transparent. | "PRO" badge in gold next to wordmark. Institutional: "INSTITUTIONAL" in burgundy. |

### DOM Security Rule

For all premium content, the static HTML emits a **truncated preview only**. The full content is never present in the DOM for free-tier users — not behind CSS blur, not in a hidden div, not in a data attribute. The `data-pro-content` attribute contains a story ID (not the content), used by authenticated JS to fetch from `/api/pro/`.

Example:
```html
<!-- Free + Pro users see this (always safe) -->
<div class="trade-setup" data-pro-content="story_n21_geopolitics_kuwait">
  <span class="gap-badge burgundy">GAP 82</span>
  <p class="preview">Structural dislocation detected between media consensus on Kuwaiti infrastructure and actual capital deployment patterns.</p>
  <div class="pro-cta">
    <a href="/upgrade" class="btn-burgundy">Upgrade to Pro — $199/mo — to unlock full trade setup</a>
  </div>
</div>
```

Pro users: JS detects `pro` tier from Clerk → fetches `POST /api/pro/ { story_id: "story_n21..." }` → Cloud Run validates JWT, fetches full content from `stories.json` on GCS → injects into DOM.

Free users: JS detects `free` tier → shows truncated preview + CTA. No API call.

### Cloud Run Function Spec (`/api/pro/`)

**Endpoint**: `POST /api/pro/`
**Auth**: Clerk JWT in `Authorization: Bearer <token>` header
**Request body**: `{ "story_id": "story_n21_geopolitics_kuwait" }`
**Response**: `{ "trade_setup": { "entry": ..., "stop": ..., "target": ..., "conviction": "HIGH", ... }, "media_consensus": "...", "market_reality": "..." }`
**Source**: Reads `gs://www.lagazzettadikyiv.com/data/stories.json`, filters by story_id, returns premium fields.
**Validation**: JWT must have `sub` claim + `tier` metadata (`pro` or `institutional`). Stripe subscription status verified via Stripe webhook (Clerk syncs subscription metadata).

**Cost**: Cloud Run free tier includes 2M requests/month. At 50 Pro users × 100 page loads/day = 5,000 requests/day = 150,000/month — well within free tier.

---

## 3. Monetisation UX Integration

### Upgrade Flow

```
Free User lands on Stream
  → Sees 3-step manifesto + Contradiction Index + story cards
  → Clicks TIER 1 card (GAP 82)
  → Card expands, shows truncated preview + burgundy CTA button
  → "Upgrade to Pro — Start 7-Day Free Trial"
  → Redirect to Stripe Checkout (hosted by Stripe — no PCI burden)
  → Payment complete → Clerk syncs subscription → page refreshes with Pro tier
  → TIER 1 card now shows full trade setup
  → Welcome email: "Your Pro terminal is live. Here's what to do first..."
```

### Retention Mechanics

| Mechanic | Trigger | Action |
|---|---|---|
| **7-day trial ending** | Day 5 of trial | Email: "Your trial ends in 2 days. Here's what you've unlocked this week." (personalized: top GAP stories viewed, narratives followed) |
| **High-GAP alert** | GAP ≥ 80 detected | Free users: "A Contradiction Alert fired — but you can't see it. Upgrade to Pro." (email + site banner) |
| **Weekly briefing** | Every Monday 09:00 Kyiv | Free newsletter: top 3 contradictions, GAP leaderboard, Pro CTA. Pro newsletter: full briefing + personalized narrative watchlist. |
| **Inactive Pro user** | 14 days no login | Email: "Your terminal has been watching. Here's what you missed." (summary of top contradictions since last visit) |
| **Annual renewal** | 30 days before expiry | Email: "Your Pro annual subscription renews soon. Here's your value report." (stories viewed, alerts received, narratives tracked) |

### Stripe Integration

- **Products**: 3 Stripe Products (Pro Monthly, Pro Annual, Institutional Annual)
- **Coupon**: `LAUNCH20` — 20% off first year for first 100 subscribers
- **Free trial**: 7 days on Pro Monthly and Pro Annual
- **Institutional**: Custom quote flow → manual invoice via Stripe Invoicing
- **API Access**: Separate Stripe Product, no trial, immediate activation
- **Telegram Premium**: Stripe Payment Link (simplest — no auth integration needed; manual Telegram username whitelist)

---

## 4. Launch Timeline

| Phase | Timeline | Actions |
|---|---|---|
| **Pre-launch** | Now – July 1 | Design implementation (Bento Grid), paywall integration, Clerk + Stripe setup, Cloud Run deployment |
| **Soft launch** | July 1 – 15 | Free tier live. Telegram channel promoted. Invite-only Pro trials (10 users). Collect feedback. |
| **Public launch** | July 15 | Public Pro subscriptions open. LAUNCH20 coupon active. Reddit + X distribution initiates. |
| **Institutional** | August 1 | Institutional landing page. Direct outreach to 20 target funds. Custom demos. |
| **API Access** | August 15 | API documentation published. Developer portal. |

---

## 5. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| **DOM scraping of premium content** | Pro subscribers lose exclusivity | Truncated previews in static HTML; full content only via authenticated `/api/pro/` |
| **Stripe/Clerk outage** | Pro users see free-tier experience | Graceful degradation: cached tier in localStorage, retry on next page load. Users never locked out. |
| **Free tier too generous** | No conversion pressure | Free tier is 24h delayed + truncated. Real-time data is Pro-only. TIER 1 trade setups are the primary conversion trigger. |
| **Telegram Premium cannibalizes Pro** | Users buy $49/mo instead of $199/mo | Telegram Premium only gets Tier 1 alerts on mobile. Pro gets the full terminal: all 4 tabs, dossiers, data export, search. Telegram is a lead-in, not a replacement. |
| **Institutional sales cycle too long** | No institutional revenue in Year 1 | Self-serve Pro + API Access carry Year 1. Institutional is Year 2+. Pro is the bridge. |

---

*End of Monetisation Plan*
