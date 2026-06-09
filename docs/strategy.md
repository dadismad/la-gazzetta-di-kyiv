# Strategy Framework

**Strategic direction, success metrics, paradigm pillars, and review cadence for Gazzetta di Kyiv.**

---

## MISSION

> Contradiction-first narrative intelligence. Track capital flows before they move prices.

## CORE PRINCIPLES

1. **Capital-first** — Every story must answer: "Where is the money going?"
2. **Contradiction over consensus** — The edge is where narratives diverge from reality
3. **Actionable, not academic** — Every story ends with a trade idea
4. **Freshness over completeness** — Timely partial intel > perfect late analysis
5. **Simple over complex** — "It's hard to create simple, but easy to create hard"

---

## SIX PARADIGM PILLARS

These are the structural narratives we track continuously. Every story, flow, and signal maps to one pillar.

| # | Pillar | Definition | Signal Sources | Story Count (active) |
|---|--------|-----------|----------------|---------------------|
| 1 | **china_ascendancy** | China's tech/industrial rise: semiconductors, 15th Five-Year Plan, patent leadership, AI autonomy | Web search, Telegram | 2 |
| 2 | **dollar_decline** | De-dollarization: BRICS currency, commodity settlement shifts, IMF COFER, central bank gold purchases | Web search, Telegram | 1 |
| 3 | **eu_fragmentation** | EU structural stress: defense spending divergence, migration, Eurobarometer, political fragmentation | Web search, Telegram | 1 |
| 4 | **abundance_tech** | Technology of abundance: fusion energy, space economy, AI compute, longevity science | Web search, Telegram | 5 |
| 5 | **blockchain_agentic** | Crypto/DeFi/Agentic economy: RWA tokenization, ETF flows, institutional adoption, stablecoin regulation | Web search, Telegram | 3 |
| 6 | **multi_pillar** | Cross-cutting: geopolitical events, macro regime shifts, commodity supply shocks, military conflicts | Telegram (primary), web search | 9 |

---

## SUCCESS METRICS (KPIs)

| KPI | Target | Current | Measurement |
|-----|--------|---------|-------------|
| **Stories active** | ≥ 15 | 12 | `stories.json` count |
| **New stories/day** | ≥ 5 | ~3 | Delta on `stories.json` |
| **Pillar coverage** | 6/6 pillars | 6/6 | Count of unique pillars in active stories |
| **Flow confidence** | ≥ 75% | 82% | `flows.json` aggregate_confidence |
| **Inflow/Outflow ratio** | 3:1+ | 11:1 | `flows.json` direction counts |
| **Data freshness** | < 2h | ~3h | File mtime of `stories.json` |
| **Pipeline success rate** | ≥ 95% | 100% (reported) | Cron `last_status` |
| **Deploy cadence** | 15m | 15m | Last deploy timestamp |
| **Site uptime** | 99%+ | 100% | HTTP 200 check |
| **Zero undefined** | 0 | 0 | `validate_stories.py` output |
| **Skills utilization** | > 50% | 28% | Active skills / total skills |
| **No failures > 4h** | 0 | ⚠️ X watchdog 5 days | Cron `last_status` |

---

## TARGET AUDIENCE

| Persona | Primary Need | Content Focus |
|---------|-------------|---------------|
| **Retail Trader** | Actionable trade ideas with entry/exit | Bet & Benefit, Track Record |
| **Institutional Investor** | Flow direction, conviction levels | Capital Flows, The Signal |
| **Geopolitical Analyst** | Narrative contradiction mapping | Stories, Source Registry |
| **Crypto Native** | Blockchain/agentic economy signals | Blockchain pillar stories |
| **Casual Reader** | What's moving markets right now | Hero section, Lead Story |

---

## COMPETITIVE POSITIONING

| Competitor | Strength | Our Edge |
|-----------|----------|----------|
| Bloomberg Terminal | Deep institutional data | Free, narrative-first, contradiction scoring |
| ZeroHedge | Breaking news speed | Structured: flow data + trade ideas, not just headlines |
| Kobeissi Letter | Macro analysis | Capital flow quantification, not just directional calls |
| Reddit r/wallstreetbets | Crowd sentiment | Institutional flow data, not retail noise |
| Twitter/X fin-twit | Real-time signals | Structured contradiction mapping, not just hot takes |

---

## GROWTH STRATEGY

### Phase 1: Stabilize (Current)
- ✅ Pipeline chain operational (60m cycle)
- ✅ Data validation (validate_stories.py)
- ✅ Freshness decay (decay_stories.py)
- ✅ Schema unification (paradigm_pillar)
- ✅ Russian translation (i18n)
- 🔲 Management dashboard
- 🔲 Alerting on failures
- 🔲 Git version control at canonical path

### Phase 2: Scale Content
- 🔲 15+ active stories at all times
- 🔲 2+ stories per pillar
- 🔲 Source diversity: Reddit, YouTube transcripts, RSS feeds
- 🔲 Automated translation pipeline (RU stories)
- 🔲 Content quality scoring (contradiction depth, actionability)

### Phase 3: Grow Audience
- 🔲 SEO optimization (sitemap, meta, structured data)
- 🔲 Newsletter / email digest
- 🔲 Social media automation (X, Telegram, Reddit — all operational)
- 🔲 Community engagement (Reddit comments, Telegram discussions)
- 🔲 Analytics: page views, time on site, story engagement

### Phase 4: Monetization (Future)
- 🔲 Premium tier: real-time intel, early access
- 🔲 API access: flow data for quant funds
- 🔲 White-label: narrative intelligence for institutions
- 🔲 Events/community: paid Telegram group, trading signals

---

## REVIEW & GOVERNANCE

| Review | Frequency | Owner | Method |
|--------|-----------|-------|--------|
| **Pipeline health** | Every 60m | pipeline_chain.sh | Automated: output validation |
| **Data freshness** | Every 30m | health-check | Automated: file age check |
| **Site availability** | Every 15m | deploy script | Automated: HTTP 200 check |
| **Dynamic indicators** | Every 15m | CEO overseer | Automated: hardcoded digit scan |
| **Strategic alignment** | Weekly | Operator (manual) | Review against KPIs |
| **Pillar coverage** | Weekly | Operator (manual) | Count stories per pillar |
| **Skill audit** | Bi-weekly | Operator (manual) | Check skill usage, archive orphans |
| **Full system audit** | Monthly | 3-persona focus group | Systems Architect, Data Engineer, SRE |
| **Strategy review** | Quarterly | Operator | Full strategy refresh |

---

## CURRENT STATE (2026-06-06)

| Layer | Status |
|-------|--------|
| **Pipeline** | ✅ Working: 12 stories, 12 flows, 82% confidence |
| **Deploy** | ✅ Every 15m to GCS |
| **Data quality** | ✅ validate_stories repairs 8/9 stories |
| **Schema** | ✅ Unified: paradigm_pillar on all stories |
| **Intel bridge** | ✅ Fixed: correct JSON key, 3 stories discovered |
| **i18n** | 🔄 Russian translation HTML done, data pipeline pending |
| **Dashboard** | 🔲 Not yet implemented |
| **Alerting** | 🔲 Not yet implemented |
| **Git** | 🔲 Init done, no push yet |
| **Skills orphans** | 🔲 72% unused |
