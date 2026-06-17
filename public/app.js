// app.js v2.0 — 6-container geopolitical intelligence dashboard
// Fetches stories.json → renders 6 collapsible containers → handles keyboard + ARIA

(function() {
  'use strict';

  const DATA_PATH = './data/stories.json';
  const MAX_CARDS_PER_CONTAINER = 5;

  // ── State ──
  let containersData = null;
  let expandedContainers = new Set(
    JSON.parse(localStorage.getItem('gazzetta_expanded') || '[]')
  );

  // ── Helpers ──
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return (ctx || document).querySelectorAll(sel); }

  function formatDate(ts) {
    if (!ts) return '';
    try {
      const d = new Date(ts);
      const months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
      return months[d.getUTCMonth()] + ' ' + d.getUTCDate();
    } catch { return ''; }
  }

  function escapeHTML(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function getSourceName(story) {
    if (story.source_name) return story.source_name;
    const url = story.source_url || '';
    try { return new URL(url).hostname.replace('www.',''); } catch { return ''; }
  }

  function getTierBadge(story) {
    const score = story.contradiction_score || 0;
    const tier = story.tier || '';
    if (score >= 67 || tier === 'CONTRADICTED') {
      return { cls: 'contradicted', label: 'MAX TENSION' };
    }
    if (score >= 34 || tier === 'DIVERGENT') {
      return { cls: 'divergent', label: 'HIGH TENSION' };
    }
    return { cls: 'aligned', label: 'BUILDING' };
  }

  // ── Story Card Renderer ──
  function renderStoryCard(story) {
    const badge = getTierBadge(story);
    const source = getSourceName(story);
    const date = formatDate(story.generated_at || story.date_published);
    const headline = story.headline || 'Untitled';
    const thesis = story.thesis || '';
    const sourceUrl = story.source_url || '';
    const tags = story.tags || [];

    let tagsHTML = '';
    if (tags.length > 0) {
      tagsHTML = '<div class="story-tags">' +
        tags.map(t => '<span class="tag tag-' + escapeHTML(t) + '">' + escapeHTML(t).replace(/-/g, ' ') + '</span>').join('') +
        '</div>';
    }

    let sourceHTML = '';
    if (source) {
      if (sourceUrl) {
        sourceHTML = '<span class="story-source">' +
          '<a href="' + escapeHTML(sourceUrl) + '" target="_blank" rel="noopener" class="source-link">' + 
          escapeHTML(source) + '</a></span>';
      } else {
        sourceHTML = '<span class="story-source">' + escapeHTML(source) + '</span>';
      }
    }

    let metaHTML = [date, sourceHTML].filter(Boolean).join(' · ');

    return '' +
      '<article class="story-card">' +
        '<div class="story-card-header">' +
          '<span class="story-meta">' + metaHTML + '</span>' +
          '<span class="tier-badge tier-' + badge.cls + '">' + badge.label + '</span>' +
        '</div>' +
        '<h3 class="story-headline">' + escapeHTML(headline) + '</h3>' +
        (thesis ? '<p class="story-thesis">' + escapeHTML(thesis) + '</p>' : '') +
        tagsHTML +
      '</article>';
  }

  // ── Container Renderer ──
  function populateContainer(containerName, containerData) {
    const el = document.querySelector('[data-container="' + containerName + '"]');
    if (!el) return;

    const count = containerData.count || 0;
    const stories = containerData.stories || [];

    // Update count badge
    const countEl = el.querySelector('.container-count');
    if (countEl) {
      countEl.textContent = count === 0 ? 'No stories yet' : count + ' stories';
    }

    // Render story cards
    const body = el.querySelector('.container-body');
    if (!body) return;

    const displayStories = stories.slice(0, MAX_CARDS_PER_CONTAINER);

    if (displayStories.length === 0) {
      body.innerHTML = '<div class="container-empty">' +
        '<p>No stories in this domain yet.</p>' +
        '<p class="empty-hint">Send a link to seed this container.</p>' +
        '</div>';
    } else {
      body.innerHTML = displayStories.map(renderStoryCard).join('');

      // "View all" link if more stories exist
      if (stories.length > MAX_CARDS_PER_CONTAINER) {
        const viewAll = document.createElement('div');
        viewAll.className = 'view-all';
        viewAll.innerHTML = '<a href="./archive.html?container=' + containerName + '">' +
          'View all ' + stories.length + ' stories in ' + containerData.title + ' →</a>';
        body.appendChild(viewAll);
      }
    }

    // Restore expanded state
    if (expandedContainers.has(containerName)) {
      el.classList.add('expanded');
      const header = el.querySelector('.container-header');
      if (header) header.setAttribute('aria-expanded', 'true');
    }
  }

  // ── Expand/Collapse Handler ──
  function setupContainerToggle(el) {
    const header = el.querySelector('.container-header');
    if (!header) return;

    header.addEventListener('click', () => {
      const isExpanded = el.classList.toggle('expanded');
      header.setAttribute('aria-expanded', String(isExpanded));

      const containerName = el.getAttribute('data-container');
      if (containerName) {
        if (isExpanded) {
          expandedContainers.add(containerName);
        } else {
          expandedContainers.delete(containerName);
        }
        localStorage.setItem('gazzetta_expanded', JSON.stringify([...expandedContainers]));
      }
    });

    // Keyboard support
    header.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        header.click();
      }
    });
  }

  // ── Data Fetch ──
  async function loadData() {
    try {
      const resp = await fetch(DATA_PATH + '?t=' + Date.now(), { cache: 'no-store' });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const data = await resp.json();
      containersData = data.containers || {};
      return true;
    } catch (err) {
      console.warn('Gazzetta: failed to load stories.json', err);
      // Show error state in each container
      $$('.container-count').forEach(el => { el.textContent = '—'; });
      return false;
    }
  }

  // ── Init ──
  async function init() {
    const ok = await loadData();
    if (!ok) return;

    // Populate all 6 containers
    const containerNames = [
      'monetary_order', 'energy_resources', 'technology_ai',
      'information_narrative', 'biosecurity_health', 'flashpoints'
    ];

    for (const name of containerNames) {
      const data = containersData[name];
      if (data) {
        populateContainer(name, data);
      }
    }

    // Setup toggle handlers for ALL containers (including empty ones)
    $$('.narrative-container').forEach(setupContainerToggle);

    // Default: expand first non-empty container on first visit
    const hasVisited = localStorage.getItem('gazzetta_visited');
    if (!hasVisited) {
      for (const name of containerNames) {
        const data = containersData[name];
        if (data && data.count > 0) {
          const el = document.querySelector('[data-container="' + name + '"]');
          if (el && !el.classList.contains('expanded')) {
            el.classList.add('expanded');
            const header = el.querySelector('.container-header');
            if (header) header.setAttribute('aria-expanded', 'true');
            expandedContainers.add(name);
            localStorage.setItem('gazzetta_expanded', JSON.stringify([...expandedContainers]));
            localStorage.setItem('gazzetta_visited', '1');
            break;
          }
        }
      }
    }

    console.log('Gazzetta v2.0 — ' + (data.all_stories ? data.all_stories.length : '?') + ' stories loaded');
  }

  // ── Start ──
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
