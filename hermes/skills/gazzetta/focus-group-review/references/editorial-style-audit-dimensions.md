# Editorial Style Audit — Scoring Dimensions & Rubric

Proven in the Gazzetta di Kyiv Cycle 6 editorial audit (June 2026). Use this reference when the task calls for evaluating writing quality, readability, headline sharpness, or accessibility for non-professional audiences.

## Persona Combination

1. **Chief Editor** — Wordiness, sentence length, container descriptions (matryoshka format), headline quality, writing architecture
2. **First-Time Regular Visitor (50+)** — Accessibility, jargon comprehension, vocabulary barrier, cognitive load
3. **Skeptical Journalist** — They Say/Reality sharpness (straw man vs. real contradiction), banned phrases, credibility

## Audit Dimensions

### 1. Headline Quality (per-headline grading)

| Grade | Criteria | Word Count Ceiling |
|-------|----------|-------------------|
| **A** | Named actor + specific event + concrete consequence. No templates. | ≤10 words |
| **B** | One of: named actor, specific event, or consequence. Minor abstraction. | ≤12 words |
| **C** | Abstract nouns (dilemma, challenge, phase), vague verbs (need, face). | ≤14 words |
| **D** | LLM template structure ("Three X Converge," "as Y Enters New Phase"). | ≤18 words |
| **F** | Multiple clauses separated by em-dashes. Paragraph disguised as headline. | >18 words |

**Red flags:**
- "As [vague event] enters new phase" — GPT-ism. Name the phase.
- "Three/Five X [verb]" — textbook LLM headline structure
- Two em-dash clauses — split into separate headline + subhead
- "While [extra context]" tacked onto end — cut it
- **ALL-CAPS overuse** — When >50% of headlines are in ALL CAPS, the publication reads as a breaking-news ticker (ZeroHedge pattern), not a premium editorial product (Bloomberg/FT/Reuters pattern). ALL CAPS signals urgency; when every headline is urgent, none are. Reserve ALL CAPS for genuinely market-moving events (≤2 per cycle). Detection: `Array.from(document.querySelectorAll('#newsCol article h3')).filter(h => h.textContent === h.textContent.toUpperCase() && h.textContent.length > 20).length` — if >50% of editorial stories, flag it.
- **"BREAKING:" prefix** — If the headline already communicates urgency through its content, the "BREAKING:" prefix is redundant decoration. Reserve for genuine first-report events.

### 2. Wordiness — Sentence-Level Scoring

**Too long (needs splitting):** >45 words per sentence. A 50+ reader with declining working memory loses the thread by word 35.

**Sentence fragment:** Incomplete sentences used as concluding thoughts. If it carries the thesis, it should be the lede, not buried at the end of a 100-word block.

**They Say / Reality duplication — CRITICAL BUG:** If the REALITY text block is a verbatim copy of the collapsed-card summary paragraph, flag as a rendering/content bug. The summary sets the scene; the REALITY should be the contradiction in sharper, punchier form. The reader sees the same text twice — this destroys the format's credibility.

**Detection method:** Expand any story card and compare:
```
summary = card collapsed-view paragraph text
reality = expanded-view REALITY section text
if summary === reality → CRITICAL bug (They Say/Reality duplication)
```

If the editorial writer pipeline populates REALITY from the same field as the summary paragraph, this affects ALL editorial stories — audit the pipeline, not just individual stories. The REALITY should be a distinct, shorter, punchier restatement of the contradiction, not a copy-paste of the scene-setting summary.

**Note on INTEL BRIEF vs REALITY:** The expanded story view has BOTH an INTEL BRIEF section and a REALITY section. The INTEL BRIEF should be the analytical expansion. The REALITY should be the contradiction landing blow. These serve different purposes — don't merge them.

### 3. They Say / Reality — Sharpness Tiers

| Tier | Criteria | Example |
|------|----------|---------|
| **VERY SHARP ✓** | They Say quotes actual media narrative verbatim. Reality names a specific counter-event with numbers. | "They say: 'Constructive talks. Iran close to signing.' Reality: Iran publicly denied every concession." |
| **SHARP ✓** | They Say describes a real, attributable belief. Reality provides concrete, falsifiable counter-evidence. | "They say: corporate accumulation creates BTC price floor. Reality: Strategy sold, BTC broke support." |
| **MODERATE** | They Say is plausible but generic. Reality is factual but not a direct counter. | "They say: Labour stable, BoE at peak. Reality: leadership challenge + rate debate." |
| **WEAK ✗** | They Say is a straw man — no real person holds this view in this form. Reality doesn't contradict because the premise was never real. | "They say: Ukraine dependent on Western aid only. Reality: Gulf-Ukraine axis forming." — No analyst claims the Gulf can't have foreign relations. |
| **STRAW MAN ✗** | They Say constructs an opponent who doesn't exist to score an easy point. | "They say: AI benefits all tech equally." — Nobody credible says this. |

