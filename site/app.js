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

function confidenceRetailTag(conf='medium'){
  const v = String(conf).toLowerCase();
  if(v.includes('high')) return 'Stronger setup';
  if(v.includes('low')) return 'Higher risk';
  return 'Balanced risk';
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
    <article class="story story-card ${lead ? 'story-lead' : ''}" data-expandable="true" tabindex="0" role="button" aria-expanded="false" aria-label="${title}. Click to expand details.">
      <div class="story-core">
        <h3>${title}</h3>
        <p class="story-thesis">${short(summary, lead ? 220 : 150)}</p>
        <p class="story-contradiction"><strong>Contradiction:</strong> ${short(contradiction, lead ? 185 : 130)}</p>
      </div>
      <div class="story-details">
        <p class="story-strategy"><strong>How it moves markets:</strong> ${short(strategy, 220)}</p>
        ${actors.length ? `<p class="story-meta"><strong>Main actors:</strong> ${actors.join(', ')}</p>` : ''}
        ${map.length ? `<p class="story-meta"><strong>Likely market path:</strong> ${map.join(' · ')}</p>` : ''}
        <div class="story-playbook">
          <p><strong>Retail entry idea:</strong> ${ensureSentence(playbook.entry || 'Wait for confirmation move in primary asset and vol companion.')}</p>
          <p><strong>Stop / invalidation:</strong> ${ensureSentence(playbook.invalidation || 'Narrative fails if policy and price stop reinforcing each other.')}</p>
          <p><strong>What to watch next 24h:</strong> ${ensureSentence(playbook.next_24h || 'Watch policy headlines, liquidity conditions, and cross-asset follow-through.')}</p>
          <p class="story-confidence"><strong>Risk level:</strong> ${confidenceRetailTag(confidence)}</p>
        </div>
      </div>
    </article>
  `;
}

function profileFromCard(card){
  const tags = card?.asset_tags || [];
  const profiles = {
    oil: {ticker:'BZ=F', name:'Brent Crude', if_right:'Oil likely rises', if_wrong:'Oil cools fast', trigger:'New Hormuz risk headline', horizon:'24-72h'},
    shipping: {ticker:'BDRY', name:'Shipping Costs', if_right:'Freight rates rise', if_wrong:'Freight stress fades', trigger:'Insurance/routing stress', horizon:'2-5 days'},
    ust_yields: {ticker:'TLT', name:'US Bonds (TLT)', if_right:'TLT weak if yields rise', if_wrong:'TLT rebounds', trigger:'Hawkish Fed signal', horizon:'1-2 weeks'},
    usd: {ticker:'DXY', name:'US Dollar', if_right:'Dollar strengthens', if_wrong:'Dollar softens', trigger:'Risk-off and delayed cuts', horizon:'1-2 weeks'},
    semiconductors: {ticker:'SOXX', name:'Semis ETF', if_right:'Leadership extends', if_wrong:'Fast pullback risk', trigger:'AI guidance upgrades/downgrades', horizon:'1-2 weeks'},
    megacap_tech: {ticker:'QQQ', name:'Nasdaq 100', if_right:'Trend continues', if_wrong:'Crowded unwind', trigger:'Mega-cap earnings signal', horizon:'24-72h'},
    autos: {ticker:'CARZ', name:'Global Autos', if_right:'Winners by policy', if_wrong:'Tariff relief squeeze', trigger:'Tariff/probe announcement', horizon:'1-3 weeks'},
    batteries: {ticker:'LIT', name:'Battery Supply Chain', if_right:'Policy winners outperform', if_wrong:'Input prices normalize', trigger:'EV trade restrictions', horizon:'1-3 weeks'},
    lng: {ticker:'UNG', name:'US Nat Gas', if_right:'Gas pricing firm', if_wrong:'Demand cool-off', trigger:'New LNG contract news', horizon:'1-4 weeks'},
    prediction_markets: {ticker:'COIN', name:'Platform Risk Proxy', if_right:'Risk premium expands', if_wrong:'Regulatory clarity relief', trigger:'Enforcement headlines', horizon:'24-72h'},
    default: {ticker:'SPY', name:'S&P 500', if_right:'Risk premium rises/falls with narrative', if_wrong:'Mean reversion', trigger:'Macro contradiction resolves', horizon:'1-2 weeks'}
  };
  const key = tags.find((t)=>profiles[t]) || 'default';
  return profiles[key] || profiles.default;
}

function renderBetContainer(items){
  const target = byId('focusBet');
  if(!target) return;
  const picks = items.slice(0,5);
  if(!picks.length){
    target.innerHTML = '<p>Positioning watchlist pending.</p>';
    return;
  }

  target.innerHTML = picks.map((card, idx)=>{
    const p = profileFromCard(card);
    const confidence = card?.confidence ? String(card.confidence).replace('_',' ') : 'medium';
    return `
      <article class="bet-item">
        <div class="bet-top"><span class="bet-rank">Idea ${idx+1}</span><span class="bet-ticker">${p.ticker}</span></div>
        <div class="bet-name">${p.name}</div>
        <div class="bet-hook">${short(card?.title || 'Story', 72)}</div>
        <div class="bet-meta"><strong>If this story is right:</strong> ${p.if_right}</div>
        <div class="bet-meta"><strong>If this story is wrong:</strong> ${p.if_wrong}</div>
        <div class="bet-meta"><strong>Trigger:</strong> ${p.trigger}</div>
        <div class="bet-meta"><strong>Time window:</strong> ${p.horizon} · <strong>Risk:</strong> ${confidenceRetailTag(confidence)}</div>
      </article>
    `;
  }).join('');
}

function setStoryExpanded(card, expanded){
  const details = card?.querySelector('.story-details');
  if(!details) return;
  card.setAttribute('aria-expanded', String(expanded));
  card.classList.toggle('is-expanded', expanded);
}

function wireExpandableStories(){
  const cards = [...document.querySelectorAll('[data-expandable="true"]')];
  cards.forEach((card)=>{
    const toggle = ()=>{
      const expanded = card.getAttribute('aria-expanded') === 'true';
      if(expanded){
        setStoryExpanded(card, false);
        return;
      }
      cards.forEach((other)=>{ if(other !== card) setStoryExpanded(other, false); });
      setStoryExpanded(card, true);
    };

    card.addEventListener('click', ()=>toggle());
    card.addEventListener('keydown', (e)=>{
      if(e.key === 'Enter' || e.key === ' '){
        e.preventDefault();
        toggle();
      }
    });
  });
}

function renderFocus(items){
  const lead = items[0] || {};
  if(byId('focusInfluence')){
    byId('focusInfluence').innerHTML = `
      <p>${short(ensureSentence(lead?.summary || lead?.body || 'Power actors are forcing repricing faster than public messaging admits.'), 170)}</p>
      <p>${short(ensureSentence(lead?.contradiction || 'Watch who decides, who pays, and who quietly benefits.'), 150)}</p>
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
  const cards = (curated?.main?.cards || curated?.version_b?.cards || []).slice(0,10);

  const lead = cards[0] || null;
  const stack = cards.slice(1,10);

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
