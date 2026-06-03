// La Gazzetta di Kyiv — News + Asset Terminal
const DATA = './data/stories.json';

function byId(id) { return document.getElementById(id); }

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch (e) { console.warn('Fetch:', path); return fallback; }
}

// ── Italian thinkers mapped to sectors ──
const THINKERS = {
  geopolitics:  { icon: '⚜', name: 'Machiavelli — Power & Strategy' },
  markets:      { icon: '⚖', name: 'Pareto — Elite Circulation' },
  tech:         { icon: '⚡', name: 'Marinetti — Acceleration' },
  wealth:       { icon: '🏛', name: 'Vico — Historical Cycles' },
  pleasure:     { icon: '✧', name: "D'Annunzio — Aesthetic Will" },
  default:      { icon: '⚜', name: 'Machiavelli — Power & Strategy' },
};

// ── Asset tickers influenced by story sectors ──
const ASSETS = [
  { symbol: 'BZ=F', name: 'Brent Crude', price: '74.20', change: '+2.1%', dir: 'up', sector: 'geopolitics' },
  { symbol: 'USD/JPY', name: 'Dollar-Yen', price: '159.85', change: '-0.4%', dir: 'down', sector: 'markets' },
  { symbol: 'NVDA', name: 'NVIDIA', price: '1,142', change: '+3.2%', dir: 'up', sector: 'tech' },
  { symbol: 'SOXX', name: 'Semiconductor ETF', price: '248.60', change: '+1.8%', dir: 'up', sector: 'tech' },
  { symbol: 'XLE', name: 'Energy Select', price: '92.45', change: '+1.5%', dir: 'up', sector: 'geopolitics' },
  { symbol: 'DXY', name: 'Dollar Index', price: '104.30', change: '-0.2%', dir: 'down', sector: 'markets' },
  { symbol: 'BTC', name: 'Bitcoin', price: '68,450', change: '+0.9%', dir: 'up', sector: 'wealth' },
];

// ── Masthead ──
function updateMasthead(leadStory) {
  const metaEl = byId('mastheadMeta');
  if (metaEl) {
    const now = new Date();
    metaEl.textContent = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')} EET`;
  }
  // Update thinker based on lead story sector
  const thinkerEl = byId('thinkerPortrait');
  if (thinkerEl && leadStory) {
    const sector = (leadStory.sector || '').toLowerCase();
    const thinker = THINKERS[sector] || THINKERS.default;
    thinkerEl.textContent = thinker.icon;
    thinkerEl.title = thinker.name;
  }
}

// ── Asset panel ──
function renderAssets(leadSector) {
  const el = byId('assetList');
  if (!el) return;
  el.innerHTML = ASSETS.map(a => `
    <div class="asset-row">
      <span class="asset-symbol">${a.symbol}</span>
      <span class="asset-name">${a.name}</span>
      <span class="asset-change ${a.dir}">${a.change}</span>
    </div>
  `).join('');
}

// ── Story card ──
function cardHTML(story, idx, isLead) {
  const sector = story.sector || '';
  const theySay = story.they_say || '';
  const reality = story.reality || '';

  return `
    <article class="card${isLead ? ' lead' : ''}" data-expand="true">
      <div class="card-head">
        ${sector ? `<span class="sector">${sector}</span>` : ''}
        <h3>${story.headline}</h3>
      </div>
      ${reality ? `<p class="summary">${reality}</p>` : ''}
      ${theySay || reality ? `
      <div class="detail">
        ${theySay ? `<div class="con-they"><span class="con-label">They say</span>${theySay}</div>` : ''}
        ${reality ? `<div class="con-real"><span class="con-label">Reality</span>${reality}</div>` : ''}
      </div>` : ''}
    </article>`;
}

function wireExpand() {
  document.querySelectorAll('.card[data-expand]').forEach(card => {
    card.addEventListener('click', () => {
      const was = card.classList.contains('expanded');
      document.querySelectorAll('.card.expanded').forEach(c => c.classList.remove('expanded'));
      if (!was) card.classList.add('expanded');
    });
  });
}

// ── Boot ──
async function boot() {
  const data = await getJSON(DATA, null);
  if (!data || !data.lead) {
    const el = byId('newsCol');
    if (el) el.innerHTML = '<p style="text-align:center;color:var(--ink-muted);padding:40px;font-style:italic">Intelligence update in progress.</p>';
    renderAssets('default');
    return;
  }

  const all = [data.lead, ...(data.stories || [])];
  const el = byId('newsCol');
  if (el) el.innerHTML = all.map((s, i) => cardHTML(s, i, i === 0)).join('');

  updateMasthead(data.lead);
  renderAssets(data.lead.sector);
  wireExpand();
}

boot();