**Test:** If you showed the They Say to someone who holds that view, would they say "yes, that's what I believe"? If not, it's a straw man.

### 4. Jargon Density — Accessibility Score

Count unexplained terms per card. Terms that a 50+ reader without finance background would not understand:

- **Tier 1 (must explain in-text):** ATH, ASICs, ATR, PDR, DePIN, RWA, gamma, DXY
- **Tier 2 (glossary link sufficient):** conviction score, velocity, positioning, structural bid, marginal buyer, repricing
- **Tier 3 (acceptable jargon for target audience):** ETF, volatility, yield, futures, stop-loss

**Target:** ≤2 unexplained Tier 1 terms per card. Add a glossary link below the masthead defining Tier 1 terms.

### 5. Container Descriptions — Matryoshka Quality

| Grade | Criteria |
|-------|----------|
| **A** | Clean, confident, zero jargon. Tells the reader what they'll find without using internal system language. |
| **B** | Clear but slightly wordy. One minor jargon term. |
| **C** | Repetitive (same term used in adjacent sentences). Abstract benefit statement without concrete example. |
| **D** | Uses internal dev language ("Container 1," "Container 2"), YouTube-trader language ("MAX CONVICTION"), or meta-language that breaks reader immersion. |
| **F** | Grammar error, completely opaque, or misleading about what's inside. |

**Red flag:** Any container description that mentions container numbers or internal architecture terms. The reader doesn't think in container numbers — replace with natural language.

### 6. Aggregator Story Detection — Editorial Integrity Check

**Definition:** Stories that are raw wire-service feed items with ZERO editorial treatment. They have no They Say section, no Reality section, no Intel Brief, and no original THE PLAY — just a headline sourced from Reuters/Bloomberg/CNBC with source attribution links.

**Detection:** Query each story's expanded view for `THEY SAY` and `REALITY` and `INTEL BRIEF` headings. If all three are absent and the headline matches wire-service format ("Headline - Source Name"), flag as aggregator.

**Browser-console detection:**
```js
Array.from(document.querySelectorAll('#newsCol article')).map((a,i) => {
  const hasTheySay = a.textContent.includes('THEY SAY');
  const hasReality = a.textContent.includes('REALITY');
  const hasIntelBrief = a.textContent.includes('INTEL BRIEF');
  const hasSourceAttr = a.textContent.includes('reuters_business') || a.textContent.includes('Source:');
  return { idx: i, isAggregator: !hasTheySay && !hasReality && !hasIntelBrief && hasSourceAttr };
}).filter(r => r.isAggregator)
```

**Impact:** Aggregator stories dilute the editorial brand. A reader who clicks expecting the They Say/Reality contradiction format gets a raw feed item with no framing. This breaks the implicit contract with the reader. Every story on Gazzetta must have They Say/Reality, or it doesn't belong in the editorial feed.

**Fix options:** (a) Run aggregator stories through the editorial writer pipeline before publishing, or (b) segregate them into a separate "Wire" section clearly labeled as unedited feed items. The story count in the hero ("33 stories") should distinguish editorial vs. wire if both are present.

**Severity:** HIGH. Even one aggregator story without editorial treatment signals that the publication doesn't stand behind every piece of content.

### 7. Data Integrity Quick-Checks

Before diving into writing-style analysis, scan for these data bugs that destroy reader trust instantly:

| Bug | Detection | Severity |
|-----|-----------|----------|
| **"undefined" in flow amount** | Flow line shows `undefined — projected` instead of `$XB ↑ sector` | CRITICAL — "undefined" is a JavaScript keyword visible to readers |
| **"undefined" confidence** | Confidence shows `change at undefined confidence` | CRITICAL |
| **"BUILDING" contradiction score** | Score badge shows `BUILDING 45/100` — incomplete processing visible to readers | HIGH — either hide until complete or show "Calculating…" |
| **Templating bug: wrong ticker** | Flow link shows `→ NVDA BUY HIGH` on a commodities/defense story completely unrelated to NVIDIA | HIGH — signals sloppy templating to the reader |
| **THE PLAY = Projected Flow (duplicate)** | THE PLAY text is identical to the CAPITAL FLOW "Projected further flow" text | MEDIUM — reader sees same paragraph twice |
| **ALL-CAPS headline ≠ breaking news** | ALL-CAPS headline for a story that's 2+ days old with no market-moving update | MEDIUM — urgency inflation |

