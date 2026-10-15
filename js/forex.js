/*!
 * Sahaba Travels — Forex rates table + converter
 *
 *  BUY  = live market rate (INR per unit) from free, CORS-enabled APIs.
 *  SELL = your own rate, read from /data/forex-rates.xlsx (edit in Excel, upload, done).
 *
 *  To swap the logic (sell live / buy from Excel), set BUY_SOURCE / SELL_SOURCE below.
 */
(() => {
  'use strict';

  const tbody = document.getElementById('ratesBody');
  if (!tbody) return;

  const CONFIG = {
    BUY_SOURCE: 'live',   // 'live' | 'excel'
    SELL_SOURCE: 'excel', // 'live' | 'excel'
    BUY_MARGIN_PCT: 0,    // optional: subtract % from live market rate for the Buy column (e.g. 0.5)
    EXCEL_URL: new URL('../data/forex-rates.xlsx', document.currentScript?.src || location.href).href,
    SHEETJS_URL: 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js',
    REFRESH_MS: 5 * 60 * 1000,
    CACHE_MS: 10 * 60 * 1000,
    TIMEOUT_MS: 10000,
  };

  // code, name, symbol, flag (ISO-3166 for flagcdn), unit shown
  const CURRENCIES = [
    ['USD', 'US Dollar', '$', 'us', 1],
    ['EUR', 'Euro', '€', 'eu', 1],
    ['GBP', 'British Pound', '£', 'gb', 1],
    ['SAR', 'Saudi Riyal', '﷼', 'sa', 1],
    ['AED', 'UAE Dirham', 'د.إ', 'ae', 1],
    ['QAR', 'Qatari Riyal', 'ر.ق', 'qa', 1],
    ['KWD', 'Kuwaiti Dinar', 'د.ك', 'kw', 1],
    ['OMR', 'Omani Rial', 'ر.ع.', 'om', 1],
    ['BHD', 'Bahraini Dinar', '.د.ب', 'bh', 1],
    ['MYR', 'Malaysian Ringgit', 'RM', 'my', 1],
    ['SGD', 'Singapore Dollar', 'S$', 'sg', 1],
    ['THB', 'Thai Baht', '฿', 'th', 1],
    ['TRY', 'Turkish Lira', '₺', 'tr', 1],
    ['AUD', 'Australian Dollar', 'A$', 'au', 1],
    ['CAD', 'Canadian Dollar', 'C$', 'ca', 1],
    ['CHF', 'Swiss Franc', 'Fr', 'ch', 1],
    ['JPY', 'Japanese Yen', '¥', 'jp', 100],
  ].map(([code, name, symbol, flag, unit]) => ({ code, name, symbol, flag, unit }));

  const t = (k) => (window.SahabaI18n ? window.SahabaI18n.t(k) : k);
  const statusEl = document.getElementById('fxStatus');
  const updatedEl = document.getElementById('fxUpdated');
  const fmt = (n) => (Number.isFinite(n) ? n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '—');

  const state = { market: null, prev: null, excel: null, updatedAt: null, source: '', failed: false };

  const fetchJson = async (url) => {
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), CONFIG.TIMEOUT_MS);
    try {
      const res = await fetch(url, { signal: ctrl.signal, cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } finally {
      clearTimeout(id);
    }
  };

  /** Live market: returns { rates: {USD: inrPerUnit,...}, time, source } */
  const PROVIDERS = [
    async () => {
      const j = await fetchJson('https://open.er-api.com/v6/latest/INR');
      if (j.result !== 'success') throw new Error('provider error');
      return { perInr: j.rates, time: j.time_last_update_unix * 1000, source: 'ExchangeRate-API' };
    },
    async () => {
      const j = await fetchJson('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/inr.json');
      const perInr = Object.fromEntries(Object.entries(j.inr).map(([k, v]) => [k.toUpperCase(), v]));
      return { perInr, time: Date.parse(j.date), source: 'fawazahmed0 currency-api' };
    },
  ];

  const toInrPerUnit = (perInr) => {
    const out = {};
    CURRENCIES.forEach(({ code }) => { if (perInr[code] > 0) out[code] = 1 / perInr[code]; });
    return out;
  };

  const readCache = () => {
    try {
      const c = JSON.parse(localStorage.getItem('st-fx') || 'null');
      return c && Date.now() - c.fetchedAt < CONFIG.CACHE_MS ? c : null;
    } catch { return null; }
  };
  const writeCache = (data) => { try { localStorage.setItem('st-fx', JSON.stringify({ ...data, fetchedAt: Date.now() })); } catch { /* ignore */ } };

  const loadMarket = async ({ force = false } = {}) => {
    const cached = !force && readCache();
    if (cached) return cached;
    let lastErr;
    for (const p of PROVIDERS) {
      try {
        const r = await p();
        const data = { rates: toInrPerUnit(r.perInr), time: r.time, source: r.source };
        if (Object.keys(data.rates).length) { writeCache(data); return data; }
      } catch (err) { lastErr = err; }
    }
    throw lastErr || new Error('no provider');
  };

  /** Previous day's rates, for the 24h change column (best effort). */
  const loadPrevious = async () => {
    try {
      const d = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
      const j = await fetchJson(`https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@${d}/v1/currencies/inr.json`);
      const perInr = Object.fromEntries(Object.entries(j.inr).map(([k, v]) => [k.toUpperCase(), v]));
      return toInrPerUnit(perInr);
    } catch { return null; }
  };

  /** Excel: sheet with columns Code | ... | Sell Rate (INR) [| Buy Rate] */
  const loadScript = (src) => new Promise((resolve, reject) => {
    if (window.XLSX) return resolve();
    const s = document.createElement('script');
    s.src = src; s.async = true; s.crossOrigin = 'anonymous';
    s.onload = resolve; s.onerror = () => reject(new Error('SheetJS failed to load'));
    document.head.append(s);
  });

  const loadExcel = async () => {
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), CONFIG.TIMEOUT_MS);
    try {
      const [buf] = await Promise.all([
        fetch(`${CONFIG.EXCEL_URL}?v=${Math.floor(Date.now() / 6e4)}`, { signal: ctrl.signal }).then((r) => {
          if (!r.ok) throw new Error(`Excel HTTP ${r.status}`);
          return r.arrayBuffer();
        }),
        loadScript(CONFIG.SHEETJS_URL),
      ]);
      const wb = window.XLSX.read(buf, { type: 'array' });
      const sheet = wb.Sheets[wb.SheetNames[0]];
      const rows = window.XLSX.utils.sheet_to_json(sheet, { defval: '' });
      const out = { sell: {}, buy: {}, updated: '' };
      rows.forEach((row) => {
        const keys = Object.keys(row);
        const pick = (re) => row[keys.find((k) => re.test(k))];
        const code = String(pick(/^code$|currency code/i) || '').trim().toUpperCase();
        if (!/^[A-Z]{3}$/.test(code)) return;
        const sell = parseFloat(pick(/sell/i));
        const buy = parseFloat(pick(/buy/i));
        if (Number.isFinite(sell) && sell > 0) out.sell[code] = sell;
        if (Number.isFinite(buy) && buy > 0) out.buy[code] = buy;
        const upd = pick(/updated|date/i);
        if (upd && !out.updated) out.updated = upd instanceof Date ? upd.toLocaleDateString('en-IN') : String(upd);
      });
      return out;
    } finally {
      clearTimeout(id);
    }
  };

  /* ------------------------------------------------------------------ render */
  const buyRate = (c) => {
    if (CONFIG.BUY_SOURCE === 'excel') return state.excel?.buy[c.code];
    const m = state.market?.rates[c.code];
    return m ? m * c.unit * (1 - CONFIG.BUY_MARGIN_PCT / 100) : undefined;
  };
  const sellRate = (c) => {
    if (CONFIG.SELL_SOURCE === 'live') { const m = state.market?.rates[c.code]; return m ? m * c.unit : undefined; }
    return state.excel?.sell[c.code];
  };

  const changeCell = (c) => {
    const now = state.market?.rates[c.code];
    const prev = state.prev?.[c.code];
    if (!now || !prev) return '<span class="rate-flat">—</span>';
    const diff = (now - prev) * c.unit;
    const pct = ((now - prev) / prev) * 100;
    if (Math.abs(pct) < 0.005) return '<span class="rate-flat">0.00%</span>';
    const up = diff > 0;
    return `<span class="${up ? 'rate-up' : 'rate-down'}"><i class="fas fa-arrow-${up ? 'up' : 'down'}" aria-hidden="true"></i> ${Math.abs(pct).toFixed(2)}%</span>`;
  };

  let lastRendered = {};
  const render = () => {
    const rows = CURRENCIES.map((c) => {
      const b = buyRate(c);
      const s = sellRate(c);
      const changed = lastRendered[c.code] && lastRendered[c.code] !== fmt(b) ? ' rate-flash' : '';
      lastRendered[c.code] = fmt(b);
      return `<tr data-code="${c.code}">
        <td><div class="currency-cell">
          <img src="https://flagcdn.com/w40/${c.flag}.png" srcset="https://flagcdn.com/w80/${c.flag}.png 2x" width="28" height="20" alt="" loading="lazy" decoding="async">
          <div><span class="currency-code">${c.code}</span> <span class="currency-sym" aria-hidden="true">${c.symbol}</span>
          <span class="currency-name">${c.unit > 1 ? `${c.unit} ` : ''}${c.name}</span></div>
        </div></td>
        <td class="${changed.trim()}">${b ? `₹${fmt(b)}` : '—'}</td>
        <td>${s ? `₹${fmt(s)}` : `<small>${t('js.onRequest')}</small>`}</td>
        <td class="hide-xs">${changeCell(c)}</td>
      </tr>`;
    }).join('');
    tbody.innerHTML = rows;

    if (statusEl) {
      statusEl.classList.toggle('is-offline', state.failed);
      statusEl.innerHTML = `<span class="live-dot" aria-hidden="true"></span> ${t(state.failed ? 'js.offline' : 'js.live')}`;
    }
    if (updatedEl) {
      const parts = [];
      if (state.market) {
        const when = new Date(state.market.time).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Kolkata' });
        parts.push(`${t('fx.buy')}: ${t('js.updated')} ${when} IST · ${state.market.source}`);
      }
      if (state.excel?.updated) parts.push(`${t('fx.sell')}: ${t('js.updated')} ${state.excel.updated}`);
      if (state.failed) parts.push(t('js.ratesFail'));
      updatedEl.textContent = parts.join('  ·  ');
    }
    convert();
  };

  /* ------------------------------------------------------------------ converter */
  const cvAmt = document.getElementById('cv-amt');
  const cvCur = document.getElementById('cv-cur');
  const cvMode = document.getElementById('cv-mode');
  const cvOut = document.getElementById('cv-out');
  if (cvCur && !cvCur.options.length) {
    cvCur.innerHTML = CURRENCIES.map((c) => `<option value="${c.code}">${c.code} — ${c.name}</option>`).join('');
  }
  function convert() {
    if (!cvOut || !cvCur) return;
    const c = CURRENCIES.find((x) => x.code === cvCur.value);
    const amt = parseFloat(cvAmt.value);
    if (!c || !Number.isFinite(amt) || amt <= 0) { cvOut.textContent = '—'; return; }
    const mode = cvMode.value; // 'sell' = customer buys foreign currency (our sell rate)
    const rate = mode === 'sell' ? sellRate(c) : buyRate(c);
    if (!rate) { cvOut.textContent = `${t('js.onRequest')} — +91 97690 47633`; return; }
    const inr = (amt / c.unit) * rate;
    cvOut.textContent = `${amt.toLocaleString('en-IN')} ${c.code} = ₹${fmt(inr)}  (${t(mode === 'sell' ? 'js.youPay' : 'js.youGet')})`;
  }
  [cvAmt, cvCur, cvMode].forEach((el) => el?.addEventListener('input', convert));

  /* ------------------------------------------------------------------ boot */
  const refresh = async (force = false) => {
    try {
      state.market = await loadMarket({ force });
      state.failed = false;
    } catch {
      state.failed = !state.market;
    }
    render();
  };

  const start = async () => {
    const [marketRes, excelRes, prevRes] = await Promise.allSettled([loadMarket(), loadExcel(), loadPrevious()]);
    if (marketRes.status === 'fulfilled') state.market = marketRes.value; else state.failed = true;
    if (excelRes.status === 'fulfilled' && Object.keys(excelRes.value.sell).length) state.excel = excelRes.value;
    else if (window.SAHABA_FX_FALLBACK) state.excel = window.SAHABA_FX_FALLBACK; // copy generated from the Excel at build time
    if (prevRes.status === 'fulfilled') state.prev = prevRes.value;
    render();
  };

  // Load when the forex section approaches the viewport (saves requests on first paint)
  const section = document.getElementById('forex');
  let started = false;
  const go = () => { if (!started) { started = true; start(); } };
  if ('IntersectionObserver' in window && section) {
    const io = new IntersectionObserver((en) => { if (en.some((e) => e.isIntersecting)) { io.disconnect(); go(); } }, { rootMargin: '600px' });
    io.observe(section);
  } else { go(); }
  if (location.hash === '#forex') go();

  setInterval(() => { if (started && document.visibilityState === 'visible') refresh(true); }, CONFIG.REFRESH_MS);
  document.addEventListener('visibilitychange', () => { if (started && document.visibilityState === 'visible') refresh(); });
  document.addEventListener('langchange', () => { if (started) render(); });
})();
