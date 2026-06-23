# Phase C Visual Rebuild Specifications
## 2026-06-22

Full rebuild plan for build_frontend.py after file corruption from read_file→write_file line-prefix bug. Git checkout reverted to v3.1 (pre all Phase C features).

## Feature Inventory

| # | Feature | Lines | Complexity | Dependencies |
|---|---------|-------|-----------|--------------|
| F1 | Zoned Stream (BREAKING/ACTIVE/SETTLING) | ~95 | HIGH | Refactors card render loop |
| F2 | Crosshair scatter plot | ~50 | MEDIUM | Isolated JS function |
| F3 | Decay Clock (12h half-life) | ~40 | LOW | Piggybacks on F1 |
| F4 | GAP Leaderboard (top 5) | ~40 | LOW | Isolated JS function |
| F5 | Source Tiers (TIER 1/2) | ~20 | LOW | Piggybacks on F1 |
| F6 | Web Share API button | ~15 | LOW | Replaces copy-link button |
| F7 | Sticky Radar on mobile | ~5 | TRIVIAL | Pure CSS |
| F8 | Settling zone empty state | ~3 | TRIVIAL | Piggybacks on F1 |

## Execution Order

Phase 1 (Foundation): F1 + F3 + F5 + F8 — touch card render loop
Phase 2 (Enhancements): F6 + F4 + F2 — isolated additions
Phase 3 (Polish): F7 — CSS only

## Safe Editing Rules

1. Use `patch` tool or direct Python `open()` — NEVER read_file→write_file
2. Save backup before each phase: `cp build_frontend.py build_frontend.py.bak`
3. Test deploy after each phase: SCP to VM, run build, verify via curl
4. Commit to git after each phase

## Verification

After rebuild, curl deployed HTML for: BREAKING ZONE, ACTIVE SIGNALS, SETTLING NOISE, decay-meter, GAP LEADERBOARD, TIER 1, navigator.share, NARRATIVE CROSSHAIR, sticky;top:56px
Governor must show: 11/11 OK, 156/156 PASS
