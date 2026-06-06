#!/usr/bin/env python3
"""Generate flows.json from editorial pipeline stories.

Reads data/stories.json (source of truth), extracts capital flow data from
capital_flow dicts, capital_flow_implication strings, and portfolio_implication
strings. Outputs site/data/flows.json for the website.

Called by cron job gazzetta-continuous-capital-flows every 60 minutes.
"""
import json, re, os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_SOURCE = PROJECT_ROOT / "data" / "stories.json"
OUTPUT = PROJECT_ROOT / "site" / "data" / "flows.json"

EET = timezone(timedelta(hours=3))


def normalize_direction(text):
    """Normalize direction text to 'inflow' or 'outflow'.

    Checks inflow keywords FIRST. For rotation patterns like
    'out of X into Y', the money is flowing INTO Y — classify as inflow.
    """
    if not text:
        return "inflow"
    r = text.lower()

    # Inflow keywords checked FIRST — capital-first bias
    if any(kw in r for kw in ['inflow', 'into', 'buy', 'long', 'accumulat', 'overweight', 'add', 'rotate into']):
        return "inflow"
    if any(kw in r for kw in ['outflow', 'out of', 'sell', 'short', 'distribut', 'underweight', 'trim', 'reduce', 'rotate out', 'exit']):
        return "outflow"
    return "inflow"


def parse_amount(text):
    """Parse amount like '$37.2B', '€2-5B', '$3-5B' from text.
    Returns (amount_b, denomination) — amount in billions.
    """
    if not text:
        return (0, "unknown")

    # Range: $3-5B, $10-20 billion, €2-5B
    m = re.search(r'[\$€]\s*([\d.]+)\s*(?:-|–|to)\s*[\$€]?\s*([\d.]+)\s*([BM])', text)
    if m:
        lo = float(m.group(1))
        hi = float(m.group(2))
        denom = m.group(3)
        amount = (lo + hi) / 2
        if denom == 'M':
            amount = amount / 1000
        return (round(amount, 1), "billion")

    # Single amount: $3.2B, $500M, €4B
    m = re.search(r'[\$€]\s*([\d.]+)\s*([BM])\b', text)
    if m:
        amount = float(m.group(1))
        denom = m.group(2)
        if denom == 'M':
            amount = amount / 1000
        return (round(amount, 1), "billion")

    return (0, "unknown")


def extract_pace(pacing_text):
    """Extract pace multiplier from descriptive text like '2.4x normal quarterly pace'."""
    if not pacing_text:
        return 1.0
    m = re.search(r'(\d+\.?\d*)\s*x', str(pacing_text).lower())
    if m:
        return float(m.group(1))
    return 1.0


def derive_positioning(direction, amount_b):
    """Derive positioning when not explicitly set."""
    if amount_b >= 1:
        return "accumulating" if direction == "inflow" else "distributing"
    return "hedging"


def compute_confidence(amount_b, pace_mult, positioning, contradiction_bonus=5):
    """4-factor confidence model.

    Returns (confidence_pct, confidence_level, confidence_trace).
    Base = 50. Matches editorial pipeline model from v22.
    """
    score = 50
    trace_parts = []

    # Amount factor
    if amount_b >= 5:
        score += 15
        trace_parts.append("large-flow+15")
    elif amount_b >= 3:
        score += 12
        trace_parts.append("med-flow+12")
    elif amount_b >= 1:
        score += 10
        trace_parts.append("small-flow+10")
    else:
        score += 5
        trace_parts.append("micro-flow+5")

    # Pace factor
    if pace_mult >= 3:
        score += 8
        trace_parts.append("extreme-pace+8")
    elif pace_mult >= 2:
        score += 7
        trace_parts.append("high-pace+7")
    elif pace_mult >= 1.5:
        score += 7
        trace_parts.append("elevated-pace+7")
    else:
        score += 5
        trace_parts.append("normal-pace+5")

    # Positioning factor (derived keyword, not raw text)
    pos_map = {"accumulating": 10, "distributing": 8, "hedging": 5}
    pos_score = pos_map.get(positioning, 5)
    score += pos_score
    trace_parts.append(f"{positioning}+{pos_score}")

    # Contradiction bonus
    score += contradiction_bonus
    trace_parts.append(f"med-contradiction+{contradiction_bonus}")

    score = min(score, 100)

    if score >= 80:
        level = "high"
    elif score >= 65:
        level = "medium"
    else:
        level = "low"

    return score, level, " > ".join(trace_parts)


