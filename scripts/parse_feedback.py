#!/usr/bin/env python3
"""parse_feedback.py — Reads feedback/focus_groups.md, compiles backlog items.

Outputs a structured JSON report of design/technical modifications for the backlog.
Each entry includes: persona, priority, category, and suggested action.
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FEEDBACK_PATH = PROJECT / "feedback" / "focus_groups.md"
OUTPUT_PATH = PROJECT / "data" / "feedback_backlog.json"

CATEGORY_KEYWORDS = {
    "UI/UX": ["button", "badge", "mobile", "view", "font", "color", "layout", "read", "cut off", "spacing"],
    "Data Freshness": ["time", "timestamp", "fresh", "stale", "real-time", "static", "update"],
    "Actionability": ["buy", "sell", "do with", "trade", "entry", "stop", "target", "direction", "signal"],
    "Analytics": ["formula", "scoring", "score", "heat", "correlation", "metric", "calculation", "magnitude"],
    "Content Format": ["words", "text", "paragraph", "bullet", "concise", "summary"],
    "Distribution": ["pdf", "export", "email", "report", "brief", "presentation", "committee"],
    "Trust/Provenance": ["source", "provenance", "trust", "verify", "data quality", "arbitrary"],
}


def parse_feedback():
    if not FEEDBACK_PATH.exists():
        return {"ok": False, "error": "feedback/focus_groups.md not found"}

    text = FEEDBACK_PATH.read_text()
    entries = []

    # Match: [YYYY-MM-DD] Persona: Feedback text — Priority
    pattern = re.compile(
        r'\[(\d{4}-\d{2}-\d{2})\]\s+(\w[^:]+?):\s+(.+?)\s+[—–-]\s+(High|Medium|Low)',
        re.IGNORECASE
    )

    for match in pattern.finditer(text):
        date_str = match.group(1)
        persona = match.group(2).strip()
        feedback = match.group(3).strip()
        priority = match.group(4).strip().capitalize()

        # Categorize
        category = "General"
        feedback_lower = feedback.lower()
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in feedback_lower for kw in keywords):
                category = cat
                break

        # Generate suggested action
        action = f"[{category}] Address: {feedback[:100]}"

        entries.append({
            "date": date_str,
            "persona": persona,
            "feedback": feedback,
            "priority": priority,
            "category": category,
            "action": action,
        })

    # Sort by priority (High first) then date (newest first)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    entries.sort(key=lambda e: (priority_order.get(e["priority"], 99), e["date"]), reverse=False)
    # Re-sort: high priority first
    entries.sort(key=lambda e: priority_order.get(e["priority"], 99))

    # Summary
    summary = {
        "total": len(entries),
        "by_priority": {"High": 0, "Medium": 0, "Low": 0},
        "by_persona": {},
        "by_category": {},
    }
    for e in entries:
        summary["by_priority"][e["priority"]] = summary["by_priority"].get(e["priority"], 0) + 1
        summary["by_persona"][e["persona"]] = summary["by_persona"].get(e["persona"], 0) + 1
        summary["by_category"][e["category"]] = summary["by_category"].get(e["category"], 0) + 1

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(FEEDBACK_PATH),
        "summary": summary,
        "backlog": entries,
    }

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False))

    return output


if __name__ == "__main__":
    result = parse_feedback()
    print(json.dumps({
        "ok": result.get("ok", True),
        "entries": len(result.get("backlog", [])),
        "summary": result.get("summary", {}),
    }, indent=2))
