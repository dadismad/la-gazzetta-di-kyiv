     1|// story-app.js — Immersive single-story intel report page
// v24.1: +multi-persona +async init fix
     2|// v24.0: +multi-persona blocks (C-Suite/Quant/Degen)
     3|// v2.0: Modular rewrite — eliminated scope fragility, proper async init
     4|
     5|(function() {
     6|  'use strict';
     7|
     8|  const STORIES_PATH = './data/stories.json';
     9|  const STORIES_RU_PATH = './data/stories_ru.json';
    10|  const LIVING_PATH = './data/living_stories.json';
    11|
    12|  async function getJSON(path, fallback) {
    13|    try {
    14|      const r = await fetch(path + '?t=' + Date.now(), { cache: 'no-store' });
    15|      if (!r.ok) throw new Error(String(r.status));
    16|      return await r.json();
    17|    } catch (e) { console.warn('Fetch:', path, e); return fallback; }
    18|  }
    19|
    20|  function getStoryId() {
    21|    const p = new URLSearchParams(window.location.search);
    22|    return p.get('id') || p.get('story') || '';
    23|  }
    24|
    25|  function findStory(data, id) {
    26|    if (!data) return null;
    27|    const stories = data.stories || [];
    28|    if (data.lead && data.lead.story_id === id) return data.lead;
    29|    return stories.find(s => s.story_id === id) || null;
    30|  }
    31|
    32|  function formatDate(ts) {
    33|    if (!ts) return '';
    34|    try {
    35|      const d = new Date(ts);
    36|      return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' }).toUpperCase();
    37|    } catch { return ts; }
    38|  }
    39|
    40|  function tensionBadge(score) {
    41|    const s = score || 0;
    42|    if (s >= 67) return { cls: 'contradicted', label: window.i18n ? i18n.t('tension_max','MAX TENSION') : 'MAX TENSION' };
    43|    if (s >= 34) return { cls: 'divergent', label: window.i18n ? i18n.t('tension_high','HIGH TENSION') : 'HIGH TENSION' };
    44|    return { cls: 'aligned', label: window.i18n ? i18n.t('tension_building','BUILDING') : 'BUILDING' };
    45|  }
    46|
    47|  function buildHTML(story, allStories, currentIdx) {
    48|    const t = window.i18n ? (k, fb) => i18n.t(k, fb) : (k, fb) => fb;
    49|    const cf = story.capital_flow || {};
    50|    const tension = tensionBadge(story.contradiction_score || 0);
    51|    const category = t('sector_' + (story.sector || 'markets').toLowerCase(), (story.sector || 'MARKETS').toUpperCase());
    52|    const severity = (story.severity || 'HIGH').toUpperCase();
    53|    const date = formatDate(story.timestamp || story.date || story.generated_at);
    54|
    55|    const photo = story.photo || (cf.asset_class ? `./media/${cf.asset_class}.jpg` : '');
    56|    const headline = story.headline || story.title || '';
    57|    const summary = story.body || story.description || story.thesis || '';
    58|    const theySay = story.they_say || '';
    59|    const reality = story.reality || '';
    60|    const claim = cf.claim || '';
    61|    const projected = cf.projected || '';
    62|    const positioning = cf.positioning || '';
    63|    const amountB = cf.amount_b || 0;
    64|    const direction = cf.direction || '';
    65|    const confidence = cf.confidence_pct || story.confidence || 0;
    66|    const confLabel = confidence >= 80 ? 'HIGH' : confidence >= 60 ? 'MEDIUM' : 'LOW';
    67|    const extremum = story.extremum || '';
    68|    const play = story.portfolio_implication || story.the_play || '';
    69|    const catalysts = story.catalysts || [];
    70|
    71|    const dirArrow = direction === 'inflow' ? '↑' : direction === 'outflow' ? '↓' : '';
    72|    const dirWord = direction === 'inflow' ? 'into' : 'out of';
    73|    const assetClass = cf.asset_class || 'equities';
    74|
    75|    const totalStories = allStories.length;
    76|    const hasNext = currentIdx < totalStories - 1;
    77|    const nextStory = hasNext ? allStories[currentIdx + 1] : null;
    78|
    79|    return `
    80|    <article class="intel-report">
    81|      <header class="intel-header">
    82|        <div class="intel-meta">
    83|          <span class="intel-category">${category}</span>
    84|          <span class="intel-severity severity-${severity.toLowerCase()}">${t('severity_' + severity.toLowerCase(), severity)}</span>
    85|          <time class="intel-date">${date}</time>
    86|          <span class="tier-badge ${tension.cls}">${tension.label} <span class="tier-score">${story.contradiction_score || 0}/100</span></span>
    87|        </div>
    88|        <h1 class="intel-headline">${headline}</h1>
    89|        ${photo ? `<div class="intel-photo"><img src="${photo}" alt="" loading="lazy" onerror="this.style.display='none'"/></div>` : ''}
    90|      </header>
    91|
    92|      <section class="intel-brief">
    93|        <h2 class="intel-section-label">${t('intel_brief', 'INTEL BRIEF')}</h2>
    94|        <div class="intel-summary">${summary}</div>
    95|      </section>
    96|
    97|      <section class="intel-play">
    98|        <h2 class="intel-section-label play-label">${t('the_play_label', 'THE PLAY')}</h2>
    99|        <div class="intel-play-content">${play}</div>
   100|        ${catalysts.length ? `<div class="intel-catalysts"><span class="catalyst-tag">${t('catalysts', 'Catalysts')}:</span> ${catalysts.join(' · ')}</div>` : ''}
   101|      </section>
   102|
   103|      <div class="intel-contradiction">
   104|        <section class="intel-they-say">
   105|          <h2 class="intel-section-label they-say-label">${t('they_say', 'THEY SAY')}</h2>
   106|          <div class="intel-they-say-content">${theySay}</div>
   107|        </section>
   108|        <section class="intel-reality">
   109|          <h2 class="intel-section-label reality-label">${t('reality', 'REALITY')}</h2>
   110|          <div class="intel-reality-content">${reality}</div>
   111|        </section>
   112|      </div>
   113|
   114|      <section class="intel-capital-flow">
   115|        <h2 class="intel-section-label cf-label">${t('capital_flow_label', 'CAPITAL FLOW')}</h2>
   116|        <div class="intel-cf-data">
   117|          <div class="intel-cf-amount">$${amountB}B ${dirArrow} ${assetClass}</div>
   118|          <div class="intel-cf-meta">
   119|            <span class="intel-cf-confidence">${confidence}% ${t('flow_confidence_pct', 'confidence')} · ${confLabel}</span>
   120|            <span class="intel-cf-direction">${t('flow_' + direction, direction)}</span>
   121|          </div>
   122|          ${claim ? `<div class="intel-cf-claim">${claim}</div>` : ''}
   123|          ${projected ? `<div class="intel-cf-projected"><span class="intel-cf-projected-label">${t('flow_projected', 'Projected')}:</span> ${projected}</div>` : ''}
   124|          ${positioning ? `<div class="intel-cf-positioning">${positioning}</div>` : ''}
   125|        </div>
   126|      </section>
   127|
   128|      <section class="intel-extremum">
   129|        <h2 class="intel-section-label extremum-label">${t('extremum', 'EXTREMUM')}</h2>
   130|        <div class="intel-extremum-content">${typeof extremum === 'object' ? (extremum.type + ': ' + (extremum.description || '').slice(0, 200)) : extremum}</div>
   131|      </section>
   132|
   133|      ${renderMultiPersona(story)}
   134|
   135|      <div class="intel-share">
   136|        <button onclick="copyStoryLink()" class="share-btn" title="${t('share_copy', 'Copy link')}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></button>
   137|        <button onclick="shareTo('x')" class="share-btn" title="${t('share_x', 'Share on X')}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 4l11.733 16h4.267l-11.733 -16z"/><path d="M4 20l6.768 -6.768m2.46 -2.46L20 4"/></svg></button>
   138|        <button onclick="shareTo('facebook')" class="share-btn" title="${t('share_facebook', 'Share on Facebook')}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg></button>
   139|        <button onclick="shareTo('telegram')" class="share-btn" title="${t('share_telegram', 'Share on Telegram')}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></button>
   140|      </div>
   141|    </article>`;
   142|  }
   143|
   144|  function renderMultiPersona(story) {
   145|    var mp = story.multi_persona;
   146|    if (!mp || !Object.keys(mp).length) return '';
   147|    var h = '<section class="intel-multi-persona">';
   148|    h += '<h2 class="intel-section-label">' + t('multi_persona_label', 'MULTI-PERSONA ANALYSIS') + '</h2>';
   149|    h += '<div class="persona-grid">';
   150|    if (mp.c_suite) {
   151|      var cs = mp.c_suite;
   152|      h += '<div class="persona-card persona-csuite">';
   153|      h += '<div class="persona-header"><span class="persona-icon">&#x1F3DB;</span><span class="persona-role">' + t('persona_csuite', 'C-SUITE') + '</span></div>';
   154|      h += '<div class="persona-headline">' + (cs.headline || '') + '</div>';
   155|      h += '<div class="persona-body">' + (cs.body || '') + '</div>';
   156|      if (cs.implication) h += '<div class="persona-implication"><span class="persona-imp-label">' + t('persona_implication', 'Board-level') + ':</span> ' + cs.implication + '</div>';
   157|      h += '</div>';
   158|    }
   159|    if (mp.quant) {
   160|      var q = mp.quant;
   161|      h += '<div class="persona-card persona-quant">';
   162|      h += '<div class="persona-header"><span class="persona-icon">&#x1F4CA;</span><span class="persona-role">' + t('persona_quant', 'QUANTITATIVE') + '</span></div>';
   163|      h += '<div class="persona-headline">' + (q.headline || '') + '</div>';
   164|      h += '<div class="persona-body">' + (q.body || '') + '</div>';
   165|      if (q.metrics) {
   166|        h += '<div class="persona-metrics">';
   167|        if (q.metrics.flow_direction) h += '<span class="persona-metric">' + q.metrics.flow_direction + '</span>';
   168|        if (q.metrics.asset_class) h += '<span class="persona-metric asset-tag">' + q.metrics.asset_class.toUpperCase() + '</span>';
   169|        h += '</div>';
   170|      }
   171|      h += '</div>';
   172|    }
   173|    if (mp.degen) {
   174|      var dg = mp.degen;
   175|      h += '<div class="persona-card persona-degen">';
   176|      h += '<div class="persona-header"><span class="persona-icon">&#x1F3AF;</span><span class="persona-role">' + t('persona_degen', 'EXECUTION') + '</span></div>';
   177|      h += '<div class="persona-headline">' + (dg.headline || '') + '</div>';
   178|      h += '<div class="persona-body">' + (dg.body || '') + '</div>';
   179|      if (dg.signal) {
   180|        var sig = dg.signal;
   181|        h += '<div class="persona-signal">';
   182|        h += '<span class="persona-sig-dir ' + (sig.direction || '').toLowerCase() + '">' + (sig.direction || '') + '</span>';
   183|        if (sig.conviction) h += '<span class="persona-sig-conviction">' + sig.conviction + '</span>';
   184|        if (sig.entry_zone && sig.entry_zone !== 'TBD' && sig.entry_zone !== 'awaiting review') h += '<span class="persona-sig-entry">Entry: ' + sig.entry_zone + '</span>';
   185|        h += '</div>';
   186|      }
   187|      h += '</div>';
   188|    }
   189|    h += '</div></section>';
   190|    return h;
   191|  }
   192|
   193|  function buildNav(storyId, allStories, currentIdx) {
   194|    const nav = document.getElementById('storyNav');
   195|    const pos = document.getElementById('storyPosition');
   196|    const next = document.getElementById('storyNext');
   197|    
   198|    pos.textContent = `Story ${currentIdx + 1} of ${allStories.length}`;
   199|    
   200|    if (currentIdx < allStories.length - 1) {
   201|      const ns = allStories[currentIdx + 1];
   202|      next.href = '?id=' + ns.story_id;
   203|      next.style.display = '';
   204|    } else {
   205|      next.style.display = 'none';
   206|    }
   207|    
   208|    nav.style.display = '';
   209|    document.title = (allStories[currentIdx].headline || 'Story') + ' — La Gazzetta di Kyiv';
   210|  }
   211|
   212|  async 
   213|// ═══════════════ v23.8: Gazzetta Namespace ═══════════════
   214|window.Gazzetta = window.Gazzetta || {};
   215|Gazzetta.Story = {};
   216|Gazzetta.Story.init = init;
   217|Gazzetta.Story.buildHTML = buildHTML;
   218|
   219|async function init() {
   220|    // Wait for i18n
   221|    if (window.i18n && !window.i18n._ready) {
   222|      await new Promise(r => { window.addEventListener('i18nReady', r, { once: true }); });
   223|    }
   224|
   225|    const storyId = getStoryId();
   226|    if (!storyId) {
   227|      document.getElementById('storyContent').innerHTML = '<p class="story-error">No story specified. <a href="./">Return to Dashboard</a></p>';
   228|      return;
   229|    }
   230|
   231|    // Load stories
   232|    const lang = window.i18n ? i18n.lang : 'en';
   233|    const dataPath = lang === 'ru' ? STORIES_RU_PATH : STORIES_PATH;
   234|    const data = await getJSON(dataPath, null);
   235|    
   236|    if (!data) {
   237|      document.getElementById('storyContent').innerHTML = '<p class="story-error">Failed to load stories. <a href="./">Return to Dashboard</a></p>';
   238|      return;
   239|    }
   240|
   241|    const stories = data.stories || [];
   242|    const allStories = data.lead ? [data.lead, ...stories] : stories;
   243|    const story = findStory(data, storyId);
   244|
   245|    if (!story) {
   246|      document.getElementById('storyContent').innerHTML = `<p class="story-error">Story not found. <a href="./">Return to Dashboard</a></p>`;
   247|      return;
   248|    }
   249|
   250|    const idx = allStories.findIndex(s => s.story_id === storyId);
   251|    
   252|    document.getElementById('storyContent').innerHTML = buildHTML(story, allStories, idx);
   253|    buildNav(storyId, allStories, idx);
   254|  }
   255|
   256|  // Share functions
   257|  window.copyStoryLink = function() {
   258|    navigator.clipboard.writeText(window.location.href).catch(() => {});
   259|  };
   260|  window.shareTo = function(platform) {
   261|    const url = encodeURIComponent(window.location.href);
   262|    const title = encodeURIComponent(document.title);
   263|    const maps = {
   264|      x: `https://x.com/intent/tweet?url=${url}&text=${title}`,
   265|      facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
   266|      telegram: `https://t.me/share/url?url=${url}&text=${title}`,
   267|    };
   268|    if (maps[platform]) window.open(maps[platform], '_blank');
   269|  };
   270|
   271|  // Start
   272|  if (document.readyState === 'loading') {
   273|    document.addEventListener('DOMContentLoaded', init);
   274|  } else {
   275|    init();
   276|  }
   277|})();
   278|
   279|
   280|// Export to namespace after definition
   281|if (typeof Gazzetta !== "undefined") { Gazzetta.Story.loaded = true; }