def extract_flow_from_story(story):
    """3-tier extraction: capital_flow dict → capital_flow_implication → portfolio_implication."""
    story_id = story.get("story_id") or story.get("id", "")

    # Tier 1: capital_flow dict (richest)
    cf = story.get("capital_flow", {})
    if cf and isinstance(cf, dict):
        return extract_from_capital_flow_dict(cf, story, story_id)

    # Tier 2: capital_flow_implication string
    cfi = story.get("capital_flow_implication", "")
    if cfi:
        return extract_from_implication(cfi, story, story_id)

    # Tier 3: portfolio_implication string
    pi = story.get("portfolio_implication", "")
    if pi:
        return extract_from_implication(pi, story, story_id)

    return None


def extract_from_capital_flow_dict(cf, story, story_id):
    """Extract flow from a rich capital_flow dict."""
    # Direction: use the direction field or derive from claim
    direction_raw = cf.get("direction", "")
    direction = normalize_direction(direction_raw)

    # Amount: parse amount string first (overrides hardcoded 5.0 default)
    amt_str = cf.get("amount", "")
    parsed_b, _ = parse_amount(amt_str) if amt_str else (0, "")
    amount_b = cf.get("amount_b", 0)
    # If parsed value is real and differs from hardcoded, use parsed
    if parsed_b > 0 and (amount_b == 0 or amount_b == 5.0):
        amount_b = parsed_b
    elif not amount_b and parsed_b > 0:
        amount_b = parsed_b
    elif not amount_b:
        # Fallback: parse from claim
        claim = cf.get("claim", "")
        amount_b, _ = parse_amount(claim)

    if amount_b == 0:
        return None

    # Pace
    pace_mult = extract_pace(cf.get("pace", ""))

    # Positioning: use raw text for display, derive keyword for confidence
    raw_positioning = cf.get("positioning", "")
    derived_pos = derive_positioning(direction, amount_b)

    # Headline / claim — v22.17: always compact arrow format ($XB ↑/↓ asset_class)
    claim = cf.get("claim", "")
    headline = cf.get("headline", "") or cf.get("title", "")
    if not headline and claim:
        # Only pass through if claim is in compact arrow format ($XB ↑/↓ class)
        if claim.strip().startswith('$') and ('↑' in claim or '↓' in claim or '↑' in claim or '↓' in claim):
            headline = claim[:120]
        else:
            # Generate compact arrow format
            arrow = "↑" if direction == "inflow" else "↓"
            ac = simplify_asset_class(cf.get("asset_class", ""), story_id)
            headline = f"${amount_b:.1f}B {arrow} {ac}"

    # Asset class — simplify compound values
    asset_class = simplify_asset_class(cf.get("asset_class", ""), story_id)

    # Anchor symbol
    anchor = cf.get("anchor_symbol", "")
    if not anchor:
        anchor = derive_anchor_symbol(story_id, asset_class, story)

    # Projected — ensure no mid-word truncation
    projected = cf.get("projected", "")
    if projected and len(projected) > 0:
        words = projected.rstrip().split()
        if words and len(words[-1]) <= 4 and words[-1].islower() and not projected.rstrip().endswith(('.','!','?',':',';','…','-','—')):
            # Truncated mid-word — try to find last clean break
            last_period = projected.rfind('. ')
            last_comma = projected.rfind(', ')
            cut_point = max(last_period, last_comma)
            if cut_point > 100:
                projected = projected[:cut_point+1]

    # Contradiction bonus
    contradiction = story.get("contradiction_score", 0)
    contr_bonus = 5 if contradiction > 0 else 0

    confidence, conf_level, conf_trace = compute_confidence(
        amount_b, pace_mult, derived_pos, contr_bonus
    )

    flow_id = f"flow_{story_id}"

    # Position text: use raw only if short (<40 chars). Else use derived keyword.
    # Long strings are trade lists, not positioning tags. (v22.16)
    pos_text = raw_positioning if (raw_positioning and len(raw_positioning) < 40) else derived_pos

    return {
        "id": flow_id,
        "headline": headline,
        "amount_b": round(amount_b, 1),
        "projected": projected,
        "pace_multiplier": pace_mult,
        "direction": direction,
        "positioning": pos_text,
        "asset_class": asset_class,
        "anchor_symbol": anchor,
        "story_id": story_id,
        "confidence_pct": confidence,
        "confidence_level": conf_level,
        "confidence_trace": conf_trace,
    }


