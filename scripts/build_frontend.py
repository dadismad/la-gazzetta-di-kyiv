#!/usr/bin/env python3
"""
build_frontend.py -- Gazzetta di Kyiv Multi-View Dashboard Compiler
Generates a single responsive SPA with 4 analytical views:
  1. The Stream — real-time story feed
  2. Capital Flows — macro ledger + discrepancy markers
  3. Contradictions — sortable matrix + vulnerability map
  4. About — epistemological framing + narrative lifecycle

Design: Stitch DESIGN.md (mobile) + Banani desktop sidebar
0px radius, no shadows, gold structural rules, Playfair+Inter.
"""

import json, sys, os
from pathlib import Path
from datetime import datetime, timezone, timedelta

PROJECT = Path(os.environ.get("GAZZETTA_HOME", "/opt/gazzetta-di-kyiv"))
DATA = PROJECT / "data"
PUBLIC = PROJECT / "public"
PUBLIC_DATA = PUBLIC / "data"

ICON_FALLBACK_MAP = {
    "dollar_decline": "trending_down", "critical_resource_control": "bolt",
    "deglobalization": "public", "china_ascent": "language",
    "space_economy": "rocket_launch", "gene_editing": "biotech",
    "tech_convergence": "memory", "wealthy_sports": "sports_soccer",
    "ai_chips": "memory", "crypto_reserve": "account_balance",
    "rate_cycle": "percent", "commodity_supercycle": "inventory_2",
}

LEGACY_ORDER = [
    "dollar_decline", "critical_resource_control", "deglobalization",
    "china_ascent", "space_economy", "gene_editing",
    "tech_convergence", "wealthy_sports"
]

def load_json(path):
    with open(path) as f:
        return json.load(f)


# ── NMC Data: load the .5T Narrative Market Capitalization cache ──
NMC_PATH = DATA / "narrative_cap.json"
NMC_DATA = {}
if NMC_PATH.exists():
    try:
        NMC_DATA = load_json(NMC_PATH)
    except Exception:
        pass

def fmt_b(n):
    if n >= 1: return f"${n:.1f}B"
    m = n * 1000
    if m >= 1: return f"${m:.0f}M"
    return f"${m:.1f}M"

def fmt_time_ago(ts_str):
    if not ts_str: return ""
    try:
        d = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        hours = (now - d).total_seconds() / 3600
        if hours < 1: return "Just now"
        return f"{int(hours)}H AGO"
    except:
        return ""

def narrative_phase(gap, count):
    """Heuristic narrative lifecycle phase using top_gap for accuracy."""
    if count < 3: return "EMERGENT", "New signal — limited data"
    if gap >= 80: return "CRITICAL SHIFT", "Extreme divergence — media narrative disconnected from capital reality"
    if gap >= 70: return "ACTIVE DIVERGENCE", "Significant gap — institutional capital actively contradicting consensus"
    if gap >= 50: return "BUILDING TENSION", "Growing friction between media framing and capital positioning"
    return "MATURE/STABLE", "Narrative and capital flows broadly aligned"


def calculate_narrative_status(top_gap, story_count):
    """Dynamic status label based on top story gap + story velocity proxy."""
    if top_gap >= 70 and story_count > 3:
        return "BREAKING ACCELERATION"
    elif top_gap >= 50:
        return "ACTIVE CONTRADICTION"
    return "SETTLING REGIME"


# Canonical ticker safe-list per narrative — gates LLM output
CANONICAL_TICKERS = {
    "dollar_decline":        ["GLD", "UUP", "SLV", "IAU", "DXY", "EURUSD=X"],
    "critical_resource_control": ["CL=F", "XOM", "CVX", "CCJ", "URNM", "URA", "NLR", "REMX"],
    "deglobalization":       ["XLI", "ITA", "PPA", "XME"],
    "china_ascent":          ["FXI", "KWEB", "MCHI", "ASHR", "BABA", "OBOR", "AAXJ", "CNYB", "EMLC"],
    "space_economy":         ["ROKT", "UFO", "ARKX", "RKLB", "LMT", "MARS", "SPCE", "ASTR", "MOON"],
    "gene_editing":          ["ARKG", "XBI", "IBB"],
    "tech_convergence":      ["CLOU", "WCLD", "ARTY", "BOTZ", "FCLD", "MSFT", "GOOGL", "NVDA", "ORCL", "CRM"],
    "wealthy_sports":        ["DKNG", "PENN", "MGM", "DIS", "CMCSA", "WBD", "FOXA", "MSG", "FUBO", "STAD"],
    "ai_chips":              ["NVDA", "AMD", "TSM", "SMH"],
    "crypto_reserve":        ["BTC-USD", "ETH-USD", "COIN"],
    "rate_cycle":            ["TLT", "SHY", "IEF"],
    "commodity_supercycle":  ["DBC", "GLD", "GDX"],
}


def build_cft_block(narrative_id, stories, narrative_config):
    """Extract the top catalyst story and build a CFT summary block."""
    # Multi-vector routing: check the containers list first, fallback to narrative_id
    mine = [
        s for s in stories
        if narrative_id in (s.get("containers") or [s.get("narrative_id")])
    ]

    if not mine:
        return None

    catalyst = max(mine, key=lambda s: s.get("contradiction_gap", 0) or 0)
    gap = catalyst.get("contradiction_gap", 0) or 0
    if gap < 25:
        return None

    capital = catalyst.get("capital_volume_usd", 0) or 0
    assets = catalyst.get("affected_asset_classes") or []

    # ── Ticker gate: filter LLM output through canonical safe-list ──
    llm_tickers = catalyst.get("affected_tickers") or []
    if narrative_id in CANONICAL_TICKERS:
        narrative_safe_list = CANONICAL_TICKERS[narrative_id]
        filtered_tickers = [t for t in llm_tickers if t in narrative_safe_list]
        final_tickers = filtered_tickers if filtered_tickers else narrative_safe_list[:4]
    else:
        # Fail-open: trust the LLM for unmapped narratives
        final_tickers = llm_tickers[:4]

    # ── Content fallbacks: they_say → catalyst, reality → flow ──
    card_catalyst = (catalyst.get("they_say") or "").strip() or "Awaiting narrative acceleration event."
    card_flow = (catalyst.get("reality") or "").strip() or "Capital baseline established. Monitoring movements."

    # ── Dynamic status label (24h velocity) ──
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_count = sum(
        1 for s in mine
        if s.get("generated_at") and datetime.fromisoformat(s["generated_at"]) > cutoff
    )
    # TODO: sync 24h velocity logic to narrative_phase() at line 220
    status_label = calculate_narrative_status(gap, recent_count)

    # Domino ripples from narrative_weights
    weights = catalyst.get("narrative_weights", {})
    domino = []
    for nid, score in sorted(weights.items(), key=lambda x: -x[1]):
        if nid == narrative_id:
            continue
        if score >= 0.25:
            cfg = narrative_config.get(nid, {})
            domino.append({
                "narrative_id": nid,
                "title": cfg.get("display_name", nid.replace("_", " ").title()),
                "score": round(score, 2),
            })

    # Safe inline formatting
    if capital >= 1_000_000_000:
        capital_fmt = f"${capital / 1e9:.1f}B"
    elif capital >= 1_000_000:
        capital_fmt = f"${capital / 1e6:.1f}M"
    else:
        capital_fmt = f"${capital:,}"

    return {
        "catalyst_text": card_catalyst,
        "catalyst_gap": gap,
        "flow_text": card_flow,
        "capital_usd": capital,
        "capital_fmt": capital_fmt,
        "affected_tickers": final_tickers,
        "affected_asset_classes": assets,
        "domino": domino,
        "status": status_label,
    }

def load_narratives_config():
    """Load narrative taxonomy from narratives.json. Returns (dict, ordered_ids)."""
    path = DATA / "narratives.json"
    if not path.exists():
        return {}, list(LEGACY_ORDER)
    data = load_json(path)
    narratives = data.get("narratives", {})
    ordered = sorted(narratives.keys(),
                    key=lambda nid: (narratives[nid].get("capital_total_usd", 0),
                                    narratives[nid].get("story_count", 0)),
                    reverse=True)
    return narratives, ordered

def build():
    import sys
    lang = "en"
    stories_src = DATA / "stories.json"

    print(f"[build_frontend] loading data... (lang={lang})")
    stories_raw = load_json(stories_src)

    # Try flows.json for cross-asset data
    flows_raw = {}
    flows_path = PUBLIC_DATA / "flows.json"
    if flows_path.exists():
        flows_raw = load_json(flows_path)

    # Normalize stories from top-level all_stories (narrative_id system)
    all_stories = stories_raw.get("all_stories", [])
    if not all_stories:
        # Legacy fallback: expand containers
        containers = stories_raw.get("containers", {})
        for cid, cdata in containers.items():
            for s in cdata.get("stories", []):
                s["_container_id"] = cid
                all_stories.append(s)

    # Load narrative taxonomy
    narrative_config, narrative_ids = load_narratives_config()

    # Inject _container_id and _container_title from narrative_id for JS rendering
    for s in all_stories:
        nid = s.get("narrative_id", "")
        if nid and nid in narrative_config:
            s["_container_id"] = nid
            s["_container_title"] = narrative_config[nid].get("display_name", nid)

    # Defence-in-depth: filter out anomalous source "T" artefacts (pre-synthesizer-fix stories)
    all_stories = [s for s in all_stories if (s.get("source_name") or "").strip().upper() != "T"]

    # Bridge: capital_at_stake_usd → capital_volume_usd
    # calculate_capital.py writes capital_at_stake_usd (computed from CFTC/FRED/prices).
    # contradiction_synthesizer.py writes capital_volume_usd (LLM inference, mostly 0).
    # All downstream Python and JS code reads capital_volume_usd. Normalize here once
    # so the 8 reference locations don't need individual patches.
    for s in all_stories:
        computed = s.get("capital_at_stake_usd", 0) or 0
        existing = s.get("capital_volume_usd", 0) or 0
        # Always prefer the computed value (real data, hard-capped) over LLM inference
        if computed > 0:
            s["capital_volume_usd"] = computed
        elif existing == 0:
            s["capital_volume_usd"] = 0
    all_stories.sort(key=lambda s: s.get("generated_at", ""), reverse=True)

    # Compute narrative summaries from narratives.json taxonomy

    narratives = []
    for cid in narrative_ids:
        cstories = [s for s in all_stories if s.get("narrative_id") == cid]
        caps = [s.get("capital_volume_usd", 0) or 0 for s in cstories]
        gaps = [s.get("contradiction_gap", 0) or 0 for s in cstories]
        total_cap = sum(caps) / 1e9
        # Override with NMC data when available (prioritises live market cap)
        nmc_entry = NMC_DATA.get(cid, {})
        nmc_usd = nmc_entry.get("narrative_cap_usd", 0)
        if nmc_usd and nmc_usd > 0:
            total_cap = nmc_usd / 1e9
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        top_gap = max(gaps) if gaps else 0
        directions = {"inflow": 0, "outflow": 0, "neutral": 0}
        for s in cstories:
            cf = s.get("capital_flow") or {}
            d = (cf.get("direction") or "neutral").lower()
            directions[d] = directions.get(d, 0) + 1
        phase, phase_desc = narrative_phase(top_gap, len(cstories))
        cfg = narrative_config.get(cid, {})
        ticker = (cfg.get("tickers", [""]) or [""])[0]
        threshold_val = cfg.get("invalidation_threshold", "N/A")
        threshold_desc = cfg.get("status", "")
        narratives.append({
            "id": cid,
            "title": cfg.get("display_name", cid.replace("_", " ").title()),
            "ticker": ticker or "N/A",
            "capital_b": total_cap,
            "count": len(cstories),
            "gap": avg_gap,
            "directions": directions,
            "phase": phase,
            "phase_desc": phase_desc,
            "threshold_val": threshold_val,
            "threshold_desc": threshold_desc,
            "icon": ICON_FALLBACK_MAP.get(cid, "public"),
            "cft": build_cft_block(cid, all_stories, narrative_config),
        })

    # Capital flows — compute discrepancies
    discrepancies = [s for s in all_stories if (s.get("contradiction_gap") or 0) >= 40]
    capital_flows = []
    for n in narratives:
        cap_stories = [s for s in all_stories if s.get("narrative_id") == n["id"]]
        inflow_total = sum((s.get("capital_volume_usd") or 0) / 1e9 for s in cap_stories
                          if (s.get("capital_flow") or {}).get("direction") == "inflow")
        outflow_total = sum((s.get("capital_volume_usd") or 0) / 1e9 for s in cap_stories
                           if (s.get("capital_flow") or {}).get("direction") == "outflow")
        disc_count = sum(1 for s in cap_stories if (s.get("contradiction_gap") or 0) >= 40)
        capital_flows.append({
            "narrative": n["title"],
            "ticker": n["ticker"],
            "inflow_b": inflow_total,
            "outflow_b": outflow_total,
            "net_b": inflow_total - outflow_total,
            "total_b": n["capital_b"],
            "stories": n["count"],
            "discrepancies": disc_count,
            "gap": n["gap"],
        })

    # Contradictions now computed client-side from STORIES (see renderMatrix)

    # Cross-asset data
    cross_asset = flows_raw.get("cross_asset", {})
    regime = flows_raw.get("regime", stories_raw.get("regime", "risk-on"))
    regime_drivers = flows_raw.get("regime_drivers", [])

    # Strip dead fields from stories (never read by frontend)
    dead_fields = {"thesis", "multi_persona", "confidence_pct", "contradiction_score", "sector", "source_name", "pillar", "tags"}
    stories_slim = []
    for s in all_stories[:200]:
        stories_slim.append({k: v for k, v in s.items() if k not in dead_fields})

    # Serialize
    stories_json = json.dumps(stories_slim, ensure_ascii=False)
    narratives_json = json.dumps(narratives, ensure_ascii=False)
    capital_json = json.dumps(capital_flows, ensure_ascii=False)
    cross_asset_json = json.dumps(cross_asset, ensure_ascii=False)
    regime_json = json.dumps(regime, ensure_ascii=False)
    regime_drivers_json = json.dumps(regime_drivers, ensure_ascii=False)
    build_time = datetime.now(timezone.utc).isoformat()
    disc_count = len(discrepancies)
    sync_status = "Active" if disc_count < 50 else "Warning"

    # Load derivatives tactical data (from fetch_derivatives.py)
    derivatives_json = "{}"
    derivatives_path = PUBLIC_DATA / "derivatives.json"
    if derivatives_path.exists():
        try:
            with open(derivatives_path) as f:
                derivatives_json = json.dumps(json.load(f), ensure_ascii=False)
        except Exception:
            pass

    print(f"[build_frontend] {len(all_stories)} stories, {disc_count} discrepancies, regime={regime}")

    html = _TEMPLATE
    html = html.replace("__STORIES_JSON__", stories_json)
    html = html.replace("__NARRATIVES_JSON__", narratives_json)
    html = html.replace("__CAPITAL_JSON__", capital_json)
    html = html.replace("__CONTRADICTIONS_JSON__", "[]")
    html = html.replace("__CROSS_ASSET_JSON__", cross_asset_json)
    html = html.replace("__REGIME_JSON__", regime_json)
    html = html.replace("__REGIME_DRIVERS_JSON__", regime_drivers_json)
    html = html.replace("__DERIVATIVES_JSON__", derivatives_json)
    html = html.replace("__REGIME_STR__", str(regime))
    html = html.replace("__BUILD_TIME__", build_time)
    html = html.replace("__STORY_COUNT__", str(len(all_stories)))
    html = html.replace("__DISC_COUNT__", str(disc_count))
    html = html.replace("__SYNC_STATUS__", sync_status)

    PUBLIC.mkdir(parents=True, exist_ok=True)
    out = PUBLIC / "index.html"
    with open(out, "w") as f:
        f.write(html)

    print(f"[build_frontend] wrote {out} ({len(html)} bytes)")

    # Generate dossier pages
    try:
        from build_dossiers import build_dossiers
        build_dossiers(all_stories, flows_raw, narrative_config)
    except ImportError:
        print("[build_frontend] build_dossiers not available, skipping dossier pages.")

    return True


