// La Gazzetta di Kyiv v20.5 — Hero · Severity badges · Contradiction Score
const DATA = './data/stories.json';
const LIVING_DATA = './data/living_stories.json';
const POLL_INTERVAL = 120000; // 2 minutes

function byId(id) { return document.getElementById(id); }

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch (e) { console.warn('Fetch:', path, e); return fallback; }
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
  geopolitics: 'GEOPOLITICS',
  markets: 'MARKETS',
  tech: 'TECH',
  macro: 'MACRO',
  wealth: 'WEALTH',
  pleasure: 'PLEASURE',
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
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function formatTimestamp(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  const time = d.toTimeString().slice(0, 5);
  if (isToday) return `${time} · Today`;
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

const ANCHOR_ASSETS = [
  // Traditional finance (7)
  { symbol: 'SPX', price: '5,840', change: '+0.4%', dir: 'up',
    bias: 'BUY', entry: '5,750', target: '5,950', stop: '5,680', conviction: 'HIGH' },
  { symbol: 'NVDA', price: '1,142', change: '+3.2%', dir: 'up',
    bias: 'BUY', entry: '1,100', target: '1,240', stop: '1,070', conviction: 'HIGH' },
  { symbol: 'BRENT', price: '74.20', change: '+2.1%', dir: 'up',
    bias: 'BUY', entry: '72.00', target: '78.00', stop: '70.50', conviction: 'MED' },
  { symbol: 'DXY', price: '104.30', change: '-0.2%', dir: 'down',
    bias: 'SELL', entry: '105.20', target: '103.00', stop: '106.00', conviction: 'MED' },
  { symbol: 'GOLD', price: '2,410', change: '+0.6%', dir: 'up',
    bias: 'BUY', entry: '2,350', target: '2,500', stop: '2,320', conviction: 'HIGH' },
  { symbol: 'BTC', price: '68,450', change: '+0.9%', dir: 'up',
    bias: 'BUY', entry: '67,200', target: '72,000', stop: '65,500', conviction: 'HIGH' },
  { symbol: '10Y', price: '4.35%', change: '+3bp', dir: 'up',
    bias: 'WATCH', entry: '4.35', target: '4.50', stop: '4.15', conviction: 'LOW' },
  // Crypto (7)
  { symbol: 'ETH', price: '3,850', change: '+2.1%', dir: 'up',
    bias: 'BUY', entry: '3,600', target: '4,200', stop: '3,400', conviction: 'HIGH' },
  { symbol: 'SOL', price: '178', change: '+4.5%', dir: 'up',
    bias: 'BUY', entry: '155', target: '210', stop: '145', conviction: 'MED' },
  { symbol: 'XRP', price: '1.25', change: '+1.2%', dir: 'up',
    bias: 'WATCH', entry: '1.15', target: '1.80', stop: '1.05', conviction: 'LOW' },
  { symbol: 'BNB', price: '645', change: '+3.0%', dir: 'up',
    bias: 'BUY', entry: '580', target: '720', stop: '550', conviction: 'MED' },
  { symbol: 'ADA', price: '0.92', change: '-1.8%', dir: 'down',
    bias: 'SELL', entry: '1.05', target: '1.25', stop: '1.10', conviction: 'HIGH' },
  { symbol: 'DOGE', price: '0.28', change: '+5.2%', dir: 'up',
    bias: 'WATCH', entry: '0.25', target: '0.35', stop: '0.22', conviction: 'LOW' },
];

const ANCHOR_CRYPTO = {
  stablecoinSupply: { value: '$172B', delta: '+$4.2B', label: 'Stablecoin Supply (30d)' },
  exchangeNetflow: { value: '-$890M', delta: '7d outflow', label: 'Exchange Netflow' },
  fundingRate: { value: '-0.01%', regime: 'neutral', label: 'Aggregate Funding' },
};

const ANCHOR_PDR = { value: '1.7', regime: 'passive', regimeLabel: 'Passive Discovery', trend: '▁▃▅▆▇' };

function anchorRowHTML(a) {
  const pillClass = a.bias === 'BUY' ? 'anchor-pill buy' : a.bias === 'SELL' ? 'anchor-pill sell' : 'anchor-pill watch';
  const badgeClass = a.conviction === 'HIGH' ? 'anchor-badge high' : a.conviction === 'MED' ? 'anchor-badge med' : 'anchor-badge low';
  return `
    <div class="asset-row">
      <div class="asset-info">
        <span class="asset-symbol">${a.symbol}</span>
        <span class="asset-price">$${a.price}</span>
        <span class="asset-change ${a.dir}">${a.change}</span>
      </div>
      <div class="asset-trade">
        <span class="${pillClass}">${a.bias}</span>
        <span class="asset-zone">${a.entry} → ${a.target}</span>
        <span class="asset-stop">Stop ${a.stop}</span>
        <span class="${badgeClass}">${a.conviction}</span>
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
}

// ═══════════════════════════════════════════════════════════════
// CAPITAL FLOWS REPORT
// ═══════════════════════════════════════════════════════════════

const CAPITAL_FLOWS_DATA = [
  { headline: '$4.2B flowing into energy ETFs', detail: 'Projected +$1.8B further inflow (70% confidence) · 2.3x normal pace', positioning: 'Institutional positioning: accumulating', direction: 'inflow', storyId: 'n21_oil__inflection_point' },
  { headline: '$6.1B flowing into tech infrastructure', detail: 'Projected +$2.3B further inflow (70% confidence) · 3.1x normal pace', positioning: 'Institutional positioning: accumulating', direction: 'inflow', storyId: 'n21_ai__data_center_backlash' },
  { headline: '$890M flowing out of European defense', detail: 'Projected -$450M further outflow (70% confidence) · 1.8x normal pace', positioning: 'Institutional positioning: hedging', direction: 'outflow', storyId: 'n21_nato__rapid_response_cuts' },
  { headline: '$340M flowing into EM Europe bonds', detail: 'Projected +$210M further inflow (70% confidence) · 1.5x normal pace', positioning: 'Institutional positioning: accumulating', direction: 'inflow', storyId: 'n21_ukraine__gulf_eu_realignment' },
  { headline: '$3.7B flowing out of EM equities', detail: 'Projected -$1.2B further outflow (70% confidence) · 2.1x normal pace', positioning: 'Institutional positioning: distributing', direction: 'outflow', storyId: 'n21_china__property_crisis_trump' },
  { headline: '$1.9B flowing into short-duration Treasuries', detail: 'Projected +$850M further inflow (70% confidence) · 1.6x normal pace', positioning: 'Institutional positioning: hedging', direction: 'inflow', storyId: 'n21_rates__fed_discounting_war' },
];

function renderCapitalFlows() {
  const el = byId('flowsList');
  if (!el) return;
  el.innerHTML = CAPITAL_FLOWS_DATA.map(f => `
    <div class="flow-item ${f.direction}" data-flow-story-id="${f.storyId}">
      <div class="flow-headline">${f.headline}</div>
      <div class="flow-detail">${f.detail}</div>
      <div class="flow-detail" style="margin-top:2px;font-size:10px;color:var(--ink-muted)">${f.positioning}</div>
    </div>
  `).join('');
  const sub = byId('cfSubtitle');
  if (sub) {
    const inflows = CAPITAL_FLOWS_DATA.filter(f => f.direction === 'inflow');
    const outflows = CAPITAL_FLOWS_DATA.filter(f => f.direction === 'outflow');
    sub.textContent = `${inflows.length} inflows · ${outflows.length} outflows`;
  }
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

  // Event strength (max 35)
  if (story.confidence === 'high') score += 15;
  if (story.they_say && story.reality) score += 10;
  if (story.extremum) score += 10;
  signals.push({label: 'Event', cls: 'event', val: 'strong'});

  // Flow alignment (max 35)
  if (flow) {
    const amt = parseFloat(flow.amount);
    const denom = flow.denomination || flow.denom || 'B';
    if (denom === 'B' && amt >= 3) score += 15;
    else if (denom === 'B' && amt >= 1) score += 10;
    else score += 5;
    const pace = parseFloat(flow.pace) || 1;
    if (pace >= 2.5) score += 10;
    else if (pace >= 1.5) score += 7;
    else score += 4;
    if (flow.positioning === 'accumulating') score += 10;
    else if (flow.positioning === 'distributing') score += 8;
    else score += 5;
    signals.push({label: 'Flow', cls: 'flow', val: `${flow.direction} $${amt}${denom} ${pace}x`});
  } else {
    signals.push({label: 'Flow', cls: 'flow', val: 'none'});
  }

  // Bet alignment (max 30)
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
  if (cappedScore >= 85) { verdict = 'MAX CONVICTION'; verdictCls = 'max'; }
  else if (cappedScore >= 70) { verdict = 'HIGH CONVICTION'; verdictCls = 'high'; }
  else if (cappedScore >= 55) { verdict = 'MODERATE'; verdictCls = 'moderate'; }
  else { verdict = 'WATCH'; verdictCls = 'watch'; }

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
    const flowItem = CAPITAL_FLOWS_DATA.find(f => f.storyId === sid);
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
    el.innerHTML = '<div style="padding:12px;color:var(--ink-muted);font-style:italic;font-size:12px">Stories loading — triangulation will appear when cards are rendered.</div>';
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
      <span class="cf-label">CAPITAL FLOW</span>
      <span class="cf-line">${cf.claim}</span>
      <span class="cf-line">Projected further flow: ${cf.projected} (${cf.confidence} confidence)</span>
      <span class="cf-line">Institutional positioning: ${cf.positioning}</span>
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
  if (cf) {
    const amt = parseFloat(cf.amount) || 0;
    const denom = (cf.denomination || '').toUpperCase();
    const pace = (cf.pace || '');
    const paceNum = parseFloat(pace.match(/^(\d+\.?\d*)x/)?.[1] || '0');
    const amountInB = denom === 'B' ? amt : denom === 'M' ? amt / 1000 : 0;
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

  // Capital flow claim (first line, bold)
  const cf = story.capital_flow;
  const cfClaim = cf ? `<div class="cf-claim">${cf.claim} — projected ${cf.projected} change at ${cf.confidence} confidence</div>` : '';

  // Sector border-left class
  const sectorClass = sector === 'geopolitics' ? 'geopolitics' : sector === 'tech' ? 'tech' : sector === 'macro' ? 'macro' : sector === 'markets' ? 'markets' : '';

  // Status dot + update badge
  const dotClass = statusDotClass(status);
  const updateBadge = story.update_count > 0
    ? `<span class="story-update-badge">+${story.update_count} updates</span>`
    : '';
  const updatedAgo = story.last_updated
    ? `<span class="updated-ago">${formatTimeAgo(story.last_updated)}</span>`
    : '';

  // Extremum line
  const extremumHTML = story.extremum ? extremumLineHTML(story.extremum) : '';

  // Severity
  const severity = determineSeverity(story);

  // Contradiction Score
  const cs = calcContradictionScore(story);

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
          ${sector ? `<span class="category-tag ${sector}">${SECTOR_LABELS[sector] || sector}</span>` : ''}
          <span class="severity ${severity}">${severity}</span>
          ${updateBadge}
          ${updatedAgo}
        </div>
        <div style="display:flex;align-items:flex-start;gap:6px">
          <h3 style="flex:1">${story.headline}</h3>
          <span class="contradiction-score">${cs}</span>
        </div>
      </div>
      </div><!-- /card-collapsed -->
      <div class="card-expanded-body">
        ${reality ? `<p class="summary">${reality}</p>` : ''}
        ${theySay || reality ? `
        <div class="detail">
          ${theySay ? `<div class="con-they"><span class="con-label">They say</span>${theySay}</div>` : ''}
          ${reality ? `<div class="con-real"><span class="con-label">Reality</span>${reality}</div>` : ''}
        </div>` : ''}
        ${capitalFlowHTML(cf)}
        ${story.portfolio_implication ? `
        <div class="the-play">
          <span class="pi-label">THE PLAY</span>
          <span class="pi-text">${story.portfolio_implication}</span>
        </div>` : ''}
        ${extremumHTML}
        <div class="share-row">
          <button class="share-toggle" title="Share this story">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg> Share
          </button>
          <div class="share-menu">
            <button class="share-btn copy-link"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg> Copy link</button>
            <button class="share-btn share-x"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4l7.5 7.5L4 19"/><path d="M20 4l-7.5 7.5L20 19"/></svg> X</button>
            <button class="share-btn share-telegram"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg> Telegram</button>
            <button class="share-btn share-linkedin"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg> LinkedIn</button>
          </div>
        </div>
        <div class="card-photo">
          <img src="${photoUrl}" alt="${sector}" loading="lazy" onerror="this.parentElement.style.display='none'">
        </div>
      </div>
      <div class="story-evolution-timeline" style="display:none">
        <div class="timeline-loading">Loading evolution timeline...</div>
      </div>
      ${story.status === 'resolved' ? `<div class="resolved-banner"><span class="resolved-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span><span>Resolved</span></div>` : ''}
    </article>`;
}

// ── Extremum Line HTML ──
function extremumLineHTML(extremumStr) {
  if (!extremumStr) return '';
  // Parse format: "WINNER: ... | LOSER: ... | IDIOT: ... | GENIUS: ..."
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
      <span class="ex-label">EXTREMUM</span>
      ${winner ? `<span class="ex-win">WINNER: ${winner}</span>` : ''}
      ${loser ? `<span class="ex-lose">LOSER: ${loser}</span>` : ''}
      ${idiot ? `<span class="ex-idiot">IDIOT: ${idiot}</span>` : ''}
      ${genius ? `<span class="ex-genius">GENIUS: ${genius}</span>` : ''}
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
      timelineEl.innerHTML = '<div class="timeline-loading">Loading evolution timeline...</div>';

      try {
        const timelineData = await getJSON(`./data/stories/${storyId}/timeline.json`, null);
        if (timelineData && timelineData.threads) {
          timelineEl.innerHTML = timelineHTML(timelineData, timelineData.threads[0]?.thread_id);
          timelineEl.dataset.loaded = 'true';
          wireThreadNavigation(timelineEl, timelineData, storyId);
        } else {
          timelineEl.innerHTML = '<div class="timeline-empty">No evolution data available yet.</div>';
          timelineEl.dataset.loaded = 'true';
        }
      } catch (err) {
        timelineEl.innerHTML = '<div class="timeline-empty">Could not load timeline.</div>';
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
        `<span class="thread-pill${t.thread_id === activeThreadId ? ' active' : ''}" data-thread-id="${t.thread_id}">${t.type === 'main' ? 'Main' : (t.current_state?.headline?.slice(0,30) || t.thread_id.slice(0,25))} (${t.evolution?.length || 0})</span>`
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

  // Update story count badge
  updateStoryCount();
}

function updateStoryCount() {
  const countEl = byId('storyCount');
  if (countEl) {
    const count = document.querySelectorAll('.card[data-story-id]').length;
    countEl.textContent = `${count} stories`;
  }
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

  // Update contradiction score
  const csEl = card.querySelector('.contradiction-score');
  if (csEl) {
    csEl.textContent = String(calcContradictionScore(story));
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
// SHARE — single toggle + inline menu
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

function closeAllShareMenus() {
  document.querySelectorAll('.share-menu.visible').forEach(m => m.classList.remove('visible'));
}

function wireShareControls() {
  // Share toggle click — open/close menu (clicking the toggle in expanded view is fine)
  document.addEventListener('click', function(e) {
    const toggle = e.target.closest('.share-toggle');
    if (toggle) {
      e.stopPropagation();
      const menu = toggle.nextElementSibling;
      if (!menu || !menu.classList.contains('share-menu')) return;
      // Close all other menus
      closeAllShareMenus();
      menu.classList.toggle('visible');
      return;
    }

    // Share menu action buttons
    const btn = e.target.closest('.share-menu .share-btn');
    if (btn) {
      e.stopPropagation();
      const card = btn.closest('.card');
      if (!card) return;
      const text = getShareText(card);
      const menu = btn.closest('.share-menu');
      menu.classList.remove('visible');

      if (btn.classList.contains('copy-link')) {
        if (navigator.share) {
          navigator.share({ title: text.split('\n')[0], text: text }).catch(() => {});
        } else if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(() => showToast('✓ Copied to clipboard')).catch(() => {
            try { document.execCommand('copy'); showToast('✓ Copied to clipboard'); } catch(e) {}
          });
        } else {
          try { document.execCommand('copy'); showToast('✓ Copied to clipboard'); } catch(e) {}
        }
      } else if (btn.classList.contains('share-x')) {
        window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(text), '_blank', 'width=600,height=400');
      } else if (btn.classList.contains('share-telegram')) {
        const url = window.location.href;
        const shareUrl = 'https://t.me/share/url?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(text.split('\n')[0]);
        window.open(shareUrl, '_blank', 'width=600,height=400');
      } else if (btn.classList.contains('share-linkedin')) {
        const url = window.location.href;
        const shareUrl = 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(url);
        window.open(shareUrl, '_blank', 'width=600,height=400');
      }
      return;
    }

    // Click outside closes all share menus
    closeAllShareMenus();
  });
}

// ═══════════════════════════════════════════════════════════════
// BOOT
// ═══════════════════════════════════════════════════════════════

async function boot() {
  // Wire collapsible containers first
  wireCollapsibleContainers();

  // Wire card click delegation (one listener on newsCol for all cards)
  wireCardDelegation();

  // Wire share toggle + menu (document-level delegation)
  wireShareControls();

  // Render static content (non-story containers)
  renderAnchor();
  renderCapitalFlows();

  // Try data sources
  const livingData = await getJSON(LIVING_DATA, null);

  if (livingData && livingData.lead) {
    // Render with living stories format
    const leadId = livingData.lead?.story_id;
    const stories = (livingData.stories || []).filter(s => s.story_id !== leadId);
    const all = [livingData.lead, ...stories, ...(livingData.archived_stories || [])].filter(Boolean);

    const el = byId('newsCol');
    if (el) {
      all.forEach((s, i) => appendStoryCard(s, i === 0));
    }

    // Triangulation AFTER cards are in DOM
    renderTriangulation();

    updateMastheadLiving(livingData.generated_at, livingData.next_micro_update);

    // Start polling
    setInterval(pollLivingStories, POLL_INTERVAL);
    updateMasthead();
    return;
  }

  // Fallback: stories.json
  const data = await getJSON(DATA, null);
  if (!data || !data.lead) {
    const el = byId('newsCol');
    if (el) el.innerHTML = '<p style="text-align:center;color:var(--ink-muted);padding:40px;font-style:italic">Intelligence update in progress.</p>';
    updateMasthead();
    return;
  }

  // Deduplicate: filter out stories matching lead story_id
  const leadId = data.lead.story_id;
  const filteredStories = (data.stories || []).filter(s => s.story_id !== leadId);
  const all = [data.lead, ...filteredStories].filter(Boolean);

  const el = byId('newsCol');
  if (el) {
    all.forEach((s, i) => appendStoryCard(s, i === 0));
  }

  // Triangulation AFTER cards are in DOM
  renderTriangulation();

  updateMasthead();
}

boot();
