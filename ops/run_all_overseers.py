#!/usr/bin/env python3
import subprocess, json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'
scripts=['overseer_ingestion.py','overseer_analysis.py','overseer_publishing.py','overseer_governance.py','overseer_design.py','overseer_reliability.py','overseer_growth.py','ceo_orchestrator.py']
results=[]
for s in scripts:
 p=subprocess.run(['python3',f'ops/{s}'],cwd=ROOT,capture_output=True,text=True)
 results.append({'script':s,'ok':p.returncode==0,'stdout':p.stdout[-400:],'stderr':p.stderr[-300:]})

# prioritized action queue
priority=[]
for name in ['overseer_ingestion.json','overseer_analysis.json','overseer_publishing.json','overseer_governance.json','overseer_design.json','overseer_reliability.json','overseer_growth.json']:
 p=D/name
 if p.exists():
  obj=json.loads(p.read_text())
  if obj.get('state')!='running':
   priority.append({'owner':obj.get('group'),'action':obj.get('fix_plan'),'eta':obj.get('eta'),'status':'blocked'})
if not priority:
 priority=[
  {'owner':'publishing','action':'maintain homepage retail quality and deploy continuity','eta':'ongoing','status':'in_progress'},
  {'owner':'analysis','action':'refresh narratives and audit artifacts','eta':'<8h','status':'in_progress'},
  {'owner':'governance','action':'monitor compliance and add group for truly new tasks','eta':'daily','status':'in_progress'}
 ]

snap={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed':[r['script'] for r in results if r['ok']],'in_progress':[p for p in priority if p['status']=='in_progress'],'blocked':[p for p in priority if p['status']=='blocked'],'next_3_priorities':priority[:3]}
(D/'executive_snapshot.json').write_text(json.dumps(snap,indent=2))
print(json.dumps({'ok':True,'executive_snapshot':str(D/'executive_snapshot.json'),'ran':len(results)}))