_TEMPLATE = r"""<!DOCTYPE html>
<html class="light" lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>La Gazzetta di Kyiv — Geopolitical Intelligence</title>
<meta name="description" content="Institutional-grade narrative intelligence. Tracking the Contrarian Edge (Δ) between media consensus and capital flows."/>
<meta property="og:title" content="La Gazzetta di Kyiv — Geopolitical Intelligence"/>
<meta property="og:description" content="Institutional-grade narrative intelligence. Tracking the Contrarian Edge (Δ) between what the media says and what capital actually does."/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://www.lagazzettadikyiv.com/"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="La Gazzetta di Kyiv — Geopolitical Intelligence"/>
<meta name="twitter:description" content="Institutional-grade narrative intelligence. Tracking the Contrarian Edge (Δ) between what the media says and what capital actually does."/>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='12' fill='%238B0000'/><text x='50' y='65' text-anchor='middle' font-family='Georgia,serif' font-size='52' font-weight='bold' fill='%23D4AF37'>G</text></svg>"/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script>
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "surface": "#FAF9F6","surface-dim": "#DBDAD7","surface-bright": "#FAF9F6",
        "surface-container": "#EFEEEB","surface-container-high": "#E9E8E5",
        "surface-container-highest": "#E3E2E0","on-surface": "#E6E4E0",
        "on-surface-variant": "#9B97B0","inverse-surface": "#2F312F",
        "inverse-on-surface": "#F2F1EE","outline": "#747878",
        "outline-variant": "#C4C7C7","gold": "#D4AF37","gold-dim": "#B8860B","gold-accessible": "#B45309",
        "crimson": "#7F1D1D","roman-purple": "#66023C","emerald": "#10B981","navy": "#1A1F2E",
        "primary": "#000000","on-primary": "#FFFFFF","secondary": "#735C00",
        "on-secondary": "#FFFFFF","secondary-fixed-dim": "#E9C349",
        "error": "#BA1A1A","error-container": "#FFDAD6","on-error-container": "#93000A",
      },
      borderRadius: {"DEFAULT":"0px","lg":"0px","xl":"0px","full":"0px"},
      spacing: {"margin-horizontal":"16px","stack-space-lg":"32px","stack-space-sm":"8px","stack-space-md":"16px","tap-target-min":"48px"},
      fontFamily: {
        "display-xl":["Playfair Display","Georgia","serif"],
        "headline-lg":["Playfair Display","Georgia","serif"],
        "headline-lg-mobile":["Playfair Display","Georgia","serif"],
        "headline-md":["Playfair Display","Georgia","serif"],
        "body-md":["Inter","sans-serif"],"metadata-sm":["Inter","sans-serif"],"label-xs":["Inter","sans-serif"],
      },
      fontSize: {
        "display-xl":["40px",{lineHeight:"48px",letterSpacing:"-0.02em",fontWeight:"700"}],
        "headline-lg":["16px",{lineHeight:"22px",fontWeight:"700"}],
        "headline-lg-mobile":["18px",{lineHeight:"24px",fontWeight:"700"}],
        "headline-md":["14px",{lineHeight:"20px",fontWeight:"600"}],
        "body-md":["13px",{lineHeight:"20px",fontWeight:"400"}],
        "metadata-sm":["11px",{lineHeight:"16px",fontWeight:"500",letterSpacing:"0.04em"}],
        "label-xs":["10px",{lineHeight:"14px",fontWeight:"600",letterSpacing:"0.02em"}],
      },
    }
  }
}
</script>
<style>
  /* ── DARK TERMINAL THEME (v34.0) ── */
  :root {
    --bg-primary:    #0A0A0F;
    --bg-secondary:  #12121A;
    --bg-tertiary:   #1A1A24;
    --text-primary:  #E6E4E0;
    --text-secondary:#9B97B0;
    --text-muted:    #5C5870;
    --gold:          #D4AF37;
    --gold-dim:      #8B7332;
    --crimson:       #8B0000;
    --green:         #27AE60;
    --red:           #E74C3C;
    --blue:          #5DADE2;
    --edge-extreme:  #FF6B35;
    --edge-high:     #D4AF37;
    --edge-medium:   #9B97B0;
    --edge-low:      #5C5870;
  }
  *,*::before,*::after{border-radius:0!important;box-shadow:none!important}
  body{background:var(--bg-primary)!important;color:var(--text-primary)!important;min-height:100dvh}
  /* ── PHASE 8 GLOBAL TYPOGRAPHY OVERRIDES (desktop-first) ── */
  .font-body-md{font-size:13px!important;line-height:1.5}
  h3.font-headline-md,h3,.font-headline-md{font-size:14px!important;line-height:1.35!important;font-weight:600}
  .font-label-xs,.text-label-xs{font-size:11px!important}
  /* Emerald allocation token */
  .allocation-pct{color:#10B981!important;font-family:'JetBrains Mono',monospace}
  /* Data font enforcement */
  .gap-score,.price-target,.mono-data{font-family:'JetBrains Mono',monospace}
  h2.text-gold{color:#B8860B!important}
  .hide-scrollbar{-ms-overflow-style:none;scrollbar-width:none}
  .hide-scrollbar::-webkit-scrollbar{display:none}
  .gold-strikethrough{position:relative;display:inline-block}
  .gold-strikethrough::after{content:'';position:absolute;left:0;top:50%;width:100%;height:1px;background:#D4AF37;transform:translateY(-50%);z-index:10}
  .gold-outline{-webkit-text-stroke:1px #D4AF37}
  .meter-container{width:100%;height:4px;background:#E3E2E0;position:relative}
  .meter-fill-pos{position:absolute;left:50%;height:100%;background:#D4AF37}
  .meter-fill-neg{position:absolute;right:50%;height:100%;background:#BA1A1A}
  .discrepancy-row{border-left:4px solid #BA1A1A;padding-left:12px;background:rgba(255,218,214,0.2)}
  .tab-content{display:none}
  .tab-content.active{display:block}
  .tab-btn.active{border-bottom:2px solid #D4AF37;color:#1A1C1A}
  details summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:4px;user-select:none;min-height:48px}
  details summary::-webkit-details-marker{display:none}
  details summary::marker{display:none;content:''}
  details[open] summary .expand-icon{transform:rotate(180deg)}
  details .expand-icon{transition:transform 0.2s;font-size:20px}
  details[open] > .details-content{animation:fadeIn 0.2s ease}
  @keyframes fadeIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}

  /* FOCUS RINGS — WCAG 2.4.7 */
  button:focus-visible,a:focus-visible,[role=\"button\"]:focus-visible,details summary:focus-visible{outline:2px solid #B45309;outline-offset:2px}
  input:focus-visible,select:focus-visible{outline:2px solid #B45309;outline-offset:1px}

  /* GLOSSARY TOOLTIP */
  .glossary-tip{position:fixed;z-index:9999;max-width:260px;padding:10px 14px;background:#1A1C1A;color:#FAF9F6;font-size:13px;line-height:1.4;border-left:3px solid #D4AF37;box-shadow:0 4px 12px rgba(0,0,0,0.25);pointer-events:none;opacity:0;transform:translateY(4px);transition:opacity 0.15s,transform 0.15s}
  .glossary-tip.visible{opacity:1;transform:translateY(0)}
  .glossary-target{cursor:help;border-bottom:1px dotted #B8860B}
  .glossary-target:hover{color:#B45309}

  /* MOBILE BREAKPOINTS */
  /* ── HORIZONTAL NAV (scroll-snap, app-like swipe) ── */
  .top-nav{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;scrollbar-width:none;gap:0;border-bottom:1px solid var(--gold-dim)}
  .top-nav::-webkit-scrollbar{display:none}
  .top-nav a{scroll-snap-align:start;flex:0 0 auto;padding:12px 20px;font-family:'JetBrains Mono',monospace;font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-secondary);border-bottom:2px solid transparent;white-space:nowrap;text-decoration:none}
  .top-nav a.active{color:var(--gold);border-bottom-color:var(--gold)}
  /* ── MOBILE PROGRESSIVE DISCLOSURE (<details> hinting) ── */
  .story-card-hint summary{list-style:none;cursor:pointer}
  .story-card-hint summary::-webkit-details-marker{display:none}
  .story-card-hint summary::marker{display:none;content:''}
  .card-hook{display:flex;align-items:center;gap:8px;padding:12px;background:var(--bg-secondary);border-left:3px solid var(--gold);min-height:48px}
  .card-hook .edge-badge{padding:2px 8px;font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;border-radius:2px}
  .edge-badge.edge-80{background:var(--edge-extreme);color:#0A0A0F}
  .edge-badge.edge-60{background:var(--edge-high);color:#0A0A0F}
  .edge-badge.edge-40{background:var(--edge-medium);color:#0A0A0F}
  .edge-badge.edge-0{background:var(--edge-low);color:var(--text-primary)}
  .card-hook .one-liner{flex:1;font-size:13px;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .card-hook .price-move{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:600}
  .card-hook .price-move.positive{color:var(--green)}
  .card-hook .price-move.negative{color:var(--red)}
  .card-expanded{padding:16px;background:var(--bg-tertiary);border-left:3px solid var(--gold);font-size:13px;line-height:1.6}
  @media (max-width:768px){
    #desktop-sidebar{display:none!important}
    .md\\:ml-72{margin-left:0!important}
    .tab-btn{font-size:11px;padding:8px 10px;min-height:44px}
    .tab-btn .material-symbols-outlined{font-size:16px;margin-right:2px}
    #tab-nav{gap:0}
    h1{font-size:14px!important;line-height:18px!important}
    h1 .material-symbols-outlined{font-size:16px!important}
    main{padding-left:12px!important;padding-right:12px!important}
    .grid-cols-1{grid-template-columns:1fr!important}
    .md\\:grid-cols-2{grid-template-columns:1fr!important}
    .xl\\:grid-cols-3{grid-template-columns:1fr!important}
    table{font-size:12px}
    th,td{padding:6px 4px!important}
    .overflow-x-auto{-webkit-overflow-scrolling:touch}
    #cta-banner{flex-direction:column;align-items:flex-start;gap:8px}
    footer{font-size:11px;padding:16px 12px}
    footer .flex{flex-direction:column;gap:4px}
    /* PHASE A4 — Mobile touch-target compliance */
    .filter-pill{min-height:44px;min-width:44px;padding:8px 14px;font-size:14px;display:inline-flex;align-items:center;border-radius:20px;background:transparent;border:1px solid #D1D5DB;color:#6B7280;cursor:pointer;transition:all 0.15s ease;font-family:Inter,sans-serif;font-weight:500;text-transform:uppercase;letter-spacing:0.03em}
    .filter-pill:hover{background:#F3F4F6;border-color:#9CA3AF;color:#1A1C1A}
    .filter-pill.active{background:#8B0000;border-color:#8B0000;color:#FFFFFF}
    .filter-pill.active[data-filter*="ACTIVE"]{background:#D4AF37;border-color:#D4AF37;color:#1A1C1A}
    .filter-pill .material-symbols-outlined{font-size:18px;margin-right:4px}
    /* Collapse sprawling source filter into scrollable row with larger pills on mobile */
    #filter-bar{overflow-x:auto;-webkit-overflow-scrolling:touch;white-space:nowrap;padding-bottom:4px}
    #origin-pills{display:flex;flex-wrap:nowrap;gap:4px}
    /* Phase 8: Sticky radar extended to 768px */
    #tactical-radar{position:sticky;top:56px;z-index:25;background:rgba(255,255,255,0.85);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid #E5E7EB;padding:10px 12px;margin-bottom:8px}
  }
  @media (max-width:480px){
    /* Tightest phones — collapse source filter pills into a compact scrollable strip
       with minimum 44px height to meet Apple HIG / Android Material guidelines */
    .filter-pill{min-height:44px;min-width:44px;padding:10px 12px;font-size:13px}
    #origin-pills{gap:4px}
    #filter-bar{gap:4px}
    /* RADAR font-size bump for readability */
    .radar-card{font-size:13px}
    .radar-card .text-xs{font-size:12px!important}
  }
  @media (max-width:390px){
    #tab-nav{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch}
    .tab-btn{font-size:10px;padding:6px 8px;white-space:nowrap}
    h3{font-size:16px!important}
    .font-headline-md{font-size:16px!important;line-height:22px!important}
    .font-body-md{font-size:14px!important;line-height:20px!important}
  }

  /* TACTICAL RADAR */
  .radar-card{background:#EFEEEB;border-left:3px solid #B45309;padding:12px 16px;margin-bottom:12px}
  .radar-card summary{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;color:#747878;cursor:pointer;user-select:none;min-height:44px;display:flex;align-items:center;gap:6px}
  .radar-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:8px}
  @media(max-width:768px){.radar-grid{grid-template-columns:1fr}}
  .radar-cell{padding:10px 12px;background:#FAF9F6;border-left:2px solid #E3E2E0}
  .radar-cell.sqz{border-left-color:#8B0000}
  .radar-cell.warn{border-left-color:#B45309}
  .radar-cell.safe{border-left-color:#15803d}
  .badge-alert{background:#8B0000;color:#FAF9F6;padding:2px 8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.03em}
  .badge-warn{background:#78350f;color:#FEF3C7;padding:2px 8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.03em}
  .badge-safe{background:#15803d;color:#DCFCE7;padding:2px 8px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.03em}
  .glass-panel{background:rgba(255,255,255,0.85);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
  .glass-panel-dark{background:rgba(255,255,255,0.92);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}

  /* C4: DECAY CLOCK */
  .decay-meter{width:100%;height:3px;background:#E5E7EB;margin-top:4px;position:relative;overflow:hidden}
  .decay-fill{position:absolute;left:0;top:0;height:100%;transition:width 0.6s ease}
  .decay-fresh{background:#D4AF37}
  .decay-active{background:#B45309}
  .decay-critical{background:#7F1D1D;animation:decayPulse 4s ease-in-out infinite}
  @keyframes decayPulse{0%,100%{opacity:1}50%{opacity:0.5}}
  .decay-label{font-size:10px;color:#747878;text-transform:uppercase;letter-spacing:0.03em;margin-top:2px}
  .decay-label-critical{color:#8B0000;font-weight:700}
  /* Shiller layer: Media Says / Capital Says — visible card surface */
  .shiller-surface{background:linear-gradient(90deg, rgba(139,0,0,0.02) 0%, rgba(212,175,55,0.03) 100%);padding:4px 6px;border-radius:2px;margin-top:1px}
  .shiller-surface div{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  @media (max-width:640px){.shiller-surface{grid-template-columns:1fr;gap:2px}}
  /* C3: Δ EDGE PHYSICS — border thickness + color scale */
  article[data-tier="BREAKING"]{border-left-width:4px;border-left-color:#7F1D1D}
  /* Contradiction Alert cards (Δ EDGE >= 80) */
  article.contradiction-alert{border-left-width:6px;border-left-color:#8B0000;background:rgba(139,0,0,0.03);padding-left:12px}
  .contradiction-alert-badge{display:inline-block;background:#8B0000;color:#FFFFFF;font-size:11px;font-weight:600;letter-spacing:1px;padding:2px 8px;border-radius:3px;text-transform:uppercase}
  @keyframes alert-pulse{0%,100%{border-left-color:#8B0000}50%{border-left-color:#4A0000}}
  article.contradiction-alert{animation:alert-pulse 6s ease-in-out infinite}
  article.contradiction-alert .gap-score{font-size:32px!important;font-weight:700}
  article[data-tier="ACTIVE"]{border-left-width:2px;border-left-color:#D4AF37}
  article[data-tier="SETTLING"]{border-left-width:1px;border-left-color:#444748;opacity:0.7}
  @keyframes edgePulse{0%,100%{border-left-color:#7F1D1D}50%{border-left-color:#D4AF37}}
  article[data-gap-high="true"]{animation:edgePulse 6s ease-in-out infinite}
  /* Monospace for data density */
  .font-mono-data{font-family:'JetBrains Mono',SFMono-Regular,monospace;font-size:11px;letter-spacing:-0.02em}
  .gap-score,.capital-num,.ticker-mono,.price-mono{font-family:'JetBrains Mono',SFMono-Regular,monospace}

  /* ── PHASE 2: BENTO GRID for story cards ── */
  #story-cards{display:grid;grid-template-columns:1fr;gap:0;align-items:start}
  /* BREAKING ZONE header + all BREAKING cards span full width */
  #story-cards .zone-header.breaking-zone, #story-cards article[data-tier="BREAKING"]{grid-column:1/-1}
  @media(min-width:768px){
    #story-cards{grid-template-columns:repeat(2,1fr)}
    #story-cards article{border-left:1px solid #E5E7EB;border-bottom:1px solid #E5E7EB}
  }
  @media(min-width:1024px){
    #story-cards{grid-template-columns:repeat(3,1fr)}
  }
  /* CONTRADICTION ALERT cards span 2 columns on desktop for emphasis */
  @media(min-width:768px){
    #story-cards article.contradiction-alert{grid-column:span 2}
  }
  /* Maintain existing expand/collapse — cards grow vertically, not horizontally */
  #story-cards article[open] .details-content{grid-column:1/-1}
</style>
</head>
<body class="bg-surface font-body-md text-on-surface antialiased">

<!-- ═══ DESKTOP SIDEBAR ═══ -->
<aside class="hidden md:flex md:flex-col fixed left-0 top-0 h-full w-72 text-on-surface z-40 overflow-y-auto glass-panel-dark" id="desktop-sidebar">
  <div class="p-stack-space-md border-b border-gold">
    <h2 class="font-headline-md text-headline-md text-gold mb-1">Domain Intelligence</h2>
    <p class="font-label-xs text-label-xs text-outline-variant uppercase tracking-wider">__REGIME_STR__</p>
  </div>
  <nav class="flex-1 overflow-y-auto p-stack-space-sm" id="sidebar-nav"></nav>
  <div class="mt-auto p-stack-space-md border-t border-gold">
    <h3 class="font-label-xs text-label-xs text-outline-variant uppercase mb-3">Vulnerability Map</h3>
    <div class="space-y-3" id="sidebar-vuln"></div>
  </div>
</aside>

<div class="md:ml-72 flex flex-col min-h-screen">

  <!-- MASTHEAD -->
  <header class="border-b border-gold w-full px-margin-horizontal h-14 sticky top-0 z-30 glass-panel">
    <div class="flex justify-between items-center h-full">
      <button class="w-tap-target-min h-tap-target-min flex items-center justify-center text-on-surface-variant md:hidden" onclick="document.getElementById('mobile-menu').classList.toggle('hidden')">
        <span class="material-symbols-outlined">menu</span>
      </button>
      <div class="hidden md:flex w-tap-target-min h-tap-target-min items-center justify-center"></div>
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-gold hidden sm:inline" style="font-variation-settings:'FILL'1';" aria-hidden="true">pest_control</span>
        <h1 class="font-headline-lg-mobile text-[16px] leading-[20px] sm:text-[20px] sm:leading-[26px] md:text-headline-lg-mobile uppercase tracking-widest text-roman-purple gold-strikethrough gold-outline">La Gazzetta di Kyiv</h1>
        <span class="material-symbols-outlined text-gold hidden sm:inline" style="font-variation-settings:'FILL'1';" aria-hidden="true">gavel</span>
      </div>
      <div class="w-tap-target-min h-tap-target-min flex items-center justify-center"></div>
    </div>
  </header>

  <!-- TAGLINE -->
  <p class="font-body-md text-body-md text-[#747878] text-center mt-1 max-w-xl mx-auto px-4">
    Institutional Narrative Intelligence — monitoring the variance between media consensus and capital flows.
  </p>

  <!-- MOBILE MENU -->
  <div class="hidden md:hidden bg-navy fixed inset-0 z-50 flex flex-col p-stack-space-lg" id="mobile-menu">
    <div class="flex justify-between items-center mb-stack-space-lg">
      <h2 class="font-headline-md text-headline-md text-gold">Navigation</h2>
      <button class="text-on-surface w-tap-target-min h-tap-target-min flex items-center justify-center" onclick="document.getElementById('mobile-menu').classList.add('hidden')">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
    <nav class="flex flex-col gap-2" id="mobile-nav"></nav>
  </div>

  <!-- TAB NAVIGATION -->
  <nav class="border-b border-gold/20 overflow-x-auto hide-scrollbar bg-surface">
    <div class="flex px-margin-horizontal gap-0 w-max max-w-4xl mx-auto" id="tab-nav">
      <button class="tab-btn active px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="stream">
        <span class="material-symbols-outlined align-middle mr-1 text-sm" aria-hidden="true">newspaper</span><span class="nav-label">The Flow</span>
      </button>
      <button class="tab-btn px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="alpha">
        <span class="material-symbols-outlined align-middle mr-1 text-sm" aria-hidden="true">alpha</span><span class="nav-label">Tactical Bets</span>
      </button>
      <button class="tab-btn px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="capital">
        <span class="material-symbols-outlined align-middle mr-1 text-sm" aria-hidden="true">account_balance</span><span class="nav-label">Capital Flows</span>
      </button>
      <button class="tab-btn px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="contradictions">
        <span class="material-symbols-outlined align-middle mr-1 text-sm" aria-hidden="true">analytics</span><span class="nav-label">Contradictions</span>
      </button>
      <button class="tab-btn px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="about">
        <span class="material-symbols-outlined align-middle mr-1 text-sm" aria-hidden="true">psychology</span><span class="nav-label">About</span>
      </button>
    </div>
  </nav>

  <!-- CTA BANNER -->
  <div class="bg-gold/5 border-b border-gold/30 px-margin-horizontal py-2 flex items-center justify-between flex-wrap gap-2" id="cta-banner">
    <span class="font-metadata-sm text-metadata-sm text-on-surface">Join the Intelligence Network</span>
    <a class="inline-flex items-center gap-1 px-3 py-1.5 bg-primary text-on-primary font-label-xs text-label-xs uppercase tracking-wider hover:bg-primary/90 transition-colors min-h-tap-target-min" href="https://t.me/GazzettaDiKyiv" target="_blank" rel="noopener">
      <span class="material-symbols-outlined text-sm" aria-hidden="true">send</span> Telegram
    </a>
    <button class="text-on-surface-variant hover:text-on-surface ml-2 min-h-tap-target-min min-w-tap-target-min flex items-center justify-center" onclick="this.parentElement.remove();sessionStorage.setItem('cta-dismissed','1')" aria-label="Dismiss">
      <span class="material-symbols-outlined">close</span>
    </button>
  </div>
  <script>
    if (sessionStorage.getItem('cta-dismissed') === '1') {
      var banner = document.getElementById('cta-banner');
      if (banner) banner.remove();
    }
  </script>

  <!-- STREAM TAB -->
  <main class="tab-content active flex-1 max-w-4xl mx-auto w-full px-margin-horizontal py-stack-space-lg" id="view-stream">
    <div class="flex justify-between items-end mb-stack-space-md pb-stack-space-sm border-b-2 border-gold">
      <div>
        <h2 class="font-headline-lg text-headline-lg text-on-surface">The Flow</h2>
        <p class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase tracking-wider">__STORY_COUNT__ stories · __REGIME_STR__</p>
      </div>
      <span class="hidden md:inline border border-outline px-3 py-1 font-label-xs text-label-xs uppercase">Live · __REGIME_STR__</span>
    </div>
    <!-- C1: Client-side filter bar -->
    <div class="flex flex-wrap gap-2 mb-stack-space-sm" id="filter-bar">
      <span class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase self-center mr-1">Filter:</span>
      <button class="filter-pill px-2 py-1 font-label-xs text-label-xs uppercase border border-outline text-on-surface-variant hover:border-gold-accessible hover:text-gold-accessible active" data-filter="all">All</button>
      <span class="self-center text-outline mx-1">|</span>
      <span class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase self-center">Tier:</span>
      <button class="filter-pill px-2 py-1 font-label-xs text-label-xs uppercase border border-outline text-on-surface-variant hover:border-gold-accessible hover:text-gold-accessible" data-filter="tier-BREAKING">BREAKING</button>
      <button class="filter-pill px-2 py-1 font-label-xs text-label-xs uppercase border border-outline text-on-surface-variant hover:border-gold-accessible hover:text-gold-accessible" data-filter="tier-ACTIVE">ACTIVE</button>
      <button class="filter-pill px-2 py-1 font-label-xs text-label-xs uppercase border border-outline text-on-surface-variant hover:border-gold-accessible hover:text-gold-accessible" data-filter="tier-SETTLING">SETTLING</button>
      <span class="self-center text-outline mx-1">|</span>
      <span class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase self-center">Origin:</span>
      <span id="origin-pills" class="flex flex-wrap gap-1"></span>
    </div>
    <!-- TACTICAL RADAR -->
    <details class="radar-card" id="tactical-radar" open>
      <summary class="font-label-xs text-label-xs uppercase tracking-wider cursor-pointer select-none focus-visible-ring" role="button" aria-expanded="true">
        <span class="material-symbols-outlined" style="font-size:16px">radar</span> Tactical Horizon (48-Hour Derivative Radar)
      </summary>
      <div class="radar-grid text-xs mt-3" id="radar-grid"></div>
    </details>
    <!-- C6: THE CROSSHAIR (desktop) -->
    <div class="hidden md:block mb-4" id="crosshair-container">
      <div class="flex items-center gap-2 px-margin-horizontal mb-2">
        <span class="material-symbols-outlined text-gold" style="font-size:18px" aria-hidden="true">scatter_plot</span>
        <span class="font-metadata-sm text-metadata-sm text-gold uppercase tracking-wider">NARRATIVE CROSSHAIR</span>
        <span class="text-xs text-on-surface-variant">Geopolitical Tension x Capital Flow</span>
      </div>
      <div class="relative mx-margin-horizontal" id="crosshair-plot" style="height:280px;background:#FFFFFF;border:1px solid #E5E7EB">
        <div class="absolute inset-0 flex items-center justify-center" style="pointer-events:none">
          <div style="position:absolute;left:0;right:0;top:50%;border-top:1px dashed #E5E7EB"></div>
          <div style="position:absolute;top:0;bottom:0;left:50%;border-left:1px dashed #E5E7EB"></div>
        </div>
        <div id="crosshair-dots" style="position:absolute;inset:0"></div>
        <div style="position:absolute;bottom:6px;left:12px;font-size:10px;color:#444748">Δ Edge (Contrarian Edge) →</div>
        <div style="position:absolute;top:50%;left:-20px;transform:translateY(-50%) rotate(-90deg);font-size:10px;color:#444748">Capital Flow</div>
      </div>
    </div>
    <!-- C2: Δ EDGE LEADERBOARD -->
    <div class="flex flex-col gap-0" id="edge-leaderboard"></div>
    <div class="flex flex-col gap-0" id="story-cards"></div>
  </main>

  <!-- ═══ VIEW 2: ALPHA ═══ -->
  <main class="tab-content flex-1 max-w-4xl mx-auto w-full px-margin-horizontal py-stack-space-lg" id="view-alpha">
    <div class="flex justify-between items-end mb-stack-space-md pb-stack-space-sm border-b-2 border-gold">
      <div>
        <h2 class="font-headline-lg text-headline-lg text-on-surface">Tactical Bets</h2>
        <p class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase tracking-wider">Catalyst-Flow-Trade · Multi-Vector Intelligence</p>
      </div>
      <span class="hidden md:inline border border-outline px-3 py-1 font-label-xs text-label-xs uppercase">Live · __REGIME_STR__</span>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6" id="alpha-grid"></div>
  </main>

  <!-- ═══ VIEW 2: CAPITAL FLOWS ═══ -->
  <main class="tab-content flex-1 max-w-4xl mx-auto w-full px-margin-horizontal py-stack-space-lg" id="view-capital">
    <div class="flex justify-between items-end mb-stack-space-md pb-stack-space-sm border-b-2 border-gold">
      <div>
        <h2 class="font-headline-lg text-headline-lg text-on-surface">Capital Flow Ledger</h2>
        <p class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase tracking-wider">Inter-institutional Transfer Monitoring</p>
      </div>
      <div class="flex gap-3">
        <span class="border border-outline px-3 py-1 font-label-xs text-label-xs uppercase" id="sync-badge">Global Sync: __SYNC_STATUS__</span>
        <span class="border border-outline px-3 py-1 font-label-xs text-label-xs uppercase text-error" id="disc-badge">Discrepancies: __DISC_COUNT__</span>
      </div>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-left" id="capital-table">
        <thead>
          <tr class="border-b border-outline font-label-xs text-label-xs uppercase text-on-surface-variant">
            <th class="py-2 pr-4">Narrative</th>
            <th class="py-2 pr-4">Ticker</th>
            <th class="py-2 pr-4 text-right">Inflow</th>
            <th class="py-2 pr-4 text-right">Outflow</th>
            <th class="py-2 pr-4 text-right">Net</th>
            <th class="py-2 pr-4 text-right">Total</th>
            <th class="py-2 pr-4 text-right">Stories</th>
            <th class="py-2 pr-4 text-center">Disc.</th>
            <th class="py-2 text-right">Δ Edge</th>
          </tr>
        </thead>
        <tbody id="capital-body"></tbody>
      </table>
    </div>
    <details class="mt-stack-space-lg" open>
      <summary class="p-stack-space-md bg-surface-container border-l-2 border-gold font-headline-md text-headline-md text-on-surface">
        <span class="material-symbols-outlined expand-icon text-gold">expand_more</span> Macro Regime
      </summary>
      <div class="details-content px-stack-space-md pb-stack-space-md bg-surface-container border-l-2 border-gold">
        <p class="font-body-md text-body-md text-on-surface-variant mb-2">__REGIME_STR__</p>
        <div class="flex flex-wrap gap-4" id="regime-drivers"></div>
      </div>
    </details>
    <details class="mt-stack-space-sm">
      <summary class="p-stack-space-md bg-surface-container border-l-2 border-gold font-headline-md text-headline-md text-on-surface">
        <span class="material-symbols-outlined expand-icon text-gold">expand_more</span> Cross-Asset Snapshot
      </summary>
      <div class="details-content px-stack-space-md pb-stack-space-md grid grid-cols-2 md:grid-cols-4 gap-stack-space-sm" id="cross-asset-grid"></div>
    </details>
  </main>

  <!-- ═══ VIEW 3: CONTRADICTIONS ═══ -->
  <main class="tab-content flex-1 max-w-4xl mx-auto w-full px-margin-horizontal py-stack-space-lg" id="view-contradictions">
    <div class="flex justify-between items-end mb-stack-space-md pb-stack-space-sm border-b-2 border-gold flex-wrap gap-2">
      <div>
        <h2 class="font-headline-lg text-headline-lg text-on-surface">Contradiction Matrix</h2>
        <p class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase tracking-wider">Media Consensus vs Market Reality</p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <select id="matrix-filter" class="border border-outline bg-surface px-2 py-1 font-label-xs text-label-xs uppercase">
          <option value="all">All Narratives</option>
        </select>
        <select id="matrix-sort" class="border border-outline bg-surface px-2 py-1 font-label-xs text-label-xs uppercase">
          <option value="gap">Highest Δ Edge</option>
          <option value="capital">Largest Capital</option>
          <option value="recent">Most Recent</option>
        </select>
      </div>
    </div>
    <div class="space-y-1" id="matrix-body"></div>
  </main>

  <!-- ═══ VIEW 4: ABOUT / MACRO PERSPECTIVE ═══ -->
  <main class="tab-content flex-1 max-w-4xl mx-auto w-full px-margin-horizontal py-stack-space-lg" id="view-about">
    <div class="mb-stack-space-md pb-stack-space-sm border-b-2 border-gold">
      <h2 class="font-headline-lg text-headline-lg text-on-surface">Sovereign Auditor</h2>
      <p class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase tracking-wider">Epistemological Framework & Invalidation Thresholds</p>
    </div>
    <div class="space-y-stack-space-lg">
      <!-- A1 Methodology Panel -->
      <div class="p-stack-space-md bg-gold/5 border-l-2 border-gold">
        <h3 class="font-headline-sm text-headline-sm text-on-surface mb-2">Methodology & Divergence Scoring</h3>
        <p class="font-body-md text-body-md text-on-surface-variant">This platform measures the Contrarian Edge (Δ) — the structural divergence between financial media reporting and actual institutional capital migration. Dispatches are analyzed and scored based on the magnitude of divergence between qualitative consensus narratives and quantitative asset-class flow volumes; high-Δ Edge signals receive priority visibility on the ledger.</p>
      </div>
      <!-- A2 Who We Are -->
      <div class="p-stack-space-md bg-surface-container border-l-2 border-gold">
        <h3 class="font-headline-sm text-headline-sm text-on-surface mb-2">Who We Are</h3>
        <p class="font-body-md text-body-md text-on-surface-variant">La Gazzetta di Kyiv is a narrative-capital intelligence terminal founded by <strong>Alexander Solianin</strong> (CEO & Chief Editor) and <strong>Alessio Stocchi</strong> (CTO). We track the Contrarian Edge (Δ) — the structural divergence between what financial media reports and what institutional capital actually does. Our mission: supply every underdog with vivid investment and trading opportunities to exploit, and get out from the debt and currency depreciation vicious cycle.</p>
        <p class="font-body-md text-body-md text-on-surface-variant mt-2">Contact: <a class="text-gold-accessible hover:text-gold" href="https://t.me/LaGazzettadiKyiv">@LaGazzettadiKyiv on Telegram</a></p>
      </div>
      <details open>
        <summary class="font-headline-md text-headline-md text-on-surface mb-stack-space-sm flex items-center gap-1">
          <span class="material-symbols-outlined expand-icon text-gold">expand_more</span> Narrative Lifecycle Phases
        </summary>
        <div class="details-content">
        <div class="overflow-x-auto">
          <table class="w-full text-left" id="phase-table">
            <thead>
              <tr class="border-b border-outline font-label-xs text-label-xs uppercase text-on-surface-variant">
                <th class="py-2 pr-4">Narrative</th>
                <th class="py-2 pr-4">Ticker</th>
                <th class="py-2 pr-4 text-right">Δ Edge</th>
                <th class="py-2 pr-4">Phase</th>
                <th class="py-2">Invalidation Threshold</th>
              </tr>
            </thead>
            <tbody id="phase-body"></tbody>
          </table>
        </div>
      </div>
        </div>
      </details>
      <details class="mt-stack-space-md" open>
        <summary class="p-stack-space-md bg-surface-container border-l-2 border-crimson font-headline-md text-headline-md text-on-surface">
          <span class="material-symbols-outlined expand-icon text-crimson">expand_more</span> Reflexivity Alert
        </summary>
        <div class="details-content px-stack-space-md pb-stack-space-md bg-surface-container border-l-2 border-crimson">
          <p class="font-body-md text-body-md text-on-surface-variant">When positioning itself becomes the primary fundamental driver, narratives enter self-reinforcing feedback loops. The Invalidation Threshold Tracker identifies the exact price level where each macro thesis is proven wrong by price action.</p>
          <p class="font-body-md text-body-md text-on-surface-variant mt-2">Current regime: <strong class="text-crimson">__REGIME_STR__</strong></p>
        </div>
      </details>
    </div>
  </main>

  <!-- FOOTER -->
  <footer class="bg-surface-container border-t border-gold w-full flex flex-col items-center py-stack-space-lg px-margin-horizontal text-center gap-stack-space-sm mb-16 md:mb-0">
    <span class="font-label-xs text-label-xs text-gold-dim uppercase tracking-widest">Diplomatic Ledger v30.2</span>
    <div class="flex flex-wrap justify-center gap-x-6 gap-y-2">
      <a class="font-metadata-sm text-metadata-sm text-on-surface-variant hover:text-on-surface cursor-pointer" onclick="switchTab('about')">About</a>
      <a class="font-metadata-sm text-metadata-sm text-on-surface-variant hover:text-on-surface" href="https://t.me/GazzettaDiKyiv">Telegram</a>
      <a class="font-metadata-sm text-metadata-sm text-on-surface-variant hover:text-on-surface" href="https://www.reddit.com/r/LaGazzettadiKyiv/">Reddit</a>
    </div>
    <p class="font-label-xs text-label-xs text-on-surface-variant mt-2">Built __BUILD_TIME__</p>
  </footer>

  <!-- MOBILE BOTTOM NAV -->
  <nav class="md:hidden flex justify-around items-center bg-surface border-t border-gold px-margin-horizontal pb-2 pt-1 fixed bottom-0 left-0 w-full z-30">
    <button onclick="switchTab('stream')" class="flex flex-col items-center text-on-surface pt-1 w-tap-target-min">
      <span class="material-symbols-outlined text-gold" style="font-variation-settings:'FILL'1';">newspaper</span>
      <span class="font-label-xs text-label-xs uppercase">Flow</span>
    </button>
    <button onclick="switchTab('alpha')" class="flex flex-col items-center text-on-surface-variant pt-1 w-tap-target-min">
      <span class="material-symbols-outlined">alpha</span>
      <span class="font-label-xs text-label-xs uppercase">Bets</span>
    </button>
    <button onclick="switchTab('capital')" class="flex flex-col items-center text-on-surface-variant pt-1 w-tap-target-min">
      <span class="material-symbols-outlined">account_balance</span>
      <span class="font-label-xs text-label-xs uppercase">Capital</span>
    </button>
    <button onclick="switchTab('contradictions')" class="flex flex-col items-center text-on-surface-variant pt-1 w-tap-target-min">
      <span class="material-symbols-outlined">analytics</span>
      <span class="font-label-xs text-label-xs uppercase">Matrix</span>
    </button>
    <button onclick="switchTab('about')" class="flex flex-col items-center text-on-surface-variant pt-1 w-tap-target-min">
      <span class="material-symbols-outlined">psychology</span>
      <span class="font-label-xs text-label-xs uppercase">About</span>
    </button>
  </nav>

</div><!-- /md:ml-72 -->

<!-- ═══ DATA INJECTION ═══ -->
<script>
const NARRATIVES = __NARRATIVES_JSON__;
const STORIES = __STORIES_JSON__;
const CAPITAL_FLOWS = __CAPITAL_JSON__;
const CROSS_ASSET = __CROSS_ASSET_JSON__;
const REGIME = __REGIME_JSON__;
const REGIME_DRIVERS = __REGIME_DRIVERS_JSON__;
const BUILD_TIME = "__BUILD_TIME__";
const DERIVATIVES = __DERIVATIVES_JSON__;

// ── TACTICAL RADAR RENDERER ──
function renderRadar(){
  var grid = document.getElementById('radar-grid');
  if (!grid || !DERIVATIVES || !DERIVATIVES.crypto) return;
  var d = DERIVATIVES;

  function badgeClass(code){
    if (['coiled_spring','local_top_risk','contrarian_buy'].indexOf(code)>=0) return 'badge-alert';
    if (['defensive_posture','cooling_off'].indexOf(code)>=0) return 'badge-warn';
    return 'badge-safe';
  }
  function cellClass(code){
    if (['coiled_spring','local_top_risk','contrarian_buy'].indexOf(code)>=0) return 'sqz';
    if (['defensive_posture','cooling_off'].indexOf(code)>=0) return 'warn';
    return 'safe';
  }
  function card(symbol, data){
    return '<div class=\"radar-cell '+cellClass(data.code)+'\">' +
      '<div class=\"flex justify-between items-center mb-1\">' +
        '<span class=\"font-bold text-on-surface\" data-ticker=\"'+symbol+'\">'+symbol+' Futures</span>' +
        '<span class=\"'+badgeClass(data.code)+'\">'+data.condition+'</span>' +
      '</div>' +
      '<p class=\"text-on-surface-variant leading-relaxed\">'+data.projection+'</p>' +
    '</div>';
  }
  var html = '';
  var crypto = d.crypto || {};
  if (crypto.BTC) html += card('BTC', crypto.BTC);
  if (crypto.ETH) html += card('ETH', crypto.ETH);
  if (d.equities) html += card('Global Equities', d.equities);
  grid.innerHTML = html;
  // Auto-collapse Tactical Radar when all signals are EQUILIBRIUM
  var allEquilibrium = (!d.crypto || !d.crypto.BTC || d.crypto.BTC.condition === 'EQUILIBRIUM') &&
                       (!d.crypto || !d.crypto.ETH || d.crypto.ETH.condition === 'EQUILIBRIUM') &&
                       (!d.equities || d.equities.condition === 'EQUILIBRIUM');
  var details = document.getElementById('tactical-radar');
  if (details && allEquilibrium) {
    details.open = false;
    // Add a compact status line when collapsed
    var summary = details.querySelector('summary');
    if (summary) summary.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px">check_circle</span> Tactical Horizon: All Markets Equilibrium' +
      ' <span class="text-on-surface-variant text-xs">(no signal — click to expand)</span>';
  }
  // Re-wire glossary tooltips for new elements
  if (window._wireGlossary) window._wireGlossary();
}
setTimeout(renderRadar, 100);
</script>

<!-- ═══ RENDER LOGIC ═══ -->
<script>
(function() {
  // ── TAB SWITCHING ──
  window.switchTab = function(name) {
    document.querySelectorAll('.tab-content').forEach(function(v){v.classList.remove('active')});
    document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active')});
    var view = document.getElementById('view-' + name);
    if (view) view.classList.add('active');
    var btns = document.querySelectorAll('[data-tab="' + name + '"]');
    btns.forEach(function(b){b.classList.add('active')});
    if (name !== 'stream') document.getElementById('mobile-menu').classList.add('hidden');
    window.location.hash = name;
    // Update mobile bottom nav
    document.querySelectorAll('#view-stream ~ nav button').forEach(function(b,i){
      var tabs = ['stream','alpha','capital','contradictions','about'];
      if (tabs[i] === name) { b.classList.add('text-gold'); b.querySelector('span').style.fontVariationSettings = "'FILL' 1"; }
      else { b.classList.remove('text-gold'); }
    });
  };

  // ── TAB CLICK HANDLER ──
  document.getElementById('tab-nav').addEventListener('click', function(e) {
    var btn = e.target.closest('[data-tab]');
    if (!btn) return;
    switchTab(btn.getAttribute('data-tab'));
  });

  // ── HASH ROUTING ──
  var hash = window.location.hash.replace('#','');
  if (hash && ['stream','alpha','capital','contradictions','about'].indexOf(hash) >= 0) switchTab(hash);

  // ── RENDER SIDEBAR ──
  var sidebarNav = document.getElementById('sidebar-nav');
  var sidebarVuln = document.getElementById('sidebar-vuln');
  if (sidebarNav && NARRATIVES.length) {
    sidebarNav.innerHTML = NARRATIVES.map(function(n, i) {
      var active = i === 0 ? ' text-gold-accessible border-b-2 border-gold-accessible' : ' text-on-surface-variant hover:text-gold-accessible';
      return '<a href="#" class="flex items-center gap-3 px-3 py-2 font-metadata-sm text-metadata-sm uppercase tracking-wider' + active + '" data-ticker="' + n.ticker + '" data-narrative="' + n.id + '">' +
        '<span class="text-lg font-headline-md">' + n.ticker + '</span>' +
        '<span>' + n.title + '</span>' +
        '<span class="ml-auto text-gold-accessible text-xs">' + (n.capital_b >= 1 ? n.capital_b.toFixed(1)+'B' : n.capital_b > 0 ? (n.capital_b*1000).toFixed(0)+'M' : 'N/A') + '</span>' +
        '</a>';
    }).join('');
    var sorted = NARRATIVES.slice().sort(function(a,b){return b.gap - a.gap;}).slice(0,4);
    sidebarVuln.innerHTML = sorted.map(function(n){
      var pct = Math.min(n.gap, 100);
      return '<div><div class="flex justify-between text-on-primary mb-1"><span class="font-metadata-sm text-xs">'+n.title+'</span><span class="text-gold text-xs">'+n.gap.toFixed(0)+'</span></div>' +
        '<div class="meter-container"><div class="meter-fill-neg" style="width:'+pct+'%;"></div></div></div>';
    }).join('');
  }

  // ── MOBILE NAV ──
  var mobileNav = document.getElementById('mobile-nav');
  if (mobileNav && NARRATIVES.length) {
    mobileNav.innerHTML = NARRATIVES.map(function(n){
      return '<a href="#" class="flex items-center gap-3 px-4 py-3 text-on-primary hover:bg-primary-container font-metadata-sm text-metadata-sm uppercase tracking-wider" onclick="document.getElementById(\'mobile-menu\').classList.add(\'hidden\')">' +
        '<span class="material-symbols-outlined text-gold">'+n.icon+'</span>' +
        '<span>'+n.title+'</span>' +
        '<span class="ml-auto text-gold-accessible text-xs">'+n.count+'</span></a>';
    }).join('');
  }

  // ── VIEW 1: STREAM CARDS (C3: ZONED + C4: DECAY + C5: SOURCE TIERS) ──
  var cardsEl = document.getElementById('story-cards');
  if (cardsEl && STORIES.length) {
    var streamStories = STORIES.filter(function(s){ return (s.contradiction_gap || 0) >= 15; });
    // C3: tier arrays
    var breakingStories = streamStories.filter(function(s){ return (s.contradiction_gap || 0) > 50; });
    var activeStories   = streamStories.filter(function(s){ var g = s.contradiction_gap || 0; return g >= 20 && g <= 50; });
    var settlingStories = streamStories.filter(function(s){ return (s.contradiction_gap || 0) < 20; });

    function buildCard(s, tierOverride, openDetails) {
      var gap = s.contradiction_gap || 0;
      var tier = s.tier || '';
      var isDiv = gap >= 40;
      var tagClass = isDiv ? 'bg-error-container/20 text-error' : 'bg-surface-container text-on-surface-variant';
      var label = isDiv ? 'DIVERGENT' : 'CONVERGENT';
      var gapPct = Math.min(gap, 100);
      var capVol = s.capital_volume_usd || 0;
      var capB = capVol / 1e9;
      var capStr = capB >= 1 ? capB.toFixed(1)+'B' : (capB*1000).toFixed(0)+'M';
      var timeAgo = '';
      if (s.generated_at) {
        var d = new Date(s.generated_at);
        var h = Math.floor((new Date() - d) / 3600000);
        timeAgo = h <= 0 ? 'Just now' : h + 'H AGO';
      }
      // C4: Decay Clock — 12h half-life from generated_at
      var halfLife = 12;
      var decayPct = h !== undefined ? Math.max(0, Math.min(100, 100 - (h / halfLife) * 100)) : 100;
      var decayRemaining = h !== undefined ? Math.max(0, halfLife - h) : halfLife;
      var decayClass = decayPct > 50 ? 'decay-fresh' : decayPct > 20 ? 'decay-active' : 'decay-critical';
      var decayLabelClass = decayPct <= 20 ? ' decay-label-critical' : '';
      var decayHtml = decayRemaining <= 0
        ? '<div class="decay-meter"><div class="decay-fill decay-critical" style="width:4px"></div></div><div class="decay-label decay-label-critical">EDGE EXPIRED</div>'
        : '<div class="decay-meter"><div class="decay-fill ' + decayClass + '" style="width:' + decayPct.toFixed(0) + '%"></div></div><div class="decay-label' + decayLabelClass + '">EDGE DECAY: ~' + decayRemaining.toFixed(0) + 'H REMAINING</div>';
      // C5: Source provenance tiers
      var tier1Sources = ['BLOOMBERG','FT','ECB','REUTERS','WSJ'];
      var sourceTier = (s.feed_source && tier1Sources.indexOf(s.feed_source.toUpperCase()) >= 0) ? 'TIER 1' : 'TIER 2';
      var sourceTierBadge = s.feed_source ? '<span class="text-xs px-1 ml-1 border border-gold/30 text-gold-dim">' + sourceTier + '</span>' : '';
      var isHighGap = gap >= 70;
      // Contradiction Alert: Δ EDGE ≥ 80
      var isAlert = s.alert === true;
      var alertClass = isAlert ? ' contradiction-alert' : '';
      var alertBadge = isAlert ? '<span class="contradiction-alert-badge">CONTRADICTION ALERT</span>' : '';
      // Trade setup line for collapsed state
      var tt = s.trade_thesis || {};
      var hasTrade = tt.direction && tt.direction !== 'NEUTRAL';
      // Paywall: truncate trade setup for free-tier users
      var userTier = (function(){ try { return localStorage.getItem('gazzetta_tier') || 'free'; } catch(e) { return 'free'; } })();
      var isPaidUser = userTier === 'pro' || userTier === 'institutional';
      var tradeLine = hasTrade
        ? (isPaidUser
            ? '<span class="ticker-mono">' + (tt.direction||'').toUpperCase() + ' ' + (tt.primary_ticker||tt.ticker||'') + '</span>' +
              ' <span class="price-mono">@ ' + (tt.limit_entry_price||tt.entry_zone||'') + '</span>' +
              ' <span class="text-on-surface-variant">| Stop:</span> <span class="price-mono">' + (tt.stop_loss||'N/A') + '</span>' +
              ' <span class="text-on-surface-variant">| Target:</span> <span class="price-mono">' + (tt.take_profit||'N/A') + '</span>' +
              (tt.portfolio_allocation_pct ? ' <span class="text-emerald">[' + tt.portfolio_allocation_pct + ']</span>' : '')
            : (isHighGap
                ? '<span class="ticker-mono">' + (tt.direction||'').toUpperCase() + ' ' + (tt.primary_ticker||tt.ticker||'') + '</span>' +
                  ' <span class="text-crimson font-bold">Δ EDGE ' + gap.toFixed(0) + ' — </span>' +
                  '<a href="/upgrade" class="text-gold underline">Upgrade to Pro to unlock trade setup</a>'
                : '<span class="ticker-mono">' + (tt.direction||'').toUpperCase() + ' ' + (tt.primary_ticker||tt.ticker||'') + '</span>' +
                  ' <span class="text-on-surface-variant">(premium)</span>')
          )
        : '<span class="text-on-surface-variant">No active thesis</span>';
      // Source line — compressed institutional density
      var sourceLine = (s.feed_source
        ? '<span class="text-gold-dim">' + sourceTier + '</span> via <span class="text-on-surface-variant">' + (s.feed_source||'').toUpperCase() + '</span>'
        : '<span class="text-on-surface-variant">NO SOURCE</span>')
        + ' <span class="text-on-surface-variant">·</span> <span class="text-gold-accessible">' + timeAgo + '</span>'
        + ' <span class="text-on-surface-variant">·</span> <span class="gap-score text-crimson">Δ EDGE ' + gap.toFixed(0) + '</span>';

      // Build safe data attributes for share
      var safeHeadline = (s.headline||'Untitled').replace(/"/g, '&quot;');
      var safeDirection = tt.direction || '';
      var safeTicker = tt.primary_ticker || tt.ticker || '';
      var safeEntry = tt.limit_entry_price || tt.entry_zone || '';
      return '<article data-story-id="' + (s.story_id || '') + '" data-source-feed="' + (s.feed_source || '') + '" data-tier="' + (tierOverride || tier || '') + '" data-gap-high="' + (isHighGap ? 'true' : 'false') + '" data-alert="' + (isAlert ? 'true' : 'false') + '" data-headline="' + safeHeadline + '" data-capital="' + capStr + '" data-gap="' + gap.toFixed(0) + '" data-direction="' + safeDirection + '" data-ticker="' + safeTicker + '" data-entry="' + safeEntry + '" class="py-2 border-b border-[#1E293B]' + alertClass + '">' +
        '<div class="pl-3">' + decayHtml +
        (isAlert ? '<div class="mb-1">' + alertBadge + '</div>' : '') +
        // LINE 1: Source + time + Δ EDGE
        '<div class="font-label-xs text-label-xs mb-1">' + sourceLine + '</div>' +
        // LINE 2: Headline
        '<h3 class="font-headline-md text-headline-md text-on-surface leading-tight mb-1">'+(s.headline||'Untitled')+'</h3>' +
        // SHILLER LAYER: Media Says / Capital Says — always visible for TIER 1 & 2
        (gap >= 50
          ? '<div class="shiller-surface mb-1 grid grid-cols-2 gap-1 text-xs leading-snug">' +
            '<div class="text-on-surface-variant truncate"><span class="uppercase tracking-wider text-[10px]">Media</span> ' + ((s.they_say||'').substring(0,120)) + '</div>' +
            '<div class="text-on-surface truncate"><span class="uppercase tracking-wider text-[10px] text-gold-dim">Capital</span> ' + ((s.reality||'').substring(0,120)) + '</div>' +
            '</div>'
          : '') +
        // LINE 3: Trade setup + action buttons
        '<div class="flex items-center justify-between flex-wrap gap-2">' +
          '<div class="font-label-xs text-label-xs">' + tradeLine + '</div>' +
          '<div class="flex items-center gap-2">' +
            '<button type="button" onclick="shareStory(this)" class="text-[#747878] hover:text-on-surface p-1" aria-label="Share intelligence setup"><span class="material-symbols-outlined text-[16px]" aria-hidden="true">share</span></button>' +
            '<button class="text-xs text-on-surface-variant hover:text-gold-accessible card-expand-btn" onclick="event.stopPropagation();var d=this.closest(\'article\').querySelector(\'.card-drawer\');if(d){d.open=!d.open;this.querySelector(\'.expand-icon\').style.transform=d.open?\'rotate(180deg)\' : \'\'}" title="Expand"><span class="material-symbols-outlined expand-icon" style="font-size:16px">unfold_more</span></button>' +
          '</div>' +
        '</div>' +
        // DRAWER: Full dispatch (hidden by default)
        '<details class="card-drawer mt-2">' +
          '<summary class="hidden"></summary>' +
          '<div class="details-content mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">' +
            '<div class="bg-surface-container-high p-2 border-l border-outline-variant">' +
              '<h4 class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase mb-1">Media Consensus</h4>' +
              '<p class="font-body-md text-body-md text-on-surface-variant">'+(s.they_say||'No data.')+'</p>' +
            '</div>' +
            '<div class="bg-gold/5 p-2 border-l border-gold">' +
              '<h4 class="font-metadata-sm text-metadata-sm text-gold-dim uppercase mb-1">Market Reality</h4>' +
              '<p class="font-body-md text-body-md text-on-surface">'+(s.reality||'No data.')+'</p>' +
            '</div>' +
            // Extra detail: capital volume + narrative context
            '<div class="col-span-full flex items-center gap-3 text-xs text-on-surface-variant mt-1">' +
              '<span>Capital: <span class="capital-num text-on-surface">' + capStr + '</span></span>' +
              (tier ? '<span>· Tier: <span class="text-crimson">' + tier + '</span></span>' : '') +
              '<span>· Narrative: <span class="text-on-surface">' + (s._container_title||'') + '</span></span>' +
            '</div>' +
          '</div>' +
        '</details>' +
        '</div></article>';
    }

    var allCardsHtml = '';
    allCardsHtml += breakingStories.length ? '<div class="zone-header breaking-zone mb-3"><div class="flex items-center gap-2 px-margin-horizontal py-2" style="background:#F9FAFB;border-left:4px solid #8B0000"><span class="material-symbols-outlined" style="color:#7F1D1D;font-size:20px">warning</span><span class="font-metadata-sm text-metadata-sm uppercase tracking-wider" style="color:#7F1D1D">BREAKING ZONE — HIGH DIVERGENCE (' + breakingStories.length + ' SIGNALS)</span></div></div>' + breakingStories.map(function(s){ return buildCard(s,'BREAKING',true); }).join('') : '';
    allCardsHtml += activeStories.length ? '<div class="zone-header active-zone mb-3 mt-4"><div class="flex items-center gap-2 px-margin-horizontal py-2" style="background:#F9FAFB;border-left:4px solid #D4AF37"><span class="material-symbols-outlined" style="color:#D4AF37;font-size:20px">trending_up</span><span class="font-metadata-sm text-metadata-sm uppercase tracking-wider" style="color:#D4AF37">ACTIVE SIGNALS (' + activeStories.length + ' STORIES)</span></div></div>' + activeStories.map(function(s){ return buildCard(s,'ACTIVE',false); }).join('') : '';
    allCardsHtml += settlingStories.length ? '<div class="zone-header settling-zone mb-3 mt-4"><div class="flex items-center gap-2 px-margin-horizontal py-2" style="background:#F9FAFB;border-left:4px solid #444748"><span class="material-symbols-outlined" style="color:#444748;font-size:20px">check_circle</span><span class="font-metadata-sm text-metadata-sm uppercase tracking-wider" style="color:#747878">SETTLING NOISE (' + settlingStories.length + ' STORIES)</span></div></div>' + settlingStories.map(function(s){ return buildCard(s,'SETTLING',false); }).join('') : '<div class="zone-header settling-zone mb-3 mt-4"><div class="flex items-center gap-2 px-margin-horizontal py-2" style="background:#F9FAFB;border-left:4px solid #444748"><span class="material-symbols-outlined" style="color:#444748;font-size:20px">check_circle</span><span class="font-metadata-sm text-metadata-sm uppercase tracking-wider" style="color:#747878">SETTLING NOISE (0 STORIES) · No settling signals at this time</span></div></div>';
    cardsEl.innerHTML = allCardsHtml;

    injectSourceAttribution();
    renderLeaderboard();
    renderCrosshair();
  }

  function injectSourceAttribution() {
    var articles = document.querySelectorAll('article[data-story-id]');
    for (var i = 0; i < articles.length; i++) {
      var card = articles[i];
      if (card.querySelector('.source-attribution-footer')) continue;
      var sourceData = card.getAttribute('data-source-feed');
      if (!sourceData || sourceData.trim() === '') continue;
      var footer = document.createElement('div');
      footer.className = 'source-attribution-footer mt-4 pt-2 border-t border-[#1E293B] flex items-center justify-between text-xs text-[#747878] font-mono tracking-tight';
      footer.innerHTML = '<div class="flex items-center justify-between w-full p-2 bg-[#F9FAFB] rounded-b"><div class="flex items-center gap-1.5"><span class="material-symbols-outlined text-[14px] text-[#747878]" aria-hidden="true">database</span><span class="font-mono text-on-surface-variant">' + sourceData.charAt(0).toUpperCase() + sourceData.slice(1).trim() + '</span></div><div class="flex items-center gap-2"><span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-700 border border-emerald-500/40" title="Algorithmically verified via core pipeline">Verified</span></div></div>';
      card.appendChild(footer);
    }
  }

  // ── C6: CROSSHAIR RENDER ──
  function renderCrosshair() {
    var plot = document.getElementById('crosshair-plot');
    var dotsEl = document.getElementById('crosshair-dots');
    if (!plot || !dotsEl) return;

    // Aggregate narratives from FLOWS data (or stories)
    var narratives = [];
    var seen = {};
    for (var i = 0; i < STORIES.length; i++) {
      var s = STORIES[i];
      var nid = s.container || s._container_id || '';
      if (!nid || seen[nid]) continue;
      seen[nid] = true;
      var gap = s.contradiction_gap || 0;
      var cap = s.capital_volume_usd || 0;
      if (gap > 0 || cap > 0) {
        narratives.push({ id: nid, title: s._container_title || nid, gap: gap, capital: cap });
      }
    }
    if (narratives.length < 2) return;

    var maxGap = Math.max.apply(null, narratives.map(function(n){ return n.gap; })) || 100;
    var maxCap = Math.max.apply(null, narratives.map(function(n){ return n.capital; })) || 1e9;

    dotsEl.innerHTML = narratives.map(function(n){
      var left = (n.gap / Math.max(maxGap, 1)) * 100;
      var bottom = (n.capital / Math.max(maxCap, 1)) * 100;
      var size = Math.max(8, Math.min(24, (n.capital / 1e9) * 8));
      var color = n.gap >= 50 ? '#8B0000' : n.gap >= 30 ? '#D4AF37' : '#444748';
      return '<div title="' + n.title + ' | Δ EDGE ' + n.gap.toFixed(0) + ' | $' + (n.capital/1e9).toFixed(1) + 'B" style="position:absolute;left:' + left.toFixed(1) + '%;bottom:' + bottom.toFixed(1) + '%;width:' + size + 'px;height:' + size + 'px;border-radius:50%;background:' + color + ';transform:translate(-50%,50%);cursor:pointer;opacity:0.85;transition:opacity 0.2s" onmouseenter="this.style.opacity=1" onmouseleave="this.style.opacity=0.85"></div>';
    }).join('');
  }

  // ── C2: LEADERBOARD RENDER ──
  function renderLeaderboard() {
    var board = document.getElementById('edge-leaderboard');
    if (!board) return;

    // Build NARRATIVES lookups for NMC capital + narrative phase
    var narrCapLookup = {};
    var narrPhaseLookup = {};
    for (var ni = 0; ni < NARRATIVES.length; ni++) {
      var nd = NARRATIVES[ni];
      narrCapLookup[nd.id] = nd.capital_b || 0;
      narrPhaseLookup[nd.id] = nd.phase || '';
    }

    // Aggregate top narratives by EDGE from stories
    var narrMap = {};
    for (var i = 0; i < STORIES.length; i++) {
      var s = STORIES[i];
      var nid = s.container || s._container_id || '';
      if (!nid) continue;
      if (!narrMap[nid]) narrMap[nid] = { id: nid, title: s._container_title || nid, ticker: (s.affected_tickers||[])[0]||nid, gaps: [], caps: [] };
      narrMap[nid].gaps.push(s.contradiction_gap || 0);
      // Caps now come from NARRATIVES (NMC-augmented), not story-level capital_volume_usd
    }
    var ranked = [];
    for (var k in narrMap) {
      var m = narrMap[k];
      m.gaps.sort(function(a,b){ return b-a; });
      m.avgGap = m.gaps.length ? m.gaps[0] : 0;
      m.totalCap = (narrCapLookup[m.id] || 0) * 1e9;  // NMC-augmented (stored in billions, convert to raw USD for formatting)
      ranked.push(m);
    }
    ranked.sort(function(a,b){ return b.avgGap - a.avgGap; });
    var top5 = ranked.slice(0, 5);

    board.innerHTML = '<div class="px-margin-horizontal mb-3"><div class="flex items-center gap-2 mb-2"><span class="material-symbols-outlined text-gold" style="font-size:18px" aria-hidden="true">leaderboard</span><span class="font-metadata-sm text-metadata-sm text-gold uppercase tracking-wider">Δ EDGE LEADERBOARD</span><span class="cursor-help text-[12px] text-[#747878] hover:text-on-surface font-sans" title="Δ Edge (0-100): The Contrarian Edge — quantifies the absolute mathematical divergence between corporate media consensus and active structural capital flows. Higher means extreme divergence with greater alpha potential.">ⓘ</span><span class="text-xs text-crimson uppercase">LIVE</span></div>' +
      '<div class="flex gap-2 overflow-x-auto hide-scrollbar">' +
        top5.map(function(n, i){
          var barColor = n.avgGap >= 60 ? '#8B0000' : n.avgGap >= 30 ? '#D4AF37' : '#444748';
          var arrow = n.avgGap >= 50 ? String.fromCharCode(8599) : String.fromCharCode(8594);
          var capB = n.totalCap / 1e9;
          var capStr = capB >= 1 ? capB.toFixed(1)+'B' : (capB*1000).toFixed(0)+'M';
          // Phase badge — narrative lifecycle label
          var phaseLabel = narrPhaseLookup[n.id] || '';
          var phaseBadge = phaseLabel ? '<span class="text-[9px] uppercase tracking-wider" style="color:' + barColor + '">' + phaseLabel + '</span>' : '';
          return '<div class="flex-shrink-0 min-w-[140px] bg-surface-container-high p-3" style="border-left:2px solid ' + barColor + '">' +
            '<div class="flex justify-between items-start mb-1">' +
              '<span class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase">' + (n.title||'').length > 18 ? (n.title||'').substring(0,18) + '...' : (n.title||'') + '</span>' +
              '<span class="text-xs text-on-surface-variant">#' + (i+1) + '</span>' +
            '</div>' +
            '<div class="font-headline-md text-headline-md" style="color:' + barColor + '">Δ ' + n.avgGap.toFixed(0) + '</div>' +
            // Phase 1: Δ EDGE divergence bar — visual spread indicator
            '<div style="width:100%;height:4px;background:#E3E2E0;margin-top:4px;margin-bottom:2px">' +
              '<div style="width:' + Math.min(n.avgGap, 100).toFixed(0) + '%;height:100%;background:' + barColor + '"></div>' +
            '</div>' +
            // Phase badge
            '<div class="mb-1">' + phaseBadge + '</div>' +
            '<div class="flex items-center justify-between mt-1">' +
              '<span class="text-xs text-gold-accessible">' + n.ticker + ' ' + arrow + '</span>' +
              '<span class="text-xs text-on-surface-variant">' + capStr + '</span>' +
            '</div>' +
          '</div>';
        }).join('') +
      '</div></div>';
  }

  // ── VIEW 2: ALPHA BOARD (CFT Blocks) ──
  function renderAlphaView() {
    var grid = document.getElementById('alpha-grid');
    if (!grid || !NARRATIVES.length) return;

    // Only show narratives with active CFT data
    var active = NARRATIVES.filter(function(n) { return n.cft !== null && n.cft !== undefined; });

    if (!active.length) {
      grid.innerHTML = '<div class=\"col-span-full text-center py-12\"><p class=\"font-headline-md text-headline-md text-on-surface-variant\">No active catalysts</p><p class=\"font-metadata-sm text-metadata-sm text-on-surface-variant mt-2\">Waiting for contradiction gaps above threshold</p></div>';
      return;
    }

    grid.innerHTML = active.map(function(n) {
      var c = n.cft;
      var gap = c.catalyst_gap || 0;
      var gapColor = gap >= 65 ? 'bg-crimson' : (gap >= 40 ? 'bg-gold' : 'bg-gold-dim');

      // Trade pills
      var tickerPills = (c.affected_tickers || []).map(function(t) {
        return '<span class=\"px-2 py-0.5 font-label-xs text-label-xs uppercase tracking-wider border border-outline text-on-surface-variant\">' + t + '</span>';
      }).join('');

      var assetPills = (c.affected_asset_classes || []).map(function(a) {
        return '<span class=\"px-2 py-0.5 font-label-xs text-label-xs uppercase tracking-wider bg-surface-container text-on-surface-variant\">' + a + '</span>';
      }).join('');

      // Domino pills (threshold 0.30)
      var dominoHtml = '';
      if (c.domino && c.domino.length) {
        dominoHtml = '<div class=\"mt-3 flex flex-wrap gap-1.5 items-center\">' +
          '<span class=\"font-label-xs text-label-xs text-on-surface-variant uppercase mr-1\">Spillover:</span>' +
          c.domino.map(function(d) {
            return '<button class="domino-pill px-2 py-0.5 font-label-xs text-label-xs uppercase tracking-wider border border-gold/30 text-gold-accessible hover:border-gold hover:bg-gold/5 cursor-pointer transition-colors" data-target="cft-' + d.narrative_id + '">' + d.title + ' <span class="text-on-surface-variant">' + d.score.toFixed(2) + '</span></button>';
          }).join('') +
        '</div>';
      }

      return '<div class=\"bg-surface/80 backdrop-blur-sm border border-gold/20 border-l-2 border-l-gold p-stack-space-md\" id=\"cft-' + n.id + '\">' +
        // Narrative header
        '<div class=\"flex justify-between items-start mb-3\">' +
          '<div>' +
            '<h3 class=\"font-headline-md text-headline-md text-on-surface\">' + n.title + '</h3>' +
            '<span class=\"font-metadata-sm text-metadata-sm text-on-surface-variant uppercase\">' + n.count + ' stories · ' + (c.status || n.phase) + '</span>' +
          '</div>' +
          '<span class=\"px-2 py-0.5 border font-label-xs text-label-xs uppercase ' + (gap >= 65 ? 'border-crimson text-crimson' : 'border-gold text-gold-accessible') + '\">Δ EDGE ' + gap + '</span>' +
        '</div>' +

        // Gap meter bar
        '<div class=\"w-full h-1 bg-surface-container mb-stack-space-sm\"><div class=\"h-1 ' + gapColor + '\" style=\"width:' + Math.min(gap, 100) + '%;\"></div></div>' +

        // Three-column grid: Catalyst | Flow | Trade
        '<div class=\"grid grid-cols-1 sm:grid-cols-3 gap-stack-space-sm mt-stack-space-sm\">' +
          // CATALYST
          '<div>' +
            '<span class=\"font-label-xs text-label-xs text-on-surface-variant uppercase tracking-wider\">Catalyst</span>' +
            '<p class=\"font-body-md text-body-md text-on-surface mt-1 leading-snug\">' + (c.catalyst_text || 'Awaiting narrative acceleration event.') + '</p>' +
          '</div>' +
          // FLOW
          '<div>' +
            '<span class=\"font-label-xs text-label-xs text-on-surface-variant uppercase tracking-wider\">Flow</span>' +
            '<p class=\"font-body-md text-body-md text-on-surface mt-1 leading-snug\">' + (c.flow_text || 'Capital baseline established. Monitoring movements.') + '</p>' +
            (c.capital_usd > 0 ? '<p class=\"font-headline-md text-headline-md text-gold-dim mt-0.5\">' + c.capital_fmt + ' at stake</p>' : '') +
          '</div>' +
          // TRADE
          '<div>' +
            '<span class=\"font-label-xs text-label-xs text-on-surface-variant uppercase tracking-wider\">Trade Vectors</span>' +
            '<div class=\"flex flex-wrap gap-1 mt-1\">' + (tickerPills || '<span class=\"font-label-xs text-on-surface-variant\">—</span>') + '</div>' +
            '<div class=\"flex flex-wrap gap-1 mt-1\">' + (assetPills || '') + '</div>' +
          '</div>' +
        '</div>' +

        // Domino spillover
        dominoHtml +

      '</div>';
    }).join('');
  }

  // Auto-render Alpha view on first load if hash routes there; always render when tab switches
  var origSwitchTab = window.switchTab;
  window.switchTab = function(name) {
    origSwitchTab(name);
    if (name === 'alpha') renderAlphaView();
  };

  // Domino pill click handler (event delegation on alpha grid)
  document.getElementById('alpha-grid').addEventListener('click', function(e) {
    var pill = e.target.closest('.domino-pill');
    if (!pill) return;
    var targetId = pill.getAttribute('data-target');
    if (targetId) {
      var el = document.getElementById(targetId);
      if (el) el.scrollIntoView({behavior: 'smooth', block: 'center'});
    }
  });

  // ── VIEW 2: CAPITAL FLOW TABLE ──
  var capBody = document.getElementById('capital-body');
  if (capBody && CAPITAL_FLOWS.length) {
    capBody.innerHTML = CAPITAL_FLOWS.map(function(cf){
      var isDisc = cf.discrepancies > 3;
      var rowClass = isDisc ? 'discrepancy-row' : '';
      var netSign = cf.net_b >= 0 ? '+' : '';
      var netClass = cf.net_b >= 0 ? 'text-gold-dim' : 'text-error';
      return '<tr class="border-b border-surface-variant font-body-md text-body-md '+rowClass+'">' +
        '<td class="py-2 pr-4 font-metadata-sm text-metadata-sm">'+cf.narrative+'</td>' +
        '<td class="py-2 pr-4 font-headline-md text-gold-dim">'+cf.ticker+'</td>' +
        '<td class="py-2 pr-4 text-right">'+cf.inflow_b.toFixed(1)+'B</td>' +
        '<td class="py-2 pr-4 text-right">'+cf.outflow_b.toFixed(1)+'B</td>' +
        '<td class="py-2 pr-4 text-right '+netClass+'">'+netSign+cf.net_b.toFixed(1)+'B</td>' +
        '<td class="py-2 pr-4 text-right">'+cf.total_b.toFixed(1)+'B</td>' +
        '<td class="py-2 pr-4 text-right">'+cf.stories+'</td>' +
        '<td class="py-2 pr-4 text-center">'+(cf.discrepancies > 3 ? '<span class="material-symbols-outlined text-error text-sm">warning</span> '+cf.discrepancies : '<span class="material-symbols-outlined text-outline text-sm">check_circle</span>')+'</td>' +
        '<td class="py-2 text-right font-metadata-sm">'+cf.gap.toFixed(0)+'</td>' +
        '</tr>';
    }).join('');
  }

  // Cross-asset grid
  var caGrid = document.getElementById('cross-asset-grid');
  if (caGrid && Object.keys(CROSS_ASSET).length) {
    caGrid.innerHTML = Object.keys(CROSS_ASSET).map(function(k){
      return '<div class="bg-surface-container p-stack-space-sm border border-outline-variant text-center">' +
        '<span class="font-label-xs text-label-xs uppercase text-on-surface-variant block">'+k.toUpperCase()+'</span>' +
        '<span class="font-headline-md text-headline-md text-on-surface mt-1">'+CROSS_ASSET[k]+'</span>' +
        '</div>';
    }).join('');
  }

  // Regime drivers
  var rdEl = document.getElementById('regime-drivers');
  if (rdEl && REGIME_DRIVERS.length) {
    rdEl.innerHTML = REGIME_DRIVERS.map(function(d){
      return '<span class="border border-outline px-3 py-1 font-label-xs text-label-xs uppercase">'+d+'</span>';
    }).join('');
  }

  // ── VIEW 3: CONTRADICTION MATRIX (reads from STORIES) ──
  function renderMatrix(filter, sort) {
    // Build divergence dataset from STORIES (gap >= 40 only)
    var data = [];
    for (var i = 0; i < STORIES.length; i++) {
      var s = STORIES[i];
      var gap = s.contradiction_gap || 0;
      if (gap < 40) continue;
      var capB = (s.capital_volume_usd || 0) / 1e9;
      var ago = '';
      if (s.generated_at) {
        var dd = new Date(s.generated_at);
        var hh = Math.floor((new Date() - dd) / 3600000);
        ago = hh <= 0 ? 'Just now' : hh + 'H AGO';
      }
      data.push({
        id: s.story_id || 0,
        headline: s.headline || 'Untitled',
        container: s._container_title || '',
        container_id: s._container_id || '',
        gap: gap,
        capital_b: capB,
        tier: s.tier || '',
        time_ago: ago,
        they_say: (s.they_say || '').substring(0, 200),
        reality: (s.reality || '').substring(0, 200)
      });
    }
    if (filter !== 'all') data = data.filter(function(c){return c.container_id === filter;});
    if (sort === 'gap') data.sort(function(a,b){return b.gap - a.gap;});
    else if (sort === 'capital') data.sort(function(a,b){return b.capital_b - a.capital_b;});
    else data.sort(function(a,b){return b.id - a.id;});
    var matrixBody = document.getElementById('matrix-body');
    if (!matrixBody) return;
    matrixBody.innerHTML = data.slice(0, 100).map(function(c){
      var tierInfo = c.gap >= 65 ? {label:'BREAKING', border:'border-l-2 border-crimson', text:'text-crimson', badge:'bg-crimson/10 text-crimson'} :
                     c.gap >= 40 ? {label:'ACTIVE', border:'border-l-2 border-gold-accessible', text:'text-gold-accessible', badge:'bg-gold-accessible/10 text-gold-accessible'} :
                                   {label:'SETTLING', border:'border-l-2 border-gray-300', text:'text-gold-dim', badge:'bg-slate-100 text-slate-600'};
      return '<details class="py-stack-space-sm border-b border-gold/20 '+tierInfo.border+'">' +
        '<summary class="pl-stack-space-sm">' +
        '<div class="flex justify-between items-start flex-wrap gap-2">' +
          '<div><span class="font-label-xs text-label-xs text-on-surface-variant uppercase">'+c.container+'</span>' +
          '<span class="font-label-xs text-label-xs text-on-surface-variant ml-2">'+c.time_ago+'</span>' +
          '<span class="material-symbols-outlined expand-icon text-on-surface-variant align-middle ml-1" style="font-size:18px;">expand_more</span></div>' +
          '<span class="font-metadata-sm text-metadata-sm '+tierInfo.text+'">Δ Edge: '+c.gap.toFixed(0)+' | '+(c.capital_b > 0 ? c.capital_b.toFixed(1)+'B' : 'N/A')+'</span>' +
        '</div>' +
        '<p class="font-body-md text-body-md text-on-surface mt-1">'+c.headline+'</p>' +
        '<div class="flex items-center gap-2 mt-2"><span class="text-xs uppercase tracking-wider '+tierInfo.text+'">'+tierInfo.label+'</span>' +
        '<span class="text-xs uppercase px-1 py-0.5 '+tierInfo.badge+'">Δ EDGE: '+c.gap.toFixed(0)+'</span>' +
        '</div></summary>' +
        '<div class="details-content mt-2 pl-stack-space-sm grid grid-cols-1 md:grid-cols-2 gap-stack-space-sm">' +
          '<div class="bg-surface-container-high p-stack-space-sm border-l border-outline-variant">' +
            '<h4 class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase mb-1">Media Consensus</h4>' +
            '<p class="font-body-md text-body-md text-on-surface-variant">'+c.they_say+'</p>' +
          '</div>' +
          '<div class="bg-gold/5 p-stack-space-sm border-l border-gold">' +
            '<h4 class="font-metadata-sm text-metadata-sm text-gold-dim uppercase mb-1">Market Reality</h4>' +
            '<p class="font-body-md text-body-md text-on-surface">'+c.reality+'</p>' +
          '</div>' +
        '</div>' +
        '</details>';
    }).join('');
  }

  // Filter dropdown
  var filterEl = document.getElementById('matrix-filter');
  if (filterEl) {
    filterEl.innerHTML = '<option value="all">All Narratives</option>' +
      NARRATIVES.map(function(n){return '<option value="'+n.id+'">'+n.title+'</option>';}).join('');
    filterEl.addEventListener('change', function(){
      renderMatrix(this.value, document.getElementById('matrix-sort').value);
    });
  }
  var sortEl = document.getElementById('matrix-sort');
  if (sortEl) {
    sortEl.addEventListener('change', function(){
      renderMatrix(document.getElementById('matrix-filter').value, this.value);
    });
  }
  renderMatrix('all', 'gap');

  // ── C1: CLIENT-SIDE FILTERING ──
  var activeFilters = {tier: 'all', origin: 'all'};

  (function buildOriginPills() {
    var seen = {};
    var pills = '';
    for (var i = 0; i < STORIES.length; i++) {
      var fs = STORIES[i].feed_source;
      if (fs && !seen[fs]) { seen[fs] = true; pills += '<button class="filter-pill px-2 py-1 font-label-xs text-label-xs uppercase border border-outline text-on-surface-variant hover:border-gold-accessible hover:text-gold-accessible" data-filter="origin-'+fs.replace(/ /g,'_')+'">'+fs+'</button>'; }
    }
    var op = document.getElementById('origin-pills');
    if (op) op.innerHTML = pills;
  })();

  function applyFilters() {
    var cards = document.querySelectorAll('#story-cards article[data-story-id]');
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      var tier = card.getAttribute('data-tier') || '';
      var origin = card.getAttribute('data-source-feed') || '';
      var show = true;
      if (activeFilters.tier !== 'all' && tier !== activeFilters.tier) show = false;
      if (activeFilters.origin !== 'all' && origin.toUpperCase() !== activeFilters.origin.toUpperCase()) show = false;
      card.style.display = show ? '' : 'none';
    }
    if (typeof injectSourceAttribution === 'function') injectSourceAttribution();
  }

  var filterPills = document.querySelectorAll('#filter-bar .filter-pill');
  for (var i = 0; i < filterPills.length; i++) {
    filterPills[i].addEventListener('click', function(){
      var f = this.getAttribute('data-filter');
      var siblings = this.parentElement.querySelectorAll('.filter-pill');
      for (var j = 0; j < siblings.length; j++) siblings[j].classList.remove('text-gold-accessible', 'border-gold-accessible');
      this.classList.add('text-gold-accessible', 'border-gold-accessible');
      if (f === 'all') { activeFilters.tier = 'all'; activeFilters.origin = 'all'; }
      else if (f.indexOf('tier-') === 0) { activeFilters.tier = f.substring(5); activeFilters.origin = 'all'; }
      else if (f.indexOf('origin-') === 0) { activeFilters.origin = f.substring(7).replace(/_/g,' '); activeFilters.tier = 'all'; }
      if (f === 'all' || f.indexOf('tier-') === 0) {
        var allBtn = document.querySelector('#filter-bar .filter-pill[data-filter="all"]');
        if (f === 'all' && allBtn) { allBtn.classList.add('text-gold-accessible','border-gold-accessible'); }
        else if (allBtn) { allBtn.classList.remove('text-gold-accessible','border-gold-accessible'); }
      }
      applyFilters();
    });
  }
  // ── VIEW 4: ABOUT / PHASE TABLE ──
  var phaseBody = document.getElementById('phase-body');
  if (phaseBody && NARRATIVES.length) {
    phaseBody.innerHTML = NARRATIVES.map(function(n){
      return '<tr class="border-b border-surface-variant font-body-md text-body-md">' +
        '<td class="py-2 pr-4 font-metadata-sm text-metadata-sm">'+n.title+'</td>' +
        '<td class="py-2 pr-4 text-gold-dim font-headline-md" data-ticker="'+n.ticker+'" data-narrative="'+n.id+'">'+n.ticker+'</td>' +
        '<td class="py-2 pr-4 text-right">'+n.gap.toFixed(0)+'</td>' +
        '<td class="py-2 pr-4"><span class="px-2 py-0.5 font-label-xs text-label-xs uppercase '+(n.phase==='VIRAL EXPANSION'?'bg-error-container/20 text-error':'bg-surface-container text-on-surface-variant')+'">'+n.phase+'</span></td>' +
        '<td class="py-2"><span class="font-metadata-sm text-metadata-sm text-crimson">'+n.threshold_val+'</span><br><span class="text-xs text-on-surface-variant">'+n.threshold_desc+'</span></td>' +
        '</tr>';
    }).join('');
  }

})();

// ── GLOSSARY TOOLTIP ENGINE ──
(function(){
  var GLOSSARY = {
    // Tickler explanations
    QQQ:'Tech-heavy Nasdaq-100 ETF — tracks large-cap tech convergence',
    SMH:'Semiconductor ETF — tracks chip manufacturers (VanEck)',
    SOXX:'Semiconductor ETF — broader semi index (iShares)',
    FXI:'China large-cap ETF — tracks Chinese stocks on HK exchange',
    KWEB:'China internet ETF — tracks Chinese tech/consumer names',
    MCHI:'China broad-market ETF — MSCI China Index',
    ASHR:'China A-shares ETF — direct mainland China exposure',
    SPY:'S&P 500 ETF — broad US equity market benchmark',
    UUP:'US Dollar bullish ETF — rises when dollar strengthens',
    GLD:'Gold trust ETF — tracks physical gold price',
    SLV:'Silver trust ETF — tracks physical silver price',
    ARKG:'Genomic revolution ETF — CRISPR, gene editing, biotech',
    XBI:'Biotech ETF — equal-weighted biotech index',
    IBB:'Biotech ETF — market-cap weighted (iShares)',
    XLI:'Industrial sector ETF — manufacturing, defense, transport',
    ITA:'Aerospace & defense ETF — tracks defense contractors',
    PPA:'Aerospace & defense ETF — broader defense/space exposure',
    XME:'Metals & mining ETF — tracks base metals producers',
    URA:'Uranium ETF — nuclear energy supply chain',
    NLR:'Uranium & nuclear energy ETF — global nuclear infrastructure',
    REMX:'Rare earth/strategic metals ETF — critical mineral supply chain',
    ROKT:'Space economy ETF — orbital infrastructure, satellites',
    UFO:'Space ETF — procure space index',
    ARKX:'Space exploration ETF — ARK Invest space innovation',
    NVDA:'Nvidia — dominant AI/GPU chip designer',
    AMD:'Advanced Micro Devices — CPU/GPU chip designer',
    TSM:'Taiwan Semiconductor — world largest chip foundry',
    TLT:'Long-dated Treasury bond ETF — 20+ year US govt bonds',
    SHY:'Short-term Treasury ETF — 1-3 year US govt bonds',
    IEF:'Intermediate Treasury ETF — 7-10 year US govt bonds',
    DBC:'Commodity index ETF — broad basket of physical commodities',
    GDX:'Gold miners ETF — tracks gold mining companies',
    BTC:'Bitcoin — largest cryptocurrency by market cap',
    ETH:'Ethereum — smart-contract platform cryptocurrency',
    COIN:'Coinbase — largest US crypto exchange',
    BATRK:'Atlanta Braves Holdings — sports/media franchise tracking stock',
    MSGS:'Madison Square Garden Sports — owns Knicks/Rangers',
    MANU:'Manchester United — publicly traded football club',
    VIX:'CBOE Volatility Index — measures S&P 500 implied volatility (fear gauge)',
    DXY:'US Dollar Index — measures dollar vs basket of major currencies',
    CL:'Crude oil futures — WTI benchmark price',
    // Narrative labels
    dollar_decline:'Dollar Decline — USD reserve status erosion, BRICS payment rails, gold repatriation',
    critical_resource_control:'Critical Resource Control — crude, natural gas, nuclear, rare earths, grid control, critical minerals',
    deglobalization:'Deglobalization — supply chain splits, sanctions, trade blocs, reshoring',
    china_ascent:'China Ascent — tech independence, Belt & Road, parallel financial systems',
    space_economy:'Space Economy — orbital infrastructure, space mining, satellite networks',
    gene_editing:'Gene Editing & Longevity — CRISPR, biotech, healthspan extension',
    tech_convergence:'Tech Convergence — AI + quantum + biotech intersections, platform dominance',
    wealthy_sports:'Wealthy Sports — sovereign wealth in teams, sports as soft power',
    ai_chips:'AI Chips — semiconductor supremacy, GPU/TPU supply chain, TSMC/NVIDIA dominance',
    crypto_reserve:'Crypto Reserve — Bitcoin as strategic asset, stablecoin geopolitics, digital gold',
    rate_cycle:'Rate Cycle — Fed policy trajectory, yield curve dynamics, duration risk',
    commodity_supercycle:'Commodity Supercycle — critical minerals, energy transition metals, food security',
    // Scoring terms
    EDGE:'Contrarian Edge (Δ) — measures the divergence between media narrative and market price action (0-100 scale). Higher = greater alpha potential.',
    DIVERGENT:'Divergent — media narrative and market data are in significant conflict',
    CONVERGENT:'Convergent — media narrative and market data are aligned',
    BREAKING:'Breaking tier — extreme contradiction gap, highest signal priority',
    ACTIVE:'Active tier — significant contradiction, active monitoring warranted',
    SETTLING:'Settling tier — moderate or low contradiction, narrative stabilizing',
    DEVELOPING:'Developing tier — emerging narrative, insufficient data for scoring',
    CAPITAL:'Capital Flow — estimated institutional money movement tied to this narrative',
    'Domain Intelligence':'Sidebar showing real-time capital allocation per narrative — measured in billions USD',
    'Vulnerability Map':'Risk heat map — each narrative scored by divergence magnitude and capital concentration',
    'Reflexivity Alert':'When positioning becomes fundamental driver. Narratives enter self-reinforcing loops — invalidation thresholds mark where the thesis breaks.',
    'Invalidation Threshold':'The exact price or economic level where a narrative thesis is proven wrong by market action.',
    'Consensus Saturation':'Narrative phase where media and market fully agree — the story is priced in, no edge remains.',
    'Viral Expansion':'Narrative phase where the thesis is spreading rapidly through institutional positioning.',
    'Epistemological Framework':'The methodology for knowing what we know — how the terminal distinguishes signal from noise.',
    'Diplomatic Ledger':'The terminal version identifier — each increment represents a significant architecture upgrade.',
    'VERIFIED_DISPATCH':'This story has been algorithmically verified against live market data.',
    'Risk-On Momentum':'Market regime where capital is rotating into growth assets (tech, equities) and out of safe havens.',
    'Thin Liquidity':'Market condition where low trading volume amplifies price moves — signals may be exaggerated.',
    // Tactical Horizon terms
    'Funding Rate':'The periodic premium paid between long and short futures traders to align synthetic contract pricing with underlying spot values. Spikes indicate extreme structural leverage.',
    'Open Interest':'The aggregate volume of outstanding, unliquidated derivative contracts currently active. Surges indicate a market storing kinetic energy for a violent directional expansion.',
    'Long Squeeze':'A cascading liquidation event where dropping prices trigger automated margin stop-outs of long positions, feeding an accelerating downward spiral of forced market selling.',
    'Short Squeeze':'A rapid upward price movement fueled by the forced buying of trapped short sellers closing positions under liquidation duress.',
    'Liquidation Cascade':'A chain-reaction process where a sharp price move triggers sequential margin liquidations, bypassing normal order book liquidity to create extreme price displacement.',
    'Volatility Crush':'A dramatic contraction in option implied volatility premiums, typically occurring after systemic high-risk events pass, forcing sideways consolidation.',
    'Contrarian Buy':'A quantitative positioning threshold where retail panic (options buying or long capitulation) reaches a statistical extreme, creating a highly efficient entry window for institutional accumulation.',
    'De-leveraging':'The structural unwinding of debt-financed leverage positions, characterized by simultaneously falling open interest and muted asset volatility frames.',
  };

  var tipEl = null;
  function getTip(){
    if (!tipEl){ tipEl = document.createElement('div'); tipEl.className = 'glossary-tip'; document.body.appendChild(tipEl); }
    return tipEl;
  }
  function showTip(el, text){
    var tip = getTip();
    tip.textContent = text;
    tip.classList.add('visible');
    var r = el.getBoundingClientRect();
    var top = r.bottom + 6;
    if (top + 80 > window.innerHeight) top = r.top - 6 - tip.offsetHeight;
    var left = Math.max(8, Math.min(r.left, window.innerWidth - 270));
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
  }
  function hideTip(){ var t = getTip(); t.classList.remove('visible'); }

  // Wire up ticker and narrative tooltips on the Stream
  function wireGlossary(){
    var targets = document.querySelectorAll('[data-ticker],[data-narrative],[data-gloss]');
    targets.forEach(function(el){
      if (el._wired) return;
      el._wired = true;
      el.classList.add('glossary-target');
      var key = el.getAttribute('data-ticker') || el.getAttribute('data-narrative') || el.getAttribute('data-gloss');
      var def = GLOSSARY[key];
      if (!def && el.getAttribute('data-ticker')) def = el.getAttribute('data-ticker') + ' — financial instrument tracked by this terminal';
      if (!def) return;
      el.addEventListener('mouseenter', function(){ showTip(el, def); });
      el.addEventListener('mouseleave', hideTip);
      el.addEventListener('touchstart', function(e){
        e.preventDefault();
        if (tipEl && tipEl.classList.contains('visible')){ hideTip(); } else { showTip(el, def); }
      }, {passive:false});
    });
  }

  // Run on load and after tab switches
  wireGlossary();
  var origSwitchTab = window.switchTab;
  window.switchTab = function(name){
    origSwitchTab(name);
    setTimeout(wireGlossary, 300);
  };

  // ── SHARE HANDLER (reads from article dataset) ──
  window.shareStory = function(btn) {
    var article = btn.closest('article');
    if (!article) return;
    var d = article.dataset;
    var setup = d.direction && d.direction !== 'NEUTRAL'
      ? d.direction.toUpperCase() + ' ' + (d.ticker||'') + ' @ ' + (d.entry||'N/A')
      : 'No active thesis';
    var payload = d.headline + '\\n\\nCAPITAL: $' + (d.capital||'0') + ' | Δ EDGE: ' + (d.gap||'0') + '/100\\nTRADE: ' + setup + '\\n\\n' + window.location.origin + window.location.pathname + '?story=' + (article.getAttribute('data-story-id')||'');
    if (navigator.share) {
      navigator.share({
        title: 'La Gazzetta di Kyiv Wire',
        text: payload,
        url: window.location.href
      }).catch(function(){});
    } else {
      navigator.clipboard.writeText(payload);
      var icon = btn.querySelector('.material-symbols-outlined');
      if (icon) { icon.textContent = 'check'; }
      setTimeout(function(){
        if (icon) { icon.textContent = 'share'; }
      }, 2000);
    }
  };
})();
</script>

</body>
</html>"""


if __name__ == "__main__":
    if not build():
        sys.exit(1)
