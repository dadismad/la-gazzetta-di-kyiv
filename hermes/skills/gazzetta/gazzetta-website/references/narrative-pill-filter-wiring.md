# Narrative Pill Filter Wiring (v31.1 — June 2026)

## Symptom: Sidebar narrative pills are dead links

Clicking a narrative pill (e.g., "DXY Reserve Currency Realignment 258.9B") appends `#` to the URL and does nothing. No filtering, no navigation, no visual feedback beyond the URL change.

## Root Cause: Two failures

1. **No click handler**: Pills have `href="#"` with no `onclick` — pure decoration.
2. **Onclick quoting trap**: When wiring `onclick="setNarrativeFilter('+n.id+')"`, the generated HTML is `onclick="setNarrativeFilter(dollar_decline)"` — an unquoted JavaScript identifier that evaluates to `undefined`. The fix requires nested quoting: `onclick="setNarrativeFilter(\''+n.id+'\')"` produces `onclick="setNarrativeFilter('dollar_decline')"`.

## Fix

### Step 1: Wire sidebar pills with onclick

In the sidebar nav `innerHTML` template (build_frontend.py):

```javascript
// WRONG — unquoted ID resolves to undefined
'<a href="#" class="..." onclick="setNarrativeFilter('+n.id+')">'

// RIGHT — quoted string argument
'<a href="javascript:void(0)" class="..." onclick="setNarrativeFilter(\''+n.id+'\')">'
```

### Step 2: Add the filter function to the JS block

```javascript
var _narrativeFilter = null;
window.setNarrativeFilter = function(narrativeId) {
  var narrativeTitle = null;
  if (narrativeId === '__all') {
    _narrativeFilter = null;
  } else {
    var found = NARRATIVES.find(function(n){ return n.id === narrativeId; });
    narrativeTitle = found ? found.title : null;
    _narrativeFilter = narrativeId;
  }
  
  var cardsEl = document.getElementById('story-cards');
  if (!cardsEl) return;
  
  var filtered = narrativeTitle 
    ? STORIES.filter(function(s){ return s._container_title === narrativeTitle; })
    : STORIES;
  
  // Re-render story cards (copy the existing render logic)
  cardsEl.innerHTML = filtered.map(function(s){ /* ... card template ... */ }).join('');
  
  // Highlight active pill in sidebar
  var sidebarLinks = document.querySelectorAll('#sidebar-nav a');
  sidebarLinks.forEach(function(link, i){
    if (narrativeId === '__all') {
      link.classList.remove('text-gold', 'border-b-2', 'border-gold');
      link.classList.add('text-on-primary/70');
    } else {
      var n = NARRATIVES[i];
      if (n && n.id === narrativeId) {
        link.classList.add('text-gold', 'border-b-2', 'border-gold');
        link.classList.remove('text-on-primary/70');
      } else {
        link.classList.remove('text-gold', 'border-b-2', 'border-gold');
        link.classList.add('text-on-primary/70');
      }
    }
  });
  
  window.switchTab('stream');
};
```

### Step 3: Add `cursor-pointer` to pills

Pills must visually signal interactivity:
```javascript
'<a ... class="flex items-center gap-3 px-3 py-2 font-metadata-sm text-metadata-sm uppercase tracking-wider cursor-pointer' + active + '">'
```

## Verification

```js
// After clicking a pill:
document.querySelectorAll('#story-cards article').length  // Must decrease from full count
[...new Set(Array.from(document.querySelectorAll('#story-cards article')).map(
  a => a.querySelector('.font-metadata-sm')?.textContent.trim()
))]  // Must show only ONE narrative title

// Active pill must have text-gold class
document.querySelector('#sidebar-nav a.text-gold')  // Must not be null
```

## Filename
Staging deploy path: `storage.googleapis.com/www.lagazzettadikyiv.com/staging/index_v6.html`
