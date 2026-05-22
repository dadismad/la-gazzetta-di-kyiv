#!/usr/bin/env python3
"""
Compare current homepage against target editorial design heuristics and output actionable gaps.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'site' / 'index.html').read_text(encoding='utf-8')
CSS = (ROOT / 'site' / 'styles.css').read_text(encoding='utf-8')

checks = {
    'dark_background': bool(re.search(r'background:\s*#0[0-9a-f]{5}|#07090d', CSS, re.I)),
    'two_column_layout': 'grid-template-columns:2.4fr 1fr' in CSS or 'grid-template-columns: 2.4fr 1fr' in CSS,
    'serif_headlines': 'font-family:Georgia' in CSS,
    'kicker_labels': 'n-kicker' in CSS and 'letter-spacing:.28em' in CSS,
    'top_narratives_section': 'Top Narratives' in HTML,
    'narrative_focus_sidebar': 'Narrative Focus' in HTML,
    'context_action_lines': 'CONTEXT' in CSS or 'Context:' in HTML,
    'no_quant_terms_in_html': not bool(re.search(r'intensity|momentum|score|yield|confidence', HTML, re.I)),
}

score = round(100 * sum(checks.values()) / len(checks), 1)

gaps = []
if not checks['two_column_layout']:
    gaps.append('Main layout should be ~70/30 split with fixed editorial sidebar.')
if not checks['serif_headlines']:
    gaps.append('Use serif headline typography for newspaper tone.')
if not checks['no_quant_terms_in_html']:
    gaps.append('Remove quant/technical labels from homepage copy.')

print(json.dumps({'ok': True, 'score': score, 'checks': checks, 'gaps': gaps}, ensure_ascii=False, indent=2))
