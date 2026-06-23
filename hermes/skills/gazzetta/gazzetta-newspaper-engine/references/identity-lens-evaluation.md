# Identity-Lens Feature Evaluation Framework
## June 22, 2026

When evaluating any proposed feature, external prompt, or handover recommendation for La Gazzetta di Kyiv, run it through the identity lens before executing. The platform is an **institutional-grade geopolitical-finance intelligence terminal** — not a consumer news app, not a social platform, not a blog.

## The Gate Question

*Would a hedge fund analyst pay for this, or does it feel like a consumer product?*

If the answer is "consumer product," reject or defer unless the user explicitly overrides.

## Evaluation Categories

### EXECUTE — Institutional DNA
Features that reinforce the terminal identity:
- Data density, quantitative rigor, real-time indicators
- Transparency (source provenance, methodology tooltips)
- Professional formatting (GapFire dispatch, structured trade theses)
- Persistent awareness tools (sticky tickers, decay clocks, radar)
- Private sharing (Web Share API, native OS share sheets — no Facebook/Twitter icons)
- Premium visual depth (glassmorphism, backdrop-filter, layered depth)

### DEFER — Not Urgent But Not Harmful
Features that don't damage identity but add complexity without clear ROI:
- User personalization state (pinning narratives, localStorage preferences)
- UI pattern libraries from consumer apps (bottom nav bars, tab bars)
- Features that require ongoing state management across sessions

### REJECT — Consumer App Anti-Patterns
Features that actively damage institutional credibility:
- Swipe gestures (Tinder-style curation) — traders scan, they don't swipe
- Social media sharing icons (Facebook, Twitter, Instagram logos)
- Emoji-heavy or casual language
- "Engagement" metrics (likes, comments, view counts)
- Any UI that suggests entertainment rather than intelligence

## Application Pattern

For each item in a proposal or handover document:

1. State the feature
2. Classify as EXECUTE / DEFER / REJECT
3. One-sentence reasoning tied to the identity lens
4. If EXECUTE: specify implementation approach (CSS-only, JS, HTML change)

## Examples from June 22 Session

| Feature | Verdict | Reasoning |
|---------|---------|-----------|
| Sticky Tactical Radar on mobile | EXECUTE | Bloomberg-style persistent ticker — pure institutional |
| Web Share API (native share sheet) | EXECUTE | Private sharing via Signal/Telegram/WhatsApp — no social branding |
| Glassmorphism (backdrop-filter) | EXECUTE | Premium depth at zero cost — institutional aesthetic |
| localStorage "pin" narratives | DEFER | Consumer personalization — traders want all signals |
| Bottom app-bar navigation | DEFER | iOS pattern — current horizontal tabs are more Bloomberg-like |
| Swipe gestures (dismiss/watchlist) | REJECT | Tinder for geopolitics — destroys credibility |
| Facebook/Twitter share icons | REJECT | Consumer social media — antithetical to terminal identity |
