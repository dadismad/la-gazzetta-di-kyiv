#!/usr/bin/env python3
import csv
import json
import os
import sqlite3
import hashlib
from collections import Counter
from datetime import datetime, timezone, timedelta

BASE = os.path.expanduser('~/.hermes/data/social_umbrella')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DATA = os.path.join(REPO, 'data')
OUT_SITE = os.path.join(REPO, 'site')

os.makedirs(OUT_DATA, exist_ok=True)
os.makedirs(OUT_SITE, exist_ok=True)
os.makedirs(os.path.join(OUT_SITE, 'data'), exist_ok=True)
os.makedirs(os.path.join(OUT_SITE, 'api', 'v1', 'home'), exist_ok=True)

registry_json = os.path.join(BASE, 'source_registry_ranked.json')
events_db = os.path.join(BASE, 'events.db')

with open(registry_json, 'r') as f:
    registry = json.load(f)

since = datetime.now(timezone.utc) - timedelta(hours=24)
keywords = ['ukraine','russia','nato','eu','inflation','rates','oil','gas','ai','china','sanctions','ceasefire','drone','crypto','election']
NARRATIVE_SEMANTICS = {
    'ai': {
        'actors': ['Sam Altman', 'Jensen Huang', 'Microsoft', 'NVIDIA'],
        'svo': 'US hyperscalers increase AI capex and pull forward semiconductor demand',
        'claim': 'AI infrastructure spending is extending equity momentum while concentrating liquidity risk',
        'contradiction': 'Consensus says AI upside is fully priced, while compute bottlenecks imply further repricing',
        'manipulation': 'Headline selection bias toward product launches can hide margin and power-constraint risks',
        'transmission': 'Capex headlines -> growth expectations -> equity leadership -> duration sensitivity and USD spillovers',
        'repricing': 'NQ +1.5% to +4.0%; SOXX leads if breadth holds',
        'invalidation': 'Mega-cap guidance cuts or AI capex deferrals across two reporting cycles'
    },
    'eu': {
        'actors': ['European Commission', 'ECB', 'Germany', 'France'],
        'svo': 'EU institutions tighten industrial and fiscal responses to external shocks',
        'claim': 'Policy fragmentation risk inside Europe is underpriced in cross-asset correlation',
        'contradiction': 'Headline calm implies cohesion, but fiscal-energy divergence suggests rising dispersion',
        'manipulation': 'National headlines can downplay cross-border policy conflict and timeline slippage',
        'transmission': 'Policy signal -> sovereign spread expectations -> EUR risk premium -> equity factor rotation',
        'repricing': 'SX5E dispersion +2% to +5%; EURUSD two-way with downside skew on policy conflict',
        'invalidation': 'Coordinated fiscal package and stable energy forwards over multiple sessions'
    },
    'china': {
        'actors': ['Xi Jinping', 'PBoC', 'State Council', 'MOFCOM'],
        'svo': 'Chinese policymakers recalibrate stimulus while trade constraints reshape export channels',
        'claim': 'China macro impulse uncertainty is mispriced in cyclicals and commodity beta',
        'contradiction': 'Stimulus headlines suggest reflation, while private-demand weakness limits follow-through',
        'manipulation': 'Policy headlines may overstate immediacy while underreporting implementation lag',
        'transmission': 'Policy tone -> EM growth expectations -> commodity demand assumptions -> FX beta',
        'repricing': 'Copper/EM equities ±3% range; AUDCNH sensitivity rises in policy windows',
        'invalidation': 'Sustained PMIs and credit impulse confirmation across two data cycles'
    },
    'election': {
        'actors': ['White House', 'US Congress', 'European Parliament', 'party leaderships'],
        'svo': 'Election narratives alter fiscal and regulatory expectations across regions',
        'claim': 'Political transition risk is feeding risk premia faster than consensus models imply',
        'contradiction': 'Poll stability implies low risk, while policy path asymmetry keeps tail risk elevated',
        'manipulation': 'Campaign framing can amplify certainty and suppress policy implementation constraints',
        'transmission': 'Political probability shifts -> fiscal path repricing -> rates vol -> sector leadership changes',
        'repricing': 'Rates vol +10% to +25%; policy-sensitive sectors swing 2% to 6%',
        'invalidation': 'Cross-party convergence on fiscal and trade policy trajectories'
    },
    'gas': {
        'actors': ['Gazprom', 'QatarEnergy', 'European utilities', 'energy ministers'],
        'svo': 'Gas supply narratives influence European cost structures and inflation expectations',
        'claim': 'Gas transport and storage risk remains underweighted in equity and FX pricing',
        'contradiction': 'Inventory comfort implies stability, while routing fragility preserves upside price risk',
        'manipulation': 'Spot-price focus can obscure forward-curve stress and storage quality differences',
        'transmission': 'Gas headlines -> inflation expectations -> real rates path -> equity margin assumptions',
        'repricing': 'EU utilities/chemicals dispersion +3% to +8%; EUR volatility firm on supply shocks',
        'invalidation': 'Storage trajectory beats seasonal path with stable LNG arrivals'
    },
    'oil': {
        'actors': ['OPEC+', 'Saudi Aramco', 'IEA', 'US shale producers'],
        'svo': 'Producers manage supply while conflict headlines alter shipping and insurance costs',
        'claim': 'Energy risk premium remains underpriced when geopolitical supply corridors are unstable',
        'contradiction': 'Spot calm suggests normalization, but tanker risk and inventory drawdowns suggest fragility',
        'manipulation': 'Short-term price relief can be over-amplified while logistics stress is under-reported',
        'transmission': 'Energy headlines -> inflation expectations -> rates volatility -> equity and FX rotation',
        'repricing': 'Brent +2% to +6% in shock windows; airlines/transport underperform; gold supported',
        'invalidation': 'Verified de-escalation with sustained inventory rebuild and freight normalization'
    },
    'inflation': {
        'actors': ['Federal Reserve', 'ECB', 'BLS', 'Eurostat'],
        'svo': 'Inflation prints reset central-bank reaction functions and real-yield expectations',
        'claim': 'Disinflation confidence is fragile and vulnerable to energy and wage second-round effects',
        'contradiction': 'Core moderation implies easing path, while services stickiness delays policy pivot',
        'manipulation': 'Single-print framing can hide composition effects and revision risk',
        'transmission': 'Inflation surprise -> terminal-rate repricing -> duration and growth-beta reset',
        'repricing': 'UST 2Y/10Y move 8-18bp window; growth-value rotation 2% to 5%',
        'invalidation': 'Sequential core cooling plus easing wage indicators across releases'
    },
    'rates': {
        'actors': ['Federal Reserve', 'ECB', 'UST market', 'Bund market'],
        'svo': 'Rate expectations re-anchor portfolio duration and equity valuation assumptions',
        'claim': 'Rates volatility remains a primary transmission channel for cross-asset repricing',
        'contradiction': 'Soft-landing consensus implies lower vol, while policy ambiguity keeps vol supply constrained',
        'manipulation': 'Forward-guidance headlines may overstate certainty around reaction functions',
        'transmission': 'Rates path -> discount-rate reset -> equity multiple compression/expansion -> FX carry shifts',
        'repricing': 'MOVE regime upshift; duration-sensitive equities ±3% to 7%',
        'invalidation': 'Consistent central-bank signaling and realized inflation convergence'
    },
    'russia': {
        'actors': ['Kremlin', 'Russian MoD', 'EU Council', 'NATO'],
        'svo': 'Conflict escalation narratives affect sanctions expectations and defense-energy pricing',
        'claim': 'Geopolitical escalation risk is repeatedly under-discounted in European risk assets',
        'contradiction': 'Frontline stalemate implies contained risk, while sanctions and logistics dynamics keep spillovers alive',
        'manipulation': 'War coverage can prioritize tactical headlines over supply-chain strategic impact',
        'transmission': 'Conflict headline -> sanctions premium -> energy/defense repricing -> regional risk premium',
        'repricing': 'European defensives and defense names +2% to +6%; cyclical beta under pressure',
        'invalidation': 'Verified durable de-escalation and sanctions path relaxation'
    },
    'nato': {
        'actors': ['NATO', 'US DoD', 'European defense ministries', 'Ukrainian command'],
        'svo': 'Alliance posture updates alter procurement, fiscal defense burdens, and risk perception',
        'claim': 'Defense-cycle extension has longer earnings visibility than consensus assumes',
        'contradiction': 'Budget fatigue narrative implies slowdown, while procurement pipelines suggest persistence',
        'manipulation': 'Announcement headlines may overstate immediate capacity without delivery timelines',
        'transmission': 'Posture shifts -> procurement cycle -> industrial order books -> fiscal mix expectations',
        'repricing': 'Defense complex outperformance +3% to +9%; sovereign spread sensitivity rises',
        'invalidation': 'Procurement delays and coalition budget retrenchment'
    },
    'crypto': {
        'actors': ['SEC', 'Major exchanges', 'ETF issuers', 'Institutional allocators'],
        'svo': 'Regulatory and liquidity signals drive crypto beta and risk appetite spillovers',
        'claim': 'Crypto risk-on reflex can front-run broader liquidity shifts but remains shock-sensitive',
        'contradiction': 'ETF inflow narrative implies stability, while leverage concentration increases fragility',
        'manipulation': 'Flow headlines can omit concentration and liquidation cascade risk',
        'transmission': 'Crypto flows -> risk sentiment -> high-beta equity participation -> vol spillovers',
        'repricing': 'BTC/ETH ±4% to ±12% windows; high-beta tech correlation episodically rises',
        'invalidation': 'Sustained deleveraging with stable spot participation and lower funding stress'
    }
}

