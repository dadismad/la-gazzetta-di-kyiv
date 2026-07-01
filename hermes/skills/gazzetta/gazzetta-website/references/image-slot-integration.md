# Image Slot Integration (absorbed from frontend-image-slot-integration)

Techniques for placing images into HTML containers — background fill, ornament strips, legibility overlays, and gradient replacement.

## A) Image as Container Background

1. Find the exact target container in HTML/CSS.
2. Copy image to project static assets (`site/media/`, `assets/`, etc.).
3. Apply fill pattern:
   - **Full-fill (crop allowed):** `background: url(...) center/cover no-repeat`
   - **Width-stretch, keep ratio:** `background: url(...) center/100% auto no-repeat`
4. **Text-on-image legibility** — use ONE of:
   - **Dark scrim overlay:** `.container::before { content:""; position:absolute; inset:0; background:rgba(0,0,0,0.32); pointer-events:none; z-index:1 }` then `.container > * { position:relative; z-index:2 }`
   - **Semi-opaque chip:** `.container a { background: rgba(255,255,255,0.82); color: #111 }`
   - **Text shadow:** `text-shadow: 0 1px 3px rgba(0,0,0,0.4)`
   - **Glass chip + backdrop-blur:** `background: rgba(255,255,255,0.08); backdrop-filter: blur(1px)`
   - ⚠️ **PREFER EXTRACTING TEXT OUT of the image container** instead of overlaying. Only overlay if the text was always inside the image area or the user explicitly says "overlay text on the image." The scrim technique is a last resort, not the default.

## B) Ornament Strip Between Containers

Use a dedicated structural element — do NOT stuff it into a neighboring container's background:

```html
<div class="ornament-strip" role="presentation" aria-hidden="true"></div>
```

```css
.ornament-strip {
  height: 48px;
  background: url("./media/image.jpg") center 35%/cover no-repeat;
  position: relative;
}

/* Optional: gradient fade into the section below */
.ornament-strip::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(246,243,236,0) 0%, rgba(246,243,236,0.55) 100%);
  pointer-events: none;
}

/* Optional: bottom border as a clean cut line */
.ornament-strip {
  border-bottom: 1px solid var(--line);
}
```

Why a dedicated element matters:
- **Independent** — not bound to container padding/sizing
- **Full-viewport** — can bleed edge-to-edge even if nav has side padding
- **Transition-safe** — gradient overlays can fade into adjacent sections
- **Repositionable** — move between responsive breakpoints without changing nav CSS
- **Accessible** — `role="presentation" aria-hidden="true"` keeps it decorative

Variations:
- **Crop focus:** `background-position: center 35%` shifts the visible crop
- **Gradient blend:** `::after` with a fade-to-bg-color overlay softens the transition
- **Pattern repeat:** `background-size: auto` with `background-repeat: repeat-x` for tiling ornaments
- **Full image tag:** use `<img>` instead of `background` when you need lazy-loading, alt text for SEO, or srcset for breakpoints

## C) Replacing Image with Editorial Gradient

1. Remove `background-image` from container.
2. Apply gradient: `background: linear-gradient(180deg, #10151c 0%, #181e26 100%)`
3. Move statement text inside as first child.
4. Style text: cream `#ece4d5`, serif italic, larger size (18px), centered.
5. Restyle child elements (links, buttons) for dark bg: lighter tones, translucent chips.

## D) Reverting Image Placement

1. Identify what changed (git diff or compare to known-good commit).
2. Restore image: add `background-image` back, keep text that was migrated.
3. Add legibility scrim if text readability is affected.
4. Verify in browser with computed styles.

## Pitfalls

- Editing wrong file variant (active vs unused HTML/CSS).
- Leaving image in transient cache — must be in project static assets.
- `contain` vs `cover` confusion: `cover` fills + crops, `contain` shows whole image.
- Browser snapshot blindspot: `<p>` inside `<nav>` often invisible in a11y tree — use `browser_console` with `document.querySelector`.
- Deploy lag (GitHub Pages: 14–60s) — poll CSS for a needle string before claiming success.
- **Text-on-image legibility is mandatory** — if adding an image background breaks text, the user will call it broken.

## Verification

- Container visually filled (or strip present between sections).
- Text legible over image (scrim, chip, or shadow applied).
- Computed styles confirmed via `getComputedStyle` in browser_console.
- For ornaments: strip element exists in DOM, positioned between correct containers.
- For deployed sites: poll live CSS URL for changed properties.

## Gazzetta-Specific Cases

See also:
- `references/gazzetta-dark-editorial-nav-statement.md` — statement migration into dark nav gradient
- `references/gazzetta-topnav-floral-fill.md` — floral image as nav background
- `references/gazzetta-width-stretch-and-live-refresh.md` — width-stretch nav image + live refresh verification pattern
