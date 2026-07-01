# Telegram Publishing Format — La Gazzetta di Kyiv

Contradiction-first publishing format for Telegram channel posts. Designed for institutional readers who see notification previews before opening.

## Three-Line Structure (v3.0)

```
HOOK  — 50-80 chars, notification-preview, data-driven suspense
STORY — Consensus vs Reality block + Capital Flow Impact + Contradiction Score
LINK  — Direct anchor URL to story page
```

## Section Details

### 1. HOOK (notification-visible)

- **Must stand alone** in the notification preview — captivate without requiring the user to open
- **Max 80 characters** (60-70 ideal for Telegram mobile previews)
- **Contradiction-first** — frame the gap between market belief and capital flow reality
- **No emojis, no clickbait** — data-driven suspense only
- Bold-wrapped: `<b>hook text</b>`

**Template pool (13 patterns):**

| Trigger | Hook |
|---|---|
| High contradiction (≥70) + both they_say/reality | "The consensus and the capital flows are telling opposite stories." |
| Flow ≥$100B | "$87B moving into SOVEREIGN DEBT. The reason is not consensus." |
| Flow ≥$10B | "$12B repositioning into TECH. Capital is voting." |
| Flow <$10B | "$3.2B shift in COMMODITIES. Data contradicts the narrative." |
| Contradiction without flows | "Markets are pricing one thing. Capital flows show another." |
| Contradiction ≥75 | "The data refuses to confirm what the market believes." |
| Rates/Fed/ECB | "The rate decision was expected. The capital reaction was not." |
| War/conflict/sanctions | "Geopolitics is moving capital. Track where it flows." |
| China | "What Beijing is doing vs what Western capital is assuming." |
| AI/chips | "AI capital flows are diverging from AI headlines." |
| Crypto | "Crypto prices move. Capital flows reveal why." |
| Energy | "Energy repricing is underway. Here is where capital is moving." |
| Crash/collapse | "Behind the selloff: the capital flow signal most are missing." |
| Rally/surge | "This rally has a capital flow dimension no one is discussing." |
| Generic/fallback | "{headline[:80]} — the flows tell a different story." |

### 2. STORY (contradiction + implications)

Two modes depending on data availability:

**Mode A: Contradiction story (has both they_say and reality)**
```
Consensus: "Markets expect rate pause through Q3..."
Reality: "Yield curve steepening and $87B institutional rotation into duration..."
Capital flow impact: inflow: $87.3B in SOVEREIGN DEBT at 1.8x velocity
Contradiction score: 72/100 — significant divergence from consensus
```

**Mode B: News story (they_say only or missing reality)**
```
{headline[:300]}
Capital flow impact: {direction}: ${amount_b}B in {asset} at {pace}x velocity
Contradiction score: {score}/100
```

### 3. LINK

Must be a **direct anchor URL** to the specific story, not just the homepage:
```
Read the full report: lagazzettadikyiv.com
```
HTML: `<a href="https://www.lagazzettadikyiv.com/stories.html#story-{id}">Read the full report: lagazzettadikyiv.com</a>`

## Implementation

Script: `scripts/cco_telegram.py` (also synced to `agents_build/cco_telegram.py`)

Key functions:
- `format_story(story: dict) -> str` — three-line assembly
- `_generate_hook(...)` — hook selection logic
- `send_post(text, dry_run)` — Telegram Bot API dispatch

Commands:
```bash
python3 scripts/cco_telegram.py --story-id 123 --headline "..." --they-say "..." --reality "..."
python3 scripts/cco_telegram.py --dry-run  # preview format
```

## Anti-Patterns (do NOT do)

- Do NOT use emojis or ASCII art in hooks
- Do NOT link to homepage — always link to the specific story anchor
- Do NOT use generic CTAs ("UNLOCK FULL SIGNAL", "VIEW NOW") — use direct action language
- Do NOT include source names or confidence as separate lines — integrate into the story block
- Do NOT exceed 80 characters in the hook line
