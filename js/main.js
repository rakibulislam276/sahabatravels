/*!
 * Sahaba Travels & Forex — site behaviour (no dependencies)
 */
(() => {
  'use strict';

  /* ------------------------------------------------------------------ CONFIG
   * formEndpoint: paste your Formspree (or Web3Forms/Getform) URL to receive
   *   form submissions by email, e.g. 'https://formspree.io/f/abcdwxyz'.
   *   Left empty, forms open WhatsApp with the details pre-filled instead.
   * googlePlaceId: from Google Business Profile → enables the "Write a review" link.
   */
  const CONFIG = {
    whatsapp: '919769047633',
    formEndpoint: '',
    googlePlaceId: '',
    requestTimeoutMs: 12000,
  };

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
  const t = (key) => (window.SahabaI18n ? window.SahabaI18n.t(key) : key);
  const root = document.documentElement;
  root.classList.add('js');

  const storage = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
  };

  /* ------------------------------------------------------------------ toast */
  const toastEl = $('#toast');
  let toastTimer;
  const toast = (msg) => {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('show'), 3200);
  };

  /* ------------------------------------------------------------------ theme */
  const themeBtn = $('#themeBtn');
  const metaTheme = $('meta[name="theme-color"]');
  const syncThemeUi = () => {
    const dark = root.dataset.theme === 'dark';
    if (themeBtn) {
      themeBtn.setAttribute('aria-label', t(dark ? 'js.toLight' : 'js.toDark'));
      themeBtn.setAttribute('aria-pressed', String(dark));
    }
    if (metaTheme) metaTheme.content = dark ? '#0a1230' : '#13235b';
  };
  if (!root.dataset.theme) root.dataset.theme = 'light';
  syncThemeUi();
  themeBtn?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    storage.set('st-theme', root.dataset.theme);
    syncThemeUi();
  });
  document.addEventListener('langchange', syncThemeUi);

  /* ------------------------------------------------------------------ language menu */
  const langBtn = $('#langBtn');
  const langMenu = $('#langMenu');
  const closeLang = (focusBtn = false) => {
    if (!langMenu || langMenu.hidden) return;
    langMenu.hidden = true;
    langBtn.setAttribute('aria-expanded', 'false');
    if (focusBtn) langBtn.focus();
  };
  if (langBtn && langMenu) {
    langBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = langMenu.hidden;
      langMenu.hidden = !open;
      langBtn.setAttribute('aria-expanded', String(open));
      if (open) ($('[aria-checked="true"]', langMenu) || $('button', langMenu)).focus();
    });
    langMenu.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-lang]');
      if (!btn) return;
      window.SahabaI18n?.set(btn.dataset.lang);
      closeLang(true);
    });
    langMenu.addEventListener('keydown', (e) => {
      const items = $$('button', langMenu);
      const i = items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); items[(i + 1) % items.length].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
      if (e.key === 'Escape') closeLang(true);
      if (e.key === 'Tab') closeLang();
    });
    document.addEventListener('click', (e) => { if (!e.target.closest('.lang-switch')) closeLang(); });
  }

  /* ------------------------------------------------------------------ mobile menu */
  const hamburger = $('#hamburger');
  const mobileMenu = $('#mobileMenu');
  const setMenu = (open) => {
    if (!mobileMenu) return;
    mobileMenu.classList.toggle('open', open);
    mobileMenu.setAttribute('aria-hidden', String(!open));
    hamburger?.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) $('.mobile-close', mobileMenu)?.focus();
    else hamburger?.focus({ preventScroll: true });
  };
  hamburger?.addEventListener('click', () => setMenu(true));
  $('#mobileClose')?.addEventListener('click', () => setMenu(false));
  mobileMenu?.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileMenu?.classList.contains('open')) setMenu(false);
  });
  matchMedia('(min-width: 1025px)').addEventListener?.('change', (e) => { if (e.matches) setMenu(false); });

  /* ------------------------------------------------------------------ scroll: navbar shadow + back-to-top */
  const navbar = $('#navbar');
  const backToTop = $('#backToTop');
  let ticking = false;
  const onScroll = () => {
    const y = window.scrollY;
    navbar?.classList.toggle('scrolled', y > 40);
    backToTop?.classList.toggle('show', y > 700);
    ticking = false;
  };
  window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
  backToTop?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  /* ------------------------------------------------------------------ reveal on scroll */
  const reveals = $$('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('visible'));
  }

  /* ------------------------------------------------------------------ scroll-spy (home nav + package tabs) */
  const spy = (links) => {
    const map = new Map();
    links.forEach((a) => {
      const id = a.getAttribute('href').split('#')[1];
      const sec = id && document.getElementById(id);
      if (sec) map.set(sec, a);
    });
    if (!map.size || !('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        links.forEach((l) => { l.classList.remove('active'); l.removeAttribute('aria-current'); });
        const a = map.get(en.target);
        a.classList.add('active');
        a.setAttribute('aria-current', 'location');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    map.forEach((_, sec) => io.observe(sec));
  };
  if (document.body.classList.contains('page-home')) spy($$('.nav-links a[href^="#"]'));
  spy($$('.pkg-tabs a'));

  /* ------------------------------------------------------------------ search tabs (WAI-ARIA tabs) */
  const tabs = $$('.search-tab');
  const selectTab = (tab, focus = false) => {
    tabs.forEach((tb) => {
      const on = tb === tab;
      tb.classList.toggle('active', on);
      tb.setAttribute('aria-selected', String(on));
      tb.tabIndex = on ? 0 : -1;
      const panel = document.getElementById(tb.getAttribute('aria-controls'));
      if (panel) { panel.hidden = !on; panel.classList.toggle('active', on); }
    });
    if (focus) tab.focus();
  };
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => selectTab(tab));
    tab.addEventListener('keydown', (e) => {
      const dir = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (!dir) return;
      e.preventDefault();
      const rtl = root.dir === 'rtl' ? -1 : 1;
      selectTab(tabs[(i + dir * rtl + tabs.length) % tabs.length], true);
    });
  });
  // sensible minimum dates
  const today = new Date().toISOString().slice(0, 10);
  $$('input[type="date"]').forEach((d) => { d.min = today; });

  /* ------------------------------------------------------------------ package filters */
  $$('.filter-bar').forEach((bar) => {
    const grid = bar.parentElement.querySelector('[data-filter-grid]');
    if (!grid) return;
    bar.addEventListener('click', (e) => {
      const chip = e.target.closest('.chip');
      if (!chip) return;
      $$('.chip', bar).forEach((c) => { c.classList.toggle('active', c === chip); c.setAttribute('aria-pressed', String(c === chip)); });
      const f = chip.dataset.filter;
      $$('.package-card', grid).forEach((card) => card.classList.toggle('is-hidden', f !== 'all' && card.dataset.kind !== f));
    });
  });

  /* ------------------------------------------------------------------ "Plan Your Trip" prefill */
  document.addEventListener('click', (e) => {
    const link = e.target.closest('[data-plan]');
    if (!link) return;
    const name = link.dataset.plan;
    const contact = $('#contactForm');
    const enquiry = $('#enquire');
    if (contact) {
      const service = $('#cf-service');
      const msg = $('#cf-msg');
      const lower = name.toLowerCase();
      if (service) {
        const match = [...service.options].find((o) => o.text === name) || [...service.options].find((o) =>
          (lower.includes('umrah') && o.text.includes('Umrah')) || (lower.includes('hajj') && o.text.includes('Hajj')) ||
          (lower.includes('forex') && o.text.includes('Forex')));
        service.value = match ? match.value || match.text : 'Holiday Package';
      }
      const isService = link.classList.contains('service-link');
      if (msg && !isService && !msg.value.includes(name) && !lower.includes('forex')) msg.value = `I'm interested in: ${name}\n${msg.value}`.trim();
      // let the anchor scroll, then focus the first field
      setTimeout(() => $('#cf-first')?.focus({ preventScroll: true }), 600);
    } else if (enquiry) {
      setTimeout(() => $('#eq-name')?.focus({ preventScroll: true }), 500);
    }
  });

  /* ------------------------------------------------------------------ forms */
  const fetchWithTimeout = async (url, opts = {}) => {
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), CONFIG.requestTimeoutMs);
    try {
      return await fetch(url, { ...opts, signal: ctrl.signal });
    } finally {
      clearTimeout(id);
    }
  };

  const formToLines = (form, data) => {
    const lines = [];
    for (const [k, v] of data.entries()) {
      if (k.startsWith('_') || !String(v).trim()) continue;
      const field = form.elements[k];
      const label = form.dataset.form === 'feedback' ? k.replace(/_/g, ' ') : (field?.labels?.[0]?.textContent.trim() || k.replace(/_/g, ' '));
      lines.push(`${label}: ${v}`);
    }
    return lines;
  };

  const validate = (form) => {
    let firstBad = null;
    $$('input, select, textarea', form).forEach((f) => {
      if (f.classList.contains('hp') || f.type === 'hidden') return;
      const ok = f.checkValidity();
      f.setAttribute('aria-invalid', String(!ok));
      if (!ok && !firstBad) firstBad = f;
    });
    if (firstBad) firstBad.focus();
    return !firstBad;
  };

  const setStatus = (form, msg, type) => {
    let el = $('.form-status', form);
    if (!el) {
      el = document.createElement('p');
      el.className = 'form-status';
      el.setAttribute('role', 'status');
      form.append(el);
    }
    el.className = `form-status${type ? ` is-${type}` : ''}`;
    el.textContent = msg;
    return el;
  };

  const openWhatsApp = (text) => {
    const url = `https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(text)}`;
    // A synthetic anchor click opens a new tab without being treated as a popup
    const a = Object.assign(document.createElement('a'), { href: url, target: '_blank', rel: 'noopener' });
    document.body.append(a);
    a.click();
    a.remove();
    return url;
  };

  const handleSubmit = async (e) => {
    const form = e.target.closest('form[data-form]');
    if (!form) return;
    e.preventDefault();
    if (form.elements._gotcha?.value) return; // bot
    if (!validate(form)) { setStatus(form, t('js.invalid'), 'error'); return; }

    const data = new FormData(form);
    const subject = form.dataset.subject || (form.dataset.form === 'enquiry' ? `Package enquiry: ${data.get('package')}` : 'Website enquiry');
    const lines = formToLines(form, data);
    const waText = `Hello Sahaba Travels,\n${subject}\n\n${lines.join('\n')}`;
    const btn = $('button[type="submit"]', form);
    const btnHtml = btn?.innerHTML;

    // Search widget & no endpoint configured → WhatsApp hand-off
    if (!CONFIG.formEndpoint || form.dataset.form === 'search' || form.dataset.form === 'feedback') {
      openWhatsApp(waText);
      setStatus(form, t('js.waOpened'), 'success');
      if (form.dataset.form !== 'search') toast(t('js.waOpened'));
      return;
    }

    try {
      if (btn) { btn.disabled = true; btn.textContent = t('js.sending'); }
      data.append('_subject', subject);
      data.append('page', location.href);
      const res = await fetchWithTimeout(CONFIG.formEndpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      form.reset();
      $$('[aria-invalid]', form).forEach((f) => f.removeAttribute('aria-invalid'));
      setStatus(form, t('js.sent'), 'success');
      toast(t('js.sent'));
    } catch {
      const el = setStatus(form, `${t('js.error')} `, 'error');
      const a = document.createElement('a');
      a.href = `https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(waText)}`;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = 'WhatsApp →';
      el.append(a);
    } finally {
      if (btn) { btn.disabled = false; btn.innerHTML = btnHtml; }
    }
  };
  document.addEventListener('submit', handleSubmit);
  document.addEventListener('input', (e) => {
    if (e.target.getAttribute?.('aria-invalid') === 'true' && e.target.checkValidity()) e.target.setAttribute('aria-invalid', 'false');
  });

  /* ------------------------------------------------------------------ FAQ: only one open at a time
   * (native <details name> handles this in modern browsers; this covers older ones) */
  document.addEventListener('toggle', (e) => {
    const d = e.target;
    if (!(d instanceof HTMLDetailsElement) || !d.open || !d.classList.contains('faq-item')) return;
    d.closest('.faq-list')?.querySelectorAll('details.faq-item[open]').forEach((o) => { if (o !== d) o.open = false; });
  }, true);

  /* ------------------------------------------------------------------ itinerary: expand/collapse, share, print */
  const dayDetails = $$('.timeline details');
  const toggleDays = $('#toggleDays');
  const allOpen = () => dayDetails.every((d) => d.open);
  const syncToggle = () => { if (toggleDays) toggleDays.textContent = t(allOpen() ? 'js.collapse' : 'js.expand'); };
  toggleDays?.addEventListener('click', () => {
    const open = !allOpen();
    dayDetails.forEach((d) => { d.open = open; });
    syncToggle();
  });
  dayDetails.forEach((d) => d.addEventListener('toggle', syncToggle));
  document.addEventListener('langchange', syncToggle);

  let openedForPrint = [];
  window.addEventListener('beforeprint', () => {
    openedForPrint = dayDetails.filter((d) => !d.open);
    openedForPrint.forEach((d) => { d.open = true; });
  });
  window.addEventListener('afterprint', () => { openedForPrint.forEach((d) => { d.open = false; }); });

  const copyText = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      const ta = Object.assign(document.createElement('textarea'), { value: text });
      ta.style.cssText = 'position:fixed;opacity:0';
      document.body.append(ta);
      ta.select();
      const ok = document.execCommand?.('copy');
      ta.remove();
      return Boolean(ok);
    }
  };

  const nativeShare = $('[data-action="share"]');
  if (nativeShare && navigator.share) nativeShare.hidden = false;

  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const action = btn.dataset.action;
    if (action === 'print') {
      window.print();
    } else if (action === 'copy') {
      toast(t((await copyText(btn.dataset.url || location.href)) ? 'js.copied' : 'js.copyFail'));
    } else if (action === 'share') {
      try { await navigator.share({ title: btn.dataset.title || document.title, url: btn.dataset.url || location.href }); } catch { /* cancelled */ }
    }
  });

  /* ------------------------------------------------------------------ gallery lightbox */
  const lightbox = $('#lightbox');
  if (lightbox && typeof lightbox.showModal === 'function') {
    const img = $('img', lightbox);
    document.addEventListener('click', (e) => {
      const item = e.target.closest('.gallery-item');
      if (!item) return;
      img.src = item.dataset.full;
      img.alt = item.dataset.alt || '';
      lightbox.showModal();
    });
    $('.lightbox-close', lightbox).addEventListener('click', () => lightbox.close());
    lightbox.addEventListener('click', (e) => { if (e.target === lightbox) lightbox.close(); });
  } else {
    $$('.gallery-item').forEach((b) => b.addEventListener('click', () => window.open(b.dataset.full, '_blank', 'noopener')));
  }

  /* ------------------------------------------------------------------ open-now badge (Asia/Kolkata) */
  const openNow = $('#openNow');
  const updateOpenNow = () => {
    if (!openNow) return;
    try {
      const parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Kolkata', weekday: 'short', hour: 'numeric', minute: 'numeric', hourCycle: 'h23' }).formatToParts(new Date());
      const get = (type) => parts.find((p) => p.type === type)?.value;
      const day = get('weekday');
      const mins = Number(get('hour')) * 60 + Number(get('minute'));
      const closeAt = day === 'Sat' ? 18 * 60 : 21 * 60;
      const open = day !== 'Sun' && mins >= 10 * 60 && mins < closeAt;
      openNow.hidden = false;
      openNow.className = `open-now ${open ? 'is-open' : 'is-closed'}`;
      openNow.textContent = `● ${t(open ? 'js.openNow' : 'js.closedNow')}`;
    } catch { /* Intl unsupported */ }
  };
  updateOpenNow();
  setInterval(updateOpenNow, 60000);
  document.addEventListener('langchange', updateOpenNow);

  /* ------------------------------------------------------------------ welcome flyer (first visit only) */
  const flyer = $('#flyer');
  const FLYER_KEY = 'st-flyer-v1';
  const flyerSeen = () => { try { return localStorage.getItem(FLYER_KEY) || sessionStorage.getItem(FLYER_KEY); } catch { return null; } };
  const markFlyer = () => { try { localStorage.setItem(FLYER_KEY, String(Date.now())); sessionStorage.setItem(FLYER_KEY, '1'); } catch { /* ignore */ } };
  if (flyer && typeof flyer.showModal === 'function' && !flyerSeen() && !/bot|crawl|spider|lighthouse/i.test(navigator.userAgent)) {
    setTimeout(() => {
      if (document.querySelector('dialog[open]')) return;
      flyer.showModal();
      markFlyer();
    }, 2500);
    flyer.addEventListener('click', (e) => {
      if (e.target === flyer || e.target.closest('[data-close-flyer]')) flyer.close();
    });
    flyer.addEventListener('close', markFlyer);
  }

  /* ------------------------------------------------------------------ visa page: filter, search, prefill */
  const visaGrid = $('#visaGrid');
  if (visaGrid) {
    const cards = $$('.visa-card', visaGrid);
    const search = $('#visaSearch');
    const countEl = $('#visaCount');
    const empty = $('#visaEmpty');
    let type = 'all';
    const apply = () => {
      const q = (search?.value || '').trim().toLowerCase();
      let shown = 0;
      cards.forEach((c) => {
        const ok = (type === 'all' || c.dataset.type === type) && (!q || c.dataset.name.includes(q));
        c.hidden = !ok;
        if (ok) shown += 1;
      });
      if (countEl) countEl.textContent = `${shown} ${shown === 1 ? 'destination' : 'destinations'}`;
      if (empty) empty.hidden = shown > 0;
    };
    $$('[data-visa-filter]').forEach((chip) => chip.addEventListener('click', () => {
      type = chip.dataset.visaFilter;
      $$('[data-visa-filter]').forEach((c) => { c.classList.toggle('active', c === chip); c.setAttribute('aria-pressed', String(c === chip)); });
      apply();
    }));
    search?.addEventListener('input', apply);
    $('#visaClear')?.addEventListener('click', () => { if (search) search.value = ''; apply(); search?.focus(); });
  }
  document.addEventListener('click', (e) => {
    const link = e.target.closest('[data-visa]');
    const sel = $('#va-country');
    if (!link || !sel) return;
    const opt = [...sel.options].find((o) => o.text === link.dataset.visa);
    if (opt) sel.value = opt.value || opt.text;
    setTimeout(() => $('#va-first')?.focus({ preventScroll: true }), 600);
  });

  /* ------------------------------------------------------------------ misc */
  $$('[data-year]').forEach((el) => { el.textContent = String(new Date().getFullYear()); });
  if (CONFIG.googlePlaceId) {
    const w = $('#gWriteLink');
    const r = $('#gReadLink');
    if (w) w.href = `https://search.google.com/local/writereview?placeid=${encodeURIComponent(CONFIG.googlePlaceId)}`;
    if (r) r.href = `https://search.google.com/local/reviews?placeid=${encodeURIComponent(CONFIG.googlePlaceId)}`;
  }
})();
