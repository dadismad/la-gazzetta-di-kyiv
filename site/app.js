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
  return cleanTitle(title).toLowerCase();
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
  const positioningRaw = (s?.retail_execution || [])[0] || narrative?.semantics?.repricing || 'Prefer defined-risk structures with staged entry.';
  const positioning = ensureSentence(positioningRaw);
  const limits = compact
    ? {thesis:150, contradiction:130, strategy:150, positioning:120}
    : {thesis:220, contradiction:200, strategy:200, positioning:160};
  return `
    <${headingTag}>${title}</${headingTag}>
    <p class="story-thesis">${short(thesis, limits.thesis)}</p>
    <p class="story-contradiction">${short(contradiction, limits.contradiction)}</p>
    <p class="story-strategy">${short(strategy, limits.strategy)}</p>
    <p class="story-positioning">${short(positioning, limits.positioning)}</p>
  `;
}

function cardBody(card, {headingTag='h3'} = {}){
  const title = short(card?.title || 'Story in Play', 90);
  const body = short(ensureSentence(card?.body || 'Update pending.'), 360);
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

  const renderStories = (version) => {
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
        byId('storyStack').innerHTML = items.slice(1,6).map((card)=>{
          return `<article class="story story-card">${cardBody(card, {headingTag:'h4'})}</article>`;
        }).join('') || '<p>No additional stories yet.</p>';
      } else {
        byId('storyStack').innerHTML = items.slice(1,6).map(s=>{
          const narrative = narrativeMap[topicFromTitle(s?.title)];
          return `<article class="story story-card">${storyBody(s, narrative, {headingTag:'h4', compact:true})}</article>`;
        }).join('') || '<p>No additional stories yet.</p>';
      }
    }

    setActiveToggle(version);
    return { items, lead, usingCurated };
  };

  const firstRender = renderStories(currentVersion);
  const lead = firstRender.lead;
  const items = firstRender.items;

  const toggleA = byId('toggleVersionA');
  const toggleB = byId('toggleVersionB');
  if(toggleA){
    toggleA.addEventListener('click', () => {
      currentVersion = 'version_a';
      renderStories(currentVersion);
    });
  }
  if(toggleB){
    toggleB.addEventListener('click', () => {
      currentVersion = 'version_b';
      renderStories(currentVersion);
    });
  }

  const primaryReview = (narratives.narrative_reviews || [])[0];
  const primaryTopic = primaryReview?.topic || topicFromTitle(lead?.title);
  const defaultActors = ['Sovereign funds','Strategic alliances','Major banks','Defense ministries'];
  const influenceActors = firstRender.usingCurated
    ? (lead?.actors || [])
    : (primaryReview?.semantics?.actors || []).slice(0,6);
  const actors = influenceActors.length ? influenceActors : defaultActors;

  if(byId('focusInfluence')){
    const influence = `
      <p>${short(ensureSentence(primaryReview?.semantics?.svo || primaryReview?.review || 'Key actors are repositioning around shifting incentives.'), 190)}</p>
      <ul class="focus-actors">${actors.map(a=>`<li>${a}</li>`).join('')}</ul>
      <p>${short(ensureSentence(primaryReview?.semantics?.claim || 'Coalition behaviour and capital discipline set the tempo.'), 170)}</p>
    `;
    byId('focusInfluence').innerHTML = influence;
  }

  if(byId('focusStakes')){
    const stakesMap = {
      ai: {
        sectors: 'Semiconductors, hyperscale capex, cloud infrastructure',
        assets: 'NQ, SOXX, mega-cap duration',
        volatility: 'Growth beta volatility skews higher',
        supply: 'Compute and power supply chains under strain',
        flows: 'US mega-cap and thematic inflows'
      },
      eu: {
        sectors: 'European industrials, utilities, banks',
        assets: 'EUR, sovereign spreads, regional dispersion',
        volatility: 'Rates vol on policy divergence',
        supply: 'Energy routing and fiscal coordination',
        flows: 'Rotation into hedged regional exposure'
      },
      china: {
        sectors: 'Cyclicals, commodities, EM industrials',
        assets: 'CNH, EM FX, industrial metals',
        volatility: 'Macro beta volatility in Asia',
        supply: 'Export routing and supply resilience',
        flows: 'Selective EM risk appetite'
      },
      oil: {
        sectors: 'Energy, transport, industrial inputs',
        assets: 'Brent, XLE, inflation breakevens',
        volatility: 'Energy vol transmits into rates',
        supply: 'Shipping and corridor insurance costs',
        flows: 'Defensive rotation and commodity hedges'
      },
      gas: {
        sectors: 'Utilities, chemicals, European industrials',
        assets: 'TTF, EUR, regional equity dispersion',
        volatility: 'Energy vol lifts rates uncertainty',
        supply: 'LNG flow stability and storage quality',
        flows: 'Risk-off hedging into defensives'
      },
      default: {
        sectors: 'Policy-sensitive cyclicals and defensives',
        assets: 'Rates, FX, global equity beta',
        volatility: 'Volatility clusters around policy events',
        supply: 'Strategic supply chains and logistics',
        flows: 'Risk-sensitive capital rotation'
      }
    };
    const stakes = stakesMap[primaryTopic] || stakesMap.default;
    const stakesHtml = `
      <ul class="focus-list">
        <li><strong>Sectors exposed:</strong> ${stakes.sectors}</li>
        <li><strong>Asset sensitivity:</strong> ${stakes.assets}</li>
        <li><strong>Volatility:</strong> ${stakes.volatility}</li>
        <li><strong>Supply chain:</strong> ${stakes.supply}</li>
        <li><strong>Capital flows:</strong> ${stakes.flows}</li>
      </ul>
    `;
    byId('focusStakes').innerHTML = stakesHtml;
  }

  if(byId('focusBet')){
    const betMap = {
      ai: {ticker:'NVDA', range:'+8–12%'},
      eu: {ticker:'EZU', range:'±3–5%'},
      china: {ticker:'FXI', range:'±4–7%'},
      election: {ticker:'XLF', range:'±2–4%'},
      gas: {ticker:'UNG', range:'+6–10%'},
      oil: {ticker:'XLE', range:'+4–8%'},
      inflation: {ticker:'TIP', range:'±2–4%'},
      rates: {ticker:'TLT', range:'±3–6%'},
      russia: {ticker:'RSX', range:'±5–9%'},
      crypto: {ticker:'BTC', range:'±6–12%'},
      drone: {ticker:'ITA', range:'±3–6%'},
      nato: {ticker:'ITA', range:'±3–6%'},
      default: {ticker:'SPY', range:'±2–4%'}
    };
    const betItems = items.slice(0,3);
    const betHtml = betItems.map((s)=>{
      const topic = topicFromTitle(s?.title);
      const bet = betMap[topic] || betMap.default;
      const probability = Math.round(s?.probability_base ?? 50);
      const confidence = confidenceLabel(s?.confidence || 0.5);
      return `
        <div class="bet-item">
          <div class="bet-ticker">${bet.ticker}</div>
          <div class="bet-meta">Probability: ${probability}%</div>
          <div class="bet-meta">Projected repricing: ${bet.range}</div>
          <div class="bet-meta">Confidence: ${confidence}</div>
        </div>
      `;
    }).join('');
    byId('focusBet').innerHTML = betHtml || '<p>Positioning watchlist pending.</p>';
  }
}

boot();
