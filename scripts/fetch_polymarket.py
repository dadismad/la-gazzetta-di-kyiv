#!/usr/bin/env python3
"""
fetch_polymarket.py — Fetch relevant Polymarket prediction market odds.

Uses Gamma API /events endpoint with tag filtering for Gazzetta's coverage.
Markets: geopolitical, macro, crypto/commodity events.

Output: site/data/polymarket_odds.json
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
GAMMA_API = "https://gamma-api.polymarket.com"

# Tags relevant to Gazzetta coverage (use exact slugs from Polymarket)
QUERIES = [
    "iran", "israel", "ukraine", "taiwan", "china",
    "oil", "crude", "sanctions",
    "fed", "rate", "recession", "inflation",
    "bitcoin", "btc", "ethereum", "solana", "crypto",
    "trump", "election", "war", "conflict", "middle-east",
]


def search_markets(query, limit=5):
    """Search Polymarket for a query using public-search endpoint."""
    try:
        url = f"{GAMMA_API}/public-search?q={query}"
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "GazzettaDiKyiv/2.0"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        results = []
        events = data.get("events", []) if isinstance(data, dict) else []
        for event in events[:limit]:
            for market in event.get("markets", []):
                out_prices = market.get("outcomePrices", "[]")
                out_labels = market.get("outcomes", "[]")
                try:
                    prices = json.loads(out_prices)
                    labels = json.loads(out_labels)
                except (json.JSONDecodeError, TypeError):
                    prices = []
                    labels = []
                
                results.append({
                    "id": market.get("id", ""),
                    "question": market.get("question", ""),
                    "condition_id": market.get("conditionId", ""),
                    "outcomes": dict(zip(labels, prices)) if labels and prices else {},
                    "volume": float(market.get("volume", 0)),
                    "end_date": market.get("endDate", ""),
                    "event_title": event.get("title", ""),
                    "query": query,
                })
        return results
    except Exception as e:
        print(f"  ⚠ {query}: {e}", file=sys.stderr)
        return []


def fetch_relevant_markets():
    """Fetch markets for all relevant queries, deduplicate, sort by volume."""
    seen = set()
    all_markets = []
    
    for query in QUERIES:
        markets = search_markets(query, limit=3)
        for m in markets:
            q = m["question"]
            if q not in seen:
                seen.add(q)
                all_markets.append(m)
    
    all_markets.sort(key=lambda x: x["volume"], reverse=True)
    return all_markets[:20]


def main():
    print("[fetch_polymarket] Starting...")
    
    markets = fetch_relevant_markets()
    print(f"  Fetched {len(markets)} unique markets")
    
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "markets": [],
    }
    
    for m in markets:
        entry = {
            "id": m["id"],
            "question": m["question"],
            "url": f"https://polymarket.com/event/{m['id']}",
            "event": m["event_title"],
            "volume": m["volume"],
            "end_date": m["end_date"],
            "odds": {},
        }
        
        for outcome, price in m.get("outcomes", {}).items():
            pct = float(price) * 100 if isinstance(price, (int, float, str)) else 0
            entry["odds"][outcome] = round(float(pct) if isinstance(pct, (int, float)) else 0, 1)
        
        output["markets"].append(entry)
    
    out_path = PROJECT / "site" / "data" / "polymarket_odds.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    
    if output["markets"]:
        top = output["markets"][0]
        print(f"  Top market: {top['question'][:80]} ({top['odds']})")
    
    print(f"  ✓ polymarket_odds.json: {len(output['markets'])} markets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
