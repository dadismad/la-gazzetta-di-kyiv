// Shared sector page logic — loads filtered setups + stories
const API = {
  regime: './api/v1/home/regime.json',
  setups: './api/v1/home/setups.json',
  contradictions: './api/v1/home/contradictions.json',
  stories: './data/website_stories_latest.json',
};

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch { return fallback; }
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
  const [setupsData, storiesData] = await Promise.all([
    getJSON(API.setups, null),
    getJSON(API.stories, null),
  ]);

  const setups = setupsData?.items || [];
  const filtered = setups.filter(matchesSector);

  // Also check website stories
  const siteStories = storiesData?.stories || [];
  const filteredStories = siteStories.filter(s =>
    (s.sector || '').toLowerCase() === SECTOR ||
    KEYWORDS.some(k => (s.headline + s.thesis).toLowerCase().includes(k))
  );

  const el = document.getElementById('articles');
  if (!el) return;

  if (!filtered.length && !filteredStories.length) {
    el.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px">No {SECTOR} narratives active this cycle. Check back soon.</p>'.replace('{SECTOR}', SECTOR);
    return;
  }

  const items = [];

  // Website stories first (hand-curated)
  filteredStories.forEach(s => {
    items.push(`
      <article style="background:var(--bg-surface);border:1px solid var(--border);border-radius:6px;padding:20px;margin-bottom:12px">
        <h3 style="font-family:var(--sans);font-weight:600;font-size:17px;color:#fff;margin-bottom:8px">${s.headline}</h3>
        <p style="color:var(--text-secondary);font-size:13px;line-height:1.5">${s.thesis}</p>
        <div style="margin-top:8px;font-family:var(--mono);font-size:10px;color:var(--text-muted)">
          Sources: ${s.source_count || '—'} · Setup: ${s.setup_id || '—'}
        </div>
      </article>`);
  });

  // Pipeline setups
  filtered.forEach(s => {
    items.push(`
      <article style="background:var(--bg-surface);border:1px solid var(--border);border-radius:6px;padding:20px;margin-bottom:12px">
        <h3 style="font-family:var(--sans);font-weight:600;font-size:17px;color:#fff;margin-bottom:8px">${s.title || s.event || 'Narrative Signal'}</h3>
        <p style="color:var(--text-secondary);font-size:13px;line-height:1.5">${short(s.thesis || '', 300)}</p>
        ${s.actors ? `<p style="color:var(--text-muted);font-size:11px;margin-top:6px">Actors: ${s.actors.slice(0,5).join(', ')}</p>` : ''}
        <div style="margin-top:8px;font-family:var(--mono);font-size:10px;color:var(--text-muted)">
          Confidence: ${Math.round((s.confidence||0.5)*100)}% · Horizon: ${s.horizon || '24-72h'}
        </div>
      </article>`);
  });

  el.innerHTML = items.join('');
}

boot();
