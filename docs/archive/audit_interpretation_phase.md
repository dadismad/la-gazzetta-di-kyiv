# Interpretation Phase Audit — La Gazzetta di Kyiv
**Date:** 2026-06-16
**Auditor:** Hermes Agent

---

## 1. CLASSIFIER INCONSISTENCY: link_processor.py vs classify_stories.py

### Two Different Algorithms
| Aspect | link_processor.py | classify_stories.py |
|---|---|---|
| **Input** | headline + body text | headline only |
| **Scoring** | Simple keyword count, highest wins | Weighted: sector=+5, pillar=+3, keyword=+1 |
| **Sector/pillar** | Sets `sector = container_name` (e.g. "monetary_order") | Reads sector/pillar from DB, matches against CONTAINER_RULES |
| **Fallback** | "flashpoints" if no keywords match | Sector heuristic (crypto→monetary, commodities→energy, etc.) → flashpoints default |
| **Tag threshold** | 2+ keyword matches on headline+body | 2+ keyword matches on headline only |

### The Critical Bug: Sector Field Poisoning

`link_processor.py` (line 175) sets `sector = container`. This means:
- A story classified as "monetary_order" by link_processor gets `sector = "monetary_order"`
- When `classify_stories.py` runs, `sector = "monetary_order"` matches NO sector in any CONTAINER_RULES list (which expects "crypto", "fx", "fixed_income", "commodities", "tech", "equities", "defense")
- So the sector weight (+5) is NEVER applied to link_processor-ingested stories

### The Pillar Bias Toward Flashpoints

`link_processor.py` (line 176) sets `pillar = "multi_pillar"`. Only flashpoints has `"multi_pillar"` in its pillar list (`[multi_pillar, eu_fragmentation]`). This gives EVERY story ingested via link_processor +3 toward flashpoints.

### Keyword Set Drift

Keywords in link_processor and classify_stories have diverged:
- `"gold"` (bare) in link_processor vs `"gold "` (trailing space) in classify_stories → link_processor matches "gold" in "goldfish", classify_stories doesn't
- `"sanction"` (stem, no 's') in link_processor vs `"sanctions"` (plural) in classify_stories
- `"drone"` in link_processor but not in classify_stories' energy list
- Various other missing/present keywords

### CONTAINER DISTRIBUTION (from DB)

```
flashpoints             140
technology_ai           102
monetary_order           82
energy_resources         40
biosecurity_health        8
information_narrative     5
```

---

## 2. MISCLASSIFICATION AUDIT — Story-by-Story Analysis

### A. MONETARY_ORDER (82 stories) — ~10-12 clearly wrong

**Wrong — should be FLASHPOINTS:**
| Story | Why wrong | Root cause |
|---|---|---|
| Christian village in occupied West Bank goes up in flames | West Bank/israel story, not monetary | sector=crypto → monetary gets +5 sector match |
| Israel killed more Palestinians in occupied West Bank | Geopolitical violence | Sector=defense. With headline-only keywords, flashpoints wins 6-0. Bug in classify_stories path |
| EU sanctions Iranian officials, IRGC unit over Hormuz | Sanctions about Iran/Hormuz | "sanctions" keyword + sector=equities |
| Stock futures rise as U.S. completes strikes against Iran | Stock market reaction to military strikes | sector=defense → should get +5 for flashpoints |
| Israeli government to bankroll extremist Hilltop Youth | Israel/West Bank story | sector=crypto → monetary gets +5 sector match |
| Iran doubles down on key demands of US deal | Iran deal/geopolitics | sector=tech → no sector match, "sanctions" keyword pushes to monetary |
| CNBC Daily Open: Trump expresses 'love' for inflation | Story is about inflation, marginally monetary | "inflation" keyword → monetary. OK borderline case |

**Wrong — should be OTHER:**
| Story | Why wrong | Reason |
|---|---|---|
| Chase unveils massive Sapphire Preferred overhaul | Consumer banking rewards card | Not monetary_order. Should not be classified |
| Paramount-Warner Bros. Discovery Merger | Merger & acquisition (entertainment) | sector=defense, but headline has no monetary keywords. Fallthrough? |
| Prices are soaring on these everyday grocery items | Consumer inflation (marginal) | "inflation" keyword. Acceptable borderline case |

