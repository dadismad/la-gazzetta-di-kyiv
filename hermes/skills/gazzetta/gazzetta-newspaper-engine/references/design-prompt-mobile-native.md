# Mobile-Native Design Prompt for La Gazzetta di Kyiv

Prepared for external design tools (Variant, Google Stitch, etc.). Reflects the C-Suite
mobile-first strategy decision of June 2026: every reader arrives from Telegram on a phone.

## Google Stitch Prompt

```
Mobile-native financial newspaper design for "La Gazzetta di Kyiv." Every design decision
must be justified for a phone screen held in one hand.

READER JOURNEY:
1. Reader sees Telegram post with a contradiction hook
2. Taps link, lands on the STORY PAGE, not the homepage
3. Reads the story, scrolls to the contradiction breakdown
4. Maybe taps the masthead to discover the full feed
5. Never touches a desktop

This means the story page is the real homepage. The feed is secondary.

STORY PAGE LAYOUT (what 90% of readers see):
Top to bottom in a single column:
- Compact masthead bar (48px): crimson name + gold underline. Tapping it goes to feed.
- Story headline: 22px Playfair Display, dark ink, 3-4 lines max, tight leading
- Timestamp + tier badge inline (BREAKING in red pill, DEVELOPING in gold, etc.)
- Source attribution: 11px grey
- THE CONSENSUS block: 14px, grey left-border
- THE REALITY block: 14px, gold left-border
- Contradiction meter: horizontal bar, 0-100, grey-to-crimson gradient
- Capital impact: "Volume at stake: $4.2B" in gold, proportional horizontal bar
- Entity tags: small grey pills
- Narrative tag: tappable, leads to filtered feed
- Related stories: 2-3 compact cards below

FEED PAGE (discovery, secondary):
- Same compact masthead
- Story cards stacked vertically, 1px gold separators
- Each card: headline (18px), contradiction score badge, capital bar, tier badge,
  3-line consensus/reality snippet
- 2 cards visible per screen (iPhone SE)
- No images, no thumbnails — text is the asset

NAVIGATION:
Hidden behind a single icon. Opens a bottom sheet (thumb-reachable).
8 narrative domains as tappable rows. Dismiss with swipe down or tap outside.

TYPOGRAPHY:
- Playfair Display for headlines only. Inter for everything else.
- Body minimum 16px. Metadata minimum 12px.
- Line height: 1.5 for body, 1.2 for headlines.
- Maximum 65 characters per line on body text.

COLOR SYSTEM:
- Page background: #FAF9F6 (warm white, easier on eyes than pure white)
- Primary text: #1A1A1A
- Secondary text: #64748B
- Gold: #D4AF37 for borders, #B8860B for gold text (WCAG AA)
- Crimson: #8B0000 for breaking signals
- Dark navy: #1A1F2E for bottom sheet and overlays

SPACING:
- 16px horizontal padding
- 24px vertical spacing between card sections
- 12px between related elements within a section
- 48px minimum tap target height

PERFORMANCE:
- No JavaScript frameworks, zero dependencies
- First paint under 1 second on 4G
- CSS under 12KB, JS under 20KB
- No images (text-only design)

INTERACTION:
- Tap masthead → feed
- Tap narrative tag → filtered feed
- Tap entity tag → filtered feed
- Tap related story card → that story
- Pull down → refresh
- Bottom sheet → 8 domains
- No hover states, no carousels, no modals on mobile

DESKTOP FALLBACK:
- Single column, max-width 680px, centered
- Bottom sheet becomes persistent left sidebar
- Same content, same hierarchy
```

## Variant Prompt (Alternative for AI Design Generation)

```
Design a mobile-native financial intelligence feed called "La Gazzetta di Kyiv."
Optimize for phone screens (375-414px wide), portrait orientation, one-handed scrolling.

WHAT IT IS:
A capital-flow intelligence feed read by institutional investors through Telegram.
The site is linked from daily Telegram posts. Every reader arrives on a phone.

CORE EXPERIENCE:
A vertical scroll of story cards. Each card: headline, contradiction score,
capital volume bar, tier badge. No multi-column layouts. No sidebars.
The feed IS the interface.

STORY CARD DESIGN (each card, top to bottom):
- Ticker badge + timestamp (compact, 11px, grey)
- Headline: dark ink, 18-20px, 2-3 lines max
- "Consensus vs Reality" two-line comparison, 14px
- Contradiction gap badge (integer score, colored by intensity)
- Capital volume bar (horizontal gold bar)
- Tier badge: BREAKING / DEVELOPING / ACTIVE / SETTLING

MASTHEAD (sticky top, minimal height):
Name in dark crimson (#8B0000), 18px Playfair Display.
Fox & Lion symbol left of name. Single gold line below.

COLORS:
White background. Near-black text (#111827). Gold accents (#D4AF37 borders,
#B8860B for text). Breaking signals: crimson (#8B0000).

CARD DENSITY:
Show 2.5 cards on screen at once (iPhone SE). Generous padding.
Readable at arm's length. This is a newspaper, not a dashboard.

TECHNICAL:
Vanilla HTML/CSS/JS. No frameworks. Touch-friendly.
Works on Safari iOS and Chrome Android. Fast load (<2 seconds on 4G).
```
