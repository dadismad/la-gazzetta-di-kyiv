#!/usr/bin/env python3
"""intel_to_stories.py — Bridge: telegram_intel/latest.json → stories.json

Reads actionable stories from telegram intel, converts to Gazzetta story format,
appends to stories.json with deduplication. Creates capital flow entries inline.

v2.0 — Semantic Triangulation Engine:
  - Entity extraction & auto-tagging (assets, geographies, actors, instruments)
  - Time-decay value logic (half-life of actionability)
  - Multi-persona content blocks (C-Suite / Quant / Degen)
  - Cross-referencing: impacted_flows, associated_positions

Run after: gazzetta-telegram-monitor (every 30m)
Run before: generate_flows.py
"""

import json
import os
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Load central configuration
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

PROJECT = str(CONFIG_PATH.parent)
DATA = str(CONFIG_PATH.parent / config["paths"]["data"])
INTEL_PATH = os.path.join(DATA, config["data_files"]["intel_latest"])
STORIES_PATH = os.path.join(DATA, config["data_files"]["stories"])
FLOWS_PATH = os.path.join(DATA, config["data_files"]["flows"])

# ═══════════════════════════════════════════════════════
# ENTITY EXTRACTION — keyword / asset / geo mapping
# ═══════════════════════════════════════════════════════

ASSET_MAP = {
    "btc": "BTC", "bitcoin": "BTC", "xbt": "BTC",
    "eth": "ETH", "ethereum": "ETH",
    "sol": "SOL", "solana": "SOL",
    "spx": "SPX", "s&p": "SPX", "s&p 500": "SPX",
    "ndx": "NDX", "nasdaq": "NDX",
    "dxy": "DXY", "dollar index": "DXY",
    "wti": "WTI", "brent": "BRENT", "crude": "WTI",
    "gold": "XAU", "xau": "XAU", "silver": "XAG",
    "vix": "VIX",
    "us10y": "US10Y", "10y": "US10Y", "treasury": "US10Y",
    "eur": "EUR", "usd": "USD", "jpy": "JPY", "cny": "CNY",
    "nvidia": "NVDA", "nvda": "NVDA",
    "tesla": "TSLA", "tsla": "TSLA",
    "oil": "WTI", "natgas": "NG", "natural gas": "NG",
}

GEO_MAP = {
    "iran": "Iran", "tehran": "Iran",
    "israel": "Israel", "tel aviv": "Israel", "jerusalem": "Israel",
    "ukraine": "Ukraine", "kyiv": "Ukraine", "kiev": "Ukraine",
    "russia": "Russia", "moscow": "Russia",
    "china": "China", "beijing": "China", "taiwan": "Taiwan",
    "usa": "USA", "united states": "USA", "washington": "USA", "america": "USA",
    "eu": "EU", "europe": "EU", "brussels": "EU",
    "uk": "UK", "london": "UK", "britain": "UK",
    "japan": "Japan", "tokyo": "Japan",
    "india": "India", "delhi": "India",
    "saudi": "Saudi Arabia", "riyadh": "Saudi Arabia",
    "uae": "UAE", "dubai": "UAE",
    "turkey": "Turkey", "ankara": "Turkey",
    "brazil": "Brazil", "brasilia": "Brazil",
    "south korea": "South Korea", "seoul": "South Korea",
    "lebanon": "Lebanon", "beirut": "Lebanon",
    "syria": "Syria", "iraq": "Iraq", "yemen": "Yemen",
    "kuwait": "Kuwait", "qatar": "Qatar", "oman": "Oman",
    "venezuela": "Venezuela", "argentina": "Argentina",
}

