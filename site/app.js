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
  if(!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatTopic(topic){
  if(!topic) return '';
  return topic.length <= 3 ? topic.toUpperCase() : capitalize(topic);
}

function ensurePeriod(text){
  if(!text) return '';
  const trimmed = text.trim();
  return trimmed.endsWith('.') ? trimmed : `${trimmed}.`;
}

function topicFromSetup(setup){
  if(!setup || !setup.title) return '';
  const parts = setup.title.split(':');
  const topic = parts.length > 1 ? parts[1] : setup.title;
  return topic.trim().toLowerCase();
}

function confidenceLabel(confidence){
  if(confidence >= 0.75) return 'High';
  if(confidence >= 0.6) return 'Medium';
  return 'Low';
}

function repricingRange(momentum){
  if(momentum === 'high') return '+8–12%';
  if(momentum === 'medium') return '+5–9%';
  return '+3–6%';
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
  target.innerHTML = items.map((item) => {
    const setup = setups.find(s => s.title && s.title.toLowerCase().includes(item.topic));
    const divergence = STATE.divergences.find(d => d.narrative === item.topic);
    const headline = setup ? `${formatTopic(item.topic)} narrative acceleration` : formatTopic(item.topic);
    const thesis = ensurePeriod(setup ? setup.thesis : 'Second-order effects remain underpriced by consensus');
    const contradiction = ensurePeriod(
      divergence
        ? `Consensus expects ${divergence.market_belief.toLowerCase()}, yet ${divergence.observed_reality.toLowerCase()}`
        : 'Consensus expects continuity, yet signal drift keeps downside branches open'
    );
    const interpretation = item.review && item.review.includes('Interpretation:')
      ? item.review.split('Interpretation:')[1].trim()
      : item.review;
    const strategic = ensurePeriod(interpretation || 'Strategic attention remains warranted across desks');
    const positioning = ensurePeriod(
      setup && setup.retail_execution && setup.retail_execution.length
        ? setup.retail_execution[0]
        : 'Positioning favors liquid, defined-risk exposure until momentum resolves'
    );

    return `<article class="narrative-card">
      <h3 class="card-headline">${headline}</h3>
      <p class="card-line">${thesis}</p>
      <p class="card-line">${contradiction}</p>
      <p class="card-line">${strategic}</p>
      <p class="card-line">${positioning}</p>
    </article>`;
  }).join('');
}

function renderSidebar(){
  const reviews = STATE.narrativeReviews;
  const setups = STATE.setups;
  const divergences = STATE.divergences;

  const influenceMap = {
    ai: ['US AI policy teams', 'chipmakers', 'cloud platforms', 'venture funds'],
    eu: ['European Commission', 'ECB', 'NATO liaisons', 'energy ministries'],
    china: ['State Council', 'SOEs', 'tech champions', 'sovereign funds'],
    election: ['incumbent blocs', 'donor networks', 'media coalitions', 'policy advisors'],
    gas: ['producer states', 'utility buyers', 'shipping firms', 'state energy traders'],
    oil: ['OPEC+ core', 'shale producers', 'refiners', 'sovereign funds'],
    inflation: ['central banks', 'labor groups', 'consumer staples', 'treasury desks'],
    rates: ['central banks', 'primary dealers', 'mortgage desks', 'pension funds'],
    russia: ['security councils', 'energy majors', 'sanctions offices', 'defense primes'],
    crypto: ['exchanges', 'stablecoin issuers', 'market makers', 'regulators'],
    drone: ['defense ministries', 'aerospace primes', 'ISR contractors', 'border agencies'],
    nato: ['member states', 'defense ministries', 'logistics commands', 'arms suppliers']
  };

  const stakesMap = {
    ai: 'Semis, data-center capex, and grid demand are repricing on a shorter fuse.',
    eu: 'Rates, energy imports, and defense procurement are pulling capital toward core Europe.',
    china: 'Export chains, industrial metals, and EM FX risk skew to policy cadence.',
    election: 'Domestic fiscal paths and regulatory outlooks are driving front-end volatility.',
    gas: 'Utility balance sheets and storage economics face asymmetric winter pressure.',
    oil: 'Refining margins and shipping insurance remain sensitive to policy shocks.',
    inflation: 'Consumer staples margins and duration assets are most exposed to prints.',
    rates: 'Duration sensitivity and mortgage convexity remain the primary fault lines.',
    russia: 'Energy corridors and sanctions enforcement remain the pressure points.',
    crypto: 'Liquidity conditions and regulatory headlines set the near-term range.',
    drone: 'Defense procurement and ISR budgets are in a re-rating window.',
    nato: 'Defense supply chains and sovereign budgets anchor the repricing.'
  };

  const tickerMap = {
    ai: 'NVDA',
    eu: 'EZU',
    china: 'FXI',
    election: 'SPY',
    gas: 'UNG',
    oil: 'XLE',
    inflation: 'TIP',
    rates: 'TLT',
    russia: 'RSX',
    crypto: 'BTC',
    drone: 'ITA',
    nato: 'ITA'
  };

  const influenceTarget = el('spectreOfInfluence');
  const influenceTopics = reviews.slice(0, 4).map(r => r.topic);
  const influenceItems = influenceTopics.map(topic => {
    const actors = influenceMap[topic] || ['state actors', 'institutional capital', 'strategic corporates', 'policy offices'];
    return `<li><span class="item-topic">${formatTopic(topic)}</span> — ${actors.join(', ')}.</li>`;
  }).join('');
  influenceTarget.innerHTML = `<div class="sidebar-section">
    <div class="sidebar-title">Spectre of Influence</div>
    <ul class="sidebar-list">
      ${influenceItems || '<li>Influence map pending data refresh.</li>'}
    </ul>
  </div>`;

  const stakesTarget = el('stakesInPlay');
  const stakesItems = divergences.slice(0, 3).map(d => {
    const stake = stakesMap[d.narrative] || 'Cross-asset sensitivity is rising with uneven liquidity.';
    return `<li><span class="item-topic">${formatTopic(d.narrative)}</span> — ${stake}</li>`;
  }).join('');
  stakesTarget.innerHTML = `<div class="sidebar-section">
    <div class="sidebar-title">Stakes in Play</div>
    <ul class="sidebar-list">
      ${stakesItems || '<li>Stake assessment pending data refresh.</li>'}
    </ul>
  </div>`;

  const betTarget = el('betAndBenefit');
  const betItems = setups.slice(0, 3).map(setup => {
    const topic = topicFromSetup(setup);
    const review = reviews.find(r => r.topic === topic) || {};
    const ticker = tickerMap[topic] || formatTopic(topic) || 'GLOBAL';
    const probability = setup && setup.probability_base ? `${setup.probability_base}%` : `${Math.round((setup.confidence || 0.6) * 100)}%`;
    const range = repricingRange(review.momentum);
    const confidence = confidenceLabel(setup.confidence || 0);
    return `<div class="bet-card">
      <div class="bet-ticker">${ticker}</div>
      <div class="bet-meta">
        <span>Probability: ${probability}</span>
        <span>Projected repricing: ${range}</span>
        <span>Confidence: ${confidence}</span>
      </div>
    </div>`;
  }).join('');
  betTarget.innerHTML = `<div class="sidebar-section">
    <div class="sidebar-title">Bet & Benefit</div>
    ${betItems || '<div class="bet-card"><div class="bet-ticker">Awaiting setup feed</div></div>'}
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
