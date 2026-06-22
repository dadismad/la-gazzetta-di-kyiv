#!/usr/bin/env python3
"""
link_processor.py — Process a URL into a classified story in gazzetta.db.

Flow:
  1. Accept URL from command line (or stdin)
  2. Fetch page content
  3. Extract: title, source domain, date, body text
  4. Classify into 1 of 6 containers
  5. Assign power-vector tags
  6. Write to gazzetta.db
  7. Checkpoint WAL
  8. Upload DB to GCS
  9. Optional: instant-publish to GCS stories.json

Usage:
  python3 scripts/link_processor.py <url> [--instant] [--dry-run]
  echo "https://..." | python3 scripts/link_processor.py --stdin
"""

import json, os, sys, re, hashlib, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# ── Project paths ──
PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT / "gazzetta.db"
DATA = PROJECT / "data"
BUCKET = "www.lagazzettadikyiv.com"

# ── Container classification rules ──
CONTAINER_KEYWORDS = {
    "monetary_order": [
        "dollar", "fed", "treasury", "bitcoin", "crypto", "cbdc", "stablecoin",
        "sanctions", "swift", "reserve currency", "de-dollarization", "imf",
        "sovereign debt", "bond market", "yield curve", "federal reserve",
        "ecb", "pboc", "inflation", "etf", "blackrock", "tokenized"
    ],
    "energy_resources": [
        "oil", "wti", "brent", "crude", "opec", "lng", "pipeline",
        "fusion", "nuclear", "reactor", "solar", "renewable",
        "lithium", "rare earth", "critical mineral", "grid",
        "electric", "power plant", "energy", "barrel", "bpd",
        "commodities", "copper", "gold", "silver", "uranium"
    ],
    "technology_ai": [
        "ai", "artificial intelligence", "openai", "semiconductor", "chip",
        "nvidia", "tsmc", "intel", "quantum", "spacex", "starlink",
        "startup", "ipo", "venture capital", "robot", "machine learning",
        "gpu", "huawei", "tiktok", "deepseek", "cloud", "aws", "azure"
    ],
    "information_narrative": [
        "disinformation", "misinformation", "propaganda", "fake news",
        "censorship", "social media", "twitter", "telegram",
        "information war", "narrative", "deepfake", "troll farm",
        "election interference", "cyber", "content moderation"
    ],
    "biosecurity_health": [
        "biotech", "longevity", "anti-aging", "gene therapy", "crispr",
        "pandemic", "vaccine", "mrna", "fda", "clinical trial",
        "pharma", "cancer", "alzheimer", "immunotherapy", "healthspan",
        "bioweapon", "gain of function", "who", "public health"
    ],
    "flashpoints": [
        "iran", "israel", "gaza", "lebanon", "hezbollah", "ukraine",
        "russia", "taiwan", "south china sea", "nato", "missile",
        "drone", "war", "conflict", "military", "troops", "navy",
        "sanction", "blockade", "coup", "nuclear weapon", "ceasefire"
    ],
}

TAG_KEYWORDS = {
    "american-decline": ["us", "america", "pentagon", "washington", "trump", "biden", "dollar"],
    "china-ascendancy": ["china", "beijing", "xi", "bri", "rmb", "yuan", "taiwan", "ccp"],
    "eu-strategy": ["eu", "european", "brussels", "eurozone", "ecb", "germany", "france"],
    "global-south": ["africa", "india", "brazil", "asean", "brics", "global south"],
    "russia": ["russia", "moscow", "kremlin", "putin"],
}


