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

// ── Asset claim mapping: sector → asset prediction ──
const SECTOR_CLAIMS = {
  geopolitics: { asset: 'Brent Crude', symbol: 'BZ=F', target: '78.00', change: '+2.1%' },
  markets:     { asset: 'Dollar Index', symbol: 'DXY', target: '103.80', change: '-0.5%' },
  tech:        { asset: 'NVIDIA', symbol: 'NVDA', target: '1,190', change: '+3.2%' },
  wealth:      { asset: 'Bitcoin', symbol: 'BTC', target: '69,200', change: '+1.1%' },
  pleasure:    { asset: 'Energy Select', symbol: 'XLE', target: '94.20', change: '+1.5%' },
  default:     { asset: 'S&P 500', symbol: 'SPX', target: '5,840', change: '+0.4%' },
};

// ── Better domain-specific photo selection (curated, relevant Unsplash queries) ──
const SECTOR_PHOTOS = {
  geopolitics: [
    'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=240&h=160&fit=crop&q=80',  // diplomacy
    'https://images.unsplash.com/photo-1589519160732-57fc498494f8?w=240&h=160&fit=crop&q=80',  // military drone
    'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=240&h=160&fit=crop&q=80',  // conflict zone
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=240&h=160&fit=crop&q=80',  // global map
  ],
  markets: [
    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=240&h=160&fit=crop&q=80',  // trading floor
    'https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=240&h=160&fit=crop&q=80',  // stock charts
    'https://images.unsplash.com/photo-1590283603385-17ffb3a7f193?w=240&h=160&fit=crop&q=80',  // wall street
    'https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=240&h=160&fit=crop&q=80',  // bitcoin
  ],
  tech: [
    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=240&h=160&fit=crop&q=80',  // microchip
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=240&h=160&fit=crop&q=80',  // datacenter
    'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=240&h=160&fit=crop&q=80',  // AI neural
    'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=240&h=160&fit=crop&q=80',  // robot/AI
  ],
  wealth: [
    'https://images.unsplash.com/photo-1579621970588-a35d0e7ab9b6?w=240&h=160&fit=crop&q=80',  // gold bars
    'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=240&h=160&fit=crop&q=80',  // wealth/luxury
    'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=240&h=160&fit=crop&q=80',  // crypto
    'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=240&h=160&fit=crop&q=80',  // finance data
  ],
  pleasure: [
    'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=240&h=160&fit=crop&q=80',  // wine
    'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=240&h=160&fit=crop&q=80',  // luxury watch
    'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=240&h=160&fit=crop&q=80',  // design/art
    'https://images.unsplash.com/photo-1551028714-001697bdd026?w=240&h=160&fit=crop&q=80',  // yacht
  ],
  default: [
    'https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=240&h=160&fit=crop&q=80',
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
    metaEl.textContent = new Date().toTimeString().slice(0,5) + ' EET';
  }
}

// ── Bet&Benefit Panel — with Repricing % ──
const ASSETS = [
  { symbol: 'BZ=F', name: 'Brent Crude', price: '74.20', change: '+2.1%', dir: 'up',
    h2h_price: '75.80', h2h_vol: '+34%', h2h_bias: 'bullish', repricing: '68% of move' },
  { symbol: 'USD/JPY', name: 'Dollar-Yen', price: '159.85', change: '-0.4%', dir: 'down',
    h2h_price: '159.10', h2h_vol: '+22%', h2h_bias: 'bearish', repricing: '41% of move' },
  { symbol: 'NVDA', name: 'NVIDIA', price: '1,142', change: '+3.2%', dir: 'up',
    h2h_price: '1,190', h2h_vol: '+58%', h2h_bias: 'bullish', repricing: '73% of move' },
  { symbol: 'SOXX', name: 'Semiconductor ETF', price: '248.60', change: '+1.8%', dir: 'up',
    h2h_price: '256', h2h_vol: '+31%', h2h_bias: 'bullish', repricing: '55% of move' },
  { symbol: 'XLE', name: 'Energy Select', price: '92.45', change: '+1.5%', dir: 'up',
    h2h_price: '94.20', h2h_vol: '+27%', h2h_bias: 'bullish', repricing: '71% of move' },
  { symbol: 'DXY', name: 'Dollar Index', price: '104.30', change: '-0.2%', dir: 'down',
    h2h_price: '103.80', h2h_vol: '+18%', h2h_bias: 'bearish', repricing: '34% of move' },
  { symbol: 'BTC', name: 'Bitcoin', price: '68,450', change: '+0.9%', dir: 'up',
    h2h_price: '69,200', h2h_vol: '+41%', h2h_bias: 'bullish', repricing: '26% of move' },
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
      <div class="asset-repricing">
        <span class="repricing-pct">${a.repricing}</span>
        <span class="repricing-label">narrative-driven</span>
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

// ── Story card with asset claim + domain photo ──
function cardHTML(story, idx, isLead) {
  const sector = (story.sector || '').toLowerCase();
  const theySay = story.they_say || '';
  const reality = story.reality || '';
  const photoUrl = story.image_url || pickPhoto(sector, idx);

  // Asset claim pill
  const claim = SECTOR_CLAIMS[sector] || SECTOR_CLAIMS.default;
  const claimHTML = `
    <span class="asset-claim" title="${claim.symbol} projected target">
      <span class="claim-asset">${claim.asset}</span>
      <span class="claim-arrow">→</span>
      <span class="claim-target">$${claim.target}</span>
      <span class="claim-change up">${claim.change}</span>
    </span>`;

  return `
    <article class="card${isLead ? ' lead' : ''}" data-expand="true">
      <div class="card-body">
        <div class="card-text">
          ${claimHTML}
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
