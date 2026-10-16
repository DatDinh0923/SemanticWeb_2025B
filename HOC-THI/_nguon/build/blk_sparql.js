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
