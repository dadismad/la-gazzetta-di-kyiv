function byId(id){ return document.getElementById(id); }

async function getJSON(path, fallback){
  try{
    const r = await fetch(path,{cache:'no-store'});
    if(!r.ok) throw new Error(String(r.status));
    return await r.json();
  }catch{ return fallback; }
}

function cleanTitle(t=''){ return String(t).replace('Narrative acceleration: ','').trim(); }
function short(s='', n=180){ const v=String(s||'').trim(); return v.length>n?`${v.slice(0,n-1)}…`:v; }
function ensureSentence(value=''){
  const t = String(value || '').trim();
  if(!t) return '';
  return /[.!?]$/.test(t) ? t : `${t}.`;
}

function topicFromTitle(title=''){
  const t = cleanTitle(title).toLowerCase();
  if(t.includes('oil') || t.includes('hormuz') || t.includes('crude')) return 'oil';
  if(t.includes('fed') || t.includes('rate') || t.includes('inflation')) return 'rates';
  if(t.includes('ai') || t.includes('semiconductor')) return 'ai';
  if(t.includes('china') || t.includes('ev') || t.includes('tariff')) return 'autos';
  if(t.includes('lng') || t.includes('gas')) return 'lng';
  if(t.includes('prediction') || t.includes('event market')) return 'prediction';
  return t;
}

function confidenceLabel(conf=0){
  if(conf >= 0.75) return 'High';
  if(conf >= 0.6) return 'Medium';
  if(conf >= 0.45) return 'Measured';
  return 'Low';
}

function storyBody(s, narrative, {headingTag='h3', compact=false} = {}){
  const title = cleanTitle(s?.title || 'Narrative Repricing Risk Is Back');
  const thesis = ensureSentence(s?.thesis || narrative?.semantics?.claim || 'Narrative momentum is moving faster than consensus positioning.');
  const contradiction = ensureSentence(narrative?.semantics?.contradiction || (s?.invalidation_triggers || [])[0] || 'Consensus stability hides second-order pressure points.');
  const strategy = ensureSentence(narrative?.semantics?.transmission || 'Transmission runs through policy expectations, rates sensitivity, and cross-asset positioning.');
  const limits = compact
    ? {thesis:120, contradiction:110, strategy:110}
    : {thesis:170, contradiction:150, strategy:150};
  return `
    <${headingTag}>${title}</${headingTag}>
    <p class="story-thesis">${short(thesis, limits.thesis)}</p>
    <p class="story-contradiction">${short(contradiction, limits.contradiction)}</p>
    <p class="story-strategy">${short(strategy, limits.strategy)}</p>
  `;
}

function cardBody(card, {headingTag='h3', compact=false} = {}){
  const title = short(card?.title || 'Story in Play', 90);
  const raw = String(card?.body || 'Update pending.').trim();
  const sentenceSplit = raw.match(/[^.!?]+[.!?]/g) || [raw];
  const condensed = compact ? sentenceSplit[0] : raw;
  const maxLen = compact ? 128 : 220;
  const body = short(ensureSentence(condensed), maxLen);
  return `
    <${headingTag}>${title}</${headingTag}>
    <p class="story-thesis">${body}</p>
  `;
}

function setActiveToggle(version){
  const a = byId('toggleVersionA');
  const b = byId('toggleVersionB');
  if(!a || !b) return;
  a.classList.toggle('active', version === 'version_a');
  b.classList.toggle('active', version === 'version_b');
}

