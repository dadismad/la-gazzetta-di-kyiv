#!/usr/bin/env python3
"""prepare_publish_payloads_v2.py — v3.0

Aligned with:
- docs/OPERATING_MANDATE.md (narrative-intelligence newspaper)
- docs/SOCIAL_DISTRIBUTION_SYSTEM.md (platform blueprints)
- docs/CROSS_CHANNEL_EDITORIAL_SOP.md (QA gates)
- docs/BRAND_BOOK.md (voice, vision, mission)
- memory: Gazzetta di Kyiv = Narrative Intelligence OS

Produces channel-specific payloads from the canonical narrative_intelligence dataset.
Writes distribution logs for feedback-loop continuity.
"""

from __future__ import annotations
import json, os, random, re
from datetime import datetime, timezone
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP = os.path.join(REPO, 'data', 'processed', 'narrative_intelligence_latest.json')
SITE_HOME = os.path.join(REPO, 'site', 'api', 'v1', 'home')
PUBLISH_DIR = os.path.join(REPO, 'data', 'publish')
CTA_LIB = os.path.join(REPO, 'data', 'cta_library.json')
LEDGER = os.path.join(REPO, 'data', 'human_detail_ledger.md')
DIST_LOG = os.path.join(REPO, 'data', 'social_distribution_log.jsonl')

HOMEPAGE = 'https://pureciclismo.github.io/gazzetta-di-kyiv/'
SETUPS_API = f'{HOMEPAGE}api/v1/home/setups.json'
REGIME_API = f'{HOMEPAGE}api/v1/home/regime.json'
CONTRADICTIONS_API = f'{HOMEPAGE}api/v1/home/contradictions.json'

TELEGRAM_OUT = os.path.join(PUBLISH_DIR, 'telegram_latest.md')
REDDIT_OUT = os.path.join(PUBLISH_DIR, 'reddit_latest.md')
MANIFEST_OUT = os.path.join(PUBLISH_DIR, 'publish_manifest.json')

# ── guardrails (from CROSS_CHANNEL_EDITORIAL_SOP) ──
TELEGRAM_MIN_WORDS, TELEGRAM_MAX_WORDS = 50, 160
REDDIT_MIN_WORDS, REDDIT_MAX_WORDS = 140, 260
CTA_HISTORY_DEPTH = 7  # per platform


def ensure(p: str):
    os.makedirs(p, exist_ok=True)


def word_count(text: str) -> int:
    return len(re.findall(r'\b\w+\b', text))


def first(items, default='pending'):
    if not items:
        return default
    return str(items[0])


def as_pct(v, default='-'):
    try:
        return f"{int(v)}%"
    except Exception:
        return default


# ── human-detail ledger ──────────────────────────────────────

