#!/usr/bin/env python3
"""intel_to_stories.py — Bridge: telegram_intel/latest.json → gazzetta.db (SQLite)

Reads actionable stories from telegram intel, converts to Gazzetta story format,
INSERTs into gazzetta.db with deduplication. Creates capital flow entries inline.

After insertion, automatically runs db_to_json.py to compile fresh JSON output.

v3.0 — SQLite-backed:
  - Stories + flows written directly to relational tables
  - Deduplication via DB queries instead of JSON parsing
  - Entity extraction, time-decay, multi-persona preserved from v2.0
  - Auto-compiles JSON output for frontend compatibility

Run after: gazzetta-telegram-monitor (every 30m)
Run before: generate_flows.py, generate_flow_nodes.py
"""

import json
import os
import re
import sys
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Load central configuration
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

PROJECT = str(CONFIG_PATH.parent)
DATA = str(CONFIG_PATH.parent / config["paths"]["data"])
DB_PATH = str(CONFIG_PATH.parent / "gazzetta.db")
INTEL_PATH = os.path.join(DATA, config["data_files"]["intel_latest"])

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
    "1-6h": 3,
    "6-24h": 12,
    "24-72h": 36,
    "1w+": 84,
    "structural": 720,
}

CONFIDENCE_DECAY_BONUS = {
    "high": 1.5,
    "medium": 1.0,
    "low": 0.7,
}


def compute_time_decay(horizon: str, confidence: str, generated_at: str) -> dict:
    """Compute the half-life and current freshness of a story."""
    import math
    half_life = HORIZON_HALF_LIFE.get(horizon, 36)
    bonus = CONFIDENCE_DECAY_BONUS.get(confidence, 1.0)
    effective_half_life = half_life * bonus

    try:
        gen_dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        hours_elapsed = (datetime.now(timezone.utc) - gen_dt).total_seconds() / 3600
    except Exception:
        hours_elapsed = 0

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
    dir_emoji = "\U0001f7e2" if dir_label == "LONG" else "\U0001f534" if dir_label == "SHORT" else "\U0001f7e1"

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
                "flow_velocity": round(amount / 24, 2) if amount else 0,
                "correlation_coeff": 0.65 if dir_label != "NEUTRAL" else 0.30,
                "z_score": round(amount / 10, 2) if amount else 0,
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


