// La Gazzetta di Kyiv — News + Bet&Benefit Terminal
const DATA = './data/stories.json';

function byId(id) { return document.getElementById(id); }

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch (e) { console.warn('Fetch:', path); return fallback; }
}

// ── Domain-specific photo selection ──
const SECTOR_PHOTOS = {
  geopolitics: [
    'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1589519160732-57fc498494f8?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=140&fit=crop',
  ],
  markets: [
    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1590283603385-17ffb3a7f193?w=200&h=140&fit=crop',
  ],
  tech: [
    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=200&h=140&fit=crop',
  ],
  wealth: [
    'https://images.unsplash.com/photo-1579621970588-a35d0e7ab9b6?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=200&h=140&fit=crop',
  ],
  pleasure: [
    'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=200&h=140&fit=crop',
    'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=200&h=140&fit=crop',
  ],
  default: [
    'https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=200&h=140&fit=crop',
  ]
};

function pickPhoto(sector, idx) {
  const pool = SECTOR_PHOTOS[sector] || SECTOR_PHOTOS.default;
  return pool[idx % pool.length];
}

// ── Masthead ──
function updateMasthead() {
  const metaEl = byId('mastheadMeta');
  if (metaEl) {
    const now = new Date();
    metaEl.textContent = now.toTimeString().slice(0,5) + ' EET';
  }
}

// ── Bet&Benefit Panel — 2h horizon projections ──
const ASSETS = [
  { symbol: 'BZ=F', name: 'Brent Crude', price: '74.20', change: '+2.1%', dir: 'up',
    h2h_price: '75.80', h2h_vol: '+34%', h2h_bias: 'bullish', sector: 'geopolitics' },
  { symbol: 'USD/JPY', name: 'Dollar-Yen', price: '159.85', change: '-0.4%', dir: 'down',
    h2h_price: '159.10', h2h_vol: '+22%', h2h_bias: 'bearish', sector: 'markets' },
  { symbol: 'NVDA', name: 'NVIDIA', price: '1,142', change: '+3.2%', dir: 'up',
    h2h_price: '1,190', h2h_vol: '+58%', h2h_bias: 'bullish', sector: 'tech' },
  { symbol: 'SOXX', name: 'Semiconductor ETF', price: '248.60', change: '+1.8%', dir: 'up',
    h2h_price: '256', h2h_vol: '+31%', h2h_bias: 'bullish', sector: 'tech' },
  { symbol: 'XLE', name: 'Energy Select', price: '92.45', change: '+1.5%', dir: 'up',
    h2h_price: '94.20', h2h_vol: '+27%', h2h_bias: 'bullish', sector: 'geopolitics' },
  { symbol: 'DXY', name: 'Dollar Index', price: '104.30', change: '-0.2%', dir: 'down',
    h2h_price: '103.80', h2h_vol: '+18%', h2h_bias: 'bearish', sector: 'markets' },
  { symbol: 'BTC', name: 'Bitcoin', price: '68,450', change: '+0.9%', dir: 'up',
    h2h_price: '69,200', h2h_vol: '+41%', h2h_bias: 'bullish', sector: 'wealth' },
];

function assetRowHTML(a) {
  return `
    <div class="asset-row">
      <div class="asset-info">
        <span class="asset-symbol">${a.symbol}</span>
        <span class="asset-name">${a.name}</span>
        <span class="asset-price">$${a.price}</span>
        <span class="asset-change ${a.dir}">${a.change}</span>
      </div>
      <div class="asset-projection ${a.h2h_bias}">
        <span class="proj-label">2h→</span>
        <span class="proj-price">$${a.h2h_price}</span>
        <span class="proj-vol">Vol ${a.h2h_vol}</span>
      </div>
    </div>`;
}

function renderAssets() {
  const el = byId('assetList');
  if (el) el.innerHTML = ASSETS.map(assetRowHTML).join('');

  const bbBody = byId('bbSheetBody');
  if (bbBody) bbBody.innerHTML = ASSETS.map(assetRowHTML).join('');
}

// ── Mobile Bet&Benefit toggle ──
function wireBBToggle() {
  const toggle = byId('bbToggle');
  const overlay = byId('bbOverlay');
  const close = byId('bbClose');
  if (!toggle || !overlay || !close) return;

  toggle.addEventListener('click', () => {
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  });

  close.addEventListener('click', () => {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  });

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.classList.remove('open');
      document.body.style.overflow = '';
    }
  });
}

// ── Story card with domain photo ──
function cardHTML(story, idx, isLead) {
  const sector = (story.sector || '').toLowerCase();
  const theySay = story.they_say || '';
  const reality = story.reality || '';
  const photoUrl = pickPhoto(sector, idx);

  return `
    <article class="card${isLead ? ' lead' : ''}" data-expand="true">
      <div class="card-body">
        <div class="card-text">
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
        </div>
        <div class="card-photo">
          <img src="${photoUrl}" alt="${sector}" loading="lazy" onerror="this.parentElement.style.display='none'">
        </div>
      </div>
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
    renderAssets();
    wireBBToggle();
    return;
  }

  const all = [data.lead, ...(data.stories || [])];
  const el = byId('newsCol');
  if (el) el.innerHTML = all.map((s, i) => cardHTML(s, i, i === 0)).join('');

  updateMasthead();
  renderAssets();
  wireExpand();
  wireBBToggle();
}

boot();
