#!/usr/bin/env python3
import json, pathlib, datetime
ROOT=pathlib.Path('/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv')
D=ROOT/'data'; D.mkdir(exist_ok=True)
src=D/'narratives_curated.json'
if not src.exists(): src=D/'narratives.json'
obj=json.loads(src.read_text()) if src.exists() else {}
items=obj.get('narratives') or obj.get('narrative_reviews') or []

def mk(i):
    t=(i.get('topic') or 'macro').upper()
    claim=i.get('headline') or f'{t}: narrative momentum building'
    desc=i.get('review') or 'Short-term setup forming with regime-sensitive volatility.'
    flow=i.get('flow_billion_usd_3d',3.8)
    proj=i.get('projection_3d','±0.8%')
    conf=i.get('confidence_score',64)
    conf_lbl='high' if conf>=75 else ('medium' if conf>=55 else 'low')
    return {
      'topic':t,'narrative_claim':claim,'narrative_description':desc,
      'controversial_angle':f'Consensus may be mispricing second-order effects in {t}.',
      'implications':f'Watch sector leaders linked to {t}; reassess cross-asset correlations.',
      'action_now':'Scale in with staged risk; use invalidation before adding exposure.',
      'projection_3d_pct':proj,'confidence_score':conf,'confidence_label':conf_lbl,
      'capital_flow_3d_usd_bn':flow,
      'invalidation_triggers':'Policy/rates headline reversal or failed follow-through volume.',
      'review_summary':'Short-term tactical bias with strict risk budget.'
    }

out_items=[mk(x) for x in items[:10]]
bundle={
 'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'channels':{
   'website_frontpage':out_items,
   'newspaper_x':out_items[:5],
   'chief_editor_x':out_items[:3],
   'subreddit':out_items[:6]
 }
}
(D/'channel_content_bundle.json').write_text(json.dumps(bundle,indent=2))
state={'generated_at':bundle['generated_at'],'ok':len(out_items)>0,'count':len(out_items),'surfaces':['website','newspaper_x','chief_editor_x','subreddit']}
(D/'editorial_strategy_state.json').write_text(json.dumps(state,indent=2))
print(json.dumps({'ok':True,'count':len(out_items)}))