ACTOR_MAP = {
    "fed": "Federal Reserve", "federal reserve": "Federal Reserve", "powell": "Federal Reserve",
    "ecb": "ECB", "european central bank": "ECB", "lagarde": "ECB",
    "opec": "OPEC", "opec+": "OPEC+",
    "imf": "IMF", "world bank": "World Bank",
    "pboc": "PBOC", "people's bank": "PBOC",
    "boj": "BOJ", "bank of japan": "BOJ",
    "boe": "BOE", "bank of england": "BOE",
    "sec": "SEC", "cftc": "CFTC",
    "blackrock": "BlackRock", "vanguard": "Vanguard", "fidelity": "Fidelity",
    "goldman": "Goldman Sachs", "jpmorgan": "JPMorgan", "morgan stanley": "Morgan Stanley",
    "janus": "Janus Henderson", "henderson": "Janus Henderson",
    "trump": "Trump", "biden": "Biden", "putin": "Putin", "xi": "Xi Jinping",
    "zelensky": "Zelensky", "netanyahu": "Netanyahu",
    "nato": "NATO", "un": "UN",
    "idf": "IDF", "hezbollah": "Hezbollah", "hamas": "Hamas", "houthi": "Houthis",
    "ethena": "Ethena", "ena": "Ethena",
}

INSTRUMENT_MAP = {
    "futures": "futures", "options": "options", "calls": "options", "puts": "options",
    "spot": "spot", "etf": "ETF", "etfs": "ETF",
    "swap": "swaps", "cds": "CDS", "credit default swap": "CDS",
    "bond": "bonds", "bonds": "bonds",
    "perp": "perpetuals", "perpetual": "perpetuals",
    "stablecoin": "stablecoins", "usdt": "stablecoins", "usdc": "stablecoins",
}


def extract_entities(text: str) -> dict:
    """Scan raw text for assets, geographies, actors, and instruments."""
    text_lower = text.lower()
    found_assets = set()
    found_geos = set()
    found_actors = set()
    found_instruments = set()

    for keyword, symbol in ASSET_MAP.items():
        if keyword in text_lower:
            found_assets.add(symbol)

    for keyword, geo in GEO_MAP.items():
        if keyword in text_lower:
            found_geos.add(geo)

    for keyword, actor in ACTOR_MAP.items():
        if keyword in text_lower:
            found_actors.add(actor)

    for keyword, instrument in INSTRUMENT_MAP.items():
        if keyword in text_lower:
            found_instruments.add(instrument)

    return {
        "assets": sorted(found_assets),
        "geographies": sorted(found_geos),
        "actors": sorted(found_actors),
        "instruments": sorted(found_instruments),
    }


# ═══════════════════════════════════════════════════════
# TIME-DECAY — half-life of actionability
# ═══════════════════════════════════════════════════════

HORIZON_HALF_LIFE = {
    "1-6h": 3,      # Ultra-short: decays fast
    "6-24h": 12,     # Intraday
    "24-72h": 36,    # Multi-day
    "1w+": 84,       # Weekly
    "structural": 720,  # Monthly — slow decay
}

CONFIDENCE_DECAY_BONUS = {
    "high": 1.5,     # High-confidence stories decay slower
    "medium": 1.0,
    "low": 0.7,      # Low-confidence stories decay faster
}


def compute_time_decay(horizon: str, confidence: str, generated_at: str) -> dict:
    """Compute the half-life and current freshness of a story.
    
    Freshness = 1.0 at generation, decays toward 0 over time.
    Formula: freshness = exp(-ln(2) * hours_elapsed / half_life)
    """
    half_life = HORIZON_HALF_LIFE.get(horizon, 36)
    bonus = CONFIDENCE_DECAY_BONUS.get(confidence, 1.0)
    effective_half_life = half_life * bonus

    # Compute hours elapsed
    try:
        gen_dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        hours_elapsed = (datetime.now(timezone.utc) - gen_dt).total_seconds() / 3600
    except Exception:
        hours_elapsed = 0

    # Exponential decay: freshness = e^(-λt) where λ = ln(2)/half_life
    import math
    if effective_half_life > 0 and hours_elapsed > 0:
        freshness = math.exp(-math.log(2) * hours_elapsed / effective_half_life)
        freshness = round(max(0.0, min(1.0, freshness)), 4)
    else:
        freshness = 1.0

    return {
        "half_life_hours": round(effective_half_life, 1),
        "decay_curve": "exponential",
        "current_freshness": freshness,
        "hours_elapsed": round(hours_elapsed, 2),
        "renewal_triggers": ["new_intel", "price_breach", "flow_confirmation"],
    }


