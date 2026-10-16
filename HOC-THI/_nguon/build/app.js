/* app.js — phần tương tác của web ôn thi */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem('sw:' + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem('sw:' + k, JSON.stringify(v)); } catch (e) {} }
  };
  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { if (k === 'class') e.className = attrs[k]; else e.setAttribute(k, attrs[k]); });
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }

  /* ---------- điều hướng ---------- */
  var pages = $$('section.page'), curPg = null, scrollMem = {};
  // bản sạch của trang Bảng tra để đổ vào ngăn Tra nhanh khi mở (không nhân đôi nội dung trong HTML)
  var traHTML = (function () { var t = document.getElementById('p-TRA'); if (!t) return ''; var c = t.cloneNode(true); var h = c.querySelector('.page-head'); if (h) h.remove(); return c.innerHTML; })();
  function show(id, anchor) {
    var pg = document.getElementById('p-' + id) || document.getElementById('p-HOME') || pages[0];
    if (curPg && curPg !== pg) scrollMem[curPg.id] = window.scrollY;
    pages.forEach(function (p) { p.hidden = p !== pg; });
    $$('#nav a').forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + pg.id.slice(2)); });
    document.body.classList.remove('nav-open');
    activate(pg);
    var target = anchor && document.getElementById(anchor);
    if (target) { var dd = target.closest('details'); if (dd) dd.open = true; target.scrollIntoView({block: 'start', behavior: 'instant'}); window.scrollBy(0, -64); }
    else window.scrollTo({top: curPg === pg ? 0 : (scrollMem[pg.id] || 0), behavior: 'instant'});
    curPg = pg;
    store.set('last', pg.id.slice(2));
  }
  // hash dạng "#D8" hoặc "#D8/q-2023-c4" (trang/neo trong trang)
  function route(h) { var parts = (h || '').split('/'); show(parts[0] || store.get('last', 'HOME'), parts[1]); }
  window.addEventListener('hashchange', function () { route(location.hash.slice(1)); });
  // bấm link trỏ về đúng trang đang mở (hash không đổi) vẫn phải chạy
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (a && a.getAttribute('href') === location.hash) { e.preventDefault(); route(location.hash.slice(1)); }
  });
  $('#menuBtn').addEventListener('click', function () { document.body.classList.toggle('nav-open'); });

  /* ---------- tiến độ ---------- */
  var done = store.get('done', {});
  function refreshProgress() {
    var ids = $$('section.page[data-track]').map(function (p) { return p.id.slice(2); });
    var n = ids.filter(function (i) { return done[i]; }).length;
    $('#progBar').style.width = (ids.length ? 100 * n / ids.length : 0) + '%';
    $('#progTxt').textContent = n + '/' + ids.length + ' dạng đã nắm';
    $$('#nav a').forEach(function (a) { a.classList.toggle('done', !!done[a.getAttribute('href').slice(1)]); });
    $$('.step-row').forEach(function (r) { r.classList.toggle('done', !!done[r.dataset.go]); });
  }
  $$('section.page[data-track]').forEach(function (p) {
    var id = p.id.slice(2);
    var box = el('label', {class: 'donebox'}, '<input type="checkbox"> Tôi đã hiểu dạng này và làm được bài');
    var cb = box.querySelector('input'); cb.checked = !!done[id];
    cb.addEventListener('change', function () { done[id] = cb.checked; store.set('done', done); refreshProgress(); });
    var nx = $('.nextpage', p); if (nx) p.insertBefore(box, nx); else p.appendChild(box);
  });

  /* ---------- kích hoạt nội dung một trang (lười, vì vis cần khung đang hiển thị) ---------- */
  function activate(pg) {
    if (pg.dataset.ready) return;
    pg.dataset.ready = '1';
    $$('pre > code.language-turtle-graph', pg).forEach(function (code) { attachGraph(code.parentNode, true); });
    $$('pre > code.language-turtle', pg).forEach(function (code) { attachGraph(code.parentNode, false); });
    $$('pre > code.language-sparql', pg).forEach(function (code) { attachSparqlBtn(code.parentNode); });
    $$('pre > code.language-mermaid', pg).forEach(function (code) { attachMermaid(code.parentNode); });
    renderMermaid(pg);
    $$('.widget', pg).forEach(function (w) { var f = WIDGETS[w.dataset.w]; if (f && !w.dataset.on) { w.dataset.on = 1; f(w); } });
    glossarize(pg);
  }

  /* ---------- sơ đồ mermaid (cây tableau, sơ đồ lớp) — thư viện offline lib/mermaid.min.js ---------- */
  var MM = null, mmQ = Promise.resolve(), mmSeq = 0;
  function loadMermaid() {
    if (MM) return MM;
    MM = new Promise(function (res, rej) {
      if (window.mermaid) return res();
      var s = document.createElement('script'); s.src = 'lib/mermaid.min.js';
      s.onload = res; s.onerror = function () { MM = null; rej(new Error('không tải được lib/mermaid.min.js')); };
      document.head.appendChild(s);
    }).then(function () {
      window.mermaid.initialize({startOnLoad: false, theme: 'neutral', securityLevel: 'loose', flowchart: {useMaxWidth: true, htmlLabels: true}});
      return window.mermaid;
    });
    return MM;
  }
  function attachMermaid(pre) {
    var box = el('div', {class: 'mm-box'}); box._src = pre.textContent;
    pre.parentNode.insertBefore(box, pre); pre.hidden = true;
  }
  function renderMermaid(scope) {
    $$('.mm-box:not([data-done])', scope).forEach(function (box) {
      if (box.closest('details:not([open])')) return;  // vẽ khi mở đáp án
      box.dataset.done = '1'; box.innerHTML = '<p class="muted">Đang vẽ sơ đồ…</p>';
      mmQ = mmQ.then(function () { return loadMermaid(); })
        .then(function (m) { return m.render('mm' + (++mmSeq), box._src); })
        .then(function (r) { box.innerHTML = r.svg; })
        .catch(function (e) { box.innerHTML = '<p class="err">⚠ Không vẽ được sơ đồ (' + esc(e && e.message || e) + '). Mã sơ đồ:</p><pre>' + esc(box._src) + '</pre>'; });
    });
  }

  function renderGraph(box, ttl) {
    if (box._net) { try { box._net.destroy(); } catch (e) {} box._net = null; }
    box.innerHTML = ''; box.style.height = '';
    if (!ttl || !ttl.trim()) { box.style.height = 'auto'; box.classList.add('err'); box.textContent = 'Ô đang trống — viết Turtle vào ô trên rồi bấm Vẽ.'; return; }
    try { var r = RDF.draw(box, ttl); box._net = r.net; box.classList.remove('err'); }
    catch (e) { box.style.height = 'auto'; box.classList.add('err'); box.textContent = '⚠ Lỗi cú pháp Turtle: ' + e.message; }
  }
  function drawable(ttl) { try { return RDF.parse(ttl).triples.length > 0; } catch (e) { return false; } }
  function attachGraph(pre, auto) {
    var ttl = pre.textContent;
    if (!drawable(ttl)) return;  // đoạn trích "… như trên …" / chỉ có prefix: không gắn nút vẽ
    var bar = el('div', {class: 'codebar'});
    var btn = el('button', {class: 'btn sm'}, auto ? '◉ Ẩn/hiện đồ thị' : '◉ Vẽ đồ thị RDF');
    var edit = el('button', {class: 'btn sm ghost'}, '✎ Mở trong Bảng vẽ');
    bar.appendChild(btn); bar.appendChild(edit);
    var box = el('div', {class: 'graph-box'});
    pre.parentNode.insertBefore(bar, pre.nextSibling);
    bar.parentNode.insertBefore(box, bar.nextSibling);
    if (auto && pre.closest('details:not([open])')) { box._ttl = ttl; box.dataset.lazy = '1'; }  // vẽ khi mở đáp án
    else if (auto) renderGraph(box, ttl); else box.hidden = true;
    btn.addEventListener('click', function () {
      if (box.hidden || box.dataset.lazy) { box.hidden = false; delete box.dataset.lazy; renderGraph(box, ttl); } else box.hidden = true;
    });
    edit.addEventListener('click', function () { store.set('drawTtl', ttl); var w = $('#p-VE .widget'); if (w && w._load) w._load(ttl); location.hash = 'VE'; });
  }
  var pendingQ = null;
  function attachSparqlBtn(pre) {
    var q = pre.textContent;
    // chỉ gắn nút cho truy vấn hoàn chỉnh (bỏ khối liệt kê cú pháp, UPDATE)
    var head = q.replace(/#[^\n]*/g, '').replace(/^\s*(PREFIX|BASE)\b[^\n]*$/gim, '').trim();
    if (!/^(select|construct|ask|describe)\b/i.test(head) || /\b(INSERT|DELETE|LOAD|CLEAR)\b/.test(head)) return;
    var bar = el('div', {class: 'codebar'});
    var btn = el('button', {class: 'btn sm ghost'}, '▶ Mở trong SPARQL Playground');
    bar.appendChild(btn); pre.parentNode.insertBefore(bar, pre.nextSibling);
    btn.addEventListener('click', function () { var w = $('#p-PLAY .widget'); if (w && w._setQuery) w._setQuery(q); else pendingQ = q; location.hash = 'PLAY'; });
  }

  /* ---------- ô làm bài trước mỗi đáp án ---------- */
  var answers = store.get('answers', {});
  function prevHeading(node) {
    for (var n = node; n && n.tagName !== 'SECTION'; n = n.parentElement) {
      for (var s = n.previousElementSibling; s; s = s.previousElementSibling) {
        if (/^H[2-6]$/.test(s.tagName)) return s.textContent;
        var hs = s.querySelectorAll ? s.querySelectorAll('h2,h3,h4,h5,h6') : [];
        if (hs.length) return hs[hs.length - 1].textContent;
      }
    }
    return '';
  }
  var seenKey = {};
  $$('section.page details').forEach(function (d) {
    if (d.classList.contains('hint') || d.dataset.noWork !== undefined) return;
    if (d.parentElement.closest('details.extra')) return;  // phần Đọc thêm: không cần ô làm bài
    var pg = d.closest('section.page'), sum = (d.querySelector('summary') || {}).textContent || '';
    if (pg.id === 'p-D11' && /^Dàn ý/.test(sum.trim())) return;  // câu lý thuyết: đọc dàn ý là đủ
    // khoá theo nội dung (trang + tiêu đề câu + nhãn đáp án) → không lệch khi thêm/bớt nội dung khác
    var key = pg.id + '|' + prevHeading(d).trim().slice(0, 80) + '|' + sum.trim().slice(0, 30);
    seenKey[key] = (seenKey[key] || 0) + 1; if (seenKey[key] > 1) key += '#' + seenKey[key];
    var wrap = el('div', {class: 'work'});
    var ta = el('textarea', {rows: 4, placeholder: '✍ Tự làm ở đây trước khi mở đáp án (tự lưu trên máy này).'});
    ta.value = answers[key] || '';
    ta.addEventListener('input', function () { answers[key] = ta.value; store.set('answers', answers); });
    wrap.appendChild(ta);
    if (d.querySelector('code.language-turtle, code.language-turtle-graph')) {
      var drawBtn = el('button', {class: 'btn sm ghost'}, '◉ Vẽ Turtle của tôi');
      var box = el('div', {class: 'graph-box'}); box.hidden = true;
      drawBtn.addEventListener('click', function () { box.hidden = false; renderGraph(box, ta.value); });
      wrap.appendChild(drawBtn); wrap.appendChild(box);
    }
    d.parentNode.insertBefore(wrap, d);
  });
  // vẽ đồ thị / sơ đồ trong <details> khi mở (khung ẩn thì không đo được kích thước)
  document.addEventListener('toggle', function (e) {
    var d = e.target; if (!d.open || d.tagName !== 'DETAILS') return;
    $$('.graph-box[data-lazy]', d).forEach(function (g) { delete g.dataset.lazy; renderGraph(g, g._ttl); });
    renderMermaid(d);
  }, true);

  /* ---------- barem có ô tick + tổng điểm (lưu lại) ---------- */
  var ticks = store.get('ticks', {});
  $$('section.page').forEach(function (pg) {
    var n = 0;
    $$('li', pg).forEach(function (li) {
      var host = li, first = li.firstChild;
      if (first && first.nodeType === 3 && !first.nodeValue.trim() && li.firstElementChild && li.firstElementChild.tagName === 'P') { host = li.firstElementChild; first = host.firstChild; }
      if (!first || first.nodeType !== 3 || !/^\s*\[[ xX]\]/.test(first.nodeValue)) return;
      first.nodeValue = first.nodeValue.replace(/^\s*\[[ xX]\]\s*/, '');
      var key = pg.id + ':' + (n++);
      var cb = el('input', {type: 'checkbox', class: 'barem'}); cb.checked = !!ticks[key];
      host.insertBefore(cb, host.firstChild); li.classList.add('task');
      var m = /\(([\d.,]+)\s*đ\)/.exec(li.textContent); cb.dataset.pt = m ? m[1].replace(',', '.') : '0';
      cb.addEventListener('change', function () { ticks[key] = cb.checked; store.set('ticks', ticks); updateScore(li.closest('ul,ol')); });
    });
  });
  $$('ul,ol').forEach(function (ul) { if ($('input.barem', ul)) updateScore(ul); });
  function updateScore(ul) {
    if (!ul) return;
    var tot = 0, got = 0;
    $$('input.barem', ul).forEach(function (c) { var p = parseFloat(c.dataset.pt) || 0; tot += p; if (c.checked) got += p; });
    if (!tot) return;
    var s = ul._score || (ul._score = ul.parentNode.insertBefore(el('div', {class: 'score'}), ul.nextSibling));
    s.textContent = 'Tự chấm: ' + got.toFixed(2).replace(/\.?0+$/, '') + ' / ' + tot.toFixed(2).replace(/\.?0+$/, '') + ' điểm (tick ý bạn đã viết đúng)';
  }

  /* ---------- từ điển thuật ngữ ---------- */
  var GL = window.SW_GLOSS || {};
  var terms = Object.keys(GL).sort(function (a, b) { return b.length - a.length; });
  var glRe = null;
  try {
    glRe = terms.length ? new RegExp('(^|[^\\p{L}\\p{N}_:])(' + terms.map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')(?![\\p{L}\\p{N}_])', 'giu') : null;
  } catch (e) { glRe = null; }
  var glLower = {}; terms.forEach(function (t) { if (!glLower[t.toLowerCase()]) glLower[t.toLowerCase()] = t; });
  function glLookup(w) { return GL.hasOwnProperty(w) ? w : glLower[w.toLowerCase()]; }
  function glossarize(root) {
    if (!glRe) return;
    var used = {};
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {acceptNode: function (n) {
      var p = n.parentNode;
      if (!p || p.closest('pre,code,textarea,button,summary,abbr,a,label,h1,h2,h3,h4,h5,h6,svg,.widget,.graph-box,.mm-box,table.res,.quiz,.step-row,.page-head')) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }});
    var list = []; while (walker.nextNode()) list.push(walker.currentNode);
    list.forEach(function (node) {
      var txt = node.nodeValue, m, hit = null;
      glRe.lastIndex = 0;
      while ((m = glRe.exec(txt))) { var k = glLookup(m[2]); if (k && !used[k]) { hit = {m: m, k: k}; break; } }
      if (!hit) return;
      used[hit.k] = 1;
      var start = hit.m.index + hit.m[1].length, end = start + hit.m[2].length;
      var ab = el('abbr', {class: 'gl', tabindex: '0', 'data-def': GL[hit.k]}); ab.textContent = txt.slice(start, end);
      var after = document.createTextNode(txt.slice(end));
      node.nodeValue = txt.slice(0, start);
      node.parentNode.insertBefore(after, node.nextSibling);
      node.parentNode.insertBefore(ab, after);
    });
  }
  // tooltip nổi (position: fixed) để không bị bảng có thanh cuộn cắt mất
  var tip = el('div', {id: 'gltip', role: 'tooltip'}); tip.hidden = true; document.body.appendChild(tip);
  function tipOn(e) {
    var ab = e.target.closest && e.target.closest('abbr.gl'); if (!ab) return;
    tip.textContent = ab.dataset.def; tip.hidden = false;
    var r = ab.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    var x = Math.max(8, Math.min(r.left, window.innerWidth - w - 8)), y = r.bottom + 6;
    if (y + h > window.innerHeight - 8) y = Math.max(8, r.top - h - 6);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function tipOff(e) { if (e.target.closest && e.target.closest('abbr.gl')) tip.hidden = true; }
  document.addEventListener('mouseover', tipOn); document.addEventListener('focusin', tipOn);
  document.addEventListener('mouseout', tipOff); document.addEventListener('focusout', tipOff);
  window.addEventListener('scroll', function () { tip.hidden = true; }, {passive: true});

  /* ---------- quiz ---------- */
  var QZ = window.SW_QUIZ || [];
  $$('.quiz[data-d]').forEach(function (box) {
    var items = QZ.filter(function (q) { return q.d === box.dataset.d; });
    if (!items.length) { box.remove(); return; }
    box.innerHTML = '<h3>⚡ Quiz nhanh 1 phút</h3>';
    items.forEach(function (q, qi) {
      var div = el('div', {class: 'qz'}, '<p><b>' + (qi + 1) + '.</b> ' + esc(q.q) + '</p>');
      q.opts.forEach(function (o, oi) {
        var b = el('button', {class: 'opt'}, String.fromCharCode(65 + oi) + '. ' + esc(o));
        b.addEventListener('click', function () {
          $$('.opt', div).forEach(function (x, xi) { x.disabled = true; if (xi === q.a) x.classList.add('right'); });
          if (oi !== q.a) b.classList.add('wrong');
          div.appendChild(el('p', {class: 'why'}, (oi === q.a ? '✔ Đúng. ' : '✘ Sai. ') + esc(q.why || '')));
        });
        div.appendChild(b);
      });
      box.appendChild(div);
    });
  });

  /* ---------- bảng tra nhanh ---------- */
  $('#qrefBtn').addEventListener('click', function () { var q = $('#qref'), box = $('.qref', q); if (!box.innerHTML) box.innerHTML = traHTML; q.classList.toggle('open'); activate(q); });
  $('#qrefClose').addEventListener('click', function () { $('#qref').classList.remove('open'); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { $('#qref').classList.remove('open'); document.body.classList.remove('nav-open'); } });

  /* ---------- đồng hồ luyện đề (theo giờ thật, không chậm khi chuyển tab) ---------- */
  $$('.timer').forEach(function (t) {
    var acc = 0, t0 = null, h = null, out = el('span', {class: 'clock'}, '00:00');
    var go = el('button', {class: 'btn sm'}, '▶ Bắt đầu tính giờ'), rs = el('button', {class: 'btn sm ghost'}, '↺');
    t.appendChild(go); t.appendChild(out); t.appendChild(rs);
    function sec() { return Math.floor((acc + (t0 ? Date.now() - t0 : 0)) / 1000); }
    function fmt() { var v = sec(), m = Math.floor(v / 60); out.textContent = (m < 10 ? '0' : '') + m + ':' + ('0' + v % 60).slice(-2); }
    go.addEventListener('click', function () {
      if (t0) { acc += Date.now() - t0; t0 = null; clearInterval(h); h = null; go.textContent = '▶ Tiếp tục'; }
      else { t0 = Date.now(); h = setInterval(fmt, 500); go.textContent = '⏸ Tạm dừng'; }
      fmt();
    });
    rs.addEventListener('click', function () { acc = 0; if (t0) t0 = Date.now(); fmt(); });
  });

  /* =================== WIDGETS =================== */
  var WIDGETS = {};

  /* ---- Bảng vẽ đồ thị RDF ---- */
  WIDGETS.drawpad = function (w) {
    w.innerHTML =
      '<div class="toolbar">' +
      '<button class="btn sm" data-a="move">✋ Di chuyển / chọn</button>' +
      '<button class="btn sm" data-a="iri">＋ Nút IRI (elip)</button>' +
      '<button class="btn sm" data-a="lit">＋ Literal (chữ nhật)</button>' +
      '<button class="btn sm" data-a="bn">＋ Blank node</button>' +
      '<button class="btn sm" data-a="edge">→ Nối cạnh (kéo từ nút này sang nút kia)</button>' +
      '<button class="btn sm ghost" data-a="del">✕ Xoá mục đang chọn</button>' +
      '<button class="btn sm ghost" data-a="clear">Xoá hết</button></div>' +
      '<p class="muted"><b>Kéo thả:</b> nhấn giữ chuột <u>ngay trên một nút</u> rồi kéo (kéo chỗ trống = dời cả khung, lăn chuột = phóng to). ' +
      '<b>Thêm nút:</b> bấm "＋" rồi bấm vào chỗ trống. <b>Nối cạnh:</b> bấm "→ Nối cạnh" rồi kéo từ nút này sang nút kia (xong tự quay về chế độ Di chuyển). Bấm đúp vào nút/cạnh để sửa nhãn.</p>' +
      '<p class="mode muted">Chế độ: <b>✋ Di chuyển</b></p>' +
      '<div class="pad graph-box"></div>' +
      '<div class="cols"><div><h4>Turtle sinh tự động từ hình vẽ</h4><pre class="out"></pre></div>' +
      '<div><h4>Nạp từ Turtle (để sửa tiếp bằng tay)</h4><textarea class="inp" rows="8" placeholder="@prefix : <http://example.org/> .&#10;:a :p :b ."></textarea>' +
      '<button class="btn sm" data-a="load">⇩ Nạp vào bảng vẽ</button><div class="loaderr"></div></div></div>';
    var pad = $('.pad', w), out = $('.out', w), inp = $('.inp', w), lerr = $('.loaderr', w);
    pad.style.height = '480px';
    var nodes = new vis.DataSet(), edges = new vis.DataSet(), seq = 0, prefixes = {};
    var net = new vis.Network(pad, {nodes: nodes, edges: edges}, {
      nodes: RDF.BW.nodes, edges: Object.assign({}, RDF.BW.edges, {smooth: {enabled: true, type: 'curvedCW', roundness: 0.1}}), physics: false,
      manipulation: {enabled: false,
        addNode: function (d, cb) {
          var kind = pending;
          if (kind === 'bn') { d.label = ' '; d.kind = 'bn'; d.shape = 'ellipse'; d.widthConstraint = {minimum: 46}; }
          else {
            var l = prompt(kind === 'lit' ? 'Giá trị literal (vd: Ann  hoặc  10  hoặc  Avatar@en  hoặc  "2024-01-01"^^xsd:date):' : 'Tên IRI (vd :Ann, foaf:Person, rdf:Statement):', kind === 'lit' ? '' : ':');
            if (l === null || !l.trim()) { cb(null); setMode('move'); return; }
            d.label = l.trim(); d.kind = kind; d.shape = kind === 'lit' ? 'box' : 'ellipse';
          }
          d.id = 'n' + (++seq); cb(d); sync(true); setMode('move');
        },
        addEdge: function (d, cb) {
          var l = prompt('Nhãn cạnh (predicate), vd: rdf:type, foaf:name, :teaches', 'rdf:type');
          if (l === null || !l.trim()) { cb(null); setMode('move'); return; }
          d.label = l.trim(); cb(d); sync(true); setMode('move');
        }
      }
    });
    var pending = null;
    function setMode(m) {
      try { net.disableEditMode(); } catch (e) {}
      if (m === 'node') net.addNodeMode();
      if (m === 'edge') net.addEdgeMode();
      $('.mode', w).innerHTML = 'Chế độ: <b>' + (m === 'node' ? '＋ Thêm nút — bấm vào chỗ trống' : m === 'edge' ? '→ Nối cạnh — kéo từ nút này sang nút kia' : '✋ Di chuyển (kéo nút để sắp xếp)') + '</b>';
    }
    $$('button[data-a]', w).forEach(function (b) {
      b.addEventListener('click', function () {
        var a = b.dataset.a;
        if (a === 'move') setMode('move');
        else if (a === 'iri' || a === 'lit' || a === 'bn') { pending = a; setMode('node'); }
        else if (a === 'edge') setMode('edge');
        else if (a === 'del') { net.deleteSelected(); sync(true); }
        else if (a === 'clear') { nodes.clear(); edges.clear(); sync(true); }
        else if (a === 'load') load(inp.value);
      });
    });
    net.on('doubleClick', function (p) {
      if (p.nodes.length) {
        var n = nodes.get(p.nodes[0]); if (n.kind === 'bn') return;
        var l = prompt('Sửa nhãn:', n.label); if (l !== null && l.trim()) { nodes.update({id: n.id, label: l.trim(), ttl: null}); sync(true); }
      } else if (p.edges.length) {
        var e = edges.get(p.edges[0]);
        var l2 = prompt('Sửa predicate:', e.label); if (l2 !== null && l2.trim()) { edges.update({id: e.id, label: l2.trim(), ttl: null}); sync(true); }
      }
    });
    // nhãn người dùng gõ → term Turtle hợp lệ
    function iriOf(label) {
      var v = label.replace(/\n/g, '').trim();
      if (/^<.*>$/.test(v)) return v;
      if (/^(https?|urn|mailto):/.test(v)) return '<' + v + '>';
      v = v.replace(/\s+/g, '_');
      return v.indexOf(':') >= 0 ? v : ':' + v;
    }
    function termOf(n) {
      if (n.kind === 'bn') return '_:b' + String(n.id).replace(/\W/g, '');
      if (n.ttl) return n.ttl;  // nút nạp từ Turtle: giữ nguyên term gốc
      if (n.kind === 'lit') {
        var v = n.label.replace(/\n/g, '').trim();
        if (/^"[\s\S]*"(@[A-Za-z]+(-[A-Za-z0-9]+)*|\^\^\S+)?$/.test(v)) return v;  // đã gõ đúng cú pháp Turtle
        if (/^-?\d+(\.\d+)?$/.test(v) || v === 'true' || v === 'false') return v;
        var m = /^(.*)@([a-z]{2,3}(-[A-Za-z0-9]+)?)$/.exec(v);
        var q = function (x) { return '"' + x.replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"'; };
        return m ? q(m[1]) + '@' + m[2] : q(v);
      }
      return iriOf(n.label);
    }
    function predOf(e) { return e.ttl || iriOf(e.label); }
    function sync(user) {
      var bySubj = {}, order = [], used = {}, warn = [];
      function pfx(t) { var m = /^([A-Za-z][\w\-]*|):/.exec(t); if (m && !/^_:/.test(t)) used[m[1]] = 1; var d = /\^\^([A-Za-z][\w\-]*|):/.exec(t); if (d) used[d[1]] = 1; }
      edges.get().forEach(function (e) {
        var s = nodes.get(e.from), o = nodes.get(e.to); if (!s || !o) return;
        if (s.kind === 'lit') { warn.push('literal ' + s.label + ' không được làm subject'); return; }
        var st = termOf(s), pt = predOf(e), ot = termOf(o);
        [st, pt, ot].forEach(pfx);
        if (!bySubj[st]) { bySubj[st] = []; order.push(st); }
        bySubj[st].push((pt === 'rdf:type' ? 'a' : pt) + ' ' + ot);
      });
      var body = order.map(function (s) { return s + ' ' + bySubj[s].join(' ;\n    ') + ' .'; }).join('\n');
      var head = Object.keys(used).map(function (p) {
        var ns = prefixes[p] || RDF.STD[p] || (p === '' ? 'http://example.org/' : 'http://example.org/' + p + '#');
        return '@prefix ' + p + ': <' + ns + '> .';
      });
      var ttl = (head.length ? head.join('\n') + '\n\n' : '') + body;
      out.textContent = edges.length ? ttl + (warn.length ? '\n\n# ⚠ ' + warn.join('; ') : '') : '(chưa có cạnh nào — mỗi cạnh = 1 triple)';
      if (user && edges.length) store.set('drawTtl', ttl);  // nhớ hình đang vẽ khi tải lại trang
    }
    function load(ttl) {
      lerr.innerHTML = '';
      var parsed;
      try { parsed = RDF.parse(ttl); if (!parsed.triples.length) throw new Error('không có triple nào.'); }
      catch (e) { lerr.innerHTML = '<p class="err">⚠ Lỗi Turtle: ' + esc(e.message) + '</p>'; return false; }
      var d = RDF.toVis(parsed); prefixes = parsed.prefixes;
      nodes.clear(); edges.clear();
      nodes.add(d.nodes.map(function (n) { if (n.kind !== 'bn') n.label = n.label.replace(/\n/g, ''); return n; }));
      edges.add(d.edges);
      net.setOptions({physics: {solver: 'forceAtlas2Based', forceAtlas2Based: {gravitationalConstant: -110, springLength: 120, avoidOverlap: 0.6}, stabilization: {iterations: 500}}});
      var froze = false;
      var freeze = function () { if (froze) return; froze = true; net.setOptions({physics: false}); net.fit(); };
      net.once('stabilizationIterationsDone', freeze); net.once('stabilized', freeze);
      net.stabilize(500); setTimeout(freeze, 2500);
      setMode('move');
      sync(false);
      return true;
    }
    w._net = net;
    w._load = function (t) { inp.value = t; load(t); };
    var saved = store.get('drawTtl', null);
    if (saved && drawable(saved)) w._load(saved); else { store.set('drawTtl', null); sync(false); }
  };

  /* ---- Bộ suy diễn RDFS từng bước ---- */
  var PRESET_RDFS = {
    '2022-C2': '@prefix : <http://exam.hust.edu.vn/> .\n:a :r :b.\n:c a :C.\n:r rdfs:range :C; rdfs:domain :D.\n:C rdfs:subClassOf :E.\n:D rdfs:subClassOf :F.',
    'Ex2 gia đình (P2 Ex2)': '@prefix : <http://example.com/terms#> .\n:Person a rdfs:Class .\n:Man a rdfs:Class ; rdfs:subClassOf :Person .\n:Parent a rdfs:Class ; rdfs:subClassOf :Person .\n:Father a rdfs:Class ; rdfs:subClassOf :Parent , :Man .\n:Child a rdfs:Class ; rdfs:subClassOf :Person .\n:hasParent a rdf:Property ; rdfs:domain :Person ; rdfs:range :Parent .\n:hasFather a rdf:Property ; rdfs:subPropertyOf :hasParent ; rdfs:range :Father .\n:isChildOf a rdf:Property ; rdfs:domain :Child ; rdfs:range :Parent .\n:Ann a :Person ; :hasFather :Carl .\n:Carl a :Man .',
    '2022-C3 Fido/Milo': '@prefix bio: <http://exam.hust.edu.vn/bio/> .\nbio:offspring rdfs:domain bio:Animal; rdfs:range bio:Animal .\nbio:Fido a bio:Dog; bio:offspring bio:Spot.\nbio:Milo a bio:Cat; bio:offspring bio:Molly.'
  };
  WIDGETS.rdfs = function (w) {
    var opts = Object.keys(PRESET_RDFS).map(function (k) { return '<option>' + esc(k) + '</option>'; }).join('');
    w.innerHTML = '<div class="toolbar"><label>Ví dụ: <select class="pre">' + opts + '</select></label>' +
      '<label><input type="checkbox" class="triv"> Bật cả luật "hiển nhiên" (rdf1, rdfs4a/4b, rdfs6, rdfs8, rdfs10)</label></div>' +
      '<textarea class="kb" rows="9"></textarea>' +
      '<div class="toolbar"><button class="btn sm" data-a="step">⏭ Bước tiếp</button><button class="btn sm" data-a="all">⏩ Chạy đến điểm cố định</button><button class="btn sm ghost" data-a="reset">↺ Làm lại</button></div>' +
      '<div class="log"></div>' +
      '<h4>Kiểm tra một mệnh đề (đúng / không xác định)</h4><div class="toolbar"><input class="ask" size="40" placeholder=":Carl a :Parent ."> <button class="btn sm" data-a="ask">? Kiểm tra</button></div><div class="askout"></div>';
    var kb = $('.kb', w), log = $('.log', w), sel = $('.pre', w);
    kb.value = PRESET_RDFS[sel.value];
    sel.addEventListener('change', function () { kb.value = PRESET_RDFS[sel.value]; reset(); });
    kb.addEventListener('input', function () { reset(); });
    $('.triv', w).addEventListener('change', function () { reset(); });
    var S = null;
    var T = RDF.RDFNS + 'type', SC = RDF.STD.rdfs + 'subClassOf', SP = RDF.STD.rdfs + 'subPropertyOf', DOM = RDF.STD.rdfs + 'domain', RNG = RDF.STD.rdfs + 'range', RES = RDF.STD.rdfs + 'Resource', PROP = RDF.RDFNS + 'Property', CLS = RDF.STD.rdfs + 'Class';
    function key(t) { return t.t + '|' + t.v + '|' + (t.lang || '') + '|' + (t.dt || ''); }
    function tk(tr) { return key(tr.s) + ' ' + key(tr.p) + ' ' + key(tr.o); }
    function I(v) { return {t: 'iri', v: v}; }
    function init() {
      var parsed = RDF.parse(kb.value);
      S = {pf: parsed.prefixes, facts: [], idx: {}, round: 0, fixed: false};
      parsed.triples.forEach(function (t) { addFact(t, 'cho sẵn', []); });
      log.innerHTML = '<p><b>B0</b> — ' + S.facts.length + ' triple cho sẵn.</p>';
    }
    function addFact(t, rule, prem) { var k = tk(t); if (S.idx[k]) return false; S.idx[k] = {t: t, rule: rule, prem: prem}; S.facts.push(t); return true; }
    function show3(t) { return RDF.label(t.s, S.pf) .replace(/^$/, '[]') + ' ' + (t.p.v === T ? 'a' : RDF.label(t.p, S.pf)) + ' ' + (t.o.t === 'lit' ? '"' + t.o.v + '"' : RDF.label(t.o, S.pf).replace(/^$/, '[]')) + ' .'; }
    function step() {
      if (!S) init();
      if (S.fixed) return false;
      var F = S.facts.slice(), news = [], seen = {}, triv = $('.triv', w).checked;
      function emit(t, rule, prem) { var k = tk(t); if (S.idx[k] || seen[k]) return; seen[k] = 1; news.push({k: k, t: t, rule: rule, prem: prem}); }
      F.forEach(function (a) {
        if (triv) {
          emit({s: a.p, p: I(T), o: I(PROP)}, 'rdf1', [a]);
          if (a.s.t !== 'lit') emit({s: a.s, p: I(T), o: I(RES)}, 'rdfs4a', [a]);
          if (a.o.t !== 'lit') emit({s: a.o, p: I(T), o: I(RES)}, 'rdfs4b', [a]);
          if (a.p.v === T && a.o.v === PROP) emit({s: a.s, p: I(SP), o: a.s}, 'rdfs6', [a]);
          if (a.p.v === T && a.o.v === CLS) { emit({s: a.s, p: I(SC), o: I(RES)}, 'rdfs8', [a]); emit({s: a.s, p: I(SC), o: a.s}, 'rdfs10', [a]); }
        }
        F.forEach(function (b) {
          // a là axiom schema, b là dữ kiện
          if (a.p.v === DOM && b.p.v === a.s.v && b.p.t === 'iri' && a.s.t === 'iri') emit({s: b.s, p: I(T), o: a.o}, 'rdfs2 (domain)', [b, a]);
          if (a.p.v === RNG && b.p.v === a.s.v && a.s.t === 'iri' && b.o.t !== 'lit') emit({s: b.o, p: I(T), o: a.o}, 'rdfs3 (range)', [b, a]);
          if (a.p.v === SP && b.p.v === SP && key(a.o) === key(b.s)) emit({s: a.s, p: I(SP), o: b.o}, 'rdfs5 (subProperty bắc cầu)', [a, b]);
          if (a.p.v === SP && b.p.v === a.s.v && a.s.t === 'iri') emit({s: b.s, p: a.o, o: b.o}, 'rdfs7 (subPropertyOf)', [b, a]);
          if (a.p.v === SC && b.p.v === T && key(b.o) === key(a.s)) emit({s: b.s, p: I(T), o: a.o}, 'rdfs9 (subClassOf)', [b, a]);
          if (a.p.v === SC && b.p.v === SC && key(a.o) === key(b.s)) emit({s: a.s, p: I(SC), o: b.o}, 'rdfs11 (subClass bắc cầu)', [a, b]);
        });
      });
      S.round++;
      if (!news.length) { S.fixed = true; log.appendChild(el('p', {class: 'fix'}, '■ Bước ' + S.round + ': không sinh thêm triple mới ⇒ <b>đạt điểm cố định ở B' + (S.round - 1) + '</b>.')); return false; }
      news.forEach(function (n) { addFact(n.t, n.rule, n.prem); });
      var tb = '<table class="res"><tr><th>Triple suy ra</th><th>Luật</th><th>Cơ sở (⇐)</th></tr>' + news.map(function (n) {
        return '<tr><td><code>' + esc(show3(n.t)) + '</code></td><td>' + esc(n.rule) + '</td><td><code>' + n.prem.map(function (p) { return esc(show3(p)); }).join('<br>') + '</code></td></tr>';
      }).join('') + '</table>';
      log.appendChild(el('div', {}, '<p><b>B' + S.round + '</b> — thêm ' + news.length + ' triple:</p>' + tb));
      return true;
    }
    function reset() { S = null; log.innerHTML = ''; $('.askout', w).innerHTML = ''; }
    $$('button', w).forEach(function (b) {
      b.addEventListener('click', function () {
        try {
          var a = b.dataset.a;
          if (a === 'step') step();
          else if (a === 'all') { var g = 0; while (step() && g++ < 30); if (S && !S.fixed) step(); }
          else if (a === 'reset') reset();
          else if (a === 'ask') { try { ask(); } catch (e2) { $('.askout', w).innerHTML = '<p class="err">⚠ ' + esc(e2.message) + '</p>'; } }
        } catch (e) { log.appendChild(el('p', {class: 'err'}, '⚠ ' + esc(e.message))); }
      });
    });
    function explain(k, depth) {
      var f = S.idx[k]; if (!f) return '';
      var pad = new Array(depth + 1).join('&nbsp;&nbsp;&nbsp;&nbsp;');
      var s = pad + (depth ? '└ ' : '') + '<code>' + esc(show3(f.t)) + '</code> — ' + esc(f.rule) + '<br>';
      if (depth < 6) f.prem.forEach(function (p) { if (S.idx[tk(p)].rule !== 'cho sẵn' || depth < 6) s += explain(tk(p), depth + 1); });
      return s;
    }
    function ask() {
      if (!S) init();
      var g = 0; while (step() && g++ < 30);
      var txt = $('.ask', w).value.trim(), out = $('.askout', w);
      if (!txt) { out.innerHTML = '<p class="muted">Gõ một mệnh đề, vd <code>:Carl a :Parent .</code></p>'; return; }
      if (!/\.\s*$/.test(txt)) txt += ' .';
      var src = Object.keys(S.pf).map(function (p) { return '@prefix ' + p + ': <' + S.pf[p] + '> .'; }).join('\n') + '\n' + txt;
      var qs = RDF.parse(src).triples;
      // blank node trong mệnh đề = "có một cái gì đó" ⇒ coi như biến, tìm cách gán khớp MỌI triple
      function unify(qt, ft, env) {
        var e = Object.assign({}, env);
        for (var pos of ['s', 'p', 'o']) {
          var a = qt[pos], b = ft[pos];
          if (a.t === 'bn') { var bk = key(b); if (e[a.v] === undefined) e[a.v] = bk; else if (e[a.v] !== bk) return null; }
          else if (key(a) !== key(b)) return null;
        }
        return e;
      }
      function solve(i, env, used) {
        if (i === qs.length) return {env: env, used: used};
        for (var j = 0; j < S.facts.length; j++) {
          var e = unify(qs[i], S.facts[j], env);
          if (e) { var r = solve(i + 1, e, used.concat([tk(S.facts[j])])); if (r) return r; }
        }
        return null;
      }
      var sol = solve(0, {}, []);
      if (sol) {
        var binds = Object.keys(sol.env).map(function (b) {
          var k = sol.env[b].split('|'), t = {t: k[0], v: k[1], lang: k[2] || undefined, dt: k[3] || undefined};
          return '[ ] ↦ ' + (t.t === 'bn' ? 'một blank node' : RDF.label(t, S.pf));
        });
        out.innerHTML = '<p class="ok"><b>✔ ĐÚNG (TRUE)</b>' + (binds.length ? ' — blank node là "một cái gì đó": gán ' + esc(binds.join(', ')) : '') + '</p><div class="tree">' +
          sol.used.map(function (k) { return explain(k, 0); }).join('') + '</div>';
      }
      else out.innerHTML = '<p class="no"><b>? KHÔNG XÁC ĐỊNH (unknown)</b> — không suy ra được bằng luật RDFS. Theo giả thiết thế giới mở (OWA) <u>không được kết luận là sai</u>; RDFS không có phủ định nên không bao giờ suy ra được "sai". (Nếu bài cho chọn true/false thì ghi: <i>không suy ra được ⇒ false/unknown</i> và giải thích.)' + (!$('.triv', w).checked ? ' <br>Gợi ý: mệnh đề kiểu "X a rdfs:Resource" cần bật luật hiển nhiên.' : '') + '</p>';
    }
  };

  /* ---- Datalog từng bước ---- */
  var PRESET_DL = {
    '2023-C3 Đường đi': 'Đường-một-chiều(A, B)\nĐường-một-chiều(B, C)\nĐường-hai-chiều(D, C)\nĐường-hai-chiều(Y, X) ← Đường-hai-chiều(X, Y)\nCó-đường-đi(X, Y) ← Đường-hai-chiều(X, Y)\nCó-đường-đi(X, Y) ← Đường-một-chiều(X, Y)\nCó-đường-đi(X, Z) ← Có-đường-đi(X, Y) ∧ Có-đường-đi(Y, Z)',
    'Tổ tiên': 'parent(An, Binh)\nparent(Binh, Chi)\nparent(Chi, Dung)\nancestor(X, Y) ← parent(X, Y)\nancestor(X, Z) ← parent(X, Y) ∧ ancestor(Y, Z)',
    'RDFS dạng luật': 'subClassOf(Father, Man)\nsubClassOf(Man, Person)\ntype(Carl, Father)\nsubClassOf(X, Z) ← subClassOf(X, Y) ∧ subClassOf(Y, Z)\ntype(X, D) ← type(X, C) ∧ subClassOf(C, D)'
  };
  WIDGETS.datalog = function (w) {
    var opts = Object.keys(PRESET_DL).map(function (k) { return '<option>' + esc(k) + '</option>'; }).join('');
    w.innerHTML = '<div class="toolbar"><label>Chương trình: <select class="pre">' + opts + '</select></label></div>' +
      '<p class="muted">Mỗi dòng 1 dữ kiện hoặc 1 luật. Luật viết <code>Đầu ← Thân1 ∧ Thân2</code> (cũng nhận <code>:-</code>, <code>&lt;-</code>, dấu phẩy). <b>Biến</b> là X, Y, Z, U, V, W (hoặc bắt đầu bằng ?); còn lại là hằng.</p>' +
      '<textarea class="prog" rows="8"></textarea>' +
      '<div class="toolbar"><button class="btn sm" data-a="step">⏭ Bước tiếp</button><button class="btn sm" data-a="all">⏩ Chạy đến điểm cố định</button><button class="btn sm ghost" data-a="reset">↺ Làm lại</button></div>' +
      '<div class="log"></div><h4>Cây chứng minh</h4><div class="toolbar"><input class="goal" size="34" value="Có-đường-đi(A, D)"> <button class="btn sm" data-a="proof">🌳 Vẽ cây chứng minh</button></div><div class="proof"></div>';
    var prog = $('.prog', w), log = $('.log', w), sel = $('.pre', w);
    prog.value = PRESET_DL[sel.value];
    prog.addEventListener('input', function () { reset(); });
    sel.addEventListener('change', function () { prog.value = PRESET_DL[sel.value]; $('.goal', w).value = {'Tổ tiên': 'ancestor(An, Dung)', 'RDFS dạng luật': 'type(Carl, Person)'}[sel.value] || 'Có-đường-đi(A, D)'; reset(); });
    var S = null;
    var atomRe = /([^\s(),←∧:<\-][^\s(),←∧]*)\s*\(([^)]*)\)/g;
    function atoms(s) { var r = [], m; atomRe.lastIndex = 0; while ((m = atomRe.exec(s))) r.push({p: m[1], a: m[2].split(',').map(function (x) { return x.trim(); })}); return r; }
    function isVar(x) { return /^([XYZUVW]\d*|\?.+)$/.test(x); }
    function fk(a) { return a.p + '(' + a.a.join(', ') + ')'; }
    function init() {
      S = {facts: [], idx: {}, rules: [], round: 0, fixed: false};
      prog.value.split('\n').forEach(function (line) {
        line = line.trim(); if (!line || line[0] === '#' || line.indexOf('%') === 0) return;
        var parts = line.split(/←|:-|<-/);
        if (parts.length > 1) S.rules.push({h: atoms(parts[0])[0], b: atoms(parts[1]), txt: line});
        else atoms(line).forEach(function (a) { add(a, null, []); });
      });
      log.innerHTML = '<p><b>B0</b> = {' + S.facts.map(fk).map(esc).join(', ') + '}</p>';
    }
    function add(a, rule, prem) { var k = fk(a); if (S.idx[k]) return false; S.idx[k] = {a: a, rule: rule, prem: prem}; S.facts.push(a); return true; }
    function match(body, i, env, F, out, used) {
      if (i === body.length) { out.push({env: Object.assign({}, env), used: used.slice()}); return; }
      var b = body[i];
      F.forEach(function (f) {
        if (f.p !== b.p || f.a.length !== b.a.length) return;
        var e = Object.assign({}, env), ok = true;
        for (var j = 0; j < b.a.length && ok; j++) {
          var x = b.a[j];
          if (isVar(x)) { if (e[x] === undefined) e[x] = f.a[j]; else if (e[x] !== f.a[j]) ok = false; }
          else if (x !== f.a[j]) ok = false;
        }
        if (ok) { used.push(f); match(body, i + 1, e, F, out, used); used.pop(); }
      });
    }
    function step() {
      if (!S) init(); if (S.fixed) return false;
      var F = S.facts.slice(), news = [], seen = {};
      S.rules.forEach(function (r, ri) {
        var res = []; match(r.b, 0, {}, F, res, []);
        res.forEach(function (m) {
          var h = {p: r.h.p, a: r.h.a.map(function (x) { return isVar(x) ? m.env[x] : x; })}, k = fk(h);
          if (S.idx[k] || seen[k]) return; seen[k] = 1; news.push({a: h, rule: 'Luật ' + (ri + 1), prem: m.used});
        });
      });
      S.round++;
      if (!news.length) { S.fixed = true; log.appendChild(el('p', {class: 'fix'}, '■ Áp dụng tiếp không sinh dữ kiện mới ⇒ <b>điểm cố định thu được ở Bước ' + (S.round - 1) + '</b> (B' + (S.round - 1) + ', tổng ' + S.facts.length + ' dữ kiện).')); return false; }
      news.forEach(function (n) { add(n.a, n.rule, n.prem); });
      log.appendChild(el('div', {}, '<p><b>B' + S.round + '</b>: + {' + news.map(function (n) { return '<span class="new">' + esc(fk(n.a)) + '</span>'; }).join(', ') + '}</p>' +
        '<details class="hint" data-no-work><summary>vì sao?</summary><ul>' + news.map(function (n) { return '<li><code>' + esc(fk(n.a)) + '</code> ⇐ ' + esc(n.rule) + ' với ' + n.prem.map(fk).map(esc).join(' ∧ ') + '</li>'; }).join('') + '</ul></details>'));
      return true;
    }
    function reset() { S = null; log.innerHTML = ''; $('.proof', w).innerHTML = ''; }
    function tree(k, pre, last, depth) {
      var f = S.idx[k]; if (!f) return pre + '(?) ' + k + '\n';
      var line = pre + (depth ? (last ? '└── ' : '├── ') : '') + k + (f.rule ? '   [' + f.rule + ']' : '   [dữ kiện]') + '\n';
      var np = pre + (depth ? (last ? '    ' : '│   ') : '');
      f.prem.forEach(function (p, i) { line += tree(fk(p), np, i === f.prem.length - 1, depth + 1); });
      return line;
    }
    $$('button', w).forEach(function (b) {
      b.addEventListener('click', function () {
        try {
          var a = b.dataset.a;
          if (a === 'step') step();
          else if (a === 'all') { var g = 0; while (step() && g++ < 40); }
          else if (a === 'reset') reset();
          else if (a === 'proof') {
            if (!S) init(); var g2 = 0; while (step() && g2++ < 40);
            var goal = atoms($('.goal', w).value)[0];
            $('.proof', w).innerHTML = goal && S.idx[fk(goal)] ? '<pre>' + esc(tree(fk(goal), '', true, 0)) + '</pre><p class="muted">Khi thi: vẽ cây với gốc là khẳng định cần chứng minh, mỗi nút con là các tiền đề của luật đã dùng, lá là dữ kiện cho sẵn.</p>'
              : '<p class="no">Không suy ra được ' + esc($('.goal', w).value) + '.</p>';
          }
        } catch (e) { log.appendChild(el('p', {class: 'err'}, '⚠ ' + esc(e.message))); }
      });
    });
  };

  /* ---- SPARQL Playground (oxigraph WASM) ---- */
  var OX = null;
  function loadOx() {
    if (OX) return OX;
    // nạp bản offline lib/oxigraph.js (chứa sẵn wasm) — không cần mạng
    OX = new Promise(function (res, rej) {
      if (window.oxigraph) return res();
      var s = document.createElement('script'); s.src = 'lib/oxigraph.js';
      s.onload = res; s.onerror = function () { OX = null; rej(new Error('không tải được lib/oxigraph.js (để file index.html cùng thư mục với lib/)')); };
      document.head.appendChild(s);
    }).then(function () {
      var b = atob(window.OX_WASM), u = new Uint8Array(b.length);
      for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
      return window.oxigraph.init({module_or_path: u}).then(function () { return window.oxigraph; });
    }).catch(function (e) { OX = null; throw e; });  // lỗi thì lần sau thử lại
    return OX;
  }
  var DATA = window.SW_DATA || {datasets: {}, examples: []};
  function norm(t) {
    if (!t) return '';
    if (t.termType === 'NamedNode') return t.value;
    if (t.termType === 'BlankNode') return '_:';
    if (t.termType === 'Literal') {
      var dt = t.datatype && t.datatype.value || '';
      if (t.language) return '"' + t.value + '"@' + t.language;
      if (/XMLSchema#(integer|decimal|double|float|int|long|boolean)$/.test(dt)) return t.value;
      if (dt && !/XMLSchema#string$/.test(dt) && !/rdf-syntax-ns#langString$/.test(dt)) return '"' + t.value + '"^^' + dt;
      return '"' + t.value + '"';
    }
    return String(t.value);
  }
  function pfOf(ttl) { try { return RDF.parse(ttl).prefixes; } catch (e) { var p = {}; ttl.replace(/@?prefix\s+([\w\-]*):\s*<([^>]+)>/gi, function (m, a, b) { p[a] = b; }); return p; } }
  function short(v, pf) {
    if (v === '' || v === undefined) return '';
    if (/^(https?|urn|mailto):/.test(v)) return RDF.compact(v, pf);
    var m = /^(".*")\^\^(.+)$/.exec(v); if (m) return m[1] + '^^' + RDF.compact(m[2], pf);
    return v;
  }
  function selectVars(query) {
    var m = /select\s+(?:distinct\s+|reduced\s+)?([\s\S]*?)\s*(?:where\b|\{|from\b)/i.exec(query.replace(/#[^\n]*/g, ''));
    if (!m || /^\s*\*/.test(m[1])) return null;
    var s = m[1], prev;
    do { prev = s; s = s.replace(/\(([^()]*)\)/, function (all, inner) { var a = /\bas\s+\?(\w+)/i.exec(inner); return a ? ' ?' + a[1] + ' ' : ' '; }); } while (s !== prev);
    var out = []; s.replace(/\?(\w+)/g, function (all, v) { if (out.indexOf(v) < 0) out.push(v); });
    return out.length ? out : null;
  }
  function rowsKey(vars, rows) { return rows.map(function (r) { return vars.map(function (v) { return r[v] || ''; }).join(' | '); }).sort().join('\n'); }
  WIDGETS.sparql = function (w) {
    var dsOpts = Object.keys(DATA.datasets).map(function (k) { return '<option>' + esc(k) + '</option>'; }).join('');
    var exOpts = '<option value="">— chọn bài mẫu (tự nạp dữ liệu đúng) —</option>' + DATA.examples.map(function (e, i) { return '<option value="' + i + '">' + esc(e.title) + '</option>'; }).join('');
    w.innerHTML = '<div class="toolbar"><label>Bài: <select class="ex">' + exOpts + '</select></label> <label>Dữ liệu: <select class="ds">' + dsOpts + '</select></label></div>' +
      '<div class="ex-task"></div>' +
      '<div class="cols"><div><h4>Dữ liệu (Turtle — sửa được)</h4><textarea class="data" rows="14"></textarea></div>' +
      '<div><h4>Truy vấn của bạn</h4><textarea class="q" rows="14" placeholder="PREFIX : <...>\nSELECT ?x WHERE { ?x a :Movie . }"></textarea></div></div>' +
      '<div class="toolbar"><button class="btn" data-a="run">▶ Chạy truy vấn</button><button class="btn ghost" data-a="cmp">⚖ So với đáp án</button><button class="btn ghost" data-a="sol">👁 Xem đáp án</button><button class="btn ghost" data-a="draw">◉ Vẽ đồ thị dữ liệu</button><span class="status muted"></span></div>' +
      '<div class="result"></div><div class="cmp"></div><div class="sol"></div><div class="graph-box" hidden></div>';
    var ds = $('.ds', w), ex = $('.ex', w), data = $('.data', w), q = $('.q', w), res = $('.result', w), status = $('.status', w);
    var cur = null, last = null;
    function setDs(name) { ds.value = name; data.value = DATA.datasets[name] || ''; }
    setDs(ds.value);
    ds.addEventListener('change', function () { setDs(ds.value); });
    ex.addEventListener('change', function () {
      cur = DATA.examples[ex.value] || null; $('.sol', w).innerHTML = ''; $('.cmp', w).innerHTML = ''; res.innerHTML = '';
      if (!cur) { $('.ex-task', w).innerHTML = ''; return; }
      setDs(cur.dataset);
      $('.ex-task', w).innerHTML = '<div class="task-box"><b>Đề:</b> ' + esc(cur.task || cur.title) + '</div>';
      q.value = cur.prefix || '';
    });
    // so khớp truy vấn bỏ qua comment, dòng PREFIX, khoảng trắng
    function stripQ(t) { return t.replace(/#[^\n]*/g, '').replace(/^\s*PREFIX\s+[\w\-]*:\s*<[^>]*>\s*$/gim, '').replace(/\s+/g, ' ').trim(); }
    function queryPf(t) { var p = {}; t.replace(/PREFIX\s+([\w\-]*):\s*<([^>]+)>/gi, function (m, a, b) { p[a] = b; }); return p; }
    function pnames(t) {
      var out = [], body = t.replace(/^\s*PREFIX[^\n]*$/gim, '').replace(/<[^>]*>/g, ' ').replace(/"[^"]*"/g, ' ').replace(/#[^\n]*/g, '');
      body.replace(/(^|[\s(,;{\/^|!])([A-Za-z][\w\-]*)?:([A-Za-z_][\w\-]*)/g, function (m, b, pf, loc) { out.push([pf || '', loc]); });
      return out;
    }
    var STDNS = Object.keys(RDF.STD).map(function (k) { return RDF.STD[k]; });
    // chọn bộ dữ liệu khớp nhất với các tên (pf:local) mà truy vấn dùng
    function guessDs(text) {
      var qp = queryPf(text), names = pnames(text), best = null, bestScore = 0;
      Object.keys(DATA.datasets).forEach(function (k) {
        var ttl = DATA.datasets[k], dp = pfOf(ttl), score = 0, seen = {};
        names.forEach(function (n) {
          var ns = qp[n[0]] || dp[n[0]]; if (!ns || STDNS.indexOf(ns) >= 0 || seen[n.join(':')]) return;
          seen[n.join(':')] = 1;
          Object.keys(dp).forEach(function (p2) { if (dp[p2] === ns && new RegExp('(^|[\\s;,(\\[])' + p2 + ':' + n[1] + '(?![\\w\\-])').test(ttl)) score++; });
        });
        if (score > bestScore) { bestScore = score; best = k; }
      });
      return best;
    }
    function clearOut() { res.innerHTML = ''; $('.cmp', w).innerHTML = ''; $('.sol', w).innerHTML = ''; $('.ex-task', w).innerHTML = ''; status.textContent = ''; }
    w._setQuery = function (text) {
      clearOut(); cur = null; ex.value = '';
      var hit = DATA.examples.filter(function (e) { return stripQ(e.query) === stripQ(text); })[0];
      if (hit) {
        ex.value = DATA.examples.indexOf(hit); cur = hit; setDs(hit.dataset); q.value = text;
        $('.ex-task', w).innerHTML = '<div class="task-box"><b>Đề:</b> ' + esc(hit.task || hit.title) + '</div>';
        return;
      }
      var k = guessDs(text);
      if (k) {
        setDs(k);
        // truy vấn trích thiếu PREFIX → chèn prefix của bộ dữ liệu
        var qp = queryPf(text), dp = pfOf(DATA.datasets[k]), add = [];
        pnames(text).forEach(function (n) { if (!qp[n[0]] && (dp[n[0]] || RDF.STD[n[0]]) && add.indexOf(n[0]) < 0) add.push(n[0]); });
        q.value = add.map(function (p) { return 'PREFIX ' + p + ': <' + (dp[p] || RDF.STD[p]) + '>'; }).join('\n') + (add.length ? '\n' : '') + text;
        $('.ex-task', w).innerHTML = '<div class="task-box">Đã tự chọn dữ liệu <b>' + esc(k) + '</b> cho truy vấn này' + (add.length ? ' và thêm ' + add.length + ' dòng PREFIX còn thiếu' : '') + '. Bấm <b>▶ Chạy truy vấn</b>.</div>';
      } else {
        q.value = text;
        $('.ex-task', w).innerHTML = '<div class="task-box">⚠ Truy vấn minh hoạ — không có bộ dữ liệu nào chứa các tên này. Muốn chạy thì dán dữ liệu Turtle vào ô bên trái.</div>';
      }
    };
    function run(query) {
      status.textContent = 'Đang chạy…';
      return loadOx().then(function (ox) {
        var st = new ox.Store(), r;
        try { st.load(data.value, {format: 'text/turtle', base_iri: 'http://example.org/'}); }
        catch (e) { throw new Error('Lỗi ở ô DỮ LIỆU (Turtle): ' + (e && e.message || e)); }
        try { r = st.query(query); }
        catch (e) {
          var msg = String(e && e.message || e), hint = '';
          if (/prefix/i.test(msg) || /not\s+(been\s+)?declared|unknown prefix/i.test(msg)) hint = ' — thiếu dòng PREFIX cho một tiền tố đang dùng.';
          throw new Error('Lỗi ở ô TRUY VẤN: ' + msg + hint);
        }
        status.textContent = 'Xong · dữ liệu có ' + st.size + ' triple';
        return r;
      });
    }
    function toTable(r) {
      if (typeof r === 'boolean') return {type: 'ASK', value: r};
      if (!r.length) return {type: 'SELECT', vars: [], rows: []};
      if (r[0] instanceof Map) {
        var vars = []; r.forEach(function (m) { m.forEach(function (v, k) { if (vars.indexOf(k) < 0) vars.push(k); }); });
        vars = selectVars(last || '') || vars;
        return {type: 'SELECT', vars: vars, rows: r.map(function (m) { var o = {}; vars.forEach(function (v) { o[v] = norm(m.get(v)); }); return o; })};
      }
      return {type: 'CONSTRUCT', rows: r.map(function (qd) { return {s: norm(qd.subject), p: norm(qd.predicate), o: norm(qd.object)}; }), vars: ['s', 'p', 'o']};
    }
    function render(t, pf) {
      if (t.type === 'ASK') return '<p class="big">ASK ⇒ <b>' + t.value + '</b></p>';
      if (!t.rows.length) return '<p class="muted">(0 kết quả)</p>';
      return '<table class="res"><tr>' + t.vars.map(function (v) { return '<th>' + (t.type === 'CONSTRUCT' ? v : '?' + esc(v)) + '</th>'; }).join('') + '</tr>' +
        t.rows.map(function (r) { return '<tr>' + t.vars.map(function (v) { return '<td>' + esc(short(r[v], pf)) + '</td>'; }).join('') + '</tr>'; }).join('') + '</table><p class="muted">' + t.rows.length + ' dòng</p>';
    }
    function fail(e) { status.textContent = ''; res.innerHTML = '<p class="err">⚠ ' + esc(e && e.message || e) + '</p>'; }
    $$('button', w).forEach(function (b) {
      b.addEventListener('click', function () {
        var a = b.dataset.a, pf = pfOf(data.value);
        if (a === 'run') { last = q.value; run(q.value).then(function (r) { var t = toTable(r); w._lastT = t; res.innerHTML = render(t, pf); }).catch(fail); }
        else if (a === 'sol') { if (!cur) { $('.sol', w).innerHTML = '<p class="muted">Chọn một bài mẫu ở ô "Bài" trước.</p>'; return; }
          $('.sol', w).innerHTML = '<h4>Đáp án tham khảo</h4><pre>' + esc(cur.query) + '</pre><h4>Kết quả đúng</h4>' + render(cur.expected, pf) + (cur.note ? '<p>' + esc(cur.note) + '</p>' : ''); }
        else if (a === 'cmp') {
          if (!cur) { $('.cmp', w).innerHTML = '<p class="muted">Chọn một bài mẫu để so.</p>'; return; }
          last = q.value;
          run(q.value).then(function (r) {
            var t = toTable(r), e = cur.expected, ok;
            res.innerHTML = render(t, pf);
            if (e.type === 'ASK') ok = t.type === 'ASK' && t.value === e.value;
            else if (e.type === 'CONSTRUCT') ok = rowsKey(['s', 'p', 'o'], t.rows) === rowsKey(['s', 'p', 'o'], e.rows);
            else {
              // so theo giá trị từng dòng, không phụ thuộc tên biến
              var gc = /group_concat/i.test(q.value);
              var cell = function (x) { x = x || ''; return gc ? x.replace(/^"|"(@\w+)?$/g, '').split(/\s*[,;|]\s*/).sort().join(',') : x; };
              var a1 = t.rows.map(function (r) { return t.vars.map(function (v) { return cell(r[v]); }).sort().join('|'); }).sort().join('\n');
              var a2 = e.rows.map(function (r) { return e.vars.map(function (v) { return cell(r[v]); }).sort().join('|'); }).sort().join('\n');
              ok = a1 === a2;
            }
            var needOrder = ok && /order\s+by/i.test(cur.query) && !/order\s+by/i.test(q.value);
            $('.cmp', w).innerHTML = needOrder ? '<p class="no big">≈ Đúng các dòng kết quả, nhưng đề yêu cầu <b>sắp xếp</b> — thêm ORDER BY như đáp án.</p>'
              : ok ? '<p class="ok big">✔ Kết quả KHỚP đáp án (' + (e.rows ? e.rows.length + ' dòng' : e.value) + ').</p>'
              : '<p class="no big">✘ Chưa khớp. Kết quả đúng là:</p>' + render(e, pf);
          }).catch(fail);
        }
        else if (a === 'draw') { var gb = $('.graph-box', w); gb.hidden = !gb.hidden; if (!gb.hidden) renderGraph(gb, data.value); }
      });
    });
    if (pendingQ) { w._setQuery(pendingQ); pendingQ = null; }
  };

  /* ---------- khởi động ---------- */
  refreshProgress();
  $$('.step-row').forEach(function (r) { r.addEventListener('click', function (e) { if (e.target.closest('a')) return; if (location.hash.slice(1) === r.dataset.go) show(r.dataset.go); else location.hash = r.dataset.go; }); });
  var first = location.hash.slice(1) || store.get('last', 'HOME');
  if (!document.getElementById('p-' + first.split('/')[0])) first = 'HOME';
  try { history.replaceState(null, '', '#' + first); } catch (e) {}  // nút Back quay về đúng trang đầu
  route(first);

  // tự kiểm (chỉ chạy khi mở với ?selftest)
  if (/selftest/.test(location.search)) {
    var R = document.documentElement;
    ['D4', 'D7', 'PLAY'].forEach(function (id) { activate(document.getElementById('p-' + id)); });
    try { $('#p-D4 .widget button[data-a="all"]').click(); R.setAttribute('data-rdfs', $$('#p-D4 .widget .log table.res tr').length - $$('#p-D4 .widget .log table.res').length + ' rows; ' + ($('#p-D4 .widget .fix') || {}).textContent); } catch (e) { R.setAttribute('data-rdfs', 'ERR ' + e.message); }
    try { $('#p-D7 .widget button[data-a="all"]').click(); $('#p-D7 .widget button[data-a="proof"]').click(); R.setAttribute('data-dl', $('#p-D7 .widget .log').textContent.replace(/vì sao\?.*?(?=B\d|■)/g, '').slice(0, 900) + ' || ' + $('#p-D7 .widget .proof').textContent.slice(0, 400)); } catch (e) { R.setAttribute('data-dl', 'ERR ' + e.message); }
    var w = $('#p-PLAY .widget'), ex = $('.ex', w), results = [], idx = 0;
    function nextEx() {
      if (idx >= DATA.examples.length) { R.setAttribute('data-sparql', results.join(' ; ')); document.title = 'SELFTEST-DONE'; return; }
      ex.value = String(idx); ex.dispatchEvent(new Event('change'));
      $('.q', w).value = DATA.examples[idx].query;
      $('button[data-a="cmp"]', w).click();
      var my = idx++;
      var t0 = Date.now();
      (function wait() {
        var c = $('.cmp', w).textContent, e = $('.result', w).textContent;
        if (c || /⚠/.test(e) || Date.now() - t0 > 8000) { results.push(my + ':' + (/KHỚP/.test(c) ? 'OK' : 'FAIL ' + (e + c).slice(0, 120))); $('.cmp', w).innerHTML = ''; $('.result', w).innerHTML = ''; nextEx(); }
        else setTimeout(wait, 50);
      })();
    }
    nextEx();
  }
})();