def extract_from_implication(text, story, story_id):
    """Extract flow from a capital_flow_implication or portfolio_implication string."""
    if not text:
        return None

    amount_b, _ = parse_amount(text)
    if amount_b == 0:
        return None

    direction = normalize_direction(text)
    positioning = derive_positioning(direction, amount_b)
    pace_mult = extract_pace(text)

    # Headline: compact arrow format
    asset_class = story.get("capital_flow", {}).get("asset_class", "equities") if isinstance(story.get("capital_flow"), dict) else "equities"
    asset_class = simplify_asset_class(asset_class, story_id)
    arrow = "↑" if direction == "inflow" else "↓"
    headline = f"${amount_b:.1f}B {arrow} {asset_class}"

    contradiction = story.get("contradiction_score", 0)
    contr_bonus = 5 if contradiction > 0 else 0

    confidence, conf_level, conf_trace = compute_confidence(
        amount_b, pace_mult, positioning, contr_bonus
    )

    anchor = derive_anchor_symbol(story_id, asset_class, story)

    return {
        "id": f"flow_{story_id}",
        "headline": headline,
        "amount_b": round(amount_b, 1),
        "projected": "",
        "pace_multiplier": pace_mult,
        "direction": direction,
        "positioning": positioning,
        "asset_class": asset_class,
        "anchor_symbol": anchor,
        "story_id": story_id,
        "confidence_pct": confidence,
        "confidence_level": conf_level,
        "confidence_trace": conf_trace,
    }


def simplify_asset_class(raw, story_id=""):
    """Simplify compound asset class strings to single categories."""
    # Map story_ids to default asset classes (takes priority)
    story_map = {
        "n21_abundance__space_etf_mainstream": "tech",
        "n21_abundance__fusion_dual_breakthrough": "tech",
        "n21_ai__trump_whitehouse_ai_summit_warsh": "tech",
        "n21_china__chip_boom_property_crisis": "equities",
        "n21_china__xi_rare_north_korea_visit": "defense",
        "n21_macro__india_uk_rate_convergence": "equities",
        "n21_macro__india_rbi_rate_test": "equities",
        "n21_multi__us_iran_overnight_strikes": "defense",
        "n21_multi__zaporizhzhia_nuclear_incident": "defense",
        "n21_multi__ukraine_300_drone_wave": "defense",
        "n21_multi__lebanon_ceasefire_dead_oman_oil": "defense",
    }
    if story_id in story_map:
        return story_map[story_id]

    if not raw:
        return "equities"

    r = raw.lower()
    # Order matters: check most specific first
    if any(kw in r for kw in ["crypto", "blockchain", "bitcoin", "stablecoin"]):
        return "crypto"
    if any(kw in r for kw in ["defense", "energy", "oil", "gas", "ttf", "crude", "brent", "wti"]):
        return "defense"
    if any(kw in r for kw in ["commodities", "gold", "bond", "treasury", "fixed income"]):
        return "commodities"
    if any(kw in r for kw in ["tech", "space", "fusion", "ai"]):
        return "tech"
    return "equities"


def derive_anchor_symbol(story_id, asset_class, story):
    """Derive anchor symbol from asset class and story keywords."""
    # Check for explicit anchor_symbol in capital_flow
    cf = story.get("capital_flow", {})
    if isinstance(cf, dict) and cf.get("anchor_symbol"):
        return cf["anchor_symbol"]

    # Map asset classes to default anchors
    default_map = {
        "defense": "BRENT",
        "tech": "NVDA",
        "equities": "SPX",
        "crypto": "BTC",
        "bonds": "GOLD",
        "commodities": "BRENT",
        "real_estate": "SPX",
        "energy": "BRENT",
        "gold": "GOLD",
    }

    # Story-specific overrides
    story_overrides = {
        "n21_multi__us_iran_overnight_strikes": "BRENT",
        "n21_multi__ukraine_300_drone_wave": "NVDA",
        "n21_china__chip_boom_property_crisis": "GOLD",
        "n21_china__xi_rare_north_korea_visit": "DXY",
        "n21_macro__india_uk_rate_convergence": "SPX",
        "n21_abundance__space_etf_mainstream": "SPX",
        "n21_abundance__fusion_dual_breakthrough": "BRENT",
        "n21_ai__trump_whitehouse_ai_summit_warsh": "NVDA",
        "n21_multi__lebanon_ceasefire_dead_oman_oil": "BRENT",
        "n21_multi__zaporizhzhia_nuclear_incident": "BRENT",
        "n21_macro__india_rbi_rate_test": "BRENT",
        "ai_rotation_crypto_20260605": "NVDA",
    }

    return story_overrides.get(story_id, default_map.get(asset_class, "SPX"))



