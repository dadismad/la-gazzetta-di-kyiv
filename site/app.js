// La Gazzetta di Kyiv — Living Stories Stateful Renderer
const DATA = './data/stories.json';
const LIVING_DATA = './data/living_stories.json';
const STORY_REGISTRY_URL = './data/story_registry.json';
const POLL_INTERVAL = 120000; // 2 minutes

function byId(id) { return document.getElementById(id); }

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path, { cache: 'no-store' });
    if (!r.ok) throw new Error(String(r.status));
    return await r.json();
  } catch (e) { console.warn('Fetch:', path); return fallback; }
}

// ── ETag/If-Modified-Since support for polling ──
let _lastEtag = null;
let _lastModified = null;

async function getJSONWithConditional(path, fallback) {
  try {
    const headers = {};
    if (_lastEtag) headers['If-None-Match'] = _lastEtag;
    if (_lastModified) headers['If-Modified-Since'] = _lastModified;
    headers['Cache-Control'] = 'no-cache';

    const r = await fetch(path, { headers, cache: 'no-store' });
    if (r.status === 304) {
      // Not modified — return sentinel
      return { __notModified: true };
    }
    if (!r.ok) throw new Error(String(r.status));

    // Store response headers for next poll
    _lastEtag = r.headers.get('ETag') || _lastEtag;
    _lastModified = r.headers.get('Last-Modified') || _lastModified;

    return await r.json();
  } catch (e) {
    console.warn('Poll fetch:', path);
    return fallback;
  }
}

// ── Asset claim mapping: sector → asset prediction (fallback) ──
const SECTOR_CLAIMS = {
  geopolitics: { asset: 'Brent Crude', symbol: 'BZ=F', target: '78.00', change: '+2.1%' },
  markets:     { asset: 'Dollar Index', symbol: 'DXY', target: '103.80', change: '-0.5%' },
  tech:        { asset: 'NVIDIA', symbol: 'NVDA', target: '1,190', change: '+3.2%' },
  wealth:      { asset: 'Bitcoin', symbol: 'BTC', target: '69,200', change: '+1.1%' },
  pleasure:    { asset: 'Energy Select', symbol: 'XLE', target: '94.20', change: '+1.5%' },
  default:     { asset: 'S&P 500', symbol: 'SPX', target: '5,840', change: '+0.4%' },
};

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
  wealth: 'WEALTH',
  pleasure: 'PLEASURE',
};

// ── Thesis/Pillar Filter ──
const LS_PILLAR_KEY = 'gazzetta_active_pillar';

function getActivePillar() {
  return localStorage.getItem(LS_PILLAR_KEY) || 'ALL';
}

function setActivePillar(pillar) {
  localStorage.setItem(LS_PILLAR_KEY, pillar);
}

function renderFilterBar(activePillar) {
  const bar = byId('thesisFilterBar');
  if (!bar) return;
  bar.querySelectorAll('.thesis-filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.pillar === activePillar);
  });
}

function wireFilterBar() {
  const bar = byId('thesisFilterBar');
  if (!bar) return;
  bar.addEventListener('click', function(e) {
    const btn = e.target.closest('.thesis-filter-btn');
    if (!btn) return;
    const pillar = btn.dataset.pillar;
    setActivePillar(pillar);
    renderFilterBar(pillar);
    applyFilter(pillar);
  });
}

function applyFilter(pillar) {
  document.querySelectorAll('.card[data-story-id], .card[data-expand]').forEach(card => {
    if (pillar === 'ALL') {
      card.style.display = '';
      return;
    }
    const cardPillar = card.dataset.pillar;
    card.style.display = cardPillar === pillar ? '' : 'none';
  });
}

// ── Time formatting ──
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

// ── Masthead ──
function updateMasthead() {
  const metaEl = byId('mastheadMeta');
  if (metaEl) {
    metaEl.textContent = new Date().toTimeString().slice(0,5) + ' EET';
  }
}

function updateMastheadLiving(generatedAt, nextMicroUpdate) {
  const metaEl = byId('mastheadMeta');
  if (!metaEl) return;
  const time = generatedAt ? new Date(generatedAt).toTimeString().slice(0,5) + ' EET' : new Date().toTimeString().slice(0,5) + ' EET';
  const next = nextMicroUpdate ? `· next update ${new Date(nextMicroUpdate).toTimeString().slice(0,5)}` : '';
  metaEl.textContent = `${time} ${next}`;
}