**Net misclassification count for monetary_order: ~8-10 stories**

### B. ENERGY_RESOURCES (40 stories) — 5 clearly wrong

**Wrong — should be FLASHPOINTS:**
| Story | Why wrong | Root cause |
|---|---|---|
| UKRAINE FP-5 FLAMINGO MISSILES STRIKE CHEBOKSARY | Military strike on Russia | sector=commodities → energy gets +5. "missile" and "strike" match energy? No — but "refinery" in body? |
| IDF Declares Readiness to Resume Iran Operations | Military/pipeline bypass | sector=commodities → energy +5 + "hormuz" keyword |
| BREAKING: EU Proposes Biggest Sanctions Package | Sanctions/LNG ban | sector=commodities → energy +5 + "lng" keyword |
| US seeking precise info on Iran's enriched uranium | Iran/IAEA/nuclear | "uranium" keyword matches energy → +1. sector=equities |
| IAEA passes anti-Iran resolution | Iran/IAEA/nuclear | "uranium" keyword matches energy → +1. sector=defense |

**Net misclassification count for energy_resources: 5 stories**

### C. TECHNOLOGY_AI (102 stories) — ~3-5 clearly wrong

| Story | Why wrong | Root cause |
|---|---|---|
| Amazon opens full-scale, less-than-truckload shipping | Logistics, not AI/tech sovereignty | sector=equities → tech gets +5 sector match. Also "amazon" not in tech keywords |
| Chase Sapphire Preferred Card... Apple Customers | Consumer credit card perk | sector=defense → no tech sector match. Neither "amazon" nor "apple" in keywords. Fallacy? |
| Amazon strengthens its investment in Missouri | Community investment, not tech | Possible body-text keyword match from link_processor |
| Amazon's Early Prime Day Deals | Retail/shopping | Amazon is keyword in... actually not in tech keywords. sector=tech → +5 |

**Net misclassification count for technology_ai: ~3-5 stories**

### D. FLASHPOINTS (140 stories) — ~12-15 clearly wrong

Flashpoints is the default catch-all. Many non-geopolitical stories end up here:
- "Starbucks brings soccer fans together" — marketing
- "The Best Tech Gifts for Father's Day" — shopping guide
- "Remote Work Comes With a Little-Known Downside" — lifestyle
- "Sunscreens in the U.S. Might Finally Be Getting Better" — health/beauty
- "Honda recalls more than 880,000 vehicles" — auto recall
- "Hugo Boss pops 8%..." — corporate finance
- "Sea-Tac Airport's big new concourse opens" — travel
- "Rivian Made You Wait 50 Days for Service" — customer service
- "$169M Fishers District expansion..." — real estate development
- "Claude Fable is too scared to teach you about the powerhouse of the cell" — satire/education
- "Ellison's Net Worth Down Nearly $50 Billion" — wealth tracking

**Net misclassification count for flashpoints: ~12-15 stories**

### E. INFORMATION_NARRATIVE (5 stories) — 2 clearly wrong

| Story | Why wrong |
|---|---|
| Starbucks Korea to close stores early for mandatory history training | Marketing/compliance, not narrative warfare |
| KFC's The Colonel gets a subtle makeover | Rebranding, not narrative warfare |

The other 3 (Ben-Gvir urging abduction, Iran threatens Musk companies, French watchdog reveals Israeli propaganda) are correctly classified.

### F. BIOSECURITY_HEALTH (8 stories) — 2-3 clearly wrong

| Story | Why wrong |
|---|---|
| Health insurance for many Oregonians could get a lot more expensive | Insurance costs, not biosecurity |
| Health Insurer Centene Offers Most Staff Buyouts | Corporate restructuring |
| China retail sales sink for first time since Covid | Retail/economic (mentions "covid" → keyword match) |

The other 5 (biotech IPO, sunscreen FDA, GLP-1 drugs, infant formula recall, sunscreen approval) are correctly classified.