def semantic_for_topic(topic: str):
    default = {
        'actors': ['European Commission', 'Federal Reserve', 'Global macro funds', 'Major corporates'],
        'svo': f'{topic.upper()} headlines change policy expectations and reprice cross-asset risk',
        'claim': f'{topic.upper()} narrative intensity is shifting positioning behaviour across markets',
        'contradiction': f'{topic.upper()} appears priced in, yet second-order effects remain underweighted',
        'manipulation': 'Framing distortion and omission risk can exaggerate certainty in fast headlines',
        'transmission': 'Headline flow -> liquidity regime -> positioning -> cross-asset repricing',
        'repricing': 'Risk assets +1% to +3% in risk-on continuation; defensive assets bid on volatility spikes',
        'invalidation': 'Narrative share falls below 7-day baseline for two consecutive cycles'
    }
    return NARRATIVE_SEMANTICS.get(topic, default)
counts = Counter()
recent_items = 0

if os.path.exists(events_db):
    con = sqlite3.connect(events_db)
    cur = con.cursor()
    try:
        cur.execute("SELECT title, published_at, url FROM events")
        rows = cur.fetchall()
        for title, published_at, url in rows:
            if not title:
                continue
            t = title.lower()
            in_window = True
            if published_at:
                try:
                    dt = datetime.fromisoformat(str(published_at).replace('Z','+00:00'))
                    in_window = dt >= since
                except Exception:
                    in_window = True
            if not in_window:
                continue
            recent_items += 1
            for k in keywords:
                if k in t:
                    counts[k] += 1
    finally:
        con.close()