// ── THE ANCHOR ──
// Static anchor: key levels persist weekly; price/regime/vol update per cycle
const ANCHOR_ASSETS = [
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
    bias: 'BUY', entry: '67,200', target: '72,000', stop: '65,500', conviction: 'LOW' },
  { symbol: '10Y', price: '4.35%', change: '+3bp', dir: 'up',
    bias: 'WATCH', entry: '4.35', target: '4.50', stop: '4.15', conviction: 'LOW' },
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
  const bbBody = byId('bbSheetBody');
  if (bbBody) bbBody.innerHTML = ANCHOR_ASSETS.map(anchorRowHTML).join('') + cryptoSignalHTML();
  renderPDR('pdrGauge');
  renderPDR('pdrGaugeMobile');
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

// ── Living Stories ──
// Stateful store: keyed by story_id → DOM element
let currentStories = {};
let storyRegistry = null;

// Status dot CSS class
function statusDotClass(status) {
  if (status === 'evolving') return 'story-status-dot gold pulse';
  if (status === 'stable') return 'story-status-dot sky';
  return 'story-status-dot grey'; // resolved or unknown
}

// Asset claim HTML from living story data
function assetClaimHTML(claim) {
  if (!claim) return '';
  const changeClass = claim.change_pct >= 0 ? 'up' : 'down';
  const deltaStr = `${claim.initial || ''}→${claim.current || ''}`;
  return `
    <span class="asset-claim" data-ticker="${claim.ticker || ''}">
      <span class="claim-asset">${claim.ticker || claim.asset}</span>
      <span class="asset-delta monospace">${deltaStr}</span>
      <span class="asset-delta ${changeClass}">${claim.change}</span>
    </span>`;
}

// Living story card HTML
function livingCardHTML(story, isLead) {
  const sector = (story.sector || '').toLowerCase();
  const theySay = story.they_say || '';
  const reality = story.reality || '';
  const thesis = story.thesis || '';
  const photoUrl = story.image_url || pickPhoto(sector, 0);
  const status = story.status || 'stable';

  // Asset claim
  const claim = story.asset_claim;
  const claimHTML = assetClaimHTML(claim);

  // Status dot + update badge
  const dotClass = statusDotClass(status);
  const updateBadge = story.update_count > 0
    ? `<span class="story-update-badge">+${story.update_count} updates</span>`
    : '';
  const updatedAgo = story.last_updated
    ? `<span class="updated-ago">${formatTimeAgo(story.last_updated)}</span>`
    : '';

  // Thread preview pills (sub-stories collapsed by default — guardrail)
  const threadHTML = story.thread_previews && story.thread_previews.length > 1
    ? `<div class="thread-nav" style="display:none">
        ${story.thread_previews.map((t, i) =>
          `<span class="thread-pill${i === 0 ? ' active' : ''}" data-thread-id="${t.thread_id}">${t.headline} (${t.update_count})</span>`
        ).join('')}
      </div>`
    : '';

  // Resolved banner
  const resolvedBanner = status === 'resolved'
    ? `<div class="resolved-banner"><span class="resolved-icon">✓</span><span>Resolved</span></div>`
    : '';

  return `
    <article class="card${isLead ? ' lead' : ''}"
             data-story-id="${story.story_id}"
             data-status="${status}"
             data-update-count="${story.update_count}"
             data-last-updated="${story.last_updated || ''}"
             data-pillar="${story.paradigm_pillar || ''}">
      <div class="card-collapsed" onclick="this.parentElement.classList.toggle('expanded')">
        <div class="card-head">
          ${claimHTML}
          ${sector ? `<span class="category-tag ${sector}">${SECTOR_LABELS[sector] || sector}</span>` : ''}
          <h3>${story.headline}</h3>
        </div>
        <span class="expand-hint">▾</span>
      </div>
      <div class="card-expanded-body">
        ${reality ? `<p class="summary">${reality}</p>` : ''}
        ${theySay || reality ? `
        <div class="detail">
          ${theySay ? `<div class="con-they"><span class="con-label">They say</span>${theySay}</div>` : ''}
          ${reality ? `<div class="con-real"><span class="con-label">Reality</span>${reality}</div>` : ''}
        </div>` : ''}
        ${story.capital_flow ? `
        <div class="capital-flow-block">
          <span class="cf-label">CAPITAL FLOW</span>
          ${story.capital_flow}
        </div>` : ''}
        ${story.portfolio_implication ? `
        <div class="the-play">
          <span class="pi-label">THE PLAY</span>
          <span class="pi-text">${story.portfolio_implication}</span>
        </div>` : ''}
        <div class="card-photo">
          <img src="${photoUrl}" alt="${sector}" loading="lazy" onerror="this.parentElement.style.display='none'">
        </div>
      </div>
      <div class="story-evolution-timeline" style="display:none">
        <div class="timeline-loading">Loading evolution timeline...</div>
      </div>
      ${threadHTML}
      ${resolvedBanner}
    </article>`;
}