### GLOBAL MISCLASSIFICATION SUMMARY
| Container | Total | Clearly Misclassified | Misclassification Rate |
|---|---|---|---|
| monetary_order | 82 | ~10 | ~12% |
| energy_resources | 40 | ~5 | ~12.5% |
| technology_ai | 102 | ~5 | ~5% |
| flashpoints | 140 | ~15 | ~11% |
| information_narrative | 5 | ~2 | ~40% |
| biosecurity_health | 8 | ~2 | ~25% |
| **TOTAL** | **377** | **~39** | **~10%** |

---

## 3. CONTRADICTION SCORES

### Distribution
```
Score  Count
-----  -----
  0       1
 47       2
 48       1
 49       2
 50      19
 52       1
 53       4
 54       2
 55       5
 56       1
 57       1
 58       2
 59       2
 60       1
 61       1
 63       1
 65       2
 75     329     ← default/hotwash value
```

### Analysis
- **329/377 (87.2%) have score=75**: This is a default/placeholder value set by the Agent pipeline hotwash step, NOT a meaningful score. It provides NO differentiation between stories.
- **48 stories have non-75 scores**: These are genuinely scored (range 0-65). Higher scores correlate with genuine contradiction stories (e.g., "Critical Contradiction: WTI Drops Below 90 Despite Israel-Iran War" = 65, "Ben-Gvir Urges Cabinet to Abduct Lebanese Women" = 60).
- **19 stories have score=50**: This is the link_processor default (line 173). These stories were ingested by link_processor and never processed by the contradiction-scoring Agent step.
- **Score=75 is meaningless**: It's used for sort order in db_to_json.py (line 68: `ORDER BY s.contradiction_score DESC`) but since ~87% are the same value, the sort is effectively by `generated_at DESC` for those stories.

### Recommendation
- Replace the 75 default with a proper score or NULL
- Implement a contradiction classifier that produces meaningful variance
- The 48 stories with varying scores could serve as training examples

---

## 4. CAPITAL FLOW DATA

### Coverage
| Metric | Count |
|---|---|
| Stories with capital_flow in full_json | 377 (100%) |
| Stories with non-null amount_b | 286 (76%) |
| Stories with null amount_b | 91 (24%) |

### Direction Distribution
| Direction | Count |
|---|---|
| inflow | 118 |
| neutral | 198 |
| outflow | 61 |

### Flows Table
- 199 entries in `flows` table
- 214 entries in `story_flow_links` table (story-to-flow associations)
- Each flow has: amount_b, asset_class, direction, pace_multiplier, divergence, heat_score, trade_signal, PDR ratio, and full metadata

### Assessment
✅ Capital flow data IS being extracted and populated in full_json
✅ Amount_b values are present (non-null) for 76% of stories
✅ Flows are linked to stories via story_flow_links table
✅ Direction data is meaningful (inflow/neutral/outflow)
⚠️ **BUT** db_to_json.py does NOT output flow data in the JSON — no flow data is emitted despite being available
⚠️ Capital flow in full_json has `pace_multiplier` (all 377 stories), but `amount_b: null` for 24% — may indicate extraction failures

---

## 5. TAGS ACCURACY

### Tag Distribution
| Tag | Count | Comment |
|---|---|---|
| american-decline | 44 | Heaviest tag — "US", "trump", "biden", "dollar" are common keywords |
| eu-strategy | 3 | Very few stories trigger 2+ EU keyword matches |
| china-ascendancy | 1 | Only 1 story! Despite many China-related stories |
| russia | 1 | Only 1 story! Despite Ukraine/Russia coverage |
| global-south | 0 | Defined in code, NEVER assigned |

### Total: 49 tag assignments across 377 stories (13% coverage)

### Issues
1. **Too few tags**: 49/377 stories have any tags (13%). The 2-keyword threshold is too strict for headline-only matching (classify_stories.py route). For body text (link_processor route), it's reasonable but still produces few matches.

