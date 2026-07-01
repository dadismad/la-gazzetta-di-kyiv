---
name: content-analysis-loop
description: Analyzes every post/article/story shared in the Gazzetta di Kyiv Telegram chat. Extracts domain, structure, ideas, taxonomy, views, and ideologies. Stores as structured knowledge. Feeds back into content publishing and curation strategies.
version: 1.0.0
author: Hermes Agent
created_by: agent
---

# Content Analysis Loop

A knowledge ingestion system for Gazzetta di Kyiv. Every post, article, or story shared in the Telegram chat is analyzed and stored as structured intelligence. This creates a growing database of what works — what structures engage, what language resonates, what ideological framings convert.

## When to Use

- Whenever the user shares an external article, post, or story in chat
- As a background process that reviews recent chat history for unanalyzed content
- When building or refining the editorial strategy

## Workflow

### Step 1: Detect Content
When the user shares a URL or a substantive post in the Telegram chat, flag it for analysis. Also check recent chat history for unanalyzed items.

### Step 2: Extract Characteristics
For each item, extract:

| Dimension | What to Extract | Example |
|-----------|----------------|---------|
| **Domain** | Sector: geopolitics, macro, tech, crypto, longevity, space, culture | "geopolitics" |
| **Structure** | Headline pattern, argument flow (claim→evidence→implication vs narrative→contradiction), paragraph count, word count, use of data/quotes | "headline: contradiction pattern, 3-part argument, 240 words" |
| **Ideas** | Core thesis in one sentence, supporting claims (max 3) | "US petrodollar system is in structural decline" |
| **Taxonomy** | Key terms used, categories invoked, jargon density | "de-dollarization, BRICS, reserve currency, petroyuan" |
| **Views** | Ideological stance, school of thought, what it argues against | "multipolar realist, argues against unipolar consensus" |
| **Voice** | Tone (sharp/neutral/academic), conviction level (observer vs believer), emotional register | "sharp, conviction-driven, urgent" |
| **Engagement Hooks** | What makes it attention-grabbing: contradiction, named actor, specific number, emotional trigger | "contradiction + named actor + specific data point" |
| **Thesis Alignment** | Which of the six Gazzetta theses it supports, contradicts, or relates to | "aligns with US Petrodollar Decline (thesis 2)" |

### Step 3: Store
Save to `data/content_analysis/store.jsonl` — one JSON object per line:

```json
{
  "id": "ca_20260603_001",
  "source": "telegram_chat",
  "url": "https://...",
  "title": "...",
  "analyzed_at": "ISO timestamp",
  "domain": "geopolitics",
  "structure": {"headline_pattern": "contradiction", "argument_flow": "claim→evidence", "word_count": 240},
  "ideas": {"core_thesis": "...", "supporting_claims": ["...", "..."]},
  "taxonomy": {"key_terms": ["de-dollarization", "BRICS"], "jargon_density": "medium"},
  "views": {"stance": "multipolar realist", "argues_against": "unipolar consensus"},
  "voice": {"tone": "sharp", "conviction": "high", "emotional_register": "urgent"},
  "engagement_hooks": ["contradiction", "named_actor", "data_point"],
  "thesis_alignment": ["us_decline"],
  "quality_rating": "high|medium|low",
  "reuse_notes": "Headline structure effective. Contradiction opening works."
}
```

### Step 4: Integrate
Periodically (every 12h or on demand), review the knowledge store and extract patterns:
- Which headline structures appear most in high-quality items?
- Which taxonomic language correlates with engagement?
- Which ideological stances produce the sharpest content?
- What voice characteristics appear in the best-performing items?

Feed these patterns into the editorial writer skill as "proven techniques."

### Step 5: Apply
When writing new content (via `gazzetta-editorial-writer`), consult the knowledge store:
- "Previous high-quality headlines used contradiction pattern — use that"
- "Sharper voice correlates with engagement — increase conviction"
- "Named actors + specific data = attention hook — ensure both are present"

## Storage Format

File: `data/content_analysis/store.jsonl`

One JSON object per line. Append-only. Keyed by `id` (ca_YYYYMMDD_NNN). Deduplicate by URL before adding.

Also maintain a summary index at `data/content_analysis/index.json`:
```json
{
  "total_items": 42,
  "last_analyzed": "ISO timestamp",
  "top_domains": {"geopolitics": 18, "macro": 12, "tech": 8},
  "top_structures": {"contradiction_headline": 22, "narrative_lede": 14},
  "top_voice": {"sharp": 30, "neutral": 8, "academic": 4},
  "proven_patterns": [
    "Contradiction headline + named actor + data point = highest engagement",
    "Sharp voice (+ conviction) outperforms neutral observer tone",
    "Stories aligned with thesis framework get reused more"
  ]
}
```

## Integration with Editorial Pipeline

The content analysis loop feeds into `gazzetta-editorial-writer`:

1. Before writing, the editor loads `data/content_analysis/index.json`
2. Checks `proven_patterns` for current best practices
3. Applies patterns to new content generation
4. After publishing, the published content itself gets analyzed and added to the store

This creates a closed loop: analyze → learn → apply → publish → analyze.

## Automation

Add to the editorial cron workflow (`gazzetta-agentic-nlp-guarded-autopost-8h`):
- After Step 10 (write output files), run content analysis on the just-published content
- Also scan the Telegram chat for any user-shared URLs not yet analyzed

Manual trigger: the user can say "analyze this" with a URL, or "review content analysis" to see patterns.