// ── Stateful DOM patching ──
function patchStoryCard(card, story) {
  if (!card) return;

  // Update data attributes
  card.dataset.status = story.status || 'stable';
  card.dataset.updateCount = String(story.update_count || 0);
  card.dataset.lastUpdated = story.last_updated || '';

  // Update status dot
  const dot = card.querySelector('.story-status-dot');
  if (dot) {
    const newClass = statusDotClass(story.status);
    dot.className = newClass;
  }

  // Update update badge — if count changed, animate briefly
  const badge = card.querySelector('.story-update-badge');
  if (badge) {
    const oldCount = parseInt(badge.textContent.replace(/[^0-9]/g, ''), 10) || 0;
    const newCount = story.update_count || 0;
    if (newCount !== oldCount) {
      card.classList.add('recently-updated');
      setTimeout(() => card.classList.remove('recently-updated'), 3000);
    }
    badge.textContent = `+${newCount} updates`;
  }

  // Update "updated ago" timestamp
  const ago = card.querySelector('.updated-ago');
  if (ago && story.last_updated) {
    ago.textContent = formatTimeAgo(story.last_updated);
  }

  // Update headline — but original headline is LOCKED (guardrail)
  const headlineEl = card.querySelector('h3');
  if (headlineEl) {
    const originalHeadline = headlineEl.dataset.original || '';
    // If there's an original headline stored, never overwrite it
    // Only update if no original is stored (first-time set)
    if (!originalHeadline) {
      headlineEl.dataset.original = story.headline;
      headlineEl.textContent = story.headline;
    }
    // Update the current_headline display only if it's content evolution,
    // but the original is preserved in data-original
  }

  // Update summary (reality text)
  const summary = card.querySelector('.summary');
  if (summary && story.reality) {
    summary.textContent = story.reality;
  }

  // Update they_say / reality in detail
  const conThey = card.querySelector('.con-they');
  if (conThey && story.they_say) {
    conThey.innerHTML = `<span class="con-label">They say</span>${story.they_say}`;
  }
  const conReal = card.querySelector('.con-real');
  if (conReal && story.reality) {
    conReal.innerHTML = `<span class="con-label">Reality</span>${story.reality}`;
  }

  // Update portfolio implication → THE PLAY
  if (story.portfolio_implication) {
    const piEl = card.querySelector('.the-play, .portfolio-implication');
    if (piEl) {
      const textEl = piEl.querySelector('.pi-text');
      if (textEl) textEl.textContent = story.portfolio_implication;
      const labelEl = piEl.querySelector('.pi-label');
      if (labelEl) labelEl.textContent = 'THE PLAY';
    } else {
      // Insert new THE PLAY block after detail section
      const detailEl = card.querySelector('.detail');
      const piHTML = `
        <div class="the-play">
          <span class="pi-label">THE PLAY</span>
          <span class="pi-text">${story.portfolio_implication}</span>
        </div>`;
      if (detailEl) {
        detailEl.insertAdjacentHTML('afterend', piHTML);
      } else {
        const cardText = card.querySelector('.card-text');
        if (cardText) cardText.insertAdjacentHTML('beforeend', piHTML);
      }
    }
  }

  // Update asset claim
  if (story.asset_claim) {
    const claimEl = card.querySelector('.asset-claim');
    if (claimEl) {
      const claim = story.asset_claim;
      const changeClass = claim.change_pct >= 0 ? 'up' : 'down';
      const deltaHTML = `
        <span class="claim-asset">${claim.ticker || claim.asset}</span>
        <span class="asset-delta monospace">${claim.initial||''}→${claim.current||''}</span>
        <span class="asset-delta ${changeClass}">${claim.change}</span>
        <span class="claim-sep">|</span>
        <span class="asset-delta">narrative-driven ${claim.narrative_driven_pct}%</span>`;
      claimEl.innerHTML = deltaHTML;
      claimEl.dataset.ticker = claim.ticker || '';
    }
  }

  // Flash card if updated recently (within 10 min)
  if (story.last_updated && Date.now() - new Date(story.last_updated).getTime() < 600000) {
    if (!card.classList.contains('recently-updated')) {
      card.classList.add('recently-updated');
      setTimeout(() => card.classList.remove('recently-updated'), 3000);
    }
  }
}