function profileFromCard(card){
  const tags = card?.asset_tags || [];
  const topic = topicFromTitle(card?.title || '');
  const profiles = {
    oil: {ticker:'BZ=F', name:'Brent Crude', trigger:'Any Strait of Hormuz disruption headline', horizon:'24-72h', thesis:'Conflict headlines can quickly reprice fuel costs and inflation expectations.'},
    shipping: {ticker:'BDRY', name:'Dry Bulk Shipping', trigger:'Freight insurance or routing stress', horizon:'2-5d', thesis:'Logistics friction lifts transport costs before policy reacts.'},
    rates: {ticker:'TLT', name:'US Duration', trigger:'Fed tone hardens or CPI surprises', horizon:'1-2w', thesis:'High rates keep pressure on leveraged balance sheets and growth multiples.'},
    usd: {ticker:'DXY', name:'US Dollar Index', trigger:'Risk-off + delayed cuts', horizon:'1-2w', thesis:'Dollar strength tightens global financing conditions.'},
    semiconductors: {ticker:'SOXX', name:'Semiconductors', trigger:'AI capex guidance revisions', horizon:'1-2w', thesis:'Crowded AI leadership can amplify both upside and drawdowns.'},
    megacap_tech: {ticker:'QQQ', name:'Nasdaq 100', trigger:'Mega-cap earnings miss', horizon:'24-72h', thesis:'Concentrated index leadership means one miss can hit the whole tape.'},
    autos: {ticker:'CARZ', name:'Global Autos', trigger:'Tariff/probe announcements', horizon:'1-3w', thesis:'Auto margins now move with politics, not only demand.'},
    batteries: {ticker:'LIT', name:'Battery Supply Chain', trigger:'Trade restrictions on EV inputs', horizon:'1-3w', thesis:'Policy shocks can rewire battery winners fast.'},
    lng: {ticker:'UNG', name:'US Natural Gas', trigger:'New long-term LNG offtake deals', horizon:'1-4w', thesis:'Energy security contracts keep gas infrastructure bid.'},
    utilities: {ticker:'XLU', name:'Utilities', trigger:'Energy cost volatility spike', horizon:'1-2w', thesis:'Defensive utilities re-rate when growth confidence weakens.'},
    prediction_markets: {ticker:'COIN', name:'Platform Risk Proxy', trigger:'Regulatory enforcement headlines', horizon:'24-72h', thesis:'Compliance shocks can instantly reprice platform risk.'},
    regulatory_risk: {ticker:'XLF', name:'Regulated Financials', trigger:'Enforcement cycle broadens', horizon:'1-2w', thesis:'Regulatory uncertainty raises discount rates for platform-dependent models.'},
    default: {ticker:'SPY', name:'S&P 500', trigger:'Macro contradiction resolves', horizon:'1-2w', thesis:'Index level follows whether risk premium rises or fades.'}
  };

  const key = tags.find((t)=>profiles[t]) || (profiles[topic] ? topic : 'default');
  return profiles[key] || profiles.default;
}

function renderBetContainer(items){
  const target = byId('focusBet');
  if(!target) return;
  const picks = items.slice(0,4);
  if(!picks.length){
    target.innerHTML = '<p>Positioning watchlist pending.</p>';
    return;
  }

  const html = picks.map((card, idx)=>{
    const p = profileFromCard(card);
    const conviction = card?.confidence ? String(card.confidence).replace('_',' ') : confidenceLabel(0.55);
    return `
      <article class="bet-item">
        <div class="bet-top">
          <span class="bet-rank">#${idx+1}</span>
          <span class="bet-ticker">${p.ticker}</span>
        </div>
        <div class="bet-name">${p.name}</div>
        <div class="bet-hook">${short(card?.title || 'Story', 70)}</div>
        <div class="bet-meta"><strong>Trigger:</strong> ${p.trigger}</div>
        <div class="bet-meta"><strong>Horizon:</strong> ${p.horizon} · <strong>Conviction:</strong> ${conviction}</div>
        <div class="bet-thesis">${p.thesis}</div>
      </article>
    `;
  }).join('');

  target.innerHTML = html;
}

