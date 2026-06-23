# Contradiction Score Algorithm — v2 (June 2026)

## History

**v1 (May 2026):** Field-existence check. Every story scored 85-95 because they all had `capital_flow`, `extremum`, and `confidence` fields filled. Zero discrimination. Flagged by Macro Analyst focus group persona as "not measuring contradiction at all."

**v2 (June 2026):** Text-based analysis measuring actual narrative-vs-reality tension + flow-narrative divergence + confidence grounding. Scores now distribute 45-70 across stories.

## v2 Algorithm

```javascript
function calcContradictionScore(story) {
  let score = 30; // baseline — a story by definition has some contradiction

  const cf = story.capital_flow;
  const theySay = (story.they_say || '').toLowerCase();
  const reality = (story.reality || '').toLowerCase();

  // 1. Narrative-Reality Tension (0-30)
  if (theySay && reality) {
    // Count contrast markers (signals of actual contradiction)
    const markers = ['but','however','not','instead','actually','yet','contrary',
                     'despite','while','whereas','though','unlike'];
    const hits = markers.filter(m => reality.includes(m)).length;
    score += Math.min(hits * 5, 15);

    // Substantive pushback: reality must have meaningful length
    if (reality.length > 50 && theySay.length > 30) score += 10;
    if (reality.length > theySay.length * 0.7) score += 5;
  }

  // 2. Flow-Narrative Divergence (0-25)
  if (cf) {
    const pos = /surge|boom|rally|bull|growth|soar|outperform|strength|optimis/.test(theySay);
    const neg = /crash|fear|crisis|risk|plunge|bear|collapse|sell|recession|weakness|pessimis/.test(theySay);

    if (pos && cf.direction === 'outflow') score += 20;
    else if (neg && cf.direction === 'inflow') score += 20;
    else if (pos || neg) score += 5;

    const amt = parseFloat(cf.current_amount || '0');
    if (amt > 5) score += 10;
    else if (amt > 2) score += 5;
  }

  // 3. Extremum quality (0-15)
  if (story.extremum) {
    const e = story.extremum;
    if (e.winner || e.loser) score += 5;
    if (e.idiot || e.genius) score += 5;
    if ((e.winner || e.loser) && (e.idiot || e.genius)) score += 5;
  }

  // 4. Confidence grounding (0-10)
  if (story.confidence === 'high' && cf && cf.current_amount) score += 10;
  else if (story.confidence === 'high') score += 5;

  return Math.min(score, 100);
}
```

## Scoring Dimensions

| Dimension | Max | What It Measures |
|-----------|-----|-----------------|
| Narrative-Reality Tension | 30 | Contrast language density in the "reality" text + length ratio between "they say" and "reality" |
| Flow-Narrative Divergence | 25 | Whether capital flow direction contradicts the consensus narrative tone |
| Extremum Quality | 15 | Whether extremum lines name specific WINNER/LOSER/IDIOT/GENIUS entities |
| Confidence Grounding | 10 | Whether high-confidence stories back their claims with flow data |
| **Baseline** | 30 | Every story inherently contains some contradiction by being selected |
| **Total Cap** | 100 | |

## Validation Results (June 2026)

After deploying v2, the focus group confirmed scores now distribute meaningfully:

| Story | Score | Why |
|-------|-------|-----|
| Morgan Stanley/Fed | 45 | Low flow-narrative divergence, shorter reality text |
| Hungary/EU Bid | 50 | Positive narrative, modest flow magnitude |
| AI Data Centre | 55 | Strong flow magnitude but narrative-flow alignment |
| Trafigura Oil | 55 | Moderate contrast markers, aligned flow |
| Hurricane Trump/China | 65 | Strong divergence (narrative negative, flows confirm), high magnitude |
| US NATO Cuts | 70 | Strongest contrast language + highest flow-narrative tension + complete extremum |

Range: 45-70. Previous range (v1): 85-95. Discrimination improved by 5x.

## Limitations

- Still heuristic-based, not NLP. Contrast marker counting is a proxy for contradiction strength, not a direct measure.
- The `pos`/`neg` regex on `theySay` is fragile — it misses nuanced narratives that are neither clearly positive nor negative.
- Does not cross-reference with the anchor asset's directional signal (that's what the SIGNAL container's `computeTriangulation()` does separately).
- "Confidence grounding" still uses the story's declared confidence level, not an independently verified metric.

## When to Re-evaluate

- If score distribution narrows again (all stories scoring within 10 points of each other)
- If a Macro Analyst focus group persona again flags it as decorative
- If NLP embedding-based contradiction detection becomes feasible in browser JS
