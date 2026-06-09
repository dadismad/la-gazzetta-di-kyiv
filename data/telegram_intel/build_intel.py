#!/usr/bin/env python3
"""
Build actionable Telegram intel report for Gazzetta di Kyiv / Bet&Benefit.
Reads raw_all.json (from fetch_all.py), filters to last ~30min, analyzes.
"""
import json
import sys
from datetime import datetime, timezone, timedelta

with open("/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/raw_all.json") as f:
    data = json.load(f)

channels = data["channels"]
scan_time = datetime.fromisoformat(data["timestamp"])
now = scan_time

def parse_date(d):
    try:
        return datetime.fromisoformat(d)
    except:
        return None

# Count total messages and recent ones
total_msgs = sum(len(v) for v in channels.values())
cutoff_30m = now.timestamp() - 30 * 60
cutoff_2h = now.timestamp() - 120 * 60

recent_30m = {}
recent_2h = {}
for ch, msgs in channels.items():
    r30 = []
    r120 = []
    for m in msgs:
        dt = parse_date(m.get("date", ""))
        ts = dt.timestamp() if dt else 0
        if ts >= cutoff_30m:
            r30.append(m)
        if ts >= cutoff_2h:
            r120.append(m)
    recent_30m[ch] = r30
    recent_2h[ch] = r120

print(f"=== SCAN TIME: {now.isoformat()} UTC ===", file=sys.stderr)
print(f"Total messages across all channels: {total_msgs}", file=sys.stderr)
print(f"Messages in last 30min: {sum(len(v) for v in recent_30m.values())}", file=sys.stderr)
print(f"Messages in last 2h: {sum(len(v) for v in recent_2h.values())}", file=sys.stderr)
for ch in channels:
    print(f"  @{ch}: {len(recent_30m[ch])} in 30min / {len(recent_2h[ch])} in 2h / {len(channels[ch])} total", file=sys.stderr)

stories = []

# ─── STORY 1: China-Taiwan Maritime Operation (FRESHEST - last 30-60min) ───
china_msgs = [m for m in channels.get("MonitoringSituation", []) if "China" in m["text"] and "Taiwan" in m["text"]]
china_msgs += [m for m in channels.get("markettwits", []) if "тайвань" in m["text"].lower() or "Taiwan" in m["text"]]
if china_msgs:
    china_latest = max(china_msgs, key=lambda m: parse_date(m.get("date","")) or datetime.min)
    china_dt = parse_date(china_latest["date"])
    china_age_min = int((now - china_dt).total_seconds() / 60) if china_dt else "?"
    stories.append({
        "id": f"china-taiwan-maritime-{now.strftime('%Y%m%d')}",
        "title": f"China Launches Maritime Enforcement Operation East of Taiwan — Fresh {china_age_min}min ago",
        "freshness": f"{china_age_min} minutes ago" if isinstance(china_age_min, int) else "unknown",
        "source_channels": ["@MonitoringSituation", "@markettwits"],
        "event": "China announced a special maritime traffic law enforcement operation east of Taiwan on June 6. Framed as 'exercising jurisdiction' in response to Japan-Philippines maritime boundary talks. This is the first time China has publicly announced a specific time/place/legal basis for an enforcement operation in waters east of Taiwan.",
        "consensus_narrative": "Consensus reads this as incremental blockade preparation — China establishing administrative control over waters east of Taiwan via 'traffic enforcement' as legal basis for interdiction and boarding. Markets pricing zero probability of actual confrontation but the operational transparency is unusual.",
        "contradiction": "Operation is framed as routine 'maritime traffic safety / law enforcement.' But timing — same day as Japan-Philippines talks — and language ('necessary action', 'safeguard rights') suggest escalatory intent. Markets may dismiss as posturing until a vessel is actually boarded. No physical confrontation yet.",
        "bet": {
            "direction": "SHORT Taiwan equities/semis, LONG gold/VIX",
            "assets": ["$TSM", "$SMH", "$GLD", "$VIX", "EWT (Taiwan ETF)"],
            "trigger": "Any report of Chinese MSA boarding/intercepting a vessel in the operation zone = 3-5% TSM gap down at Monday Asia open. No boarding = elevated risk premium but no immediate trade.",
            "horizon": "Next 24-48 hours / Monday Asia open",
            "confidence": "HIGH — China has publicly announced time/place/legal basis, unusually transparent. Japan-Philippines talks give them a pretext."
        },
        "benefit": {
            "Gazzetta di Kyiv": "Frame: 'China's Taiwan blockade rehearsal — what Europe must learn from Ukraine.' Taiwan security = global semiconductor supply chain risk. Connect to Ukraine: 'Putin watches as US is stretched across three theaters.'",
            "Bet&Benefit": "Position short semiconductor futures pre-market Sunday night. If China boards any vessel before Monday open, gap down guaranteed. TSM options with Monday expiry — buy puts. Without boarding, the elevated risk premium alone is a short-term fade."
        },
        "materiality_score": 8.5
    })

