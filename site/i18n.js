// i18n.js — Lightweight internationalization for Gazzetta di Kyiv
// Supports: en (default, built into HTML) and ru (loaded from i18n_ru.json)
// Usage: add data-i18n="key" to any element needing translation

(function() {
  'use strict';

  const SUPPORTED = ['en', 'ru'];
  const STORAGE_KEY = 'gazzetta_lang';
  let currentLang = 'en';
  let translations = {};

  // Detect language: localStorage > browser > default en
  function detectLang() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && SUPPORTED.includes(stored)) return stored;
    const browser = (navigator.language || '').split('-')[0];
    if (browser === 'ru') return 'ru';
    return 'en';
  }

  // Load translations JSON
  async function loadTranslations(lang) {
    if (lang === 'en') {
      translations = {};
      return;
    }
    try {
      const resp = await fetch(`./i18n_${lang}.json?t=${Date.now()}`, { cache: 'no-store' });
      if (resp.ok) {
        translations = await resp.json();
      }
    } catch (e) {
      console.warn('i18n: failed to load translations for', lang);
    }
  }

  // Apply translations to DOM
  function applyTranslations() {
    document.documentElement.lang = currentLang;

    // Elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (translations[key]) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = translations[key];
        } else {
          el.textContent = translations[key];
        }
      }
    });

    // Title and meta
    if (translations.site_title) {
      document.title = translations.site_title;
    }
    if (translations.site_description) {
      const meta = document.querySelector('meta[name="description"]');
      if (meta) meta.content = translations.site_description;
    }

    // Update language switcher
    document.querySelectorAll('.lang-switch').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-lang') === currentLang);
    });
  }

  // Switch language
  async function switchLang(lang) {
    if (!SUPPORTED.includes(lang) || lang === currentLang) return;
    currentLang = lang;
    localStorage.setItem(STORAGE_KEY, lang);
    await loadTranslations(lang);
    applyTranslations();
    // Dispatch event so app.js can reload data
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
    // Reload page to pick up language-specific data files
    // Store current language so app.js can detect it on reload
    localStorage.setItem('gazzetta_lang', lang);
    setTimeout(() => location.reload(), 200);
  }

  // Public API
  window.i18n = {
    get lang() { return currentLang; },
    get translations() { return translations; },
    t: function(key, fallback) { return translations[key] || fallback || key; },
    switchLang: switchLang,
    _ready: false,
    init: async function() {
      currentLang = detectLang();
      await loadTranslations(currentLang);
      applyTranslations();
      // Signal that i18n is ready
      window.i18n._ready = true;
      window.dispatchEvent(new Event('i18nReady'));
    }
  };
})();
