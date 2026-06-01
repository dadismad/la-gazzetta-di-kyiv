#!/usr/bin/env python3
from __future__ import annotations
import json, os, re
from collections import Counter, defaultdict
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(REPO, 'data', 'normalized', 'events_latest.json')
OUT = os.path.join(REPO, 'data', 'processed', 'narrative_intelligence_latest.json')

SEM = {
    'ai': {
        'actors': ['OpenAI', 'Microsoft', 'NVIDIA', 'Amazon'],
        'claim': 'AI capex concentration risk is rising while narrative momentum stays strong',
        'incentives': ['capture compute rents', 'defend platform distribution'],
    },
    'oil': {
        'actors': ['OPEC+', 'Saudi Aramco', 'shipping insurers'],
        'claim': 'Energy corridor fragility can reprice inflation expectations quickly',
        'incentives': ['defend fiscal revenues', 'manage supply optics'],
    },
    'rates': {
        'actors': ['Federal Reserve', 'ECB', 'rates desks'],
        'claim': 'Rate-path ambiguity remains the key cross-asset transmission channel',
        'incentives': ['preserve policy credibility', 'stabilize inflation expectations'],
    },
    'inflation': {
        'actors': ['BLS', 'Eurostat', 'central banks'],
        'claim': 'Disinflation confidence is vulnerable to services and energy stickiness',
        'incentives': ['anchor expectations', 'avoid policy whipsaw'],
    },
    'russia': {
        'actors': ['Kremlin', 'EU Council', 'NATO'],
        'claim': 'Geopolitical escalation tails are underweighted in regional risk premia',
        'incentives': ['preserve strategic leverage', 'shape sanction pathways'],
    },
    'china': {
        'actors': ['PBoC', 'State Council', 'export manufacturers'],
        'claim': 'Stimulus messaging may outpace private-demand follow-through',
        'incentives': ['stabilize growth optics', 'support employment channels'],
    },
    'crypto': {
        'actors': ['ETF issuers', 'major exchanges', 'leveraged traders'],
        'claim': 'Liquidity reflexivity can extend risk-on sentiment but increases fragility',
        'incentives': ['grow flow capture', 'maintain market share'],
    },
}

KEYWORD_TAGS = ['inflation','rates','oil','gas','ai','nato','ukraine','russia','china','election','crypto']
ENTITY_PATTERNS = [
    (r'\bfed\b|federal reserve', 'Federal Reserve'),
    (r'\becb\b', 'ECB'),
    (r'\bnato\b', 'NATO'),
    (r'\bopec\+?\b', 'OPEC+'),
    (r'openai', 'OpenAI'),
    (r'nvidia', 'NVIDIA'),
    (r'microsoft', 'Microsoft'),
    (r'xi\s+j(in|i)ping|\bpboc\b|state council', 'Chinese policy complex'),
    (r'kremlin|russia', 'Kremlin/Russia'),
]


def infer_tags(text: str):
    t = text.lower()
    return [k for k in KEYWORD_TAGS if re.search(rf'\b{re.escape(k)}\b', t)]


def extract_entities(text: str):
    t = text.lower()
    out = []
    for pat, name in ENTITY_PATTERNS:
        if re.search(pat, t):
            out.append(name)
    return out


def safe_probs(base: int):
    base = max(40, min(80, base))
    bull = max(8, int((100 - base) * 0.42))
    bear = 100 - base - bull
    return base, bull, bear


def topic_claim(topic: str, evidence_titles: list[str]):
    sem = SEM.get(topic)
    if sem:
        return sem['claim']
    # fallback claim from observed words in top titles
    joined = ' '.join(evidence_titles).lower()
    if 'deal' in joined or 'talks' in joined:
        return f'{topic} narrative is sensitive to negotiation headlines and repricing whipsaws'
    if 'rates' in joined or 'inflation' in joined:
        return f'{topic} narrative can re-anchor discount-rate expectations faster than consensus assumes'
    return f'{topic} second-order effects remain underpriced by consensus'


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    d = json.load(open(INP, 'r', encoding='utf-8'))
    items = d.get('items', [])

    tag_count = Counter()
    topic_count = Counter()
    evidence_by_topic = defaultdict(list)
    actors_by_topic = defaultdict(Counter)

    for ev in items:
        txt = f"{ev.get('title','')}\n{ev.get('text','')}"
        tags = ev.get('tags', []) or infer_tags(txt)
        topic = (ev.get('topic') or '').lower().strip() or 'macro'

        if tags:
            for t in tags:
                tag_count[t] += 1
                evidence_by_topic[t].append(ev.get('title',''))
                for a in extract_entities(txt):
                    actors_by_topic[t][a] += 1
        else:
            topic_count[topic] += 1
            evidence_by_topic[topic].append(ev.get('title',''))
            for a in extract_entities(txt):
                actors_by_topic[topic][a] += 1

    combined = Counter(tag_count)
    combined.update(topic_count)
    top = combined.most_common(12)

    setups, contradictions = [], []
    total = sum(v for _, v in top) or 1
    for k, v in top:
        sem = SEM.get(k, {})
        evidence_titles = evidence_by_topic.get(k, [])[:6]
        claim = topic_claim(k, evidence_titles)

        named_actors = [a for a, _ in actors_by_topic.get(k, Counter()).most_common(4)]
        actors = named_actors or sem.get('actors') or ['policy and market actors']
        incentives = sem.get('incentives') or ['preserve policy credibility', 'capture allocation flows']

        # confidence quality scales with evidence breadth
        src_breadth = len(set((x.get('source_id') for x in items if (k in (x.get('tags') or []) or (x.get('topic') or '').lower() == k))))
        conf = round(min(0.9, 0.42 + (v / max(total, 1)) + min(0.12, src_breadth * 0.02)), 2)

        pbase, pbull, pbear = safe_probs(44 + int(v * 2))
        setups.append({
            'setup_id': f'n21_{k}',
            'title': f'Narrative acceleration: {k}',
            'horizon': '24-72h',
            'thesis': claim,
            'actors': actors,
            'incentives': incentives,
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
            'confidence': conf,
            'citations': ['data/normalized/events_latest.json'],
            'evidence_titles': evidence_titles[:3],
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
        'source_count': len(set([x.get('source_id') for x in items if x.get('source_id')])),
        'regime_label': 'Narrative Repricing Risk' if top else 'Insufficient Data',
        'risk_state': 'selective risk-off' if any(k in dict(top) for k in ['oil', 'rates', 'inflation', 'russia']) else 'mixed',
        'confidence': 0.74 if top else 0.3
    }

    out = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'setups': setups,
        'contradictions': contradictions,
        'regime': regime,
        'source_events': len(items),
        'method': 'v2.1 semantic extraction + quality-ready output'
    }
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps({'ok': True, 'setups': len(setups), 'output': OUT}))


if __name__ == '__main__':
    main()