# ─── STORY 2: Iran Multi-Front Military Posture (ACTIVE TODAY) ───
# Iran fighter jets + missile intercepts + negotiations collapse
iran_air_msgs = [m for m in channels.get("ethanlevins", []) if any(k in m["text"] for k in ["Bandar Abbas", "Shiraz", "Hamedan", "fighter jet", "missile over"]) and "Iran" in m["text"]]
iran_condemn = [m for m in channels.get("ethanlevins", []) if "Iran" in m["text"] and "condemns" in m["text"].lower()]
iran_leak = [m for m in channels.get("ethanlevins", []) if "Leaked" in m["text"] and "Iran" in m["text"]]
kuwait_msgs = [m for m in channels.get("ethanlevins", []) if "Kuwait" in m["text"] and "ballistic" in m["text"]]
bahrain_msg = [m for m in channels.get("MonitoringSituation", []) if "Bahrain" in m["text"] and "missiles" in m["text"]]
pakistan_msgs = [m for m in channels.get("ethanlevins", []) if "Pakistan" in m["text"] and "Tehran" in m["text"]]

if iran_air_msgs or iran_condemn or kuwait_msgs or bahrain_msg:
    # Find fresh iran condemnation (20:28 UTC - newest)
    condemn_latest = max(iran_condemn, key=lambda m: parse_date(m.get("date","")) or datetime.min) if iran_condemn else None
    air_latest = max(iran_air_msgs, key=lambda m: parse_date(m.get("date","")) or datetime.min) if iran_air_msgs else None
    
    stories.append({
        "id": f"iran-multi-front-escalation-{now.strftime('%Y%m%d')}",
        "title": "Iran Military Posture Surge — Fighter Jets, Missiles into Kuwait/Bahrain, Negotiations Leaked as Collapsing",
        "freshness": "Active within last 2-4 hours",
        "source_channels": ["@ethanlevins", "@MonitoringSituation", "@trad_fin"],
        "event": "Iranian fighter jets spotted over Bandar Abbas + Shiraz + Hamedan. Kuwait Army intercepted 7 ballistic missiles. Bahrain intercepted 3 missiles + drones from Iran. Iran strongly condemned Israeli attacks on Lebanese Army. Leaked US-Iran negotiation sticking points: US interceptions of Iranian ships causing drone/missile exchanges. Pakistan Interior Minister traveled to Tehran. US struck Iranian radar sites at Goruk and Qeshm Island yesterday (trad_fin). Khamenei aide confirmed no meeting with Trump. Bandar Abbas explosions reported.",
        "consensus_narrative": "Iran is in active military posture shift — air activity across multiple cities, missile launches toward Gulf states, all while negotiations with US are on brink of failure. The pattern is coherent: Iran is preparing for escalation or demonstrating capability as bargaining leverage. Oil risk premium is underpriced given Hormuz blockade + active strikes.",
        "contradiction": "Pakistan Interior Minister traveling to Tehran suggests diplomatic channels still open. Iran's condemnation of Israeli attacks on Lebanon is diplomatic language — may signal they want to keep the conflict framed as Israel-Lebanon, not US-Iran. House voted 215-208 to end Trump's Iran war — domestic US political pressure may constrain further escalation. Axios: Trump wants to end the war but Netanyahu wants to resume it — the actual escalation vector may shift to Israel-Lebanon.",
        "bet": {
            "direction": "LONG oil, LONG gold, LONG defense",
            "assets": ["$USO", "$CL (WTI Crude)", "$XLE", "$LMT", "$GD", "$GLD", "$SPY puts"],
            "trigger": "Additional Iranian missile fire toward Gulf states or Hormuz tanker incident = $3-5 WTI spike within hours. US-Iran talks officially declared broken accelerates move. CME opens Sunday evening — oil futures will gap.",
            "horizon": "Next 2-12 hours / Sunday CME open through Monday",
            "confidence": "MEDIUM-HIGH — multiple corroborating channels, coherent pattern across military + diplomatic signals"
        },
        "benefit": {
            "Gazzetta di Kyiv": "Frame: 'Putin watches as US is stretched toward two-front conflict; Iran tests American resolve while Russia grinds in Donbas.' Connect Iran escalation to Ukraine: 'The US can't arm Israel, Ukraine, and Taiwan simultaneously — something breaks.'",
            "Bet&Benefit": "Crude oil longs for Sunday CME open. If Hormuz disruption narrative intensifies (radar already struck), WTI above $85 is plausible. Defense stocks (LMT, GD) have multi-front conflict tailwind. If House vote gains Senate traction, USD weakens = commodities bid."
        },
        "materiality_score": 9.0
    })

