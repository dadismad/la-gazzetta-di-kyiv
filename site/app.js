function byId(id){ return document.getElementById(id); }

async function getJSON(path, fallback){
  try{
    const r = await fetch(path,{cache:'no-store'});
    if(!r.ok) throw new Error(String(r.status));
    return await r.json();
  }catch{ return fallback; }
}

function short(s='', n=180){ const v=String(s||'').trim(); return v.length>n?`${v.slice(0,n-1)}…`:v; }
function ensureSentence(value=''){ const t=String(value||'').trim(); if(!t) return ''; return /[.!?]$/.test(t)?t:`${t}.`; }
function confidenceLabel(conf=0){
  if(conf >= 0.75) return 'High';
  if(conf >= 0.6) return 'Medium';
  if(conf >= 0.45) return 'Measured';
  return 'Low';
}

function cardStoryMarkup(card, {lead=false} = {}){
  const title = short(card?.title || 'Story in Play', 96);
  const summary = ensureSentence(card?.summary || card?.body || 'Update pending.');
  const contradiction = ensureSentence(card?.contradiction || 'Consensus framing and real positioning remain misaligned.');
  const strategy = ensureSentence(card?.transmission || card?.strategy || 'Transmission runs through rates, FX, credit, and policy-sensitive equities.');
  const actors = (card?.actors || []).slice(0,6);
  const map = card?.market_map || [];
  const playbook = card?.playbook || {};
  const confidence = card?.confidence || confidenceLabel(0.58);

  return `
    <article class="story story-card ${lead ? 'story-lead' : ''}" data-expandable="true">
      <div class="story-core">
        <h3>${title}</h3>
        <p class="story-thesis">${short(summary, lead ? 260 : 180)}</p>
        <p class="story-contradiction"><strong>Contradiction:</strong> ${short(contradiction, lead ? 220 : 150)}</p>
        <button class="story-expand-btn" type="button" aria-expanded="false">Expand story</button>
      </div>
      <div class="story-details" hidden>
        <p class="story-strategy"><strong>Transmission:</strong> ${short(strategy, 220)}</p>
        ${actors.length ? `<p class="story-meta"><strong>Actors:</strong> ${actors.join(', ')}</p>` : ''}
        ${map.length ? `<p class="story-meta"><strong>Market map:</strong> ${map.join(' · ')}</p>` : ''}
        <div class="story-playbook">
          <p><strong>Playbook entry:</strong> ${ensureSentence(playbook.entry || 'Wait for confirmation move in primary asset and vol companion.')}</p>
          <p><strong>Invalidation:</strong> ${ensureSentence(playbook.invalidation || 'Narrative fails if policy and price stop reinforcing each other.')}</p>
          <p><strong>Next 24h watch:</strong> ${ensureSentence(playbook.next_24h || 'Watch policy headlines, liquidity conditions, and cross-asset follow-through.')}</p>
          <p class="story-confidence"><strong>Conviction:</strong> ${String(confidence).replace('_',' ')}</p>
        </div>
      </div>
    </article>
  `;
}

