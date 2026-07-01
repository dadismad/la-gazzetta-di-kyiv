# RU Fintech Terminology — Gazzetta di Kyiv (v23.19)

Professional Russian localization guide. Do NOT use literal Google Translate — use trading-floor terminology familiar to Russian-speaking quants, macro analysts, and retail traders who follow channels like MMI, Bitkogan, RationalAnswer.

## Core Terminology Upgrades

| Old (generic) | New (professional) | Rationale |
|---|---|---|
| Противоречия | **Асимметрия** | "Противоречие" = contradiction in logic. "Асимметрия" = price-narrative gap — the actual math |
| Убежденность | **Прогнозная вероятность** | "Убежденность" = belief. "Прогнозная вероятность" = computed probability — data, not opinion |
| уверенность | **вероятность** | Same distinction — confidence is computed, not felt |
| Action Triggers | **Триггеры Позиций** | English "Action Triggers" is lazy. Russian traders say "триггер на вход" |
| Flow Telemetry | **Телеметрия Потоков** | Institutional-grade term. "Данные потоков" is acceptable but weaker |
| Trust Framework | **Рамка Доверия** | E-E-A-T widget label |
| Contradiction | **Асимметрия** | Throughout — the score measures asymmetry, not contradiction |
| Confidence (noun in flows) | **вероятность** | Lowercase — it's a metric, not a title |

## Context-Sensitive Translations

| EN key | RU value | Where used |
|--------|----------|------------|
| `hero_contradictions` | Асимметрия | Hero indicator label |
| `conviction_` | Прогнозная вероятность | Conviction badge label |
| `conviction_HIGH` | ВЫСОКАЯ | Badge tier |
| `conviction_MED` | СРЕДНЯЯ | Badge tier |
| `conviction_LOW` | НИЗКАЯ | Badge tier |
| `flow_confidence_pct` | вероятность | Flow detail |
| `asymmetry_label` | Асимметрия | Sidebar gauge label |
| `prob_label` | Прогнозная вероятность | Probability badge |
| `svc_trader_title` | Триггеры Позиций | Service persona card |
| `svc_action_triggers` | Триггеры Позиций | Service persona card |
| `trust_framework` | РАМКА ДОВЕРИЯ | Trust widget label |
| `183_assertions` | 183 утверждения верификации | Trust widget row |
| `live_vm` | Облачный сервер | Cloud brain status |
| `eeat_expertise` | Экспертиза | E-E-A-T row |
| `eeat_authority` | Авторитет | E-E-A-T row |
| `eeat_trust` | Доверие | E-E-A-T row |

## Channel-Style Tone Rules

1. **No passive voice in RU headlines** — Russian financial readers expect active, direct language. "Был зафиксирован отток" → "Зафиксирован отток".
2. **Keep INTEL/ALPHA untranslated** — These are product labels, not content. Russian traders recognize them as platform taxonomy.
3. **BUY/SELL/WATCH** — Keep English. Russian trading platforms (Tinkoff, Alfa-Direct) use English direction labels.
4. **Numbers in Roman numerals** — "2.4×" stays "2.4×", not "2,4×". Russian quants use decimal points in charts.
5. **$ and B/M suffixes** — Keep Western: "$88B" not "88 млрд $" — financial professionals read both.