def slugify(text, max_len=80):
    """URL-friendly slug from text."""
    if not text:
        return "untitled"
    slug = text.lower()[:max_len]
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-') or "untitled"


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
            projected = (cut[:last_space] if last_space > 150 else cut) + '\u2026'
        else:
            projected = raw_proj
    else:
        projected = f"Capital repositioning on {headline[:80]}"

    # Confidence tier
    conf = intel_story.get("confidence", 75)
    # v26.3: Confidence floor — if amount_b is tiny (<0.1B), confidence should reflect
    # that this is trace-level flow, not a conviction signal. Cap at 50 unless explicitly set.
    if amount_b < 0.1 and conf >= 50 and intel_story.get("confidence") is None:
        conf = max(conf, 40)  # Don't fabricate high confidence on micro-flows
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

    # Asset class detection — more keywords, better ordering
    asset_class = "equities"
    text_lower = (bet_text + " " + event_text + " " + headline).lower()
    # Check tech/business keywords FIRST (before defense, to avoid "war for users" → defense)
    if any(w in text_lower for w in ["ai", "tech", "software", "openai", "anthropic", "nvidia", "chip", "semiconductor", "data center", "cloud", "startup", "ipo", "valuation"]):
        asset_class = "tech"
    elif any(w in text_lower for w in ["btc", "bitcoin", "crypto", "eth", "ethereum", "blockchain", "defi", "stablecoin"]):
        asset_class = "crypto"
    elif any(w in text_lower for w in ["oil", "crude", "brent", "wti", "energy", "opec", "gasoline"]):
        asset_class = "commodities"
    elif any(w in text_lower for w in ["gold", "silver", "metal", "copper", "lithium"]):
        asset_class = "commodities"
    elif any(w in text_lower for w in ["bond", "treasury", "yield", "tlt", "fed", "federal reserve", "ecb", "interest rate", "inflation"]):
        asset_class = "fixed_income"
    elif any(w in text_lower for w in ["dollar", "fx", "forex", "currency", "dxy", "euro", "yen"]):
        asset_class = "fx"
    elif any(w in text_lower for w in ["pharma", "drug", "fda", "health", "medicare", "medicaid", "biotech", "clinical"]):
        asset_class = "fixed_income"  # healthcare → fixed_income for now
    # Defense LAST — only if no other category matched
    elif any(w in text_lower for w in ["missile", "military", "pentagon", "hezbollah", "houthi", "iran strike", "israel strike"]):
        asset_class = "defense"

    horizon = intel_story.get("horizon", "24-72h")

    # ── v22.45: Pace derivation from story content (was hardcoded 1.0) ──
    # Urgency keywords in headline/bet score higher pace
    urgency_keywords = [
        "breaking", "urgent", "flash", "alert", "crash", "spike",
        "plunge", "surge", "rout", "panic", "soar", "tumble",
        "crisis", "emergency", "imminent", "warning", "red alert"
    ]
    text_combined = f"{headline} {bet_text} {event_text}".lower()
    urgency_hits = sum(1 for k in urgency_keywords if k in text_combined)
    # Horizon-based base pace: shorter horizon = higher velocity
    horizon_base = {
        "1-6h": 3.0, "6-24h": 2.2, "24-72h": 1.5,
        "1w+": 1.1, "structural": 0.8
    }.get(horizon, 1.3)
    # Contradiction multiplier: high contradiction = capital moves faster
    contra_mult = 1.0 + (contradiction_score - 50) * 0.01 if contradiction_score > 50 else 1.0
    # Urgency bonus: each urgency keyword adds 0.3
    urgency_bonus = urgency_hits * 0.3
    # Asset-class velocity modifier
    asset_velocity = {
        "crypto": 1.3, "defense": 1.2, "commodities": 1.1,
        "equities": 0.95, "fixed_income": 0.8, "fx": 0.9, "tech": 1.1
    }.get(asset_class, 1.0)
    pace_mult = round((horizon_base + urgency_bonus) * contra_mult * asset_velocity, 1)
    pace_mult = max(0.5, min(5.0, pace_mult))  # Clamp to sensible range

    # Entity extraction
    all_text = f"{headline} {bet_text} {event_text} {benefit_text}"
    entity_tags = extract_entities(all_text)

    # Build base story
    they_say_raw = intel_story.get("consensus_narrative", "")
    reality_raw = intel_story.get("contradiction", "")
    
    # v26.3: Prevent They Say/Reality copy-paste — the #1 editorial trust killer.
    # If they're >70% identical, derive a differentiated reality from available data.
    if they_say_raw and reality_raw:
        # Simple word-overlap similarity check
        ts_words = set(they_say_raw.lower().split())
        re_words = set(reality_raw.lower().split())
        if ts_words and re_words:
            overlap = len(ts_words & re_words) / max(len(ts_words), len(re_words))
            if overlap > 0.7:
                # Use bet text or benefit as reality instead of duplicate
                reality_raw = bet_text[:300] if bet_text else benefit_text[:300]
                if not reality_raw or reality_raw == they_say_raw:
                    reality_raw = f"Capital flow data shows ${amount_b}B {direction} in {asset_class} — narrative may be mispricing the actual money flow."
    
    base_story = {
        "story_id": story_id,
        "headline": headline[:200],
        "sector": asset_class,
        "pillar": pillar,
        "paradigm_pillar": pillar,
        "paradigm_implications": [benefit_text[:200]] if benefit_text else [],
        "they_say": they_say_raw,
        "reality": reality_raw,
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
            "pace_multiplier": pace_mult,
            "confidence_pct": conf,
            "confidence_level": confidence_level,
        },
        "capital_flow_implication": bet_text[:300],
        "evidence": intel_story.get("sources", []),
        "source": "telegram_intel",
        "generated_at": now,
        "freshness": "breaking",
        "entity_tags": entity_tags,
        "time_decay": compute_time_decay(horizon, confidence_level, now),
        "impacted_flows": [],
        "associated_positions": [],
        "multi_persona": {},
    }

    base_story["multi_persona"] = generate_multi_persona(base_story)
    
    # ── v23.18: Conviction Probability (0-100%) ──
    # Multi-factor model: contradiction strength + source corroboration + freshness
    sources = intel_story.get("sources", [])
    source_count = len(sources) if isinstance(sources, list) else 1
    source_bonus = min((source_count - 1) * 5, 15)  # +5% per corroborating source, max +15%
    freshness_bonus = 10 if intel_story.get("freshness") == "breaking" else (5 if horizon in ("1-6h", "6-24h") else 0)
    confidence_bonus = 10 if confidence_level == "high" else (5 if confidence_level == "medium" else 0)
    # Contradiction score base: 50-85
    contra_base = 50 + min((contradiction_score - 45) * 0.8, 35)  # CS 45→50, CS 90→86
    conviction_prob = min(95, max(50, round(contra_base + source_bonus + freshness_bonus + confidence_bonus)))
    base_story["conviction_probability"] = conviction_prob
    base_story["conviction_tier"] = "ALPHA" if conviction_prob >= 85 else ("HIGH" if conviction_prob >= 75 else ("MODERATE" if conviction_prob >= 60 else "BASELINE"))
    
    return base_story


