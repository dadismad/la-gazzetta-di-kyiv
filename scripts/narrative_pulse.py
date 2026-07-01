#!/usr/bin/env python3
"""
narrative_pulse.py — Tier 2 Radar Alert engine.

Detects narrative velocity anomalies (≥2x rolling 7-day average),
generates a macro-focused Radar Alert via DeepSeek, and queues it
for telegram_broadcast.py priority routing.

Usage:
  python3 scripts/narrative_pulse.py
"""

import os
import json
import sqlite3
import requests
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "gazzetta.db"
QUEUE_PATH = PROJECT_ROOT / "mailbox" / "radar_queue.json"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

ANOMALY_QUERY = """
SELECT current.narrative_tag, current.vol, avg_table.rolling_avg, 
       (current.vol / NULLIF(avg_table.rolling_avg, 0)) as anomaly_score
FROM 
  (SELECT narrative_tag, COUNT(*) as vol FROM ingestion_hashes 
   WHERE created_at > datetime('now', '-6 hours') GROUP BY narrative_tag) current
JOIN 
  (SELECT narrative_tag, COUNT(*)/28.0 as rolling_avg FROM ingestion_hashes 
   WHERE created_at > datetime('now', '-7 days') GROUP BY narrative_tag) avg_table
ON current.narrative_tag = avg_table.narrative_tag
WHERE (current.vol / NULLIF(avg_table.rolling_avg, 0)) >= 2.0 AND current.vol > 5;
"""


def get_recent_headlines(narrative_tag, limit=15):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title FROM ingestion_hashes WHERE narrative_tag = ? "
            "AND created_at > datetime('now', '-12 hours') "
            "ORDER BY created_at DESC LIMIT ?",
            (narrative_tag, limit)
        )
        return [row[0] for row in cursor.fetchall()]


def generate_radar_alert(narrative_tag, anomaly_score, headlines):
    if not DEEPSEEK_API_KEY:
        print("[ERROR] DeepSeek API key missing.")
        return None

    headline_block = "\n".join([f"- {h}" for h in headlines])

    system_prompt = (
        "You are an elite macro narrative analyst. Your worldview is built on Raoul Pal's liquidity cycles "
        "and Jordi Visser's asymmetry framework. You do not just read the news; you track how capital prices in "
        "civilizational shifts.\n\n"
        "GUARDRAIL: Use the Pal/Visser frameworks as lenses for interpreting the data, not as predetermined conclusions. "
        "If the narrative velocity contradicts the structural bull thesis, highlight the divergence. "
        "The contradiction IS the signal.\n\n"
        "Our ingestion engine just detected a major structural narrative volume spike.\n"
        "Your task is to write a high-signal 'Radar Alert' summarizing the tectonic shift happening in the headlines.\n\n"
        "CRITICAL RULES:\n"
        "- Frame the surge through a structural lens: Is the market pricing in the denominator effect in real-time? "
        "Is this a leading indicator of supply chain fracturing, energy sovereignty shifts, or a leap in the Exponential Age?\n"
        "- Do NOT predict specific price movements or offer explicit entry/stop/target levels.\n"
        "- Do NOT name specific company tickers or single-name equities. That belongs to a different tier.\n"
        "- DO highlight which broad sectors, industries, or asset classes are showing the largest capital flow divergence.\n"
        "- Keep it punchy, slightly contrarian, and heavily focused on the asymmetry of the narrative shift. "
        "Make the reader feel like they are seeing the matrix of global liquidity.\n\n"
        "OUTPUT STRUCTURE: Follow the structured template in the user prompt exactly — "
        "open with the RADAR ALERT header, then the Velocity Surge metric, "
        "then the Denominator/Macro Shift analysis."
    )

    user_prompt = (
        f"Narrative: {narrative_tag.upper()}\n"
        f"Anomaly Multiplier: {anomaly_score:.2f}x baseline\n\n"
        f"Recent Ingested Headlines:\n{headline_block}\n\n"
        f"STRUCTURED OUTPUT FORMAT — follow exactly:\n\n"
        f"🚨 **RADAR ALERT | {narrative_tag.upper()}**\n"
        f"---\n"
        f"**Velocity Surge:** {anomaly_score:.2f}x above 7-day baseline.\n\n"
        f"**The Denominator/Macro Shift:**\n"
        f"[2-3 punchy sentences explaining what this velocity surge means through a liquidity "
        f"and structural asymmetry lens. Connect it to geopolitics, geoeconomics, or global "
        f"inflation cycles. Do NOT name specific tickers or predict price levels.]"
    )

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.4
            },
            timeout=45
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ERROR] DeepSeek API call failed for {narrative_tag}: {e}")
        return None


def append_to_queue(alert_data):
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

    queue = []
    if QUEUE_PATH.exists():
        try:
            with open(QUEUE_PATH, "r") as f:
                queue = json.load(f)
        except json.JSONDecodeError:
            queue = []

    queue.append(alert_data)

    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)


def main():
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(ANOMALY_QUERY)
        anomalies = cursor.fetchall()

    for row in anomalies:
        tag = row['narrative_tag']
        score = row['anomaly_score']
        print(f"[PULSE] Detected anomaly for {tag}: {score:.2f}x")

        headlines = get_recent_headlines(tag)
        if not headlines:
            continue

        alert_text = generate_radar_alert(tag, score, headlines)
        if alert_text:
            alert_payload = {
                "narrative_tag": tag,
                "anomaly_score": round(score, 2),
                "text": alert_text,
                "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            }
            append_to_queue(alert_payload)
            print(f"[PULSE] Successfully queued Radar Alert for {tag}")


if __name__ == "__main__":
    main()
