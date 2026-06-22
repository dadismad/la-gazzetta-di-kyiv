#!/usr/bin/env python3
"""
cco_newsletter.py — Chief Content Officer: Newsletter Draft Formatter

Synthesizes daily/weekly intelligence briefs in newsletter format.
Voice register: THE DISPATCH + THE BRIEF — institutional grade.

Saves formatted drafts to GCS cco_drafts/newsletter/ pending email provider
API key provisioning (SendGrid or Mailchimp).

Daily brief: top 5 stories, flow summary, market regime
Weekly deep-dive: paradigm analysis, contradiction clusters, capital flow trends

Usage:
  python3 scripts/cco_newsletter.py --mode daily
  python3 scripts/cco_newsletter.py --mode weekly
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from collections import Counter

try:
    from google.cloud import storage  # type: ignore
    HAS_GCP = True
except ImportError:
    HAS_GCP = False

BUCKET_NAME = os.environ.get("GCS_BUCKET", "www.lagazzettadikyiv.com")
DRAFTS_PATH = "cco_drafts/newsletter"
SITE_URL = "https://www.lagazzettadikyiv.com"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_date() -> str:
    return datetime.now(timezone.utc).strftime("%B %d, %Y")


def fetch_data() -> dict:
    """Fetch stories.json and flows.json from GCS."""
    result = {"stories": [], "flows": []}
    if not HAS_GCP:
        return result
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        for blob_name in ["data/stories.json", "data/flows.json"]:
            blob = bucket.blob(blob_name)
            if blob.exists():
                key = "stories" if "stories" in blob_name else "flows"
                data = json.loads(blob.download_as_text())
                result[key] = data.get("stories", data.get("flows", []))
    except Exception as e:
        print(f"[{now()}] Data fetch failed: {e}")
    return result


def format_daily_brief(stories: list[dict], flows: list[dict]) -> str:
    """Generate daily intelligence brief."""
    date_str = now_date()

    # Top 5 by contradiction score
    ranked = sorted(stories, key=lambda s: (
        (s.get("contradiction_score", 0) or 0) * (s.get("confidence_pct", 0) or 0) / 100
    ), reverse=True)[:5]

    lines = [
        f"# La Gazzetta di Kyiv — Daily Brief",
        f"**{date_str}**",
        "",
        "---",
        "",
        "## Top Stories",
        "",
    ]

    for i, story in enumerate(ranked):
        headline = (story.get("headline", "") or "Untitled").strip()
        they_say = (story.get("they_say", "") or "").strip()
        reality = (story.get("reality", "") or "").strip()
        confidence = story.get("confidence_pct", 0)

        lines.append(f"### {i+1}. {headline}")
        if they_say:
            lines.append(f"*They Say:* {they_say}")
        if reality:
            lines.append(f"*Reality:* {reality}")
        if confidence:
            lines.append(f"Confidence: {confidence:.0f}%")
        lines.append("")

    # Flow summary
    if flows:
        inflow_count = sum(1 for f in flows if "in" in (f.get("direction", "") or "").lower())
        outflow_count = len(flows) - inflow_count
        total_amount = sum(f.get("amount_b", 0) or 0 for f in flows)

        lines.extend([
            "---",
            "",
            "## Capital Flow Summary",
            "",
            f"- **Total flows tracked:** {len(flows)}",
            f"- **Inflows:** {inflow_count} | **Outflows:** {outflow_count}",
            f"- **Aggregate capital:** ${total_amount:.1f}B",
            "",
        ])

    # Footer
    lines.extend([
        "---",
        "",
        f"*Full intelligence: [{SITE_URL}]({SITE_URL})*",
        f"*Generated: {now()}*",
    ])

    return "\n".join(lines)


def format_weekly_deep_dive(stories: list[dict], flows: list[dict]) -> str:
    """Generate weekly deep-dive newsletter."""
    date_str = now_date()

    # Aggregate contradiction clusters
    sectors = Counter()
    directions = Counter()
    for s in stories:
        sector = (s.get("sector", "") or "uncategorized").lower()
        sectors[sector] += 1
        direction = (s.get("capital_flow", {}) or {}).get("direction", "") or "unknown"
        directions[direction] += 1

    ranked = sorted(stories, key=lambda s: (
        (s.get("contradiction_score", 0) or 0) * (s.get("confidence_pct", 0) or 0) / 100
    ), reverse=True)[:10]

    lines = [
        f"# La Gazzetta di Kyiv — Weekly Deep-Dive",
        f"**Week ending {date_str}**",
        "",
        "---",
        "",
        "## Paradigm Analysis",
        "",
    ]

    if sectors:
        lines.append("### Contradiction Clusters by Sector")
        for sector, count in sectors.most_common(5):
            lines.append(f"- **{sector.title()}**: {count} stories")
        lines.append("")

    if directions:
        lines.append("### Capital Flow Direction")
        for d, count in directions.most_common():
            lines.append(f"- **{d.title()}**: {count} flows")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Top 10 Stories of the Week",
        "",
    ])

    for i, story in enumerate(ranked):
        headline = (story.get("headline", "") or "Untitled").strip()
        they_say = (story.get("they_say", "") or "").strip()
        reality = (story.get("reality", "") or "").strip()
        lines.append(f"### {i+1}. {headline}")
        if they_say:
            lines.append(f"They Say: {they_say}")
        if reality:
            lines.append(f"Reality: {reality}")
        lines.append("")

    # Footer
    lines.extend([
        "---",
        f"*Full intelligence: [{SITE_URL}]({SITE_URL})*",
        f"*Generated: {now()}*",
    ])

    return "\n".join(lines)


def save_draft(content: str, mode: str) -> bool:
    """Save newsletter draft to GCS."""
    filename = f"{mode}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"

    if not HAS_GCP:
        from pathlib import Path
        Path(f"/tmp/{DRAFTS_PATH}/{filename}").parent.mkdir(parents=True, exist_ok=True)
        Path(f"/tmp/{DRAFTS_PATH}/{filename}").write_text(content)
        print(f"[{now()}] Newsletter draft saved locally: {filename}")
        return False

    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{DRAFTS_PATH}/{filename}")
        blob.upload_from_string(content)
        print(f"[{now()}] Newsletter draft saved: {DRAFTS_PATH}/{filename}")
        return True
    except Exception as e:
        print(f"[{now()}] Newsletter save failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="CCO Newsletter Formatter")
    parser.add_argument("--mode", type=str, default="daily",
                       choices=["daily", "weekly"], help="Brief mode")
    args = parser.parse_args()

    print(f"[{now()}] CCO Newsletter: generating {args.mode} brief...")
    data = fetch_data()
    stories = data.get("stories", [])
    flows = data.get("flows", [])

    print(f"[{now()}] Loaded {len(stories)} stories, {len(flows)} flows")

    if args.mode == "weekly":
        content = format_weekly_deep_dive(stories, flows)
    else:
        content = format_daily_brief(stories, flows)

    save_draft(content, args.mode)
    print(f"DRAFT_SAVED:{args.mode}")


if __name__ == "__main__":
    main()