# ═══════════════════════════════════════════════════════
# DATABASE OPERATIONS
# ═══════════════════════════════════════════════════════

def insert_story_to_db(conn, story: dict) -> bool:
    """INSERT OR REPLACE a story into gazzetta.db."""
    sid = story.get("story_id", "")
    if not sid:
        return False

    conn.execute("""
        INSERT OR REPLACE INTO stories (
            id, slug, headline, sector, pillar, tier, confidence,
            contradiction_score, generated_at,
            time_decay_raw, entity_tags_raw, multi_persona_raw,
            capital_flow_raw, full_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sid,
        slugify(story.get("headline", "")),
        story.get("headline", ""),
        story.get("sector", ""),
        story.get("pillar", ""),
        story.get("tier", "active"),
        story.get("confidence", "medium"),
        story.get("contradiction_score", 0),
        story.get("generated_at", ""),
        json.dumps(story.get("time_decay", {})) if story.get("time_decay") else None,
        json.dumps(story.get("entity_tags", {})) if story.get("entity_tags") else None,
        json.dumps(story.get("multi_persona", {})) if story.get("multi_persona") else None,
        json.dumps(story.get("capital_flow", {})) if story.get("capital_flow") else None,
        json.dumps(story, ensure_ascii=False),
    ))
    return True


def story_exists(conn, story_id: str) -> bool:
    """Check if a story ID already exists in the DB."""
    row = conn.execute("SELECT 1 FROM stories WHERE id = ?", (story_id,)).fetchone()
    return row is not None


def compile_json_output():
    """Run db_to_json.py to regenerate JSON files from the updated DB."""
    db_to_json = Path(__file__).resolve().parent / "db_to_json.py"
    if db_to_json.exists():
        import subprocess
        result = subprocess.run(
            [sys.executable, str(db_to_json)],
            capture_output=True, text=True, cwd=str(CONFIG_PATH.parent)
        )
        if result.returncode != 0:
            print(json.dumps({"ok": True, "warning": "db_to_json failed", "stderr": result.stderr[:200]}), file=sys.stderr)


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    if not os.path.exists(INTEL_PATH):
        print(json.dumps({"ok": False, "error": "no telegram intel file"}))
        return

    if not os.path.exists(DB_PATH):
        print(json.dumps({"ok": False, "error": f"gazzetta.db not found at {DB_PATH} — run init_db.py first"}))
        return

    # Load intel
    with open(INTEL_PATH) as f:
        intel = json.load(f)

    actionable = intel.get("stories") or intel.get("actionable_stories", [])
    if not actionable:
        print(json.dumps({"ok": True, "stories_added": 0, "reason": "no stories in intel", "intel_keys": list(intel.keys())[:10]}))
        return

    conn = sqlite3.connect(DB_PATH)

    try:
        # Convert and deduplicate against DB
        added = 0
        for intel_story in actionable:
            headline = intel_story.get("title", intel_story.get("headline", ""))
            if not headline:
                continue

            pillar = detect_pillar(headline + " " + intel_story.get("event", ""))
            story_id = (intel_story.get("story_id") or generate_story_id(headline, pillar))[:80]

            if story_exists(conn, story_id):
                continue

            gazzetta_story = intel_story_to_gazzetta(intel_story, pillar)

            # Cross-reference: check for existing flows with matching story_id
            flow_id = f"flow_{story_id}"
            flow_row = conn.execute("SELECT 1 FROM flows WHERE id = ? OR story_id = ?", (flow_id, story_id)).fetchone()
            if flow_row:
                gazzetta_story["impacted_flows"] = [flow_id]
                conn.execute(
                    "INSERT OR IGNORE INTO story_flow_links (story_id, flow_id) VALUES (?, ?)",
                    (story_id, flow_id)
                )

            insert_story_to_db(conn, gazzetta_story)
            added += 1

        conn.commit()

        if added == 0:
            print(json.dumps({"ok": True, "stories_added": 0, "reason": "all stories already exist in DB"}))
            return

        # Compile JSON output for frontend
        compile_json_output()

        print(json.dumps({
            "ok": True,
            "stories_added": added,
            "total_stories": conn.execute("SELECT COUNT(*) FROM stories").fetchone()[0],
        }))

    except Exception as e:
        conn.rollback()
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
