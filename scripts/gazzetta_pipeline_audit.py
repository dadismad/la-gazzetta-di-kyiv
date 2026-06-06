#!/usr/bin/env python3
"""Pipeline audit — checks that all Gazzetta data artifacts are current and valid."""
import json, datetime, pathlib

ROOT = pathlib.Path('/Users/alexstocchi/projects/gazzetta-di-kyiv')
DATA = ROOT / 'data'
OUT = DATA / 'pipeline_audit.json'

now = datetime.datetime.now(datetime.timezone.utc).isoformat()

artifacts = {
    'stories.json': DATA / 'stories.json',
    'flows.json': DATA / 'flows.json',
    'narratives.json': DATA / 'narratives.json',
    'living_stories.json': DATA / 'living_stories.json',
    'source_registry_ranked.json': DATA / 'source_registry_ranked.json',
    'representation_techniques.json': DATA / 'representation_techniques.json',
}

results = []
for name, path in artifacts.items():
    status = {'name': name, 'exists': path.exists()}
    if path.exists():
        try:
            data = json.loads(path.read_text())
            status['valid_json'] = True
            status['size_bytes'] = path.stat().st_size
            if 'generated_at' in data:
                status['generated_at'] = data['generated_at']
                age = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00'))
                status['age_hours'] = round(age.total_seconds() / 3600, 1)
        except Exception as e:
            status['valid_json'] = False
            status['error'] = str(e)
    else:
        status['valid_json'] = False
    results.append(status)

audit = {
    'generated_at': now,
    'artifacts': results,
    'summary': {
        'total': len(results),
        'present': sum(1 for r in results if r['exists']),
        'valid_json': sum(1 for r in results if r.get('valid_json')),
        'stale_24h': sum(1 for r in results if r.get('age_hours', 0) > 24),
    }
}

OUT.write_text(json.dumps(audit, indent=2))
print(json.dumps({'ok': True, 'audit_file': str(OUT), 'summary': audit['summary']}, indent=2))
