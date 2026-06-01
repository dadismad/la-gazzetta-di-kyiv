#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(REPO, 'data', 'processed', 'narrative_intelligence_latest.json')
OUT = os.path.join(REPO, 'data', 'audit', 'quality_gate_v22.json')

MIN_SETUPS = 3
MIN_CONF = 0.45
MIN_INVALIDATIONS = 2
MIN_ACTORS = 1
MIN_SOURCE_COUNT = 4
MIN_EVIDENCE_TITLES = 2
STRICT_TOP_N = 6


def write_and_exit(ok: bool, findings, checked_setups=0, reason=None, code=0):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'ok': ok,
        'reason': reason,
        'checked_setups': checked_setups,
        'thresholds': {
            'min_setups': MIN_SETUPS,
            'min_confidence': MIN_CONF,
            'min_invalidations': MIN_INVALIDATIONS,
            'min_actors': MIN_ACTORS,
            'min_source_count': MIN_SOURCE_COUNT,
            'min_evidence_titles': MIN_EVIDENCE_TITLES,
        },
        'findings': findings,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(json.dumps(payload))
    sys.exit(code)


def main():
    if not os.path.exists(INP):
        write_and_exit(False, [{'severity': 'blocker', 'detail': f'missing file: {INP}'}], reason='missing processed intelligence', code=2)

    d = json.load(open(INP, 'r', encoding='utf-8'))
    setups = d.get('setups', [])
    regime = d.get('regime', {})
    findings = []

    if len(setups) < MIN_SETUPS:
        findings.append({'severity': 'blocker', 'detail': f'setups<{MIN_SETUPS}: {len(setups)}'})

    src_count = int(regime.get('source_count', 0) or 0)
    if src_count < MIN_SOURCE_COUNT:
        findings.append({'severity': 'blocker', 'detail': f'source_count<{MIN_SOURCE_COUNT}: {src_count}'})

    for i, s in enumerate(setups):
        title = s.get('title', f'idx:{i}')
        conf = float(s.get('confidence', 0) or 0)
        inv = s.get('invalidation_triggers', []) or []
        actors = s.get('actors', []) or []
        evidence = s.get('evidence_titles', []) or []
        p = int(s.get('probability_base', 0) or 0) + int(s.get('probability_bull', 0) or 0) + int(s.get('probability_bear', 0) or 0)

        strict = i < STRICT_TOP_N
        if strict and conf < MIN_CONF:
            findings.append({'severity': 'blocker', 'detail': f'low confidence {conf} on {title}'})
        if len(inv) < MIN_INVALIDATIONS:
            findings.append({'severity': 'blocker', 'detail': f'not enough invalidations on {title}'})
        if len(actors) < MIN_ACTORS:
            findings.append({'severity': 'blocker', 'detail': f'not enough actors on {title}'})
        if strict and len(evidence) < MIN_EVIDENCE_TITLES:
            findings.append({'severity': 'high', 'detail': f'low evidence titles on {title}: {len(evidence)}'})
        if p != 100:
            findings.append({'severity': 'blocker', 'detail': f'probabilities!=100 on {title}: {p}'})

    blockers = [f for f in findings if f['severity'] == 'blocker']
    if blockers:
        write_and_exit(False, findings, checked_setups=len(setups), reason='quality gate failed', code=2)

    write_and_exit(True, findings, checked_setups=len(setups), reason='quality gate passed', code=0)


if __name__ == '__main__':
    main()
