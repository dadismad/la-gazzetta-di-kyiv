function el(id){ return document.getElementById(id); }

let STATE = {
  regime: null,
  setups: [],
  divergences: [],
  contradictions: [],
  narrativeReviews: []
};

async function fetchJSON(path, fallback){
  try{
    const r = await fetch(path, {cache:'no-store'});
    if(!r.ok) throw new Error(`${path} ${r.status}`);
    return await r.json();
  }catch(e){
    console.warn('fetch failed', path, e.message);
    return fallback;
  }
}

function capitalize(str){
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function renderNarratives(){
  const reviews = STATE.narrativeReviews;
  const setups = STATE.setups;
  const target = el('narrativesList');

  if(!reviews.length && !setups.length){
    target.innerHTML = '<p style="color:var(--ink-muted)">No narrative data available yet.</p>';
    return;
  }

  const items = reviews.slice(0, 6);
  target.innerHTML = items.map((item, i) => {
    const setup = setups.find(s => s.title && s.title.toLowerCase().includes(item.topic));
    const thesis = setup ? setup.thesis : 'Second-order effects underpriced by consensus';
    const horizon = setup ? setup.horizon : '3d';
    const confidence = setup ? Math.round(setup.confidence * 100) + '%' : 'n/a';

    return `<article class="narrative-card">
      <div class="card-category">${capitalize(item.topic)}</div>
      <h3 class="card-headline">${item.review.split('.')[0]}.</h3>
      <p class="card-body">${thesis}. Mentions: ${item.mentions_24h} in 24h. Intensity: ${item.intensity_score}/100. Momentum: ${item.momentum}.</p>
      <div class="card-meta">
        <span><span class="meta-label">Context:</span><span class="meta-value">Intensity ${item.intensity_score}/100, ${item.momentum} momentum.</span></span>
        <span><span class="meta-label">Action:</span><span class="meta-value">Monitor ${item.topic} with ${horizon} horizon.</span></span>
      </div>
    </article>`;
  }).join('');
}

function renderSidebar(){
  const reviews = STATE.narrativeReviews;
  const regime = STATE.regime || {};
  const topNarrative = reviews[0] || {};
  const setups = STATE.setups;
  const divergences = STATE.divergences;

  // Narrative Focus panel
  const focusTarget = el('narrativeFocus');
  const topSetup = setups[0];
  focusTarget.innerHTML = `<div class="sidebar-section">
    <div class="sidebar-title">Narrative Focus</div>
    <div class="sidebar-category">${capitalize(topNarrative.topic || 'Macro')}</div>
    <h3 class="sidebar-headline">${topNarrative.review ? topNarrative.review.split('.')[0] + '.' : 'Pending update.'}</h3>
    <p class="sidebar-body">${topNarrative.review || 'Awaiting narrative data cycle.'}</p>
  </div>`;

  // Crucial Details panel
  const detailsTarget = el('crucialDetails');
  const topItems = divergences.slice(0, 4);
  detailsTarget.innerHTML = `<div class="sidebar-section">
    <div class="sidebar-title">Crucial Details</div>
    <ul class="detail-list">
      ${topItems.map(d => `<li>${capitalize(d.narrative)}: Market believes "${d.market_belief}" but ${d.observed_reality.toLowerCase()}. Divergence: ${d.divergence_score}.</li>`).join('')}
      <li>Regime: ${regime.regime_label || 'Pending'}. Risk state: ${regime.risk_state || 'n/a'}. Confidence: ${Math.round((regime.confidence || 0) * 100)}%.</li>
    </ul>
  </div>`;

  // What to Watch Next panel
  const watchTarget = el('watchNext');
  const watchItems = reviews.slice(1, 5);
  watchTarget.innerHTML = `<div class="sidebar-section">
    <div class="sidebar-title">What to Watch Next</div>
    <ul class="watch-list">
      ${watchItems.map(w => `<li>${capitalize(w.topic)}: ${w.mentions_24h} mentions, ${w.momentum} momentum. Monitor for position-relevant shifts.</li>`).join('')}
    </ul>
  </div>`;
}

async function boot(){
  const [regime, setups, divergences, narratives] = await Promise.all([
    fetchJSON('./api/v1/home/regime.json', {}),
    fetchJSON('./api/v1/home/setups.json', {items:[]}),
    fetchJSON('./api/v1/home/divergences.json', {items:[]}),
    fetchJSON('./data/narratives.json', {narrative_reviews:[]})
  ]);

  STATE.regime = regime;
  STATE.setups = setups.items || [];
  STATE.divergences = divergences.items || [];
  STATE.narrativeReviews = narratives.narrative_reviews || [];

  renderNarratives();
  renderSidebar();
}

boot();
