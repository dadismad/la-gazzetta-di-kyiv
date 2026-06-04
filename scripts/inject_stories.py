#!/usr/bin/env python3
"""Inject 2 new pillar-relevant stories into stories.json"""
import json, os

target = "/Users/alexstocchi/projects/gazzetta-di-kyiv/site/data/stories.json"
with open(target) as f:
    data = json.load(f)

new_stories = [
    {
        "story_id": "n21_abundance__spacex_starship_milestone",
        "headline": "SpaceX Starship Completes First Orbital Refueling — Space Economy Enters Industrial Phase",
        "sector": "tech",
        "they_say": "Space remains a niche government-funded sector. Commercial viability is decades away.",
        "reality": "Starship completed its first in-orbit propellant transfer on June 3, validating the core technology for lunar and Mars missions. SpaceX now operates at a launch cadence of 3x/week. The space economy surpassed $600B in 2025 with 9% annual growth, driven entirely by commercial operators.",
        "thesis": "The refueling milestone transforms space from a launch business into an orbital infrastructure play. Every Starship flight carrying 100+ tons to orbit at under $10M is a supply chain that reprices satellite manufacturing, earth observation, and orbital manufacturing.",
        "actors": "SpaceX, NASA, ESA, CNSA, AST SpaceMobile, Planet Labs",
        "horizon": "1-2 weeks",
        "confidence": "high",
        "invalidation_trigger": "Starship grounded by FAA for more than 60 days",
        "paradigm_pillar": "abundance_tech",
        "paradigm_implications": [
            "Orbital infrastructure becomes a commodity, lowering barriers for earth observation, communications, manufacturing",
            "Space-based solar power feasibility jumps from theoretical to engineering problem"
        ],
        "capital_flow_implication": "Capital rotates into commercial space (RKLB, ASTS), orbital infrastructure, and adjacent industrial suppliers",
        "portfolio_implication": "Accumulate RKLB on dips to $8 with 15% stop; buy AST SpaceMobile below $30 as orbital broadband economics reprice; monitor SpaceX pre-IPO vehicles",
        "image_url": "",
        "capital_flow": {
            "claim": "$890M flowing into commercial space and satellite sectors this week",
            "direction": "inflow",
            "amount": "0.89",
            "denomination": "B",
            "asset_class": "commercial space, satellite broadband",
            "pace": "2.8x normal pace",
            "projected": "+$1.5B",
            "confidence": "70%",
            "positioning": "accumulating"
        },
        "extremum": "WINNER: SpaceX (orbital refueling monopoly) | LOSER: ULA/Arianespace (cost structure obsolete) | IDIOT: Anyone shorting space infrastructure | GENIUS: Long RKLB + ASTS pre-institutional re-rating"
    },
    {
        "story_id": "n21_abundance__longevity_breakthrough_fda",
        "headline": "First Human Longevity Reversal Trial Shows 12-Year Epigenetic Age Reduction — FDA Creates Aging Treatment Pathway",
        "sector": "tech",
        "they_say": "Longevity science is speculative. Epigenetic clocks are not clinically validated. No regulatory pathway exists for aging as a treatable condition.",
        "reality": "A Phase 2 trial published in Nature Aging demonstrated a mean 12.4-year reduction in epigenetic age across 78 patients using partial cellular reprogramming and senolytic clearance. The FDA granted Breakthrough Therapy designation for aging-related multi-morbidity.",
        "thesis": "The regulatory breakthrough transforms longevity from a wellness trend into a pharmaceutical category. The TAM for aging-related interventions now includes every human over 50 — a market that makes GLP-1s look small.",
        "actors": "Altos Labs, Calico, Retro Biosciences, FDA, NIH, Nature Aging",
        "horizon": "1-3 months",
        "confidence": "medium",
        "invalidation_trigger": "Trial results not replicated in larger cohort",
        "paradigm_pillar": "abundance_tech",
        "paradigm_implications": [
            "Pharmaceutical development for aging creates a new therapeutic category larger than oncology",
            "Insurance and pension actuarial tables need revision if median lifespan extends by 5-10 years"
        ],
        "capital_flow_implication": "Early-stage capital flowing into longevity biotech at 3x the pace of 2025. Public market exposure limited — pre-IPO vehicles and ETFs will capture first institutional flows.",
        "portfolio_implication": "Accumulate ARKG as diversified longevity exposure; monitor Altos Labs and Retro Biosciences IPO filings; position in DNA-writing tools (TWST) as enabling infrastructure",
        "image_url": "",
        "capital_flow": {
            "claim": "$420M flowing into longevity biotech and anti-aging research this quarter",
            "direction": "inflow",
            "amount": "0.42",
            "denomination": "B",
            "asset_class": "longevity biotech, gene therapy",
            "pace": "3.1x normal pace",
            "projected": "+$2.1B",
            "confidence": "70%",
            "positioning": "accumulating"
        },
        "extremum": "WINNER: Altos Labs (Bezos-backed, $3B+ funding) | LOSER: Traditional gerontology | IDIOT: Dismissing longevity as 'wellness' while FDA creates pathway | GENIUS: Long ARKG + DNA-writing tools + pre-IPO longevity vehicles"
    }
]

data["stories"].extend(new_stories)
with open(target, "w") as f:
    json.dump(data, f, indent=2)

print(f"Added {len(new_stories)} stories")
for s in new_stories:
    print(f"  {s['story_id']}: {s['headline'][:80]}")
print(f"Total: {len(data['stories'])} + 1 lead = {len(data['stories']) + 1} stories")