# ─── STORY 3: Ukraine Drone Strike on St. Petersburg During PMEF ───
ukraine_drone_msgs = [m for m in channels.get("ASupersharij", []) if any(k in m["text"] for k in ["дрон", "БПЛА", "250", "Питер", "Санкт-Петербург", "ПМЭФ", "Петергоф"])]
if ukraine_drone_msgs:
    # Most relevant ones
    st_pete_msgs = [m for m in ukraine_drone_msgs if any(k in m["text"] for k in ["Санкт-Петербург", "Питер", "Петергоф", "ПМЭФ", "250"])]
    latest_drone = max(ukraine_drone_msgs, key=lambda m: parse_date(m.get("date","")) or datetime.min)
    
    stories.append({
        "id": f"ukraine-st-petersburg-drone-pmef-{now.strftime('%Y%m%d')}",
        "title": "Ukraine Hits St. Petersburg with 250+ Drones During PMEF — Military Base + Physics Institute Destroyed",
        "freshness": "Today (posts from 07:25-20:17 UTC)",
        "source_channels": ["@ASupersharij", "@ethanlevins"],
        "event": "Ukraine launched ~250 drones attacking Russia. St. Petersburg and Leningrad Oblast hit during PMEF (St. Petersburg International Economic Forum). Target hits: Military unit 81263 (7082nd naval mine-torpedo base, 1st category), Fock Physics Research Institute in Petrodvorets, Kronstadt cadet corps area. Sochi simultaneously under drone attack. Port of Mariupol also struck. Russian budget deficit at 6.01T rubles (2.6% of GDP), oil/gas revenues down 29.8%.",
        "consensus_narrative": "Ukraine demonstrated deep-strike capability against Russia's second city during Russia's flagship economic forum — massive political humiliation. Shows St. Petersburg air defense is porous. Russia's budget bleeding accelerates (29.8% oil/gas revenue drop). War increasingly expensive for Moscow.",
        "contradiction": "Putin rejected peace talks with Zelensky same day, telling army to 'work.' Strike may strengthen Putin's hardline position domestically — 'see what they do to us.' Ushakov says US prioritizing Iran over Ukraine — Ukraine acting more aggressively precisely because US attention diverted to Iran, trying to force battlefield realities before US focus shifts away from Ukraine permanently.",
        "bet": {
            "direction": "LONG defense/nuclear security (Zaporizhzhia incident), LONG Ukrainian war bonds if risk-on, SHORT Russian assets",
            "assets": ["$LMT", "$GD", "$RSX (Russia ETF shorts)", "Ukrainian sovereign bonds (if tradeable)", "$URA (uranium/nuclear)"],
            "trigger": "Russia retaliates against Ukrainian energy grid forcefully = energy spike. IAEA Zaporizhzhia incident escalates = nuclear security plays bid. Budget data shows Russia's financial runway shortening = RSX shorts accumulate.",
            "horizon": "This week (Monday-Friday)",
            "confidence": "HIGH for narrative value (Gazzetta content), MEDIUM for direct market impact"
        },
        "benefit": {
            "Gazzetta di Kyiv": "PRIMARY FRAME: Ukraine just bombed St. Petersburg during Putins Davos - this destroys Russias normal life continues propaganda. Secondary: The Ukrainian drone industry - 250+ drones, started by kitchen enthusiasts - is a compelling tech/industrial underdog narrative. Budget deficit data shows Russias war is financially unsustainable.",
            "Bet&Benefit": "Narrative is the main product here — this is Gazzetta di Kyiv front-page material. For Bet&Benefit: if IAEA Zaporizhzhia incident escalates into a radiological event, uranium/nuclear safety plays get bid. Russian budget data is a slow-burn short thesis on RSX."
        },
        "materiality_score": 7.5
    })

