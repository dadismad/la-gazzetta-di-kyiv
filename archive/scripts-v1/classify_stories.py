#!/usr/bin/env python3
"""
classify_stories.py — Backfill container + tags for all 377 stories.

Classification rules (domain-first, tag-second):
  1. MONETARY ORDER — dollar, bitcoin, crypto, cbdc, sanctions, reserve, debt
  2. ENERGY & RESOURCES — oil, gas, fusion, nuclear, rare earth, lithium, grid
  3. TECHNOLOGY & AI — semiconductor, chip, ai, quantum, spacex, data center
  4. INFORMATION & NARRATIVE — disinformation, propaganda, censorship, media
  5. BIOSECURITY & HEALTH — biotech, pandemic, vaccine, longevity, pharma, health
  6. FLASHPOINTS — iran, israel, ukraine, taiwan, houthi, hezbollah, missile, war

Tags (power vectors): american-decline, china-ascendancy, eu-strategy, 
                      global-south, russia, flashpoint

Usage: python3 scripts/classify_stories.py [--dry-run]
"""

import sqlite3, json, os, sys, re
from datetime import datetime, timezone

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT, "gazzetta.db")
DRY_RUN = "--dry-run" in sys.argv

# ── Container classification rules ──
# Ordered by specificity — more specific containers checked first
CONTAINER_RULES = [
    # (container_name, keywords_in_headline, match_sectors, match_pillars)
    ("monetary_order", [
        "dollar", "fed ", "treasury", "deficit", "debt ceiling", "debt crisis",
        "bitcoin", "btc", "crypto", "ethereum", "eth", "defi", "stablecoin",
        "cbdc", "blockchain", "coinbase", "binance", "sanctions", "swift",
        "reserve currency", "de-dollarization", "imf", "sovereign debt",
        "bond market", "bond vigilante", "yield curve", "rate hike", "rate cut",
        "federal reserve", "ecb", "pboc", "monetary", "inflation",
        "strategy resumes bitcoin", "blackrock", "etf", "tokenized"
    ], 
    ["crypto", "fx", "fixed_income"], 
    ["blockchain_agentic", "dollar_decline"]),
    
    ("energy_resources", [
        "oil ", "wti", "brent", "crude", "opec", "gas ", "lng", "pipeline",
        "fusion", "nuclear", "reactor", "solar", "wind ", "renewable",
        "lithium", "rare earth", "critical mineral", "cobalt", "nickel",
        "grid", "electric", "power plant", "energy", "barrel", "bpd",
        "strategic petroleum reserve", "spr", "gas price", "oil price",
        "petroleum", "hormuz", "tanker", "offshore", "upstream", "downstream",
        "commodities", "copper", "gold ", "silver", "uranium",
        "data center", "data centre"
    ], 
    ["commodities"], 
    ["abundance_tech"]),
    
    ("technology_ai", [
        "ai ", "artificial intelligence", "openai", "anthropic", "google ai",
        "semiconductor", "chip ", "nvidia", "tsmc", "intel", "amd ",
        "quantum", "spacex", "starlink", "satellite", "tech ",
        "silicon valley", "startup", "ipo ", "venture capital",
        "autonomous", "robot", "machine learning", "llm", "gpu",
        "huawei", "tiktok", "deepseek", "apple ", "microsoft",
        "software", "cloud ", "aws", "azure", "saas",
        "tech sovereignty", "technology", "innovation"
    ], 
    ["tech", "equities"], 
    []),
    
    ("information_narrative", [
        "disinformation", "misinformation", "propaganda", "fake news",
        "censorship", "social media", "twitter", "x.com", "telegram",
        "information war", "narrative", "media ", "deepfake",
        "troll farm", "bot network", "influence operation",
        "election interference", "hack and leak", "cyber",
        "content moderation", "free speech", "deplatform",
        "state media", "rt ", "sputnik", "voice of america"
    ], 
    [], 
    []),
    
    ("biosecurity_health", [
        "biotech", "longevity", "anti-aging", "gene therapy", "crispr",
        "pandemic", "covid", "vaccine", "mrna", "fda ", "clinical trial",
        "pharma", "drug ", "cancer", "alzheimer", "immunotherapy",
        "healthspan", "life extension", "bioweapon", "biological weapon",
        "gain of function", "biosecurity", "who ", "world health",
        "aging", "dementia", "diabetes", "obesity", "public health"
    ], 
    [], 
    []),
    
    ("flashpoints", [
        "iran", "israel", "gaza", "lebanon", "hezbollah", "houthi",
        "ukraine", "zelensky", "putin", "russia", "moscow", "kyiv",
        "taiwan", "south china sea", "xinjiang", "tibet",
        "nato", "missile", "drone", "strike", "ballistic",
        "war ", "conflict", "military", "troops", "navy", "air force",
        "idf", "hamas", "yemen", "syria", "iraq", "afghanistan",
        "sanction", "blockade", "embargo", "coup", "regime",
        "nuclear weapon", "icbm", "hypersonic", "chemical weapon",
        "ben-gvir", "nabatieh", "tyre", "dahiyeh", "apache",
        "kinetic", "ceasefire", "peace deal", "hostage", "refugee",
        "hormuz", "strait of hormuz", "red sea", "suez",
        "terror", "insurgency", "jihad", "militia", "rebels"
    ], 
    ["defense"], 
    ["multi_pillar", "eu_fragmentation"]),
]

