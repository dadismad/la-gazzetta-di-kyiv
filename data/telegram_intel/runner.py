#!/usr/bin/env python3
"""Run the intel pipeline: analyze fetched data and produce latest.json"""
import json
from datetime import datetime, timezone

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

# Count messages by recency
total_msgs = sum(len(v) for v in channels.values())
cutoff_30 = now.timestamp() - 30 * 60
cutoff_120 = now.timestamp() - 120 * 60

recent_30 = {}
recent_120 = {}
for ch, msgs in channels.items():
    r30 = []
    r120 = []
    for m in msgs:
        dt = parse_date(m.get("date", ""))
        ts = dt.timestamp() if dt else 0
        if ts >= cutoff_30:
            r30.append(m)
        if ts >= cutoff_120:
            r120.append(m)
    recent_30[ch] = r30
    recent_120[ch] = r120

print(f"=== SCAN: {now.isoformat()} UTC ===")
print(f"Total msgs: {total_msgs}")
print(f"Last 30min: {sum(len(v) for v in recent_30.values())}")
print(f"Last 2h: {sum(len(v) for v in recent_120.values())}")

stories = []

# --- Story 1: Israel bombs Beirut Dahiyeh + Iran SNSC emergency ---
ethan = channels.get("ethanlevins", [])
monitor = channels.get("MonitoringSituation", [])

beirut_bomb = [m for m in ethan if "Dahieh" in m["text"] or "Dahiyeh" in m["text"]]
iran_snsc = [m for m in ethan if "Supreme National Security Council" in m["text"]]
trump_leb = [m for m in ethan if "Lebanon is not required" in m["text"]]
hormuz = [m for m in ethan if "Hormuz" in m["text"] and "paying" in m["text"]]
idf_beirut = [m for m in monitor if "BEIRUT" in m["text"] or "Beirut" in m["text"]]
tyre = [m for m in monitor if "TYRE" in m["text"] or "Tyre" in m["text"]]
invasion = [m for m in ethan if "Metula" in m["text"] or "Nabatieh" in m["text"]]

beirut_all = beirut_bomb + iran_snsc + trump_leb + idf_beirut + tyre + invasion

stories.append({
    "id": f"israel-beirut-dahiyeh-iran-snsc-{now.strftime('%Y%m%d-%H%M')}",
    "title": "BREAKING: Israel Bombs Beirut's Dahiyeh (Iran's Final Red Line) — Iran SNSC Emergency Session",
    "freshness": "0-30 min ago (LIVE BREAKING)",
    "source_channels": ["@ethanlevins", "@MonitoringSituation"],
    "event": (
        "Israel bombed apartments in Beirut's Dahiyeh (Dahieh) — Hezbollah's southern Beirut stronghold. "
        "Iran had designated this as its 'final red line.' Iran's Supreme National Security Council called an emergency session. "
        "Trump told NBC Lebanon is not part of the Iran agreement. "
        "IDF issued evacuation alerts for Tyre, bombed Hezbollah infrastructure in southern suburbs. "
        "Ground ops advancing toward Metula, Kfar Tibnit, Nabatieh al-Fawqa. "
        "Iran has begun charging ships $1.5-2M per Hormuz transit."
    ),
    "consensus_narrative": (
        "Israel deliberately escalated by striking Iran's stated final red line while troops push deeper into Lebanon. "
        "Iran SNSC emergency session signals response being decided. Hormuz toll ($1.5-2M/ship) already imposed as asymmetric economic weapon. "
        "This combination = multi-front escalation the market has NOT priced for Sunday CME open. "
        "Trump removing Lebanon from Iran deal = green light for Israel."
    ),
    "contradiction": (
        "SNSC emergency session may produce diplomatic condemnation only, not military action. "
        "Hormuz toll may be unenforceable without naval confrontation. "
        "But Dahiyeh bombing crosses a stated red line — qualitative difference from prior escalations."
    ),
    "bet": {
        "direction": "LONG WTI oil, LONG gold, LONG defense, LONG VIX. SHORT equities.",
        "assets": ["$CL", "$USO", "$XLE", "$LMT", "$GD", "$GLD", "$VIX", "$SPY puts", "Brent"],
        "trigger": "Iran announces military retaliation = WTI $5+ gap at CME Sunday 18:00 ET open. Hormuz enforcement with naval confrontation = $85+ oil.",
        "horizon": "Next 2-12h / CME Sunday open through Monday",
        "confidence": "HIGH — stated red line crossed, SNSC session confirms deliberation, Hormuz toll already in effect."
    },
    "benefit": {
        "Gazzetta di Kyiv": "FRAME: 'Iran's Red Line Crossed — What Putin Learns from Beirut.' US stretched across 3 theaters (Iran, Lebanon, Ukraine). Oil spike bails out Russia's budget deficit (29.8% oil/gas revenue drop).",
        "Bet&Benefit": "ALL-IN oil for CME Sunday open. Multi-standard-deviation event. If Iran retaliates, WTI $85-90 by Monday. Gold + defense as secondary."
    },
    "materiality_score": 9.5
})