# ─── STORY 4: Israel-Lebanon Ground War ───
lebanon_msgs = [m for m in channels.get("ethanlevins", []) if any(k in m["text"] for k in ["Lebanon", "Lebanese", "Hezbollah", "IDF", "Israeli"]) and any(k in m["text"] for k in ["southern", "occupation", "soldier", "killed", "died", "wound", "attack"])]
if lebanon_msgs:
    latest_lebanon = max(lebanon_msgs, key=lambda m: parse_date(m.get("date","")) or datetime.min)
    lebanon_dt = parse_date(latest_lebanon.get("date",""))
    lebanon_age = int((now - lebanon_dt).total_seconds() / 60) if lebanon_dt else "?"
    
    stories.append({
        "id": f"israel-lebanon-ground-war-{now.strftime('%Y%m%d')}",
        "title": f"Israel-Lebanon Conflict Deepening — Full Occupation Publicly Discussed, IDF Taking Daily Casualties",
        "freshness": f"Latest {lebanon_age}min ago, active all day",
        "source_channels": ["@ethanlevins"],
        "event": "IDF officer from Egoz Recon Unit died of wounds from southern Lebanon clashes. Several Israeli soldiers injured in battles in southern Lebanon. Israeli military leader: 'Impossible to disarm Hezbollah without full occupation of Lebanon.' Israel attacked Lebanese Army vehicle, killing soldiers including officer. 2,500 Hezbollah fighters operating south of Litani. Israeli airstrikes continue across southern Lebanon. Iran condemns Israeli attacks on Lebanese Army.",
        "consensus_narrative": "Escalation is accelerating — IDF taking casualties daily, leadership publicly discussing full occupation. 2,500 Hezbollah fighters south of Litani despite ceasefire terms. This is no longer 'border clashes' — it's an entrenched ground war with no exit strategy. Axios: Netanyahu wants to resume Iran war, but Israel is already heavily committed in Lebanon — suggests two-front Israeli strategy.",
        "contradiction": "Ceasefire understanding included halt of demolitions in southern Lebanon — diplomatic framework still active. Halt of demolitions is a concession, implying both sides still bargaining. Israel killed Lebanese Army soldiers but Lebanese Army has zero ties to Hezbollah — could backfire diplomatically. Full occupation language may be negotiating posture, not actual strategy.",
        "bet": {
            "direction": "LONG oil (broader ME risk), LONG gold, LONG defense (Israel-specific $ISRA ETF if accessible)",
            "assets": ["$USO", "$CL", "$GLD", "$LMT", "$ISRA"],
            "trigger": "Full occupation announcement or major Israeli ground operation into southern Lebanon = risk-off spike across all Middle East exposed assets. Iran entering the conflict explicitly = oil spike above $85.",
            "horizon": "Next 12-48 hours / week",
            "confidence": "MEDIUM — casualties are real but occupation language may be negotiating posture; however trend is clearly escalatory and accumulating"
        },
        "benefit": {
            "Gazzetta di Kyiv": "Frame: 'Middle East 2026: Three Wars, No Off-Ramp.' Tie Iran, Lebanon, Ukraine into single narrative of global conflict expansion under distracted US administration. 'The US can't fight three wars — which one gets deprioritized?'",
            "Bet&Benefit": "Broad Middle East conflict hedge (gold + oil) for weekend carry. Market underestimates spillover risk. If Iran-US talks officially break AND Israel announces full Lebanon occupation simultaneously, that's a multi-standard-deviation oil move."
        },
        "materiality_score": 7.0
    })

# ─── Channel status ───
channel_status = {}
for ch, msgs in channels.items():
    if msgs:
        latest = max(msgs, key=lambda m: parse_date(m.get("date","")) or datetime.min)
        dt = parse_date(latest.get("date",""))
        age_m = int((now - dt).total_seconds() / 60) if dt else 999
        if age_m <= 30:
            status = "HOT — within last 30min"
        elif age_m <= 120:
            status = "ACTIVE — within last 2h"
        elif age_m <= 1440:
            status = f"STALE — last post {age_m} min ago"
        else:
            days = age_m // 1440
            status = f"DEAD — last post {days}d ago"
        channel_status[f"@{ch}"] = f"{status} (latest: {latest.get('date','?')[:16]})"
    else:
        channel_status[f"@{ch}"] = "NO DATA"

# ─── Final output ───
final = {
    "scrape_time": now.isoformat(),
    "model": "deepseek-v4-flash",
    "horizon": "1-2 hours",
    "channels_monitored": [f"@{ch}" for ch in channels],
    "channel_status": channel_status,
    "summary_stats": {
        "total_messages_scanned": total_msgs,
        "messages_last_30min": sum(len(v) for v in recent_30m.values()),
        "messages_last_2h": sum(len(v) for v in recent_2h.values()),
        "actionable_stories_identified": len(stories)
    },
    "stories": sorted(stories, key=lambda s: s["materiality_score"], reverse=True),
    "meta_observation": f"Sunday June 7, {now.strftime('%H:%M')} UTC. Equity markets closed. Crypto (BTC 24/7) and CME futures (open Sunday evening) are the only liquid venues. Primary actionable themes: (1) China-Taiwan maritime operation — biggest potential Monday gap risk for semis/TSM. (2) Iran multi-front military posture — oil will react at CME Sunday open. (3) Ukraine St. Petersburg drone strike during PMEF — Gazzetta content gold, Russia budget bleeding. (4) Israel-Lebanon ground war — slow-burn accumulation, but daily IDF casualties + full occupation discussion is a ticking clock. BTC approaching 200-week MA ($57-58K) with Strategy selling — crypto narrative bearish but approaching technical levels where bottoms historically form."
}

with open("/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/latest.json", "w") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

# Print summary for delivery
print(json.dumps(final, ensure_ascii=False, indent=2))
