#!/usr/bin/env python3
"""
Gazzetta di Kyiv — Story Market Data Enricher

Enriches stories.json with commodity prices, FX rates, VIX, yield curve data
from local market data files. Used by gazzetta-continuous-capital-flows cron.

Reads: data/stories.json + data/market_regime.json + data/alpha_vantage.json
Writes: site/data/stories.json (enriched)
"""

import json
import os
import sys
import datetime
from pathlib import Path

PROJECT = Path(os.environ.get('GAZZETTA_PROJECT', os.path.expanduser('~/projects/gazzetta-di-kyiv')))
STORIES_PATH = PROJECT / 'data' / 'stories.json'
REGIME_PATH = PROJECT / 'site' / 'data' / 'market_regime.json'
AV_PATH = PROJECT / 'data' / 'alpha_vantage.json'
OUTPUT_PATH = PROJECT / 'site' / 'data' / 'stories.json'

def load_json(path):
    """Load JSON file, return empty dict on failure."""
    if not path.exists():
        print(f'  [WARN] {path.name} not found')
        return {}
    try:
        return json.load(open(path))
    except Exception as e:
        print(f'  [WARN] Failed to load {path.name}: {e}')
        return {}

def main():
    print(f'[enrich_market_data] {datetime.datetime.utcnow().isoformat()}Z START')
    
    # Load sources
    stories_data = load_json(STORIES_PATH)
    regime = load_json(REGIME_PATH)
    av_data = load_json(AV_PATH)
    
    stories = stories_data.get('stories', [])
    if not stories:
        print('  No stories to enrich')
        return 0
    
    # Extract market context from regime
    regime_context = {}
    if regime:
        for ind in regime.get('indicators', []):
            regime_context[ind['indicator']] = {
                'direction': ind.get('direction', ind.get('level', 'N/A')),
                'strength': ind.get('strength', ind.get('score', 'N/A'))
            }
    
    # Extract commodity/FX/VIX data
    market_prices = {}
    if av_data:
        for name, quote in av_data.get('data', {}).items():
            if '05. price' in quote:
                market_prices[name] = {
                    'price': quote.get('05. price'),
                    'change_pct': quote.get('10. change percent', 'N/A')
                }
    
    # Enrich each story
    enriched_count = 0
    for s in stories:
        # Add market regime context
        if regime_context and 'market_regime' not in s:
            s['market_regime'] = regime_context
            enriched_count += 1
        
        # Add market prices if relevant
        if market_prices and 'market_prices' not in s:
            s['market_prices'] = market_prices
    
    # Write enriched stories
    output = dict(stories_data)
    output['stories'] = stories
    output['enriched_at'] = datetime.datetime.utcnow().isoformat() + 'Z'
    output['enriched_by'] = 'enrich_market_data.py'
    
    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
    json.dump(output, open(OUTPUT_PATH, 'w'), indent=2, ensure_ascii=False)
    
    print(f'  Enriched {len(stories)} stories ({enriched_count} with new market_regime field)')
    print(f'  Output: {OUTPUT_PATH}')
    print(f'[enrich_market_data] {datetime.datetime.utcnow().isoformat()}Z DONE')
    return 0

if __name__ == '__main__':
    sys.exit(main())