function renderFocus(items, lead, usingCurated, primaryReview, narrativeMap){
  const primaryTopic = primaryReview?.topic || topicFromTitle(lead?.title);
  const defaultActors = ['US administration','Iran','Federal Reserve','European Commission'];
  const influenceActors = usingCurated
    ? (lead?.actors || [])
    : (primaryReview?.semantics?.actors || []).slice(0,6);
  const actors = influenceActors.length ? influenceActors : defaultActors;

  if(byId('focusInfluence')){
    const influence = `
      <p>${short(ensureSentence(primaryReview?.semantics?.svo || primaryReview?.review || 'Power actors are forcing markets to reprice faster than public messaging suggests.'), 170)}</p>
      <ul class="focus-actors">${actors.map(a=>`<li>${a}</li>`).join('')}</ul>
      <p>${short(ensureSentence(primaryReview?.semantics?.claim || 'Watch who decides, who pays, and who quietly benefits.'), 150)}</p>
    `;
    byId('focusInfluence').innerHTML = influence;
  }

  if(byId('focusStakes')){
    const stakesMap = {
      ai: {sectors:'Semis, cloud, power infrastructure', assets:'SOXX, QQQ, USD', volatility:'Concentration risk remains high', supply:'Compute + power bottlenecks', flows:'Mega-cap concentration persists'},
      oil: {sectors:'Energy, transport, airlines', assets:'Brent, breakevens, XLE', volatility:'Energy-to-rates pass-through risk', supply:'Shipping and insurance chokepoints', flows:'Defensive commodity bids'},
      rates: {sectors:'Banks, housing, leveraged tech', assets:'UST 2Y/10Y, DXY, TLT', volatility:'Policy path uncertainty elevated', supply:'Credit availability tightens', flows:'Cash + USD preference'},
      autos: {sectors:'Autos, batteries, metals', assets:'CARZ, LIT, copper', volatility:'Tariff headline swings', supply:'Trade-route and tariff friction', flows:'Policy-driven sector rotation'},
      lng: {sectors:'Utilities, industry, chemicals', assets:'UNG, XLU, EUR crosses', volatility:'Gas-linked inflation sensitivity', supply:'Long-term offtake securitization', flows:'Infrastructure allocation support'},
      prediction: {sectors:'Platforms, fintech, exchanges', assets:'COIN, XLF proxies', volatility:'Compliance event spikes', supply:'Liquidity quality at risk', flows:'Risk-premium reset in platform names'},
      default: {sectors:'Policy-sensitive cyclicals', assets:'SPY, rates, dollar', volatility:'Headline-driven clustering', supply:'Logistics + financing constraints', flows:'Risk-sensitive rotations'}
    };

    const stakes = stakesMap[primaryTopic] || stakesMap.default;
    byId('focusStakes').innerHTML = `
      <ul class="focus-list">
        <li><strong>Who gets hit first:</strong> ${stakes.sectors}</li>
        <li><strong>Where price moves:</strong> ${stakes.assets}</li>
        <li><strong>Volatility regime:</strong> ${stakes.volatility}</li>
        <li><strong>Supply chain pressure:</strong> ${stakes.supply}</li>
        <li><strong>Capital flow direction:</strong> ${stakes.flows}</li>
      </ul>
    `;
  }

  renderBetContainer(items);
}

async function boot(){
  const [setups, narratives, curated] = await Promise.all([
    getJSON('./api/v1/home/setups.json',{items:[]}),
    getJSON('./data/narratives.json',{narrative_reviews:[]}),
    getJSON('./data/stories_in_play.json', null)
  ]);

  const curatedA = (curated?.version_a?.cards || []).slice(0,6);
  const curatedB = (curated?.version_b?.cards || []).slice(0,6);
  const fallbackItems = (setups.items || []).slice(0,9);
  const hasCurated = curatedA.length >= 6;
  let currentVersion = 'version_a';

  const narrativeMap = {};
  (narratives.narrative_reviews || []).forEach((review)=>{ narrativeMap[review.topic] = review; });

  const getItemsForVersion = (version) => {
    if(!hasCurated) return fallbackItems;
    if(version === 'version_b' && curatedB.length >= 6) return curatedB;
    return curatedA;
  };

  const primaryReview = (narratives.narrative_reviews || [])[0];

  const renderPage = (version) => {
    const items = getItemsForVersion(version);
    const usingCurated = hasCurated;
    const lead = items[0] || null;

    if(byId('leadStory')){
      if(usingCurated){
        byId('leadStory').innerHTML = lead ? cardBody(lead, {headingTag:'h3'}) : '<p>Intelligence update pending.</p>';
      } else {
        const narrative = narrativeMap[topicFromTitle(lead?.title)];
        byId('leadStory').innerHTML = lead ? storyBody(lead, narrative, {headingTag:'h3'}) : '<p>Intelligence update pending.</p>';
      }
    }

    if(byId('storyStack')){
      if(usingCurated){
        byId('storyStack').innerHTML = items.slice(1,6).map((card)=>`<article class="story story-card">${cardBody(card, {headingTag:'h4', compact:true})}</article>`).join('') || '<p>No additional stories yet.</p>';
      } else {
        byId('storyStack').innerHTML = items.slice(1,6).map(s=>{
          const narrative = narrativeMap[topicFromTitle(s?.title)];
          return `<article class="story story-card">${storyBody(s, narrative, {headingTag:'h4', compact:true})}</article>`;
        }).join('') || '<p>No additional stories yet.</p>';
      }
    }

    renderFocus(items, lead, usingCurated, primaryReview, narrativeMap);
    setActiveToggle(version);
  };

  renderPage(currentVersion);

  const toggleA = byId('toggleVersionA');
  const toggleB = byId('toggleVersionB');
  if(toggleA){
    toggleA.addEventListener('click', () => {
      currentVersion = 'version_a';
      renderPage(currentVersion);
    });
  }
  if(toggleB){
    toggleB.addEventListener('click', () => {
      currentVersion = 'version_b';
      renderPage(currentVersion);
    });
  }
}

boot();
