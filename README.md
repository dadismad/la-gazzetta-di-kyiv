# La Gazzetta di Kyiv

**Enterprise-Grade Autonomous Financial News Pipeline**

*"What capital believes vs. what capital does."*

---

## Overview

La Gazzetta di Kyiv is an autonomous, LLM-driven financial intelligence newspaper that monitors 12 macroeconomic narratives through the lens of **contradiction analysis** — measuring the gap between institutional narrative ("they say") and capital flow reality ("reality").

**Core thesis:** Capital flows reveal what institutions won't say. Every story surfaces the contradiction between media/analyst consensus and actual capital movement, quantified as a 0–100 GAP score.

### The 12 Destination Narratives

| Narrative | Tag | Focus |
|-----------|-----|-------|
| Sovereign Liquidity Migration | Dollar Decline | De-dollarization, reserve diversification |
| Industrial Reshoring & Defense Hegemony | Deglobalization | Supply chain repatriation, defense industrial base |
| Longevity & Bioreality | Gene Editing | Biotech, anti-aging, synthetic biology |
| Decentralized Capital Architecture | Crypto Reserve | Bitcoin reserves, DeFi, stablecoin regulation |
| Compute Hegemony & Intelligence Infrastructure | AI Chips | GPU supply chains, AI infrastructure buildout |
| Eurasia Capital Architecture | China Ascent | BRI, RMB internationalization, China tech |
| Physical Resource Revaluation | Commodity Supercycle | Critical minerals, energy metals, food security |
| Energy Sovereignty | Energy Sovereignty | Nuclear renaissance, grid independence |
| Liquidity Regime Transition | Rate Cycle | Central bank policy, yield curve dynamics |
| Orbital Industrialization & Defense | Space Economy | Space manufacturing, orbital infrastructure |
| Enterprise Intelligence Consolidation | Tech Convergence | AI enterprise adoption, M&A, platform consolidation |
| Trophy Asset Financialization | Wealthy Sports | Sports team valuations, franchise economics |

---

## Architecture

### Pipeline (16-step DAG)

```
youtube → arxiv → ingestion → market_data → cftc_data → fred_data → derivatives
    → synthesis → classify → calc_capital → gen_flows
    → build_frontend → test_platform → pulse → telegram_post → deploy
```

Runs on a 10-minute governor cycle via systemd timer on GCP VM.

### Technology Stack

- **Synthesis:** DeepSeek V4 (LLM contradiction analysis)
- **Data:** SQLite (`gazzetta.db`), FRED API, CFTC COT, yfinance, YouTube Data API v3, arXiv API
- **Frontend:** Static HTML/CSS/JS deployed to GCS (`gs://www.lagazzettadikyiv.com`)
- **Distribution:** Telegram broadcast (6-format dispatch), web (`lagazzettadikyiv.com`)
- **Infrastructure:** GCP Compute Engine, GCS static hosting, GCP Secret Manager
- **Sovereign Vault:** Structured data lake for institutional research, patents, central bank papers

### Repository Structure

```
lagazzettadikyiv/
├── scripts/           # Pipeline executables (16 steps + utilities)
├── data/              # JSON state files, narratives config, market data
│   └── vault/         # Sovereign Vault — raw research intake
├── public/            # Built frontend (deployed to GCS)
│   └── data/          # Generated JSON (stories.json, flows.json)
├── design/            # Design briefs, UX specifications
├── docs/              # Identity reports, monetisation plan, architecture docs
├── ops/               # Operational playbooks
├── distribution/      # Telegram format templates, broadcast config
├── schemas/           # JSON schema definitions
├── templates/         # HTML templates
├── archive/           # Deprecated/superseded files
├── playbooks/         # Runbooks and troubleshooting guides
├── .env.example       # Environment variable template
├── governor.py        # Main pipeline orchestrator (systemd)
└── deploy_to_gcs.py   # GCS deployment with CDN invalidation
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/pureciclismo/gazzetta-di-kyiv.git
cd gazzetta-di-kyiv

# Configure
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run full pipeline
python scripts/governor.py --once
```

### Requirements

- Python 3.11+
- API keys: DeepSeek, Telegram, YouTube Data API v3, AlphaVantage, FRED
- GCP credentials for deployment (optional for local dev)

---

## Monetisation

Freemium model with client-side feature gating via Clerk + Stripe:
- **Free tier:** GAP ≤ 70 stories, delayed Telegram broadcast
- **Pro tier ($199/mo):** Full GAP spectrum, real-time alerts, trade theses
- **Institutional ($2,500/mo):** API access, raw data feeds, Macro Dossiers

---

## Deployment

```bash
# Full deploy to GCS + CDN invalidation
python scripts/deploy_to_gcs.py

# Frontend only (staging)
python scripts/build_frontend_staging.py
```

Production: `https://lagazzettadikyiv.com`

---

## License

Proprietary. All rights reserved.

---

*Built with Hermes Agent. Governed by the contradiction.*
