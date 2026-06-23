# RU Force-Translate Gate (v23.22)

## Problem
Before v23.22, the Russian version of the site could drift from the English version. If `translate_content.py` failed silently or was skipped during a deploy, the RU site would serve stale content. Users would see English text leaking through or outdated stories.

## Solution: Atomic Twin Enforcement

Added Stage 2.6 to `shipit.sh` that BLOCKS deploy if RU story count < EN story count.

### Gate Logic

```bash
# ═══ Stage 2.6: RU Sync Gate — Atomic Twin enforcement ═══
EN_COUNT=$(python3 -c "import json; d=json.load(open('$PROJECT/site/data/stories.json')); print(len([d.get('lead')]+d.get('stories',[])))")
RU_COUNT=$(python3 -c "import json; d=json.load(open('$PROJECT/site/data/stories_ru.json')); print(len([d.get('lead')]+d.get('stories',[])))")

if [ "$RU_COUNT" -lt "$EN_COUNT" ]; then
  echo "RU stories ($RU_COUNT) < EN stories ($EN_COUNT) — running translate_content.py"
  $PYTHON "$PROJECT/scripts/translate_content.py"
  RU_COUNT_NEW=$(python3 -c "...")
  if [ "$RU_COUNT_NEW" -lt "$EN_COUNT" ]; then
    echo "CRITICAL: RU sync failed. Aborting deploy."
    exit 1
  fi
fi
```

### Trust Page Mirroring

The gate also copies missing trust pages from EN → RU directory:
```
about.html, capital.html, data.html, methodology.html, 
sources.html, terms.html, robots.txt, sitemap.xml
```

This ensures the RU site has ALL the same static pages as EN, even if not translated yet.

## RU Terminology Standards

Professional trading-desk terminology, not literal machine translations:

| EN | RU | Context |
|----|-----|---------|
| Stories | Интел-Репорты | Not "Стори" or "История" |
| Trades | Альфа-Позиции | Not "Сделки" |
| Asymmetry | Асимметрия | Not "противоречие" |
| Conviction Probability | Прогнозная вероятность | Not "убежденность" |
| Flow Telemetry | Телеметрия Потоков | Institutional tone |
| Trust Framework | Рамка Доверия | E-E-A-T widget |
| Signal | Сигнал | Standard |
| Track Record | Трек-Рекорд | Financial term |
| Active Positions | Активные Позиции | Trading term |

## Live Verification

After every deploy, verify EN and RU story counts match:
```bash
curl -s https://www.lagazzettadikyiv.com/data/stories.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len([d.get('lead')]+d.get('stories',[])))"
curl -s https://www.lagazzettadikyiv.com/data/stories_ru.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len([d.get('lead')]+d.get('stories',[])))"
```
