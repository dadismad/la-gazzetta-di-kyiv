---
name: Diplomatic Ledger
colors:
  surface: '#faf9f6'
  surface-dim: '#dbdad7'
  surface-bright: '#faf9f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f1'
  surface-container: '#efeeeb'
  surface-container-high: '#e9e8e5'
  surface-container-highest: '#e3e2e0'
  on-surface: '#1a1c1a'
  on-surface-variant: '#444748'
  inverse-surface: '#2f312f'
  inverse-on-surface: '#f2f1ee'
  outline: '#747878'
  outline-variant: '#c4c7c7'
  surface-tint: '#5f5e5e'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#1c1b1b'
  on-primary-container: '#858383'
  inverse-primary: '#c8c6c5'
  secondary: '#735c00'
  on-secondary: '#ffffff'
  secondary-container: '#fed65b'
  on-secondary-container: '#745c00'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#410000'
  on-tertiary-container: '#ea4c3a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e5e2e1'
  primary-fixed-dim: '#c8c6c5'
  on-primary-fixed: '#1c1b1b'
  on-primary-fixed-variant: '#474746'
  secondary-fixed: '#ffe088'
  secondary-fixed-dim: '#e9c349'
  on-secondary-fixed: '#241a00'
  on-secondary-fixed-variant: '#574500'
  tertiary-fixed: '#ffdad4'
  tertiary-fixed-dim: '#ffb4a8'
  on-tertiary-fixed: '#410000'
  on-tertiary-fixed-variant: '#920703'
  background: '#faf9f6'
  on-background: '#1a1c1a'
  surface-variant: '#e3e2e0'
typography:
  display-xl:
    fontFamily: Playfair Display
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 36px
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Playfair Display
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 27px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  metadata-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.04em
  label-xs:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
spacing:
  margin-horizontal: 16px
  stack-space-lg: 32px
  stack-space-md: 16px
  stack-space-sm: 8px
  tap-target-min: 48px
  separator-height: 1px
---

## Brand & Style
The design system is built on the narrative of a modern diplomatic cable—urgent information delivered with the permanence and prestige of a well-set book. It targets high-stakes financial decision-makers who require clarity over clutter. 

The visual style blends **Minimalism** with **Editorial Authority**. It relies on high-quality typography, intentional white space, and subtle tactile metaphors (like paper-stock backgrounds) to evoke a sense of quiet confidence. Every element serves the text; there are no decorative images. The emotional response is one of "calm urgency"—the news is critical, but the delivery is stable and refined.

## Colors
The palette is anchored by a warm, non-reflective background (`#FAF9F6`) that mimics premium archival paper, reducing eye strain for long-form reading. 

- **Primary Text:** A deep charcoal (`#1A1A1A`) provides maximum contrast without the harshness of pure black.
- **Accents:** Gold (`#D4AF37`) is reserved for high-value data points and structural separators, symbolizing wealth and stability. Crimson (`#8B0000`) is used sparingly for urgent market alerts or negative fiscal trends.
- **System Overlays:** A dark navy (`#1A1F2E`) is used for menus and modal backdrops to create a clear "depth" distinction from the paper-like reading surface.

## Typography
Typography is the primary vehicle for hierarchy. This design system pairs the traditional, high-contrast serif **Playfair Display** for headlines with the utilitarian, highly legible **Inter** for body text and data.

- **Headlines:** Use tight line-heights (1.2x) to maintain a "tight-set" newspaper feel.
- **Body:** Set with generous line-height (1.5x) to facilitate "deep reading" on mobile screens.
- **Metadata:** Smaller labels use increased letter spacing and semi-bold weights to maintain legibility despite the reduced size.
- **Numeric Data:** Always use Inter with tabular lining figures for vertical alignment in financial tables.

## Layout & Spacing
The layout follows a **single-column fluid model** optimized for mobile-first consumption. It rejects complex grids in favor of a vertical "stream" of intelligence.

- **Margins:** A consistent 16px horizontal margin ensures text does not hit the edge of the device bezel.
- **Rhythm:** Vertical spacing follows a 8px baseline grid. Headlines are separated from body text by 16px, while distinct articles or sections are separated by 32px or a gold 1px rule.
- **Interactivity:** All interactive elements (links, menu triggers, filters) must adhere to a minimum 48px hit area, even if the visual element (like a text link) is smaller.

## Elevation & Depth
This design system avoids shadows to maintain its "ink-on-paper" aesthetic. Depth is communicated through **Tonal Layering** and **Line Work**.

- **Surface Levels:** The base layer is the warm white paper. Secondary information (like sidebars or quotes) may sit on a slightly darker "parchment" tint or be contained within gold 1px borders.
- **Overlays:** Navigation menus and critical alerts use the Dark Navy (`#1A1F2E`) as a solid, high-contrast sheet that slides over the content, signaling a change in context from "reading" to "managing."
- **Separators:** 1px Gold (`#D4AF37`) lines are used to bisect the page, acting as the primary structural element instead of cards or boxes.

## Shapes
The shape language is strictly **Sharp (0px)**. 

In keeping with the diplomatic cable and classic newspaper aesthetic, there are no rounded corners. Buttons, input fields, and data bars must have crisp, 90-degree angles. This reinforces the "serious" and "unrefined" nature of the intelligence being shared.

## Components
Consistent component styling ensures the interface feels like a single, cohesive document.

- **Buttons:** Text-based with a bottom 2px Gold border, or solid Primary Color blocks with no rounding. Labels use `metadata-sm`.
- **Data Visualizations:** Horizontal "Impact Bars" use a 4px tall rectangular track. The "Contradiction Meter" uses a center-aligned bar where Gold grows right (positive/agreement) and Crimson grows left (negative/dissent).
- **Lists:** Traditional news-feed style. Each item is separated by a 1px Gold rule. Headlines use `headline-md`.
- **Chips/Tags:** Simple rectangular boxes with a 1px Slate border. No background fill.
- **Input Fields:** A single 1px Primary Color bottom border (no box). Labels sit above in `label-xs` Crimson if an error occurs.
- **Cards:** The system does not use traditional cards. Use "Sections" defined by vertical spacing and horizontal rules to group related content.