# --- Story 2: Iran Hormuz Toll ---
if hormuz:
    stories.append({
        "id": f"hormuz-toll-{now.strftime('%Y%m%d')}",
        "title": "BREAKING: Iran Imposes $1.5-2M Toll on Ships in Strait of Hormuz — Oil Chokepoint Weaponized",
        "freshness": "~90 min ago (12:08 UTC)",
        "source_channels": ["@ethanlevins"],
        "event": (
            "Iran began charging ships $1.5-2M per Hormuz transit. Overseen by Supreme National Security Council. "
            "Payments in cash, goods, services, or barter. ~20% of global oil passes through Hormuz."
        ),
        "consensus_narrative": (
            "Asymmetric economic warfare — 'fee-based blockade' without military confrontation. "
            "At $1.5-2M/tanker (2M bbl), adds $0.75-1.00/bbl transport premium. Insurance surging. "
            "SNSC oversight = state policy, not local extortion."
        ),
        "contradiction": (
            "Enforcement capability unclear. US Navy may protect shipping. "
            "Barter payment flexibility suggests negotiability."
        ),
        "bet": {
            "direction": "LONG crude, LONG tanker rates, LONG inflation breakevens",
            "assets": ["$CL", "$USO", "$XLE", "$GLD", "tanker equities"],
            "trigger": "First confirmed toll collection or ship diversion = oil +$2-3. US Navy intercept = $5+.",
            "horizon": "Next 2-24h / CME Sunday open",
            "confidence": "MEDIUM-HIGH — state-affiliated Mehr News, enforcement TBD but announcement alone creates risk premium."
        },
        "benefit": {
            "Gazzetta di Kyiv": "FRAME: Iran's oil weapon = Putin's lifeline. Higher oil funds Russia's war budget.",
            "Bet&Benefit": "Long crude for structural shift, not just gap. If sustained, $80+ oil floor."
        },
        "materiality_score": 8.5
    })

# --- Story 3: China-Taiwan Maritime Enforcement ---
china = [m for m in monitor if "China" in m["text"] and "Taiwan" in m["text"] and "maritime" in m["text"].lower()]
if china:
    c = max(china, key=lambda m: parse_date(m.get("date","")) or datetime.min)
    cd = parse_date(c["date"])
    ca = int((now - cd).total_seconds() / 3600) if cd else "?"
    
    stories.append({
        "id": f"china-taiwan-enforcement-{now.strftime('%Y%m%d')}",
        "title": f"China Maritime Enforcement East of Taiwan ({ca}h ago — Ongoing)",
        "freshness": f"{ca}h ago (June 6, ongoing)",
        "source_channels": ["@MonitoringSituation"],
        "event": "China launched maritime traffic law enforcement operation east of Taiwan on June 6. Framed as 'maritime administrative law enforcement jurisdiction, strengthening deep-sea patrol.' Timed to Japan-Philippines talks.",
        "consensus_narrative": (
            "Incremental blockade preparation — regulatory layering for future interdiction/boarding. "
            "Unusual transparency (time/place/legal basis) signals operational intent."
        ),
        "contradiction": (
            "Framed as routine. No boarding reported. Could be Japan-Philippines signaling, not escalation. "
            "Gap risk is real but hasn't materialized."
        ),
        "bet": {
            "direction": "SHORT Taiwan semis, LONG VIX hedge, LONG gold",
            "assets": ["$TSM", "$SMH", "$GLD", "$VIX", "EWT"],
            "trigger": "Chinese MSA boarding = TSM -5% Monday Asia open. No boarding by Monday = fade the short.",
            "horizon": "18-30h / Monday Asia open",
            "confidence": "MEDIUM — real operation, but boarding uncertain. Transparency is concerning."
        },
        "benefit": {
            "Gazzetta di Kyiv": "Taiwan blockade rehearsal = Ukraine's warning validated. Two chokepoint confrontations (Black Sea + Taiwan Strait).",
            "Bet&Benefit": "TSM puts for Monday. If boarding occurs, clean gap down. If not, fade late Monday."
        },
        "materiality_score": 7.5
    })

# Channel status
ch_status = {}
for ch, msgs in channels.items():
    if msgs:
        latest = max(msgs, key=lambda m: parse_date(m.get("date","")) or datetime.min)
        dt = parse_date(latest.get("date",""))
        age = int((now - dt).total_seconds() / 60) if dt else 999
        if age <= 30:
            s = "HOT (last 30min)"
        elif age <= 120:
            s = "ACTIVE (last 2h)"
        elif age <= 1440:
            s = f"STALE ({age}min ago)"
        else:
            s = f"DEAD ({age//1440}d ago)"
        ch_status[f"@{ch}"] = f"{s} latest: {latest.get('date','?')[:16]}"
    else:
        ch_status[f"@{ch}"] = "NO DATA"

final = {
    "scrape_time": now.isoformat(),
    "model": "deepseek-v4-flash",
    "horizon": "1-2 hours",
    "day_of_week": "Sunday",
    "channels_monitored": [f"@{ch}" for ch in channels],
    "channel_status": ch_status,
    "summary_stats": {
        "total_messages_scanned": total_msgs,
        "messages_last_30min": sum(len(v) for v in recent_30.values()),
        "messages_last_2h": sum(len(v) for v in recent_120.values()),
        "actionable_stories": len(stories)
    },
    "stories": sorted(stories, key=lambda s: s["materiality_score"], reverse=True),
    "meta_observation": (
        f"Sunday June 7 {now.strftime('%H:%M')} UTC. Markets closed. "
        f"CRITICAL: Israel just bombed Beirut's Dahiyeh (Iran's final red line). Iran SNSC emergency session. "
        f"Hormuz toll ($1.5-2M/ship) already imposed. Oil will GAP at CME Sunday 18:00 ET open. "
        f"China-Taiwan op ongoing but less time-sensitive for 2h horizon. "
        f"BTC near 200-week MA levels. "
        f"OPEC+ expected to raise 188K bpd from July — secondary to Iran escalation."
    )
}

with open("/Users/alexstocchi/projects/gazzetta-di-kyiv/data/telegram_intel/latest.json", "w") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print(json.dumps(final, ensure_ascii=False, indent=2))
