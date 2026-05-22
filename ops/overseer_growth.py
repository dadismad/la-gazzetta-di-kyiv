#!/usr/bin/env python3
import json, datetime, pathlib
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; out=D/'overseer_growth.json'
checks={'contacts_page':(ROOT/'site/contacts.html').exists(),'cooperation_page':(ROOT/'site/cooperation.html').exists(),'privacy_page':(ROOT/'site/privacy.html').exists()}
score=round(100*sum(checks.values())/len(checks),1)
state='running' if score>=80 else 'degraded'
obj={'group':'growth','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'state':state,'score':score,'checks':checks,'blockers':[] if state=='running' else ['growth pages incomplete'],'root_cause_hypothesis':'missing trust/conversion pages','fix_plan':'restore static growth pages and links','eta':'next run < 24h'}
out.write_text(json.dumps(obj,indent=2)); print(json.dumps({'ok':True,'file':str(out),'score':score}))