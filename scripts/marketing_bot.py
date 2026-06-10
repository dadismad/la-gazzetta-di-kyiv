#!/usr/bin/env python3
"""
marketing_bot.py — Gazzetta di Kyiv Reddit Marketing Engine
Identifies high-value subreddits, drafts alpha-point posts from stories,
formats for manual review and interlinking.
"""

import json, os, sys
from datetime import datetime, timezone

PROJECT_ROOT = os.environ.get('GAZZETTA_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Target subreddits ──
TARGET_SUBREDDITS = [
    {'name': 'r/quant', 'focus': 'Quantitative finance, systematic strategies', 'relevance': 'Flow velocity, confidence models'},
    {'name': 'r/finance', 'focus': 'Professional finance', 'relevance': 'Capital flow analysis, institutional positioning'},
    {'name': 'r/geopolitics', 'focus': 'Geopolitical analysis', 'relevance': 'Contradiction-first narrative intelligence'},
    {'name': 'r/investing', 'focus': 'Retail investing', 'relevance': 'Trade ideas, THE PLAY, track record'},
    {'name': 'r/economics', 'focus': 'Economic analysis', 'relevance': 'Sovereign flows, macro regime shifts'},
    {'name': 'r/CryptoCurrency', 'focus': 'Crypto markets', 'relevance': 'Crypto capital flows, on-chain signals'},
    {'name': 'r/stocks', 'focus': 'Stock market', 'relevance': 'Equity flows, sector rotation'},
    {'name': 'r/wallstreetbets', 'focus': 'High-risk trading', 'relevance': 'Degen persona: directional bets, conviction'},
    {'name': 'r/Forex', 'focus': 'FX trading', 'relevance': 'DXY flows, currency regime shifts'},
    {'name': 'r/Commodities', 'focus': 'Commodities trading', 'relevance': 'Gold, oil, commodity flows'},
]

def load_stories():
    """Load current stories from data file."""
    stories_path = os.path.join(PROJECT_ROOT, 'data', 'stories.json')
    if not os.path.exists(stories_path):
        stories_path = os.path.join(PROJECT_ROOT, 'site', 'data', 'stories.json')
    with open(stories_path) as f:
        return json.load(f)

def match_stories_to_subreddits(stories):
    """Match stories to relevant subreddits based on entity tags and content."""
    matches = []
    
    keyword_map = {
        'r/quant': ['quant', 'model', 'velocity', 'correlation', 'signal', 'backtest', 'alpha', 'factor'],
        'r/finance': ['institutional', 'flow', 'capital', 'billion', 'treasury', 'bank', 'fund'],
        'r/geopolitics': ['geopolitic', 'war', 'sanctions', 'treaty', 'nato', 'ukraine', 'china', 'iran', 'russia'],
        'r/investing': ['portfolio', 'allocation', 'entry', 'target', 'stop', 'position'],
        'r/economics': ['gdp', 'inflation', 'fed', 'ecb', 'rate', 'yield', 'deficit', 'sovereign'],
        'r/CryptoCurrency': ['btc', 'eth', 'crypto', 'bitcoin', 'ethereum', 'stablecoin', 'defi', 'blockchain'],
        'r/stocks': ['equity', 'stock', 'spx', 'nasdaq', 'nvda', 'earnings', 'sector'],
        'r/wallstreetbets': ['yolo', 'moon', 'dump', 'pump', 'short', 'squeeze'],
        'r/Forex': ['dxy', 'usd', 'eur', 'jpy', 'forex', 'currency', 'fx'],
        'r/Commodities': ['gold', 'oil', 'wti', 'brent', 'copper', 'commodity', 'xau'],
    }
    
    for story in stories.get('stories', [])[:15]:  # Top 15 most recent
        headline = (story.get('headline') or '').lower()
        body = (story.get('summary') or story.get('reality') or '').lower()
        text = headline + ' ' + body
        
        entity_tags = story.get('entity_tags', {})
        assets = [a.lower() for a in entity_tags.get('assets', [])]
        geos = [g.lower() for g in entity_tags.get('geographies', [])]
        
        for sub in TARGET_SUBREDDITS:
            keywords = keyword_map.get(sub['name'], [])
            score = sum(1 for kw in keywords if kw in text)
            score += sum(2 for kw in keywords if any(kw in a for a in assets))
            score += sum(2 for kw in keywords if any(kw in g for g in geos))
            
            if score >= 2:
                matches.append({
                    'subreddit': sub['name'],
                    'story_id': story.get('story_id', 'unknown'),
                    'headline': story.get('headline', 'Untitled')[:120],
                    'relevance_score': score,
                    'suggested_angle': sub['relevance'],
                })
    
    return sorted(matches, key=lambda m: m['relevance_score'], reverse=True)

def generate_alpha_point(story):
    """Generate a Reddit-ready alpha point from a story."""
    headline = story.get('headline', '')[:100]
    summary = (story.get('summary') or story.get('reality') or '')[:200]
    
    cf = story.get('capital_flow', {})
    cf_line = ''
    if cf:
        amt = cf.get('amount_b', '')
        direction = cf.get('direction', '')
        asset = cf.get('asset_class', '')
        if amt and direction:
            cf_line = f"${amt}B {direction} {asset}. "
    
    play = story.get('the_play', '')
    play_line = f"THE PLAY: {play[:80]}" if play else ''
    
    story_id = story.get('story_id', '')
    url = f"https://www.lagazzettadikyiv.com/story.html?id={story_id}"
    
    post = f"{headline}\n\n{cf_line}{summary}\n\n{play_line}\n\nFull intel report: {url}"
    return post[:500]  # Reddit-friendly length

def main():
    print("═══ Gazzetta di Kyiv — Reddit Marketing Engine ═══\n")
    
    try:
        data = load_stories()
        stories = data.get('stories', [])
        print(f"Loaded {len(stories)} stories\n")
    except Exception as e:
        print(f"ERROR: Cannot load stories: {e}")
        sys.exit(1)
    
    # Match stories to subreddits
    matches = match_stories_to_subreddits({'stories': stories})
    
    print("── Top Story-Subreddit Matches ──")
    seen = set()
    for m in matches[:20]:
        key = (m['subreddit'], m['story_id'])
        if key in seen:
            continue
        seen.add(key)
        print(f"\n  {m['subreddit']} (score: {m['relevance_score']})")
        print(f"  ↳ {m['headline'][:90]}...")
        print(f"  ↳ Angle: {m['suggested_angle']}")
    
    # Generate alpha points for top stories
    print("\n── Alpha Points (top 5 stories) ──")
    for story in stories[:5]:
        post = generate_alpha_point(story)
        print(f"\n{'─'*60}")
        print(post)
        print(f"{'─'*60}")
    
    # Output JSON for automation
    output = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'matches': matches[:30],
        'top_alpha_points': [generate_alpha_point(s) for s in stories[:5]],
    }
    
    out_path = os.path.join(PROJECT_ROOT, 'data', 'marketing_candidates.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n✓ Saved {len(matches[:30])} matches to data/marketing_candidates.json")
    print("  Review before posting — these are DRAFTS, not automated posts.")

if __name__ == '__main__':
    main()
