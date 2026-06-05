#!/usr/bin/env python3
"""
post_composer.py — Gazzetta di Kyiv Devvit Post Composer

Produces varied, structurally unique markdown posts for Reddit/Devvit from
structured editorial data (scores + drafts). Four components:

  (A) PhraseBank    — openings, closings, disclaimers, uncertainty markers,
                      opinion frames, title templates
  (B) FormatTemplates — 10 structurally unique markdown-producing functions
  (C) FormatSelector — weighted random with anti-repetition, confidence gating,
                       post-type biases
  (D) Orchestrator  — ties everything together: data → varied markdown

Usage:
    from scripts.post_composer import GazzettaComposer

    composer = GazzettaComposer()
    result = composer.compose(scores_data, drafts_data)
    print(result["body"])

Architecture:
    [Data Pipeline] → [Structured Data] → [Post Composer] → [Varied Markdown] → [Reddit API]
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable

# ──────────────────────────────────────────────────────────────────────
#  (A)  PHRASE BANK
# ──────────────────────────────────────────────────────────────────────

@dataclass
class PhraseBank:
    """Central repository of all compositional elements."""

    # ── Openings (20+) ──────────────────────────────────────────────
    openings: list[str] = field(default_factory=lambda: [
        "Here's what the market isn't pricing today — and why that creates an edge.",
        "Three forces are converging while consensus sleeps on the cross-asset signal.",
        "The narrative is moving faster than the price. Here's the gap.",
        "A structural repricing window is opening. Let's decode the catalysts.",
        "While the crowd focuses on the headline, the real action is in the second derivative.",
        "The data is telling a different story than the narrative. Here's the divergence.",
        "Something shifted overnight that most feeds won't surface. Time to connect the dots.",
        "Contradiction alert: prices are saying one thing, fundamentals another.",
        "Consensus has anchored to a scenario that's already breaking. Here's the new map.",
        "There's a signal hiding in plain sight. Let's unpack it.",
        "The macro landscape just rearranged itself. Here's what changed and what it means.",
        "Ignore the noise — here are the three data points that actually matter this cycle.",
        "Every cycle has a blind spot consensus refuses to price. This is ours.",
        "The price action is telling a cleaner story than any headline today. Let's read it.",
        "Two narratives are colliding and only one repricing path survives. Here's the map.",
        "The tail is wagging the dog — here's why the second-order effect is the real story.",
        "Everyone is watching the same data. Few are reading the same signal. Let's fix that.",
        "If you only read one market briefing today, this is the one that connects the dots the consensus missed.",
        "The divergence between price and narrative just widened. Here's where the edge lives.",
        "Consensus is converging on a scenario that's already stale. Let me show you what's replacing it.",
        "The market is pricing one thing. The fundamentals are pricing another. The gap is the opportunity.",
        "Catalysts are stacking in a way that creates asymmetric payoff. Let's break down the layers.",
        "The setup has changed three times in the last 48 hours. Here's the latest configuration.",
        "Here's what the late-cycle rotation looks like when it's hiding in plain sight.",
    ])

    # ── Closings (20+) ───────────────────────────────────────────────
    closings: list[str] = field(default_factory=lambda: [
        "Stress-test this thesis: what single catalyst would break the scenario in your framework?",
        "The edge comes from updating before consensus does. Watch the invalidation triggers.",
        "Narrative without flow is noise. Flow without narrative is random. Both matter.",
        "The highest-alpha trade is the one consensus hasn't formed yet. Stay early.",
        "Keep your framework falsifiable — every thesis needs a price at which you're wrong.",
        "Cross-asset confirmation is the signal. Single-asset moves are noise until corroborated.",
        "The best risk management is knowing which scenario invalidates your position.",
        "Don't confuse narrative velocity with price discovery. They converge, but not always.",
        "The market always finds the path of least resistance. Right now, that path is unclear.",
        "When consensus converges, the opportunity migrates. Track where it's moving next.",
        "The story isn't over — but the next chapter depends on data we don't have yet.",
        "Wrap it in your own thesis. The Gazzetta provides the map, not the destination.",
        "Price is the ultimate debater. Let the next 48 hours speak.",
        "Position for the asymmetry, not the certainty. The edge is in the tail.",
        "The best trades come from contradictions consensus refuses to see. Keep looking.",
        "Invalidation clarity is more valuable than prediction accuracy. Define your exit before your entry.",
        "The market will tell you if you're wrong. The hard part is listening before the drawdown.",
        "Convergence trades work until they don't. The question is whether you see the divergence first.",
        "Three sessions from now, today's price will look either prescient or naive. Stay falsifiable.",
        "The edge is not in being right — it's in being right and consensus being wrong simultaneously.",
        "This read is directional, not binary. The path matters more than the destination this cycle.",
        "Every narrative has a shelf life. Track the decay rate, not just the headline momentum.",
    ])

    # ── Disclaimers (15+) ────────────────────────────────────────────
    disclaimers: list[str] = field(default_factory=lambda: [
        "*This is not financial advice. I'm a narrative-intelligence bot synthesizing market signals for analytical discussion.*",
        "*Not investment advice. This is an AI-generated synthesis of publicly available data for informational purposes only.*",
        "*For educational and analytical purposes only. Verify all claims independently before making any decisions.*",
        "*I'm an automated system processing narrative intelligence — not a financial advisor. DYOR.*",
        "*This content is AI-generated from public data sources and does not constitute financial recommendations.*",
        "*Data-driven narrative analysis only. No position recommendations are implied or intended.*",
        "*Automated market intelligence brief — not financial advice. Always verify with your own research.*",
        "*I read thousands of sources so you don't have to — but I'm still a bot, not a broker. Do your own due diligence.*",
        "*Synthetic market analysis for informational discussion. Not a recommendation to buy, sell, or hold any asset.*",
        "*Narrative intelligence snapshot. All trading decisions remain your own responsibility. Past narratives don't guarantee future outcomes.*",
        "*This is a narrative synthesis engine — not a licensed advisor. Markets are unpredictable; trade accordingly.*",
        "*Automated discourse for educational consumption. Cross-reference all claims against primary sources.*",
        "*Machine-generated macro analysis. No account of your personal financial situation has been considered.*",
        "*Algorithmic market commentary for discussion purposes. Not a solicitation to trade any instrument.*",
        "*Data synthesis from public sources. Verify, validate, and take responsibility for your own decisions.*",
    ])

    # ── Uncertainty markers (15+) ────────────────────────────────────
    uncertainty_markers: list[str] = field(default_factory=lambda: [
        "current consensus may underestimate",
        "the data suggests but doesn't confirm",
        "if the pattern holds, which is not guaranteed",
        "early evidence points toward",
        "the direction is probable but not certain",
        "initial signals indicate possible",
        "assuming no exogenous shock disrupts the trend",
        "narrative momentum could shift before price catches up",
        "the setup is forming but hasn't been validated",
        "this thesis depends on conditions that could change",
        "confidence is moderate — invalidation scenarios remain active",
        "the correlation is observable, though causation remains unproven",
        "convergence is emerging but not yet confirmed across all timeframes",
        "this read is probabilistic, not deterministic",
        "the signal to noise ratio is improving but not decisive yet",
        "early cycle positioning carries inherent uncertainty",
        "narrative density is increasing but flow confirmation lags",
        "the configuration is fragile — small catalysts can alter the path",
    ])

    # ── Opinion frames (10+) ──────────────────────────────────────────
    opinion_frames: list[str] = field(default_factory=lambda: [
        "The highest-conviction read-through",
        "Here's where the asymmetry lives",
        "The overlooked second-order effect",
        "What consensus is getting wrong",
        "The trade that doesn't fit the narrative",
        "A contrarian take worth stress-testing",
        "The hidden variable in this setup",
        "The signal consensus will wake up to next week",
        "Why the obvious play might be the wrong one",
        "The pocket of mispricing nobody is discussing",
        "The narrative divergence that matters most",
        "The counter-consensus angle worth examining",
        "Where the market is looking past the risk",
        "The structural shift hiding in the noise",
    ])

    # ── Title templates (3 types × 9 = 27 total) ────────────────────
    title_templates_macro: list[str] = field(default_factory=lambda: [
        "Macro Radar — {sector}",
        "Capital Flow Brief — {sector}",
        "Macro Pulse — {sector}",
        "Macro Cross-Currents: {sector}",
        "Macro Lens — {sector}",
        "The Macro Angle on {sector}",
        "Macro Signal — {sector} Edition",
        "Macro Update: {sector} in Focus",
        "Macro Dashboard — {sector}",
    ])

    title_templates_market: list[str] = field(default_factory=lambda: [
        "Market Intelligence — {sector}",
        "The Narrative Lab — {sector}",
        "Market Signal Scan — {sector}",
        "Market Depth — {sector}",
        "Market Structure Note — {sector}",
        "The Market Read on {sector}",
        "Market Brief — {sector}",
        "Market Radar — {sector} Edition",
        "Market Mosaic — {sector}",
    ])

    title_templates_sector: list[str] = field(default_factory=lambda: [
        "{sector} Spotlight — Signal vs Noise",
        "{sector} Deep Dive",
        "{sector} — The Cross-Asset View",
        "{sector} Brief: Narrative & Flow",
        "{sector} — What Changed This Cycle",
        "{sector} — Repricing in Progress",
        "{sector} Watch — Key Levels & Catalysts",
        "{sector} Outlook — Divergence Detected",
        "{sector} — Positioning for the Next Move",
    ])


# ──────────────────────────────────────────────────────────────────────
#  (B)  FORMAT TEMPLATES (10 structurally unique functions)
# ──────────────────────────────────────────────────────────────────────

def _safe(val: Any, default: str = "") -> str:
    """Return string value or default."""
    if val is None:
        return default
    s = str(val)
    return s if s.strip() and s != "None" else default


def _pct(v: Any, default: str = "—") -> str:
    """Format as percentage."""
    try:
        return f"{int(float(v))}%"
    except (ValueError, TypeError):
        return default


def _bullet(items: list[str] | None) -> list[str]:
    """Convert to markdown bullets, filtering empties."""
    if not items:
        return []
    return [f"• {s}" for s in items if s and s.strip()]


def template_macro_radar(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 1: Macro Radar — structured brief with regime header,
    contradiction block, and asset outlook."""
    sector = _safe(score.get("sector", draft.get("headline_hook", "Markets")), "Markets")
    regime = _safe(score.get("regime", "mixed"), "mixed")
    claim = _safe(draft.get("core_claim", "Narrative intelligence update"))
    actors = draft.get("actors", ["Market participants"])[:3]
    actors_str = ", ".join(actors)
    bet = draft.get("bet_snippet_24_72h", {})
    inst = _safe(bet.get("instrument", "risk assets"))
    direction = _safe(bet.get("direction", "two-way"))
    prob = _pct(bet.get("probability_pct", 50))
    inval = _safe(bet.get("invalidation", "Narrative engagement collapses"))

    lines = [
        f"## Macro Radar — {sector}",
        "",
        f"**Regime:** {regime} | **Lead sector:** {sector}",
        f"**{frame}**",
        "",
        f"**The setup:** {claim}",
        f"**Actors in play:** {actors_str}",
        "",
        f"**{marker}** — the direction is forming but consensus hasn't arrived yet.",
        "",
        f"### Contradiction",
        f"{_safe(draft.get('contradiction_map', {}).get('consensus', ''))} vs "
        f"{_safe(draft.get('contradiction_map', {}).get('evidence', ''))} — "
        f"{_safe(draft.get('contradiction_map', {}).get('implication', ''))}",
        "",
        f"### 24–72h Outlook",
        f"**{inst}** → **{direction}** | Confidence: {prob}",
        f"⛔ Invalidation: {inval}",
        "",
        f"---",
        "",
        opening,
        "",
        closing,
    ]
    return "\n".join(lines)


