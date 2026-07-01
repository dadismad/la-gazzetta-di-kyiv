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
from datetime import datetime, timezone

PROJECT = Path(os.environ.get("GAZZETTA_HOME", "/opt/gazzetta-di-kyiv"))
DATA = PROJECT / "data"
PUBLIC = PROJECT / "public"
PUBLIC_DATA = PUBLIC / "data"

TICKER_MAP = {
    "dollar_decline": "DXY", "energy_sovereignty": "Brent",
    "deglobalization": "XLI", "china_ascent": "FXI",
    "space_economy": "ROKT", "gene_editing": "ARKG",
    "tech_convergence": "QQQ", "wealthy_sports": "BATRK"
}

PILL_ORDER = [
    "dollar_decline", "energy_sovereignty", "deglobalization",
    "china_ascent", "space_economy", "gene_editing",
    "tech_convergence", "wealthy_sports"
]

ICON_MAP = {
    "dollar_decline": "trending_down", "energy_sovereignty": "bolt",
    "deglobalization": "public", "china_ascent": "language",
    "space_economy": "rocket_launch", "gene_editing": "biotech",
    "tech_convergence": "memory", "wealthy_sports": "sports_soccer"
}

def load_json(path):
    with open(path) as f:
        return json.load(f)

def fmt_b(n):
    if n >= 1: return f"{n:.1f}B"
    m = n * 1000
    if m >= 1: return f"{m:.0f}M"
    return f"{m:.1f}M"

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
    """Heuristic narrative lifecycle phase."""
    if count < 3: return "EMERGENT", "New signal — limited data"
    if gap >= 70: return "VIRAL EXPANSION", "Wide gap between narrative and reality"
    if gap >= 40: return "CONSENSUS SATURATION", "Narrative widely accepted, friction building"
    return "MATURE/STABLE", "Narrative and reality aligned"

def invalidation_threshold(nid, ticker):
    """Return price-level invalidation triggers per narrative."""
    thresholds = {
        "dollar_decline": ("DXY > 106", "USD strengthening reverses thesis"),
        "energy_sovereignty": ("Brent < $65", "Energy independence narrative breaks"),
        "deglobalization": ("XLI +8% MoM", "Industrial re-globalization invalidates"),
        "china_ascent": ("FXI -15% quarterly", "Capital flight contradicts ascent"),
        "space_economy": ("ROKT -25%", "Space investment thesis invalidated"),
        "gene_editing": ("ARKG -30%", "Biotech funding freeze contradicts"),
        "tech_convergence": ("QQQ -20%", "Tech selloff invalidates convergence"),
        "wealthy_sports": ("BATRK -25%", "Sports asset bubble pops"),
    }
    return thresholds.get(nid, ("N/A", "No threshold defined"))

