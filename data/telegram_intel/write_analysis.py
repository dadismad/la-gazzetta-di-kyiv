#!/usr/bin/env python3
"""Write telemetry intel JSON with proper escaping."""
import json

payload = {
  "scrape_timestamp": "2026-06-03T23:33:52+00:00",
  "cutoff_minutes": 30,
  "total_recent_messages": 1,
  "channels_checked": ["trad_fin", "MonitoringSituation", "ASupersharij", "infinityhedge", "ethanlevins", "markettwits"],
  "errors": [],
  "raw_messages": [
    {
      "channel": "ethanlevins",
      "text": "It's always been about \"survival\", even Nasrallah said it. Hezbollah can't \"stop\" an Israeli invasion, he's said this plenty of times. The goal is to resist and make it difficult. Hezbollah has done that. The resistance (whether it's Iran, Hamas, Hezbollah) doesn't have to \"win\", they have to survive. This is Hezbollah surviving, and Israel LEAVING. Rebuild and ReArm.",
      "published": "2026-06-03T23:19:32+00:00",
      "link": "https://t.me/ethanlevins/3326"
    }
  ],
  "actionable_intel": [
    {
      "story_id": "CEASEFIRE_AFTERMATH_HEZBOLLAH_SURVIVAL_20260603",
      "headline": "Hezbollah spins Lebanon ceasefire as survival and rearm — ethanlevins: Israel LEAVING. Rebuild and ReArm.",
      "event": "Ethan Levins at 23:19 UTC, 20 minutes after the Lebanon ceasefire was announced, publishes analysis framing the ceasefire as a Hezbollah victory: 'This is Hezbollah surviving, and Israel LEAVING. Rebuild and ReArm.' Channel 12 earlier reported (June 2) that Trump and Netanyahu agreed to issue an evacuation order for Dahiyeh without carrying out the attack. The 100+ strikes on Tyre were reportedly theater for cameras. Meanwhile ASupersharij reports ballistic strike destroying ATB's regional food warehouse in Dnipro — Ukraine's secondary theater continues escalating silently.",
      "location": "Beirut / Tel Aviv / Southern Lebanon / Dnipro, Ukraine",
      "timestamp": "2026-06-03T23:19:32+00:00",
      "narrative_consensus": "Mainstream media will frame: 'Israel achieves ceasefire, Hezbollah withdraws from southern Lebanon, de-escalation wins.' Crypto influencers: 'peace is bullish for risk assets.' Oil analysts revise down risk premium. The ethanlevins read will be dismissed as pro-Hezbollah propaganda.",
      "contradiction": "Ethan Levins just told you the actual outcome: Hezbollah doesn't lose. They evacuate the south (militarily smart — preserves force), remain ARMED, and get Israel to leave without any demobilization. The Tyre bombing that preceded it was reportedly staged (Channel 12: Trump and Netanyahu agreed to issue the evacuation order WITHOUT carrying out the attack). The 'ceasefire' is a repositioning, not a defeat. Iran still has missiles in Kuwait and Bahrain. Hormuz is unresolved. Dnipro lost its regional food supply chain to a ballistic strike — no Western press coverage.",
      "bet": {
        "primary": {
          "asset": "Crude Oil (WTI CL)",
          "direction": "HOLD SHORT FROM CEASEFIRE HEADLINE — COVER AFTER 2 HOURS OR IF IRAN NEWS BREAKS",
          "rationale": "The ceasefire headline gap-down is the dominant near-term oil move at Asian open. WTI ~$68 should gap to $65-66. HOWEVER: ethanlevins says Hezbollah is 'surviving and rearming' and Iran-US warship incident (Kuwait airport hit, Hormuz strike claim) is UNRESOLVED. This ceasefire trade has very short half-life. Take the short, take profit inside 2 hours, and flip long if Iranian retaliation is confirmed. The 'peace' narrative is being counter-spun by the same channels that broke the ceasefire.",
          "target_move": "-$2 to -$3/bbl WTI at Asian open, then RECOVERY within 2-4 hours as Hezbollah rearm and Iran shooting reality filters in.",
          "volume_impact": "Very high at Asian open. Expect $2+ spreads in WTI."
        },
        "secondary": {
          "asset": "Ethereum (ETH/USD) / Bitcoin (BTC/USD)",
          "direction": "SHORT / SELL ANY RELIEF BOUNCE",
          "rationale": "Marketwits at 19:12 UTC: MSTR unrealized BTC loss >$8.5B. Corporate BTC purchases at lowest since October 2024. The 'peace breakout -> risk-on -> crypto pump' trade is the trap. Whales will use the relief bounce to distribute. ETH at ~$1800 with BitMine $9B underwater means every green candle is exit liquidity. Short any bounce to $1830+ on ETH, $65.5K+ on BTC.",
          "target_move": "-5% to -8% ETH within 4 hours; -3% to -5% BTC targeting $62K.",
          "volume_impact": "Extreme. Funding rates deeply negative, OI contracting. Whales distributing into any bid."
        }
      }
    },
    {
      "story_id": "MSTR_BITMINE_WHALE_DISTRESS_UNRESOLVED_20260603",
      "headline": "MSTR $8.5B underwater, BitMine $9B underwater, corporate BTC buying at Oct 2024 lows — structural crypto distress confirmed",
      "event": "Marketwits (Russian-language) at 19:12 UTC: MSTR has $8.5B+ unrealized BTC loss. Trad_fin earlier: Google upsized equity raise to $84.75B from $80B — broad capital market stress. Marketwits (17:55 UTC): central banks bought 17 tons gold in April, net purchases resumed after March's net sales. Marketwits (20:03 UTC): Trump confirmed for G7 (June 15-17, France) and NATO summit (July 7-8, Turkey). infinityhedge has been silent since April 29, 2026 — dead channel for 6+ weeks.",
      "location": "Global crypto markets / US equity capital markets / Paris / Antalya",
      "timestamp": "2026-06-03T19:12:50+00:00",
      "narrative_consensus": "Crypto Twitter will use any peace headline to pump. 'Risk assets rally on Middle East ceasefire' is the default. Mainstream analysts will ignore MSTR/BitMine balance sheet stress as not systemic.",
      "contradiction": "The 'peace pump' narrative conveniently ignores that the largest corporate holders of both major crypto assets are technically insolvent on their holdings. MSTR at $8.5B underwater. BitMine at $9B underwater. They filed preferred shares NOT because they're bullish — they filed because they're BRINK. Google raising $84.75B same day tells you capital markets are stressed, not loose. Central banks buying gold confirms rotation away from risk. The crypto 'relief rally' will be sold into by the very whales who need to survive.",
      "bet": {
        "primary": {
          "asset": "Ethereum (ETH/USD)",
          "direction": "AGGRESSIVE SHORT / SELL THE PEACE RALLY",
          "rationale": "BitMine at $9B underwater with ETH at $1800 means every $100 drop adds $500M+ to their hole. Preferred share filing is a distress signal. If Lebanon ceasefire triggers 2-3% bounce to $1830-50, that's the distribution event. Target $1650-1700. Broader market realization that US-Iran shooting is unresolved accelerates cascade.",
          "target_move": "-5% to -10% ETH within 4-8 hours. $1800 -> $1700 fast. Below $1700 opens $1550.",
          "volume_impact": "Extreme. OI collapse visible in perpetual swap funding. V-shaped reversals expected."
        },
        "secondary": {
          "asset": "Gold (XAU/USD)",
          "direction": "SELECTIVE LONG / BUY ON CRYPTO CRASH",
          "rationale": "Marketwits confirms central banks resumed net gold purchases (17t April). G7 and NATO summits 12 and 30 days away — catalysts for Iran deal (bearish gold) or escalation (bullish). Crypto whale distress creates flow vector: if ETH/BTC cascade, capital flees to gold. Buy XAU if BTC breaks $64K. Target $2380-2400.",
          "target_move": "+1% to +2% XAU on crypto liquidation event. Gold range $2340-2380 currently.",
          "volume_impact": "Moderate. Gold consolidating. Crypto crash adds a bid."
        }
      }
    },
    {
      "story_id": "IRAN_US_WARSHIP_KUWAIT_AIRPORT_LATENT_20260603",
      "headline": "Iran struck Kuwait International Airport (killed 1), struck US-linked vessel Panaya, IRGC claims US hit oil tanker at Hormuz — ALL unresolved as ceasefire dominates",
      "event": "Layered unresolved incidents from past 24 hours being ignored due to Lebanon ceasefire: (1) Iran struck Kuwait International Airport 10:25 UTC today — killed 1, physical damage (ethanlevins). (2) US struck Iranian oil tanker near Hormuz, IRGC responded by striking US-Israeli vessel Panaya (ethanlevins, Jun 2 23:56 UTC). (3) Iran missile/drone attacks on Kuwait and Bahrain with ballistic missiles (Jun 2, 23:39 UTC). (4) Iran laid out 4-stage deal with US — same terms, USA won't accept (marketwits, 17:15 UTC). (5) Rubio called Russia a challenge (marketwits, 20:04 UTC). (6) MonitoringSituation: Trump yelled at Netanyahu 'What the fuck are you doing?' (10:19 UTC). (7) Blast in Qeshm Island (10:20 UTC). (8) Trump told Netanyahu 'You'd be in prison if it weren't for me. Everybody hates Israel.' (14:20 UTC). ALL unresolved.",
      "location": "Kuwait City / Persian Gulf / Strait of Hormuz / Qeshm Island / Washington DC",
      "timestamp": "2026-06-03T10:25:08+00:00",
      "narrative_consensus": "Zero. Entire narrative bandwidth consumed by Lebanon ceasefire. Kuwait airport strike, Hormuz tanker engagement, Qeshm blast — all buried under 'peace breakthrough.' Bloomberg terminals: 'Lebanon ceasefire = Middle East risk premium collapsing.'",
      "contradiction": "The market has been offered a monocausal narrative: Lebanon ceasefire = region at peace. IRAN MISSILED KUWAIT INTERNATIONAL AIRPORT TODAY. They killed someone. At an international civilian airport. And the market isn't pricing it. Trump told Netanyahu 'You're fucking crazy. You'd be in prison.' The US and Iran exchanged fire at Hormuz. Blast on Qeshm Island. Russia's deputy FM Ryabkov warned 'this is a signal, take it seriously.' The Lebanon ceasefire is a DISTRACTION, not a resolution. The Iran theater is hotter than 24 hours ago, and the market is about to misprice it badly.",
      "bet": {
        "primary": {
          "asset": "Crude Oil (WTI CL)",
          "direction": "BUY THE CEASEFIRE DIP — CONTRARIAN LONG",
          "rationale": "Everyone shorts oil on Lebanon ceasefire. But Iran struck Kuwait Airport. Hormuz tanker engagement unresolved. Qeshm Island had a blast. IRGC and US Navy actively shooting at each other's vessels. Lebanon ceasefire removes the NOISE from oil price and lets actual Iran-Hormuz risk be mispriced. WTI at $68 with shooting war at Hormuz is absurdly cheap. Buy the $2-3 gap-down at Asian open. Hold through European session. Recoupling to Iran risk happens within 6-12 hours.",
          "target_move": "Gap down to $65-66 (ceasefire headline), then recovery to $68-70 within 6 hours as Hormuz risk reprices. 2-hour window: BUY $65-66 area, target $67.50.",
          "volume_impact": "Extreme. Two-sided volatility. Gap-down triggers long stops, then Iran reality triggers short covering."
        },
        "secondary": {
          "asset": "US Defense (LMT, NOC, RTX)",
          "direction": "LONG / BUY THE PEACE DIP",
          "rationale": "Defense stocks sold on peace headlines. House voted 215-208 to end Iran war (symbolic, not veto-proof). But Kuwait got hit. Hormuz is active. US Navy engaged. Lebanon ceasefire doesn't stop US-Iran confrontation. LMT at $470-480 is a buy. Hold through G7/NATO summit catalysts.",
          "target_move": "+2% to +4% defense basket within 1-2 days as Hormuz re-emerges.",
          "volume_impact": "Moderate. Institutional."
        },
        "contrarian": {
          "asset": "Bitcoin (BTC/USD)",
          "direction": "SHORT / SELL THE FALSE PEACE PUMP",
          "rationale": "If crypto rallies 2-3% on 'peace = risk-on', that's the short entry. MSTR/BitMine distress hasn't changed. Iran-US shooting hasn't changed. Only Lebanon front changed — the SMALLEST of three risk vectors. Sell any BTC bounce to $65.5K+.",
          "target_move": "Short pump +2%, then unwind to -3% within 4 hours as macro reality reasserts.",
          "volume_impact": "High. Momentum market. Pump aggressive but short-lived."
        }
      }
    }
  ],
  "meta": {
    "analysis_model": "DeepSeek V4 Flash",
    "analysis_timestamp": "2026-06-03T23:33:52+00:00",
    "horizon": "2-hour market window",
    "current_time_utc": "2026-06-04T00:33:00+00:00",
    "stories_identified": 3,
    "channels_silent": ["trad_fin (last 9.3h ago)", "MonitoringSituation (last 8.9h ago)", "ASupersharij (last 6.6h ago)", "infinityhedge (DEAD — Apr 29)", "markettwits (last 3.5h ago)"],
    "note": "Only 1 fresh message (ethanlevins ceasefire analysis). Three structural stories remain actionable: (1) ceasefire aftermath + Hezbollah rearm narrative, (2) MSTR/BitMine whale distress confirmed multi-source, (3) Iran-US Hormuz conflict still actively unresolved and MIS-PRICED by market. infinityhedge dead since Apr 29. Most actionable 2-hour trade: BUY the oil dip (Hormuz > Lebanon), SHORT the crypto pump (whale distribution > relief rally)."
  }
}

with open("/Users/alexstocchi/.hermes/hermes-agent/gazzetta-di-kyiv/data/telegram_intel/latest.json", "w") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)

print("Written successfully")
print(f"Size: {len(json.dumps(payload, indent=2, ensure_ascii=False))} chars")
