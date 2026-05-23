function normTopic(t){return (t||'macro').toLowerCase();}
const POT=['Low','Medium','High','Extreme'];

function frameFor(topic){
  const t=normTopic(topic);
  const m={ai:['TECH/AI','Automated Abundance'],oil:['ENERGY','Decentralized Grids'],inflation:['MACRO','Price Friction'],rates:['FIXED INCOME','Liquidity Discipline'],crypto:['FINTECH','Algorithmic Sovereignty'],russia:['GEOPOLITICS','Strategic Fragmentation'],election:['POLICY','Election Volatility'],eu:['EUROPE','Fiscal Divergence']};
  return m[t]||['GLOBAL','Narrative Transition'];
}
function frameInsight(frame){
  const m={
    'Automated Abundance':'AI capex and productivity narratives driving growth-vs-valuation tension.',
    'Decentralized Grids':'Energy supply shocks interacting with inflation expectations and transport costs.',
    'Price Friction':'Sticky price dynamics reshaping consumer demand and central-bank signaling.',
    'Liquidity Discipline':'Rates and funding conditions driving cross-asset repositioning pressure.',
    'Algorithmic Sovereignty':'Crypto/beta sentiment leading risk-on and liquidity rotation cues.',
    'Strategic Fragmentation':'Geopolitical disruptions repricing trade routes, sanctions, and commodity risk.',
    'Election Volatility':'Policy uncertainty altering sector dispersion and options-implied risk.',
    'Fiscal Divergence':'European fiscal stress affecting sovereign spreads and FX flows.',
    'Narrative Transition':'Mixed macro regime with rotating leadership across assets.'
  };
  return m[frame] || m['Narrative Transition'];
}
function potentialFor(topic){ const t=normTopic(topic); const m={ai:'High',oil:'High',inflation:'Medium',rates:'Medium',crypto:'Extreme',russia:'Low',election:'High',eu:'Medium'}; return m[t]||'Medium';}
function flowFor(topic){const m={ai:12.4,oil:6.1,inflation:4.3,rates:5.0,election:3.2,crypto:9.7,russia:2.8,ukraine:2.5,eu:4.9};return (m[normTopic(topic)]??3.8)}
function proj3dFor(topic){const m={ai:'+1.8%',oil:'+1.2%',inflation:'-0.4%',rates:'-0.6%',election:'±1.1%',crypto:'+2.6%',russia:'+0.7%',ukraine:'+0.5%',eu:'+0.9%'};return m[normTopic(topic)]||'±0.8%'}
function assetFor(topic){const m={ai:'NASDAQ 100',oil:'Brent',inflation:'UST 2Y',rates:'UST 10Y',crypto:'BTC',russia:'EU Gas',election:'S&P 500',eu:'EURUSD'};return m[normTopic(topic)]||'Global Risk Basket'}

let N=[];let activeFrame='';

async function load(){
  const n=await fetch('./data/narratives.json').then(r=>r.json()).catch(()=>({}));
  const reviews=(n.narrative_reviews||[]).slice(0,12);
  N=reviews.map((r,i)=>{
    const [cat,frame]=frameFor(r.topic);
    return {
      id:i+1,topic:(r.topic||'macro').toUpperCase(),cat,frame,
      claim:(r.headline||'Narrative drift requires tactical adaptation.'),
      desc:(r.review||'Cross-asset conditions suggest selective risk-taking with strict invalidation points.'),
      potential:potentialFor(r.topic),flow:flowFor(r.topic),proj3d:proj3dFor(r.topic),asset:assetFor(r.topic)
    }
  });
  renderFrames(); renderClaims(); bindControls(); if(N[0]) showFocus(0);
}

function renderFrames(){
  const frames=[...new Map(N.map(x=>[x.frame,x])).values()];
  const el=document.getElementById('frameList');
  el.innerHTML=frames.map((x,i)=>`<div class='frame-item ${i===0?'active':''}' data-frame='${x.frame}'><div class='frame-cat'>${x.cat}</div><div class='frame-name'>${x.frame}</div><div class='frame-note'>${frameInsight(x.frame)}</div></div>`).join('');
  activeFrame=frames[0]?.frame||'';
  el.querySelectorAll('.frame-item').forEach(node=>node.onclick=()=>{activeFrame=node.dataset.frame;el.querySelectorAll('.frame-item').forEach(n=>n.classList.remove('active'));node.classList.add('active');renderClaims();});
}

function claimRow(x,idx){
  return `<div class='claim-row' data-id='${idx}'>
    <div class='claim-head'>
      <div class='claim-idx'>${String(x.id).padStart(2,'0')}</div>
      <div><div class='claim-title'>${x.claim}</div><div class='claim-sub'>${x.desc.slice(0,120)}</div></div>
      <div class='claim-pot'>${x.potential}</div>
    </div>
    <div class='claim-extra'>
      <div class='insight-line'><span class='badge'>Flow 3d</span> ~$${x.flow}B</div>
      <div class='insight-line'><span class='badge'>Projection 3d</span> ${x.proj3d}</div>
      <div class='insight-line'><span class='badge'>Primary asset</span> ${x.asset}</div>
    </div>
  </div>`;
}

function renderClaims(){
  let list=activeFrame?N.filter(x=>x.frame===activeFrame):N;
  if(!list.length) list=N.slice(0,8);
  const el=document.getElementById('claimsList');
  el.innerHTML=list.length ? list.map((x,i)=>claimRow(x,N.indexOf(x))).join('') : `<div class='claim-empty'>No active claims yet. Pipeline is refreshing; showing latest macro frames shortly.</div>`;
  el.querySelectorAll('.claim-row').forEach(r=>{r.querySelector('.claim-head').onclick=()=>{r.classList.toggle('open');showFocus(Number(r.dataset.id));};});
}

function showFocus(i){
  const x=N[i]; if(!x) return;
  document.getElementById('selectedNarrative').innerHTML=`
    <div class='focus-title'>Dominating Regime: ${x.frame}</div>
    <div class='kpi'><span>Capital flow (3d)</span><b>~$${x.flow}B</b></div>
    <div class='kpi'><span>${x.asset} projection (3d)</span><b>${x.proj3d}</b></div>
    <div class='kpi'><span>Industry pressure</span><b>${x.potential}</b></div>
    <div class='focus-copy'>Actionable setup: wait for confirmation candle + volume expansion in ${x.asset}; invalidate if macro headline reverses policy/rates direction.</div>
    <ul class='focus-list'>
      <li>Entry protocol: stage risk in 2 tranches over 24h.</li>
      <li>Risk cap: max portfolio heat 1.2% for this narrative cluster.</li>
      <li>Watchlist: rates path, energy shock, and policy headlines.</li>
    </ul>`;
}

function bindControls(){
  document.getElementById('searchBox').oninput=(e)=>{const q=e.target.value.toLowerCase();document.querySelectorAll('.claim-row').forEach(r=>{r.style.display=r.innerText.toLowerCase().includes(q)?'block':'none';});};
  document.getElementById('collapseAll').onclick=()=>document.querySelectorAll('.claim-row').forEach(r=>r.classList.remove('open'));
  document.getElementById('expandAll').onclick=()=>document.querySelectorAll('.claim-row').forEach(r=>r.classList.add('open'));
}

load();