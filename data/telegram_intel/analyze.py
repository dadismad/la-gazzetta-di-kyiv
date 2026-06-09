#!/usr/bin/env python3
"""Analyze Telegram intel and produce the final actionable report + save to JSON."""
import json
import sys
from datetime import datetime, timezone

# Load raw data
with open("/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/raw_all.json") as f:
    data = json.load(f)

now = datetime.fromisoformat(data["timestamp"])
channels = data["channels"]

# Extract key data points for analysis
ethan = channels.get("ethanlevins", [])
monitor = channels.get("MonitoringSituation", [])
trad = channels.get("trad_fin", [])
supersh = channels.get("ASupersharij", [])
infinity = channels.get("infinityhedge", [])

# === Story 1: China-Taiwan Maritime Enforcement ===
china_taiwan_msgs = [m for m in monitor if "China" in m["text"] and "Taiwan" in m["text"]]
china_taiwan_story = china_taiwan_msgs[0] if china_taiwan_msgs else None

# === Story 2: US-Iran escalation ===
iran_msgs = [m for m in ethan if any(kw in m["text"] for kw in ["Iran", "Bandar Abbas", "Hamedan", "Shiraz", "Kuwait", "Bahrain"])]
iran_msgs_sorted = sorted(iran_msgs, key=lambda x: x.get("date", ""), reverse=True)

iran_leaks = [m for m in ethan if "Iran" in m["text"] and "negotiation" in m["text"].lower()]
iran_air = [m for m in ethan if "Bandar Abbas" in m["text"] or "Hamedan" in m["text"] or "Shiraz" in m["text"]]
kuwait_missiles = [m for m in ethan if "Kuwait" in m["text"]]
bahrain = [m for m in monitor if "Bahrain" in m["text"]]

# US struck Iranian radar sites from trad_fin
us_strike = [m for m in trad if "IRANIAN" in m["text"] and "RADAR" in m["text"]]

# === Story 3: Lebanon-Israel escalation ===
lebanon_msgs = [m for m in ethan if "Lebanon" in m["text"] or "Hezbollah" in m["text"] or "IDF" in m["text"] or "Israeli" in m["text"]]
lebanon_msgs_sorted = sorted(lebanon_msgs, key=lambda x: x.get("date", ""), reverse=True)

# === Story 4: Ukraine-Russia ===
ukraine_msgs = [m for m in ethan if "Ukraine" in m["text"] or "Russian" in m["text"] or "Kostantinivka" in m["text"]]
ukraine_drones = [m for m in supersh if "дрон" in m["text"].lower() or "БПЛА" in m["text"]]

# Build actionable stories
stories = []

# Story 1: China-Taiwan
if china_taiwan_story:
    stories.append({
        "title": "China Launches Maritime Enforcement Operation East of Taiwan — Blockade Prep Signal",
        "freshness": "27 minutes ago",
        "source": "@MonitoringSituation",
        "event": "China announced and initiated a special maritime traffic law enforcement operation in waters east of Taiwan on June 6, citing jurisdiction. Framed as response to Japan-Philippines 'maritime boundary delimitation negotiations' east of Taiwan.",
        "narrative": "Consensus reads this as a slow-roll blockade preparation. China is establishing administrative control over waters east of Taiwan incrementally — starting with 'traffic enforcement' as legal basis for interdiction and boarding.",
        "contradiction": "Operation is framed as 'traffic safety / maritime jurisdiction' routine. But timing — same day as Japan-Philippines talks — and language ('necessary action', 'safeguard rights') suggest it's escalatory. Markets may dismiss as posturing until a vessel is actually boarded.",
        "bet": {
            "direction": "SHORT Taiwan equities, LONG VIX, LONG gold",
            "assets": ["$TSM", "$SMH", "$GLD", "$VIX", "EWT (Taiwan ETF)", "USD/JPY (safe haven JPY)"],
            "trigger": "Any report of vessel inspection/boarding by Chinese MSA in the operation zone triggers 3-5% TSM gap down at Monday open",
            "horizon": "Next 48 hours / Monday Asia open",
            "confidence": "HIGH — China has publicly announced the time/place/legal basis, which is unusually transparent for them"
        },
        "benefit": {
            "Gazzetta di Kyiv": "Frame as 'China's Taiwan blockade rehearsal — what Europe must learn from Ukraine' linking Taiwan security to global semiconductor supply chain risk",
            "Bet&Benefit": "Position short semiconductor futures / TSM pre-market Sunday night. If China boards any vessel, gap down is guaranteed. Even without boarding, elevated risk premium persists until Monday"
        }
    })

