#!/usr/bin/env python3
import json, datetime, pathlib, subprocess
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; D.mkdir(exist_ok=True)

def sh(cmd):
    p=subprocess.run(cmd,shell=True,capture_output=True,text=True,cwd=ROOT)
    return p.stdout.strip(), p.returncode

# static model (cron list is external; this is authoritative intended map)
planes={
 'data_plane':[
  {'name':'social-umbrella-collector','cadence':'15m','owner':'DataOps','purpose':'ingestion'},
  {'name':'phase2-publish','cadence':'8h','owner':'PublishingOps','purpose':'site refresh/deploy prep'},
  {'name':'sources-daily-update','cadence':'daily 06:00','owner':'DataOps','purpose':'source quality/ranking'},
  {'name':'pipeline-audit','cadence':'daily 06:30','owner':'Governance','purpose':'audit + integrity'}
 ],
 'control_plane':[
  {'name':'ceo-upgrade-control-loop','cadence':'2h','owner':'CEO','purpose':'external availability + canary + blockers'},
  {'name':'brandbook-representation-ops','cadence':'daily 09:00','owner':'Brand/Data','purpose':'brand/content gates'},
  {'name':'morning-evening-newsroom-cycle','cadence':'06:30 & 18:30','owner':'Editorial','purpose':'newspaper cadence + newsletter bundles'}
 ]
}

kpi={
 'availability_target':'>=99%',
 'non_empty_claims':'required',
 'narrative_actionability':'required fields present',
 'publish_cadence':'morning+evening fulfilled'
}

out={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'planes':planes,'kpi':kpi,'next_prune_review':'weekly'}
(D/'grand_operating_map.json').write_text(json.dumps(out,indent=2))

md=['# Grand Operating Map','',f"Generated: {out['generated_at']}",'','## Data Plane']
for j in planes['data_plane']:
    md.append(f"- {j['name']} | {j['cadence']} | {j['owner']} | {j['purpose']}")
md.append('')
md.append('## Control Plane')
for j in planes['control_plane']:
    md.append(f"- {j['name']} | {j['cadence']} | {j['owner']} | {j['purpose']}")
md.append('')
md.append('## KPI Contracts')
for k,v in kpi.items():
    md.append(f"- {k}: {v}")
(ROOT/'docs'/'GRAND_OPERATING_MAP.md').write_text('\n'.join(md))
print(json.dumps({'ok':True,'json':str(D/'grand_operating_map.json'),'md':str(ROOT/'docs'/'GRAND_OPERATING_MAP.md')}))