function appendStoryCard(story, isLead) {
  const el = byId('newsCol');
  if (!el) return;
  const html = livingCardHTML(story, isLead);
  // Insert lead at top, other stories before archived
  if (isLead) {
    el.insertAdjacentHTML('afterbegin', html);
  } else {
    // Find where archived stories begin or append to end
    const archivedMarker = el.querySelector('.archived-header');
    if (archivedMarker) {
      archivedMarker.insertAdjacentHTML('beforebegin', html);
    } else {
      el.insertAdjacentHTML('beforeend', html);
    }
  }
  // Wire click handler on new card
  const newCard = el.querySelector(`[data-story-id="${story.story_id}"]`);
  if (newCard) wireCardClick(newCard);
}

// ── Timeline detail view ──
function wireCardClick(card) {
  card.addEventListener('click', async function(e) {
    // Don't toggle if clicking a thread pill
    if (e.target.closest('.thread-pill')) return;
    // Don't toggle if clicking a resolved banner link
    if (e.target.closest('.resolved-archive-link')) return;

    const storyId = this.dataset.storyId;
    const timelineEl = this.querySelector('.story-evolution-timeline');
    if (!timelineEl) return;

    const wasExpanded = this.classList.contains('expanded');

    // Close all other expanded cards
    document.querySelectorAll('.card.expanded').forEach(c => {
      if (c !== this) c.classList.remove('expanded');
    });

    if (wasExpanded) {
      // Collapse
      this.classList.remove('expanded');
      // Don't hide timeline immediately — let CSS transition
      return;
    }

    // Expand this card
    this.classList.add('expanded');

    // Lazy-load timeline if not loaded yet
    if (!timelineEl.dataset.loaded) {
      timelineEl.style.display = 'block';
      timelineEl.innerHTML = '<div class="timeline-loading">Loading evolution timeline...</div>';

      try {
        const timelineData = await getJSON(`./data/stories/${storyId}/timeline.json`, null);
        if (timelineData && timelineData.threads) {
          timelineEl.innerHTML = timelineHTML(timelineData, timelineData.threads[0]?.thread_id);
          timelineEl.dataset.loaded = 'true';
          // Wire thread switching
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
      // Already loaded — just show
      timelineEl.style.display = 'block';
    }
  });
}

function timelineHTML(timelineData, activeThreadId) {
  // Find the active thread
  const thread = timelineData.threads?.find(t => t.thread_id === activeThreadId)
    || timelineData.threads?.[0];
  if (!thread) return '<div class="timeline-empty">No thread data.</div>';

  const threadNav = timelineData.threads && timelineData.threads.length > 1
    ? `<div class="thread-nav">
        ${timelineData.threads.map(t =>
          `<span class="thread-pill${t.thread_id === activeThreadId ? ' active' : ''}" data-thread-id="${t.thread_id}">${t.type === 'main' ? 'Main' : t.current_state?.headline?.slice(0,30) || t.thread_id.slice(0,25)} (${t.evolution?.length || 0})</span>`
        ).join('')}
      </div>`
    : '';

  const entries = (thread.evolution || []).map((ev, i) => {
    const isLatest = i === thread.evolution.length - 1;
    const dotClass = ev.type === 'frame_shift' || ev.type === 'thread_creation'
      ? (isLatest ? 'timeline-dot gold pulse' : 'timeline-dot gold')
      : (isLatest ? 'timeline-dot gold pulse' : 'timeline-dot');
    const typeLabel = ev.type.replace(/_/g, ' ');
    const sourceStr = ev.source_count ? ` · ${ev.source_count} sources` : '';
    const assetStr = ev.asset_projection
      ? `<div class="timeline-asset">
          <span class="asset-delta monospace">${ev.asset_projection.ticker || ''} ${ev.asset_projection.initial || ''}→${ev.asset_projection.current || ''}</span>
          <span class="asset-delta ${(ev.asset_projection.change_pct || 0) >= 0 ? 'up' : 'down'}">${ev.asset_projection.change || ''}</span>
          <span class="asset-delta">| ${ev.asset_projection.narrative_driven_pct || 0}% narrative-driven</span>
        </div>`
      : '';

    return `
      <div class="update-entry" data-type="${ev.type}"${isLatest ? ' data-latest="true"' : ''}>
        <span class="${dotClass}"></span>
        <div class="timeline-content">
          <span class="update-timestamp">${formatTimestamp(ev.timestamp)}</span>
          <span class="update-type-badge">${typeLabel}</span>
          <p class="update-delta">${ev.reality_delta || ''}</p>
          ${assetStr}
          ${ev.sub_thread_spawned ? `<span class="update-spawn">→ Sub-thread spawned</span>` : ''}
        </div>
      </div>`;
  }).join('');

  return `
    ${threadNav}
    <div class="timeline-entries">
      ${entries}
    </div>
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
      // Update active state
      timelineEl.querySelectorAll('.thread-pill').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      // Re-render timeline for this thread
      const entriesContainer = timelineEl.querySelector('.timeline-entries');
      const stateContainer = timelineEl.querySelector('.timeline-state');
      if (entriesContainer && stateContainer) {
        const thread = timelineData.threads.find(t => t.thread_id === threadId);
        if (thread) {
          // Replace entries with new thread data
          const navHtml = timelineData.threads.map(t =>
            `<span class="thread-pill${t.thread_id === threadId ? ' active' : ''}" data-thread-id="${t.thread_id}">${t.type === 'main' ? 'Main' : t.current_state?.headline?.slice(0,30) || t.thread_id.slice(0,25)} (${t.evolution?.length || 0})</span>`
          ).join('');
          timelineEl.querySelector('.thread-nav').innerHTML = navHtml;

          const entries = (thread.evolution || []).map((ev, i) => {
            const isLatest = i === thread.evolution.length - 1;
            const dotClass = ev.type === 'frame_shift' || ev.type === 'thread_creation'
              ? (isLatest ? 'timeline-dot gold pulse' : 'timeline-dot gold')
              : (isLatest ? 'timeline-dot gold pulse' : 'timeline-dot');
            const typeLabel = ev.type.replace(/_/g, ' ');
            const assetStr = ev.asset_projection
              ? `<div class="timeline-asset">
                  <span class="asset-delta monospace">${ev.asset_projection.ticker || ''} ${ev.asset_projection.initial || ''}→${ev.asset_projection.current || ''}</span>
                  <span class="asset-delta ${(ev.asset_projection.change_pct || 0) >= 0 ? 'up' : 'down'}">${ev.asset_projection.change || ''}</span>
                  <span class="asset-delta">| ${ev.asset_projection.narrative_driven_pct || 0}% narrative-driven</span>
                </div>`
              : '';

            return `
              <div class="update-entry" data-type="${ev.type}"${isLatest ? ' data-latest="true"' : ''}>
                <span class="${dotClass}"></span>
                <div class="timeline-content">
                  <span class="update-timestamp">${formatTimestamp(ev.timestamp)}</span>
                  <span class="update-type-badge">${typeLabel}</span>
                  <p class="update-delta">${ev.reality_delta || ''}</p>
                  ${assetStr}
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

          // Re-wire thread navigation for the new pills
          wireThreadNavigation(timelineEl, timelineData, storyId);
        }
      }
    });
  });
}