def load_ledger_entries() -> list[dict]:
    """Parse human_detail_ledger.md table rows (non-template only)."""
    entries = []
    if not os.path.exists(LEDGER):
        return entries
    with open(LEDGER, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('| HD-'):
                continue
            cols = [c.strip() for c in line.strip('|\n').split('|')]
            if len(cols) < 7:
                continue
            eid, subject, detail, url, v_at, relevance, notes = cols
            if 'TEMPLATE' in eid or 'REPLACE' in detail:
                continue
            entries.append({
                'id': eid, 'subject': subject, 'detail': detail,
                'source_url': url, 'verified_at': v_at
            })
    return entries


def pick_ledger_entry(setup: dict, entries: list[dict]) -> dict | None:
    """Try to find a ledger entry related to the setup's narrative/actors."""
    actors = [a.lower() for a in setup.get('actors', [])]
    title = setup.get('title', '').lower()
    matched = [e for e in entries
               if any(a in e['subject'].lower() for a in actors)
               or any(a in e['detail'].lower() for a in actors + [title])]
    if matched:
        return matched[0]
    if entries:
        return random.choice(entries)
    return None


def format_human_detail(entry: dict | None) -> str:
    if not entry:
        return "¹ Verified human details pending ledger population."
    return (
        f"¹ {entry['detail']} "
        f"(ledger: {entry['id']}, source: {entry['source_url']})"
    )


# ── CTA rotation tracker ─────────────────────────────────────

def pick_cta(channel: str) -> str:
    """Pick a CTA from the library, avoiding recent reuse."""
    fallback = {
        'telegram': f'Full briefing and positioning map: {HOMEPAGE}',
        'reddit': f'Full narrative dossier and data links: {HOMEPAGE}',
    }.get(channel, f'More: {HOMEPAGE}')

    if not os.path.exists(CTA_LIB):
        return fallback

    try:
        lib = json.load(open(CTA_LIB, 'r', encoding='utf-8'))
        choices = lib.get(channel, [])
        if not choices:
            return fallback

        # Avoid recent reuse: check last CTA_HISTORY_DEPTH posts
        used = []
        if os.path.exists(DIST_LOG):
            with open(DIST_LOG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in reversed(lines[-CTA_HISTORY_DEPTH:]):
                try:
                    rec = json.loads(line.strip())
                    if rec.get('channel') == channel:
                        cta_text = rec.get('cta_used', '')
                        used.append(cta_text)
                except Exception:
                    continue

        available = [c for c in choices if c not in used]
        if not available:
            available = choices  # reset if all used

        return random.choice(available).replace('{website_url}', HOMEPAGE)
    except Exception:
        return fallback


# ── social distribution logger ────────────────────────────────

def log_distribution(narrative_id: str, channel: str, post_type: str,
                     actors: list, sectors: list, framing: str, cta: str,
                     evidence_urls: list, continuity: str, human_detail_id: str,
                     word_cnt: int):
    """Append to social_distribution_log.jsonl."""
    ensure(os.path.dirname(DIST_LOG))
    entry = {
        'narrative_id': narrative_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'channel': channel,
        'post_type': post_type,
        'actors': actors or [],
        'sectors': sectors or [],
        'framing_pattern': framing,
        'cta_used': cta,
        'evidence_urls': evidence_urls or [],
        'continuity_link': continuity,
        'human_detail_id': human_detail_id or 'none',
        'word_count': word_cnt,
        'publish_state': 'ready',
        'schedule_window': 'pending',
    }
    with open(DIST_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# ── content-length guardrails ─────────────────────────────────

def check_word_count(channel: str, wc: int) -> list[str]:
    warnings = []
    if channel == 'telegram':
        if wc < TELEGRAM_MIN_WORDS:
            warnings.append(f'Telegram post under minimum ({wc}<{TELEGRAM_MIN_WORDS} words)')
        if wc > TELEGRAM_MAX_WORDS:
            warnings.append(f'Telegram post over maximum ({wc}>{TELEGRAM_MAX_WORDS} words)')
    elif channel == 'reddit':
        if wc < REDDIT_MIN_WORDS:
            warnings.append(f'Reddit post under minimum ({wc}<{REDDIT_MIN_WORDS} words)')
        if wc > REDDIT_MAX_WORDS:
            warnings.append(f'Reddit post over maximum ({wc}>{REDDIT_MAX_WORDS} words)')
    return warnings


# ── Telegram builder (Rapid Intelligence Terminal) ────────────

def build_telegram(regime: dict, setups: list[dict],
                   contradictions: list[dict]) -> tuple[str, int]:
    """
    Format per SOCIAL_DISTRIBUTION_SYSTEM § Telegram:
    1) Opening signal (1 line)
    2) Immediate implication
    3) Actionable interpretation (1–3 bullets)
    4) Verified human detail (with citation)
    5) Continuity link + next trigger
    6) CTA

    Target: 90–160 words. Concise, sharp, strategic.
    """
    lead = setups[0] if setups else {}
    conts = [c for c in contradictions if
             c.get('narrative') and c.get('urgency') == 'high']
    top_cont = conts[0] if conts else {}

    # narrative_id for logging
    narrative_id = lead.get('setup_id', 'unknown')

    lines = []

    # 1) Opening signal
    signal = lead.get('thesis', 'Narrative intelligence update')
    lines.append(signal)

    # 2) Immediate implication
    regime_label = regime.get('regime_label', 'Mixed')
    risk_state = regime.get('risk_state', 'neutral')
    lines.append('')
    lines.append(
        f'Implication: {regime_label} regime '
        f'({risk_state}) — '
        f'positioning shifts likely within 24–72h.'
    )

    # 3) Actionable interpretation (1–3 bullets)
    lines.append('')
    lines.append('Actionable:')
    bullets = []
    top3 = setups[:3]
    for s in top3:
        title = s.get('title', 'Setup')
        thesis_short = s.get('thesis', '')[:90]
        if thesis_short:
            bullets.append(f'• {title}: {thesis_short}')
    if not bullets:
        bullets.append(f'• Monitor {regime_label} regime for signal evolution.')
    lines.extend(bullets)

    # 4) Verified human detail
    entries = load_ledger_entries()
    hd = pick_ledger_entry(lead, entries)
    lines.append('')
    lines.append(format_human_detail(hd))

    # 5) Continuity link + next trigger
    next_trig = first(lead.get('invalidation_triggers', []))
    lines.append('')
    inval_trigger = f'{top_cont.get("invalidation_window","24-72h")} invalidation: {next_trig}'
    lines.append(f'Continuity: via {HOMEPAGE} | {inval_trigger}')

    # 6) CTA
    cta = pick_cta('telegram')
    lines.append('')
    lines.append(cta)

    body = '\n'.join(lines)
    wc = word_count(body)
    return body, wc


# ── Reddit builder (Narrative Laboratory) ─────────────────────

def build_reddit(regime: dict, setups: list[dict],
                 contradictions: list[dict]) -> tuple[str, int]:
    """
    Format per SOCIAL_DISTRIBUTION_SYSTEM § Reddit (Narrative Lab):
    1) Context
    2) Dominant narrative
    3) Contradiction
    4) Second-order implications
    5) Strategic interpretation (24–72h + invalidation)
    6) Verified human detail (with citation)
    7) Discussion prompt
    8) CTA

    Target: 180–260 words. Concise, analytical, falsifiable.
    """
    lead = setups[0] if setups else {}
    conts = [c for c in contradictions if c.get('narrative')]
    top_cont = conts[0] if conts else {}
    narrative_id = lead.get('setup_id', 'unknown')

    lines = []

    # 1) Context
    lines.append(f'**Regime:** {regime.get("regime_label", "Mixed")} '
                 f'({regime.get("risk_state", "neutral")})')
    lines.append('')
    lines.append(f'*Context:* Data compiled {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} '
                 f'— {regime.get("source_count",0)} sources, {len(setups)} setups, '
                 f'{len(contradictions)} contradictions.')

    # 2) Dominant narrative
    lines.append('')
    lines.append('**Dominant narrative:**')
    actors = ', '.join((lead.get('actors') or ['policy and market actors'])[:4])
    incentives = ', '.join((lead.get('incentives') or ['reprice risk'])[:3])
    lines.append(
        f'{lead.get("thesis", "Narrative underway")}. '
        f'Key actors: {actors}. Incentives: {incentives}.'
    )

    # 3) Contradiction (explicit — key differentiator)
    lines.append('')
    lines.append('**Contradiction:**')
    if top_cont and top_cont.get('claim_a') and top_cont.get('claim_b'):
        lines.append(
            f'Consensus says *{top_cont["claim_a"]}*, but '
            f'*{top_cont["claim_b"]}*. '
            f'This gap creates repricing potential '
            f'(urgency: {top_cont.get("urgency","medium")}).'
        )
    else:
        lines.append(
            'Consensus narrative is converging without clear contradiction. '
            'Monitor for divergence signal.'
        )

    # 4) Second-order implications
    lines.append('')
    lines.append('**Second-order:**')
    retail_exec = lead.get('retail_execution', ['Position with staged entries'])
    if retail_exec:
        for i, ex in enumerate(retail_exec[:2]):
            lines.append(f'• {ex}')
    lines.append(
        f'• Cross-asset: {regime.get("regime_label","Mixed").lower()} '
        f'regimes historically compress within 24h of '
        f'the first {lead.get("title","").lower()} breakout.'
    )

    # 5) Strategic interpretation (24–72h + invalidation)
    lines.append('')
    lines.append('**24–72h path:**')
    lines.append(
        f'Base {as_pct(lead.get("probability_base"))} / '
        f'Bull {as_pct(lead.get("probability_bull"))} / '
        f'Bear {as_pct(lead.get("probability_bear"))}'
    )
    inval_trigs = lead.get('invalidation_triggers', [])
    lines.append(f'Invalidation: {first(inval_trigs)}')
    if len(inval_trigs) > 1:
        lines.append(f'Secondary: {inval_trigs[1]}')

    # 6) Verified human detail
    entries = load_ledger_entries()
    hd = pick_ledger_entry(lead, entries)
    lines.append('')
    lines.append(format_human_detail(hd))

    # 7) Discussion prompt
    lines.append('')
    lines.append(
        '**Discussion:** What signals would falsify or strengthen '
        f'this {lead.get("title","narrative")[:60]} thesis '
        'in your framework?'
    )

    # 8) Evidence + CTA
    lines.append('')
    lines.append('Evidence:')
    lines.append(f'• Homepage: {HOMEPAGE}')
    lines.append(f'• Setups API: {SETUPS_API}')
    lines.append(f'• Contradictions API: {CONTRADICTIONS_API}')
    lines.append('')
    cta = pick_cta('reddit')
    lines.append(cta)
    lines.append('')
    lines.append('READY_FOR_DEVVIT_POST')

    body = '\n'.join(lines)
    wc = word_count(body)
    return body, wc


# ── main ──────────────────────────────────────────────────────

def main():
    d = json.load(open(INP, 'r', encoding='utf-8'))
    setups = d.get('setups', [])
    contradictions = d.get('contradictions', [])
    regime = d.get('regime', {})

    ensure(SITE_HOME)
    ensure(PUBLISH_DIR)

    # Write site API payloads (ecosystem contract)
    json.dump({'generated_at': d.get('generated_at'), 'items': setups},
              open(os.path.join(SITE_HOME, 'setups.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    json.dump({'generated_at': d.get('generated_at'), 'items': contradictions},
              open(os.path.join(SITE_HOME, 'contradictions.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    json.dump(regime,
              open(os.path.join(SITE_HOME, 'regime.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    # Build channel payloads
    tg_body, tg_wc = build_telegram(regime, setups, contradictions)
    rd_body, rd_wc = build_reddit(regime, setups, contradictions)

    tg_warnings = check_word_count('telegram', tg_wc)
    rd_warnings = check_word_count('reddit', rd_wc)

    open(TELEGRAM_OUT, 'w', encoding='utf-8').write(tg_body)
    open(REDDIT_OUT, 'w', encoding='utf-8').write(rd_body)

    # Log distributions
    lead = setups[0] if setups else {}
    narrative_id = lead.get('setup_id', 'unknown')
    actors = lead.get('actors', [])
    evidence = [HOMEPAGE, SETUPS_API, CONTRADICTIONS_API]

    log_distribution(
        narrative_id=narrative_id,
        channel='telegram',
        post_type='narrative_update',
        actors=actors,
        sectors=[],
        framing=lead.get('thesis', '')[:80],
        cta=pick_cta('telegram'),
        evidence_urls=evidence,
        continuity=f'{HOMEPAGE} | invalidation: {first(lead.get("invalidation_triggers",[]))}',
        human_detail_id=load_ledger_entries()[0]['id'] if load_ledger_entries() else 'none',
        word_cnt=tg_wc,
    )

    log_distribution(
        narrative_id=narrative_id,
        channel='reddit',
        post_type='narrative_lab',
        actors=actors,
        sectors=[],
        framing=lead.get('thesis', '')[:80],
        cta=pick_cta('reddit'),
        evidence_urls=evidence,
        continuity=f'{HOMEPAGE} | invalidation: {first(lead.get("invalidation_triggers",[]))}',
        human_detail_id=load_ledger_entries()[0]['id'] if load_ledger_entries() else 'none',
        word_cnt=rd_wc,
    )

    # Manifest
    manifest = {
        'ok': True,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'inputs': {
            'setups': len(setups),
            'contradictions': len(contradictions),
            'regime_label': regime.get('regime_label'),
        },
        'outputs': {
            'telegram_markdown': TELEGRAM_OUT,
            'reddit_markdown': REDDIT_OUT,
            'site_regime_api': os.path.join(SITE_HOME, 'regime.json'),
            'site_setups_api': os.path.join(SITE_HOME, 'setups.json'),
            'site_contradictions_api': os.path.join(SITE_HOME, 'contradictions.json'),
        },
        'quality': {
            'telegram_word_count': tg_wc,
            'reddit_word_count': rd_wc,
            'telegram_range': f'{TELEGRAM_MIN_WORDS}-{TELEGRAM_MAX_WORDS}',
            'reddit_range': f'{REDDIT_MIN_WORDS}-{REDDIT_MAX_WORDS}',
            'telegram_warnings': tg_warnings,
            'reddit_warnings': rd_warnings,
        },
        'channel_profiles': {
            'telegram': 'Rapid Intelligence Terminal: signal → implication → actionable → human_detail → continuity → CTA',
            'reddit': 'Narrative Lab: context → narrative → contradiction → second-order → strategy → human_detail → discussion → CTA',
        },
    }
    json.dump(manifest, open(MANIFEST_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == '__main__':
    main()