def template_capital_flow_brief(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 2: Capital Flow Brief — emphasis on flow dynamics
    and narrative-driven allocation."""
    sector = _safe(score.get("sector", "Broad Risk Basket"))
    regime = _safe(score.get("regime", "mixed"))
    cap = _safe(score.get("captivation_score", "—"))
    flow = _safe(score.get("capital_flow_score", "—"))
    bene = _safe(score.get("beneficiary_score", "—"))
    claim = _safe(draft.get("core_claim", "Narrative momentum"))

    lines = [
        f"## Capital Flow Brief — {sector}",
        "",
        f"**Regime:** {regime}",
        f"**Captivation:** {cap} | **Flow signal:** {flow} | **Beneficiary:** {bene}",
        "",
        f"**{opening}**",
        "",
        f"**Claim:** {claim}",
        "",
        f"### Narrative-Driven Flow",
        f"{_safe(draft.get('actors', ['Unknown']))[0]} positioning is the marginal driver. "
        f"{marker}, but the {flow} flow score confirms directional lean.",
        "",
        f"### {frame}",
        f"The capital flow signal ({flow}/100) correlates with repricing potential in the "
        f"{_safe(draft.get('bet_snippet_24_72h', {}).get('instrument', 'market'))}. "
        f"When narrative precedes flow, the adjustment arrives within 2–3 sessions.",
        "",
        f"**Cross-asset check:** {_safe(draft.get('contradiction_map', {}).get('implication', ''))}",
        "",
        f"---",
        "",
        closing,
    ]
    return "\n".join(lines)


def template_narrative_lab(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 3: Narrative Lab — full analytical structure with
    context, dominant narrative, contradiction, second-order, strategy."""
    sector = _safe(score.get("sector", "Markets"))
    regime = _safe(score.get("regime", "mixed"))
    claim = _safe(draft.get("core_claim", ""))
    actors_str = ", ".join(draft.get("actors", ["Policy actors", "Market participants"])[:3])
    cmap = draft.get("contradiction_map", {})
    bet = draft.get("bet_snippet_24_72h", {})

    lines = [
        f"## Narrative Lab — {sector}",
        "",
        f"**Regime:** {regime}",
        f"*{opening}*",
        "",
        "### Context",
        f"The editorial pipeline surfaced this as a lead signal. {claim} "
        f"Key actors: {actors_str}.",
        "",
        "### Dominant Narrative",
        f"{_safe(cmap.get('consensus', 'Consensus narrative is forming'))}",
        "",
        f"### Contradiction ({frame})",
        f"Despite the consensus view, {_safe(cmap.get('evidence', 'evidence suggests otherwise'))}. "
        f"{marker} — this gap creates repricing potential.",
        f"**Implication:** {_safe(cmap.get('implication', ''))}",
        "",
        "### Second-Order Effects",
        f"• {_safe(bet.get('instrument', 'Risk assets'))} → {_safe(bet.get('direction', 'two-way'))}",
        f"• Confidence: {_pct(bet.get('probability_pct', 50))}",
        f"• Invalidation: {_safe(bet.get('invalidation', 'Monitor for reversal'))}",
        "",
        "### Strategic Interpretation",
        "The highest-alpha positioning is through the contradiction, not the consensus. "
        "If the evidence path validates, the repricing could be fast and crowded.",
        "",
        "---",
        "",
        closing,
    ]
    return "\n".join(lines)


def template_briefing_board(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 4: Briefing Board — table-heavy structured overview."""
    sector = _safe(score.get("sector", "Broad Risk"))
    regime = _safe(score.get("regime", "mixed"))
    bet = draft.get("bet_snippet_24_72h", {})
    cmap = draft.get("contradiction_map", {})

    lines = [
        f"## Briefing Board — {sector}",
        "",
        f"**Regime:** {regime}",
        "",
        f"{opening}",
        "",
        f"| Dimension | Signal |",
        f"|-----------|--------|",
        f"| **Core Claim** | {_safe(draft.get('core_claim', '—'))} |",
        f"| **Actors** | {', '.join(draft.get('actors', ['—'])[:3])} |",
        f"| **Instrument** | {_safe(bet.get('instrument', '—'))} |",
        f"| **Direction** | {_safe(bet.get('direction', '—'))} |",
        f"| **Confidence** | {_pct(bet.get('probability_pct', 50))} |",
        f"| **Invalidation** | {_safe(bet.get('invalidation', '—'))} |",
        "",
        f"### Contradiction Map",
        f"**Consensus view:** {_safe(cmap.get('consensus', '—'))}",
        f"**Evidence path:** {_safe(cmap.get('evidence', '—'))}",
        f"**Implication:** {_safe(cmap.get('implication', '—'))}",
        "",
        f"### {frame}",
        f"{marker} The board suggests positioning for repricing within 24–72h "
        f"if the evidence path confirms.",
        "",
        "---",
        "",
        closing,
    ]
    return "\n".join(lines)


def template_signal_scan(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 5: Signal Scan — signal → implication → actionable format."""
    sector = _safe(score.get("sector", "Markets"))
    regime = _safe(score.get("regime", "mixed"))
    bet = draft.get("bet_snippet_24_72h", {})

    lines = [
        f"## Signal Scan — {sector}",
        "",
        f"**Regime:** {regime}",
        "",
        f"### 🔍 Signal",
        f"{opening}",
        f"**{frame}** — {_safe(draft.get('core_claim', 'Narrative signal detected'))}",
        "",
        f"### ⚡ Implication",
        f"The concentration of narrative energy in {_safe(bet.get('instrument', 'this sector'))} "
        f"suggests {_safe(bet.get('direction', 'directional repricing'))}. "
        f"{marker} — the path is forming but not yet confirmed.",
        "",
        f"### 🎯 Actionable",
        f"• Monitor for: {_safe(bet.get('invalidation', 'catalyst confirmation'))}",
        f"• Probability: {_pct(bet.get('probability_pct', 50))}",
        f"• Actors to watch: {', '.join(draft.get('actors', ['Market participants'])[:3])}",
        "",
        f"### Cross-Asset Confirmation",
        f"{_safe(draft.get('contradiction_map', {}).get('implication', ''))} "
        f"Single-asset moves without cross-market corroboration are noise.",
        "",
        "---",
        "",
        closing,
    ]
    return "\n".join(lines)


def template_market_pulse(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 6: Market Pulse — quick condensed overview."""
    sector = _safe(score.get("sector", "Markets"))
    regime = _safe(score.get("regime", "mixed"))
    bet = draft.get("bet_snippet_24_72h", {})
    cmap = draft.get("contradiction_map", {})

    lines = [
        f"## Market Pulse — {sector}",
        "",
        f"**Regime:** {regime} | **Lead:** {sector}",
        "",
        f"{opening}",
        "",
        f"**The story:** {_safe(draft.get('core_claim', ''))}",
        f"**Contradiction:** {_safe(cmap.get('consensus', ''))} vs {_safe(cmap.get('evidence', ''))}",
        "",
        f"**24h view:** {_safe(bet.get('instrument', '—'))} → {_safe(bet.get('direction', '—'))} ({_pct(bet.get('probability_pct', 50))})",
        "",
        f"**{frame}:** {marker} — the pulse is quickening but hasn't reached full conviction.",
        "",
        f"**Watch for:** {_safe(bet.get('invalidation', 'Signal confirmation'))}",
        "",
        f"---",
        "",
        f"*Data compiled from {_safe(score.get('captivation_score', '—'))} narrative signals.*",
        "",
        closing,
    ]
    return "\n".join(lines)


def template_conviction_trade(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 7: Conviction Trade — deep dive into one trade setup."""
    sector = _safe(score.get("sector", "Markets"))
    regime = _safe(score.get("regime", "mixed"))
    bet = draft.get("bet_snippet_24_72h", {})
    cmap = draft.get("contradiction_map", {})

    lines = [
        f"## Conviction Trade — {sector}",
        "",
        f"**Regime:** {regime} | **Focus:** {_safe(bet.get('instrument', 'Risk asset'))}",
        "",
        f"### {frame}",
        f"{opening}",
        "",
        "### Setup",
        f"**Instrument:** {_safe(bet.get('instrument', '—'))}",
        f"**Direction:** {_safe(bet.get('direction', '—'))}",
        f"**Confidence:** {_pct(bet.get('probability_pct', 50))}",
        "",
        f"### Thesis",
        f"{_safe(draft.get('core_claim', ''))} "
        f"Contradiction: {_safe(cmap.get('consensus', ''))} vs "
        f"{_safe(cmap.get('evidence', ''))}. "
        f"{marker}",
        "",
        f"### Risk Framework",
        f"**Invalidation trigger:** {_safe(bet.get('invalidation', '—'))}",
        f"**Actors:** {', '.join(draft.get('actors', ['—'])[:3])}",
        "",
        "### Stress Test",
        "What would make this thesis wrong? If the contradiction resolves "
        "toward consensus rather than evidence, the trade unwinds. "
        "Position sizing should reflect this asymmetry.",
        "",
        "---",
        "",
        closing,
    ]
    return "\n".join(lines)


def template_contradiction_deep_dive(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 8: Contradiction Deep Dive — focus on the divergence."""
    sector = _safe(score.get("sector", "Markets"))
    regime = _safe(score.get("regime", "mixed"))
    cmap = draft.get("contradiction_map", {})
    bet = draft.get("bet_snippet_24_72h", {})

    lines = [
        f"## Contradiction Deep Dive — {sector}",
        "",
        f"**Regime:** {regime}",
        "",
        f"{opening}",
        "",
        "### The Gap",
        f"**Consensus:** {_safe(cmap.get('consensus', '—'))}",
        f"**Evidence:** {_safe(cmap.get('evidence', '—'))}",
        "",
        f"### Why It Matters",
        f"{_safe(cmap.get('implication', ''))} "
        f"This is not a small deviation — {marker}. "
        f"The gap creates an asymmetry that doesn't exist in consensus-priced scenarios.",
        "",
        f"### {frame}",
        f"The highest-alpha positioning exploits this divergence. "
        f"If evidence wins: {_safe(bet.get('instrument', 'the market'))} → {_safe(bet.get('direction', 'reprices'))}. "
        f"Confidence: {_pct(bet.get('probability_pct', 50))}.",
        "",
        "### Resolution Triggers",
        f"• Watch for: {_safe(bet.get('invalidation', 'Catalyst event'))}",
        f"• Actors: {', '.join(draft.get('actors', ['—'])[:3])}",
        "",
        "---",
        "",
        closing,
    ]
    return "\n".join(lines)


def template_sector_spotlight(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 9: Sector Spotlight — zoom into one sector's narrative."""
    sector = _safe(score.get("sector", "Markets"))
    regime = _safe(score.get("regime", "mixed"))
    cap = _safe(score.get("captivation_score", "—"))
    bet = draft.get("bet_snippet_24_72h", {})
    cmap = draft.get("contradiction_map", {})

    lines = [
        f"## Sector Spotlight — {sector}",
        "",
        f"**Regime:** {regime} | **Captivation:** {cap}/100",
        "",
        f"{opening}",
        "",
        f"### Why {sector} Now",
        f"Narrative energy is concentrating in {sector.lower()} "
        f"while the broader market looks elsewhere. {marker}",
        "",
        f"### Key Metrics",
        f"• **Flow direction:** {_safe(bet.get('direction', 'mixed'))}",
        f"• **Instrument:** {_safe(bet.get('instrument', '—'))}",
        f"• **Prob. path:** {_pct(bet.get('probability_pct', 50))}",
        "",
        f"### {frame}",
        f"{_safe(cmap.get('implication', ''))} "
        f"The sector-level signal is stronger than the headline suggests.",
        "",
        "### Invalidation",
        f"{_safe(bet.get('invalidation', 'Monitor sector flows'))}",
        "",
        f"**Actors:** {', '.join(draft.get('actors', ['—'])[:4])}",
        "",
        "---",
        "",
        closing,
    ]
    return "\n".join(lines)


def template_asset_claims_table(
    score: dict, draft: dict, opening: str, closing: str, marker: str, frame: str
) -> str:
    """Template 10: Asset Claims Table — full table of directional claims."""
    sector = _safe(score.get("sector", "Markets"))
    regime = _safe(score.get("regime", "mixed"))
    bet = draft.get("bet_snippet_24_72h", {})
    cmap = draft.get("contradiction_map", {})

    lines = [
        f"## Asset Claims Table — {sector}",
        "",
        f"**Regime:** {regime}",
        "",
        f"{opening}",
        "",
        "| Asset | Direction | Confidence | Key Trigger |",
        "|-------|-----------|------------|-------------|",
        f"| **{_safe(bet.get('instrument', '—'))}** | {_safe(bet.get('direction', '—'))} "
        f"| {_pct(bet.get('probability_pct', 50))} "
        f"| {_safe(bet.get('invalidation', '—'))} |",
        "",
        f"### Narrative Cross-Check",
        f"{_safe(cmap.get('implication', ''))} "
        f"{marker}",
        "",
        f"### {frame}",
        f"The table above represents the highest-conviction directional read. "
        f"Cross-asset confirmation is needed before treating any claim as actionable. "
        f"Actors: {', '.join(draft.get('actors', ['—'])[:3])}",
        "",
        "---",
        "",
        closing,
    ]
    return "\n".join(lines)

# ── Template registry ─────────────────────────────────────────────────
FORMAT_TEMPLATES: list[tuple[str, Callable, dict]] = [
    ("macro_radar", template_macro_radar, {
        "description": "Structured brief with regime header, contradiction block, asset outlook",
        "weight": 1.0,
        "preferred_regimes": ["mixed", "risk-on"],
        "min_confidence": 30,
    }),
    ("capital_flow_brief", template_capital_flow_brief, {
        "description": "Flow dynamics & narrative-driven allocation emphasis",
        "weight": 1.0,
        "preferred_regimes": ["risk-on", "mixed"],
        "min_confidence": 20,
    }),
    ("narrative_lab", template_narrative_lab, {
        "description": "Full analytical structure: context, narrative, contradiction, strategy",
        "weight": 1.0,
        "preferred_regimes": ["mixed", "risk-off"],
        "min_confidence": 40,
    }),
    ("briefing_board", template_briefing_board, {
        "description": "Table-heavy structured overview with dimension grid",
        "weight": 1.0,
        "preferred_regimes": ["mixed", "risk-on"],
        "min_confidence": 10,
    }),
    ("signal_scan", template_signal_scan, {
        "description": "Signal → Implication → Actionable format with emoji headers",
        "weight": 1.0,
        "preferred_regimes": ["mixed", "risk-off"],
        "min_confidence": 25,
    }),
    ("market_pulse", template_market_pulse, {
        "description": "Quick condensed overview in few lines",
        "weight": 1.0,
        "preferred_regimes": ["risk-on", "mixed", "risk-off"],
        "min_confidence": 5,
    }),
    ("conviction_trade", template_conviction_trade, {
        "description": "Deep dive into one trade setup with risk framework",
        "weight": 1.0,
        "preferred_regimes": ["risk-on", "mixed"],
        "min_confidence": 50,
    }),
    ("contradiction_deep_dive", template_contradiction_deep_dive, {
        "description": "Focus on the divergence between consensus and evidence",
        "weight": 1.0,
        "preferred_regimes": ["mixed", "risk-off"],
        "min_confidence": 35,
    }),
    ("sector_spotlight", template_sector_spotlight, {
        "description": "Zoom into a single sector's narrative and metrics",
        "weight": 1.0,
        "preferred_regimes": ["risk-on", "mixed"],
        "min_confidence": 15,
    }),
    ("asset_claims_table", template_asset_claims_table, {
        "description": "Full table of directional claims with narrative cross-check",
        "weight": 1.0,
        "preferred_regimes": ["mixed", "risk-on", "risk-off"],
        "min_confidence": 10,
    }),
]


# ──────────────────────────────────────────────────────────────────────
#  (C)  FORMAT SELECTOR
# ──────────────────────────────────────────────────────────────────────

@dataclass
class FormatSelector:
    """Selects format, title, opening, closing with weighted randomness,
    anti-repetition history, and confidence gating."""

    history_size: int = 30
    max_same_title_pct: float = 30.0

    # History of recently used items to avoid repetition
    _used_formats: list[str] = field(default_factory=list)
    _used_openings: list[str] = field(default_factory=list)
    _used_closings: list[str] = field(default_factory=list)
    _used_titles: list[str] = field(default_factory=list)

    def pick_format(
        self,
        score: dict,
        phrase_bank: PhraseBank,
        seed: int | None = None,
    ) -> tuple[str, Callable, dict]:
        """Pick a format template using weighted random with anti-repetition
        and confidence gating."""
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()

        confidence = max(
            int(score.get("captivation_score", 50) or 50),
            int(score.get("capital_flow_score", 30) or 30),
            10,
        )
        regime = _safe(score.get("regime", "mixed"), "mixed")

        # Build candidate list with gating: format must have min_confidence <= confidence
        candidates = []
        for name, func, meta in FORMAT_TEMPLATES:
            if meta["min_confidence"] > confidence:
                continue
            # Anti-repetition: penalize recently used formats
            weight = meta["weight"]
            recent_count = self._used_formats.count(name)
            if recent_count > 0:
                decay = 0.5 ** recent_count
                weight *= decay
            # Regime preference boost
            if regime in meta.get("preferred_regimes", []):
                weight *= 1.3
            candidates.append((weight, name, func, meta))

        if not candidates:
            # Fallback: lowest min_confidence formats
            candidates = sorted(
                [(meta["min_confidence"], name, func, meta)
                 for name, func, meta in FORMAT_TEMPLATES],
                key=lambda x: x[0],
            )[:3]
            candidates = [(1.0, name, func, meta) for _, name, func, meta in candidates]

        # Weighted random selection
        weights = [c[0] for c in candidates]
        total = sum(weights)
        if total == 0:
            weights = [1.0] * len(candidates)
            total = len(candidates)
        normalized = [w / total for w in weights]

        idx = rng.choices(range(len(candidates)), weights=normalized, k=1)[0]
        _, name, func, meta = candidates[idx]

        # Track history
        self._used_formats.append(name)
        if len(self._used_formats) > self.history_size:
            self._used_formats.pop(0)

        return name, func, meta

    def pick_opening(
        self, phrase_bank: PhraseBank, seed: int | None = None
    ) -> str:
        """Pick an opening, avoiding recent repeats."""
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()

        available = [
            o for o in phrase_bank.openings
            if o not in self._used_openings[-self.history_size:]
        ]
        if not available:
            available = phrase_bank.openings

        chosen = rng.choice(available)
        self._used_openings.append(chosen)
        if len(self._used_openings) > self.history_size:
            self._used_openings.pop(0)
        return chosen

    def pick_closing(
        self, phrase_bank: PhraseBank, seed: int | None = None
    ) -> str:
        """Pick a closing, avoiding recent repeats."""
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()

        available = [
            c for c in phrase_bank.closings
            if c not in self._used_closings[-self.history_size:]
        ]
        if not available:
            available = phrase_bank.closings

        chosen = rng.choice(available)
        self._used_closings.append(chosen)
        if len(self._used_closings) > self.history_size:
            self._used_closings.pop(0)
        return chosen

    def pick_title(
        self,
        score: dict,
        phrase_bank: PhraseBank,
        seed: int | None = None,
    ) -> str:
        """Pick a title template, fill it, and avoid format repetition."""
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()

        sector = _safe(score.get("sector", "Markets"), "Markets")

        # Choose which title template group to use
        groups = [
            phrase_bank.title_templates_macro,
            phrase_bank.title_templates_market,
            phrase_bank.title_templates_sector,
        ]

        # Anti-repetition: pick group with least recent usage
        group_weights = []
        for g in groups:
            recent_used = sum(
                1 for t in self._used_titles[-self.history_size:]
                if any(t.startswith(tmpl.split("{")[0].strip())
                       for tmpl in g[:1])
            )
            weight = 1.0 / (1.0 + recent_used)
            group_weights.append(weight)

        total_gw = sum(group_weights)
        if total_gw > 0:
            group_weights_n = [w / total_gw for w in group_weights]
        else:
            group_weights_n = [1.0 / 3] * 3

        chosen_group = rng.choices(range(3), weights=group_weights_n, k=1)[0]
        template = rng.choice(groups[chosen_group])
        title = template.format(sector=sector)

        # Enforce max_same_title_pct rule
        same_count = sum(1 for t in self._used_titles if t == title)
        total_titles = max(len(self._used_titles), 1)
        same_pct = (same_count / total_titles) * 100
        if same_pct > self.max_same_title_pct:
            # Pick a different template from a different group
            alt_groups = [g for i, g in enumerate(groups) if i != chosen_group]
            if alt_groups:
                template = rng.choice(rng.choice(alt_groups))
                title = template.format(sector=sector)

        self._used_titles.append(title)
        if len(self._used_titles) > self.history_size * 2:
            self._used_titles.pop(0)

        return title

    def pick_marker(self, phrase_bank: PhraseBank, seed: int | None = None) -> str:
        """Pick an uncertainty marker."""
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()
        return rng.choice(phrase_bank.uncertainty_markers)

    def pick_frame(self, phrase_bank: PhraseBank, seed: int | None = None) -> str:
        """Pick an opinion frame."""
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()
        return rng.choice(phrase_bank.opinion_frames)

    def pick_disclaimer(self, phrase_bank: PhraseBank, seed: int | None = None) -> str:
        """Pick a disclaimer."""
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()
        return rng.choice(phrase_bank.disclaimers)


# ──────────────────────────────────────────────────────────────────────
#  (D)  ORCHESTRATOR
# ──────────────────────────────────────────────────────────────────────

@dataclass
class GazzettaComposer:
    """Orchestrator that ties together PhraseBank, FormatSelector,
    and FormatTemplates to produce varied markdown posts from
    structured editorial data."""

    phrase_bank: PhraseBank = field(default_factory=PhraseBank)
    selector: FormatSelector = field(default_factory=FormatSelector)

    def compose(
        self,
        score: dict | None = None,
        draft: dict | None = None,
        seed: int | None = None,
    ) -> dict:
        """Produce a complete post.

        Args:
            score: A single score dict from phase2_scores ('top' item).
            draft: A single draft dict from reddit_gazzetta_drafts ('items' item).
            seed: Optional random seed for deterministic output.

        Returns:
            dict with keys:
                - body: Complete markdown post (str)
                - title: Post title (str)
                - format_name: Name of the format template used (str)
                - opening: Opening phrase used (str)
                - closing: Closing phrase used (str)
                - marker: Uncertainty marker used (str)
                - frame: Opinion frame used (str)
                - disclaimer: Disclaimer used (str)
                - has_marker: bool
                - has_frame: bool
                - word_count: int
                - generated_at: int (unix timestamp)
        """
        if seed is not None:
            rng = random.Random(seed)
        else:
            rng = random.Random()

        seed_used = seed if seed is not None else rng.randint(0, 2**31)

        # Default data if not provided
        if score is None:
            score = {
                "post_id": "default",
                "title": "Market Signal",
                "sector": "Broad Risk Basket",
                "regime": "mixed",
                "captivation_score": 55,
                "capital_flow_score": 50,
                "beneficiary_score": 45,
                "links": ["https://pureciclismo.github.io/gazzetta-di-kyiv/"],
            }
        if draft is None:
            draft = {
                "rank": 1,
                "headline_hook": "Market Signal Detected",
                "core_claim": "Narrative momentum suggests repricing attention",
                "actors": ["Retail flow", "Narrative amplifiers"],
                "contradiction_map": {
                    "consensus": "Viral = noise",
                    "evidence": "Sustained engagement indicates durable positioning",
                    "implication": "Short horizon assets can reprice before fundamentals catch up",
                },
                "bet_snippet_24_72h": {
                    "instrument": "NASDAQ-100 proxy",
                    "direction": "two-way / selective risk-on",
                    "probability_pct": 58,
                    "projection_pct": "+1.0% to +3.2%",
                    "invalidation": "Engagement decay >50% vs first 12h baseline",
                },
                "links": ["https://pureciclismo.github.io/gazzetta-di-kyiv/"],
            }

        # Select all compositional elements
        format_name, format_func, format_meta = self.selector.pick_format(
            score, self.phrase_bank, seed=seed_used
        )
        title = self.selector.pick_title(
            score, self.phrase_bank, seed=seed_used + 1
        )
        opening = self.selector.pick_opening(
            self.phrase_bank, seed=seed_used + 2
        )
        closing = self.selector.pick_closing(
            self.phrase_bank, seed=seed_used + 3
        )
        marker = self.selector.pick_marker(
            self.phrase_bank, seed=seed_used + 4
        )
        frame = self.selector.pick_frame(
            self.phrase_bank, seed=seed_used + 5
        )
        disclaimer = self.selector.pick_disclaimer(
            self.phrase_bank, seed=seed_used + 6
        )

        # Build body
        body_lines = []

        # Title header
        body_lines.append(f"# {title}")
        body_lines.append("")

        # Timestamp line
        ts = int(time.time())
        body_lines.append(
            f"*Gazzetta di Kyiv — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(ts))}*"
        )
        body_lines.append("")
        body_lines.append("---")
        body_lines.append("")

        # Main body from format template
        body_lines.append(
            format_func(score, draft, opening, closing, marker, frame)
        )

        # Separator + disclaimer
        body_lines.append("")
        body_lines.append("---")
        body_lines.append("")
        body_lines.append(disclaimer)

        # Evidence links
        links = score.get("links", []) or draft.get("links", [])
        if links:
            body_lines.append("")
            body_lines.append("*Sources:*")
            for link in links[:3]:
                if link and link.strip():
                    body_lines.append(f"- {link.strip()}")

        body_lines.append("")
        body_lines.append("READY_FOR_DEVVIT_POST")

        body = "\n".join(body_lines)
        wc = len(re.findall(r"\b\w+\b", body))

        # Ensure at least one uncertainty marker and one opinion frame in the body
        has_marker = marker.lower() in body.lower()
        has_frame = frame.lower() in body.lower()

        return {
            "body": body,
            "title": title,
            "format_name": format_name,
            "opening": opening,
            "closing": closing,
            "marker": marker,
            "frame": frame,
            "disclaimer": disclaimer,
            "has_marker": has_marker,
            "has_frame": has_frame,
            "word_count": wc,
            "generated_at": ts,
        }

    def compose_batch(
        self,
        scores: list[dict],
        drafts: list[dict],
        count: int = 20,
        seed: int | None = None,
    ) -> list[dict]:
        """Produce multiple posts, cycling through data items."""
        results = []
        for i in range(count):
            s = scores[i % len(scores)] if scores else None
            d = drafts[i % len(drafts)] if drafts else None
            s_seed = (seed or 0) + i if seed is not None else None
            result = self.compose(score=s, draft=d, seed=s_seed)
            results.append(result)
        return results

    def reset_history(self) -> None:
        """Reset all anti-repetition tracking."""
        self.selector = FormatSelector()

    def get_homepage_url(self) -> str:
        """Return the Gazzetta homepage URL used in links."""
        return "https://pureciclismo.github.io/gazzetta-di-kyiv/"


# ──────────────────────────────────────────────────────────────────────
#  UTILITY: Load data from pipeline files
# ──────────────────────────────────────────────────────────────────────

def load_pipeline_data(
    repo_root: str | None = None,
) -> tuple[list[dict], list[dict]]:
    """Load structured data from the Gazzetta editorial pipeline.

    Returns (scores_list, drafts_list) where each is a list of dicts.
    """
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    scores_path = os.path.join(repo_root, "data", "phase2_scores.json")
    drafts_path = os.path.join(repo_root, "data", "reddit_gazzetta_drafts.json")

    scores = []
    if os.path.exists(scores_path):
        with open(scores_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        scores = data.get("top", [])

    drafts = []
    if os.path.exists(drafts_path):
        with open(drafts_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        drafts = data.get("items", [])

    return scores, drafts


# ──────────────────────────────────────────────────────────────────────
#  CLI ENTRY POINT
# ──────────────────────────────────────────────────────────────────────

def main() -> None:
    """Run the composer from command line, outputting a single post to stdout."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Gazzetta di Kyiv — Devvit Post Composer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--data-root",
        default=None,
        help="Path to Gazzetta repo root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for deterministic output",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=1,
        help="Number of posts to generate (default: 1)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write batch output files (default: stdout only)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset anti-repetition history before generating",
    )
    args = parser.parse_args()

    composer = GazzettaComposer()

    if args.reset:
        composer.reset_history()

    scores, drafts = load_pipeline_data(args.data_root)

    if args.batch > 1:
        results = composer.compose_batch(scores, drafts, count=args.batch, seed=args.seed)
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            for i, r in enumerate(results):
                fname = f"post_{i+1:03d}_{r['format_name']}.md"
                path = os.path.join(args.output_dir, fname)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(r["body"])
            print(json.dumps({"ok": True, "count": len(results), "output_dir": args.output_dir}))
        else:
            print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        result = composer.compose(
            score=scores[0] if scores else None,
            draft=drafts[0] if drafts else None,
            seed=args.seed,
        )
        print(result["body"])


if __name__ == "__main__":
    main()