# ── Power vector tag rules ──
TAG_RULES = [
    ("american-decline", [
        "us deficit", "us debt", "us military", "pentagon", "us treasury",
        "federal reserve", "america", "united states", "us ", "us-",
        "wall street", "dow ", "s&p", "nasdaq", "spx", "us existing home",
        "us adp", "us producer", "us doe", "us emergency oil", "us cements",
        "republicans", "democrats", "congress", "white house", "biden", "trump",
        "dollar hegemony", "american", "new york", "washington",
        "us strikes", "us targets", "us-iran", "us sanctions"
    ]),
    ("china-ascendancy", [
        "china", "beijing", "taiwan", "xi ", "bri", "rmb", "yuan",
        "south china sea", "huawei", "tiktok", "wechat", "alibaba", "tencent",
        "semiconductor", "chip export", "rare earth",
        "ccp", "communist party", "shenzhen", "shanghai", "hong kong",
        "belt and road", "digital yuan", "chinese"
    ]),
    ("eu-strategy", [
        "eu ", "european union", "brussels", "eurozone", "ecb",
        "europe", "germany", "france", "berlin", "paris",
        "nato", "article 5", "european", "schengen", "brexit"
    ]),
    ("global-south", [
        "africa", "india", "brazil", "global south", "asean", "indonesia",
        "nigeria", "south africa", "kenya", "ethiopia",
        "brics", "non-aligned", "developing world", "global majority"
    ]),
    ("russia", [
        "russia", "moscow", "kremlin", "putin", "russian",
        "wagner", "fsb", "gru", "soviet", "st petersburg"
    ]),
]


def tokenize(text):
    """Lowercase, strip punctuation, return tokens."""
    if not text:
        return []
    return re.findall(r'[a-z0-9]+', text.lower())


def classify_story(sector, pillar, headline):
    """Return (container_name, [tags]) for a story."""
    text = (headline or "").lower()
    tokens = set(tokenize(text))
    
    # ── Pass 1: Container ──
    container = None
    best_score = 0
    
    for cname, keywords, sectors, pillars in CONTAINER_RULES:
        score = 0
        
        # Sector match (strong signal)
        if sector and sector.lower() in [s.lower() for s in sectors]:
            score += 5
        
        # Pillar match
        if pillar and pillar.lower() in [p.lower() for p in pillars]:
            score += 3
        
        # Keyword density
        for kw in keywords:
            if kw.lower() in text:
                score += 1
        
        if score > best_score:
            best_score = score
            container = cname
    
    # Fallback: if no container matched, use sector heuristic
    if not container:
        s = (sector or "").lower()
        if s == "crypto":
            container = "monetary_order"
        elif s in ("commodities",):
            container = "energy_resources"
        elif s in ("tech", "equities"):
            container = "technology_ai"
        elif s in ("defense",):
            container = "flashpoints"
        elif s in ("fx", "fixed_income"):
            container = "monetary_order"
        else:
            container = "flashpoints"  # default catch-all
    
    # ── Pass 2: Tags ──
    tags = []
    for tag_name, keywords in TAG_RULES:
        matches = 0
        for kw in keywords:
            if kw.lower() in text:
                matches += 1
        if matches >= 2:  # threshold: 2+ keyword matches
            tags.append(tag_name)
    
    return container, tags


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    
    rows = conn.execute("""
        SELECT id, sector, pillar, headline, full_json 
        FROM stories 
        WHERE full_json IS NOT NULL
    """).fetchall()
    
    total = len(rows)
    classified = 0
    container_counts = {}
    tag_counts = {}
    
    updates = []
    tag_inserts = []
    
    for sid, sector, pillar, headline, fj_str in rows:
        container, tags = classify_story(sector, pillar, headline)
        
        if container:
            updates.append((container, sid))
            container_counts[container] = container_counts.get(container, 0) + 1
            classified += 1
        
        for tag in tags:
            tag_inserts.append((sid, tag))
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    if DRY_RUN:
        print(f"DRY RUN — would classify {classified}/{total} stories:\n")
        for c, n in sorted(container_counts.items(), key=lambda x: -x[1]):
            print(f"  {c:30s} {n:4d}")
        print(f"\nTags:")
        for t, n in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"  {t:25s} {n:4d}")
        print(f"\n  {'UNCLASSIFIED':30s} {total - classified:4d}")
    else:
        # Batch update containers
        conn.executemany(
            "UPDATE stories SET container = ? WHERE id = ?", updates
        )
        
        # Batch insert tags
        conn.executemany(
            "INSERT OR IGNORE INTO story_tags (story_id, tag) VALUES (?, ?)", 
            tag_inserts
        )
        
        conn.commit()
        
        print(f"Classified {classified}/{total} stories:")
        for c, n in sorted(container_counts.items(), key=lambda x: -x[1]):
            print(f"  {c:30s} {n:4d}")
        print(f"\nTags assigned:")
        for t, n in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"  {t:25s} {n:4d}")
        print(f"\n  UNCLASSIFIED: {total - classified}")
    
    conn.close()


if __name__ == "__main__":
    main()