def build():
    print("[build_frontend] loading data...")
    stories_raw = load_json(DATA / "stories.json")

    # Try flows.json for cross-asset data
    flows_raw = {}
    flows_path = PUBLIC_DATA / "flows.json"
    if flows_path.exists():
        flows_raw = load_json(flows_path)

    # Normalize stories
    all_stories = []
    containers = stories_raw.get("containers", {})
    for cid, cdata in containers.items():
        for s in cdata.get("stories", []):
            s["_container_id"] = cid
            s["_container_title"] = cdata.get("title", cid)
            all_stories.append(s)

    all_stories.sort(key=lambda s: s.get("generated_at", ""), reverse=True)

    # Compute narrative summaries
    narratives = []
    for cid in PILL_ORDER:
        cstories = [s for s in all_stories if s.get("_container_id") == cid]
        caps = [s.get("capital_volume_usd", 0) or 0 for s in cstories]
        gaps = [s.get("contradiction_gap", 0) or 0 for s in cstories]
        total_cap = sum(caps) / 1e9
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        directions = {"inflow": 0, "outflow": 0, "neutral": 0}
        for s in cstories:
            cf = s.get("capital_flow") or {}
            d = (cf.get("direction") or "neutral").lower()
            directions[d] = directions.get(d, 0) + 1
        phase, phase_desc = narrative_phase(avg_gap, len(cstories))
        threshold_val, threshold_desc = invalidation_threshold(cid, TICKER_MAP.get(cid, ""))
        cdata = containers.get(cid, {})
        narratives.append({
            "id": cid,
            "title": cdata.get("title", cid.replace("_", " ").title()),
            "ticker": TICKER_MAP.get(cid, "N/A"),
            "capital_b": total_cap,
            "count": len(cstories),
            "gap": avg_gap,
            "directions": directions,
            "phase": phase,
            "phase_desc": phase_desc,
            "threshold_val": threshold_val,
            "threshold_desc": threshold_desc,
            "icon": ICON_MAP.get(cid, "public"),
        })

    # Capital flows — compute discrepancies
    discrepancies = [s for s in all_stories if (s.get("contradiction_gap") or 0) >= 40]
    capital_flows = []
    for n in narratives:
        cap_stories = [s for s in all_stories if s.get("_container_id") == n["id"]]
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

    print(f"[build_frontend] {len(all_stories)} stories, {disc_count} discrepancies, regime={regime}")

    html = _TEMPLATE
    html = html.replace("__STORIES_JSON__", stories_json)
    html = html.replace("__NARRATIVES_JSON__", narratives_json)
    html = html.replace("__CAPITAL_JSON__", capital_json)
    html = html.replace("__CONTRADICTIONS_JSON__", "[]")
    html = html.replace("__CROSS_ASSET_JSON__", cross_asset_json)
    html = html.replace("__REGIME_JSON__", regime_json)
    html = html.replace("__REGIME_DRIVERS_JSON__", regime_drivers_json)
    html = html.replace("__REGIME_STR__", str(regime))
    html = html.replace("__BUILD_TIME__", build_time)
    html = html.replace("__STORY_COUNT__", str(len(all_stories)))
    html = html.replace("__DISC_COUNT__", str(disc_count))
    html = html.replace("__SYNC_STATUS__", sync_status)

    PUBLIC.mkdir(parents=True, exist_ok=True)
    out = PUBLIC / "index_staging.html"
    with open(out, "w") as f:
        f.write(html)

    print(f"[build_frontend] wrote {out} ({len(html)} bytes)")
    return True


