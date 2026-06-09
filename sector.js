// Shared sector page logic — loads filtered setups + stories

// Confidence string → percentage mapping
function confPct(confidence) {
  const map = { high: 85, medium: 65, low: 40, breaking: 80, developing: 60, active: 50, stable: 40 };
  if (typeof confidence === 'number') return Math.round(confidence);
  if (typeof confidence === 'string') {
    const lower = confidence.toLowerCase();
    for (const [k, v] of Object.entries(map)) {
      if (lower.includes(k)) return v;
    }
  }
  return 50; // fallback
}

const API = {
  regime: './data/flows.json',
  setups: './data/stories.json',       // real data source
  contradictions: './data/stories.json',
  stories: './data/stories.json',      // real data source (was non-existent website_stories_latest.json)
};

let _sectorFetchAC = null;

async function getJSON(path, fallback) {
  if (_sectorFetchAC) { _sectorFetchAC.abort(); }
  _sectorFetchAC = new AbortController();
  try {
    const r = await fetch(`${path}?t=${Date.now()}`, { cache: 'no-store', signal: _sectorFetchAC.signal });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch {
    return fallback;
  }
}

function short(s, n) { const v = String(s||'').trim(); return v.length>n ? v.slice(0,n-1)+'…' : v; }

function matchesSector(setup) {
  const id = (setup.setup_id || setup.title || '').toLowerCase();
  const title = (setup.title || '').toLowerCase();
  const thesis = (setup.thesis || '').toLowerCase();
  const tags = (setup.asset_tags || []).map(t => t.toLowerCase());
  const actors = (setup.actors || []).map(a => a.toLowerCase());
  const all = [id, title, thesis, ...tags, ...actors].join(' ');
  return KEYWORDS.some(k => all.includes(k));
}

async function boot() {
  // Single fetch — both API paths point to the same data source,
  // and concurrent fetches with AbortController cancel each other.
  const data = await getJSON(API.setups, null);

  const setups = data?.stories || data?.items || [];
  const filtered = setups.filter(matchesSector);

  const siteStories = data?.stories || [];
  const filteredStories = siteStories.filter(s =>
    (s.sector || '').toLowerCase() === SECTOR ||
    KEYWORDS.some(k => (s.headline + s.thesis).toLowerCase().includes(k))
  );

  const el = document.getElementById('articles');
  if (!el) return;

  if (!filtered.length && !filteredStories.length) {
    el.innerHTML = '<p style="color:var(--ink-muted);text-align:center;padding:40px;font-style:italic">No narratives active in this sector. Check back soon.</p>';
    return;
  }

  const items = [];

  filteredStories.forEach(s => {
    items.push(`
      <article style="background:var(--white);border:1px solid var(--divider);padding:20px 22px;margin-bottom:14px">
        <h3 style="font-family:var(--serif);font-weight:700;font-size:20px;color:var(--ink);margin-bottom:8px">${s.headline}</h3>
        <p style="color:var(--ink-light);font-size:16px;line-height:1.55">${s.thesis}</p>
        <div style="margin-top:8px;font-family:var(--sans);font-size:10px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.06em">
          Sources: ${s.source_count || '—'} · Setup: ${s.setup_id || '—'}
        </div>
      </article>`);
  });

  filtered.forEach(s => {
    items.push(`
      <article style="background:var(--white);border:1px solid var(--divider);border-left:4px solid var(--sky);padding:18px 20px;margin-bottom:12px">
        <h3 style="font-family:var(--serif);font-weight:700;font-size:20px;color:var(--ink);margin-bottom:8px">${s.title || s.event || 'Narrative Signal'}</h3>
        <p style="color:var(--ink-light);font-size:16px;line-height:1.5">${short(s.thesis || '', 300)}</p>
        ${s.actors ? `<p style="color:var(--ink-muted);font-size:13px;margin-top:6px">Actors: ${s.actors.slice(0,5).join(', ')}</p>` : ''}
        <div style="margin-top:8px;font-family:var(--sans);font-size:10px;color:var(--ink-muted);text-transform:uppercase;letter-spacing:0.06em">
          Confidence: ${confPct(s.confidence)}% · Horizon: ${s.horizon || '24-72h'}
        </div>
      </article>`);
  });

  el.innerHTML = items.join('');
}

boot();
