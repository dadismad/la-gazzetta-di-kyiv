#!/usr/bin/env python3
"""fetch_intel.py — OSINT collector: RSS feeds → drafts table in gazzetta.db

Fetches open financial/macro RSS feeds, extracts core text, identifies entities
matching our asset/geo/actor maps, and writes items into the drafts table.

Each draft gets:
  - source: feed name (e.g. 'ecb_press', 'reuters_business')
  - raw_content: full item description
  - suggested_headline: item title
  - suggested_multi_persona: JSON with C-Suite/Quant/Degen blocks
  - suggested_flows: JSON with capital flow direction + asset class guess
  - status: 'pending_review'

Usage:
  python3 scripts/fetch_intel.py              # fetch all feeds, write to drafts
  python3 scripts/fetch_intel.py --dry-run    # fetch but don't write
  python3 scripts/fetch_intel.py --feed ecb   # only fetch ECB feed
"""

import json
import os
import re
import sys
import ssl
import sqlite3
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser not installed. Run: .venv/bin/pip install feedparser")
    sys.exit(1)

PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"

# ═══════════════════════════════════════════════════════
# RSS FEED CONFIGURATION
# ═══════════════════════════════════════════════════════

RSS_FEEDS = [
    {
        "name": "ecb_press",
        "label": "ECB Press Releases",
        "url": "https://www.ecb.europa.eu/rss/press.html",
        "category": "central_bank",
        "priority": "high",
    },
    {
        "name": "reuters_business",
        "label": "Reuters Business (Google News)",
        "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
        "category": "financial_news",
        "priority": "high",
    },
]

# ═══════════════════════════════════════════════════════
# ENTITY EXTRACTION — mirrors intel_to_stories.py maps
# ═══════════════════════════════════════════════════════

ASSET_MAP = {
    "btc": "BTC", "bitcoin": "BTC", "xbt": "BTC",
    "eth": "ETH", "ethereum": "ETH", "ether": "ETH",
    "sol": "SOL", "solana": "SOL",
    "spx": "SPX", "s&p": "SPX", "s&p 500": "SPX", "s&p500": "SPX",
    "ndx": "NDX", "nasdaq": "NDX",
    "dxy": "DXY", "dollar index": "DXY",
    "wti": "WTI", "brent": "BRENT", "crude": "WTI",
    "gold": "XAU", "xau": "XAU", "silver": "XAG",
    "vix": "VIX",
    "us10y": "US10Y", "10y": "US10Y", "treasury": "US10Y", "bond yield": "US10Y",
    "eur": "EUR", "usd": "USD", "jpy": "JPY", "cny": "CNY", "gbp": "GBP",
    "nvidia": "NVDA", "nvda": "NVDA",
    "tesla": "TSLA", "tsla": "TSLA",
    "oil": "WTI", "natgas": "NG", "natural gas": "NG",
    "openai": "OpenAI", "anthropic": "Anthropic",
}

GEO_MAP = {
    "iran": "Iran", "tehran": "Iran",
    "israel": "Israel", "tel aviv": "Israel", "jerusalem": "Israel",
    "ukraine": "Ukraine", "kyiv": "Ukraine", "kiev": "Ukraine",
    "russia": "Russia", "moscow": "Russia",
    "china": "China", "beijing": "China", "taiwan": "Taiwan",
    "usa": "USA", "united states": "USA", "washington": "USA", "america": "USA",
    "eu": "EU", "europe": "EU", "brussels": "EU", "european union": "EU",
    "uk": "UK", "london": "UK", "britain": "UK", "england": "UK",
    "japan": "Japan", "tokyo": "Japan",
    "india": "India", "delhi": "India",
    "saudi": "Saudi Arabia", "riyadh": "Saudi Arabia",
    "uae": "UAE", "dubai": "UAE",
    "turkey": "Turkey", "ankara": "Turkey",
    "brazil": "Brazil", "brasilia": "Brazil",
    "south korea": "South Korea", "seoul": "South Korea", "korea": "South Korea",
    "lebanon": "Lebanon", "beirut": "Lebanon",
    "syria": "Syria", "iraq": "Iraq", "yemen": "Yemen",
    "kuwait": "Kuwait", "qatar": "Qatar", "oman": "Oman",
    "venezuela": "Venezuela", "argentina": "Argentina",
    "germany": "Germany", "berlin": "Germany",
    "france": "France", "paris": "France",
    "italy": "Italy", "rome": "Italy",
    "canada": "Canada", "ottawa": "Canada",
    "australia": "Australia", "sydney": "Australia",
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
    "openai": "OpenAI", "anthropic": "Anthropic",
    "congress": "US Congress", "white house": "White House",
    "bis": "BIS", "bank for international settlements": "BIS",
}

