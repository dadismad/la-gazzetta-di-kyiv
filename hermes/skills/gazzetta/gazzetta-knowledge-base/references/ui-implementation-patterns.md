# UI Implementation Patterns — June 2026

Reusable HTML/CSS/JS patterns from Sprints 1-2 of the Phase 1 execution.

## Always-Visible Share Row

**Problem**: Share buttons (copy link, X, Telegram) were hidden inside `.story-expanded`
(`display:none`), requiring a click-to-expand before users could share. Zero discovery.

**Fix**: Move `.share-row` out of `<div class="story-expanded">` into the main card body,
after the contradiction/flow/action lines and before the expandable detail section.

Before:
```html
<article class="card">
  <h3 class="story-headline">...</h3>
  <div class="story-expanded" style="display:none">
    <!-- detail -->
    <div class="share-row">...</div>  <!-- HIDDEN -->
  </div>
</article>
```

After:
```html
<article class="card">
  <h3 class="story-headline">...</h3>
  <div class="share-row">...</div>  <!-- ALWAYS VISIBLE -->
  <div class="story-expanded" style="display:none">
    <!-- detail -->
  </div>
</article>
```

CSS requirements:
```css
.share-row {
  display: flex;
  gap: 6px;
  margin: 8px 0 0 0;
  padding-top: 4px;
  border-top: 1px solid var(--gray-200);
}
.share-btn {
  width: 44px; height: 44px;
  min-width: 44px; min-height: 44px;  /* Guideline D9 */
  display: inline-flex;
  align-items: center; justify-content: center;
  border: 1px solid var(--gray-200);
  background: #FFFFFF;
  cursor: pointer;
}
```

## Hamburger Navigation Drawer (Mobile)

**Problem**: Product nav was a horizontal text row of 7 links at 11px Inter. On mobile
(375px), links wrapped to a second line with no spacing. Tap targets measured ~20x14px
— far below the 44px minimum. No hamburger or drawer existed.

**Fix**: Three-part implementation:

### 1. Header Template (`templates/header.html`)
Add hamburger button inside `<header class="masthead">` and a nav drawer
immediately after `</header>`:

```html
<button class="nav-hamburger" id="hamburgerBtn">
  <span class="hamburger-line"></span>
  <span class="hamburger-line"></span>
  <span class="hamburger-line"></span>
</button>
</header>
<div class="nav-drawer-backdrop" id="navDrawerBackdrop"></div>
<nav class="nav-drawer" id="navDrawer">
  <div class="nav-drawer-header">
    <span class="nav-drawer-title">Navigation</span>
    <button class="nav-drawer-close" id="navDrawerClose">&times;</button>
  </div>
  <div class="nav-drawer-body">
    <div class="nav-drawer-section">
      <span class="nav-drawer-section-title">INTEL</span>
      <a href="./stories.html" class="nav-drawer-link">Stories</a>
      <!-- more links -->
    </div>
    <!-- more sections -->
  </div>
</nav>
```

### 2. CSS (`styles.css`)
```css
.nav-hamburger { display: none; }  /* hidden on desktop */
.nav-drawer {
  position: fixed; top: 0; left: 0;
  width: 280px; max-width: 85vw;
  height: 100dvh;
  background: #FFFFFF;
  z-index: 999;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}
.nav-drawer.open { transform: translateX(0); }
.nav-drawer-backdrop {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,0.4); z-index: 998;
}
.nav-drawer-backdrop.open { display: block; }

@media (max-width: 600px) {
  .masthead-right { display: none; }
  .nav-hamburger { display: flex; }
}
```

### 3. JS (`app.js`)
```javascript
function initNavDrawer() {
  var hamburger = document.getElementById('hamburgerBtn');
  var drawer = document.getElementById('navDrawer');
  var backdrop = document.getElementById('navDrawerBackdrop');
  if (!hamburger || !drawer || !backdrop) return;
  
  function closeDrawer() {
    hamburger.classList.remove('open');
    drawer.classList.remove('open');
    backdrop.classList.remove('open');
    document.body.style.overflow = '';
  }
  
  hamburger.addEventListener('click', function() {
    if (drawer.classList.contains('open')) { closeDrawer(); return; }
    hamburger.classList.add('open');
    drawer.classList.add('open');
    backdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  });
  
  backdrop.addEventListener('click', closeDrawer);
  document.getElementById('navDrawerClose').addEventListener('click', closeDrawer);
  
  // Close on nav link click (mobile navigation complete)
  drawer.querySelectorAll('.nav-drawer-link').forEach(function(link) {
    link.addEventListener('click', function() { setTimeout(closeDrawer, 150); });
  });
  
  // Close on Escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && drawer.classList.contains('open')) closeDrawer();
  });
}
```

## Mobile Tap Integrity (Guideline D9)

All interactive elements must have `min-width: 44px; min-height: 44px`. This applies to:
- Share buttons
- Navigation links
- Close buttons
- Hamburger button
- Any clickable/tappable element

Use `min-width`/`min-height` (not just `width`/`height`) so the element can grow
if needed but never shrinks below the tap threshold.

## Word-Break for Headlines on Mobile

```css
.story-headline {
  overflow-wrap: break-word;
  word-break: break-word;
  hyphens: auto;
}
```

Prevents headline overflow on narrow viewports (320-390px) where DM Serif Display
at 16-18px can push text outside card boundaries.
