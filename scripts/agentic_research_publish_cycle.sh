#!/usr/bin/env bash
set -euo pipefail
cd /Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv
# Run expanded multi-source pipeline first (collection -> analysis -> payloads -> audit)
./scripts/run_pipeline_v2.sh

# Keep backward compatibility with existing NLP/post scripts
cp data/publish/reddit_latest.md data/reddit_post_payload.md

# Legacy fallback pipeline remains as secondary path
python3 scripts/devvit_only_pipeline.py
for i in 1 2 3; do
  python3 scripts/reddit_post_nlp_audit.py
  PASS=$(python3 - <<'PY'
import json
j=json.load(open('data/reddit_post_nlp_audit.json'))
print('1' if j.get('pass') else '0')
PY
)
  if [ "$PASS" = "1" ]; then break; fi
  python3 scripts/reddit_payload_autofix.py
done
python3 scripts/reddit_post_nlp_audit.py
PASS=$(python3 - <<'PY'
import json
j=json.load(open('data/reddit_post_nlp_audit.json'))
print('1' if j.get('pass') else '0')
PY
)
if [ "$PASS" != "1" ]; then
  echo '{"status":"fail","reason":"nlp_audit_failed"}'
  exit 2
fi
/Users/alexstocchi/lagazzettadikyiv/tools/autopost_publish_install.sh
RPT=$(python3 scripts/ceo_reddit_report.py)
echo "$RPT"
PERM=$(python3 - <<'PY'
import json,sys
j=json.loads(sys.stdin.read())
p=j.get('permalink','')
print(p)
PY
<<< "$RPT")
if [[ -z "$PERM" || "$PERM" == *"not available"* ]]; then
  echo '{"status":"fail","reason":"missing_permalink_evidence"}'
  exit 3
fi
echo '{"status":"pass","nlp_audit":"pass","publish":"executed","evidence":"permalink_present"}'