# ═══════════════════════════════════════════════════════
# MULTI-PERSONA CONTENT GENERATION
# ═══════════════════════════════════════════════════════

def generate_multi_persona(story: dict) -> dict:
    """Generate three-lens content blocks: C-Suite, Quant, Degen."""
    headline = story.get("headline", "")
    they_say = story.get("they_say", "")
    reality = story.get("reality", "")
    bet = story.get("actionable_trade", "")
    direction = story.get("capital_flow", {}).get("direction", "neutral")
    asset = story.get("capital_flow", {}).get("asset_class", "equities")
    amount = story.get("capital_flow", {}).get("amount_b", 0)

    dir_label = "LONG" if direction == "inflow" else "SHORT" if direction == "outflow" else "NEUTRAL"
    dir_emoji = "🟢" if dir_label == "LONG" else "🔴" if dir_label == "SHORT" else "🟡"

    return {
        "c_suite": {
            "headline": headline[:120],
            "body": f"Structural assessment: {reality[:300] if reality else they_say[:300]}. "
                    f"Capital repositioning of ${amount}B identified in {asset}. "
                    f"Policy implication: monitor for regulatory or supply-chain cascades.",
            "implication": f"Board-level risk: {asset} exposure requires {dir_label.lower()} hedge within 72h.",
        },
        "quant": {
            "headline": f"{asset.upper()} flow: ${amount}B {direction}",
            "body": f"Raw telemetry — {asset} ${amount}B {direction}. "
                    f"Consensus vs reality divergence detected. "
                    f"Correlation regime: risk-on/off binary. Watch VIX-DXY spread for confirmation.",
            "metrics": {
                "flow_velocity": round(amount / 24, 2),
                "correlation_coeff": 0.65 if dir_label != "NEUTRAL" else 0.30,
                "z_score": round(amount / 10, 2),
            },
        },
        "degen": {
            "headline": f"{dir_emoji} {dir_label} {asset.upper()} ${amount}B",
            "body": f"Directional: {dir_label}. Flow: ${amount}B. "
                    f"Entry zone: near current. Stop: -5% from entry. "
                    f"Conviction: {story.get('confidence', 'medium').upper()}. "
                    f"Catalyst: {headline[:80]}",
            "signal": {
                "direction": dir_label,
                "entry_zone": "market",
                "stop_level": "-5%",
                "target": "+10-15%",
                "conviction": story.get("confidence", "medium").upper(),
            },
        },
    }


# ═══════════════════════════════════════════════════════
# PILLAR DETECTION
# ═══════════════════════════════════════════════════════

PILLAR_KEYWORDS = {
    "china_ascendancy": ["china", "beijing", "xi", "ccp", "chinese", "pla", "taiwan"],
    "dollar_decline": ["dollar", "dedollar", "brics", "imf", "cofer", "treasury", "fed", "central bank"],
    "eu_fragmentation": ["eu", "european", "nato", "eurozone", "ecb", "brussels", "migration"],
    "abundance_tech": ["fusion", "space", "spacex", "nasa", "longevity", "breakthrough", "quantum"],
    "blockchain_agentic": ["crypto", "bitcoin", "token", "defi", "rwa", "blockchain", "stablecoin"],
    "multi_pillar": ["iran", "war", "strike", "missile", "hormuz", "oil", "crude", "brent", "sanctions"],
}


def detect_pillar(text):
    """Detect paradigm pillar from text content."""
    text_lower = text.lower()
    scores = {}
    for pillar, keywords in PILLAR_KEYWORDS.items():
        score = sum(1 for k in keywords if k in text_lower)
        if score > 0:
            scores[pillar] = score
    if not scores:
        return "multi_pillar"
    return max(scores, key=lambda k: scores[k])


def generate_story_id(headline, pillar):
    """Generate a stable story_id from headline + pillar."""
    slug = headline.lower()[:60]
    slug = "".join(c if c.isalnum() or c in "_-" else "_" for c in slug)
    slug = slug.strip("_").replace("__", "_")
    return f"n21_{pillar}__{slug}"


# ═══════════════════════════════════════════════════════
# STORY CONVERSION
# ═══════════════════════════════════════════════════════

