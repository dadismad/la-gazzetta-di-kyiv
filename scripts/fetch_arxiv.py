#!/usr/bin/env python3
"""
fetch_arxiv.py — arXiv research monitor for the Gazzetta Sovereign Vault.

Searches arXiv for recent papers in quantitative finance, economics, and
narrative-adjacent domains. Stores raw metadata to data/vault/arxiv/YYYY-MM/.

Usage:
  python3 scripts/fetch_arxiv.py
  python3 scripts/fetch_arxiv.py --max-results 20
"""

import json, os, sys, time, urllib.request, urllib.error, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parent.parent
VAULT = PROJECT / "data" / "vault" / "arxiv"
ARXIV_API = "http://export.arxiv.org/api/query"

# ── Search queries ─────────────────────────────────────────────────
QUERIES = [
    # Quantitative Finance
    "cat:q-fin.*",
    # Economics
    "cat:econ.*",
    # Narrative economics / Shiller
    "all:narrative+economics",
    # Capital flows
    "all:capital+flows+AND+all:macro",
    # Geopolitical risk
    "all:geopolitical+risk+AND+all:financial+markets",
    # Monetary policy
    "all:monetary+policy+AND+all:central+bank",
    # AI / compute economics
    "all:ai+AND+all:compute+AND+all:economics",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def search_arxiv(query: str, max_results: int = 10) -> list:
    """Search arXiv API and return parsed paper entries."""
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    qs = urllib.parse.urlencode(params)
    url = f"{ARXIV_API}?{qs}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
    except Exception as e:
        print(f"  [arxiv] API error for '{query[:50]}': {e}")
        return []

    # Parse Atom XML
    papers = []
    try:
        root = ET.fromstring(raw)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            published_el = entry.find("atom:published", ns)
            id_el = entry.find("atom:id", ns)
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns) if a.find("atom:name", ns) is not None]
            cats = [c.get("term", "") for c in entry.findall("atom:category", ns)]

            papers.append({
                "arxiv_id": id_el.text.strip() if id_el is not None and id_el.text else "",
                "title": title_el.text.strip() if title_el is not None and title_el.text else "",
                "summary": (summary_el.text or "")[:500].strip(),
                "published": published_el.text.strip() if published_el is not None and published_el.text else "",
                "authors": authors,
                "categories": cats,
                "url": id_el.text.strip() if id_el is not None and id_el.text else "",
            })
        time.sleep(3)  # arXiv rate limit: 1 request per 3 seconds
    except ET.ParseError as e:
        print(f"  [arxiv] XML parse error: {e}")

    return papers


def fetch_all(max_per_query: int = 10, hours_back: int = 168) -> dict:
    """Fetch papers across all queries, deduplicate by arxiv_id."""
    seen = set()
    all_papers = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)

    for query in QUERIES:
        print(f"  [arxiv] Searching: {query[:60]}...", end=" ", flush=True)
        papers = search_arxiv(query, max_per_query)
        new_count = 0
        for p in papers:
            if p["arxiv_id"] and p["arxiv_id"] not in seen:
                # Filter by recency
                try:
                    pub = datetime.fromisoformat(p["published"].replace("Z", "+00:00"))
                    if pub < cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
                seen.add(p["arxiv_id"])
                all_papers.append(p)
                new_count += 1
        print(f"{new_count} new")

    return {
        "fetched_at": now_iso(),
        "hours_back": hours_back,
        "total_papers": len(all_papers),
        "queries": len(QUERIES),
        "papers": sorted(all_papers, key=lambda p: p.get("published", ""), reverse=True),
    }


def save_vault(data: dict):
    """Save to data/vault/arxiv/YYYY-MM/latest.json."""
    now = datetime.now(timezone.utc)
    month_dir = VAULT / now.strftime("%Y-%m")
    month_dir.mkdir(parents=True, exist_ok=True)
    path = month_dir / "latest.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [arxiv] Wrote {data['total_papers']} papers to {path}")

    # Ingestion pipeline summary
    summary_path = PROJECT / "data" / "arxiv_intel" / "latest.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "fetched_at": data["fetched_at"],
        "papers": [
            {
                "title": p["title"],
                "summary": p["summary"],
                "url": p["url"],
                "authors": p["authors"],
                "published": p["published"],
            }
            for p in data["papers"]
        ],
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="arXiv research monitor")
    ap.add_argument("--max-results", type=int, default=10, help="Max papers per query")
    ap.add_argument("--hours", type=int, default=168, help="Hours back to fetch (default: 1 week)")
    args = ap.parse_args()

    print(f"[arxiv] Searching {len(QUERIES)} queries, max {args.max_results} papers each, last {args.hours}h...")
    data = fetch_all(max_per_query=args.max_results, hours_back=args.hours)
    save_vault(data)
    print(f"[arxiv] Done: {data['total_papers']} unique papers")
