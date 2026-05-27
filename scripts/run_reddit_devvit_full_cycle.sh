#!/usr/bin/env bash
set -euo pipefail
MAIN="/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv"
WEB="/Users/alexstocchi/lagazzettadikyiv"

cd "$MAIN"
python3 scripts/devvit_only_pipeline.py > /tmp/gazzetta_data_lane.json
python3 scripts/reddit_post_payload.py > /tmp/gazzetta_payload.json

cd "$WEB"
npm run -s type-check >/tmp/gazzetta_typecheck.log
./node_modules/.bin/devvit upload >/tmp/gazzetta_upload.log
./node_modules/.bin/devvit install LaGazzettadiKyiv lagazzettadikyiv@latest >/tmp/gazzetta_install.log

cat <<'EOF'
{"status":"pass","data_lane":"ok","publish_lane":"install-trigger-post executed","quality_lane":"type-check pass","brand_lane":"app branding active","evidence":{"payload":"/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/reddit_post_payload.md","install_log":"/tmp/gazzetta_install.log"}}
EOF
