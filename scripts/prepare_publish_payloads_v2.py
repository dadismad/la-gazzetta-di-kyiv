#!/usr/bin/env python3
from __future__ import annotations
import json, os
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(REPO, 'data', 'processed', 'narrative_intelligence_latest.json')
SITE_HOME = os.path.join(REPO, 'site', 'api', 'v1', 'home')
TELEGRAM_OUT = os.path.join(REPO, 'data', 'publish', 'telegram_latest.md')
REDDIT_OUT = os.path.join(REPO, 'data', 'publish', 'reddit_latest.md')


def ensure(p: str):
    os.makedirs(p, exist_ok=True)


def main():
    d = json.load(open(INP, 'r', encoding='utf-8'))
    setups = d.get('setups', [])
    contradictions = d.get('contradictions', [])
    regime = d.get('regime', {})

    ensure(SITE_HOME)
    ensure(os.path.dirname(TELEGRAM_OUT))

    # Site payloads
    json.dump({'generated_at': d.get('generated_at'), 'items': setups}, open(os.path.join(SITE_HOME, 'setups.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump({'generated_at': d.get('generated_at'), 'items': contradictions}, open(os.path.join(SITE_HOME, 'contradictions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(regime, open(os.path.join(SITE_HOME, 'regime.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    lead = setups[0] if setups else {}
    t_lines = [
        f"Risk Regime: {regime.get('regime_label','Insufficient Data')} ({regime.get('risk_state','mixed')})",
        f"• {lead.get('title','No setup')} | base {lead.get('probability_base','-')}%",
        f"• Claim: {lead.get('thesis','No thesis')}",
        f"• Invalidation: {(lead.get('invalidation_triggers') or ['n/a'])[0]}",
        f"Updated: {datetime.now(timezone.utc).isoformat()}"
    ]
    open(TELEGRAM_OUT, 'w', encoding='utf-8').write('\n'.join(t_lines))

    r_lines = [
        "## La Gazzetta di Kyiv — Narrative Intelligence Brief",
        "",
        f"**Regime:** {regime.get('regime_label','Insufficient Data')} ({regime.get('risk_state','mixed')})",
        f"**Claim:** {lead.get('thesis','No thesis')}.",
        f"**Actors:** {', '.join((lead.get('actors') or ['policy/market actors'])[:3])}",
        f"**24–72h path:** base {lead.get('probability_base','-')}% / bull {lead.get('probability_bull','-')}% / bear {lead.get('probability_bear','-')}%.",
        f"**Invalidation:** {(lead.get('invalidation_triggers') or ['n/a'])[0]}",
        "",
        "Evidence:",
        "- https://pureciclismo.github.io/gazzetta-di-kyiv/",
        "- https://pureciclismo.github.io/gazzetta-di-kyiv/api/v1/home/setups.json",
        "",
        "READY_FOR_DEVVIT_POST"
    ]
    open(REDDIT_OUT, 'w', encoding='utf-8').write('\n'.join(r_lines))
    print(json.dumps({'ok': True, 'telegram': TELEGRAM_OUT, 'reddit': REDDIT_OUT, 'setups': len(setups)}))


if __name__ == '__main__':
    main()