function profileFromCard(card){
  const tags = card?.asset_tags || [];
  const profiles = {
    oil: {ticker:'BZ=F', name:'Brent Crude', trigger:'Any Strait of Hormuz disruption headline', horizon:'24-72h', thesis:'Conflict headlines can quickly reprice fuel costs and inflation expectations.'},
    shipping: {ticker:'BDRY', name:'Dry Bulk Shipping', trigger:'Freight insurance or routing stress', horizon:'2-5d', thesis:'Logistics friction lifts transport costs before policy reacts.'},
    ust_yields: {ticker:'TLT', name:'US Duration', trigger:'Fed tone hardens or CPI surprises', horizon:'1-2w', thesis:'High rates keep pressure on leveraged balance sheets and growth multiples.'},
    usd: {ticker:'DXY', name:'US Dollar Index', trigger:'Risk-off + delayed cuts', horizon:'1-2w', thesis:'Dollar strength tightens global financing conditions.'},
    semiconductors: {ticker:'SOXX', name:'Semiconductors', trigger:'AI capex guidance revisions', horizon:'1-2w', thesis:'Crowded AI leadership can amplify both upside and drawdowns.'},
    megacap_tech: {ticker:'QQQ', name:'Nasdaq 100', trigger:'Mega-cap earnings miss', horizon:'24-72h', thesis:'Concentrated index leadership means one miss can hit the whole tape.'},
    autos: {ticker:'CARZ', name:'Global Autos', trigger:'Tariff/probe announcements', horizon:'1-3w', thesis:'Auto margins now move with politics, not only demand.'},
    batteries: {ticker:'LIT', name:'Battery Supply Chain', trigger:'Trade restrictions on EV inputs', horizon:'1-3w', thesis:'Policy shocks can rewire battery winners fast.'},
    lng: {ticker:'UNG', name:'US Natural Gas', trigger:'New long-term LNG offtake deals', horizon:'1-4w', thesis:'Energy security contracts keep gas infrastructure bid.'},
    prediction_markets: {ticker:'COIN', name:'Platform Risk Proxy', trigger:'Regulatory enforcement headlines', horizon:'24-72h', thesis:'Compliance shocks can instantly reprice platform risk.'},
    default: {ticker:'SPY', name:'S&P 500', trigger:'Macro contradiction resolves', horizon:'1-2w', thesis:'Index level follows whether risk premium rises or fades.'}
  };
  const key = tags.find((t)=>profiles[t]) || 'default';
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
  target.innerHTML = picks.map((card, idx)=>{
    const p = profileFromCard(card);
    const conviction = card?.confidence ? String(card.confidence).replace('_',' ') : confidenceLabel(0.55);
    return `
      <article class="bet-item">
        <div class="bet-top"><span class="bet-rank">#${idx+1}</span><span class="bet-ticker">${p.ticker}</span></div>
        <div class="bet-name">${p.name}</div>
        <div class="bet-hook">${short(card?.title || 'Story', 70)}</div>
        <div class="bet-meta"><strong>Trigger:</strong> ${p.trigger}</div>
        <div class="bet-meta"><strong>Horizon:</strong> ${p.horizon} · <strong>Conviction:</strong> ${conviction}</div>
        <div class="bet-thesis">${p.thesis}</div>
      </article>
    `;
  }).join('');
}

function wireExpandableStories(){
  document.querySelectorAll('.story-expand-btn').forEach((btn)=>{
    btn.addEventListener('click', ()=>{
      const card = btn.closest('[data-expandable="true"]');
      const details = card?.querySelector('.story-details');
      if(!details) return;
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      btn.textContent = expanded ? 'Expand story' : 'Collapse story';
      details.hidden = expanded;
    });
  });
}

function renderFocus(items){
  const lead = items[0] || {};
  if(byId('focusInfluence')){
    byId('focusInfluence').innerHTML = `
      <p>${short(ensureSentence(lead?.summary || lead?.body || 'Power actors are forcing repricing faster than public messaging admits.'), 180)}</p>
      <p>${short(ensureSentence(lead?.contradiction || 'Watch who decides, who pays, and who quietly benefits.'), 170)}</p>
    `;
  }
  if(byId('focusStakes')){
    const map = (lead?.market_map || ['Rates path sensitivity','Cross-asset volatility transmission','Policy credibility risk']).slice(0,5);
    byId('focusStakes').innerHTML = `<ul class="focus-list">${map.map((x)=>`<li>${x}</li>`).join('')}</ul>`;
  }
  renderBetContainer(items);
}

async function boot(){
  const curated = await getJSON('./data/stories_in_play.json', null);
  const cards = (curated?.main?.cards || curated?.version_b?.cards || []).slice(0,6);

  const lead = cards[0] || null;
  const stack = cards.slice(1,6);

  if(byId('leadStory')){
    byId('leadStory').innerHTML = lead ? cardStoryMarkup(lead, {lead:true}) : '<p>Intelligence update pending.</p>';
  }
  if(byId('storyStack')){
    byId('storyStack').innerHTML = stack.map((card)=>cardStoryMarkup(card)).join('') || '<p>No additional stories yet.</p>';
  }

  renderFocus(cards);
  wireExpandableStories();
}

boot();