def fetch_url(url):
    """Fetch and extract content from URL."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("ERROR: requests and beautifulsoup4 required")
        sys.exit(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GazzettaBot/2.0; +https://lagazzettadikyiv.com)"
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Title
    title = None
    if soup.find("meta", property="og:title"):
        title = soup.find("meta", property="og:title")["content"]
    elif soup.title:
        title = soup.title.string
    if title:
        title = title.strip()[:300]

    # Source domain
    source_name = urlparse(url).netloc.replace("www.", "")

    # Date
    date = None
    for meta_name in ["article:published_time", "pubdate", "date"]:
        tag = soup.find("meta", {"name": meta_name}) or soup.find("meta", property=meta_name)
        if tag and tag.get("content"):
            date = tag["content"][:19]
            break

    # Body text
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    body = soup.get_text(separator=" ", strip=True)[:5000]

    return {
        "title": title or url,
        "source_name": source_name,
        "source_url": url,
        "date": date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "body": body,
    }


def classify(text):
    """Return (container, [tags])."""
    text_lower = text.lower()
    tokens = set(re.findall(r'[a-z0-9]+', text_lower))

    # Container
    scores = {}
    for cname, keywords in CONTAINER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[cname] = score

    container = max(scores, key=scores.get) if scores else "flashpoints"

    # Tags
    tags = []
    for tag, keywords in TAG_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        if matches >= 2:
            tags.append(tag)

    return container, tags


def write_to_db(content, container, tags):
    """Write story to gazzetta.db."""
    story_id = hashlib.sha256(content["source_url"].encode()).hexdigest()[:16]
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")

    full_json = json.dumps({
        "story_id": story_id,
        "headline": content["title"],
        "source": "osint_" + content["source_name"].replace(".", "_").replace("-", "_"),
        "source_name": content["source_name"],
        "source_url": content["source_url"],
        "date_published": content["date"],
        "generated_at": now,
        "container": container,
        "contradiction_score": 50,  # default — Agent refines later
        "tier": "DEVELOPING",
        "sector": container,
        "pillar": "multi_pillar",
        "confidence": "medium",
        "freshness": "breaking",
        "horizon": "24-72h",
        "they_say": content.get("title", ""),
        "reality": content.get("title", ""),
        "thesis": "",
        "actors": [],
        "evidence": [f"source: {content['source_name']}", f"url: {content['source_url']}"],
        "entity_tags": {"assets": [], "geographies": [], "actors": [], "instruments": []},
        "time_decay": {"half_life_hours": 36.0, "decay_curve": "exponential", "current_freshness": 1.0},
        "capital_flow": {"direction": "neutral", "amount_b": 0, "asset_class": container, "projected": False},
        "multi_persona": {"c_suite": {"headline": content.get("title", "")}},
        "impacted_flows": [],
        "associated_positions": [],
        "actionable_trade": "",
        "invalidation_trigger": "",
        "paradigm_pillar": "multi_pillar",
        "paradigm_implications": [],
        "portfolio_implication": "",
        "capital_flow_implication": "",
        "body": content.get("body", ""),
    }, ensure_ascii=False)

    conn.execute("""
        INSERT OR REPLACE INTO stories (id, headline, sector, pillar, tier, container, 
                   generated_at, full_json, confidence, contradiction_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (story_id, content["title"][:200], container, "multi_pillar", "DEVELOPING",
          container, now, full_json, "medium", 50))

    # Tags
    for tag in tags:
        conn.execute("INSERT OR IGNORE INTO story_tags (story_id, tag) VALUES (?, ?)",
                     (story_id, tag))

    conn.commit()
    conn.close()

    print(f"  ✓ Written to DB: {story_id} → {container}")
    return story_id


def checkpoint_and_upload():
    """Checkpoint WAL and upload DB to GCS."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()

    # Upload to GCS
    import subprocess
    gsutil = os.path.expanduser(
        "~/lagazzettadikyiv/devvit/google-cloud-sdk/bin/gsutil"
    )
    subprocess.run([gsutil, "cp", str(DB_PATH), f"gs://{BUCKET}/gazzetta.db"],
                   check=False)
    print(f"  ✓ DB uploaded to gs://{BUCKET}/gazzetta.db")


def main():
    url = None
    instant = "--instant" in sys.argv
    dry_run = "--dry-run" in sys.argv
    stdin_mode = "--stdin" in sys.argv

    if stdin_mode:
        url = sys.stdin.read().strip()
    else:
        for arg in sys.argv[1:]:
            if arg.startswith("http"):
                url = arg
                break

    if not url:
        print("Usage: python3 scripts/link_processor.py <url> [--instant] [--dry-run]")
        sys.exit(1)

    print(f"Processing: {url}")

    # Fetch
    try:
        content = fetch_url(url)
    except Exception as e:
        print(f"ERROR fetching URL: {e}")
        sys.exit(1)

    print(f"  Title: {content['title'][:100]}")
    print(f"  Source: {content['source_name']}")

    # Classify
    text = (content["title"] + " " + content["body"])
    container, tags = classify(text)
    print(f"  Container: {container}")
    print(f"  Tags: {tags or 'none'}")

    if dry_run:
        print("DRY RUN — not writing to DB")
        return

    # Write
    story_id = write_to_db(content, container, tags)

    # Upload DB
    checkpoint_and_upload()

    # Regenerate JSON (optional: for pipeline use)
    if instant:
        print("  Running db_to_json.py for instant publish...")
        import subprocess
        subprocess.run([sys.executable, str(PROJECT / "scripts" / "db_to_json.py")])
        print("  ✓ stories.json regenerated — ready for GCS sync")

    print(f"\nDone. Story {story_id} in {container}. Pipeline will deploy ≤10 min.")


if __name__ == "__main__":
    main()
