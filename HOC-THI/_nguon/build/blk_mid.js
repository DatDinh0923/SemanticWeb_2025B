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
  $('#qrefBtn').addEventListener('click', function () { var q = $('#qref'); q.classList.toggle('open'); activate(q); });
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

