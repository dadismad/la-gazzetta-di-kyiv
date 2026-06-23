# Competitor Site Accessibility for Browser Agents (June 2026)

## Problem: Premium financial publications block automated browser access

When running focus groups or competitor research, most premium financial sites aggressively block browser automation:

| Site | Bot Protection | Accessible? |
|------|---------------|-------------|
| Bloomberg | Cloudflare + custom challenge | No |
| Financial Times | Cloudflare | No |
| The Economist | Cloudflare | No |
| Reuters | DataDome | No |
| ZeroHedge | None | **Yes** |

## Workflow Impact

Focus group personas that are instructed to "compare against Bloomberg/FT/Economist" will fail when they hit the bot wall. They waste iterations on blocked pages and return useless findings.

## Mitigation

1. **Use ZeroHedge for accessible pattern research** — it's the only major financial publication that allows browser access. It provides valid patterns for article card layout, navigation hierarchy, and timestamp/social-proof elements.

2. **Use web search for blocked sites** — search for "[publication] homepage layout" or "[publication] navigation redesign" to find screenshots, design system documentation, or UX case studies.

3. **Use prior audit knowledge** — the `gazzetta-website` and `focus-group-review` skills contain extensive documentation of Bloomberg/FT/Economist patterns from past sessions where access still worked or was documented from screenshots.

4. **When instructing personas:** explicitly say "Only visit lagazzettadikyiv.com and zerohedge.com. For Bloomberg/FT/Economist patterns, use your training knowledge — do NOT attempt to navigate to their sites."

## Pattern Summary (from training knowledge)

All premium financial publications follow the same structural hierarchy:
- **Masthead first** (publication name at the very top of the page)
- **Horizontal navigation bar** (sections as text links, not ticker-coded pills)
- **Content below** (articles, data, charts)
- **NO sidebar data pills above the masthead**
- **NO ticker codes in navigation chrome**
- **Generous white space signals premium quality**
