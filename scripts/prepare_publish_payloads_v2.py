#!/usr/bin/env python3
from __future__ import annotations
import json, os, random
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(REPO, 'data', 'processed', 'narrative_intelligence_latest.json')
SITE_HOME = os.path.join(REPO, 'site', 'api', 'v1', 'home')
PUBLISH_DIR = os.path.join(REPO, 'data', 'publish')
TELEGRAM_OUT = os.path.join(PUBLISH_DIR, 'telegram_latest.md')
REDDIT_OUT = os.path.join(PUBLISH_DIR, 'reddit_latest.md')
MANIFEST_OUT = os.path.join(PUBLISH_DIR, 'publish_manifest.json')
CTA_LIB = os.path.join(REPO, 'data', 'cta_library.json')

HOMEPAGE = 'https://pureciclismo.github.io/gazzetta-di-kyiv/'
SETUPS_API = 'https://pureciclismo.github.io/gazzetta-di-kyiv/api/v1/home/setups.json'
REGIME_API = 'https://pureciclismo.github.io/gazzetta-di-kyiv/api/v1/home/regime.json'
CONTRADICTIONS_API = 'https://pureciclismo.github.io/gazzetta-di-kyiv/api/v1/home/contradictions.json'


def ensure(p: str):
    os.makedirs(p, exist_ok=True)


def pick_cta(channel: str, fallback: str):
    if not os.path.exists(CTA_LIB):
        return fallback
    try:
        lib = json.load(open(CTA_LIB, 'r', encoding='utf-8'))
        choices = lib.get(channel, [])
        if not choices:
            return fallback
        return random.choice(choices).replace('{website_url}', HOMEPAGE)
    except Exception:
        return fallback


def first(items, default='n/a'):
    if not items:
        return default
    return str(items[0])


def as_pct(v, default='-'):
    try:
        return f"{int(v)}%"
    except Exception:
        return default


def build_telegram(regime: dict, setups: list[dict]) -> str:
    """
    Telegram style: compact, scannable, retail-first.
    Target structure:
    1) Risk Regime (1 line)
    2) Asset Repricing Map (up to 3 bullets)
    3) Most Probable 24–72h Path (2 bullets incl. invalidation)
    """
    lead = setups[0] if setups else {}
    top3 = setups[:3]

    lines = []
    lines.append(f"Risk Regime: {regime.get('regime_label','Insufficient Data')} ({regime.get('risk_state','mixed')})")
    lines.append('')
    lines.append('Asset Repricing Map:')
    for s in top3:
        title = s.get('title', 'No setup')
        pb = as_pct(s.get('probability_base'))
        lines.append(f"• {title} — base {pb}")
    lines.append('')
    lines.append('Most Probable 24–72h Path:')
    lines.append(f"• Base case: {lead.get('thesis','No thesis')} ({as_pct(lead.get('probability_base'))})")
    lines.append(f"• Flip trigger: {first(lead.get('invalidation_triggers', []))}")
    lines.append('')
    lines.append(pick_cta('telegram', f'Full briefing and positioning map: {HOMEPAGE}'))

    return '\n'.join(lines)


def build_reddit(regime: dict, setups: list[dict]) -> str:
    """
    Reddit style: discussion-friendly with explicit logic chain + evidence links.
    """
    lead = setups[0] if setups else {}
    actors = ', '.join((lead.get('actors') or ['policy/market actors'])[:4])

    lines = []
    lines.append('## La Gazzetta di Kyiv — Market Narrative Thread')
    lines.append('')
    lines.append(f"**Regime snapshot:** {regime.get('regime_label','Insufficient Data')} ({regime.get('risk_state','mixed')})")
    lines.append(f"**Main claim:** {lead.get('thesis','No thesis')}")
    lines.append(f"**Actors driving this:** {actors}")
    lines.append(
        f"**24–72h probability path:** base {as_pct(lead.get('probability_base'))} / "
        f"bull {as_pct(lead.get('probability_bull'))} / bear {as_pct(lead.get('probability_bear'))}"
    )
    lines.append(f"**Invalidation trigger:** {first(lead.get('invalidation_triggers', []))}")
    lines.append('')
    lines.append('Why this matters for positioning:')
    lines.append('- Narrative intensity can reprice risk faster than fundamentals catch up.')
    lines.append('- Cross-asset confirmation (rates, USD, energy, equity breadth) decides follow-through.')
    lines.append('- If confirmation fails, unwind risk rises quickly.')
    lines.append('')
    lines.append('Evidence links:')
    lines.append(f'- Homepage: {HOMEPAGE}')
    lines.append(f'- Regime API: {REGIME_API}')
    lines.append(f'- Setups API: {SETUPS_API}')
    lines.append(f'- Contradictions API: {CONTRADICTIONS_API}')
    lines.append('')
    lines.append(pick_cta('reddit', f'Full narrative dossier and data links: {HOMEPAGE}'))
    lines.append('')
    lines.append('READY_FOR_DEVVIT_POST')

    return '\n'.join(lines)


def main():
    d = json.load(open(INP, 'r', encoding='utf-8'))
    setups = d.get('setups', [])
    contradictions = d.get('contradictions', [])
    regime = d.get('regime', {})

    ensure(SITE_HOME)
    ensure(PUBLISH_DIR)

    # Site payloads (ecosystem API contract)
    json.dump({'generated_at': d.get('generated_at'), 'items': setups}, open(os.path.join(SITE_HOME, 'setups.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump({'generated_at': d.get('generated_at'), 'items': contradictions}, open(os.path.join(SITE_HOME, 'contradictions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(regime, open(os.path.join(SITE_HOME, 'regime.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    tg = build_telegram(regime, setups)
    rd = build_reddit(regime, setups)

    open(TELEGRAM_OUT, 'w', encoding='utf-8').write(tg)
    open(REDDIT_OUT, 'w', encoding='utf-8').write(rd)

    manifest = {
        'ok': True,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'inputs': {'setups': len(setups), 'contradictions': len(contradictions)},
        'outputs': {
            'telegram_markdown': TELEGRAM_OUT,
            'reddit_markdown': REDDIT_OUT,
            'site_regime_api': os.path.join(SITE_HOME, 'regime.json'),
            'site_setups_api': os.path.join(SITE_HOME, 'setups.json'),
            'site_contradictions_api': os.path.join(SITE_HOME, 'contradictions.json')
        },
        'channel_profiles': {
            'telegram': 'compact / high-signal / retail-first bullets',
            'reddit': 'discussion thread / explicit claim-contradiction-invalidation + evidence'
        }
    }
    json.dump(manifest, open(MANIFEST_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
