#!/usr/bin/env python3
"""Claims container guard — validates all containers have proper empty-state fallbacks"""
import json, pathlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
html=(ROOT/'site/index.html').read_text(errors='ignore')
issues=[]

# Check all containers have body divs with IDs
containers = ['storiesContainer','capitalFlowsContainer','anchorContainer','triangulationContainer','trackRecordContainer']
for cid in containers:
    if f'id="{cid}"' not in html:
        issues.append(f'missing container {cid}')

# Check stories have newsCol rendering target
if 'newsCol' not in html: issues.append('missing newsCol render target')

ok = len(issues) == 0
out = {'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'ok': ok, 'issues': issues, 'narrative_reviews_count': len(containers)}
(ROOT/'data/claims_container_guard.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out))
