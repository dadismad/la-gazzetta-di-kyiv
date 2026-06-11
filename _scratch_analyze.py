#!/usr/bin/env python3
"""Quick analysis of stories.json for editorial writer"""
import json

with open('/Users/alexstocchi/projects/gazzetta-di-kyiv/data/stories.json') as f:
    data = json.load(f)

stories = data.get('stories', [])
print(f"Total stories: {len(stories)}")

# Show the lead story
lead = data.get('lead', {})
print(f"\n=== LEAD STORY ===")
print(f"ID: {lead.get('story_id')}")
print(f"Headline: {lead.get('headline', '')[:120]}")
print(f"Tier: {lead.get('tier')} | Confidence: {lead.get('confidence')} | Sector: {lead.get('sector')}")
print(f"They Say: {lead.get('they_say', '')[:150]}")
print(f"Reality: {lead.get('reality', '')[:150]}")
print(f"Horizon: {lead.get('horizon')}")

# Sort by conviction tier
tiers = {}
for s in stories:
    tier = s.get('tier', 'UNKNOWN')
    if tier not in tiers:
        tiers[tier] = []
    tiers[tier].append(s)

for tier in ['ALPHA', 'HIGH CONVICTION', 'SIGNAL', 'DEVELOPING', 'BACKGROUND']:
    tier_s = tiers.get(tier, [])
    print(f"\n=== {tier} ({len(tier_s)} stories) ===")
    for s in tier_s[:4]:
        flow = s.get('capital_flow', {})
        print(f"  {s.get('story_id', '?')}")
        print(f"    headline: {s.get('headline', '')[:130]}")
        print(f"    sector: {s.get('sector')} | pillar: {s.get('paradigm_pillar')} | flow: {flow.get('direction', '')} {flow.get('asset_class', '')}")
        thesis = s.get('thesis', '')
        print(f"    thesis: {thesis[:130]}")
        print()

# Also show unique sectors
sectors = set()
for s in stories:
    sectors.add(s.get('sector', '?'))
print(f"\nUnique sectors: {sorted(sectors)}")

# Show unique paradigm_pillars
pillars = set()
for s in stories:
    pillars.add(s.get('paradigm_pillar', '?'))
print(f"Unique pillars: {sorted(pillars)}")
