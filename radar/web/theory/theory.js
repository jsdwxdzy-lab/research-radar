/* 理论地图 · 科研雷达 —— 页面交互
   个人记录只存在本机 localStorage（键 research-radar.theory.v1），不上传。 */
(() => {
  'use strict';
  const LS = 'research-radar.theory.v1';
  const RADAR_LS = 'research-radar.v1';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const body = document.body;
  const prefix = body.dataset.prefix || '';
  const INDEX = window.THEORY_INDEX || { nodes: [], paths: [] };
  const byId = Object.fromEntries(INDEX.nodes.map(n => [n.id, n]));

  // ---- store ---------------------------------------------------------------
  const blank = () => ({ version: 1, theme: '', thinking: '', recent: [], nodes: {}, railsOff: false });
  let store = blank();
  let storageOk = true;
  try {
    const raw = JSON.parse(localStorage.getItem(LS) || 'null');
    if (raw && typeof raw === 'object') store = Object.assign(blank(), raw);
  } catch { storageOk = false; }
  if (!store.nodes || typeof store.nodes !== 'object') store.nodes = {};
  if (!Array.isArray(store.recent)) store.recent = [];
  const save = () => {
    try { localStorage.setItem(LS, JSON.stringify(store)); return true; }
    catch { toast('浏览器不允许保存，记录不会保留。请先导出备份。'); return false; }
  };
  const nodeRec = id => (store.nodes[id] = Object.assign({ question: '', note: '', resolved: false, dims: {}, pos: '', updatedAt: '' }, store.nodes[id] || {}));

  let toastTimer;
  function toast(msg) {
    const t = $('#toast'); if (!t) return;
    t.textContent = msg; t.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => { t.hidden = true; }, 3200);
  }

  // ---- theme: own setting; falls back to the paper radar's choice (read only)
  function themePref() {
    if (store.theme) return store.theme;
    try { const r = JSON.parse(localStorage.getItem(RADAR_LS) || 'null'); if (r && ['light', 'dark', 'auto'].includes(r.theme)) return r.theme; } catch { }
    return 'auto';
  }
  const applyTheme = () => { document.documentElement.dataset.theme = themePref(); };
  applyTheme();

  // ---- math ----------------------------------------------------------------
  function renderMath() {
    if (!window.katex) return;
    $$('.math').forEach(el => {
      try {
        window.katex.render(el.dataset.tex || '', el, { displayMode: el.dataset.display === '1', throwOnError: false, output: 'htmlAndMathml' });
        el.classList.add('katex-done');
      } catch { /* leave the TeX source visible */ }
    });
  }

  // ---- search --------------------------------------------------------------
  const input = $('#theorySearch'), list = $('#searchResults');
  let hits = [], active = -1;
  function hl(s, q) {
    s = String(s || ''); const i = s.toLowerCase().indexOf(q);
    if (!q || i < 0) return esc(s);
    return esc(s.slice(0, i)) + '<mark>' + esc(s.slice(i, i + q.length)) + '</mark>' + esc(s.slice(i + q.length));
  }
  function snippet(s, q) {
    s = String(s || ''); const i = s.toLowerCase().indexOf(q);
    if (i < 0) return s.slice(0, 90);
    const a = Math.max(0, i - 30);
    return (a > 0 ? '…' : '') + s.slice(a, a + 100);
  }
  function search(q) {
    q = q.trim().toLowerCase();
    if (!q) return [];
    const out = [];
    for (const n of INDEX.nodes) {
      let score = 0;
      if (n.title.toLowerCase().includes(q)) score += 10;
      if ((n.purpose || '').toLowerCase().includes(q)) score += 4;
      if ((n.trunk || '').toLowerCase().includes(q)) score += 2;
      if ((n.text || '').toLowerCase().includes(q)) score += 1;
      if (score) out.push({ score, title: n.title, url: n.url, meta: `${n.type}节点 · ${n.trunk} · ${n.statusLabel}`, snip: snippet(n.purpose && n.purpose.toLowerCase().includes(q) ? n.purpose : n.text, q) });
    }
    for (const p of INDEX.paths) {
      const hay = [p.title, p.question, p.general].join(' ').toLowerCase();
      if (hay.includes(q)) out.push({ score: p.title.toLowerCase().includes(q) ? 9 : 3, title: p.title, url: p.url, meta: '学习路径', snip: snippet(p.general || p.question, q) });
    }
    return out.sort((a, b) => b.score - a.score).slice(0, 8);
  }
  function drawResults(q) {
    hits = search(q); active = hits.length ? 0 : -1;
    if (!q.trim()) { list.hidden = true; input.setAttribute('aria-expanded', 'false'); return; }
    const ql = q.trim().toLowerCase();
    list.innerHTML = hits.length
      ? hits.map((h, i) => `<li role="option" id="sr-${i}" aria-selected="${i === active}" data-url="${esc(prefix + h.url)}"><span class="sr-title">${hl(h.title, ql)}</span><span class="sr-meta"> ${esc(h.meta)}</span><span class="sr-snip">${hl(h.snip, ql)}</span></li>`).join('')
      : '<li role="option" aria-disabled="true" class="empty">没有找到。可以换个说法，或者在节点页记下这个疑问。</li>';
    list.hidden = false; input.setAttribute('aria-expanded', 'true');
    input.setAttribute('aria-activedescendant', active >= 0 ? 'sr-' + active : '');
  }
  function moveActive(d) {
    if (!hits.length) return;
    active = (active + d + hits.length) % hits.length;
    $$('li[role=option]', list).forEach((li, i) => li.setAttribute('aria-selected', String(i === active)));
    input.setAttribute('aria-activedescendant', 'sr-' + active);
    const li = $('#sr-' + active); if (li) li.scrollIntoView({ block: 'nearest' });
  }
  if (input && list) {
    input.addEventListener('input', () => drawResults(input.value));
    input.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown') { e.preventDefault(); moveActive(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); moveActive(-1); }
      else if (e.key === 'Enter' && active >= 0) { e.preventDefault(); location.href = prefix + hits[active].url; }
      else if (e.key === 'Escape') { input.value = ''; drawResults(''); }
    });
    list.addEventListener('mousedown', e => { const li = e.target.closest('li[data-url]'); if (li) location.href = li.dataset.url; });
    input.addEventListener('blur', () => setTimeout(() => { list.hidden = true; input.setAttribute('aria-expanded', 'false'); }, 150));
    input.addEventListener('focus', () => { if (input.value.trim()) drawResults(input.value); });
  }
  document.addEventListener('keydown', e => {
    if (e.key !== '/' || e.metaKey || e.ctrlKey || e.altKey) return;
    const tag = (document.activeElement && document.activeElement.tagName) || '';
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag) || (document.activeElement && document.activeElement.isContentEditable)) return;
    if (input) { e.preventDefault(); input.focus(); }
  });

  // ---- export / import -------------------------------------------------------
  function exportData() {
    const now = new Date();
    const day = [now.getFullYear(), now.getMonth() + 1, now.getDate()].map(n => String(n).padStart(2, '0')).join('-');
    const blob = new Blob([JSON.stringify({ app: 'research-radar-theory', version: 1, exportedAt: new Date().toISOString(), data: store }, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = `research-radar-theory-${day}.json`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    toast('已导出。请把文件存到安全的位置。');
  }
  function importData(file) {
    const r = new FileReader();
    r.onload = () => {
      let parsed;
      try { parsed = JSON.parse(String(r.result)); } catch { toast('这个文件不是有效的 JSON。'); return; }
      if (!parsed || parsed.app !== 'research-radar-theory' || typeof parsed.data !== 'object' || !parsed.data) { toast('这不是理论地图的备份文件。'); return; }
      const n = Object.keys(parsed.data.nodes || {}).length;
      if (!confirm(`用备份替换这台设备上的理论地图记录？备份里有 ${n} 个节点的记录。当前记录会先另存一份，可以手动找回。`)) return;
      try { localStorage.setItem(LS + '.before-import', JSON.stringify(store)); } catch { }
      store = Object.assign(blank(), parsed.data);
      if (save()) { toast('已恢复。'); setTimeout(() => location.reload(), 600); }
    };
    r.readAsText(file);
  }
  const fileInput = $('#importFile');
  if (fileInput) fileInput.addEventListener('change', () => { if (fileInput.files[0]) importData(fileInput.files[0]); fileInput.value = ''; });

  // ---- shared click actions ------------------------------------------------
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-action]'); if (!b) return;
    const a = b.dataset.action;
    if (a === 'theme') {
      const order = ['auto', 'light', 'dark'];
      store.theme = order[(order.indexOf(themePref()) + 1) % order.length];
      save(); applyTheme();
      toast({ auto: '跟随系统深浅色', light: '浅色', dark: '深色' }[store.theme]);
    } else if (a === 'export') exportData();
    else if (a === 'import') fileInput && fileInput.click();
    else if (a === 'toggle-rails') {
      store.railsOff = !store.railsOff; save(); applyRails();
    } else if (a === 'edit-thinking') {
      $('#thinkingEdit').classList.remove('hidden');
      const t = $('#thinkingInput'); t.value = $('#thinkingText').textContent; t.focus();
    } else if (a === 'cancel-thinking') {
      $('#thinkingEdit').classList.add('hidden');
    } else if (a === 'save-thinking') {
      store.thinking = $('#thinkingInput').value.trim(); save();
      drawThinking(); $('#thinkingEdit').classList.add('hidden');
      toast(store.thinking ? '已保存在这台设备。' : '已恢复为路径里的原始提问。');
    }
  });

  // ---- side rails ----------------------------------------------------------
  const shell = $('.reader-shell');
  const narrow = () => window.matchMedia('(max-width:1180px)').matches;
  function applyRails() {
    if (!shell) return;
    const off = !!store.railsOff && !narrow();
    shell.classList.toggle('rails-off', off);
    const t = $('.rail-toggle');
    if (t) { t.textContent = off ? '展开侧栏' : '收起侧栏'; t.setAttribute('aria-pressed', String(off)); }
  }
  function setupRails() {
    if (!shell) return;
    if (narrow()) $$('[data-rail]').forEach(d => d.removeAttribute('open'));
    window.matchMedia('(max-width:1180px)').addEventListener('change', ev => {
      $$('[data-rail]').forEach(d => { if (ev.matches) d.removeAttribute('open'); else d.setAttribute('open', ''); });
      applyRails();
    });
    applyRails();
  }

  // ---- node page -----------------------------------------------------------
  function setupNode() {
    const id = body.dataset.node; if (!id) return;
    const rec = nodeRec(id);
    store.recent = [{ id, title: body.dataset.nodeTitle || id, at: new Date().toISOString() }]
      .concat(store.recent.filter(r => r && r.id !== id)).slice(0, 12);
    save();

    const q = $('#myQuestion'), note = $('#myNote'), resolved = $('#resolved'), state = $('#saveState');
    q.value = rec.question || ''; note.value = rec.note || ''; resolved.checked = !!rec.resolved;
    $$('[data-dim]').forEach(s => { s.value = (rec.dims[s.dataset.dim] || {}).state || ''; });
    $$('[data-dim-note]').forEach(s => { s.value = (rec.dims[s.dataset.dimNote] || {}).note || ''; });
    if (!storageOk) state.textContent = '这个浏览器不允许本地保存，记录不会保留';
    let timer = null;
    const persist = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        timer = null;
        const r = nodeRec(id);
        r.question = q.value; r.note = note.value; r.resolved = resolved.checked;
        $$('[data-dim]').forEach(s => { const k = s.dataset.dim; r.dims[k] = Object.assign({}, r.dims[k], { state: s.value }); });
        $$('[data-dim-note]').forEach(s => { const k = s.dataset.dimNote; r.dims[k] = Object.assign({}, r.dims[k], { note: s.value }); });
        r.updatedAt = new Date().toISOString();
        if (save()) state.textContent = '已保存在这台设备 ' + new Date().toTimeString().slice(0, 5);
      }, 400);
    };
    $$('#mine textarea, #mine input, #mine select').forEach(el => el.addEventListener(el.tagName === 'SELECT' || el.type === 'checkbox' ? 'change' : 'input', persist));
    // don't lose the last keystrokes when the reader navigates away inside the debounce window
    const flush = () => {
      if (timer === null) return;
      clearTimeout(timer); timer = null;
      const r = nodeRec(id);
      r.question = q.value; r.note = note.value; r.resolved = resolved.checked;
      $$('[data-dim]').forEach(s => { const k = s.dataset.dim; r.dims[k] = Object.assign({}, r.dims[k], { state: s.value }); });
      $$('[data-dim-note]').forEach(s => { const k = s.dataset.dimNote; r.dims[k] = Object.assign({}, r.dims[k], { note: s.value }); });
      r.updatedAt = new Date().toISOString();
      save();
    };
    window.addEventListener('pagehide', flush);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') flush(); });

    // layer filter: default is continuous reading
    const sections = $$('.node-section');
    $$('[data-layer-filter]').forEach(btn => btn.addEventListener('click', () => {
      const want = btn.dataset.layerFilter;
      $$('[data-layer-filter]').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
      sections.forEach(s => { s.hidden = !!want && s.dataset.layer !== want; });
      $$('.toc a').forEach(a => { const s = $(a.getAttribute('href')); a.parentElement.hidden = !!(s && s.hidden); });
    }));

    // where you stopped reading
    const tocLinks = $$('.toc a');
    if ('IntersectionObserver' in window && sections.length) {
      let posTimer;
      const io = new IntersectionObserver(entries => {
        entries.forEach(en => {
          if (!en.isIntersecting) return;
          tocLinks.forEach(a => a.classList.toggle('current', a.getAttribute('href') === '#' + en.target.id));
          clearTimeout(posTimer);
          posTimer = setTimeout(() => { nodeRec(id).pos = en.target.id; save(); }, 800);
        });
      }, { rootMargin: '-20% 0px -65% 0px' });
      sections.forEach(s => io.observe(s));
    }
    const resume = $('#resume');
    if (resume && rec.pos && rec.pos !== 'sec-1' && !location.hash) {
      const target = document.getElementById(rec.pos);
      const h = target && $('h2', target);
      if (h) { resume.innerHTML = `上次读到：<a href="#${esc(rec.pos)}">${esc(h.textContent)}</a>`; resume.classList.remove('hidden'); }
    }
  }

  // ---- home and path pages ---------------------------------------------------
  function drawThinking() {
    const t = $('#thinkingText'); if (!t) return;
    t.textContent = store.thinking || t.dataset.default || '';
  }
  function ago(iso) {
    const d = (Date.now() - Date.parse(iso)) / 86400000;
    if (!isFinite(d)) return '';
    if (d < 1) return '今天';
    if (d < 2) return '昨天';
    return Math.floor(d) + ' 天前';
  }
  function setupHome() {
    drawThinking();
    const recent = $('#recentList');
    const rows = store.recent.filter(r => r && byId[r.id]).slice(0, 6);
    if (recent && rows.length) {
      recent.innerHTML = rows.map(r => `<li><a href="${esc(prefix + byId[r.id].url)}">${esc(byId[r.id].title)}</a> <span class="small">${esc(ago(r.at))}</span></li>`).join('');
    }
    const open = $('#openQuestions');
    const qs = Object.entries(store.nodes).filter(([id, r]) => r && r.question && r.question.trim() && !r.resolved && byId[id])
      .sort((a, b) => String(b[1].updatedAt).localeCompare(String(a[1].updatedAt))).slice(0, 6);
    if (open && qs.length) {
      open.innerHTML = qs.map(([id, r]) => `<li><a href="${esc(prefix + byId[id].url)}#mine">${esc(byId[id].title)}</a><span class="q">${esc(r.question.trim())}</span></li>`).join('');
    }
  }
  function markVisited() {
    const seen = new Set(store.recent.map(r => r && r.id));
    $$('.steps li[data-node]').forEach(li => {
      const a = li.querySelector('a');
      if (!seen.has(li.dataset.node) || !a || li.classList.contains('visited')) return;
      li.classList.add('visited');
      a.insertAdjacentHTML('beforeend', '<span class="visually-hidden">（读过）</span>');
    });
  }

  const start = () => {
    renderMath();
    setupRails();
    if (body.dataset.page === 'node') setupNode();
    if (body.dataset.page === 'home') setupHome();
    markVisited();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
