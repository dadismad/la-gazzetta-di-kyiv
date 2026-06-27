# La Gazzetta di Kyiv — Infrastructure Audit

**Version:** 1.0.0 | **Date:** 2026-06-27
**Purpose:** VC-readiness assessment of current architecture and transition plan

---

## Current State

### Compute

| Resource | Spec | Status |
|----------|------|:------:|
| VM | gazzetta-prod (e2-micro, us-central1-a, 3.8GB RAM, 30GB disk, 4.2GB used) | ⚠️ Under-provisioned |
| Python | 3.x venv at /opt/gazzetta-di-kyiv/venv | ✅ |
| Scheduler | systemd timer gazzetta-governor.timer (10-min cycle) | ✅ |

**Risk:** e2-micro with 3.8GB RAM runs the full 16-step pipeline in 10-minute cycles. Memory pressure during synthesis (contradiction_synthesizer.py loads 600+ stories into memory) has caused OOM kills. **Recommendation:** Upgrade to e2-medium (4GB) or e2-standard (8GB) before institutional demo.

### Storage

| Resource | Detail | Status |
|----------|--------|:------:|
| stories.json | 600 stories, 6.8MB | ⚠️ Growing ~5MB/month |
| flows.json | 12 narratives | ✅ |
| gazzetta.db | SQLite, 4.2GB | ⚠️ No backup automation |
| GCS bucket | gs://www.lagazzettadikyiv.com | ✅ |

**Risk:** SQLite at 4.2GB with no automated backup. A VM disk failure = total data loss. **Recommendation:** Automated daily `gcsutil cp` of gazzetta.db to GCS coldline. Cost: ~$0.02/month.

### API Dependencies

| Service | Provider | Limit | Status |
|---------|----------|-------|:------:|
| GLM 5.2 (primary synthesis) | Zhipu AI | Unknown rate limit | ✅ New |
| DeepSeek (fallback synthesis) | DeepSeek | Rate limit tested | ✅ Existing |
| CFTC COT (physical) | SODA API | Public, no key | ✅ |
| CFTC COT (financial) | ZIP download | Public, no key | 🟡 Pending implementation |
| FRED | St. Louis Fed | 120 req/min | ✅ |
| Alpha Vantage | Alpha Vantage | 25 req/day | ⚠️ Very limited |
| Telegram Bot API | Telegram | ~30 msg/sec | ✅ |
| CoinGecko | CoinGecko | Free tier, ~50 calls/min | ✅ |

**Risk:** Alpha Vantage at 25 req/day is the binding constraint for live price data. **Recommendation:** Migrate to Yahoo Finance (no key needed) or Polygon.io free tier (5 req/min, unlimited) for broader coverage.

### Pipeline (16 steps)

```
youtube → arxiv → ingestion → market_data → cftc_data → fred_data → derivatives
→ synthesis → classify → calc_capital → gen_flows → build_frontend → test_platform
→ pulse → telegram_post → deploy
```

| Step | Script | Runtime | Failure Mode |
|------|--------|:-------:|-------------|
| synthesis | contradiction_synthesizer.py | 2-4 min | OOM, API rate limit |
| calc_capital | calculate_capital.py | <5 sec | Degraded data if CFTC/FRED fetch failed |
| build_frontend | build_frontend.py | 30-60 sec | JSON parse errors on corrupted stories |
| deploy | shipit.sh | 15-30 sec | GCS auth expiry |

---

## GLM 5.2 Deployment Schema

```
┌─────────────────────────────────────────────────────┐
│                 contradiction_synthesizer.py          │
│                                                       │
│  ┌─────────────┐     ┌──────────────┐               │
│  │ Ingestion   │────▶│ Build Prompt  │               │
│  │ (DB queue)  │     │ (S.T.I.R.    │               │
│  └─────────────┘     │  Protocol)   │               │
│                       └──────┬───────┘               │
│                              │                        │
│              ┌───────────────▼──────────────┐        │
│              │     PROVIDER ROUTER           │        │
│              │                               │        │
│              │  PRIMARY: GLM 5.2            │        │
│              │  ┌─────────────────────┐     │        │
│              │  │ URL: open.bigmodel. │     │        │
│              │  │ cn/api/paas/v4/     │     │        │
│              │  │ chat/completions    │     │        │
│              │  │ Model: glm-5.2      │     │        │
│              │  │ Timeout: 90s        │     │        │
│              │  └─────────────────────┘     │        │
│              │                               │        │
│              │  FALLBACK: DeepSeek           │        │
│              │  ┌─────────────────────┐     │        │
│              │  │ URL: api.deepseek.  │     │        │
│              │  │ com/chat/completions│     │        │
│              │  │ Model: deepseek-chat│     │        │
│              │  │ Timeout: 90s        │     │        │
│              │  └─────────────────────┘     │        │
│              └───────────────┬──────────────┘        │
│                              │                        │
│              ┌───────────────▼──────────────┐        │
│              │     RESPONSE VALIDATOR        │        │
│              │  - JSON schema compliance     │        │
│              │  - Required field presence    │        │
│              │  - Narrative scoring sanity   │        │
│              │  - Trade thesis completeness  │        │
│              └───────────────┬──────────────┘        │
│                              │                        │
│                       ┌──────▼───────┐               │
│                       │ Write to DB  │               │
│                       │ + stories.json│              │
│                       └──────────────┘               │
└─────────────────────────────────────────────────────┘
```

---

## Microservice Transition Plan (v2.0)

**Current:** Monolithic Python scripts on single VM.
**Target:** Containerized microservices with message queue.

| Phase | Milestone | Benefit |
|:-----:|-----------|---------|
| **I (Now)** | Provider fallback (GLM 5.2 → DeepSeek) | HA for synthesis |
| **II (Q3)** | Dockerize each pipeline step | Reproducibility, parallel scaling |
| **III (Q3)** | Redis/RabbitMQ between steps | Decoupling, retry queues |
| **IV (Q4)** | Kubernetes on GKE | Auto-scaling, zero-downtime deploy |

---

## Tech Debt Identified

| Severity | Issue | Impact |
|:--------:|-------|--------|
| 🔴 | No automated DB backup | Data loss risk |
| 🔴 | e2-micro memory pressure | Pipeline instability |
| 🟡 | SQLite at 4.2GB — approaching practical limits | Query slowdown |
| 🟡 | No API key rotation mechanism | Security |
| 🟡 | Hardcoded paths in 7 scripts (ongoing config.yaml migration) | Brittle deploys |
| 🟢 | P2 deferred items in CTO_STATE.md not tracked | Drift accumulation |
| 🟢 | No monitoring/alerting for pipeline step failures | Silent degradation |

---

## Recommended Immediate Actions (Post-Sprint)

1. Upgrade VM to e2-medium (~$25/month)
2. Automate daily DB backup to GCS
3. Migrate Alpha Vantage → Yahoo Finance free tier
4. Complete config.yaml migration for remaining hardcoded paths
5. Add `pipeline_health` endpoint returning step-level status
