function byId(id){return document.getElementById(id)}

async function getJSON(path,fallback){
  try{const r=await fetch(path,{cache:'no-store'}); if(!r.ok) throw new Error(String(r.status)); return await r.json()}catch{return fallback}
}

function cleanTitle(t=''){return String(t).replace('Narrative acceleration: ','').trim()}
function snippet(t=''){const s=String(t||'').trim(); return s.length>170?`${s.slice(0,167)}…`:s}

function storyItem(title,text){
  return `<div class="item"><h4>${title}</h4><p>${snippet(text)}</p></div>`
}

async function boot(){
  const setups = await getJSON('./api/v1/home/setups.json',{items:[]})
  const contradictions = await getJSON('./api/v1/home/contradictions.json',{items:[]})
  const regime = await getJSON('./api/v1/home/regime.json',{})

  const items=(setups.items||[]).slice(0,9)
  const lead=items[0]

  if(lead){
    byId('leadStory').innerHTML = `
      <h3>${cleanTitle(lead.title)}</h3>
      <p>${lead.thesis || 'Top story under analysis.'}</p>
      <p><b>Why now:</b> ${(lead.invalidation_triggers||[])[0] || 'Narrative velocity is rising across macro/politics channels.'}</p>
    `
  } else {
    byId('leadStory').innerHTML = '<h3>Top Story Pending</h3><p>Data pipeline will populate this section on next cycle.</p>'
  }

  const topGrid=items.slice(1,4).map(s=>`<article class="story-card"><h4>${cleanTitle(s.title)}</h4><p>${snippet(s.thesis)}</p></article>`).join('')
  byId('topStoryGrid').innerHTML = topGrid || '<p>No additional top stories yet.</p>'

  const macro=items.slice(0,3).map(s=>storyItem(cleanTitle(s.title),s.thesis)).join('')
  byId('macroStories').innerHTML = macro || '<p>No macro stories yet.</p>'

  const politicsSeed = contradictions.items||[]
  byId('politicsStories').innerHTML = politicsSeed.slice(0,3).map(c=>storyItem(c.claim_a,c.claim_b)).join('') || '<p>No politics stories yet.</p>'

  byId('geopoliticsStories').innerHTML = items.slice(3,6).map(s=>storyItem(cleanTitle(s.title), (s.invalidation_triggers||[]).join(' · '))).join('') || '<p>No geopolitics stories yet.</p>'

  const niSource = contradictions.items?.[0]
  byId('niColumnCard').innerHTML = niSource ? `
    <article class="ni-card">
      <h3>${niSource.claim_a}</h3>
      <p><b>Consensus:</b> ${niSource.claim_b}</p>
      <p><b>Interpretation:</b> ${niSource.why_it_matters || 'Incentive mismatch can force repricing across adjacent assets.'}</p>
      <p><b>Regime context:</b> ${regime.regime_label || 'Pending'} (${Math.round((regime.confidence||0)*100)}% confidence)</p>
      <span class="badge">Actors</span><span class="badge">Incentives</span><span class="badge">Contradictions</span>
    </article>
  ` : '<p>NI column pending latest contradiction map.</p>'
}

boot()