narratives = [{'topic':k,'mentions_24h':v} for k,v in counts.most_common(15)]

narrative_reviews = []
for n in narratives:
    topic = n['topic']
    mentions = n['mentions_24h']
    intensity = round(min(100, mentions * 4.2), 1)
    momentum = 'high' if mentions >= 15 else ('medium' if mentions >= 6 else 'low')
    bias = 'risk-on' if topic in ['ai','crypto','technology'] else ('risk-off' if topic in ['war','sanctions','inflation','rates','oil','gas'] else 'mixed')
    review = (
        f"Signal strength {intensity}/100 with {momentum} momentum. "
        f"Regime bias appears {bias}. "
        f"Interpretation: short-term desks should treat this narrative as "
        f"{'position-relevant and timing-sensitive' if intensity >= 60 else 'context-relevant with selective execution'}; "
        f"cross-check with rates, energy, and policy headlines for confirmation before sizing."
    )
    narrative_reviews.append({
        'topic': topic,
        'mentions_24h': mentions,
        'intensity_score': intensity,
        'momentum': momentum,
        'review': review,
        'semantics': semantic_for_topic(topic),
    })

generated_at = datetime.now(timezone.utc).isoformat()
summary = {
    'generated_at': generated_at,
    'recent_items_24h': recent_items,
    'top_narratives': narratives,
    'narrative_reviews': narrative_reviews,
}

def _scenario_triplet(mentions: int):
    base = min(70, 45 + int(mentions * 0.8))
    bull_cap = max(5, 100 - base - 5)
    bull = min(bull_cap, 20 + int(mentions * 0.3))
    bear = 100 - base - bull
    return base, bull, bear

def _confidence_for_mentions(mentions: int):
    if mentions >= 20:
        return 0.82
    if mentions >= 10:
        return 0.72
    if mentions >= 5:
        return 0.62
    return 0.54

source_count = len(registry.get('sources', []))
freshness = max(0, int((datetime.now(timezone.utc) - since).total_seconds()))

