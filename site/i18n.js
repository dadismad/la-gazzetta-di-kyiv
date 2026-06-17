// i18n.js — Gazzetta di Kyiv Localization Engine v2.0
// Dynamic JSON-based dictionary system. Fetches locale files on demand.
// Supports EN and RU. Language swap WITHOUT page reload.
(function() {
  'use strict';

  const LOCALE_PATH = './data/locales/';
  const SUPPORTED = ['en', 'ru'];
  const STORAGE_KEY = 'gazzetta_lang';

  let currentLang = 'en';
  let translations = {};

  // ── Detect stored preference or browser default ──
  function detectLang() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && SUPPORTED.includes(stored)) return stored;
    const browser = (navigator.language || 'en').split('-')[0];
    return SUPPORTED.includes(browser) ? browser : 'en';
  }

  // ── Fetch locale JSON ──
  async function loadLocale(lang) {
    try {
      const resp = await fetch(`${LOCALE_PATH}${lang}.json?t=${Date.now()}`, { cache: 'no-store' });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      translations = data.strings || {};
      currentLang = lang;
      localStorage.setItem(STORAGE_KEY, lang);
      document.documentElement.lang = lang;
      return true;
    } catch (e) {
      console.warn(`i18n: Failed to load ${lang} locale —`, e.message);
      if (lang !== 'en') {
        // Fallback to English
        return loadLocale('en');
      }
      return false;
    }
  }

  // ── Apply translations to DOM ──
  function applyToDOM() {
    // 1. data-i18n attributes → textContent
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (key && translations[key]) {
        // Only update if the element hasn't been dynamically modified
        if (!el.dataset.i18nDynamic || el.dataset.i18nDynamic === 'true') {
          el.textContent = translations[key];
        }
      }
    });

    // 2. data-i18n-placeholder → input placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (key && translations[key]) {
        el.placeholder = translations[key];
      }
    });

    // 3. data-i18n-title → title attributes
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      if (key && translations[key]) {
        el.title = translations[key];
      }
    });

    // Dispatch event so app.js can re-render i18n-dependent dynamic content
    window.dispatchEvent(new CustomEvent('i18nApplied', { detail: { lang: currentLang } }));
  }

  // ── Public API ──
  window.i18n = {
    get lang() { return currentLang; },
    get ready() { return window.i18n._ready; },

    // Translate a key — for JS usage (app.js i18n.t calls)
    t: function(key, fallback) {
      return translations[key] || fallback || key;
    },

    // Get list of available languages
    getLanguages: function() {
      return SUPPORTED.map(code => ({
        code: code,
        name: code === 'en' ? 'English' : code === 'ru' ? 'Русский' : code
      }));
    },

    // Switch language — returns Promise<true|false>
    switchTo: async function(lang) {
      if (!SUPPORTED.includes(lang)) {
        console.warn(`i18n: Unsupported language "${lang}"`);
        return false;
      }
      if (lang === currentLang) return true;

      const success = await loadLocale(lang);
      if (success) {
        applyToDOM();
        window.dispatchEvent(new Event('i18nReady'));
      }
      return success;
    },

    // Apply translations to dynamically inserted DOM (called by app.js after innerHTML)
    applyTranslations: function(rootEl) {
      const scope = rootEl || document;
      scope.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (key && translations[key]) {
          el.textContent = translations[key];
          el.dataset.i18nDynamic = 'true';
        }
      });
    },

    // Initialize — load detected locale and apply
    init: async function() {
      const lang = detectLang();
      await loadLocale(lang);
      applyToDOM();
      window.i18n._ready = true;
      window.dispatchEvent(new Event('i18nReady'));
    }
  };

  // ── Auto-initialize ──
  window.i18n.init();

  // ── Language toggle helper — creates a small UI element ──
  // Pages can include: <div id="langToggle"></div>
  // i18n will populate it with EN | RU buttons
  document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('langToggle');
    if (toggle && !toggle.dataset.wired) {
      toggle.dataset.wired = 'true';
      toggle.innerHTML = SUPPORTED.map(code => {
        const active = code === currentLang ? ' lang-active' : '';
        return `<button class="lang-btn${active}" data-lang="${code}" style="background:none;border:1px solid var(--divider);padding:2px 8px;cursor:pointer;font-size:11px;font-family:Inter,sans-serif;color:var(--ink);margin:0 2px;">${code.toUpperCase()}</button>`;
      }).join('');

      toggle.addEventListener('click', async function(e) {
        const btn = e.target.closest('[data-lang]');
        if (!btn) return;
        const lang = btn.getAttribute('data-lang');
        await window.i18n.switchTo(lang);
        // Update active button
        toggle.querySelectorAll('.lang-btn').forEach(b => {
          b.classList.toggle('lang-active', b.getAttribute('data-lang') === lang);
          b.style.fontWeight = b.getAttribute('data-lang') === lang ? '700' : '400';
        });
      });
    }
  });
})();
