# Focus Group — June 22, 2026
## Portfolio Manager ($5B AUM) + Skeptical Reuters Journalist

### Portfolio Manager: 4.4 → 5.2/10 (marginal)

**What improved:** Forward Declarations concept validated. Alpha trigger framing ("market prices X, capital shows Y") is structurally sound.

**What failed:**
1. **Tiering broken** — All stories showed SETTLING even at GAP 95. Frontend CSS had BREAKING/ACTIVE/SETTLING rules but backend `gap_to_tier()` used different thresholds (80/65/40 vs frontend 50/20). FIXED: aligned thresholds.
2. **"Current levels" entry zones** — 100% of trade theses used vague "current levels ($X)" phrasing. PM needs limit prices not suggestions. FIXED: schema upgraded to `limit_entry_price` (single number), `stop_loss`, `take_profit`, `entry_rationale`, `portfolio_allocation_pct`. "current levels" banned in prompt.
3. **Zero position sizing** — No allocation %, Kelly fraction, vol adjustment. FIXED: `portfolio_allocation_pct` field added (HIGH=1.5-2.5%, MODERATE=0.5-1.5%, SPECULATIVE=0.25-0.5%).
4. **Thesis concentration** — 68% of trades were SHORT URA. New prompt warns against concentration.
5. **Decay Clock frozen** — All stories had `time_decay: 0.00, freshness: 1.00`. FIXED: added `compute_decay()` server-side + client-side JS decay from `generated_at`.

**What the PM needs to pay $2k/month:**
- Fix tiering (done)
- Live P&L tracker with win rate, Sharpe, documented fills
- Price-aware entry zones with limit orders (done)
- Position sizing algorithm (done)
- API access (WebSocket/REST)
- Multi-asset breadth (FX, rates, commodities, credit)

### Reuters Journalist: 3.25 → 4.5/10 (still FAIL for wire citation)

**What improved:** Source provenance concept validated. TIER 1/2 badges, DATA SYNC indicator, capital tooltips are the right direction.

**What failed:**
1. **Features in code, not deployment** — CDN served stale version. FIXED: CDN cache-control hardened.
2. **Capital volumes flat** — 189/191 stories at $100M (stale CDN artifact — current data shows only 8/395 at $100M).
3. **"flows.json aggregate" is circular** — Citing system's own output isn't source attribution. Need: "QQQ $28.8B: Invesco QQQ Trust AUM as of 2026-06-22 (source: Invesco.com)".
4. **GAP score is LLM black box** — `reality_data_sources: []` on every story. No stored price snapshots. Cannot reproduce any GAP calculation.
5. **OSINT filler** — 150+ stories with `contradiction_gap: 15` and garbled text labeled "VERIFIED_DISPATCH" with no editorial review.

**What the journalist needs to cite in a wire story:**
- Per-ticker price snapshots stored and displayed for GAP ≥ 40
- Specific FRED series IDs and CFTC report codes
- Methodology page listing exact data sources
- GAP score reproducibility (timestamped data + formula)

### Key Insight

Both reviewers validated the DIRECTION but killed the EXECUTION. The architecture, visual hierarchy, and trade thesis schema are right. The problems were:
1. CDN delivery pipeline (stale cache)
2. Data pipeline bugs (tier thresholds, static decay)
3. Prompt engineering (LLM ignoring "no current levels" rule)

These were execution gaps, not design flaws. All have been fixed.