intelligence_objects = []
for i, item in enumerate(narrative_reviews[:12], start=1):
    mentions = int(item.get('mentions_24h', 0) or 0)
    base_p, bull_p, bear_p = _scenario_triplet(mentions)
    topic = item.get('topic', 'macro')
    io_id = f"io_{hashlib.md5(f'{topic}-{i}'.encode()).hexdigest()[:10]}"
    intelligence_objects.append({
        'id': io_id,
        'event': f"Narrative acceleration: {topic}",
        'narrative_primary': topic,
        'narrative_hidden': 'Second-order effects underpriced by consensus',
        'beneficiaries': ['momentum-aligned assets', 'early thematic allocators'],
        'losers': ['late consensus positioning', 'mean-reversion-only books'],
        'cross_asset_impacts': [
            {'asset_class': 'equities', 'direction': 'mixed', 'note': 'sector dispersion likely to rise'},
            {'asset_class': 'rates', 'direction': 'watch', 'note': 'policy-path sensitivity remains elevated'},
            {'asset_class': 'commodities', 'direction': 'conditional', 'note': 'headline-dependent transmission'}
        ],
        'scenarios': [
            {'name': 'base', 'probability': base_p},
            {'name': 'bull', 'probability': bull_p},
            {'name': 'bear', 'probability': bear_p}
        ],
        'retail_setups': [
            'Use staged entries in liquid ETFs',
            'Prefer defined-risk options structures for high-volatility narratives'
        ],
        'invalidations': [
            'Narrative mention share drops below 7d baseline for 2 consecutive cycles',
            'Cross-source confirmation weakens materially'
        ],
        'confidence': _confidence_for_mentions(mentions),
        'citations': ['events.db (rolling 24h titles)'],
        'updated_at': generated_at
    })

regime_payload = {
    'generated_at': generated_at,
    'data_freshness_seconds': freshness,
    'source_count': source_count,
    'regime_label': 'Narrative Transition',
    'risk_state': 'neutral',
    'confidence': 0.68,
    'updated_at': generated_at
}

setups_payload = {
    'generated_at': generated_at,
    'data_freshness_seconds': freshness,
    'source_count': source_count,
    'items': [
        {
            'setup_id': io['id'],
            'title': io['event'],
            'horizon': '3d',
            'thesis': io['narrative_hidden'],
            'probability_base': io['scenarios'][0]['probability'],
            'probability_bull': io['scenarios'][1]['probability'],
            'probability_bear': io['scenarios'][2]['probability'],
            'invalidation_triggers': io['invalidations'],
            'retail_execution': io['retail_setups'],
            'confidence': io['confidence'],
            'citations': io['citations']
        } for io in intelligence_objects
    ]
}

divergences_payload = {
    'generated_at': generated_at,
    'data_freshness_seconds': freshness,
    'source_count': source_count,
    'items': [
        {
            'narrative': io['narrative_primary'],
            'market_belief': 'Consensus expects smooth continuation',
            'observed_reality': 'Signal remains noisy with asymmetric downside branches',
            'divergence_score': round(0.45 + (idx * 0.03), 2),
            'evidence_links': io['citations']
        } for idx, io in enumerate(intelligence_objects[:12])
    ]
}

contradictions_payload = {
    'generated_at': generated_at,
    'data_freshness_seconds': freshness,
    'source_count': source_count,
    'items': [
        {
            'contradiction_id': f"cx_{idx+1:03d}",
            'claim_a': f"{io['narrative_primary']} is fully priced",
            'claim_b': f"{io['narrative_primary']} still accelerating in headline share",
            'contradiction_score': round(0.52 + (idx * 0.02), 2),
            'urgency': 'medium' if idx < 6 else 'low',
            'invalidation_window': '24-72h'
        } for idx, io in enumerate(intelligence_objects[:12])
    ]
}

aftershocks_payload = {
    'generated_at': generated_at,
    'data_freshness_seconds': freshness,
    'source_count': source_count,
    'items': [
        {
            'first_order_event': io['event'],
            'second_order_path': ['positioning shift', 'liquidity repricing', 'sector dispersion'],
            'expected_lag': '24-96h',
            'exposed_assets': ['SPY', 'QQQ', 'TLT', 'BTC']
        } for io in intelligence_objects[:12]
    ]
}

