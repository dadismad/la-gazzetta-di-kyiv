#!/usr/bin/env python3
from __future__ import annotations
import json, os, time
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_DIR = os.path.join(REPO, 'data', 'audit')
JSON_OUT = os.path.join(AUDIT_DIR, 'pipeline_audit_latest.json')
MD_OUT = os.path.join(AUDIT_DIR, 'pipeline_audit_latest.md')

CHECKS = [
    ('normalized_events', 'data/normalized/events_latest.json'),
    ('processed_intelligence', 'data/processed/narrative_intelligence_latest.json'),
    ('site_regime', 'site/api/v1/home/regime.json'),
    ('site_setups', 'site/api/v1/home/setups.json'),
    ('site_contradictions', 'site/api/v1/home/contradictions.json'),
    ('telegram_payload', 'data/publish/telegram_latest.md'),
    ('reddit_payload', 'data/publish/reddit_latest.md'),
]


def age_seconds(path: str):
    if not os.path.exists(path):
        return None
    return int(time.time() - os.path.getmtime(path))


def main():
    os.makedirs(AUDIT_DIR, exist_ok=True)
    findings = []
    artifacts = []

    for key, rel in CHECKS:
        p = os.path.join(REPO, rel)
        ok = os.path.exists(p)
        age = age_seconds(p)
        artifacts.append({'key': key, 'path': rel, 'exists': ok, 'age_seconds': age})
        if not ok:
            findings.append({'severity': 'blocker', 'title': f'Missing artifact: {key}', 'evidence': rel, 'fix': f'Generate {rel} via v2 pipeline scripts'})
        elif age is not None and age > 86400:
            findings.append({'severity': 'high', 'title': f'Stale artifact: {key}', 'evidence': f'{rel} age={age}s', 'fix': 'Run pipeline and refresh'})

    # source ingestion checks
    norm_path = os.path.join(REPO, 'data/normalized/events_latest.json')
    if os.path.exists(norm_path):
        norm = json.load(open(norm_path, 'r', encoding='utf-8'))
        failures = norm.get('failures', [])
        if failures:
            findings.append({
                'severity': 'medium',
                'title': 'Source retrieval failures detected',
                'evidence': f"failures={len(failures)} in data/normalized/events_latest.json",
                'fix': 'Add alternate mirror/feed and retry policy for failed sources'
            })
        if norm.get('stale'):
            findings.append({
                'severity': 'blocker',
                'title': 'Normalized events marked stale',
                'evidence': 'events_latest.json stale=true',
                'fix': 'Recover collection stage before publish'
            })

    # schema/semantic checks
    setups_path = os.path.join(REPO, 'site/api/v1/home/setups.json')
    if os.path.exists(setups_path):
        setups = json.load(open(setups_path, 'r', encoding='utf-8')).get('items', [])
        for i, s in enumerate(setups[:20]):
            ps = s.get('probability_base', 0) + s.get('probability_bull', 0) + s.get('probability_bear', 0)
            if ps != 100:
                findings.append({'severity': 'high', 'title': 'Probability sum != 100', 'evidence': f'setups[{i}] {s.get("title")}', 'fix': 'Normalize probabilities in analyze stage'})
            if not s.get('invalidation_triggers'):
                findings.append({'severity': 'high', 'title': 'Missing invalidation trigger', 'evidence': f'setups[{i}] {s.get("title")}', 'fix': 'Enforce invalidation in analyzer'})

    regime_path = os.path.join(REPO, 'site/api/v1/home/regime.json')
    if os.path.exists(regime_path):
        regime = json.load(open(regime_path, 'r', encoding='utf-8'))
        if not regime.get('regime_label'):
            findings.append({'severity': 'medium', 'title': 'Missing regime label', 'evidence': 'regime.json', 'fix': 'Set fallback regime label'})

    status = 'ok' if not [f for f in findings if f['severity'] in ('blocker', 'high')] else 'degraded'
    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'artifact_checks': artifacts,
        'findings': findings,
        'summary': {
            'total_findings': len(findings),
            'blockers': len([f for f in findings if f['severity'] == 'blocker']),
            'high': len([f for f in findings if f['severity'] == 'high']),
            'medium': len([f for f in findings if f['severity'] == 'medium']),
            'low': len([f for f in findings if f['severity'] == 'low']),
        }
    }
    json.dump(report, open(JSON_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    lines = [
        '# Pipeline Audit (Latest)',
        '',
        f"Status: **{status}**",
        f"Generated: {report['generated_at']}",
        '',
        '## Artifact checks',
    ]
    for a in artifacts:
        lines.append(f"- {a['key']}: exists={a['exists']} age_seconds={a['age_seconds']} path=`{a['path']}`")
    lines.append('')
    lines.append('## Findings')
    if findings:
        for f in findings:
            lines.append(f"- [{f['severity'].upper()}] {f['title']} | evidence: {f['evidence']} | fix: {f['fix']}")
    else:
        lines.append('- No critical findings.')

    open(MD_OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print(json.dumps({'ok': True, 'status': status, 'json': JSON_OUT, 'md': MD_OUT, 'findings': len(findings)}))


if __name__ == '__main__':
    main()
