function normalizeTopic(t){return (t||'market theme').toLowerCase();}

function retailSentence(topic, review){
  const base = normalizeTopic(topic);
  return `${base.charAt(0).toUpperCase()+base.slice(1)} is becoming a market-moving story traders should monitor closely.`;
}

function retailSubpoints(topic, review, mentions, momentum){
  return [
    `Why it matters now: ${review || 'News flow is clustering around this theme and can influence short-term price behavior.'}`,
    `Most crucial detail: this narrative is seeing repeated discussion across sources, suggesting persistent attention rather than a one-off headline.`,
    `Practical read for retail traders: watch related assets and wait for confirmation before taking oversized positions.`
  ];
}

async function load(){
  const n = await fetch('../data/narratives.json').then(r=>r.json()).catch(()=>({}));
  const reviews=(n.narrative_reviews||[]);

  const updated=document.getElementById('updated');
  if(updated) updated.textContent=`Updated: ${n.generated_at||'n/a'}`;

  const listEl=document.getElementById('narrativeList');
  const details=document.getElementById('selectedNarrative');

  window.__retailNarratives = reviews.map(x=>({
    topic: x.topic,
    sentence: retailSentence(x.topic, x.review),
    subpoints: retailSubpoints(x.topic, x.review, x.mentions_24h, x.momentum)
  }));

  if(listEl){
    listEl.innerHTML = window.__retailNarratives.map((x,i)=>`
      <article class='n-row' onclick='selectNarrative(${i})'>
        <div class='n-title'>${(x.topic||'NARRATIVE').toUpperCase()}</div>
        <div class='n-sentence'>${x.sentence}</div>
        <div class='n-sub'>${x.subpoints[0]}</div>
      </article>
    `).join('');
  }

  window.selectNarrative=(i)=>{
    const x=(window.__retailNarratives||[])[i]; if(!x||!details) return;
    details.innerHTML=`
      <div class='muted'>Selected narrative</div>
      <div class='focus-title'>${x.sentence}</div>
      <div class='focus-copy'>${x.subpoints[0]}</div>
      <ul class='subpoints'>
        <li>${x.subpoints[1]}</li>
        <li>${x.subpoints[2]}</li>
      </ul>
    `;
  };

  if(window.__retailNarratives[0]) window.selectNarrative(0);
}

load();