PILLAR_KEYWORDS = {
    "china_ascendancy": ["china", "beijing", "xi", "ccp", "chinese", "pla", "taiwan"],
    "dollar_decline": ["dollar", "dedollar", "brics", "imf", "cofer", "treasury", "fed", "central bank"],
    "eu_fragmentation": ["eu", "european", "nato", "eurozone", "ecb", "brussels", "migration"],
    "abundance_tech": ["fusion", "space", "spacex", "nasa", "longevity", "breakthrough", "quantum"],
    "blockchain_agentic": ["crypto", "bitcoin", "token", "defi", "rwa", "blockchain", "stablecoin"],
    "multi_pillar": ["iran", "war", "strike", "missile", "hormuz", "oil", "crude", "brent", "sanctions"],
}


# ═══════════════════════════════════════════════════════
# EXTRACTION HELPERS
# ═══════════════════════════════════════════════════════

def strip_html(text):
    """Remove HTML tags from text."""
    if not text:
        return ""
    return re.sub(r'<[^>]+>', ' ', text).strip()


def extract_entities(text):
    """Scan text for assets, geographies, actors."""
    text_lower = text.lower()
    found_assets = set()
    found_geos = set()
    found_actors = set()

    for keyword, symbol in ASSET_MAP.items():
        if keyword in text_lower:
            found_assets.add(symbol)
    for keyword, geo in GEO_MAP.items():
        if keyword in text_lower:
            found_geos.add(geo)
    for keyword, actor in ACTOR_MAP.items():
        if keyword in text_lower:
            found_actors.add(actor)

    return {
        "assets": sorted(found_assets),
        "geographies": sorted(found_geos),
        "actors": sorted(found_actors),
    }


def detect_asset_class(text):
    """Guess asset class from text content."""
    t = text.lower()
    if any(w in t for w in ["crypto", "bitcoin", "btc", "eth", "token", "defi", "blockchain", "stablecoin"]):
        return "crypto"
    if any(w in t for w in ["oil", "crude", "brent", "wti", "energy", "gas", "opec"]):
        return "commodities"
    if any(w in t for w in ["gold", "silver", "metal", "copper", "iron"]):
        return "commodities"
    if any(w in t for w in ["bond", "treasury", "yield", "tlt", "sovereign debt"]):
        return "fixed_income"
    if any(w in t for w in ["defense", "missile", "military", "nato", "war"]):
        return "defense"
    if any(w in t for w in ["dollar", "eur", "yen", "forex", "currency", "exchange rate", "fx"]):
        return "fx"
    if any(w in t for w in ["tech", "ai", "artificial intelligence", "chip", "semiconductor", "software"]):
        return "tech"
    return "equities"


def detect_direction(text):
    """Guess capital flow direction from tone/words."""
    t = text.lower()
    bullish = ["surge", "rally", "jump", "soar", "climb", "gain", "rise", "boost",
               "expansion", "growth", "bullish", "optimism", "upgrade", "buy",
               "cut rates", "easing", "stimulus", "inflow"]
    bearish = ["plunge", "crash", "tumble", "drop", "fall", "decline", "sink",
               "recession", "contraction", "bearish", "downgrade", "sell",
               "hike rates", "tightening", "crisis", "outflow", "fears"]

    bull_score = sum(1 for w in bullish if w in t)
    bear_score = sum(1 for w in bearish if w in t)

    if bull_score > bear_score:
        return "inflow"
    elif bear_score > bull_score:
        return "outflow"
    return "neutral"