# Story 2: US-Iran Negotiations Collapsing + Military Activity Surge
if iran_leaks or iran_air or kuwait_missiles or bahrain:
    # Find the most recent negotiation leak
    recent_iran_leak = iran_leaks[0] if iran_leaks else None
    iran_air_text = "\n".join([m["text"][:120] for m in iran_air[:3]])

    stories.append({
        "title": "US-Iran Talks on Brink of Failure — Military Activity Surges Across Persian Gulf",
        "freshness": "56-116 minutes ago (multiple data points)",
        "source": "@ethanlevins, @MonitoringSituation",
        "event": f"Leaked US-Iran negotiation sticking points published: 'Continued US interception of Iranian ships causing severe...' | Iranian fighter jets over Bandar Abbas, Shiraz, Hamedan | Kuwait Army intercepted 7 ballistic missiles from Iran ({[m.get('date','')[:16] for m in kuwait_missiles]}) | Bahrain intercepted 3 missiles and drones from Iran | US had previously struck Iranian radar sites in Goruk and Qeshm Island",
        "narrative": "Pattern suggests coordinated Iranian military posture shift: air activity across multiple cities + missile launches toward Kuwait/Bahrain + negotiation leaks simultaneously. Indicates Iran is preparing for either a strike or demonstrating capability ahead of talks collapse.",
        "contradiction": "No official declaration of talks failure yet. Pakistan Interior Minister traveling to Tehran (reported 166 min ago) suggests diplomatic channels still active. Iranian activity could be coercive negotiation tactic rather than prelude to strikes.",
        "bet": {
            "direction": "LONG oil, LONG defense, SHORT risk-on",
            "assets": ["$USO", "$CL (WTI Crude)", "$XLE", "$LMT", "$GD", "$SPY puts"],
            "trigger": "US-Iran talks officially break = $5+ spike in WTI within hours. Additional Iranian missile fire toward Gulf states accelerates move",
            "horizon": "Next 2-6 hours / overnight",
            "confidence": "MEDIUM-HIGH — multiple corroborating data points from independent channels; pattern of military + diplomatic signals coherent"
        },
        "benefit": {
            "Gazzetta di Kyiv": "Connect Iran escalation to Ukraine war — 'Putin watches as US is stretched toward two-front conflict; Iran tests American resolve while Russia grinds in Donbas'",
            "Bet&Benefit": "Crude oil longs overnight. If Strait of Hormuz disruption narrative intensifies (US struck radar sites already), WTI above $85 is plausible. Defense stocks have room to run on multi-front conflict narrative"
        }
    })

# Story 3: Lebanon-Israel Ground War Escalation
if lebanon_msgs_sorted:
    most_recent_lebanon = lebanon_msgs_sorted[0]
    lebanon_texts = "\n".join([m["text"][:200] for m in lebanon_msgs_sorted[:5]])

    stories.append({
        "title": "Israel-Lebanon Conflict Deepening — Full Occupation of Southern Lebanon Now Openly Discussed",
        "freshness": "56-245 minutes ago (active)",
        "source": "@ethanlevins",
        "event": f"IDF officer from Egoz Reconnaissance Unit died of wounds sustained in southern Lebanon clashes (66 min ago) | Several Israeli soldiers injured in battles in southern Lebanon (56 min ago) | Israeli military leader stated: 'It is impossible to disarm Hezbollah of its weapons without a full occupation of Lebanon' (161 min ago) | Israeli airstrikes continue across southern Lebanon | Halt of demolishing villages in southern Lebanon was included in ceasefire understanding (183 min ago)",
        "narrative": "Escalation is accelerating. IDF taking casualties daily. Leadership now publicly discussing full occupation. 2,500 Hezbollah fighters operating south of Litani despite ceasefire terms. This is no longer 'border clashes' — it's a ground war with no exit strategy visible.",
        "contradiction": "Ceasefire understanding included halt of demolitions — suggests there IS an active diplomatic framework. Halt of demolitions is a concession, implying both sides are still bargaining rather than committed to all-out war.",
        "bet": {
            "direction": "LONG oil (broader Middle East risk), LONG defense (Israel-specific: $ISRA ETF), LONG gold",
            "assets": ["$USO", "$CL", "$GLD", "$ISRA", "$LMT"],
            "trigger": "Full occupation announcement or major Israeli ground operation into southern Lebanon triggers risk-off spike across all Middle East exposed assets",
            "horizon": "Next 12-24 hours / week ahead",
            "confidence": "MEDIUM — casualties are real but occupation language may be negotiating posture; however trend is clearly escalatory"
        },
        "benefit": {
            "Gazzetta di Kyiv": "Frame as 'Middle East 2026: Three Wars, No Off-Ramp' — tie Iran, Lebanon, Ukraine into single narrative of global conflict expansion under a distracted US administration",
            "Bet&Benefits": "Broad Middle East conflict hedge (gold + oil) for weekend carry. Market underestimates spillover risk to broader region"
        }
    })

# Final output structure
final = {
    "timestamp": now.isoformat(),
    "query_window": "All available (most recent messages, prioritizing last 2 hours)",
    "total_stories_identified": len(stories),
    "scan_channels": ["@trad_fin", "@MonitoringSituation", "@ASupersharij", "@infinityhedge", "@ethanlevins", "@marketwits"],
    "channels_active_status": {
        "@trad_fin": "OLD — most recent post 21h ago (Strait of Hormuz strikes). Channel slow/dormant on weekends.",
        "@MonitoringSituation": "ACTIVE — China-Taiwan post 27 min ago is fresh and highly consequential.",
        "@ASupersharij": "ACTIVE — Russian-language, Ukraine war focus. Last post ~0 min ago but mostly social commentary, not market-moving.",
        "@infinityhedge": "STALE — most recent post 3.4 days old. No weekend coverage.",
        "@ethanlevins": "HOT — continuous posting including 56 min ago. Best real-time source for Middle East escalation today.",
        "@marketwits": "DEAD — last posts from 2024. Channel abandoned."
    },
    "stories": stories,
    "meta_observation": "Saturday evening (20:08 UTC). Equity markets closed. Crypto and futures are the only liquid venues. Primary actionable themes: (1) China-Taiwan maritime operation — biggest potential Monday gap risk, (2) US-Iran talks collapse + military posturing — oil will react overnight, (3) Lebanon-Israel ground war deepening — slow burn escalation but accumulating. Missing element: no fresh macro data (jobs report digested Friday). Watch for Iran Strait of Hormuz developments — the US already struck Iranian radar there (trad_fin, 21h ago) so retaliation is overdue."
}

# Write final output
with open("/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/latest.json", "w") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print(json.dumps(final, ensure_ascii=False, indent=2))