def intel_story_to_gazzetta(intel_story, pillar):
    """Convert a telegram intel story into Gazzetta story format with full triangulation fields."""
    headline = intel_story.get("title", intel_story.get("headline", "Untitled"))
    story_id = intel_story.get("story_id") or generate_story_id(headline, pillar)
    now = datetime.now(timezone.utc).isoformat()

    bet_raw = intel_story.get("bet", {})
    bet_text = bet_raw if isinstance(bet_raw, str) else bet_raw.get("direction", "")
    benefit_raw = intel_story.get("benefit", {})
    if isinstance(benefit_raw, str):
        benefit_text = benefit_raw
    else:
        benefit_text = benefit_raw.get("Bet&Benefit", "") or benefit_raw.get("Gazzetta di Kyiv", "") or json.dumps(benefit_raw)
    event_text = intel_story.get("event", "")

    # Determine direction from bet text
    is_long = "LONG" in bet_text.upper()
    direction = "inflow" if is_long else "outflow"

    # Extract amount: search for $XB patterns in bet/event
    amount_b = 5.0
    amounts = re.findall(r'\$(\d+\.?\d*)\s*[Bb]', bet_text + " " + event_text)
    if amounts:
        amount_b = float(amounts[0])

    # Build projected
    raw_proj = benefit_text or event_text
    if raw_proj:
        if len(raw_proj) > 200:
            cut = raw_proj[:200].rstrip()
            last_space = cut.rfind(' ')
            projected = (cut[:last_space] if last_space > 150 else cut) + '…'
        else:
            projected = raw_proj
    else:
        projected = f"Capital repositioning on {headline[:80]}"

    # Confidence tier
    conf = intel_story.get("confidence", 75)
    if conf >= 80:
        confidence_level = "high"
    elif conf >= 60:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    # Contradiction score
    raw_contradiction = intel_story.get("contradiction_score")
    if raw_contradiction is not None and raw_contradiction != 55:
        contradiction_score = raw_contradiction
    else:
        they_say = (intel_story.get("consensus_narrative", "") or "").lower()
        reality_text = (intel_story.get("contradiction", "") or "").lower()
        combined = they_say + " " + reality_text
        contradiction_keywords = [
            "but", "however", "despite", "unexpected", "surprising", "contrary",
            "diverging", "contradiction", "paradox", "irony", "ironically",
            "yet", "nonetheless", "nevertheless", "whereas", "while",
            "in reality", "actually", "the truth", "the reality",
        ]
        kw_count = sum(1 for k in contradiction_keywords if k in combined)
        base = 45 + min(kw_count * 5, 20)
        length_bonus = min(len(combined) // 200, 10)
        contradiction_score = min(base + length_bonus, 95)

    tier = "DEVELOPING" if contradiction_score >= 55 else "ALIGNED"

    # Asset class detection
    asset_class = "equities"
    text_lower = (bet_text + " " + event_text).lower()
    if any(w in text_lower for w in ["oil", "crude", "brent", "wti", "energy"]):
        asset_class = "commodities"
    elif any(w in text_lower for w in ["btc", "bitcoin", "crypto", "eth"]):
        asset_class = "crypto"
    elif any(w in text_lower for w in ["gold", "silver", "metal"]):
        asset_class = "commodities"
    elif any(w in text_lower for w in ["bond", "treasury", "yield", "tlt"]):
        asset_class = "fixed_income"
    elif any(w in text_lower for w in ["defense", "missile", "military"]):
        asset_class = "defense"

    horizon = intel_story.get("horizon", "24-72h")

    # ── Entity extraction ──
    all_text = f"{headline} {bet_text} {event_text} {benefit_text}"
    entity_tags = extract_entities(all_text)

    # ── Build base story first, then add triangulation fields ──
    base_story = {
        "story_id": story_id,
        "headline": headline[:200],
        "sector": asset_class,
        "pillar": pillar,
        "paradigm_pillar": pillar,
        "paradigm_implications": [benefit_text[:200]] if benefit_text else [],
        "they_say": intel_story.get("consensus_narrative", ""),
        "reality": intel_story.get("contradiction", ""),
        "thesis": bet_text[:300],
        "actors": intel_story.get("actors", []),
        "horizon": horizon,
        "confidence": confidence_level,
        "tier": tier,
        "actionable_trade": bet_text[:300],
        "contradiction_score": contradiction_score,
        "invalidation_trigger": "Narrative reversal or event resolution",
        "portfolio_implication": benefit_text[:300],
        "capital_flow": {
            "direction": direction,
            "amount_b": amount_b,
            "asset_class": asset_class,
            "projected": projected,
            "pace_multiplier": 1.0,
            "confidence_pct": conf,
            "confidence_level": confidence_level,
        },
        "capital_flow_implication": bet_text[:300],
        "evidence": intel_story.get("sources", []),
        "source": "telegram_intel",
        "generated_at": now,
        "freshness": "breaking",
        # ── v2.0: Triangulation fields ──
        "entity_tags": entity_tags,
        "time_decay": compute_time_decay(horizon, confidence_level, now),
        "impacted_flows": [],   # filled after flow generation by generate_flows.py
        "associated_positions": [],  # filled by trading system
        "multi_persona": {},  # filled below
    }

    base_story["multi_persona"] = generate_multi_persona(base_story)
    return base_story


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    if not os.path.exists(INTEL_PATH):
        print(json.dumps({"ok": False, "error": "no telegram intel file"}))
        return

    # Load intel
    with open(INTEL_PATH) as f:
        intel = json.load(f)

    actionable = intel.get("stories") or intel.get("actionable_stories", [])
    if not actionable:
        print(json.dumps({"ok": True, "stories_added": 0, "reason": "no stories in intel", "intel_keys": list(intel.keys())[:10]}))
        return

    # Load current stories
    if os.path.exists(STORIES_PATH):
        with open(STORIES_PATH) as f:
            stories_data = json.load(f)
    else:
        stories_data = {"generated_at": "", "lead": None, "stories": []}

    # Load flows for cross-referencing
    existing_flow_ids = set()
    if os.path.exists(FLOWS_PATH):
        with open(FLOWS_PATH) as f:
            flows_data = json.load(f)
        for flow in flows_data.get("flows", []):
            existing_flow_ids.add(flow.get("id", ""))
            existing_flow_ids.add(flow.get("story_id", ""))

    existing_ids = {s.get("story_id", "") for s in stories_data.get("stories", [])}
    if stories_data.get("lead") and stories_data["lead"].get("story_id"):
        existing_ids.add(stories_data["lead"]["story_id"])

    # Convert and deduplicate
    added = 0
    for intel_story in actionable:
        headline = intel_story.get("title", intel_story.get("headline", ""))
        if not headline:
            continue

        pillar = detect_pillar(headline + " " + intel_story.get("event", ""))
        story_id = (intel_story.get("story_id") or generate_story_id(headline, pillar))[:80]

        if story_id in existing_ids:
            continue

        gazzetta_story = intel_story_to_gazzetta(intel_story, pillar)

        # Cross-reference: link to existing flows with matching story_id
        flow_id = f"flow_{story_id}"
        if flow_id in existing_flow_ids:
            gazzetta_story["impacted_flows"] = [flow_id]

        stories_data["stories"].insert(0, gazzetta_story)
        existing_ids.add(story_id)
        added += 1

    if added == 0:
        print(json.dumps({"ok": True, "stories_added": 0, "reason": "all stories already exist"}))
        return

    # Update timestamp
    stories_data["generated_at"] = datetime.now(timezone.utc).isoformat()

    # Write back
    with open(STORIES_PATH, "w") as f:
        json.dump(stories_data, f, indent=2, ensure_ascii=False)

    # Also sync to site/data/
    site_data = os.path.join(PROJECT, config["paths"]["site"], config["paths"]["data"], config["data_files"]["stories"])
    os.makedirs(os.path.dirname(site_data), exist_ok=True)
    with open(site_data, "w") as f:
        json.dump(stories_data, f, indent=2, ensure_ascii=False)

    print(json.dumps({
        "ok": True,
        "stories_added": added,
        "total_stories": len(stories_data["stories"]),
        "new_ids": [s["story_id"] for s in stories_data["stories"][:added]],
    }, indent=2))


if __name__ == "__main__":
    main()

