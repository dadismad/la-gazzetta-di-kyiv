#!/usr/bin/env python3
"""
Pipeline audit v2.2 — source diversity + paradigm coverage + anti-template checks.
"""
from __future__ import annotations
import json, os, time
from collections import Counter
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_DIR = os.path.join(REPO, 'data', 'audit')
JSON_OUT = os.path.join(AUDIT_DIR, 'pipeline_audit_latest.json')
MD_OUT = os.path.join(AUDIT_DIR, 'pipeline_audit_latest.md')
SRC_CFG = os.path.join(REPO, 'data', 'config', 'data_sources_v2.json')

CHECKS = [
    ('normalized_events', 'data/normalized/events_latest.json'),
    ('processed_intelligence', 'data/processed/narrative_intelligence_latest.json'),
    ('stories_json', 'data/publish/stories.json'),
    ('telegram_payload', 'data/publish/telegram_latest.md'),
    ('reddit_payload', 'data/publish/reddit_latest.md'),
    ('editorial_state', 'data/editorial_state.json'),
]

EXPECTED_PILLARS = [
    'china_ascendancy', 'dollar_decline', 'eu_fragmentation',
    'abundance_tech', 'blockchain_agentic',
]


def age_seconds(path: str):
    if not os.path.exists(path):
        return None
    return int(time.time() - os.path.getmtime(path))


def main():
    os.makedirs(AUDIT_DIR, exist_ok=True)
    findings = []
    artifacts = []
    paradigm_counts = Counter({p: 0 for p in EXPECTED_PILLARS})

    # ── Artifact freshness ──
    for key, rel in CHECKS:
        p = os.path.join(REPO, rel)
        ok = os.path.exists(p)
        age = age_seconds(p)
        artifacts.append({'key': key, 'path': rel, 'exists': ok, 'age_seconds': age})
        if not ok:
            findings.append({'severity': 'blocker', 'title': f'Missing: {key}', 'evidence': rel, 'fix': f'Generate {rel}'})
        elif age is not None and age > 86400:
            findings.append({'severity': 'high', 'title': f'Stale: {key}', 'evidence': f'{rel} age={age}s', 'fix': 'Run pipeline'})

    # ── Source diversity ──
    total_sources = 0
    if os.path.exists(SRC_CFG):
        src_cfg = json.load(open(SRC_CFG, 'r', encoding='utf-8'))
        for cat_data in src_cfg.get('sources', {}).values():
            total_sources += len(cat_data.get('sources', []))

    norm_path = os.path.join(REPO, 'data/normalized/events_latest.json')
    norm_sources = set()
    if os.path.exists(norm_path):
        norm = json.load(open(norm_path, 'r', encoding='utf-8'))
        for ev in norm.get('items', []):
            sid = ev.get('source_id', '')
            if sid:
                norm_sources.add(sid)

    coverage_pct = round(len(norm_sources) / max(total_sources, 1) * 100, 1)
    artifacts.append({
        'key': 'source_diversity', 'path': 'data/normalized/events_latest.json',
        'active_sources': len(norm_sources), 'total_configured': total_sources,
        'coverage_pct': coverage_pct,
    })
    if len(norm_sources) < 3 and total_sources > 0:
        findings.append({'severity': 'medium', 'title': 'Low source diversity',
                         'evidence': f'{len(norm_sources)}/{total_sources} active', 'fix': 'Check RSS/API reachability'})

    # ── Paradigm coverage ──
    intel_path = os.path.join(REPO, 'data/processed/narrative_intelligence_latest.json')
    if os.path.exists(intel_path):
        intel = json.load(open(intel_path, 'r', encoding='utf-8'))
        for s in intel.get('setups', []):
            pillar = s.get('paradigm_pillar', 'unknown')
            paradigm_counts[pillar] += 1

    uncovered = [p for p in EXPECTED_PILLARS if paradigm_counts.get(p, 0) == 0]
    paradigm_report = [{'pillar': p, 'setup_count': paradigm_counts.get(p, 0), 'covered': paradigm_counts.get(p, 0) > 0} for p in EXPECTED_PILLARS]
    artifacts.append({
        'key': 'paradigm_coverage', 'pillars': paradigm_report,
        'coverage_pct': round(len([p for p in EXPECTED_PILLARS if paradigm_counts.get(p, 0) > 0]) / len(EXPECTED_PILLARS) * 100, 1),
    })
    if uncovered:
        findings.append({'severity': 'medium', 'title': 'Paradigm pillars uncovered',
                         'evidence': f'No setups: {", ".join(uncovered)}', 'fix': 'Expand source ingestion'})

    # ── Anti-template check ──
    stories_path = os.path.join(REPO, 'data/publish/stories.json')
    if os.path.exists(stories_path):
        stories_data = json.load(open(stories_path, 'r', encoding='utf-8'))
        banned = ['narrative acceleration', 'second-order effects remain underpriced',
                  'transmission effects remain underpriced', 'repricing whipsaws',
                  'mention-share drops below 7d baseline', 'cross-source confirmation',
                  'policy and market actors']
        all_s = [stories_data.get('lead', {})] + stories_data.get('stories', [])
        violations = []
        for i, s in enumerate(all_s):
            for phrase in banned:
                if phrase in json.dumps(s).lower():
                    violations.append({'story_index': i, 'banned_phrase': phrase, 'headline': s.get('headline', '')[:60]})
        if violations:
            findings.append({'severity': 'high', 'title': f'Taxonomy phrases: {len(violations)} stories',
                             'evidence': json.dumps(violations[:3]), 'fix': 'Rewrite without template language'})

    # ── Status ──
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
        },
    }
    json.dump(report, open(JSON_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # ── Markdown report ──
    lines = ['# Pipeline Audit', '', f"Status: **{status}**", f"Generated: {report['generated_at']}", '', '## Artifacts']
    for a in artifacts:
        if a.get('pillars'):
            lines.append(f"- **paradigm_coverage**: {a.get('coverage_pct', '?')}%")
            for pr in a['pillars']:
                lines.append(f"  - {pr['pillar']}: {pr['setup_count']} {'✅' if pr['covered'] else '❌'}")
        elif a.get('active_sources') is not None:
            lines.append(f"- **source_diversity**: {a['active_sources']}/{a['total_configured']} active ({a['coverage_pct']}%)")
        else:
            age_str = f"{a.get('age_seconds', '?')}s" if a.get('age_seconds') is not None else 'N/A'
            lines.append(f"- {a['key']}: {'✅' if a.get('exists') else '❌'} age={age_str}")

    lines.append(''); lines.append('## Findings')
    if findings:
        for f in findings:
            lines.append(f"- [{f['severity'].upper()}] {f['title']} | {f.get('evidence','')}")
    else:
        lines.append('- No findings.')
    lines.append(''); lines.append('## Source Coverage')
    lines.append(f"- {len(norm_sources)} of {total_sources} configured sources active")
    lines.append(''); lines.append('## Paradigm Lens')
    for pid in EXPECTED_PILLARS:
        lines.append(f"- **{pid}**: {paradigm_counts.get(pid, 0)} setups")

    open(MD_OUT, 'w', encoding='utf-8').write('\n'.join(lines))
    print(json.dumps({'ok': True, 'status': status, 'json': JSON_OUT, 'md': MD_OUT, 'findings': len(findings)}))


if __name__ == '__main__':
    main()