schema_payload = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    'title': 'IntelligenceObject',
    'type': 'object',
    'required': ['id', 'event', 'narrative_primary', 'scenarios', 'retail_setups', 'invalidations', 'confidence', 'citations', 'updated_at'],
    'properties': {
        'id': {'type': 'string'},
        'event': {'type': 'string'},
        'narrative_primary': {'type': 'string'},
        'narrative_hidden': {'type': 'string'},
        'beneficiaries': {'type': 'array', 'items': {'type': 'string'}},
        'losers': {'type': 'array', 'items': {'type': 'string'}},
        'cross_asset_impacts': {'type': 'array', 'items': {'type': 'object'}},
        'scenarios': {
            'type': 'array',
            'minItems': 3,
            'items': {
                'type': 'object',
                'required': ['name', 'probability'],
                'properties': {
                    'name': {'type': 'string'},
                    'probability': {'type': 'integer', 'minimum': 0, 'maximum': 100}
                }
            }
        },
        'retail_setups': {'type': 'array', 'items': {'type': 'string'}},
        'invalidations': {'type': 'array', 'items': {'type': 'string'}},
        'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'citations': {'type': 'array', 'items': {'type': 'string'}},
        'updated_at': {'type': 'string'}
    }
}

with open(os.path.join(OUT_DATA,'narratives.json'),'w') as f:
    json.dump(summary,f,indent=2)
with open(os.path.join(OUT_SITE,'data','narratives.json'),'w') as f:
    json.dump(summary,f,indent=2)

# Stories in Play editorial package (if present in data/, publish through to site/data/)
stories_in_play_path = os.path.join(OUT_DATA, 'stories_in_play.json')
if os.path.exists(stories_in_play_path):
    with open(stories_in_play_path, 'r', encoding='utf-8') as sf:
        stories_payload = json.load(sf)
    with open(os.path.join(OUT_SITE, 'data', 'stories_in_play.json'), 'w', encoding='utf-8') as sf:
        json.dump(stories_payload, sf, indent=2)

with open(os.path.join(OUT_DATA,'intelligence_objects.json'),'w') as f:
    json.dump({'generated_at': generated_at, 'items': intelligence_objects},f,indent=2)
with open(os.path.join(OUT_SITE,'data','intelligence_objects.json'),'w') as f:
    json.dump({'generated_at': generated_at, 'items': intelligence_objects},f,indent=2)

with open(os.path.join(OUT_DATA,'source_registry_ranked.json'),'w') as f:
    json.dump(registry,f,indent=2)
with open(os.path.join(OUT_SITE,'data','source_registry_ranked.json'),'w') as f:
    json.dump(registry,f,indent=2)

