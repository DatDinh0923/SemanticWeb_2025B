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

