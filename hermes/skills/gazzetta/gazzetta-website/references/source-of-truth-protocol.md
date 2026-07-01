# Source of Truth Override Protocol (June 2026)

User directive: "Do not rely on your local file cache. Your files are messy and out of sync."

## Before executing any code on the Gazzetta project:

1. **Fetch live repo structure via GitHub API:**
   ```bash
   curl -s "https://api.github.com/repos/pureciclismo/gazzetta-di-kyiv/git/trees/main?recursive=1" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(t['path']) for t in d.get('tree',[]) if t['type']=='blob']"
   ```

2. **Read live files from GitHub raw (not local disk):**
   ```bash
   curl -s "https://raw.githubusercontent.com/pureciclismo/gazzetta-di-kyiv/main/index.html"
   ```

3. **Verify live site structure via browser:**
   - `browser_navigate` to `https://www.lagazzettadikyiv.com/`
   - `browser_console` to check JS interactivity

4. **Only then** read local files for editing. Local files may be stale, corrupted, or out of sync with the deployed site. Trust the GitHub API + live browser over local disk.

## Why
- Local `site/` may have unpushed changes
- CDN may serve different content than local `site/`
- `patch()` tool can corrupt files with line-number artifacts
- Root-vs-site overwrite risk: `cp root site/` can destroy site/ edits

## Snapshot Compact-Mode False Positive (June 2026)

**Pitfall:** `browser_snapshot` in compact mode (default `full=false`) only shows interactive elements in the accessibility tree. JS-populated content (story cards, flow cards, signal grids) may NOT appear as interactive elements. A page with 246 stories and a 2.1MB body can show as 17 elements in the snapshot.

**Symptom:** Snapshot shows masthead + nav + footer (17-20 elements), no content visible. Looks like "skeletal page."

**Reality:** `browser_console` shows `window.STORIES_DATA.length = 246`, `body.innerHTML.length = 2189443`. The page IS fully populated.

**Rule: NEVER claim a page is empty/skeletal/broken based on snapshot alone.** Always verify with at least one of:
```javascript
// Check 1: Body size
browser_console("document.body.innerHTML.length")
// Check 2: Data loaded
browser_console("typeof STORIES_DATA !== 'undefined' ? STORIES_DATA.length : 'no data'")
// Check 3: Computed styles (confirms CSS applied)
browser_console("getComputedStyle(document.querySelector('.container')).borderLeftWidth")
// Check 4: Browser screenshot for visual confirmation
browser_vision("Show me the full page")
```

**Detection heuristic:** If snapshot shows ≤30 elements but curl shows the HTML file >5000 bytes, the page is likely populated — verify with console, not snapshot.
