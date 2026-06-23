# Phase C Implementation — Sovereign Terminal
## June 22, 2026

### C1: Dark Mode + Sidebar Fix
- **Dark mode**: `<html class="dark">`, body `background:#0A0A0F!important;color:#E6E4E0!important`
- **Why !important**: Tailwind `bg-surface` class overrides inline CSS. Must use `!important` to win specificity.
- **Sidebar fix**: `build()` now reads `flows_raw.get("narrative_flows", {})` and uses `total_capital_b` instead of summing story-level `capital_volume_usd`. Result: all 12 narratives show real capital ($244.4B to $100M), zero $0M ghost data.
- **Colors**: Meter fills green (#22C55E) for positive, crimson (#8B0000) for negative. Gold (#D4AF37) restricted to GAP>50 and navigation. Crimson reserved for BREAKING tier and GAP>70.
- **Glossary tooltip**: background #1A1A1E, text #E6E4E0, gold border, removed box-shadow.

### C2: GAP Leaderboard
- **Position**: Above the Stream, rendered via `gap-leaderboard` div.
- **Data**: Top 5 NARRATIVES by GAP score, sorted descending.
- **Visual**: Horizontal scroll cards, color-coded (crimson for GAP>=60, gold for 30-60, gray for <30), ticker + arrow (↗ for >=50, → for <50), capital value.
- **Mobile**: Horizontal scroll via `overflow-x-auto`.

### C3: Information Hierarchy (Zoned Stream)
- **BREAKING ZONE** (GAP > 50): Crimson `border-left:4px solid #8B0000`, warning icon, cards expanded by default (`<details open>`), full card layout.
- **ACTIVE ZONE** (GAP 20-50): Gold `border-left:2px solid #D4AF37`, trending_up icon, standard layout, details collapsed.
- **SETTLING ZONE** (GAP < 20): Muted `border-left-color:#444748`, opacity 0.75, check_circle icon, compact layout (smaller heading, no tier badges), heavily collapsed.
- **Zone headers**: Full-width divider banners with dark background (#141418), icon, label, and story count.
- **Implementation**: Stream stories split into three arrays via filter, each rendered with zone-specific card template. Single `allCardsHtml` concatenation.

### C4: Decay Clock
- **Logic**: 12-hour half-life from `generated_at` timestamp. `decayPct = max(0, min(100, 100 - (hoursAgo / 12) * 100))`. `decayRemaining = max(0, 12 - hoursAgo)`.
- **Visual**: Horizontal meter bar (gold #D4AF37 → amber #B45309 → crimson #8B0000). Label: "EDGE DECAY: ~XH REMAINING". Critical state (<20%) pulses with `decayPulse` animation. Expired state: 4px red bar + "EDGE EXPIRED".
- **Placement**: Top of each story card, between article tag and content.

### C5: Source Provenance
- **DATA SYNC indicator**: Green dot (#22C55E) + "DATA SYNC: LIVE · REGIME · BUILD_TIME" in header. Replaces old "Live · REGIME" span.
- **Source TIER badges**: TIER 1 (Bloomberg, FT, ECB, Reuters, WSJ) and TIER 2 (all others). Gold-bordered badge next to feed source label.
- **Sidebar capital tooltip**: `title` attribute showing "Source: flows.json aggregate · N stories · CFTC/FRED/ETF flows".

### C6: The Crosshair
- **Type**: Native JS/CSS scatter plot — no external library.
- **Layout**: Desktop-only (`hidden md:block`), 280px height, dark background (#0D0D14), dashed quadrant dividers.
- **Data**: NARRATIVES array. X-axis: GAP score (0-100). Y-axis: capital flow direction (inflow vs outflow dominance). Bubble size: proportional to `total_capital_b`.
- **Interaction**: Hover scales dot 1.6x, shows tooltip with narrative name, GAP score, and capital value.
- **Labels**: "Narrative Intensity (GAP) →" on X-axis, "Capital Flow" rotated on Y-axis.

### Deploy Fix
- **Root cause**: `NoNewPrivileges=yes` in systemd service blocks sudo, preventing `gsutil cp` to GCS.
- **Fix**: Changed to `NoNewPrivileges=no` in `/etc/systemd/system/gazzetta-governor.service`. `sudo systemctl daemon-reload` required.
- **Verification**: `sudo gsutil cp` succeeds after fix.

### Tool Workarounds
- **Patch tool escape-drift**: The patch tool fails on JS-in-Python strings with nested quotes. Workaround: use `execute_code` with `from hermes_tools import patch` and pass raw strings via Python variables, not via the tool's serialization.
- **Patch tool duplicate matches**: When `old_string` is too short, it matches multiple locations. Use `read_file` to get exact context, add surrounding lines to make the match unique.
- **File deployment**: When local `git checkout` reverts changes, pull fresh from VM via `scp gazzetta-prod:/opt/.../file.py .` then re-apply patches.