def detect_pillar(text):
    """Detect paradigm pillar from text."""
    text_lower = text.lower()
    scores = {}
    for pillar, keywords in PILLAR_KEYWORDS.items():
        score = sum(1 for k in keywords if k in text_lower)
        if score > 0:
            scores[pillar] = score
    return max(scores, key=scores.get) if scores else "multi_pillar"


def extract_amount(text):
    """Extract dollar amount in billions from text."""
    if not text:
        return 5.0
    m = re.search(r'\$(\d+\.?\d*)\s*[Bb]', text)
    if m:
        return float(m.group(1))
    m = re.search(r'(\d+\.?\d*)\s*(billion|trillion)', text, re.IGNORECASE)
    if m:
        amt = float(m.group(1))
        if m.group(2).lower() == "trillion":
            amt *= 1000
        return amt
    return 5.0


def generate_multi_persona(headline, raw_text, entities, asset_class, direction):
    """Generate three-lens suggested content blocks."""
    dir_label = "LONG" if direction == "inflow" else "SHORT" if direction == "outflow" else "WATCH"
    dir_emoji = "\U0001f7e2" if dir_label == "LONG" else "\U0001f534" if dir_label == "SHORT" else "\U0001f7e1"
    assets_str = ", ".join(entities.get("assets", [])[:3]) or asset_class
    geos_str = ", ".join(entities.get("geographies", [])[:3]) or "global"

    return {
        "c_suite": {
            "headline": headline[:120],
            "body": f"Structural assessment: {raw_text[:250]}... "
                    f"Implicated assets: {assets_str}. Regions: {geos_str}. "
                    f"Monitor for policy or supply-chain cascades.",
            "implication": f"Board-level: {asset_class} exposure review recommended. "
                          f"Directional bias: {dir_label}.",
        },
        "quant": {
            "headline": f"{asset_class.upper()} signal: {dir_label}",
            "body": f"Raw telemetry — {asset_class} flow detected from {raw_text[:150]}... "
                    f"Assets tagged: {assets_str}. "
                    f"Correlation regime: TBD. Watch vol surface for confirmation.",
            "metrics": {
                "flow_direction": direction,
                "asset_class": asset_class,
                "geographies": entities.get("geographies", []),
            },
        },
        "degen": {
            "headline": f"{dir_emoji} {dir_label} {assets_str}",
            "body": f"Directional: {dir_label}. Asset: {assets_str}. "
                    f"Context: {headline[:80]}. "
                    f"Conviction: LOW (unvetted draft). Entry zone: TBD. Stop: TBD.",
            "signal": {
                "direction": dir_label,
                "entry_zone": "awaiting review",
                "stop_level": "TBD",
                "target": "TBD",
                "conviction": "LOW",
            },
        },
    }


def generate_suggested_flows(headline, raw_text, asset_class, direction):
    """Generate suggested capital flow entry."""
    amount_b = extract_amount(raw_text)
    return {
        "direction": direction,
        "amount_b": amount_b,
        "asset_class": asset_class,
        "projected": raw_text[:200] if raw_text else "",
        "pace_multiplier": 1.0,
        "confidence_pct": 50,
        "confidence_level": "low",
        "claim": f"${amount_b}B {direction} {asset_class}",
        "confidence": "50%",
    }


# ═══════════════════════════════════════════════════════
# DATABASE OPERATIONS
# ═══════════════════════════════════════════════════════

def draft_exists(conn, headline, source):
    """Check if a draft with this headline+source already exists."""
    row = conn.execute(
        "SELECT 1 FROM drafts WHERE suggested_headline = ? AND source = ?",
        (headline, source)
    ).fetchone()
    return row is not None