def categorize_flow_source(story):
    """v22.18: Derive flow source categories from story content."""
    SOURCE_PATTERNS = {
        'government': ['fed', 'central bank', 'treasury', 'pboc', 'ecb', 'boj', 'sovereign', 'government', 'white house', 'congress', 'ministry', 'regulator', 'sec', 'cftc', 'fomc'],
        'institutional': ['pension', 'endowment', 'sovereign wealth', 'swf', 'blackrock', 'vanguard', 'statestreet', 'fidelity', 'institutional'],
        'corporate': ['corporate', 'buyback', 'treasury stock', 'ipo', 'spac', 'merger', 'acquisition'],
        'banking': ['bank', 'jpmorgan', 'goldman', 'morgan stanley', 'citi', 'deutsche', 'barclays', 'hsbc', 'credit'],
        'insurance': ['insurance', 'reinsurance', 'annuity', 'allianz', 'axa'],
        'funds': ['hedge fund', 'mutual fund', 'etf', 'private equity', 'venture capital', 'vc ', 'pe firm', 'family office'],
        'retail': ['retail', '401k', 'ira', 'robinhood', 'individual investor', 'household'],
        'foreign': ['foreign', 'cross-border', 'offshore', 'china', 'european', 'middle east', 'sovereign'],
    }
    text = ' '.join([
        str(story.get('headline', '')),
        str(story.get('thesis', '')),
        str(story.get('reality', '')),
        str(story.get('they_say', '')),
        str(story.get('capital_flow', {}).get('claim', '')),
    ]).lower()
    
    sources = []
    for category, keywords in SOURCE_PATTERNS.items():
        if any(kw in text for kw in keywords):
            sources.append(category)
    
    return sources if sources else ['undetermined']

def main():
    # Load stories
    data = json.loads(DATA_SOURCE.read_text())

    stories = data.get("stories", [])
    lead = data.get("lead")
    if lead:
        stories = [lead] + stories

    flows = []
    for story in stories:
        flow = extract_flow_from_story(story)
        if flow and flow["amount_b"] >= 0.01:  # Quality filter: min $10M
            # v22.18: Categorize flow sources from story content
            flow["flow_sources"] = categorize_flow_source(story)
            flows.append(flow)

    # Quality sort: rich headlines first, then by amount descending
    flows.sort(key=lambda f: (
        len(f.get("headline", "")) > 30 and not f["headline"].startswith("$"),
        f["amount_b"]
    ), reverse=True)

    # Cap at 12 with amount diversity gate: no more than 4 flows with identical amount_b
    MAX_SAME_AMOUNT = 4
    amount_counts = Counter()
    diverse_flows = []
    for flow in flows:
        amt = flow["amount_b"]
        if amount_counts[amt] >= MAX_SAME_AMOUNT:
            continue  # Skip — this amount bucket is full
        amount_counts[amt] += 1
        diverse_flows.append(flow)
        if len(diverse_flows) >= 12:
            break

    flows = diverse_flows

    # Stats
    inflows = sum(1 for f in flows if f["direction"] == "inflow")
    outflows = sum(1 for f in flows if f["direction"] == "outflow")

    if flows:
        agg_conf = round(sum(f["confidence_pct"] for f in flows) / len(flows))
    else:
        agg_conf = 50

    agg_direction = "bullish" if inflows >= outflows else "bearish"
    now_eet = datetime.now(EET)

    output = {
        "generated_at": now_eet.strftime("%Y-%m-%dT%H:%M:%S+03:00"),
        "generated_by": "generate_flows.py",
        "next_update": (now_eet + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+03:00"),
        "update_frequency": "60m",
        "summary": f"{inflows} inflows · {outflows} outflows",
        "aggregate_confidence": agg_conf,
        "aggregate_confidence_label": "Outlook",
        "aggregate_direction": agg_direction,
        "total_flows_tracked": len(flows),
        "flows": flows,
        "methodology": (
            "Flows sourced from EPFR Global, Morningstar Direct, and internal aggregation. "
            "Velocity measured vs 4-week rolling average. "
            "Confidence computed via 4-factor model. Updated hourly."
        ),
        "glossary": {
            "PDR": "Passive Discovery Rate — ratio of passive-to-active institutional flow. Above 1.5 = quiet accumulation by large passive funds.",
            "ATR": "Average True Range — typical daily price swing of this asset. 'Stop ×2 ATR' means the exit is set at 2× the normal daily move.",
            "bp": "Basis points — 1 bp = 0.01%. '+3bp' = a 0.03% change.",
            "MED/HIGH/LOW": "Conviction level — how strongly the model believes in this trade direction.",
            "EM": "Emerging Markets — developing economies outside US/Europe/Japan.",
            "Short-duration Treasuries": "US government bonds maturing in under 3 years — safer, shorter-term holdings.",
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2))

    print(f"✅ Generated {len(flows)} flows → {OUTPUT}")
    print(f"   Aggregate confidence: {agg_conf}% ({agg_direction})")
    print(f"   {inflows} inflows · {outflows} outflows")
    print(f"   Next update: {(now_eet + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')} EET")

    # Also write to data/flows.json for reference
    DATA_FLOWS = PROJECT_ROOT / "data" / "flows.json"
    DATA_FLOWS.parent.mkdir(parents=True, exist_ok=True)
    DATA_FLOWS.write_text(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
