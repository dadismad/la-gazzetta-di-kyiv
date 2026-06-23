# Truncated init() & Missing `</script>` — Reproduction

**Date:** June 2026  
**Severity:** Critical — page renders loading spinner forever, zero JS execution  
**Detected on:** event_horizon.html (1209 lines, init() truncated at line 1208)

## Pattern

The `init()` function:
1. Fetches data successfully (`await getJSON(...)`)
2. Fetches prices (`await fetchPrices()` or `const prices = await fetchPrices()`)
3. **File ends here** — no render calls, no `loading.style.display='none'`, no `content.style.display='block'`

The last line of the file is mid-function. The `</script>` closing tag is also missing because the patch replaced the end of the file without including it.

## Symptoms
- Browser snapshot: 9 elements (masthead only + "EVENT HORIZON" heading)
- Console: `loadingVisible: ""` (default display), `contentVisible: "none"`, `errorVisible: "none"`
- No JS errors — the script tag doesn't close, so the browser treats all remaining content as HTML text
- Page shows "Loading event horizon data..." spinner forever

## Detection
```bash
# Check for missing </script>
grep -c '</script>' site/event_horizon.html
# MUST: >= 1

# Check init() is complete
tail -3 site/event_horizon.html
# MUST end with: })();\n</script>\n</body>\n</html>
# MUST NOT end mid-function

# Check script tag balance
opens=$(grep -c '<script' site/event_horizon.html)
closes=$(grep -c '</script>' site/event_horizon.html)
[ "$opens" = "$closes" ] || echo "FATAL: unbalanced script tags"
```

## Fix

1. Add rendering code after `fetchPrices()`:
```js
// Hide loading, show content
loading.style.display = 'none';
content.style.display = 'block';
// Render barometer, chokepoints, timeline...
```

2. Close the init function and IIFE:
```js
  }
  init();
})();
```

3. Add closing tags:
```html
</script>
</body>
</html>
```

## Prevention
After ANY patch to a standalone HTML page (not index.html which loads external JS), ALWAYS:
1. `tail -3 site/PAGE.html` — verify it ends with `</script>\n</body>\n</html>`
2. `grep -c '</script>' site/PAGE.html` — verify ≥ 1
3. `grep -c 'init()' site/PAGE.html` — verify it's called at end
