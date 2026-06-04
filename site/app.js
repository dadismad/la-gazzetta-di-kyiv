// La Gazzetta di Kyiv v20 — φ-Constellation Layout · Bet & Benefit · Share Buttons · Extremum Lines
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
  // Update subtitle
  const sub = byId('cfSubtitle');
  if (sub) {
    const inflows = CAPITAL_FLOWS_DATA.filter(f => f.direction === 'inflow');
    const outflows = CAPITAL_FLOWS_DATA.filter(f => f.direction === 'outflow');
    sub.textContent = `${inflows.length} inflows · ${outflows.length} outflows`;
  }
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
            ${updateBadge}
            ${updatedAgo}
          </div>
          <h3>${story.headline}</h3>
        </div>
        <div class="card-actions">
          <div class="share-actions">
            <button class="share-btn copy-link" title="Copy link">📋</button>
            <button class="share-btn share-x" title="Share on X">𝕏</button>
            <button class="share-btn share-telegram" title="Share on Telegram">✈</button>
          </div>
          <span class="expand-hint">▾</span>
        </div>
      </div>
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
        <div class="card-photo">
          <img src="${photoUrl}" alt="${sector}" loading="lazy" onerror="this.parentElement.style.display='none'">
        </div>
        <div class="share-actions" style="margin-top:6px;opacity:0.3">
          <button class="share-btn copy-link" title="Copy link">📋 Share</button>
          <button class="share-btn share-x" title="Share on X">𝕏 Share</button>
          <button class="share-btn share-telegram" title="Share on Telegram">✈ Share</button>
        </div>
      </div>
      <div class="story-evolution-timeline" style="display:none">
        <div class="timeline-loading">Loading evolution timeline...</div>
      </div>
      ${story.status === 'resolved' ? `<div class="resolved-banner"><span class="resolved-icon">✓</span><span>Resolved</span></div>` : ''}
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
    // Skip share button clicks
    if (e.target.closest('.share-btn') || e.target.closest('.thread-pill') || e.target.closest('.resolved-archive-link')) return;

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

  // Wire click handler on new card (delegation handles expand, wire share buttons directly)
  const newCard = el.querySelector(`[data-story-id="${story.story_id}"]`);
  if (newCard) {
    wireShareButtons(newCard);
  }

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

// ═══════════════════════════════════════════════════════════════
// SHARE BUTTONS
// ═══════════════════════════════════════════════════════════════

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

function wireShareButtons(container) {
  container.querySelectorAll('.share-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      const card = this.closest('.card');
      if (!card) return;
      const text = getShareText(card);

      if (this.classList.contains('copy-link')) {
        if (navigator.share) {
          navigator.share({ title: text.split('\n')[0], text: text }).catch(() => {});
        } else if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(() => showToast('✓ Copied to clipboard')).catch(() => {
            try { document.execCommand('copy'); showToast('✓ Copied to clipboard'); } catch(e) {}
          });
        } else {
          try { document.execCommand('copy'); showToast('✓ Copied to clipboard'); } catch(e) {}
        }
      } else if (this.classList.contains('share-x')) {
        window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(text), '_blank', 'width=600,height=400');
      } else if (this.classList.contains('share-telegram')) {
        const url = window.location.href;
        const shareUrl = 'https://t.me/share/url?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(text.split('\n')[0]);
        window.open(shareUrl, '_blank', 'width=600,height=400');
      }
    });
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

  // Render static content
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

  updateMasthead();
}

boot();
