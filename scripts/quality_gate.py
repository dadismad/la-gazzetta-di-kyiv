#!/usr/bin/env python3
"""Quality gate checker for Gazzetta editorial cycle."""

import json
import re
import sys

# Load files
with open('data/publish/telegram_latest.md', 'r') as f:
    telegram = f.read().strip()

with open('data/publish/reddit_latest.md', 'r') as f:
    reddit = f.read().strip()

with open('data/editorial_state.json', 'r') as f:
    state = json.load(f)

with open('data/processed/narrative_intelligence_latest.json', 'r') as f:
    ni = json.load(f)

results = []

# === 1. Word counts ===
tg_words = len(telegram.split())
rd_words = len(reddit.split())
results.append(('TELEGRAM_WORD_COUNT', tg_words, '80-140' if 80 <= tg_words <= 140 else 'FAIL'))
results.append(('REDDIT_WORD_COUNT', rd_words, '180-260' if 180 <= rd_words <= 260 else 'FAIL'))

# === 2. Cross-platform uniqueness (under 40% identical 3-word phrases) ===
def get_trigrams(text):
    words = text.split()
    return set(' '.join(words[i:i+3]) for i in range(len(words)-2))

tg_trigrams = get_trigrams(telegram)
rd_trigrams = get_trigrams(reddit)
if len(tg_trigrams) > 0:
    overlap = len(tg_trigrams & rd_trigrams) / len(tg_trigrams)
else:
    overlap = 0
results.append(('CROSS_PLATFORM_OVERLAP', f'{overlap:.1%}', 'PASS' if overlap < 0.40 else 'FAIL'))

# === 3. Evidence check ===
tg_urls = re.findall(r'https?://[^\s)]+', telegram)
rd_urls = re.findall(r'https?://[^\s)]+', reddit)
results.append(('TELEGRAM_URLS', len(tg_urls), 'PASS' if len(tg_urls) >= 1 else 'FAIL'))
results.append(('REDDIT_URLS', len(rd_urls), 'PASS' if len(rd_urls) >= 1 else 'FAIL'))

# === 4. Anti-template check ===
banned = [
    'second-order effects remain underpriced by consensus',
    'narrative is sensitive to negotiation headlines',
    'transmission effects',
    'repricing whipsaws',
    'narrative acceleration',
    'mention-share',
    'cross-source confirmation',
]

tg_lower = telegram.lower()
rd_lower = reddit.lower()
tg_banned = [p for p in banned if p in tg_lower]
rd_banned = [p for p in banned if p in rd_lower]
results.append(('TELEGRAM_BANNED_PHRASES', tg_banned if tg_banned else 'none', 'FAIL' if tg_banned else 'PASS'))
results.append(('REDDIT_BANNED_PHRASES', rd_banned if rd_banned else 'none', 'FAIL' if rd_banned else 'PASS'))

# === 5. Check Telegram opening != raw thesis from pipeline ===
first_line_tg = telegram.split('\n')[0].strip().lower()
first_line_rd = reddit.split('\n')[0].strip().lower()
setup_theses = [s.get('thesis', '').lower() for s in ni.get('setups', [])]
tg_thesis_match = any(t in first_line_tg for t in setup_theses)
results.append(('TELEGRAM_OPENING_NOT_THESIS', f'match={"yes" if tg_thesis_match else "no"}', 'FAIL' if tg_thesis_match else 'PASS'))

# === 6. Freshness check ===
last_tg = state.get('last_telegram_opening', '').strip()
last_rd = state.get('last_reddit_opening', '').strip()
tg_fresh = first_line_tg != last_tg.lower()
rd_fresh = first_line_rd != last_rd.lower()
results.append(('TELEGRAM_FRESH', 'different' if tg_fresh else 'SAME', 'PASS' if tg_fresh else 'FAIL'))
results.append(('REDDIT_FRESH', 'different' if rd_fresh else 'SAME', 'PASS' if rd_fresh else 'FAIL'))

# === 7. Check :READY_FOR_DEVVIT_POST: tag ===
has_tag = reddit.strip().endswith('READY_FOR_DEVVIT_POST')
results.append(('REDDIT_HAS_TAG', str(has_tag), 'PASS' if has_tag else 'FAIL'))

# Print results
all_pass = True
print('=== QUALITY GATE RESULTS ===')
for name, value, status in results:
    emoji = '✅' if status == 'PASS' or (isinstance(status, str) and status == 'PASS') else '❌'
    if isinstance(value, list):
        value_str = ', '.join(value) if value else 'none'
    else:
        value_str = str(value)
    print(f'  {emoji} {name}: {value_str} -> {status}')
    if isinstance(status, str) and status == 'FAIL' or (isinstance(status, str) and status.startswith('FAIL')):
        all_pass = False
    elif status == 'FAIL':
        all_pass = False

print(f'\nOverall: {"ALL PASS" if all_pass else "SOME CHECKS FAILED"}')
sys.exit(0 if all_pass else 1)
