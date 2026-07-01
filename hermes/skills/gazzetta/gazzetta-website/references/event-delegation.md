# Interactive Button Hardening — Event Delegation Pattern

**Added:** v23.20 · **Updated:** v23.22 (lang switchers, nav-flows, Gazzetta namespace)

**Problem:** Share buttons used inline `onclick="shareToX(this.closest('.card'))"`. After JS-refreshed DOM, inline handlers survived but `this.closest('.card')` resolved incorrectly → non-clickable buttons.

**Solution:** Replace ALL inline `onclick` with `data-action` attributes + single document-level delegation listener in the Gazzetta.UI namespace.

## Implementation

### In `boot()` (app.js):

```javascript
document.addEventListener('click', function(e) {
  const btn = e.target.closest('[data-action]');
  if (!btn) return;
  const action = btn.getAttribute('data-action');
  const card = btn.closest('.card') || btn.closest('.story-card');
  switch(action) {
    case 'copy-link': copyShareLink(card); break;
    case 'share-x': shareToX(card); break;
    case 'share-facebook': shareToFacebook(card); break;
    case 'share-telegram': shareToTelegram(card); break;
    case 'share-reddit': shareToReddit(card); break;
    case 'nav-flows':
      window.location.href = (window.i18n && i18n.lang === 'ru') ? './flows.html?lang=ru' : './flows.html';
      break;
    case 'lang-en':
      if (window.i18n && i18n.switchLang) i18n.switchLang('en');
      break;
    case 'lang-ru':
      if (window.i18n && i18n.switchLang) i18n.switchLang('ru');
      break;
  }
});
```

### HTML pattern:

```html
<!-- BEFORE (fragile — breaks on DOM refresh) -->
<button class="share-btn copy-link" onclick="copyShareLink(this.closest('.card'))">...</button>
<button class="share-btn share-x" onclick="shareToX(this.closest('.card'))">...</button>

<!-- AFTER (robust — survives any DOM change) -->
<button class="share-btn copy-link" data-action="copy-link">...</button>
<button class="share-btn share-x" data-action="share-x">...</button>

<!-- Lang switcher (v23.22) — also via delegation -->
<button class="lang-switch active" data-lang="en" data-action="lang-en">EN</button>
<button class="lang-switch" data-lang="ru" data-action="lang-ru">RU</button>
```

## Why this works

- Listener registered ONCE at boot — handles all future elements
- `e.target.closest('[data-action]')` works on dynamically-created buttons
- `btn.closest('.card')` finds the parent card from the clicked button (just like `this.closest()`)
- Add new actions to the switch — no per-button changes needed
- DOM can be completely replaced by JSON refresh — delegation still catches clicks

## Covered Elements (v23.22)

All interactive buttons in index.html migrated to data-action:

| Button | data-action | Handler |
|--------|-------------|---------|
| Copy link | `copy-link` | `copyShareLink(card)` |
| Share X | `share-x` | `shareToX(card)` |
| Share Facebook | `share-facebook` | `shareToFacebook(card)` |
| Share Telegram | `share-telegram` | `shareToTelegram(card)` |
| Share Reddit | `share-reddit` | `shareToReddit(card)` |
| Sidebar hook rows | `nav-flows` | `location.href` (lang-aware) |
| EN switch | `lang-en` | `i18n.switchLang('en')` |
| RU switch | `lang-ru` | `i18n.switchLang('ru')` |

## Pitfall

If `data-action` handlers rely on functions defined after the delegation listener, put the listener at the end of `boot()` or use `typeof` checks. The listener itself can be registered early — it only fires on click, by which time all functions are guaranteed defined.
