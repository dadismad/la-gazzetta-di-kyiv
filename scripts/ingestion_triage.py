#!/usr/bin/env python3
"""
ingestion_triage.py -- RSS + YouTube transcript ingestion with SHA-256 dedup.

Pulls RSS feeds and YouTube transcripts, hashes full text with SHA-256,
and saves only previously-unseen items to gazzetta.db. This is the cost-
control gate -- duplicates never reach the LLM enrichment layer.

Dependencies: feedparser, youtube-transcript-api, requests
  pip install feedparser youtube-transcript-api requests

Usage:
  python3 ingestion_triage.py
  python3 ingestion_triage.py --rss-only
  python3 ingestion_triage.py --youtube-only
  python3 ingestion_triage.py -v dQw4w9WgXcQ,AnotherVideoId
"""

import hashlib
import sqlite3
import sys
import os
import re
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs

# ── external deps ───────────────────────────────────────────────────
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import requests

# ── config ──────────────────────────────────────────────────────────
PROJECT = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("GAZZETTA_DB_PATH", str(PROJECT / "gazzetta.db"))

RSS_FEEDS = [
    {"url": "https://www.ecb.europa.eu/rss/press.html",      "narrative": "dollar_decline"},
    {"url": "https://www.world-nuclear-news.org/feed",       "narrative": "energy_sovereignty"},
    {"url": "https://www.scmp.com/rss/91/feed",              "narrative": "china_ascent"},
    {"url": "https://www.technologyreview.com/feed/",        "narrative": "tech_convergence"},
    {"url": "https://spacenews.com/feed/",                   "narrative": "space_economy"},
    {"url": "https://www.fiercebiotech.com/feed",            "narrative": "gene_editing"},
    {"url": "https://feeds.bloomberg.com/markets/news.rss",  "narrative": "deglobalization"},
    {"url": "https://www.ft.com/markets?format=rss",         "narrative": "dollar_decline"},
    {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/","narrative": "crypto_reserve"},
    {"url": "https://www.al-monitor.com/feed",               "narrative": "china_ascent"},
    {"url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147", "narrative": "tech_convergence"},
]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ingestion_hashes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    hash          TEXT NOT NULL UNIQUE,
    source_url    TEXT NOT NULL,
    source_type   TEXT NOT NULL CHECK (source_type IN ('rss','youtube','manual')),
    title         TEXT,
    text_preview  TEXT,
    full_text     TEXT,
    narrative_tag TEXT,
    created_at    TEXT DEFAULT (datetime('now'))
)
"""


# ── db helpers ──────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def ensure_tables(conn):
    conn.execute(CREATE_TABLE_SQL)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ingestion_hash ON ingestion_hashes(hash)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ingestion_source ON ingestion_hashes(source_url)"
    )
    conn.commit()


def hash_exists(conn, sha256_hex):
    row = conn.execute(
        "SELECT 1 FROM ingestion_hashes WHERE hash=?", (sha256_hex,)
    ).fetchone()
    return row is not None


def save_ingestion(conn, h, url, stype, title, text, narrative=None):
    if hash_exists(conn, h):
        return False
    preview = text[:500] if text else ""
    conn.execute(
        """INSERT INTO ingestion_hashes
           (hash, source_url, source_type, title, text_preview, full_text, narrative_tag)
           VALUES (?,?,?,?,?,?,?)""",
        (h, url, stype, title, preview, text, narrative),
    )
    conn.commit()
    return True


# ── hashing ─────────────────────────────────────────────────────────
def sha256(text):
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


# ── RSS ─────────────────────────────────────────────────────────────
def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "")


def fetch_rss(feed_url, narrative):
    """Return list of (title, url, text) tuples."""
    items = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = strip_html(entry.get("summary", entry.get("description", "")))
            if title and link:
                items.append((title, link, f"{title}\n\n{summary}", narrative))
    except Exception as e:
        print(f"  rss error {feed_url}: {e}", file=sys.stderr)
    return items


def process_rss(conn):
    print("-- RSS --")
    new, skip = 0, 0
    for cfg in RSS_FEEDS:
        for title, url, text, narrative in fetch_rss(cfg["url"], cfg["narrative"]):
            h = sha256(text)
            if save_ingestion(conn, h, url, "rss", title, text, narrative):
                new += 1
                print(f"  NEW {title[:90]}")
            else:
                skip += 1
    print(f"  rss: +{new}  dupes:{skip}")
    return new


# ── YouTube ─────────────────────────────────────────────────────────
def extract_video_id(ref):
    """Return 11-char video ID from URL or bare ID, else None."""
    if re.match(r"^[A-Za-z0-9_-]{11}$", ref):
        return ref
    p = urlparse(ref)
    if p.netloc in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        return parse_qs(p.query).get("v", [None])[0]
    if p.netloc == "youtu.be":
        return p.path.lstrip("/")
    return None


def fetch_transcript(video_id):
    try:
        parts = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        return " ".join(e["text"] for e in parts)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        print(f"    transcript error {video_id}: {e}", file=sys.stderr)
        return None


def fetch_yt_title(video_id):
    try:
        r = requests.get(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            timeout=10,
        )
        if r.status_code == 200:
            return r.json().get("title", "")
    except Exception:
        pass
    return ""


def process_youtube(conn, video_ids=None):
    print("-- YouTube --")
    new = 0
    for ref in (video_ids or []):
        vid = extract_video_id(ref)
        if not vid:
            print(f"  bad ref: {ref}")
            continue
        url = f"https://www.youtube.com/watch?v={vid}"

        if conn.execute(
            "SELECT 1 FROM ingestion_hashes WHERE source_url=?", (url,)
        ).fetchone():
            print(f"  SKIP {vid} (already ingested)")
            continue

        title = fetch_yt_title(vid)
        transcript = fetch_transcript(vid)
        if not transcript:
            print(f"  SKIP {vid} (no transcript)")
            continue

        text = f"{title}\n\n{transcript}"
        h = sha256(text)
        if save_ingestion(conn, h, url, "youtube", title, text):
            new += 1
            print(f"  SAVED {vid}: {title[:80]}  ({len(transcript)} chars)")
        else:
            print(f"  SKIP {vid} (hash collision)")

    print(f"  youtube: +{new}")
    return new


# ── main ────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Ingestion triage: RSS + YouTube dedup")
    p.add_argument("--rss-only", action="store_true")
    p.add_argument("--youtube-only", action="store_true")
    p.add_argument("-v", "--video", nargs="*", help="YouTube video IDs or URLs")
    args = p.parse_args()

    conn = get_db()
    ensure_tables(conn)
    total = 0

    if not args.youtube_only:
        total += process_rss(conn)
    if not args.rss_only:
        total += process_youtube(conn, args.video)

    conn.close()
    print(f"\ntotal new items: {total}")


if __name__ == "__main__":
    main()
