#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(REPO, 'data', 'processed', 'narrative_intelligence_latest.json')
OUT = os.path.join(REPO, 'data', 'audit', 'quality_gate_v21.json')

MIN_SETUPS = 2
MIN_CONF = 0.42
MIN_INVALIDATIONS = 2


def fail(msg, findings):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'ok': False,
        'reason': msg,
        'findings': findings,
    }
    json.dump(payload, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps(payload))
    sys.exit(2)


def main():
    if not os.path.exists(INP):
        fail('missing processed intelligence file', [{'severity':'blocker','detail':INP}])

    d = json.load(open(INP, 'r', encoding='utf-8'))
    setups = d.get('setups', [])
    findings = []

    if len(setups) < MIN_SETUPS:
        findings.append({'severity':'blocker','detail':f'setups<{MIN_SETUPS}: {len(setups)}'})

    for i, s in enumerate(setups):
        title = s.get('title', f'idx:{i}')
        conf = s.get('confidence', 0)
        inv = s.get('invalidation_triggers', []) or []
        actors = s.get('actors', []) or []

        if conf < MIN_CONF:
            findings.append({'severity':'blocker','detail':f'low confidence {conf} on {title}'})
        if len(inv) < MIN_INVALIDATIONS:
            findings.append({'severity':'blocker','detail':f'not enough invalidations on {title}'})
        if not actors:
            findings.append({'severity':'blocker','detail':f'missing actors on {title}'})

        ps = (s.get('probability_base', 0) + s.get('probability_bull', 0) + s.get('probability_bear', 0))
        if ps != 100:
            findings.append({'severity':'blocker','detail':f'probabilities!=100 on {title}: {ps}'})

    ok = len(findings) == 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'ok': ok,
        'checked_setups': len(setups),
        'thresholds': {'min_setups': MIN_SETUPS, 'min_confidence': MIN_CONF, 'min_invalidations': MIN_INVALIDATIONS},
        'findings': findings,
    }
    json.dump(payload, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps(payload))
    if not ok:
        sys.exit(2)


if __name__ == '__main__':
    main()
