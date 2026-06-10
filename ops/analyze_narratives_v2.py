#!/usr/bin/env python3
"""
Gazzetta di Kyiv — Narrative Brain v2.0
Queries gazzetta.db for top 15 most recent stories, synthesizes the
3 Core Market Narratives using Gemini, and updates site/data/narratives.json.

Usage:
    .venv/bin/python ops/analyze_narratives_v2.py
    .venv/bin/python ops/analyze_narratives_v2.py --dry-run  # skip API call

Output: site/data/narratives.json
"""

import json, os, sys, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "gazzetta.db"
DATA_DIR = PROJECT_ROOT / "data"
NARRATIVES_PATH = DATA_DIR / "narratives.json"

# ── Gemini API setup ──
def get_deepseek_client():
    """Use DeepSeek API (available in Hermes' custom_providers env var)."""
    try:
        custom_providers = json.loads(os.environ.get('custom_providers', '[]'))
        for provider in custom_providers:
            if 'deepseek' in provider.get('name', '').lower():
                return provider
    except Exception:
        pass
    return None


def query_top_stories(limit=15):
    """Get the top N most recent non-OSINT stories with their core fields."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT id, full_json FROM stories
        WHERE (
            json_extract(full_json, '$.source') NOT LIKE 'osint%'
            OR json_extract(full_json, '$.source') IS NULL
        )
        ORDER BY json_extract(full_json, '$.generated_at') DESC
        LIMIT ?
    """, (limit,)).fetchall()

    stories = []
    for row in rows:
        try:
            story = json.loads(row['full_json'])
            story['story_id'] = row['id']
            stories.append({
                'headline': (story.get('headline') or '')[:150],
                'they_say': (story.get('they_say') or '')[:200],
                'reality': (story.get('reality') or '')[:200],
                'thesis': (story.get('thesis') or '')[:200],
                'asset_class': story.get('capital_flow', {}).get('asset_class', ''),
                'direction': story.get('capital_flow', {}).get('direction', ''),
                'contradiction_score': story.get('contradiction_score', 50),
                'paradigm_pillar': story.get('paradigm_pillar', ''),
            })
        except Exception:
            continue

    conn.close()
    return stories


def synthesize_narratives(stories, dry_run=False):
    """Use Gemini/DeepSeek to synthesize 3 core narratives from stories."""
    if not stories:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "narratives": [],
            "disclaimer": "No stories available for analysis."
        }

    # Build story digest for AI
    digest_lines = []
    for i, s in enumerate(stories, 1):
        digest_lines.append(
            f"{i}. [{s['asset_class'] or 'macro'}] {s['headline']}\n"
            f"   They Say: {s['they_say'][:100]}\n"
            f"   Reality: {s['reality'][:100]}\n"
            f"   Contradiction: {s['contradiction_score']}/100"
        )

    digest = "\n".join(digest_lines)

    if dry_run:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dry_run": True,
            "story_count": len(stories),
            "narratives": [
                {
                    "title": "Geopolitical Risk Repricing",
                    "strength": "STRONG",
                    "direction": "Risk-Off",
                    "summary": "Multiple stories point to escalating Middle East tensions (Iran/Hormuz/Israel-Lebanon) with capital flowing into commodities and defense. Markets underpricing tail risk.",
                    "key_stories": len([s for s in stories if s['asset_class'] in ('commodities', 'defense')]),
                    "trade_implication": "Long oil, gold, defense. Short risk assets with Middle East exposure.",
                },
                {
                    "title": "Labor Market Cracking — Stagflation Signal",
                    "strength": "BUILDING",
                    "direction": "Neutral-to-Bearish",
                    "summary": "ADP miss combined with Home Sales beat creates mixed macro picture. Inflation expectations rising for 3rd month despite labor softening.",
                    "key_stories": sum(1 for s in stories if s['asset_class'] == 'macro'),
                    "trade_implication": "Long TLT (bonds), short financials. Gold as stagflation hedge.",
                },
                {
                    "title": "Crypto Institutional Adoption vs Distribution",
                    "strength": "MODERATE",
                    "direction": "Neutral",
                    "summary": "Ethena's Janus Henderson partnership signals institutional inflows while BlackRock BTC exchange transfers suggest distribution. Mixed signal.",
                    "key_stories": sum(1 for s in stories if s['asset_class'] == 'crypto'),
                    "trade_implication": "Neutral BTC. Long ETH (institutional flows). Watch stablecoin supply.",
                },
            ],
            "synthesis_note": "DRY RUN — narratives are pre-canned, not AI-generated. Use without --dry-run for live analysis.",
        }

    # Try DeepSeek API
    provider = get_deepseek_client()
    if not provider:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error": "No DeepSeek API key available in custom_providers. Set up a provider or use --dry-run.",
            "narratives": [],
        }

    # Build the prompt
    prompt = f"""You are a macro strategist at a top-tier hedge fund. Below are the 15 most recent intelligence reports from our capital flow monitoring system. Each report tracks where money is actually moving — not what headlines say.

Synthesize the 3 Core Market Narratives currently driving global capital flows. Each narrative must:
- Have a clear TITLE (3-7 words)
- Have a STRENGTH rating (DOMINANT / STRONG / BUILDING / MODERATE)
- Have a DIRECTION (Risk-On / Risk-Off / Neutral-to-Bullish / Neutral-to-Bearish / Neutral)
- Include a 2-3 sentence SUMMARY explaining what capital is doing and why
- Include a TRADE IMPLICATION (specific, actionable, asset-class level)
- Reference how many of the 15 stories support this narrative (KEY_STORIES count)

INTELLIGENCE REPORTS:
{digest}

Respond with ONLY valid JSON in this exact format:
{{
  "narratives": [
    {{
      "title": "...",
      "strength": "STRONG",
      "direction": "Risk-Off",
      "summary": "...",
      "key_stories": 5,
      "trade_implication": "..."
    }}
  ]
}}"""

    try:
        # Use HTTP request to DeepSeek API
        import urllib.request, urllib.error

        api_key = provider.get('api_key', '')
        base_url = provider.get('base_url', 'https://api.deepseek.com/v1')
        model = provider.get('model', 'deepseek-chat')

        req_data = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a macro strategist. Respond with ONLY valid JSON, no markdown."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
        }).encode('utf-8')

        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))

        text = result['choices'][0]['message']['content'].strip()

        # Strip markdown code fences if present
        if text.startswith('```'):
            text = text.split('\n', 1)[1]
            if text.endswith('```'):
                text = text[:-3]

        narratives = json.loads(text)

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "story_count": len(stories),
            "model": model,
            "narratives": narratives.get('narratives', []),
        }

    except Exception as e:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "narratives": [],
            "fallback": True,
        }


def main():
    dry_run = '--dry-run' in sys.argv

    print("Narrative Brain v2.0")
    print(f"  Querying DB: {DB_PATH}")

    stories = query_top_stories(15)
    print(f"  Stories loaded: {len(stories)}")

    print(f"  Synthesizing narratives{' (dry run)' if dry_run else ' via AI'}...")
    result = synthesize_narratives(stories, dry_run=dry_run)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(NARRATIVES_PATH, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Written to {NARRATIVES_PATH}")

    if result.get('narratives'):
        for i, n in enumerate(result['narratives'], 1):
            print(f"  Narrative {i}: {n.get('title', '?')} [{n.get('strength', '?')}]")
    elif result.get('error'):
        print(f"  ⚠ Error: {result['error']}")

    if result.get('dry_run'):
        print("  ⚠ DRY RUN — pre-canned narratives, not AI-generated")


if __name__ == '__main__':
    main()
