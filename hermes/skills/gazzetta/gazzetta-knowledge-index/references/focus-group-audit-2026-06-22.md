# Focus Group Audit — June 22, 2026

Five-persona parallel audit of production Gazzetta di Kyiv (v3.2).

## Scores

| Audit | Score | Persona |
|-------|-------|---------|
| Telegram Broadcast | 7.5/10 | Systems auditor |
| Site Colours | 8.5/10 | Design auditor |
| Features Usability | 5.5/10 | UX auditor |
| Operational State | 8.5/10 | SRE auditor |
| Usage Feasibility | 4.0/10 | $5B Portfolio Manager |
| **Weighted average** | **6.8/10** | — |

## Critical Findings

### P0 — Tactical Radar is Dead (Deploy Sync Issue, Not Code Bug)
**CORRECTION (post-audit diagnosis):** The radar is NOT broken by code. `build_frontend.py` correctly injects derivatives data at build time via the `__DERIVATIVES_JSON__` placeholder (line 264). The VM's local `index.html` has live derivatives data. The CDN serves a stale build from 19:41 UTC with `DERIVATIVES = {}`. Root cause: silently stale deploy (pitfall 51). Fixing the deploy sync fixes the radar automatically — no code change needed in the JS template.

### P0 — Capital Data Credibility Gap
PM verdict: "Capital flows are mostly $0; no CFTC/FRED evidence found. A $5B portfolio cannot allocate capital based on a black-box algorithm." The pipeline IS producing real CFTC/FRED data (56 TIER_1, 50 TIER_2 stories) but the frontend shows no data source attribution or fidelity tiering. Fix: fidelity badges on cards + methodology section in About tab.

### P1 — Crimson Inconsistency
Badges use `#8B0000` per spec, BREAKING article borders use `#7F1D1D` from Tailwind palette. Fix: replace all `#7F1D1D` with `#8B0000`.

### P1 — Watchdog Service Broken
`health_check.py` line 11 points to `/data/stories-v4.json` (404). Fix: change to `/data/stories.json`.

### P1 — flows.json Deploy Gap
Governor generates fresh `flows.json` but CDN serves 4-hour-stale version. Fix: explicit `gsutil cp` with `Cache-Control: no-store` in deploy step.

### P2 — Missing Deep-Links
Share buttons construct `?story={id}` but nothing reads it on load. Telegram posts link to homepage. Fix: DOMContentLoaded listener + `?story=` handler in JS.

### P2 — No Narrative Filter on Stream Tab
Users can only filter by tier and source on main feed. Narrative filtering exists only in Contradictions tab. Fix: add narrative filter pills to Stream.

### P2 — Mobile Touch Targets Below 44px
Bottom nav buttons lack `min-h-[44px]`. Glossary tooltips block scroll on mobile.

## Post-Audit Diagnosis: Telegram Channel Mix-Up

Both governor operational alerts (`tg_send`) and editorial broadcasts (`send_telegram`) default to the same chat ID `-1003990434181`. Every 10-minute cycle sends `*Gazzetta* — HH:MM UTC\nN stories | X/Y steps OK` to the public subscriber channel. Fix: separate the chat IDs — governor alerts go to a private admin group, broadcast stays on public channel. Governor line 54 change needed.

## Design Shift (Approved, Not Executed)

Dark terminal (#0A0A0F / #E6E4E0) → warm paper (#FAF9F6 / #1A1C1A) with three-colour palette:
- White: #FAF9F6 background
- Gold: #D4AF37 decorative, #8C7123 text (WCAG AA)
- Roman Purple: #66023C masthead/headings

Full colour map documented in session. Estimated 90-minute build_frontend.py refactor (~50 search-replace operations).
