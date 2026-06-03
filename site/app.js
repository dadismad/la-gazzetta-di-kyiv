// La Gazzetta di Kyiv — Ultra-Dense Front Page
const DATA = './data/stories.json';

function byId(id) { return document.getElementById(id); }

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch (e) { console.warn('Fetch:', path, e.message); return fallback; }
}

// ── Masthead meta ──
function updateMasthead(stories) {
  const el = byId('mastheadMeta');
  if (!el) return;
  const now = new Date();
  const h = now.getHours().toString().padStart(2,'0');
  const m = now.getMinutes().toString().padStart(2,'0');
  el.textContent = `${stories.length} stories · Updated ${h}:${m}`;
}

// ── Build card ──
function cardHTML(story, idx, isLead) {
  const sector = story.sector || '';
  const leadClass = isLead ? ' lead' : '';
  const theySay = story.they_say || '';
  const reality = story.reality || '';

  return `
    <article class="card${leadClass}" data-expand="true">
      ${sector ? `<span class="sector">${sector}</span>` : ''}
      <h3>${story.headline}</h3>
      ${reality ? `<p class="summary">${reality}</p>` : ''}
      ${theySay || reality ? `
      <div class="detail">
        ${theySay ? `<div class="con-they"><span class="con-label">They say</span>${theySay}</div>` : ''}
        ${reality ? `<div class="con-real"><span class="con-label">Reality</span>${reality}</div>` : ''}
      </div>` : ''}
    </article>`;
}

// ── Wire expand ──
function wireExpand() {
  document.querySelectorAll('.card[data-expand]').forEach(card => {
    card.addEventListener('click', () => {
      const was = card.classList.contains('expanded');
      // Close all
      document.querySelectorAll('.card.expanded').forEach(c => c.classList.remove('expanded'));
      if (!was) card.classList.add('expanded');
    });
  });
}

// ── Boot ──
async function boot() {
  const data = await getJSON(DATA, null);
  if (!data || !data.lead) {
    const grid = byId('storyGrid');
    if (grid) grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;color:var(--ink-muted);padding:40px;font-style:italic">Intelligence update in progress.</p>';
    return;
  }

  const all = [data.lead, ...(data.stories || [])];
  const grid = byId('storyGrid');
  if (!grid) return;

  grid.innerHTML = all.map((s, i) => cardHTML(s, i, i === 0)).join('');
  updateMasthead(all);
  wireExpand();
}

boot();