def insert_draft(conn, source, raw_content, headline, multi_persona, flows, created_at):
    """Insert a new draft into the drafts table."""
    conn.execute("""
        INSERT INTO drafts (source, raw_content, suggested_headline,
                           suggested_multi_persona, suggested_flows,
                           created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending_review')
    """, (
        source,
        raw_content,
        headline,
        json.dumps(multi_persona, ensure_ascii=False) if multi_persona else None,
        json.dumps(flows, ensure_ascii=False) if flows else None,
        created_at,
    ))


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def fetch_feed(feed_cfg):
    """Fetch one RSS feed, return list of parsed entries."""
    url = feed_cfg["url"]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; GazzettaBot/1.0; +https://lagazzettadikyiv.com)"
    })

    try:
        resp = urllib.request.urlopen(req, timeout=20, context=ctx)
        raw = resp.read()
        parsed = feedparser.parse(raw)
        if parsed.bozo and not parsed.entries:
            print(f"  {feed_cfg['name']}: parse error — {parsed.bozo_exception}")
            return []
        return parsed.entries
    except Exception as e:
        print(f"  {feed_cfg['name']}: fetch error — {e}")
        return []


def process_entries(conn, feed_cfg, entries, dry_run):
    """Process feed entries: extract, deduplicate, insert into drafts."""
    added = 0
    skipped = 0

    for entry in entries:
        headline = (entry.get("title") or "").strip()
        if not headline or len(headline) < 15:
            continue

        # Build raw text from description/summary
        raw_text = strip_html(entry.get("description") or entry.get("summary") or "")
        if not raw_text or len(raw_text) < 30:
            raw_text = headline  # fallback: use headline as content

        if draft_exists(conn, headline, feed_cfg["name"]):
            skipped += 1
            continue

        # Extract entities
        combined_text = f"{headline} {raw_text}"
        entities = extract_entities(combined_text)

        # Detect asset class and direction
        asset_class = detect_asset_class(combined_text)
        direction = detect_direction(combined_text)

        # Generate suggested content
        multi_persona = generate_multi_persona(headline, raw_text, entities, asset_class, direction)
        suggested_flows = generate_suggested_flows(headline, raw_text, asset_class, direction)

        created_at = datetime.now(timezone.utc).isoformat()

        if dry_run:
            print(f"    [DRY RUN] {headline[:70]}...")
            print(f"      → {asset_class} {direction} | assets: {entities['assets'][:5]}")
            added += 1
        else:
            insert_draft(conn, feed_cfg["name"], raw_text, headline,
                        multi_persona, suggested_flows, created_at)
            added += 1

    return added, skipped


def main():
    dry_run = "--dry-run" in sys.argv
    feed_filter = None
    for arg in sys.argv[1:]:
        if arg.startswith("--feed="):
            feed_filter = arg.split("=", 1)[1]

    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found. Run init_db.py first.")
        sys.exit(1)

    # Check for drafts table
    conn = sqlite3.connect(str(DB_PATH))
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "drafts" not in tables:
        print("ERROR: drafts table not found. Run: python3 scripts/init_db.py --migrate")
        conn.close()
        sys.exit(1)
    conn.close()

    feeds = [f for f in RSS_FEEDS if not feed_filter or f["name"] == feed_filter]
    print(f"Fetching {len(feeds)} feeds{' (dry run)' if dry_run else ''}...\n")

    total_added = 0
    total_skipped = 0

    for feed_cfg in feeds:
        print(f"  [{feed_cfg['label']}]")
        entries = fetch_feed(feed_cfg)

        if not entries:
            print(f"    No entries retrieved")
            continue

        print(f"    {len(entries)} entries fetched")

        conn = sqlite3.connect(str(DB_PATH))
        try:
            added, skipped = process_entries(conn, feed_cfg, entries, dry_run)
            if not dry_run:
                conn.commit()
            total_added += added
            total_skipped += skipped
            print(f"    {added} new drafts · {skipped} duplicates skipped")
        finally:
            conn.close()

    print(f"\n  Total: {total_added} new drafts · {total_skipped} duplicates")

    # Show summary
    if not dry_run and total_added > 0:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            pending = conn.execute(
                "SELECT COUNT(*) FROM drafts WHERE status = 'pending_review'"
            ).fetchone()[0]
            print(f"  Pending review queue: {pending}")
        finally:
            conn.close()

    print(json.dumps({"ok": True, "drafts_added": total_added, "duplicates": total_skipped}))


if __name__ == "__main__":
    main()