**Browser-console sweep:**
```js
// Check for "undefined" data
document.querySelectorAll('#newsCol article').forEach((a,i) => {
  const txt = a.textContent;
  if (txt.includes('undefined')) console.warn(`Story ${i}: "undefined" in card`);
  if (txt.includes('BUILDING')) console.warn(`Story ${i}: "BUILDING" score visible`);
});
// Check for templating bugs: NVDA on non-tech stories
Array.from(document.querySelectorAll('#newsCol article')).filter(a => {
  const hasNVDA = a.textContent.includes('NVDA');
  const isTech = a.textContent.includes('crypto') || a.textContent.includes('AI') || a.textContent.includes('chip');
  return hasNVDA && !isTech;
}).forEach((a,i) => console.warn(`Story ${i}: NVDA ticker on non-tech story`));
```

### 8. Overall Readability Score (1-10)

Weights: Vocabulary (25%), Sentence length (20%), Scannability (20%), Information hierarchy (15%), Jargon density (20%).

## Report Format

```markdown
# Editorial Style Audit — [Site/Date]

## Verdict: PASS / CONDITIONAL PASS / FAIL — X/10 Readability

### 1. Headline Quality
| # | Headline | Grade | Words | Issue |

### 2. Wordiness
- Longest sentence: [text] ([N] words) → Fix: [rewrite]
- Sentence fragments found: [count]
- They Say/Reality duplication: [count]

### 3. They Say / Reality Sharpness
| Story | Tier | Notes |

### 4. Jargon Audit
| Term | Story | Tier | Should explain? |

### 5. Container Descriptions
| Container | Current | Grade | Fix |

### 6. Top-3 Rewrites
1. [Most impactful headline fix]
2. [Most confusing container description fix]
3. [Weakest They Say fix]

### 7. Additional Findings
- Rendering bugs
- Content gaps
- Typos
- Aggregator stories found: [count]
- Data integrity bugs: [list]
```

## Pitfalls

**Cron audit must verify site reachability first.** The GitHub Pages URL (`pureciclismo.github.io/gazzetta-di-kyiv`) is DEPRECATED — it returns 404. The canonical URL is `www.lagazzettadikyiv.com` (GCS bucket). If the custom domain SSL certificate is broken (ERR_CERT_COMMON_NAME_INVALID), use the direct GCS URL: `https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html`. Verify with:
```bash
curl -sI "https://storage.googleapis.com/www.lagazzettadikyiv.com/index.html" | head -3
```
If all URLs fail, record `CANNOT ASSESS` for all visual metrics and focus on content-only evaluation from the source `stories.json`.

**Hero stat must match rendered count.** If "33 STORIES" appears in the hero but `stories.json` contains 33 stories, check whether some of those 33 are aggregator stories without editorial treatment. The count should distinguish editorial vs. wire — or the aggregator stories should be excluded from the count entirely. A count that mixes editorial and raw-feed items overstates the publication's editorial output.

**They Say/Reality content loads dynamically — collapsed cards won't show it.** When using `browser_console` to query `innerHTML`, collapsed story cards do NOT contain the They Say/Reality/Intel Brief sections. These are injected by JavaScript only when the card is expanded. To audit They Say/Reality quality, either (a) expand individual cards via click and then query, or (b) capture the full page snapshot after initial load (the `browser_snapshot` tool captures rendered text content including dynamically-injected sections from the initial page render). The `innerHTML` of collapsed cards will misleadingly show zero They Say/Reality sections for ALL stories — this is a DOM query limitation, not a content gap.

**"CRITICAL" badge overuse dilutes signal.** If 12+ of 33 stories are tagged CRITICAL, the badge loses meaning. When everything is critical, nothing is. Reserve CRITICAL for genuinely market-moving events — ≤3 per cycle. Flag overuse as an editorial judgment issue, not a rendering bug.

**Card summaries exceeding 80 words overwhelm collapsed view.** The collapsed card is designed for scanning. If >8 stories have summary paragraphs exceeding 80 words, flag it. The analytical depth belongs in the expanded INTEL BRIEF, not the card preview.
