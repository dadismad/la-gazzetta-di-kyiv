#!/usr/bin/env python3
from __future__ import annotations
import json, os
from collections import Counter
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(REPO, 'data', 'normalized', 'events_latest.json')
OUT = os.path.join(REPO, 'data', 'processed', 'narrative_intelligence_latest.json')

SEM = {
    'ai': ('US mega-cap AI cluster', 'capex concentration risk rises as narrative momentum extends'),
    'oil': ('OPEC+ and shipping corridor actors', 'energy shock premium can re-enter inflation path expectations'),
    'rates': ('Fed/ECB policy complex', 'discount-rate ambiguity amplifies cross-asset volatility'),
    'inflation': ('central banks and wage-setting actors', 'services stickiness can delay easing path'),
    'russia': ('Kremlin/NATO/EU', 'geopolitical escalation risk leaks into energy and defense premia'),
    'china': ('PBoC/State Council/export channels', 'stimulus narrative may outrun demand reality'),
    'crypto': ('ETF issuers and leveraged risk takers', 'liquidity reflexivity can front-run broad risk sentiment')
}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    d = json.load(open(INP, 'r', encoding='utf-8'))
    items = d.get('items', [])
    c = Counter()
    for ev in items:
        tags = ev.get('tags', []) or []
        if not tags and ev.get('topic'):
            tags = [str(ev.get('topic')).lower()]
        for t in tags:
            c[t] += 1

    top = c.most_common(12)
    setups, contradictions = [], []
    total = sum(v for _, v in top) or 1
    for k, v in top:
        actor, claim = SEM.get(k, ('policy/market actors', 'second-order effects are underpriced by consensus'))
        pbase = min(75, 45 + int(v * 2))
        pbull = max(10, int((100 - pbase) * 0.45))
        pbear = 100 - pbase - pbull
        setups.append({
            'setup_id': f'n2_{k}',
            'title': f'Narrative acceleration: {k}',
            'horizon': '24-72h',
            'thesis': claim,
            'actors': [actor],
            'incentives': ['preserve policy credibility', 'capture allocation flows'],
            'probability_base': pbase,
            'probability_bull': pbull,
            'probability_bear': pbear,
            'invalidation_triggers': [
                'Mention-share drops below 7d baseline for two cycles',
                'Cross-source confirmation weakens materially'
            ],
            'retail_execution': [
                'Use staged ETF entries with explicit invalidation',
                'Prefer defined-risk options in high-volatility windows'
            ],
            'confidence': round(min(0.9, 0.45 + v / max(total, 1)), 2),
            'citations': ['data/normalized/events_latest.json']
        })
        contradictions.append({
            'narrative': k,
            'claim_a': f'{k} is fully priced',
            'claim_b': f'{k} transmission effects remain underpriced',
            'urgency': 'high' if v >= 8 else 'medium',
            'invalidation_window': '24-72h'
        })

    regime = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'data_freshness_seconds': 3600,
        'source_count': len(set({x.get('source_id') for x in items})),
        'regime_label': 'Narrative Repricing Risk' if top else 'Insufficient Data',
        'risk_state': 'selective risk-off' if any(k in dict(top) for k in ['oil', 'rates', 'inflation', 'russia']) else 'mixed',
        'confidence': 0.72 if top else 0.3
    }

    out = {'generated_at': datetime.now(timezone.utc).isoformat(), 'setups': setups, 'contradictions': contradictions, 'regime': regime, 'source_events': len(items)}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps({'ok': True, 'setups': len(setups), 'output': OUT}))


if __name__ == '__main__':
    main()