with open(os.path.join(OUT_DATA,'source_registry_ranked.csv'),'w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=['platform','source_id','name','url','popularity','engagement','score','access','description'])
    w.writeheader(); w.writerows(registry.get('sources',[]))

repr_data = {'techniques': []}
try:
    with open(os.path.join(REPO, 'data', 'representation_techniques.json'),'r') as rf:
        repr_data = json.load(rf)
except Exception:
    repr_data = {'techniques': []}
with open(os.path.join(OUT_SITE,'data','representation_techniques.json'),'w') as f:
    json.dump(repr_data,f,indent=2)

api_home_dir = os.path.join(OUT_SITE, 'api', 'v1', 'home')
with open(os.path.join(api_home_dir, 'regime.json'),'w') as f:
    json.dump(regime_payload,f,indent=2)
with open(os.path.join(api_home_dir, 'setups.json'),'w') as f:
    json.dump(setups_payload,f,indent=2)
with open(os.path.join(api_home_dir, 'divergences.json'),'w') as f:
    json.dump(divergences_payload,f,indent=2)
with open(os.path.join(api_home_dir, 'contradictions.json'),'w') as f:
    json.dump(contradictions_payload,f,indent=2)
with open(os.path.join(api_home_dir, 'aftershocks.json'),'w') as f:
    json.dump(aftershocks_payload,f,indent=2)
with open(os.path.join(OUT_SITE, 'api', 'v1', 'intelligence_object.schema.json'),'w') as f:
    json.dump(schema_payload,f,indent=2)

# Phase 3 publish hard gates
for i, s in enumerate(setups_payload.get('items', []), start=1):
    probs = [s.get('probability_base'), s.get('probability_bull'), s.get('probability_bear')]
    if any(p is None for p in probs):
        raise RuntimeError(f'Publish gate failed: missing probabilities at setup #{i}')
    if sum(probs) != 100:
        raise RuntimeError(f'Publish gate failed: probabilities must sum to 100 at setup #{i}, got {sum(probs)}')
    if min(probs) < 0:
        raise RuntimeError(f'Publish gate failed: negative probability at setup #{i}')
    if not s.get('invalidation_triggers'):
        raise RuntimeError(f'Publish gate failed: missing invalidation triggers at setup #{i}')
    if s.get('confidence') is None:
        raise RuntimeError(f'Publish gate failed: missing confidence at setup #{i}')
    if not s.get('citations'):
        raise RuntimeError(f'Publish gate failed: missing citations at setup #{i}')

html = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gazzetta di Kyiv — Data Desk</title>
<style>body{{font-family:Arial,sans-serif;background:#0b1020;color:#e7ecff;margin:24px}}h1{{margin:0 0 8px}}.muted{{color:#a9b3d6}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{border-bottom:1px solid #24305d;padding:8px;text-align:left}}a{{color:#8ec5ff}}</style></head><body>
<h1>Gazzetta di Kyiv</h1><div class="muted">Continuous source intelligence + narrative interpretation.</div>
<p>Updated: {summary['generated_at']}</p>
<h2>Top Narratives (24h)</h2>
<table><thead><tr><th>Narrative</th><th>Actors</th><th>Proposition (SVO)</th><th>Claim/Thesis</th><th>Contradiction</th><th>Manipulation risk</th><th>Transmission</th><th>Repricing</th><th>Invalidation</th><th>Mentions(24h)</th><th>Intensity</th><th>Momentum</th></tr></thead><tbody>
{''.join([f"<tr><td>{n['topic']}</td><td>{', '.join(n['semantics']['actors'])}</td><td>{n['semantics']['svo']}</td><td>{n['semantics']['claim']}</td><td>{n['semantics']['contradiction']}</td><td>{n['semantics']['manipulation']}</td><td>{n['semantics']['transmission']}</td><td>{n['semantics']['repricing']}</td><td>{n['semantics']['invalidation']}</td><td>{n['mentions_24h']}</td><td>{n['intensity_score']}</td><td>{n['momentum']}</td></tr>" for n in narrative_reviews]) or '<tr><td colspan="12">No data yet</td></tr>'}
</tbody></table>
<h2>Written Narrative Reviews</h2>
{''.join([f"<article style='margin:14px 0;padding:10px 12px;background:#121a33;border-radius:10px'><h3 style='margin:0 0 6px'>{n['topic'].upper()}</h3><p style='margin:0 0 4px;color:#c7d4ff'>Mentions: {n['mentions_24h']} | Intensity: {n['intensity_score']} | Momentum: {n['momentum']}</p><p style='margin:0'>{n['review']}</p></article>" for n in narrative_reviews]) or '<p>No written reviews yet.</p>'}
<h2>Top Sources</h2>
<table><thead><tr><th>Source</th><th>Platform</th><th>Score</th><th>Access</th><th>Description</th></tr></thead><tbody>
{''.join([f"<tr><td><a target='_blank' href='{s['url']}'>{s['name']}</a></td><td>{s['platform']}</td><td>{s['score']}</td><td>{s['access']}</td><td>{(s.get('description') or '')}</td></tr>" for s in sorted(registry.get('sources',[]), key=lambda x:(x.get('access',''), -(float(x.get('score',0) or 0))))[:60]])}
</tbody></table>
<h2>Representation Techniques Research</h2>
{''.join([f"<div style='margin:10px 0;padding:8px 10px;background:#11172c;border-radius:8px'><b>{t['technique']}</b> — evidence {t['evidence_count']}, priority {t['adoption_priority']}<br>{t['implementation_note']}</div>" for t in repr_data.get('techniques',[])[:10]]) or '<p>No techniques available yet.</p>'}
</body></html>'''

with open(os.path.join(OUT_SITE,'data.html'),'w') as f:
    f.write(html)

index_path = os.path.join(OUT_SITE, 'index.html')
if os.path.exists(index_path):
    index_txt = open(index_path, 'r', encoding='utf-8', errors='ignore').read().lower()
    banned = ['intensity', 'momentum', 'signal strength', 'confidence_bands', 'yield']
    if any(b in index_txt for b in banned):
        raise RuntimeError('Homepage contract violation: quant/technical terms detected on retail homepage index.html')

print(json.dumps({
    'ok': True,
    'narratives': len(narratives),
    'recent_items_24h': recent_items,
    'api_endpoints_written': [
        '/api/v1/home/regime.json',
        '/api/v1/home/setups.json',
        '/api/v1/home/divergences.json',
        '/api/v1/home/contradictions.json',
        '/api/v1/home/aftershocks.json'
    ]
}))