2. **china-ascendancy has 1 assignment** — This is clearly wrong. Stories about "Huawei", "taiwan", "South China Sea", "semiconductor" should trigger this tag. Root cause: the tag keywords include "semiconductor" and "chip export" (not "chip" bare) and "rare earth" — but many stories use "chip" (not "chip export"), and "china" as a bare word is in the list but "chinese" is also there. Let me check: the story tagged china-ascendancy is "Somaliland opens diplomatic office in Taiwan" — tags: china-ascendancy. No wait, looking at the output:
   - 471|flashpoints|tech|neutral|china-ascendancy|Somaliland opens diplomatic office in Taiwan...
   
   This story has "taiwan" which is in china-ascendancy keywords. But also check: does "taiwan" alone trigger 2 matches? Let me see: "taiwan" is in the keywords. What else? "somaliland" — no. "diplomatic office" — no. So this should have 1 match, not 2. Unless the body text has other keywords.
   
   Hmm, but the tag is china-ascendancy. This must have come from link_processor which uses body text.

3. **american-decline tags some non-US stories incorrectly**: e.g., "S&P/Nasdaq Break Below Friday's Low" is tagged american-decline because "nasdaq", "s&p" are in the keywords. This is correct because the stock market stories ARE about American financial decline.

4. **Incorrect tag assignment**: "Christian village in occupied West Bank goes up in flames after large-scale attack by Israeli settlers" — tagged "china-ascendancy". This is COMPLETELY wrong. The story is about Israel/West Bank violence. Tag should be none or possibly "russia" if connected. Root cause: the story's pillar field is "china_ascendancy" — the pillar field is being confused with tags somewhere in the pipeline.

5. **Tags not used in output**: db_to_json.py does include `story["tags"]` and `tags_index` in the output. So tags ARE surfaced. But with 13% coverage, they're mostly empty.

---

## 6. ROOT CAUSE SUMMARY

| Issue | Root Cause | Severity |
|---|---|---|
| Dual classifiers | link_processor.py and classify_stories.py use different algorithms | HIGH |
| Sector field poisoning | link_processor sets sector=container_name, breaking classify_stories' sector matching | HIGH |
| Flashpoints pillar bias | "multi_pillar" default gives ALL stories +3 toward flashpoints | MEDIUM |
| Keyword set drift | Different keyword lists, some with trailing spaces, different tokens | MEDIUM |
| 87% have contradiction_score=75 | Agent hotwash sets default placeholder, not meaningful score | HIGH |
| 13% tag coverage | 2-keyword threshold too strict; headline-only matching insufficient | MEDIUM |
| Tags not audited | Stories tagged with wrong power vectors (china-ascendancy on West Bank story) | HIGH |
| global-south tag unused | Defined but never assigned | LOW |
| Capital flow not in JSON output | db_to_json.py doesn't emit flow data despite availability | MEDIUM |

---

## 7. RECOMMENDED FIXES

### Fix 1: Unify Classifiers (HIGH PRIORITY)
Merge link_processor and classify_stories into a single classification module:
```python
# new: classifier.py — used by both ingestion and backfill
def classify(healine, body=None, sector=None, pillar=None):
    # Unified keyword+pattern matching
    # Same algorithm in both paths
```

### Fix 2: Fix Sector Field (HIGH PRIORITY)
In link_processor.py, change line 175:
```python
# BAD:
"sector": container,
# GOOD:
"sector": derive_actual_sector(container, headline, body)
```

### Fix 3: Remove Pillar Bias (MEDIUM PRIORITY)
Add "multi_pillar" to all container pillar lists, or use a neutral pillar default that doesn't bias any container.

### Fix 4: Meaningful Contradiction Scores (HIGH PRIORITY)
Replace the 75 default with NULL and implement a proper contradiction classifier. Use the 48 scored stories as seed examples.

### Fix 5: Lower Tag Threshold (MEDIUM PRIORITY)
Lower from 2 to 1 keyword match for tags, or keep 2 but use full text (headline+body) instead of headline-only. Add global-south keyword triggers.

### Fix 6: Emit Flow Data in JSON (LOW PRIORITY)
Add flow data embedding to db_to_json.py output.

### Fix 7: Reclassify ~39 Misclassified Stories (HIGH PRIORITY)
Re-run classify_stories.py after fixing the classifier, or manually fix the most egregious misclassifications.