_TEMPLATE = r"""<!DOCTYPE html>
<html class="light" lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>La Gazzetta di Kyiv — Geopolitical Intelligence</title>
<meta name="description" content="Institutional-grade narrative intelligence. Tracking the gap between media consensus and capital flows."/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet"/>
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
        "surface-container-highest": "#E3E2E0","on-surface": "#1A1C1A",
        "on-surface-variant": "#444748","inverse-surface": "#2F312F",
        "inverse-on-surface": "#F2F1EE","outline": "#747878",
        "outline-variant": "#C4C7C7","gold": "#D4AF37","gold-dim": "#B8860B","gold-accessible": "#B45309",
        "crimson": "#8B0000","roman-purple": "#66023C","navy": "#1A1F2E",
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
        "headline-lg":["30px",{lineHeight:"36px",fontWeight:"700"}],
        "headline-lg-mobile":["26px",{lineHeight:"32px",fontWeight:"700"}],
        "headline-md":["22px",{lineHeight:"28px",fontWeight:"600"}],
        "body-md":["16px",{lineHeight:"24px",fontWeight:"400"}],
        "metadata-sm":["13px",{lineHeight:"18px",fontWeight:"500",letterSpacing:"0.04em"}],
        "label-xs":["12px",{lineHeight:"16px",fontWeight:"600",letterSpacing:"0.02em"}],
      },
    }
  }
}
</script>
<style>
  *,*::before,*::after{border-radius:0!important;box-shadow:none!important}
  body{background:#FAF9F6;color:#1A1C1A;min-height:100dvh}
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
</style>
</head>
<body class="bg-surface font-body-md text-on-surface antialiased">

<!-- ═══ DESKTOP SIDEBAR ═══ -->
<aside class="hidden md:flex md:flex-col fixed left-0 top-0 h-full w-72 bg-primary text-on-primary z-40 overflow-y-auto" id="desktop-sidebar">
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
  <header class="bg-surface border-b border-gold w-full px-margin-horizontal h-14 sticky top-0 z-30">
    <div class="flex justify-between items-center h-full">
      <button class="w-tap-target-min h-tap-target-min flex items-center justify-center text-on-surface-variant md:hidden" onclick="document.getElementById('mobile-menu').classList.toggle('hidden')">
        <span class="material-symbols-outlined">menu</span>
      </button>
      <div class="hidden md:flex w-tap-target-min h-tap-target-min items-center justify-center"></div>
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-gold" style="font-variation-settings:'FILL'1;">pest_control</span>
        <h1 class="font-headline-lg-mobile text-headline-lg-mobile uppercase tracking-widest text-roman-purple gold-strikethrough gold-outline">La Gazzetta di Kyiv</h1>
        <span class="material-symbols-outlined text-gold" style="font-variation-settings:'FILL'1;">gavel</span>
      </div>
      <div class="w-tap-target-min h-tap-target-min flex items-center justify-center"></div>
    </div>
  </header>

  <!-- MOBILE MENU -->
  <div class="hidden md:hidden bg-navy fixed inset-0 z-50 flex flex-col p-stack-space-lg" id="mobile-menu">
    <div class="flex justify-between items-center mb-stack-space-lg">
      <h2 class="font-headline-md text-headline-md text-gold">Navigation</h2>
      <button class="text-on-primary w-tap-target-min h-tap-target-min flex items-center justify-center" onclick="document.getElementById('mobile-menu').classList.add('hidden')">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>
    <nav class="flex flex-col gap-2" id="mobile-nav"></nav>
  </div>

  <!-- TAB NAVIGATION -->
  <nav class="border-b border-gold/20 overflow-x-auto hide-scrollbar bg-surface">
    <div class="flex px-margin-horizontal gap-0 w-max max-w-4xl mx-auto" id="tab-nav">
      <button class="tab-btn active px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="stream">
        <span class="material-symbols-outlined align-middle mr-1 text-sm">newspaper</span> Stream
      </button>
      <button class="tab-btn px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="capital">
        <span class="material-symbols-outlined align-middle mr-1 text-sm">account_balance</span> Capital Flows
      </button>
      <button class="tab-btn px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="contradictions">
        <span class="material-symbols-outlined align-middle mr-1 text-sm">analytics</span> Contradictions
      </button>
      <button class="tab-btn px-4 py-3 font-metadata-sm text-metadata-sm uppercase tracking-wider text-on-surface-variant hover:text-on-surface min-h-tap-target-min" data-tab="about">
        <span class="material-symbols-outlined align-middle mr-1 text-sm">psychology</span> About
      </button>
    </div>
  </nav>

  <!-- ═══ VIEW 1: THE STREAM ═══ -->
  <main class="tab-content active flex-1 max-w-4xl mx-auto w-full px-margin-horizontal py-stack-space-lg" id="view-stream">
    <div class="flex justify-between items-end mb-stack-space-md pb-stack-space-sm border-b-2 border-gold">
      <div>
        <h2 class="font-headline-lg text-headline-lg text-on-surface">The Stream</h2>
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
    <div class="flex flex-col gap-0" id="story-cards"></div>
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
            <th class="py-2 text-right">Gap</th>
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
          <option value="gap">Highest Gap</option>
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
        <p class="font-body-md text-body-md text-on-surface-variant">This platform measures the structural gap between financial media reporting and actual institutional capital migration. Dispatches are analyzed and scored based on the magnitude of divergence between qualitative consensus narratives and quantitative asset-class flow volumes; large contradiction gaps receive priority visibility on the ledger.</p>
      </div>
      <details class="mb-stack-space-md" open>
        <summary class="p-stack-space-md bg-surface-container border-l-2 border-gold font-headline-md text-headline-md text-on-surface">
          <span class="material-symbols-outlined expand-icon text-gold">expand_more</span> The Lefevre Filter
        </summary>
        <div class="details-content px-stack-space-md pb-stack-space-md bg-surface-container border-l-2 border-gold">
          <p class="font-body-md text-body-md text-on-surface-variant">Market price action is verification, not subject. For every story, ask: "If this news is true, why isn't the price moving?" Silence in the tape when the narrative screams is the loudest signal.</p>
        </div>
      </details>
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
                <th class="py-2 pr-4 text-right">Gap</th>
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
      <span class="material-symbols-outlined text-gold" style="font-variation-settings:'FILL'1;">newspaper</span>
      <span class="font-label-xs text-label-xs uppercase">Stream</span>
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
      var tabs = ['stream','capital','contradictions','about'];
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
  if (hash && ['stream','capital','contradictions','about'].indexOf(hash) >= 0) switchTab(hash);

  // ── RENDER SIDEBAR ──
  var sidebarNav = document.getElementById('sidebar-nav');
  var sidebarVuln = document.getElementById('sidebar-vuln');
  if (sidebarNav && NARRATIVES.length) {
    sidebarNav.innerHTML = NARRATIVES.map(function(n, i) {
      var active = i === 0 ? ' text-gold-accessible border-b-2 border-gold-accessible' : ' text-on-primary/70 hover:text-gold-accessible';
      return '<a href="#" class="flex items-center gap-3 px-3 py-2 font-metadata-sm text-metadata-sm uppercase tracking-wider' + active + '">' +
        '<span class="text-lg font-headline-md">' + n.ticker + '</span>' +
        '<span>' + n.title + '</span>' +
        '<span class="ml-auto text-gold-accessible text-xs">' + (n.capital_b >= 1 ? n.capital_b.toFixed(1)+'B' : (n.capital_b*1000).toFixed(0)+'M') + '</span>' +
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

  // ── VIEW 1: STREAM CARDS ──
  var cardsEl = document.getElementById('story-cards');
  if (cardsEl && STORIES.length) {
    cardsEl.innerHTML = STORIES.map(function(s){
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
      return '<article data-story-id="' + (s.story_id || '') + '" data-source-feed="' + (s.feed_source || '') + '" data-tier="(s.tier || '')" class="py-stack-space-md border-b border-gold/20 border-l-2 border-gold/30">' +
        '<div class="pl-stack-space-md">' +
        '<div class="flex justify-between items-start mb-2 flex-wrap gap-2">' +
          '<div class="flex items-center gap-2">' +
            '<span class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase">'+(s._container_title||'')+'</span>' +
            '<span class="font-label-xs text-label-xs text-gold-accessible">'+timeAgo+'</span>' +
          '</div>' +
          '<span class="px-2 py-0.5 border border-outline-variant font-label-xs text-label-xs uppercase '+tagClass+'">'+label+' · '+gap.toFixed(0)+'/100</span>' +
        '</div>' +
        '<h3 class="font-headline-md text-headline-md text-on-surface leading-tight mb-2">'+(s.headline||'Untitled')+'</h3>' +
        '<div class="mt-stack-space-sm flex items-center gap-3">' +
          '<span class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase">Capital</span>' +
          '<div class="flex-grow h-[3px] bg-surface-variant relative"><div class="absolute left-0 top-0 h-full bg-gold" style="width:'+gapPct+'%;"></div></div>' +
          '<span class="font-metadata-sm text-metadata-sm text-on-surface">'+capStr+'</span>' +
        '</div>' +
        '<div class="mt-2 flex gap-2 flex-wrap">' +
          (tier?'<span class="text-xs text-crimson uppercase tracking-wider border border-error/30 px-1.5 py-0.5">'+tier+'</span>':'') +
          '<span class="text-xs text-on-surface-variant uppercase tracking-wider">Gap: '+gap.toFixed(0)+'</span>' +
        '</div>' +
        '<details class="mt-2">' +
          '<summary class="font-metadata-sm text-metadata-sm text-gold-accessible uppercase tracking-wider flex items-center gap-1">' +
            '<span class="material-symbols-outlined expand-icon" style="font-size:18px;">expand_more</span> Read Dispatch' +
          '</summary>' +
          '<div class="details-content mt-stack-space-sm grid grid-cols-1 md:grid-cols-2 gap-stack-space-sm">' +
            '<div class="bg-surface-container-high p-stack-space-sm border-l border-outline-variant">' +
              '<h4 class="font-metadata-sm text-metadata-sm text-on-surface-variant uppercase mb-1">Media Consensus</h4>' +
              '<p class="font-body-md text-body-md text-on-surface-variant">'+(s.they_say||'No data.')+'</p>' +
            '</div>' +
            '<div class="bg-gold/5 p-stack-space-sm border-l border-gold">' +
              '<h4 class="font-metadata-sm text-metadata-sm text-gold-dim uppercase mb-1">Market Reality</h4>' +
              '<p class="font-body-md text-body-md text-on-surface">'+(s.reality||'No data.')+'</p>' +
            '</div>' +
          '</div>' +
        '</details>' +
        '</div></article>';
        '</div></div></article>';
    }).join('');

    // Post-render source attribution injection
    injectSourceAttribution();
  }

  function injectSourceAttribution() {
    var articles = document.querySelectorAll('article[data-story-id]');
    for (var i = 0; i < articles.length; i++) {
      var card = articles[i];
      if (card.querySelector('.source-attribution-footer')) continue;
      var sourceData = card.getAttribute('data-source-feed');
      if (!sourceData || sourceData.trim() === '') continue;
      var footer = document.createElement('div');
      footer.className = 'source-attribution-footer mt-4 pt-2 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400 font-mono tracking-tight';
      footer.innerHTML = '<div class="flex items-center gap-1.5"><span class="material-symbols-outlined text-[12px] text-gray-300">database</span><span>FEED_SOURCE: ' + sourceData.toUpperCase().trim() + '</span></div><div class="text-[10px] bg-gray-50 px-1.5 py-0.5 rounded border border-gray-200 font-sans">VERIFIED_DISPATCH</div>';
      card.appendChild(footer);
    }
  }

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
          '<span class="font-metadata-sm text-metadata-sm '+tierInfo.text+'">Gap: '+c.gap.toFixed(0)+' | '+c.capital_b.toFixed(1)+'B</span>' +
        '</div>' +
        '<p class="font-body-md text-body-md text-on-surface mt-1">'+c.headline+'</p>' +
        '<div class="flex items-center gap-2 mt-2"><span class="text-xs uppercase tracking-wider '+tierInfo.text+'">'+tierInfo.label+'</span>' +
        '<span class="text-xs uppercase px-1 py-0.5 '+tierInfo.badge+'">GAP: '+c.gap.toFixed(0)+'</span>' +
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
        '<td class="py-2 pr-4 text-gold-dim font-headline-md">'+n.ticker+'</td>' +
        '<td class="py-2 pr-4 text-right">'+n.gap.toFixed(0)+'</td>' +
        '<td class="py-2 pr-4"><span class="px-2 py-0.5 font-label-xs text-label-xs uppercase '+(n.phase==='VIRAL EXPANSION'?'bg-error-container/20 text-error':'bg-surface-container text-on-surface-variant')+'">'+n.phase+'</span></td>' +
        '<td class="py-2"><span class="font-metadata-sm text-metadata-sm text-crimson">'+n.threshold_val+'</span><br><span class="text-xs text-on-surface-variant">'+n.threshold_desc+'</span></td>' +
        '</tr>';
    }).join('');
  }

})();
</script>

</body>
</html>"""


if __name__ == "__main__":
    if not build():
        sys.exit(1)