// ── Polling ──
async function pollLivingStories() {
  const data = await getJSONWithConditional(LIVING_DATA, null);
  if (!data) return;
  // If not modified, just update timestamps
  if (data.__notModified) {
    updateTimestamps();
    return;
  }

  // 1. Update masthead with cycle info
  updateMastheadLiving(data.generated_at, data.next_micro_update);

  // 2. Build list of all stories
  const allStories = [data.lead, ...(data.stories || []), ...(data.archived_stories || [])];

  // 3. Track which IDs we've seen
  const seenIds = new Set();

  allStories.forEach(story => {
    seenIds.add(story.story_id);
    const card = document.querySelector(`[data-story-id="${story.story_id}"]`);
    if (card) {
      // Patch existing card
      patchStoryCard(card, story);
    } else {
      // New story — append
      appendStoryCard(story, story === data.lead);
    }
  });

  // 4. Remove cards for stories no longer in the data
  document.querySelectorAll('.card[data-story-id]').forEach(card => {
    if (!seenIds.has(card.dataset.storyId)) {
      card.style.opacity = '0';
      card.style.transition = 'opacity 0.5s';
      setTimeout(() => card.remove(), 500);
    }
  });

  // 5. Update asset projections
  if (data.lead?.asset_claim) {
    patchAssetProjection(data.lead.asset_claim);
  }

  // 6. Update timestamps
  updateTimestamps();

  // 7. Re-apply active filter to any new cards
  const activePillar = getActivePillar();
  if (activePillar !== 'ALL') applyFilter(activePillar);
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

function patchAssetProjection(claim) {
  // Update the Bet&Benefit panel with the lead story's asset claim
  if (!claim) return;
  const el = byId('assetList');
  if (!el) return;
  const row = el.querySelector(`[data-ticker="${claim.ticker}"]`) || el.querySelector('.asset-row');
  // Update the relevant asset row if we can find it
  el.querySelectorAll('.asset-row').forEach(row => {
    const symbol = row.querySelector('.asset-symbol');
    if (symbol && symbol.textContent === claim.ticker) {
      const price = row.querySelector('.asset-price');
      const change = row.querySelector('.asset-change');
      if (price) price.textContent = `$${claim.current}`;
      if (change) {
        change.textContent = claim.change;
        change.className = `asset-change ${(claim.change_pct || 0) >= 0 ? 'up' : 'down'}`;
      }
    }
  });
}

// ── Legacy card render (fallback) ──
function cardHTML(story, idx, isLead) {
  const sector = (story.sector || '').toLowerCase();
  const theySay = story.they_say || '';
  const reality = story.reality || '';
  const photoUrl = story.image_url || pickPhoto(sector, idx);

  const claim = SECTOR_CLAIMS[sector] || SECTOR_CLAIMS.default;
  const claimHTML = `
    <span class="asset-claim" title="${claim.symbol} projected target">
      <span class="claim-asset">${claim.asset}</span>
      <span class="claim-arrow">→</span>
      <span class="claim-target">$${claim.target}</span>
      <span class="claim-change up">${claim.change}</span>
    </span>`;

  return `
    <article class="card${isLead ? ' lead' : ''}" data-expand="true" data-pillar="${story.paradigm_pillar || ''}">
      <div class="card-body">
        <div class="card-text">
          ${claimHTML}
          <div class="card-head">
            ${sector ? `<span class="category-tag ${sector}">${SECTOR_LABELS[sector] || sector}</span>` : ''}
            <h3>${story.headline}</h3>
          </div>
          ${reality ? `<p class="summary">${reality}</p>` : ''}
          ${theySay || reality ? `
          <div class="detail">
            ${theySay ? `<div class="con-they"><span class="con-label">They say</span>${theySay}</div>` : ''}
            ${reality ? `<div class="con-real"><span class="con-label">Reality</span>${reality}</div>` : ''}
          </div>` : ''}
          ${story.portfolio_implication ? `
          <div class="the-play">
            <span class="pi-label">THE PLAY</span>
            <span class="pi-text">${story.portfolio_implication}</span>
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
  // Try living stories first
  const livingData = await getJSON(LIVING_DATA, null);
  const regData = await getJSON(STORY_REGISTRY_URL, null);
  if (regData) storyRegistry = regData;

  // Wire filter bar early so it's ready
  wireFilterBar();
  const savedPillar = getActivePillar();
  renderFilterBar(savedPillar);

  if (livingData && livingData.lead) {
    // Render with living stories format
    const all = [livingData.lead, ...(livingData.stories || []), ...(livingData.archived_stories || [])];
    const el = byId('newsCol');
    if (el) el.innerHTML = all.map((s, i) => livingCardHTML(s, i === 0)).join('');

    updateMastheadLiving(livingData.generated_at, livingData.next_micro_update);
    renderAnchor();
    wireBBToggle();

    // Wire click handlers for living story cards
    document.querySelectorAll('.card[data-story-id]').forEach(card => wireCardClick(card));

    // Apply saved filter
    applyFilter(savedPillar);

    // Start polling (2 min interval)
    setInterval(pollLivingStories, POLL_INTERVAL);
    return;
  }

  // Fallback: legacy stories.json
  const data = await getJSON(DATA, null);
  if (!data || !data.lead) {
    const el = byId('newsCol');
    if (el) el.innerHTML = '<p style="text-align:center;color:var(--ink-muted);padding:40px;font-style:italic">Intelligence update in progress.</p>';
    renderAnchor();
    wireBBToggle();
    return;
  }

  const all = [data.lead, ...(data.stories || [])];
  const el = byId('newsCol');
  if (el) el.innerHTML = all.map((s, i) => cardHTML(s, i, i === 0)).join('');

  // Apply saved filter after rendering legacy cards
  applyFilter(savedPillar);

  updateMasthead();
  renderAnchor();
  wireExpand();
  wireBBToggle();
}

boot();
