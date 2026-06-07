// La Gazzetta di Kyiv v20.24 — i18n support · language-specific data files
const DATA_BASE = './data/stories';
const LIVING_DATA = './data/living_stories.json';
const FLOWS_BASE = './data/flows';
function getDataPath() { return DATA_BASE + (window.i18n && i18n.lang === 'ru' ? '_ru' : '') + '.json'; }
function getFlowsPath() { return FLOWS_BASE + (window.i18n && i18n.lang === 'ru' ? '_ru' : '') + '.json'; }
const FLOWS_POLL_INTERVAL = 300000;

// ── Story cache for flow→story cross-linking ──
const STORIES_CACHE = {}; // story_id → {headline, dom_card}

function byId(id) { return document.getElementById(id); }

// AbortController for stale fetch cancellation
let _fetchAC = null;

async function getJSON(path, fallback) {
  if (_fetchAC) { _fetchAC.abort(); }
  _fetchAC = new AbortController();
  try {
    const r = await fetch(`${path}?t=${Date.now()}`, { cache: 'no-store', signal: _fetchAC.signal });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch (e) {
    if (e.name === 'AbortError') { console.debug('Fetch aborted:', path); return fallback; }
    console.warn('Fetch:', path, e); return fallback;
  }
}

// ── Captured story set (accumulation — never remove old cards) ──
let capturedStoryIds = new Set();

// ── Sector photos ──
const SECTOR_PHOTOS = {
  geopolitics: [
    'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1589519160732-57fc498494f8?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=240&h=160&fit=crop&q=80',
  ],
  markets: [
    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1590283603385-17ffb3a7f193?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=240&h=160&fit=crop&q=80',
  ],
  tech: [
    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=240&h=160&fit=crop&q=80',
  ],
  wealth: [
    'https://images.unsplash.com/photo-1579621970588-a35d0e7ab9b6?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=240&h=160&fit=crop&q=80',
  ],
  pleasure: [
    'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1551028714-001697bdd026?w=240&h=160&fit=crop&q=80',
  ],
  macro: [
    'https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=240&h=160&fit=crop&q=80',
    'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=240&h=160&fit=crop&q=80',
  ],
  default: [
    'https://images.unsplash.com/photo-1504711434969-e33886168d6c?w=240&h=160&fit=crop&q=80',
  ]
};

function pickPhoto(sector, idx) {
  const pool = SECTOR_PHOTOS[sector] || SECTOR_PHOTOS.default;
  return pool[idx % pool.length];
}

// ── Category tag labels ──
const SECTOR_LABELS = {
  geopolitics: () => i18n.t('sector_geopolitics','GEOPOLITICS'),
  markets: () => i18n.t('sector_markets','MARKETS'),
  tech: () => i18n.t('sector_tech','TECH'),
  macro: () => i18n.t('sector_macro','MACRO'),
  wealth: () => i18n.t('sector_wealth','WEALTH'),
  pleasure: () => i18n.t('sector_pleasure','PLEASURE'),
};

// ═══════════════════════════════════════════════════════════════
// COLLAPSIBLE CONTAINERS
// ═══════════════════════════════════════════════════════════════

function wireCollapsibleContainers() {
  document.querySelectorAll('.container.collapsible').forEach(container => {
    const header = container.querySelector('.container-header');
    if (!header) return;
    header.addEventListener('click', function(e) {
      e.stopPropagation();
      container.classList.toggle('expanded');
      // Signal container: render triangulation on expand
      if (container.classList.contains('expanded') && container.querySelector('#triangulationList')) {
        renderTriangulation();
      }
    });
  });
}

// ═══════════════════════════════════════════════════════════════
// TIME FORMATTING
// ═══════════════════════════════════════════════════════════════

function formatTimeAgo(isoString) {
  if (!isoString) return '';
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return i18n.t('just_now','just now');
  if (mins < 60) return `${mins}${i18n.t('m_ago','m ago')}`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}${i18n.t('h_ago','h ago')}`;
  return `${Math.floor(hours / 24)}${i18n.t('d_ago','d ago')}`;
}

function formatTimestamp(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  const time = d.toTimeString().slice(0, 5);
  if (isToday) return `${time} · ${i18n.t('today','Today')}`;
  const date = `${d.getDate()}/${d.getMonth() + 1}`;
  return `${time} · ${date}`;
}

// ═══════════════════════════════════════════════════════════════
// MASTHEAD
// ═══════════════════════════════════════════════════════════════

function updateMasthead() {
  const metaEl = byId('mastheadMeta');
  if (metaEl) {
    const now = new Date();
    const time = now.toTimeString().slice(0,5);
    const date = `${now.getDate()}/${now.getMonth()+1}/${now.getFullYear().toString().slice(-2)}`;
    metaEl.textContent = `${date} · ${time} EET`;
  }
}

function updateMastheadLiving(generatedAt, nextMicroUpdate) {
  const metaEl = byId('mastheadMeta');
  if (!metaEl) return;
  const time = generatedAt ? new Date(generatedAt).toTimeString().slice(0,5) + ' EET' : new Date().toTimeString().slice(0,5) + ' EET';
  const next = nextMicroUpdate ? `· next update ${new Date(nextMicroUpdate).toTimeString().slice(0,5)}` : '';
  metaEl.textContent = `${time} ${next}`;
}

// ═══════════════════════════════════════════════════════════════
// THE ANCHOR / BET & BENEFIT — Expanded to 14 assets (7 tradFi + 7 crypto)
// ═══════════════════════════════════════════════════════════════

// ── ATR-based stop calculation (volatility-adjusted) ──
// atr_pct = approximate 14-day ATR as % of price
// stop_atr_mult = how many ATRs from entry for stop placement
// stop_display = computed: entry ± (entry * atr_pct * stop_atr_mult)
function computeATRStop(entry, atrPct, mult, bias) {
  if (bias === 'WATCH') return null; // WATCH assets have no directional stop
  const e = parseFloat(String(entry).replace(/,/g, ''));
  const atrMove = e * atrPct * mult;
  if (bias === 'SELL') return (e + atrMove).toFixed(e > 1000 ? 0 : e > 100 ? 1 : 2);
  return (e - atrMove).toFixed(e > 1000 ? 0 : e > 100 ? 1 : 2);
}

const ANCHOR_ASSETS = [
  // Traditional finance (7) — with ATR volatility context
  { symbol: 'SPX', price: '5,840', change: '+0.4%', dir: 'up',
    bias: 'BUY', entry: '5,750', target: '5,950',
    atr_pct: 0.012, stop_atr_mult: 2.0, conviction: 'HIGH' },
  { symbol: 'NVDA', price: '1,142', change: '+3.2%', dir: 'up',
    bias: 'BUY', entry: '1,100', target: '1,240',
    atr_pct: 0.035, stop_atr_mult: 2.0, conviction: 'HIGH' },
  { symbol: 'BRENT', price: '74.20', change: '+2.1%', dir: 'up',
    bias: 'BUY', entry: '72.00', target: '78.00',
    atr_pct: 0.022, stop_atr_mult: 2.5, conviction: 'MED' },
  { symbol: 'DXY', price: '104.30', change: '-0.2%', dir: 'down',
    bias: 'SELL', entry: '105.20', target: '103.00',
    atr_pct: 0.006, stop_atr_mult: 3.0, conviction: 'MED' },
  { symbol: 'GOLD', price: '2,410', change: '+0.6%', dir: 'up',
    bias: 'BUY', entry: '2,350', target: '2,500',
    atr_pct: 0.014, stop_atr_mult: 2.5, conviction: 'HIGH' },
  { symbol: 'BTC', price: '68,450', change: '+0.9%', dir: 'up',
    bias: 'BUY', entry: '67,200', target: '72,000',
    atr_pct: 0.025, stop_atr_mult: 2.0, conviction: 'HIGH' },
  { symbol: '10Y', price: '4.35%', change: '+3bp', dir: 'up',
    bias: 'WATCH', entry: '4.35', target: '4.50',
    atr_pct: 0.015, stop_atr_mult: 2.0, conviction: 'LOW' },
  // Crypto (7) — higher ATR reflects crypto volatility
  { symbol: 'ETH', price: '3,850', change: '+2.1%', dir: 'up',
    bias: 'BUY', entry: '3,600', target: '4,200',
    atr_pct: 0.040, stop_atr_mult: 2.0, conviction: 'HIGH' },
  { symbol: 'SOL', price: '178', change: '+4.5%', dir: 'up',
    bias: 'BUY', entry: '155', target: '210',
    atr_pct: 0.055, stop_atr_mult: 2.0, conviction: 'MED' },
  { symbol: 'XRP', price: '1.25', change: '+1.2%', dir: 'up',
    bias: 'WATCH', entry: '1.15', target: '1.80',
    atr_pct: 0.045, stop_atr_mult: 2.0, conviction: 'LOW' },
  { symbol: 'BNB', price: '645', change: '+3.0%', dir: 'up',
    bias: 'BUY', entry: '580', target: '720',
    atr_pct: 0.035, stop_atr_mult: 2.0, conviction: 'MED' },
  { symbol: 'ADA', price: '0.92', change: '-1.8%', dir: 'down',
    bias: 'SELL', entry: '1.05', target: '0.85',
    atr_pct: 0.050, stop_atr_mult: 2.0, conviction: 'HIGH' },
  { symbol: 'DOGE', price: '0.28', change: '+5.2%', dir: 'up',
    bias: 'WATCH', entry: '0.25', target: '0.35',
    atr_pct: 0.065, stop_atr_mult: 2.0, conviction: 'LOW' },
];

// Pre-compute stops on load
ANCHOR_ASSETS.forEach(a => {
  a.stop = computeATRStop(a.entry, a.atr_pct, a.stop_atr_mult, a.bias);
});

const ANCHOR_CRYPTO = {
  stablecoinSupply: { value: '$172B', delta: '+$4.2B', label: 'Stablecoin Supply (30d)' },
  exchangeNetflow: { value: '-$890M', delta: '7d outflow', label: 'Exchange Netflow' },
  fundingRate: { value: '-0.01%', regime: 'neutral', label: 'Aggregate Funding' },
};

const ANCHOR_PDR = { value: '1.7', regime: 'passive', get regimeLabel() { return i18n.t('pdr_regime_passive','Passive Discovery'); }, trend: '▁▃▅▆▇' };

function anchorRowHTML(a) {
  const pillClass = a.bias === 'BUY' ? 'anchor-pill buy' : a.bias === 'SELL' ? 'anchor-pill sell' : 'anchor-pill watch';
  const badgeClass = a.conviction === 'HIGH' ? 'anchor-badge high' : a.conviction === 'MED' ? 'anchor-badge med' : 'anchor-badge low';
  const atrPct = (a.atr_pct * 100).toFixed(1);
  return `
    <div class="asset-row">
      <div class="asset-info">
        <span class="asset-symbol">${a.symbol}</span>
        <span class="asset-price">$${a.price}</span>
        <span class="asset-change ${a.dir}">${a.change}</span>
      </div>
      <div class="asset-trade">
        <span class="${pillClass}">${i18n.t(a.bias.toLowerCase(), a.bias)}</span>
        <span class="asset-zone">${a.entry} → ${a.target}</span>
        <span class="asset-stop" title="Volatility-adjusted: ${a.stop_atr_mult}×${atrPct}% ATR from entry">Stop ${a.stop} · ${a.stop_atr_mult}×ATR</span>
        <span class="${badgeClass}">${i18n.t("conviction_"+a.conviction, a.conviction)}</span>
      </div>
    </div>`;
}

function cryptoSignalHTML() {
  return `
    <div class="asset-row anchor-crypto">
      <div class="anchor-crypto-row"><span class="anchor-crypto-label">${ANCHOR_CRYPTO.stablecoinSupply.label}</span><span class="anchor-crypto-value">${ANCHOR_CRYPTO.stablecoinSupply.value} <span class="asset-change up">${ANCHOR_CRYPTO.stablecoinSupply.delta}</span></span></div>
      <div class="anchor-crypto-row"><span class="anchor-crypto-label">${ANCHOR_CRYPTO.exchangeNetflow.label}</span><span class="anchor-crypto-value">${ANCHOR_CRYPTO.exchangeNetflow.value} <span class="anchor-crypto-sub">${ANCHOR_CRYPTO.exchangeNetflow.delta}</span></span></div>
      <div class="anchor-crypto-row"><span class="anchor-crypto-label">${ANCHOR_CRYPTO.fundingRate.label}</span><span class="anchor-crypto-value">${ANCHOR_CRYPTO.fundingRate.value} <span class="anchor-crypto-sub">${ANCHOR_CRYPTO.fundingRate.regime}</span></span></div>
    </div>`;
}

function renderPDR(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.querySelector('.pdr-value').textContent = ANCHOR_PDR.value;
  const regimeEl = el.querySelector('.pdr-regime');
  regimeEl.textContent = ANCHOR_PDR.regimeLabel;
  regimeEl.className = 'pdr-regime ' + ANCHOR_PDR.regime;
  el.querySelector('.pdr-trend').textContent = ANCHOR_PDR.trend;
}

function renderAnchor() {
  const el = byId('assetList');
  if (el) el.innerHTML = ANCHOR_ASSETS.map(anchorRowHTML).join('') + cryptoSignalHTML();
  renderPDR('pdrGauge');
  
  // Update container description with dynamic asset count
  const anchorCount = byId('anchorCount');
  if (anchorCount) anchorCount.textContent = String(ANCHOR_ASSETS.length);
  
  // Data freshness note — anchor prices are reference points, not live
  const freshnessEl = byId('anchorFreshness');
  if (freshnessEl) {
    const now = new Date();
    freshnessEl.textContent = i18n.t('reference_prices','Reference prices · reviewed') + ` ${now.toDateString()}`;
  }
}

// ═══════════════════════════════════════════════════════════════
// CAPITAL FLOWS REPORT — dynamically loaded from flows.json
// ═══════════════════════════════════════════════════════════════

let CAPITAL_FLOWS_DATA = [];
let GLOSSARY = {};

async function fetchFlows() {
  const data = await getJSON(getFlowsPath(), null);
  if (!data || !data.flows) return false;
  CAPITAL_FLOWS_DATA = data.flows;
  GLOSSARY = data.glossary || {};
  renderCapitalFlows();
  renderGlossaryTooltips();
  updateHeroConfidence(data.aggregate_confidence, data.aggregate_confidence_label, data.aggregate_direction);
  updateMastheadFlows(data);
  // Update flow freshness timestamp
  const tsEl = byId('flowFreshness');
  if (tsEl && data.generated_at) {
    tsEl.textContent = 'updated ' + formatTimeAgo(data.generated_at);
    tsEl.title = data.generated_at;
  }
  // Re-apply i18n to dynamically rendered flow items (v22.18)
  if (window.i18n && window.i18n.applyTranslations) window.i18n.applyTranslations();
  return true;
}

// ── Position label: institutional jargon → varied retail insight ──
const POSITION_VARIANTS = {
  'accumulating': [
    { key: 'pos_accumulating_1', fallback: 'Institutions buying — net inflow' },
    { key: 'pos_accumulating_2', fallback: 'Capital flowing in — accumulation detected' },
    { key: 'pos_accumulating_3', fallback: 'Positioning long — institutional demand' }
  ],
  'distributing': [
    { key: 'pos_distributing_1', fallback: 'Institutions selling — net outflow' },
    { key: 'pos_distributing_2', fallback: 'Capital flowing out — distribution detected' },
    { key: 'pos_distributing_3', fallback: 'Reducing positions — institutional selling' }
  ],
  'hedging': [
    { key: 'pos_hedging_1', fallback: 'Mixed signals — hedging both sides' },
    { key: 'pos_hedging_2', fallback: 'Direction unclear — capital in standby' },
    { key: 'pos_hedging_3', fallback: 'Balanced flows — no clear direction' }
  ]
};

let _variantIdx = {};
function positionLabel(positioning) {
  if (!POSITION_VARIANTS[positioning]) return positioning;
  const variants = POSITION_VARIANTS[positioning];
  // Cycle through variants deterministically per positioning type
  if (!_variantIdx[positioning]) _variantIdx[positioning] = 0;
  const idx = _variantIdx[positioning] % variants.length;
  _variantIdx[positioning] = (idx + 1) % variants.length;  // deterministic cycling
  const v = variants[idx];
  return i18n.t(v.key, v.fallback);
}

// ── Source label mappings ──
const SOURCE_LABELS = {
  'epfr': 'EPFR Global (institutional fund flows)',
  'morningstar': 'Morningstar Direct (mutual fund/ETF)',
  'bloomberg': 'Bloomberg Terminal (market data)',
  'fed_z1': 'Federal Reserve Z.1 (Flow of Funds)',
  'cftc_cot': 'CFTC Commitments of Traders',
  'ici': 'ICI Weekly Fund Flows',
  'cboe': 'CBOE (VIX/options data)',
  'bls': 'BLS Employment (age-cohort data)',
  'telegram_intel': 'Open-source intelligence (Telegram)',
  'internal': 'Internal editorial pipeline',
};
function sourceLabel(source) {
  if (!source) return 'Open-source intelligence';
  return SOURCE_LABELS[source] || source.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

// ── Aggregate duplicate flows (same headline+direction+amount) ──
function aggregateFlows(flows) {
  const seen = new Map();
  const result = [];
  flows.forEach(f => {
    const key = `${f.headline}|${f.direction}|${f.amount_b}`;
    if (seen.has(key)) {
      seen.get(key).catalyst_count = (seen.get(key).catalyst_count || 1) + 1;
      seen.get(key).story_ids.push(f.story_id);
    } else {
      const item = {...f, story_ids: [f.story_id], catalyst_count: 1};
      seen.set(key, item);
      result.push(item);
    }
  });
  return result;
}

function renderCapitalFlows() {
  const el = byId('flowsList');
  if (!el) return;
  if (!CAPITAL_FLOWS_DATA.length) {
    el.innerHTML = '<div class="flows-loading">' + i18n.t('analyzing_capital','Analyzing capital movements…') + '</div>';
    return;
  }
  // Aggregate duplicate flows (same headline+direction+amount) with catalyst counts
  const aggregated = aggregateFlows(CAPITAL_FLOWS_DATA);
  el.innerHTML = aggregated.map(f => {
    const anchorSym = f.anchor_symbol || matchAnchor(f.headline);
    const anchorAsset = ANCHOR_ASSETS.find(a => a.symbol === anchorSym);
    const dirArrow = f.direction === 'inflow' ? '↑' : '↓';
    const dirLabel = f.direction === 'inflow' ? 'IN' : 'OUT';
    const confPct = f.confidence_pct || 50;
    const paceDisplay = f.pace_multiplier >= 1.5 ? `↑ ${f.pace_multiplier}×` : f.pace_multiplier <= 0.7 ? `↓ ${f.pace_multiplier}×` : `= ${f.pace_multiplier}×`;
    const catalystBadge = f.catalyst_count > 1 ? `<span class="catalyst-badge">${f.catalyst_count} ` + i18n.t('catalysts','catalysts') + `</span>` : '';

    // v22.16: Retail-flattened — direction + sector + play only. % and pace in detail.
    const playPill = anchorAsset
      ? `<span class="flow-bet-pill-mini">${anchorAsset.symbol} ${anchorAsset.bias} · ${anchorAsset.conviction}</span>`
      : '';
    return `
    <div class="flow-row ${f.direction}" data-flow-story-id="${f.story_ids ? f.story_ids[0] : f.story_id}">
      <div class="flow-row-main">
        <span class="flow-amount">$${f.amount_b.toFixed(1)}B</span>
        <span class="flow-dir ${f.direction}">${dirArrow} ${dirLabel}</span>
        <span class="flow-asset">${f.asset_class || 'equities'}</span>
        ${playPill}
        ${catalystBadge}
        <span class="flow-expand-hint">&#9660;</span>
      </div>
      <div class="flow-row-detail">
        <div class="flow-detail-section">
          <span class="flow-detail-label">PROJECTED MOVEMENT</span>
          <p class="flow-detail-text">${f.projected || 'No projection available'}</p>
        </div>
        <div class="flow-detail-section">
          <span class="flow-detail-label">CONVICTION</span>
          <span class="flow-confidence-badge">${confPct}% ${f.confidence_level || ''}</span>
          ${f.confidence_trace ? '<span class="flow-confidence-trace">' + f.confidence_trace.split(' > ').join(' + ') + '</span>' : ''}
        </div>
        <div class="flow-detail-section">
          <span class="flow-detail-label">LINKED STORY</span>
          <a href="./story.html?id=${f.story_ids ? f.story_ids[0] : f.story_id || ''}" class="flow-story-link">&rarr; View intelligence report</a>
        </div>
        <div class="flow-detail-section">
          <span class="flow-detail-label">DATA SOURCE</span>
          <span class="flow-source-badge" style="font-family:var(--sans);font-size:10px;color:var(--ink-muted);">${sourceLabel(f.source || 'telegram_intel')}</span>
        </div>
        <div class="flow-detail-section">
          <span class="flow-detail-label">POSITIONING</span>
          <span class="flow-positioning-detail">${f.positioning ? positionLabel(f.positioning) : 'No data'} &middot; ${paceDisplay} pace</span>
        </div>
      </div>
    </div>`;
  }).join('');

  const sub = byId('cfSubtitle');
  if (sub) {
    const inflows = CAPITAL_FLOWS_DATA.filter(f => f.direction === 'inflow');
    const outflows = CAPITAL_FLOWS_DATA.filter(f => f.direction === 'outflow');
    sub.textContent = `${inflows.length} ${i18n.t('flow_inflows','inflows')} · ${outflows.length} ${i18n.t('flow_outflows','outflows')}`;
  }

  // Wire expand-on-click (v22.17)
  el.addEventListener('click', function(e) {
    const row = e.target.closest('.flow-row');
    if (!row) return;
    // Accordion: collapse others
    el.querySelectorAll('.flow-row.expanded').forEach(r => {
      if (r !== row) r.classList.remove('expanded');
    });
    row.classList.toggle('expanded');
  });
}

// ── Refresh flow→story links after story cards render ──
function refreshFlowStoryLinks() {
  document.querySelectorAll('.flow-story-title').forEach(link => {
    if (link.textContent === 'Loading...' || link.textContent === 'Story not yet loaded') {
      const item = link.closest('.flow-item');
      if (!item) return;
      const sid = item.dataset.flowStoryId;
      const card = document.querySelector(`.card[data-story-id="${sid}"]`);
      const cached = STORIES_CACHE[sid];
      if (card) {
        const h3 = card.querySelector('h3');
        link.textContent = h3 ? h3.textContent : i18n.t('story_found','Story found');
        link.style.cursor = 'pointer';
        link.style.color = 'var(--blue)';
        link.addEventListener('click', () => {
          card.scrollIntoView({behavior:'smooth'});
          card.classList.add('expanded');
        });
      } else if (cached) {
        link.textContent = cached.headline;
        link.style.color = 'var(--ink-muted)';
        link.style.cursor = 'default';
        link.title = i18n.t('refresh_for_click','Refresh page to enable click-through to story');
      }
    }
  });
}

// ═══════════════════════════════════════════════════════════════
// HERO CONFIDENCE — qualitative tier + direction, not naked %
// ═══════════════════════════════════════════════════════════════

function updateHeroConfidence(pct, label, direction) {
  const el = byId('heroConfidence');
  if (!el) return;
  if (!pct) {
    el.textContent = '—';
    el.style.color = '';
    return;
  }
  // Directional conviction badge — % + direction visible (v22.28: degen+retail focus group)
  // Both focus group personas couldn't find the confidence — it was hidden in tooltip
  const badge = direction === 'bullish' ? 'BULLISH' : direction === 'bearish' ? 'BEARISH' : 'NEUTRAL';
  const color = direction === 'bullish' ? 'var(--green)' : direction === 'bearish' ? 'var(--red)' : 'var(--ink-muted)';
  el.innerHTML = `<span style="color:${color};font-weight:700;font-size:inherit;">${pct}% ${badge}</span>`;
  el.title = `${pct}% flow conviction — ${direction} (${label})`;
  el.style.color = color;
  // Label stays clean — data-i18n handles it
}

function updateMastheadFlows(flowsData) {
  const total = byId('heroFlowTotal');
  if (!total || !flowsData) return;
  const totalB = flowsData.flows ? flowsData.flows.reduce((s, f) => s + (f.amount_b || 0), 0) : 0;
  if (totalB > 0) {
    total.textContent = `$${totalB.toFixed(1)}B`;
  }
  // NOTE: heroStoryCount is updated by updateCumulativeStats — do NOT set it here
}

// ═══════════════════════════════════════════════════════════════
// GLOSSARY TOOLTIPS — inline explanations for finance terms
// ═══════════════════════════════════════════════════════════════

function renderGlossaryTooltips() {
  if (!Object.keys(GLOSSARY).length) return;
  // Add tooltip data attributes to known acronyms in the DOM
  const terms = Object.entries(GLOSSARY);
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  const textNodes = [];
  while (walker.nextNode()) textNodes.push(walker.currentNode);

  textNodes.forEach(node => {
    if (!node.parentElement || node.parentElement.closest('script,style,noscript,.glossary-tip')) return;
    let html = node.textContent;
    let changed = false;
    terms.forEach(([term, definition]) => {
      const regex = new RegExp(`\\b(${term})\\b`, 'g');
      if (regex.test(html)) {
        const escaped = definition.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        html = html.replace(regex, `<span class="glossary-tip" data-tip="${escaped}" tabindex="0">$1</span>`);
        changed = true;
      }
    });
    if (changed && node.parentElement) {
      const span = document.createElement('span');
      span.innerHTML = html;
      node.parentElement.replaceChild(span, node);
    }
  });
}

// ═══════════════════════════════════════════════════════════════
// TRIANGULATION — Cross-Container Intelligence Signal
// ═══════════════════════════════════════════════════════════════

const STORY_ANCHOR_MAP = {
  oil: 'BRENT', energy: 'BRENT', gold: 'GOLD',
  treasury: '10Y', fed: '10Y', nvidia: 'NVDA', ai: 'NVDA',
  tech: 'NVDA', china: 'DXY', defense: 'SPX', nato: 'SPX',
  ukraine: 'GOLD', europe: 'DXY'
};

function matchAnchor(headline) {
  const h = headline.toLowerCase();
  for (const [kw, asset] of Object.entries(STORY_ANCHOR_MAP)) {
    if (h.includes(kw)) return asset;
  }
  return null;
}

function computeTriangulation(story, flow, anchorAsset) {
  let score = 0;
  const signals = [];

  // Flow alignment (max 50 — capital is the prime mover)
  if (flow) {
    const amtMatch = (flow.headline || '').match(/\$([\d.]+)([MBT])/);
    const amt = amtMatch ? parseFloat(amtMatch[1]) : 0;
    const denom = amtMatch ? amtMatch[2] : 'M';
    const paceMatch = (flow.detail || '').match(/(\d+\.?\d*)x/);
    const pace = paceMatch ? parseFloat(paceMatch[1]) : 1;
    const direction = flow.direction || 'none';
    
    // Amount tier
    if (denom === 'B' && amt >= 5) score += 20;
    else if (denom === 'B' && amt >= 3) score += 15;
    else if (denom === 'B' && amt >= 1) score += 10;
    else score += 5;
    // Velocity tier (boosted for capital-first: pace matters more)
    if (pace >= 3.0) score += 15;
    else if (pace >= 2.5) score += 12;
    else if (pace >= 2.0) score += 10;
    else if (pace >= 1.5) score += 7;
    else score += 4;
    // Positioning
    if (flow.positioning === 'accumulating') score += 10;
    else if (flow.positioning === 'distributing') score += 8;
    else score += 5;
    signals.push({label: 'Flow', cls: 'flow', val: `${direction} $${amt}${denom} ${pace}x`});
  } else {
    signals.push({label: 'Flow', cls: 'flow', val: 'none'});
    // No flow data = story exists outside capital-first paradigm
  }

  // Bet conviction (max 30)
  let betBias = 'WATCH', betConviction = 'LOW';
  if (anchorAsset && anchorAsset in ANCHOR_ASSETS.reduce((m,a)=>(m[a.symbol]=a,m),{})) {
    const a = ANCHOR_ASSETS.find(x => x.symbol === anchorAsset);
    if (a) { betBias = a.bias; betConviction = a.conviction; }
    if (a && a.bias !== 'WATCH') score += 15;
    if (a && a.conviction === 'HIGH') score += 10;
    else if (a && a.conviction === 'MED') score += 5;
    signals.push({label: 'Bet', cls: 'bet', val: `${anchorAsset} ${betBias} ${betConviction}`});
  } else {
    signals.push({label: 'Bet', cls: 'bet', val: 'no match'});
  }

  // Event strength (max 20 — events without flow are noise)
  if (story.confidence === 'high') score += 10;
  if (story.they_say && story.reality) score += 5;
  if (story.extremum) score += 5;
  signals.push({label: 'Event', cls: 'event', val: story.confidence === 'high' ? 'strong' : 'moderate'});

  // Alignment bonus
  const flowDir = flow ? (flow.direction || 'none') : 'none';
  let alignment = 'neutral', alignDetail = '';
  if (flowDir === 'inflow' && betBias === 'BUY') { score += 5; alignment = 'aligned'; alignDetail = '✅ Flow+Bet aligned BUY'; }
  else if (flowDir === 'outflow' && betBias === 'SELL') { score += 5; alignment = 'aligned'; alignDetail = '✅ Flow+Bet aligned SELL'; }
  else if (flowDir === 'inflow' && betBias === 'SELL') { alignment = 'divergent'; alignDetail = '⚠️ Inflow but SELL signal'; }
  else if (flowDir === 'outflow' && betBias === 'BUY') { alignment = 'divergent'; alignDetail = '⚠️ Outflow but BUY signal'; }
  else if (betBias === 'WATCH') { alignment = 'neutral'; alignDetail = 'Bet is WATCH — no directional signal'; }

  const cappedScore = Math.min(score, 100);
  let verdict, verdictCls;
  if (cappedScore >= 85) { verdict = i18n.t('tri_max_conviction','MAX CONVICTION'); verdictCls = 'max'; }
  else if (cappedScore >= 70) { verdict = i18n.t('tri_high_conviction','HIGH CONVICTION'); verdictCls = 'high'; }
  else if (cappedScore >= 55) { verdict = i18n.t('tri_moderate','MODERATE'); verdictCls = 'moderate'; }
  else { verdict = i18n.t('tri_watch','WATCH'); verdictCls = 'watch'; }

  return { score: cappedScore, verdict, verdictCls, alignment, alignDetail, signals, anchorAsset, flowDir, betBias };
}

function renderTriangulation() {
  const el = byId('triangulationList');
  if (!el) return;

  // Collect stories from the DOM
  const cards = document.querySelectorAll('.card[data-story-id]');
  const items = [];
  cards.forEach(card => {
    const sid = card.dataset.storyId;
    const headline = card.querySelector('h3')?.textContent || '';
    const flowItem = CAPITAL_FLOWS_DATA.find(f => f.story_id === sid);
    // Build a minimal story object from card data
    const story = {
      story_id: sid,
      headline: headline,
      confidence: 'high', // default
      they_say: card.querySelector('.con-they')?.textContent || '',
      reality: card.querySelector('.con-real')?.textContent || '',
      extremum: card.querySelector('.card-extremum')?.textContent || '',
    };
    const anchorAsset = matchAnchor(headline);
    const tri = computeTriangulation(story, flowItem, anchorAsset);
    items.push({ ...tri, headline, storyId: sid });
  });

  if (items.length === 0) {
    el.innerHTML = '<div style="padding:12px;color:var(--ink-muted);font-style:italic;font-size:12px">' + i18n.t('stories_loading','Stories loading — triangulation will appear when cards are rendered.') + '</div>';
    return;
  }

  items.sort((a, b) => b.score - a.score);

  el.innerHTML = items.map(t => `
    <div class="triangulation-item">
      <div class="triangulation-header">
        <span class="triangulation-score ${t.alignment}">${t.score}</span>
        <span class="triangulation-headline">${t.headline}</span>
        <span class="triangulation-verdict ${t.verdictCls}">${t.verdict}</span>
      </div>
      <div class="triangulation-detail">
        ${t.signals.map(s => `<span><span class="tri-label ${s.cls}">${s.label}</span> ${s.val}</span>`).join('')}
        ${t.alignDetail ? `<span class="tri-align ${t.alignment}">${t.alignDetail}</span>` : ''}
      </div>
    </div>
  `).join('');
}

// ═══════════════════════════════════════════════════════════════
// CAPITAL FLOW HTML HELPER (embedded per story card)
// ═══════════════════════════════════════════════════════════════

function capitalFlowHTML(cf) {
  if (!cf) return '';
  return `
    <div class="capital-flow-block">
      <span class="cf-label">${i18n.t('capital_flow_label','CAPITAL FLOW')}</span>
      <span class="cf-line">${cf.claim || ''}</span>
      <span class="cf-line">${i18n.t('flow_projected','Projected further flow')}: ${cf.projected} (${cf.confidence} ${i18n.t('flow_confidence_pct','confidence')})</span>
      <span class="cf-line">${cf.positioning ? positionLabel(cf.positioning) : ''}</span>
    </div>`;
}

// ═══════════════════════════════════════════════════════════════
// STORY CARD RENDERING
// ═══════════════════════════════════════════════════════════════

function statusDotClass(status) {
  if (status === 'evolving') return 'story-status-dot gold pulse';
  if (status === 'stable') return 'story-status-dot sky';
  return 'story-status-dot grey';
}

// ── Severity determination ──
function determineSeverity(story) {
  const cf = story.capital_flow;
  // CRITICAL: capital_flow with large amount (>$3B) or pace >2x
  // v22.19: Read amount_b and pace_multiplier directly (pipeline writes these, not amount/denomination/pace strings)
  if (cf) {
    const amountInB = cf.amount_b || 0;
    const paceNum = cf.pace_multiplier || 1;
    if (amountInB > 3 || paceNum > 2) {
      return 'critical';
    }
  }
  // HIGH: high confidence + THE PLAY
  if (story.confidence === 'high' && story.portfolio_implication) {
    return 'high';
  }
  // Falling from the living stories format
  return 'elevated';
}

// ── Contradiction Score (0-100) ──
function calcContradictionScore(story) {
  // Measures actual narrative-vs-reality tension + flow divergence + confidence grounding
  let score = 30; // baseline — a story by definition has some contradiction

  const cf = story.capital_flow;
  const theySay = (story.they_say || '').toLowerCase();
  const reality = (story.reality || '').toLowerCase();

  // 1. Narrative-Reality Tension (0-30)
  if (theySay && reality) {
    // Count contrast markers (signals of actual contradiction, not just co-existence)
    const markers = ['but','however','not','instead','actually','yet','contrary','despite','while','whereas','though','unlike'];
    const hits = markers.filter(m => reality.includes(m)).length;
    score += Math.min(hits * 5, 15);

    // Substantive pushback: reality should be meaningful length
    if (reality.length > 50 && theySay.length > 30) score += 10;
    if (reality.length > theySay.length * 0.7) score += 5;
  }

  // 2. Flow-Narrative Divergence (0-25)
  if (cf) {
    const claim = (cf.claim || '').toLowerCase();
    const pos = /surge|boom|rally|bull|growth|soar|outperform|strength|optimis/.test(theySay);
    const neg = /crash|fear|crisis|risk|plunge|bear|collapse|sell|recession|weakness|pessimis/.test(theySay);

    if (pos && cf.direction === 'outflow') score += 20;
    else if (neg && cf.direction === 'inflow') score += 20;
    else if (pos || neg) score += 5;

    // Flow magnitude = more at stake
    const amt = parseFloat(cf.current_amount || '0');
    if (amt > 5) score += 10;
    else if (amt > 2) score += 5;
  }

  // 3. Extremum quality (0-15)
  if (story.extremum) {
    const e = story.extremum;
    if (e.winner || e.loser) score += 5;
    if (e.idiot || e.genius) score += 5;
    if ((e.winner || e.loser) && (e.idiot || e.genius)) score += 5;
  }

  // 4. Confidence grounding (0-10)
  if (story.confidence === 'high' && cf && cf.current_amount) score += 10;
  else if (story.confidence === 'high') score += 5;

  return Math.min(score, 100);
}

function livingCardHTML(story, isLead) {
  const sector = (story.sector || '').toLowerCase();
  const theySay = story.they_say || '';
  const reality = story.reality || '';
  const photoUrl = story.image_url || pickPhoto(sector, 0);
  const status = story.status || 'stable';

  // Capital flow — from story data or fallback to matching flow in CAPITAL_FLOWS_DATA
  let cf = story.capital_flow;
  if (!cf) {
    const matchedFlow = (CAPITAL_FLOWS_DATA || []).find(f => f.story_id === story.story_id);
    if (matchedFlow) {
      cf = {
        claim: matchedFlow.headline || '',
        direction: matchedFlow.direction || 'inflow',
        amount_b: matchedFlow.amount_b || 0,
        projected: matchedFlow.projected || '',
        confidence: matchedFlow.confidence_pct ? matchedFlow.confidence_pct + '%' : '70%',
        asset_class: matchedFlow.asset_class || '',
        positioning: matchedFlow.positioning || ''
      };
    }
  }
  const cfClaim = cf ? `<div class="cf-claim">${cf.claim} — projected ${cf.projected} change at ${cf.confidence} confidence</div>` : '';

  // Capital flow connector chip — flow amount + trade position (v22.29)
  let cfHint = '';
  if (cf && cf.amount_b) {
  const hintDir = (cf.direction === 'outflow') ? '↓' : '↑';
  const hintAmt = cf.amount_b >= 1 ? `$${cf.amount_b.toFixed(1)}B` : `$${(cf.amount_b * 1000).toFixed(0)}M`;
  const hintColor = cf.direction === 'outflow' ? 'var(--red)' : 'var(--green)';
  const sectorHint = cf.asset_class ? ` ${cf.asset_class}` : '';
  // Find linked trade position from ANCHOR_ASSETS
  let tradeHint = '';
  const anchorSym = cf.anchor_symbol || matchAnchor(story.headline || '');
  if (anchorSym) {
    const anchorAsset = ANCHOR_ASSETS.find(a => a.symbol === anchorSym);
    if (anchorAsset) {
      const tradeColor = anchorAsset.bias === 'BUY' || anchorAsset.bias === 'LONG' ? 'var(--green)' : anchorAsset.bias === 'SELL' || anchorAsset.bias === 'SHORT' ? 'var(--red)' : 'var(--ink-muted)';
      tradeHint = `<span style="color:${tradeColor};margin-left:4px;">→ ${anchorAsset.symbol} ${anchorAsset.bias} ${anchorAsset.conviction}</span>`;
    }
  }
  cfHint = `<span class="cf-hint" style="color:${hintColor}" title="Capital flowing ${cf.direction === 'outflow' ? 'out of' : 'into'} ${cf.asset_class || 'this sector'}">${hintAmt} ${hintDir}${sectorHint}${tradeHint}</span>`;
  }

  // Sector border-left class
  const sectorClass = sector === 'geopolitics' ? 'geopolitics' : sector === 'tech' ? 'tech' : sector === 'macro' ? 'macro' : sector === 'markets' ? 'markets' : '';

  // Status dot + update badge
  const dotClass = statusDotClass(status);
  const updateBadge = story.update_count > 0
    ? `<span class="story-update-badge">+${story.update_count} ` + i18n.t('updates','updates') + `</span>`
    : '';
  const updatedAgo = story.last_updated
    ? `<span class="updated-ago">${formatTimeAgo(story.last_updated)}</span>`
    : '';

  // Extremum line
  const extremumHTML = story.extremum ? extremumLineHTML(story.extremum) : '';

  // Severity
  const severity = determineSeverity(story);

  // Contradiction tier badge — 4 tiers for visual differentiation
  const cs = calcContradictionScore(story);
  const tier = cs >= 66 ? 'contradicted' : cs >= 51 ? 'divergent' : cs >= 31 ? 'developing' : 'aligned';
  const tierLabel = cs >= 66 ? i18n.t('tension_max','MAX TENSION') : cs >= 51 ? i18n.t('tension_high','HIGH TENSION') : cs >= 31 ? i18n.t('tension_building','BUILDING') : i18n.t('tension_consensus','CONSENSUS');
  const tierTitle = cs >= 66 ? 'Narrative inverts reality — strongest trade signal. Contradiction score: ' + cs + '/100'
    : cs >= 51 ? 'Material gap between narrative and reality — opportunity. Contradiction score: ' + cs + '/100'
    : cs >= 31 ? 'Early tension forming — watch for widening. Contradiction score: ' + cs + '/100'
    : 'Narrative and reality align — lower edge. Contradiction score: ' + cs + '/100';

  return `
    <article class="card${isLead ? ' lead' : ''}${sectorClass ? ' ' + sectorClass : ''}"
             data-story-id="${story.story_id}"
             data-status="${status}"
             data-update-count="${story.update_count}"
             data-last-updated="${story.last_updated || ''}"
             data-pillar="${story.paradigm_pillar || ''}">
      <div class="card-collapsed">
      <div class="card-head">
        ${cfClaim}
        <div style="display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;margin-bottom:2px">
          ${sector ? `<span class="category-tag ${sector}">${SECTOR_LABELS[sector] ? SECTOR_LABELS[sector]() : sector}</span>` : ''}
          <span class="severity ${severity}">${severity === 'critical' ? i18n.t('severity_critical','CRITICAL') : severity === 'high' ? i18n.t('severity_high','HIGH') : i18n.t('severity_elevated','ELEVATED')}</span>
          ${updateBadge}
          ${updatedAgo}
          <time class="story-date" datetime="${story.generated_at || story.last_updated || ''}">${story.generated_at ? new Date(story.generated_at).toLocaleDateString('en-GB', {day:'numeric',month:'short',year:'numeric'}) : ''}</time>
        </div>
        <div style="display:flex;align-items:flex-start;gap:6px">
          <h3 style="flex:1"><a href="./story.html?id=${story.story_id}" style="color:inherit;text-decoration:none">${story.headline}</a></h3>
          ${cfHint}
          <span class="tier-badge ${tier}" title="${tierTitle}">${tierLabel} <span class="tier-score">${cs}/100</span></span>
        </div>
      </div>
      </div><!-- /card-collapsed -->
      <div class="card-expanded-body">
        ${reality ? `<p class="summary">${reality}</p>` : ''}
        ${theySay || reality ? `
        <div class="detail">
          ${theySay ? `<div class="con-they"><span class="con-label">${i18n.t('they_say','They say')}</span>${theySay}</div>` : ''}
          ${reality ? `<div class="con-real"><span class="con-label">${i18n.t('reality','Reality')}</span>${reality}</div>` : ''}
        </div>` : ''}
        ${capitalFlowHTML(cf)}
        ${story.portfolio_implication ? `
        <div class="the-play">
          <span class="pi-label">${i18n.t('the_play_label','THE PLAY')}</span>
          <span class="pi-text">${story.portfolio_implication}</span>
        </div>` : ''}
        ${extremumHTML}
        <a href="./story.html?id=${story.story_id}" class="intel-report-link" data-i18n="story_full_report">Full intelligence report →</a>
        <div class="share-row">
          <button class="share-btn copy-link" title="${i18n.t('share_copy','Copy link')}" onclick="copyShareLink(this.closest('.card'))">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
          </button>
          <button class="share-btn share-x" title="${i18n.t('share_x','Share on X')}" onclick="shareToX(this.closest('.card'))">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4l7.5 7.5L4 19"/><path d="M20 4l-7.5 7.5L20 19"/></svg>
          </button>
          <button class="share-btn share-facebook" title="${i18n.t('share_facebook','Share on Facebook')}" onclick="shareToFacebook(this.closest('.card'))">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
          </button>
          <button class="share-btn share-telegram" title="${i18n.t('share_telegram','Share on Telegram')}" onclick="shareToTelegram(this.closest('.card'))">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </button>
          <button class="share-btn share-reddit" title="${i18n.t('share_reddit','Share on Reddit')}" onclick="shareToReddit(this.closest('.card'))">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 8s-4-1-8 2"/><path d="M8 16s4 1 8-2"/><circle cx="9" cy="9" r="0.5" fill="currentColor"/><circle cx="15" cy="9" r="0.5" fill="currentColor"/></svg>
          </button>
        </div>
        <div class="card-photo">
          <img src="${photoUrl}" alt="${sector}" loading="lazy" onerror="this.parentElement.style.display='none'">
        </div>
      </div>
      <div class="story-evolution-timeline" style="display:none">
        <div class="timeline-loading">${i18n.t('loading_timeline','Loading evolution timeline...')}</div>
      </div>
      ${story.status === 'resolved' ? `<div class="resolved-banner"><span class="resolved-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span><span>${i18n.t('resolved','Resolved')}</span></div>` : ''}
    </article>`;
}

// ── Extremum Line HTML ──
function extremumLineHTML(extremumStr) {
  if (!extremumStr) return '';
  // Handle object format: {type, description}
  if (typeof extremumStr === 'object') {
    const t = extremumStr.type || '';
    const desc = extremumStr.description || JSON.stringify(extremumStr);
    const typeLabel = t.replace(/_/g, ' ').toUpperCase();
    return `
    <div class="card-extremum">
      <span class="ex-label">${i18n.t('extremum','EXTREMUM')}</span>
      <span class="ex-win">${typeLabel}: ${desc.slice(0,120)}</span>
    </div>`;
  }
  // Parse string format: "WINNER: ... | LOSER: ... | IDIOT: ... | GENIUS: ..."
  const parts = extremumStr.split('|').map(s => s.trim());
  let winner = '', loser = '', idiot = '', genius = '';
  parts.forEach(p => {
    if (p.startsWith('WINNER:')) winner = p.replace('WINNER:', '').trim();
    else if (p.startsWith('LOSER:')) loser = p.replace('LOSER:', '').trim();
    else if (p.startsWith('IDIOT:')) idiot = p.replace('IDIOT:', '').trim();
    else if (p.startsWith('GENIUS:')) genius = p.replace('GENIUS:', '').trim();
  });
  return `
    <div class="card-extremum">
      <span class="ex-label">${i18n.t('extremum','EXTREMUM')}</span>
      ${winner ? `<span class="ex-win">${i18n.t('winner','WINNER')}: ${winner}</span>` : ''}
      ${loser ? `<span class="ex-lose">${i18n.t('loser','LOSER')}: ${loser}</span>` : ''}
      ${idiot ? `<span class="ex-idiot">${i18n.t('idiot','IDIOT')}: ${idiot}</span>` : ''}
      ${genius ? `<span class="ex-genius">${i18n.t('genius','GENIUS')}: ${genius}</span>` : ''}
    </div>`;
}

// ── Card click: expand/collapse + lazy-load timeline (event delegation) ──
function wireCardDelegation() {
  const newsCol = byId('newsCol');
  if (!newsCol) return;

  newsCol.addEventListener('click', async function(e) {
    // Skip share menu clicks — they're handled by wireShareControls
    if (e.target.closest('.share-toggle') || e.target.closest('.share-menu') || e.target.closest('.thread-pill') || e.target.closest('.resolved-archive-link')) return;

    const card = e.target.closest('.card');
    if (!card) return;

    const storyId = card.dataset.storyId;
    const timelineEl = card.querySelector('.story-evolution-timeline');
    if (!timelineEl) return;

    const wasExpanded = card.classList.contains('expanded');

    // Close all other expanded cards
    document.querySelectorAll('.card.expanded').forEach(c => {
      if (c !== card) c.classList.remove('expanded');
    });

    if (wasExpanded) {
      card.classList.remove('expanded');
      return;
    }

    // Expand this card
    card.classList.add('expanded');

    // Lazy-load timeline
    if (!timelineEl.dataset.loaded) {
      timelineEl.style.display = 'block';
      timelineEl.innerHTML = '<div class="timeline-loading">' + i18n.t('loading_timeline','Loading evolution timeline...') + '</div>';

      try {
        const timelineData = await getJSON(`./data/stories/${storyId}/timeline.json`, null);
        if (timelineData && timelineData.threads) {
          timelineEl.innerHTML = timelineHTML(timelineData, timelineData.threads[0]?.thread_id);
          timelineEl.dataset.loaded = 'true';
          wireThreadNavigation(timelineEl, timelineData, storyId);
        } else {
          timelineEl.innerHTML = '<div class="timeline-empty">' + i18n.t('no_evolution','No evolution data available yet.') + '</div>';
          timelineEl.dataset.loaded = 'true';
        }
      } catch (err) {
        timelineEl.innerHTML = '<div class="timeline-empty">' + i18n.t('could_not_load','Could not load timeline.') + '</div>';
        timelineEl.dataset.loaded = 'true';
      }
    } else {
      timelineEl.style.display = 'block';
    }
  });
}

// ── Timeline rendering (simplified, preserved from v18) ──
function timelineHTML(timelineData, activeThreadId) {
  const thread = timelineData.threads?.find(t => t.thread_id === activeThreadId)
    || timelineData.threads?.[0];
  if (!thread) return '<div class="timeline-empty">No thread data.</div>';

  const threadNav = timelineData.threads && timelineData.threads.length > 1
    ? `<div class="thread-nav">${timelineData.threads.map(t =>
        `<span class="thread-pill${t.thread_id === activeThreadId ? ' active' : ''}" data-thread-id="${t.thread_id}">${t.type === 'main' ? i18n.t('main','Main') : (t.current_state?.headline?.slice(0,30) || t.thread_id.slice(0,25))} (${t.evolution?.length || 0})</span>`
      ).join('')}</div>`
    : '';

  const entries = (thread.evolution || []).map((ev, i) => {
    const isLatest = i === thread.evolution.length - 1;
    const dotClass = (ev.type === 'frame_shift' || ev.type === 'thread_creation')
      ? (isLatest ? 'timeline-dot gold pulse' : 'timeline-dot gold')
      : (isLatest ? 'timeline-dot gold pulse' : 'timeline-dot');
    const typeLabel = ev.type.replace(/_/g, ' ');
    const sourceStr = ev.source_count ? ` · ${ev.source_count} sources` : '';
    return `
      <div class="update-entry" data-type="${ev.type}"${isLatest ? ' data-latest="true"' : ''}>
        <span class="${dotClass}"></span>
        <div class="timeline-content">
          <span class="update-timestamp">${formatTimestamp(ev.timestamp)}</span>
          <span class="update-type-badge">${typeLabel}</span>
          <p class="update-delta">${ev.reality_delta || ''}</p>
          ${ev.sub_thread_spawned ? `<span class="update-spawn">→ Sub-thread spawned</span>` : ''}
        </div>
      </div>`;
  }).join('');

  return `${threadNav}<div class="timeline-entries">${entries}</div>
    <div class="timeline-state">
      <span class="timeline-state-label">Status: </span>
      <span class="story-status-dot ${statusDotClass(timelineData.status)}"></span>
      <span class="timeline-state-text">${timelineData.status || 'unknown'}</span>
      <span class="timeline-source-count">${thread.current_state?.source_count || 0} sources</span>
    </div>`;
}

function wireThreadNavigation(timelineEl, timelineData, storyId) {
  timelineEl.querySelectorAll('.thread-pill').forEach(pill => {
    pill.addEventListener('click', function(e) {
      e.stopPropagation();
      const threadId = this.dataset.threadId;
      timelineEl.querySelectorAll('.thread-pill').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      const entriesContainer = timelineEl.querySelector('.timeline-entries');
      const stateContainer = timelineEl.querySelector('.timeline-state');
      if (entriesContainer && stateContainer) {
        const thread = timelineData.threads.find(t => t.thread_id === threadId);
        if (thread) {
          const entries = (thread.evolution || []).map((ev, i) => {
            const isLatest = i === thread.evolution.length - 1;
            const dotClass = (ev.type === 'frame_shift' || ev.type === 'thread_creation')
              ? (isLatest ? 'timeline-dot gold pulse' : 'timeline-dot gold')
              : (isLatest ? 'timeline-dot gold pulse' : 'timeline-dot');
            const typeLabel = ev.type.replace(/_/g, ' ');
            return `<div class="update-entry" data-type="${ev.type}"${isLatest ? ' data-latest="true"' : ''}>
              <span class="${dotClass}"></span>
              <div class="timeline-content">
                <span class="update-timestamp">${formatTimestamp(ev.timestamp)}</span>
                <span class="update-type-badge">${typeLabel}</span>
                <p class="update-delta">${ev.reality_delta || ''}</p>
                ${ev.sub_thread_spawned ? `<span class="update-spawn">→ Sub-thread spawned</span>` : ''}
              </div>
            </div>`;
          }).join('');
          entriesContainer.innerHTML = entries;
          stateContainer.innerHTML = `
            <span class="timeline-state-label">Status: </span>
            <span class="story-status-dot ${statusDotClass(timelineData.status)}"></span>
            <span class="timeline-state-text">${timelineData.status || 'unknown'}</span>
            <span class="timeline-source-count">${thread.current_state?.source_count || 0} sources</span>`;
          wireThreadNavigation(timelineEl, timelineData, storyId);
        }
      }
    });
  });
}

// ═══════════════════════════════════════════════════════════════
// STORY ACCUMULATION — appendStoryCard adds new cards at the top
// ═══════════════════════════════════════════════════════════════

function appendStoryCard(story, isLead) {
  const el = byId('newsCol');
  if (!el) return;

  // Check if this story_id already exists (deduplication)
  // Deduplication: only check inside newsCol — flow items also carry data-story-id
  if (el.querySelector(`[data-story-id="${story.story_id}"]`)) return;
  if (capturedStoryIds.has(story.story_id)) return;
  capturedStoryIds.add(story.story_id);

  const html = livingCardHTML(story, isLead);
  // Insert at the top — newest first
  el.insertAdjacentHTML('afterbegin', html);

  // Populate story cache for flow→story cross-linking
  STORIES_CACHE[story.story_id] = { headline: story.headline };

  // Update story count badge
  updateStoryCount();
}

function updateStoryCount() {
  const countEl = byId('storyCount');
  const heroCountEl = byId('heroStoryCount');
  const count = document.querySelectorAll('.card[data-story-id]').length;
  if (countEl) countEl.textContent = `${count} ${i18n.t('hero_stories','stories')}`;
  if (heroCountEl) heroCountEl.textContent = String(count);
  updateCumulativeStats();
}

// ═══════════════════════════════════════════════════════════════
// CUMULATIVE TRACKING — forever counters (localStorage)
// ═══════════════════════════════════════════════════════════════

function getCumulative(key, fallback) {
  try {
    const v = localStorage.getItem('gazzetta_' + key);
    return v ? JSON.parse(v) : fallback;
  } catch(e) { return fallback; }
}

function setCumulative(key, val) {
  try { localStorage.setItem('gazzetta_' + key, JSON.stringify(val)); } catch(e) {}
}

function updateCumulativeStats() {
  // Stories tracked — cumulative, never decreases
  const currentStories = document.querySelectorAll('.card[data-story-id]').length;
  let tracked = getCumulative('stories_tracked', 10);
  if (currentStories > tracked) {
    tracked = currentStories;
    setCumulative('stories_tracked', tracked);
  }

  // Capital tracked — parse current total from flow data and accumulate
  let flowTotal = 0;
  CAPITAL_FLOWS_DATA.forEach(f => {
    flowTotal += (f.amount_b || 0);
  });
  let cumFlow = getCumulative('capital_tracked_b', 17.1);
  if (flowTotal > cumFlow) {
    cumFlow = flowTotal;
    setCumulative('capital_tracked_b', cumFlow);
  }

  // Assets positioned
  let cumAssets = getCumulative('assets_positioned', 14);
  if (ANCHOR_ASSETS.length > cumAssets) {
    cumAssets = ANCHOR_ASSETS.length;
    setCumulative('assets_positioned', cumAssets);
  }

  // Total at stake — sum of all entry prices × conviction multiplier
  let stakeTotal = 0;
  ANCHOR_ASSETS.forEach(a => {
    const price = parseFloat(String(a.price).replace(/[,$%bp]/g, ''));
    if (!isNaN(price)) {
      const mult = a.conviction === 'HIGH' ? 1.5 : a.conviction === 'MED' ? 1.0 : 0.5;
      stakeTotal += price * mult;
    }
  });
  stakeTotal = Math.round(stakeTotal / 1000); // in thousands for display
  let cumStake = getCumulative('total_at_stake_k', 18.4);
  if (stakeTotal > cumStake) {
    cumStake = stakeTotal;
    setCumulative('total_at_stake_k', cumStake);
  }

  // Update hero stats — use CURRENT numbers, not cumulative localStorage
  const heroStory = byId('heroStoryCount');
  const heroFlow = byId('heroFlowTotal');
  const heroAssets = byId('heroAssetCount');
  const heroStake = byId('heroBetTotal');
  const heroLayers = byId('heroLayerCount');
  const heroProduct = byId('heroProductCount');
  if (heroStory) heroStory.textContent = String(currentStories);
  if (heroFlow) heroFlow.textContent = '$' + cumFlow.toFixed(1) + 'B';
  if (heroAssets) heroAssets.textContent = String(cumAssets);
  if (heroStake) heroStake.textContent = '$' + cumStake.toFixed(1) + 'K';
  if (heroLayers) heroLayers.textContent = String(document.querySelectorAll('.container.collapsible').length);
  if (heroProduct) heroProduct.textContent = String(document.querySelectorAll('.hint-card').length || 5);
}

// ═══════════════════════════════════════════════════════════════
// TRACK RECORD — store predictions, compute realized P&L
// ═══════════════════════════════════════════════════════════════

const TRACK_RECORD_KEY = 'gazzetta_track_record';

function getTrackRecord() {
  try {
    const v = localStorage.getItem(TRACK_RECORD_KEY);
    return v ? JSON.parse(v) : [];
  } catch(e) { return []; }
}

function saveTrackRecord(records) {
  try { localStorage.setItem(TRACK_RECORD_KEY, JSON.stringify(records)); } catch(e) {}
}

function snapshotPredictions() {
  const today = new Date().toISOString().slice(0, 10);
  const records = getTrackRecord();
  const alreadySnapped = records.some(r => r.date === today);
  if (alreadySnapped) return records;

  ANCHOR_ASSETS.forEach(a => {
    records.push({
      date: today,
      symbol: a.symbol,
      bias: a.bias,
      entry: a.entry,
      target: a.target,
      stop: a.stop,
      conviction: a.conviction,
      atr_pct: a.atr_pct,
      price_at_snapshot: a.price,
      settled: false
    });
  });

  saveTrackRecord(records);
  return records;
}

function settlePredictions() {
  const records = getTrackRecord();
  let changed = false;

  records.forEach(r => {
    if (r.settled) return;

    // Find current asset data
    const current = ANCHOR_ASSETS.find(a => a.symbol === r.symbol);
    if (!current) return;

    const entry = parseFloat(String(r.entry).replace(/,/g, ''));
    const currentPrice = parseFloat(String(current.price).replace(/[,$%bp]/g, ''));
    const target = parseFloat(String(r.target).replace(/,/g, ''));
    const stop = parseFloat(String(r.stop).replace(/,/g, ''));

    if (isNaN(entry) || isNaN(currentPrice)) return;

    // Determine if target or stop was hit
    let hitTarget = false, hitStop = false;
    if (r.bias === 'BUY') {
      hitTarget = currentPrice >= target;
      hitStop = stop !== null && currentPrice <= stop;
    } else if (r.bias === 'SELL') {
      hitTarget = currentPrice <= target;
      hitStop = stop !== null && currentPrice >= stop;
    } else {
      // WATCH — settle on significant move: >2× ATR from entry
      const atrMove = entry * (r.atr_pct || 0.02);
      hitTarget = Math.abs(currentPrice - entry) > atrMove * 3;
    }

    // Calculate P&L
    let pnlPct;
    if (r.bias === 'BUY' || r.bias === 'SELL') {
      // Directional: long/short return
      if (r.bias === 'BUY') {
        pnlPct = ((currentPrice - entry) / entry) * 100;
      } else {
        pnlPct = ((entry - currentPrice) / entry) * 100;
      }
    } else {
      // WATCH: absolute move P&L (just measuring event magnitude)
      pnlPct = (Math.abs(currentPrice - entry) / entry) * 100;
    }

    // Settle if target, stop, or >7 days old
    const ageDays = (Date.now() - new Date(r.date).getTime()) / 86400000;
    const shouldSettle = hitTarget || hitStop || ageDays > 7;

    if (shouldSettle) {
      r.settled = true;
      r.realized_pnl_pct = Math.round(pnlPct * 10) / 10;
      r.resolved_price = String(currentPrice);
      r.resolved_reason = hitTarget ? 'target' : hitStop ? 'stop' : 'expiry';
      r.resolved_date = new Date().toISOString().slice(0, 10);
      changed = true;
    }
  });

  if (changed) saveTrackRecord(records);
  return records;
}

function computeTrackRecordStats() {
  const records = getTrackRecord();
  const settled = records.filter(r => r.settled && r.realized_pnl_pct !== undefined);
  const open = records.filter(r => !r.settled);
  const wins = settled.filter(r => r.realized_pnl_pct > 0);
  const losses = settled.filter(r => r.realized_pnl_pct <= 0);

  const totalPnL = settled.reduce((s, r) => s + (r.realized_pnl_pct || 0), 0);
  const avgWin = wins.length ? wins.reduce((s, r) => s + r.realized_pnl_pct, 0) / wins.length : 0;
  const avgLoss = losses.length ? losses.reduce((s, r) => s + r.realized_pnl_pct, 0) / losses.length : 0;
  const winRate = settled.length ? Math.round(wins.length / settled.length * 100) : 0;

  return {
    total: settled.length,
    open: open.length,
    wins: wins.length,
    losses: losses.length,
    winRate,
    totalPnL: Math.round(totalPnL * 10) / 10,
    avgWin: Math.round(avgWin * 10) / 10,
    avgLoss: Math.round(avgLoss * 10) / 10,
    expectancy: settled.length ? Math.round((winRate/100 * avgWin + (1-winRate/100) * avgLoss) * 10) / 10 : 0,
    lastSettled: settled.length ? settled.sort((a,b) => b.date.localeCompare(a.date))[0] : null
  };
}

function renderTrackRecord(targetId) {
  const el = document.getElementById(targetId);
  if (!el) return;

  snapshotPredictions();
  settlePredictions();
  const stats = computeTrackRecordStats();

  let html = '';
  if (stats.total === 0) {
    const openCount = stats.open || 0;
    const openExposure = openCount > 0 ? '$' + (openCount * 1.5).toFixed(1) + 'K' : '—';
    html = `<div class="tr-active">
      <div class="tr-grid">
        <div class="tr-stat"><span class="tr-val">${openCount}</span><span class="tr-label">Open Positions</span></div>
        <div class="tr-stat"><span class="tr-val">${openExposure}</span><span class="tr-label">Notional Exposure</span></div>
        <div class="tr-stat"><span class="tr-val">0</span><span class="tr-label">Settled</span></div>
      </div>
      <div class="tr-empty" style="margin-top:8px">Positions snapshotted today. First settlements expected within 7 days as targets/stops hit.</div>
    </div>`;
  } else {
    html = `
      <div class="tr-grid">
        <div class="tr-stat"><span class="tr-val">${stats.total}</span><span class="tr-label">Bets Settled</span></div>
        <div class="tr-stat"><span class="tr-val">${stats.winRate}%</span><span class="tr-label">Win Rate</span></div>
        <div class="tr-stat"><span class="tr-val">${stats.totalPnL > 0 ? '+' : ''}${stats.totalPnL}%</span><span class="tr-label">Total P&L</span></div>
        <div class="tr-stat"><span class="tr-val">${stats.expectancy > 0 ? '+' : ''}${stats.expectancy}%</span><span class="tr-label">Expectancy</span></div>
      </div>
      <div class="tr-detail">
        <span>Avg win: +${stats.avgWin}%</span>
        <span>Avg loss: ${stats.avgLoss}%</span>
        <span>Open positions: ${stats.open}</span>
      </div>`;
  }

  // Methodology link
  html += `<div class="tr-methodology"><a href="capital.html">Full methodology →</a></div>`;
  el.innerHTML = html;
}

// ═══════════════════════════════════════════════════════════════
// PATCH EXISTING CARD
// ═══════════════════════════════════════════════════════════════

function patchStoryCard(card, story) {
  if (!card) return;

  card.dataset.status = story.status || 'stable';
  card.dataset.updateCount = String(story.update_count || 0);
  card.dataset.lastUpdated = story.last_updated || '';

  const dot = card.querySelector('.story-status-dot');
  if (dot) {
    const newClass = statusDotClass(story.status);
    dot.className = newClass;
  }

  const badge = card.querySelector('.story-update-badge');
  if (badge) {
    const newCount = story.update_count || 0;
    badge.textContent = `+${newCount} updates`;
    if (newCount > 0) {
      card.classList.add('recently-updated');
      setTimeout(() => card.classList.remove('recently-updated'), 3000);
    }
  }

  const ago = card.querySelector('.updated-ago');
  if (ago && story.last_updated) {
    ago.textContent = formatTimeAgo(story.last_updated);
  }

  const headlineEl = card.querySelector('h3');
  if (headlineEl && !headlineEl.dataset.original) {
    headlineEl.dataset.original = story.headline;
    headlineEl.textContent = story.headline;
  }

  // Update severity badge
  const sevEl = card.querySelector('.severity');
  if (sevEl) {
    const newSev = determineSeverity(story);
    sevEl.className = 'severity ' + newSev;
    sevEl.textContent = newSev;
  }

  // Update contradiction tier badge
  const tierEl = card.querySelector('.tier-badge');
  if (tierEl) {
    const newCs = calcContradictionScore(story);
    const newTier = newCs >= 66 ? 'contradicted' : newCs >= 51 ? 'divergent' : newCs >= 31 ? 'developing' : 'aligned';
    const newLabel = newCs >= 66 ? 'MAX TENSION' : newCs >= 51 ? 'HIGH TENSION' : newCs >= 31 ? 'BUILDING' : 'CONSENSUS';
    const newTitle = newCs >= 66 ? 'Narrative inverts reality — strongest trade signal. Contradiction score: ' + newCs + '/100'
      : newCs >= 51 ? 'Material gap between narrative and reality — opportunity. Contradiction score: ' + newCs + '/100'
      : newCs >= 31 ? 'Early tension forming — watch for widening. Contradiction score: ' + newCs + '/100'
      : 'Narrative and reality align — lower edge. Contradiction score: ' + newCs + '/100';
    tierEl.className = 'tier-badge ' + newTier;
    tierEl.title = newTitle;
    tierEl.innerHTML = newLabel + ' <span class="tier-score">' + newCs + '/100</span>';
  }

  const summary = card.querySelector('.summary');
  if (summary && story.reality) {
    summary.textContent = story.reality;
  }

  const conThey = card.querySelector('.con-they');
  if (conThey && story.they_say) {
    conThey.innerHTML = `<span class="con-label">They say</span>${story.they_say}`;
  }
  const conReal = card.querySelector('.con-real');
  if (conReal && story.reality) {
    conReal.innerHTML = `<span class="con-label">Reality</span>${story.reality}`;
  }

  if (story.portfolio_implication) {
    const piEl = card.querySelector('.the-play');
    if (piEl) {
      const textEl = piEl.querySelector('.pi-text');
      if (textEl) textEl.textContent = story.portfolio_implication;
    } else {
      const detailEl = card.querySelector('.detail');
      if (detailEl) {
        detailEl.insertAdjacentHTML('afterend', `
          <div class="the-play">
            <span class="pi-label">THE PLAY</span>
            <span class="pi-text">${story.portfolio_implication}</span>
          </div>`);
      }
    }
  }

  if (story.last_updated && Date.now() - new Date(story.last_updated).getTime() < 600000) {
    if (!card.classList.contains('recently-updated')) {
      card.classList.add('recently-updated');
      setTimeout(() => card.classList.remove('recently-updated'), 3000);
    }
  }
}

// ═══════════════════════════════════════════════════════════════
// POLLING — accumulate, never remove
// ═══════════════════════════════════════════════════════════════

async function pollLivingStories() {
  const data = await getJSON(LIVING_DATA, null);
  if (!data) return;

  updateMastheadLiving(data.generated_at, data.next_micro_update);

  // Build story list — deduplicate: skip if story_id matches lead
  const leadId = data.lead?.story_id;
  const stories = (data.stories || []).filter(s => s.story_id !== leadId);
  const allStories = [data.lead, ...stories, ...(data.archived_stories || [])].filter(Boolean);

  allStories.forEach(story => {
    const card = document.querySelector(`[data-story-id="${story.story_id}"]`);
    if (card) {
      patchStoryCard(card, story);
    } else {
      appendStoryCard(story, story === data.lead);
    }
  });

  updateTimestamps();
  // Refresh flow→story links (new cards may have arrived)
  refreshFlowStoryLinks();
}

function updateTimestamps() {
  document.querySelectorAll('.card[data-last-updated]').forEach(card => {
    const iso = card.dataset.lastUpdated;
    if (iso) {
      const ago = card.querySelector('.updated-ago');
      if (ago) ago.textContent = formatTimeAgo(iso);
    }
  });
}

// ═══════════════════════════════════════════════
// SHARE — conventional visible buttons (X, FB, Telegram, Reddit, Copy)
// ═══════════════════════════════════════════════

function getShareText(articleEl) {
  const headline = articleEl.querySelector('h3')?.textContent || '';
  const playEl = articleEl.querySelector('.the-play .pi-text');
  const playText = playEl ? playEl.textContent.trim() : '';
  const url = window.location.href;
  let text = headline;
  if (playText) text += '\n\n' + playText;
  text += '\n\n' + url;
  return text;
}

function showToast(msg) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}

function copyShareLink(card) {
  if (!card) return;
  const text = getShareText(card);
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => showToast('✓ Link copied')).catch(() => {});
  } else {
    try { document.execCommand('copy'); showToast('✓ Link copied'); } catch(e) {}
  }
}

function shareToX(card) {
  if (!card) return;
  const text = getShareText(card);
  window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(text), '_blank', 'width=600,height=400');
}

function shareToFacebook(card) {
  if (!card) return;
  const url = encodeURIComponent(window.location.href);
  window.open('https://www.facebook.com/sharer/sharer.php?u=' + url, '_blank', 'width=600,height=400');
}

function shareToTelegram(card) {
  if (!card) return;
  const text = getShareText(card);
  const url = window.location.href;
  const shareUrl = 'https://t.me/share/url?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(text.split('\n')[0]);
  window.open(shareUrl, '_blank', 'width=600,height=400');
}

function shareToReddit(card) {
  if (!card) return;
  const headline = card.querySelector('h3')?.textContent || '';
  const url = encodeURIComponent(window.location.href);
  window.open('https://www.reddit.com/submit?url=' + url + '&title=' + encodeURIComponent(headline), '_blank', 'width=800,height=600');
}

// ═══════════════════════════════════════════════════════════════
// BOOT
// ═══════════════════════════════════════════════════════════════

async function boot() {
  // Wait for i18n translations to finish loading before rendering
  if (window.i18n && !window.i18n._ready) {
    await new Promise(resolve => {
      const check = () => {
        if (window.i18n._ready) { resolve(); return; }
        setTimeout(check, 50);
      };
      window.addEventListener('i18nReady', resolve, { once: true });
      check();
      // Hard safety: proceed after 5s regardless
      setTimeout(resolve, 5000);
    });
  }

  // v22.18: Product page detection — only render what exists on this page
  const isProductPage = !!document.querySelector('.product-page');
  
  // Wire collapsible containers first (if any)
  wireCollapsibleContainers();

  // Wire card click delegation (one listener on newsCol for all cards)
  wireCardDelegation();

  // Render static content — only if containers exist on this page
  if (byId('anchorGrid')) renderAnchor();
  if (byId('trackRecord')) renderTrackRecord('trackRecord');

  // Set masthead timestamp IMMEDIATELY (don't wait for async ops)
  updateMasthead();

  // Fetch flows — only if flows container exists
  if (byId('flowsList')) await fetchFlows();

  // Start flows polling (5 min cadence)
  setInterval(fetchFlows, FLOWS_POLL_INTERVAL);

  // Try data sources
  const livingData = await getJSON(LIVING_DATA, null);

  // v20.22: living_stories.json now uses active_stories (no 'lead' key).
  // If it has a legacy 'lead', render directly. Otherwise fall through to stories.json.
  if (livingData && livingData.lead) {
    // Render with living stories format (legacy)
    const leadId = livingData.lead?.story_id;
    const stories = (livingData.stories || []).filter(s => s.story_id !== leadId);
    const all = [livingData.lead, ...stories, ...(livingData.archived_stories || [])].filter(Boolean);

    const el = byId('newsCol');
    if (el) {
      all.forEach((s, i) => appendStoryCard(s, i === 0));
    }

    // Triangulation AFTER cards are in DOM — with mutation observer fallback
    scheduleTriangulation();
    updateMastheadLiving(livingData.generated_at, livingData.next_micro_update);
    updateMasthead();
    // Refresh flow→story links now that stories are in DOM
    refreshFlowStoryLinks();
    // Re-apply i18n to dynamically inserted DOM (v22.18)
    if (window.i18n && window.i18n.applyTranslations) window.i18n.applyTranslations();

    // Start polling
    setInterval(pollLivingStories, POLL_INTERVAL);
    updateCumulativeStats();
    return;
  }

  // v20.22: Update masthead with living_stories timestamp even when using stories.json fallback
  if (livingData && livingData.generated_at) {
    updateMastheadLiving(livingData.generated_at, livingData.next_micro_update);
  }

  // Fallback: stories.json
  const data = await getJSON(getDataPath(), null);
  if (!data || !data.lead) {
    const el = byId('newsCol');
    if (el) el.innerHTML = '<p style="text-align:center;color:var(--ink-muted);padding:40px;font-style:italic">Intelligence update in progress.</p>';
    updateCumulativeStats();
    updateMasthead();
    return;
  }

  // Deduplicate: filter out stories matching lead story_id
  const leadId = data.lead.story_id;
  const filteredStories = (data.stories || []).filter(s => s.story_id !== leadId);
  const all = [data.lead, ...filteredStories].filter(Boolean);

  const el2 = byId('newsCol');
  if (el2) {
    all.forEach((s, i) => appendStoryCard(s, i === 0));
  }

  // Triangulation AFTER cards are in DOM — with retry
  scheduleTriangulation();
  updateCumulativeStats();
  updateMasthead();
  // Refresh flow→story links now that stories are in DOM
  refreshFlowStoryLinks();
  // Re-apply i18n to dynamically inserted DOM (v22.18)
  if (window.i18n && window.i18n.applyTranslations) window.i18n.applyTranslations();

  // v22.18: Hints lobby — populate front page cards from summary.json
  if (document.querySelector('.hints-lobby')) {
    fetch('./api/v1/home/summary.json?t=' + Date.now(), {cache:'no-store'})
      .then(r => r.json())
      .then(d => {
        if (d.stories) {
          const sc = document.getElementById('hintStoriesCount');
          const sl = document.getElementById('hintStoriesLatest');
          if (sc) sc.textContent = d.stories.count + ' stories';
          if (sl) sl.textContent = (d.stories.lead_headline || '').slice(0, 60) + '...';
        }
        if (d.flows) {
          const fa = document.getElementById('hintFlowsAmount');
          const fd = document.getElementById('hintFlowsDirection');
          if (fa) fa.textContent = '$' + d.flows.total_b.toFixed(1) + 'B';
          if (fd) {
            const arrow = d.flows.direction === 'bullish' ? '↑' : '↓';
            fd.textContent = arrow + ' ' + d.flows.inflows + ' inflows · ' + d.flows.outflows + ' outflows · ' + d.flows.confidence + '% confidence';
          }
        }
        if (d.trades) {
          const tc = document.getElementById('hintTradesCount');
          const tt = document.getElementById('hintTradesTop');
          if (tc) tc.textContent = d.trades.open_count + ' positions';
          if (tt) tt.textContent = 'PDR ' + d.trades.pdr + ' · Top: ' + (d.trades.top_tickers || []).join(', ');
        }
        if (d.signal) {
          const ss = document.getElementById('hintSignalScore');
          const sd = document.getElementById('hintSignalDetail');
          if (ss) ss.textContent = d.signal.highest_score + '/100';
          if (sd) sd.textContent = d.signal.count + ' signals · ' + d.signal.max_conviction + ' max conviction';
        }
        if (d.track) {
          const tr = document.getElementById('hintTrackRate');
          const tt = document.getElementById('hintTrackTotal');
          if (tr) tr.textContent = d.track.win_rate + '%';
          if (tt) tt.textContent = 'Win rate · ' + d.track.total_trades + ' trades · +' + d.track.avg_return + '% avg';
        }
      })
      .catch(() => {}); // Silent fail — cards show dashes
  }
  // v22.18: Mobile hint condensation — shorten subtitles on small screens
  if (window.innerWidth < 600 && document.querySelector('.hints-lobby')) {
    document.querySelectorAll('.hint-card-sub').forEach(el => {
      const text = el.textContent;
      // Condense to ~60 chars max
      if (text.length > 60) {
        el.textContent = text.slice(0, 57).trim() + '...';
      }
    });
    // Smaller value font on mobile
    document.querySelectorAll('.hint-card-value').forEach(el => {
      el.style.fontSize = '20px';
    });
  }


}

// v22.20: Front-page teaser populator — headlines only, not full content
async function populateTeasers() {
  if (!document.querySelector('.teaser-list')) return;

  // Stories teaser
  try {
    const storiesData = await getJSON(getDataPath(), null);
    if (storiesData && storiesData.stories) {
      const el = document.getElementById('storiesTeaserContent');
      const countEl = document.getElementById('teaserStoryCount');
      if (el) {
        const items = [storiesData.lead, ...storiesData.stories].filter(Boolean).slice(0, 8);
        el.innerHTML = items.map(s => {
          const cf = s.capital_flow || {};
          const amtHtml = cf.amount_b ? `<span class="teaser-amount">$${cf.amount_b}B</span>` : '';
          const headline = (s.headline || '').slice(0, 80);
          return `<a href="./story.html?id=${s.story_id || s.id || ''}" class="teaser-item">${amtHtml}${headline}</a>`;
        }).join('');
        if (countEl) countEl.textContent = items.length + ' stories';
      }
    }
  } catch(e) {}

  // Flows teaser
  try {
    const flowsData = await getJSON(getFlowsPath(), null);
    if (flowsData && flowsData.flows) {
      const el = document.getElementById('flowsTeaserContent');
      const subEl = document.getElementById('teaserFlowSub');
      if (el) {
        const items = flowsData.flows.slice(0, 6);
        el.innerHTML = items.map(f => {
          const cls = f.direction === 'outflow' ? 'outflow' : '';
          return `<a href="./flows.html" class="teaser-item"><span class="teaser-amount ${cls}">$${f.amount_b}B ${f.direction === 'inflow' ? '↑' : '↓'}</span>${f.asset_class} — ${(f.headline || '').replace(/^\$[\d.]+B\s*[↑↓]\s*/, '')}</a>`;
        }).join('');
        if (subEl) {
          const inflows = flowsData.flows.filter(f => f.direction === 'inflow').length;
          const outflows = flowsData.flows.filter(f => f.direction === 'outflow').length;
          subEl.textContent = `${inflows} inflows · ${outflows} outflows · ${flowsData.aggregate_confidence}%`;
        }
      }
    }
  } catch(e) {}

  // Trades teaser
  try {
    if (typeof ANCHOR_ASSETS !== 'undefined' && ANCHOR_ASSETS.length) {
      const el = document.getElementById('tradesTeaserContent');
      const subEl = document.getElementById('teaserTradeSub');
      if (el) {
        const items = ANCHOR_ASSETS.filter(a => a.bias !== 'WATCH').slice(0, 6);
        el.innerHTML = items.map(a => {
          const cls = a.bias === 'BUY' ? 'buy' : 'sell';
          return `<a href="./trades.html" class="teaser-item">${a.symbol} <span class="teaser-ticker ${cls}">${a.bias} · ${a.conviction}</span> ${a.entry_low || a.entry}–${a.entry_high || a.target}</a>`;
        }).join('');
        if (subEl) subEl.textContent = `${ANCHOR_ASSETS.length} positions`;
      }
    }
  } catch(e) {}

  // Signal teaser
  setTimeout(() => {
    try {
      const signalCards = document.querySelectorAll('#signalGrid .signal-card');
      const el = document.getElementById('signalTeaserContent');
      const subEl = document.getElementById('teaserSignalSub');
      if (el && signalCards.length) {
        el.innerHTML = Array.from(signalCards).slice(0, 4).map(c => {
          const score = c.querySelector('.signal-score')?.textContent || '';
          const name = c.querySelector('.signal-name')?.textContent || '';
          return `<a href="./signal.html" class="teaser-item">${score} — ${name.slice(0, 60)}</a>`;
        }).join('');
        if (subEl) subEl.textContent = `${signalCards.length} signals`;
      }
    } catch(e) {}
  }, 3000);

  // Track teaser
  try {
    const trEl = document.getElementById('trackRecord');
    const el = document.getElementById('trackTeaserContent');
    const subEl = document.getElementById('teaserTrackSub');
    if (el && trEl) {
      const text = trEl.textContent || '';
      el.innerHTML = `<span class="teaser-item">${text.slice(0, 120)}</span>`;
      if (subEl) subEl.textContent = 'Performance summary';
    }
  } catch(e) {}

  // Re-apply i18n
  if (window.i18n && window.i18n.applyTranslations) window.i18n.applyTranslations();
}

// Call teasers after boot completes
if (document.querySelector('.teaser-list')) {
  setTimeout(populateTeasers, 1500);
}


// ── Delayed triangulation: retries if DOM not ready ──
function scheduleTriangulation() {
  let attempts = 0;
  function tryRender() {
    try {
      const cards = document.querySelectorAll('.card[data-story-id]');
      if (cards.length > 0) {
        renderTriangulation();
        return;
      }
      attempts++;
      if (attempts < 10) setTimeout(tryRender, 300);
    } catch(e) {
      console.warn('Triangulation error, retrying:', e);
      attempts++;
      if (attempts < 10) setTimeout(tryRender, 300);
    }
  }
  tryRender();
}

boot();
