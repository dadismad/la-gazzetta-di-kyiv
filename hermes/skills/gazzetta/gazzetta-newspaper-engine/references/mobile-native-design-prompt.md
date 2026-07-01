# Mobile-Native Design Prompt (for Google Stitch, Variant, etc.)

Gazzetta di Kyiv is MOBILE-FIRST. Every reader arrives via Telegram on a phone. The story page is the real homepage. Desktop is a fallback.

## Prompt

```
Mobile-native financial newspaper design for "La Gazzetta di Kyiv." Every design decision must be justified for a phone screen held in one hand.

READER JOURNEY:
1. Reader sees Telegram post with a contradiction hook ("Markets price oil at $72. Physical flows show China stockpiling at 18-month high. Gap: 78/100.")
2. Taps link → lands on the STORY PAGE, not the homepage
3. Reads the story, scrolls to the contradiction breakdown
4. Maybe taps the masthead to discover the full feed
5. Never touches a desktop. Ever.

STORY PAGE LAYOUT (what 90% of readers see):
- Compact masthead bar (48px): crimson name + gold underline. Tapping goes to feed.
- Story headline: 22px Playfair Display, dark ink, 3-4 lines max
- Timestamp + tier badge inline (BREAKING red, DEVELOPING gold, etc.)
- Source attribution: 11px grey
- THE CONSENSUS block: 14px, grey left-border, "Markets believe..."
- THE REALITY block: 14px, gold left-border, "Capital flows show..."
- Contradiction meter: horizontal bar 0-100, colored gradient grey→amber→gold→crimson
- Capital impact: "$4.2B at stake" in gold with proportional bar
- Entity tags: small grey pills
- Related stories: 2-3 compact cards below

FEED PAGE (discovery, secondary):
- Same compact masthead
- Cards stacked vertically, 1px gold separators
- 2 cards visible per screen (iPhone SE)
- No images. Text is the asset.
- Pull-to-refresh native

NAVIGATION:
Bottom sheet (thumb-reachable), slides up. 8 narrative domains. Dismiss with swipe down.

TYPOGRAPHY:
- Playfair Display for headlines only. Inter for everything else.
- Body minimum 16px (financial readers skew older)
- Metadata minimum 12px
- Max 65 characters per line on body
- No font weights below 400 for body

COLORS:
- Background: #FAF9F6 (warm white, easier on OLED)
- Primary text: #1A1A1A
- Secondary: #64748B
- Gold: #D4AF37 borders, #B8860B text (WCAG AA)
- Crimson: #8B0000 for breaking
- Dark navy: #1A1F2E for bottom sheet
- Divergence gradient: #94A3B8(0) → #D4AF37(40) → #E07B39(65) → #8B0000(80+)

SPACING:
- 16px horizontal padding from screen edge
- 24px vertical between card sections
- 48px minimum tap target for EVERY interactive element
- 1px gold line separators with 16px vertical padding

PERFORMANCE:
- No JS frameworks. Zero dependencies.
- First paint under 1s on 4G
- CSS under 12KB, JS under 20KB
- No images (text-only design)
- System font fallback while Playfair loads

INTERACTION (mobile-only):
- Tap masthead → feed
- Tap narrative tag → filtered feed
- Tap entity tag → filtered feed
- Tap related card → that story
- Pull down → refresh
- Bottom sheet → 8 domains
- No hover states. No carousels. No modals.

WHAT THIS IS NOT:
- Not a Bloomberg terminal
- Not a Substack
- Not a news aggregator
- Not a blog

REFERENCE FEEL:
The quiet confidence of a diplomatic cable. Readable at 6am with coffee. Not skimmed during a meeting.
```
