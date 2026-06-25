#!/usr/bin/env python3
"""fetch_nber.py — NBER Working Papers RSS collector with pdfplumber extraction.

Fetches https://www.nber.org/rss/new.xml, extracts paper metadata,
downloads PDFs, parses text via pdfplumber, stores in Vault.

Usage:
  python3 fetch_nber.py              # Full run
  python3 fetch_nber.py --dry-run    # Preview only, no downloads
  python3 fetch_nber.py --max 5      # Cap papers to process

Hourly cron. Decoupled from governor.
"""

import json
import os
import re
import sys
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests
import pdfplumber

# ── Paths ──
PROJECT = Path(os.environ.get("GAZZETTA_HOME", "/opt/gazzetta-di-kyiv"))
VAULT_RAW = PROJECT / "data" / "vault" / "raw" / "nber"
LEDGER_PATH = VAULT_RAW / "nber_ledger.json"
SUMMARY_PATH = VAULT_RAW / "latest.json"

NBER_RSS = "https://www.nber.org/rss/new.xml"
PDF_BASE = "https://www.nber.org/system/files/working_papers"
TIMEOUT = 15
MAX_RETRIES = 2
REQUEST_DELAY = 3  # seconds between PDF downloads (be gentle)


def now_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_ledger() -> dict:
    """Return {paper_id: sha256_hash} of previously processed papers."""
    if LEDGER_PATH.exists():
        try:
            with open(LEDGER_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_ledger(ledger: dict):
    VAULT_RAW.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)


def fetch_rss() -> list:
    """Fetch NBER RSS feed, return list of paper dicts."""
    print(f"[{now_ts()}] Fetching NBER RSS: {NBER_RSS}")
    feed = feedparser.parse(NBER_RSS)

    if feed.bozo and not feed.entries:
        print(f"[{now_ts()}] RSS parse error: {feed.bozo_exception}")
        return []

    papers = []
    for entry in feed.entries:
        # Extract paper ID from link: /papers/w35337 → w35337
        paper_id = ""
        match = re.search(r'/papers/(w\d+)', entry.get("link", ""))
        if match:
            paper_id = match.group(1)
        elif "link" in entry:
            match = re.search(r'(w\d+)', entry["link"])
            if match:
                paper_id = match.group(1)

        if not paper_id:
            continue

        papers.append({
            "paper_id": paper_id,
            "title": entry.get("title", "").strip(),
            "authors": entry.get("author", "").strip(),
            "link": entry.get("link", ""),
            "abstract": entry.get("description", entry.get("summary", "")).strip(),
            "published": entry.get("published", entry.get("updated", "")),
            "pdf_url": f"{PDF_BASE}/{paper_id}/{paper_id}.pdf",
        })

    print(f"[{now_ts()}] RSS fetched: {len(papers)} papers")
    return papers


def download_pdf(url: str, paper_id: str) -> bytes | None:
    """Download PDF with retry. Returns bytes or None."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; GazzettaDiKyiv/1.0)"}
    for attempt in range(MAX_RETRIES + 1):
        try:
            if attempt > 0:
                wait = 2 ** attempt
                print(f"  Retry {attempt}/{MAX_RETRIES} in {wait}s...")
                time.sleep(wait)
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)
            resp.raise_for_status()
            if b"%PDF" in resp.content[:1024]:
                return resp.content
            else:
                print(f"  Not a PDF: {url}")
                return None
        except Exception as e:
            print(f"  Download error ({attempt}): {e}")
    return None


def extract_text(pdf_bytes: bytes, paper_id: str) -> str:
    """Extract text from PDF bytes using pdfplumber."""
    month_dir = datetime.now(timezone.utc).strftime("%Y-%m")
    tmp_path = VAULT_RAW / month_dir / f"{paper_id}.pdf"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)

    # Write temp PDF
    with open(tmp_path, "wb") as f:
        f.write(pdf_bytes)

    try:
        text_parts = []
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages[:20]:  # First 20 pages max
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"  pdfplumber error: {e}")
        return ""
    finally:
        # Clean up temp PDF
        try:
            tmp_path.unlink()
        except OSError:
            pass


def hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def save_paper(paper: dict, text: str):
    """Save extracted text to vault."""
    month_dir = datetime.now(timezone.utc).strftime("%Y-%m")
    out_dir = VAULT_RAW / month_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    md_content = f"""---
source: NBER
paper_id: {paper["paper_id"]}
title: {paper["title"]}
authors: {paper["authors"]}
url: {paper["pdf_url"]}
published: {paper["published"]}
fetched_at: {now_ts()}
---

# {paper["title"]}

**Authors:** {paper["authors"]}
**Paper ID:** {paper["paper_id"]}
**Published:** {paper["published"]}
**URL:** {paper["link"]}

## Abstract

{paper["abstract"]}

## Full Text

{text[:50000]}
"""
    md_path = out_dir / f"{paper['paper_id']}.md"
    with open(md_path, "w") as f:
        f.write(md_content)
    return md_path


def main():
    import argparse
    ap = argparse.ArgumentParser(description="NBER Working Papers Collector")
    ap.add_argument("--dry-run", action="store_true", help="Preview only")
    ap.add_argument("--max", type=int, default=0, dest="max_papers",
                    help="Max papers to process (0=all)")
    args = ap.parse_args()

    papers = fetch_rss()
    if not papers:
        print(f"[{now_ts()}] No papers found. Exiting.")
        return

    ledger = load_ledger()
    processed = 0
    skipped = 0
    new_papers = []

    for paper in papers:
        if args.max_papers and processed >= args.max_papers:
            break

        pid = paper["paper_id"]

        # Check if already processed
        if pid in ledger:
            skipped += 1
            continue

        print(f"\n[{now_ts()}] Processing: {pid} — {paper['title'][:80]}")

        if args.dry_run:
            print(f"  [DRY RUN] Would download: {paper['pdf_url']}")
            processed += 1
            continue

        # Download PDF
        pdf_bytes = download_pdf(paper["pdf_url"], pid)
        if not pdf_bytes:
            print(f"  Failed to download PDF for {pid}")
            continue

        # Extract text
        text = extract_text(pdf_bytes, pid)
        if not text:
            print(f"  No text extracted from {pid}")
            continue

        # Hash and dedup
        content_hash = hash_content(text)

        # Save paper
        md_path = save_paper(paper, text)
        print(f"  Saved: {md_path} ({len(text)} chars)")

        # Update ledger
        ledger[pid] = content_hash
        new_papers.append({
            "paper_id": pid,
            "title": paper["title"],
            "authors": paper["authors"],
            "abstract": paper["abstract"][:500],
            "path": str(md_path),
            "hash": content_hash,
        })

        processed += 1

        # Be gentle to NBER's server
        if not args.dry_run:
            time.sleep(REQUEST_DELAY)

    # Save state
    save_ledger(ledger)

    # Write summary JSON for downstream ingestion
    summary = {
        "source": "NBER",
        "fetched_at": now_ts(),
        "papers_found": len(papers),
        "new_processed": processed,
        "skipped_existing": skipped,
        "papers": new_papers,
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n[{now_ts()}] Done. Found: {len(papers)}, New: {processed}, Skipped: {skipped}")
    print(f"  Summary: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
