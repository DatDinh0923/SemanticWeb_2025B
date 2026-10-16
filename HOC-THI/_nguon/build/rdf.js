/* rdf.js — dùng chung cho web và bản in: Turtle mini-parser + vẽ đồ thị RDF (vis-network) */
var RDF = (function () {
  var RDFNS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#';
  var STD = {
    rdf: RDFNS, rdfs: 'http://www.w3.org/2000/01/rdf-schema#',
    owl: 'http://www.w3.org/2002/07/owl#', xsd: 'http://www.w3.org/2001/XMLSchema#',
    foaf: 'http://xmlns.com/foaf/0.1/', dc: 'http://purl.org/dc/elements/1.1/',
    dcterms: 'http://purl.org/dc/terms/', sh: 'http://www.w3.org/ns/shacl#',
    schema: 'http://schema.org/'
  };

  function lineCol(src, at) { var pre = src.slice(0, at).split('\n'); return 'dòng ' + pre.length + ', cột ' + (pre[pre.length - 1].length + 1); }

  function tokenize(src) {
    var toks = [], i = 0, n = src.length, m;
    function lc(at) { return lineCol(src, at); }
    function push(t, at) { t.pos = at; toks.push(t); }
    var reName = /^(?:[A-Za-z_À-￿][\wÀ-￿\-.]*)?:(?:[\wÀ-￿\-.:%+]*[\wÀ-￿\-:%+])?/;
    while (i < n) {
      var c = src[i];
      if (/\s/.test(c)) { i++; continue; }
      if (c === '#') { while (i < n && src[i] !== '\n') i++; continue; }
      var rest = src.slice(i);
      if (c === '<') { var j = src.indexOf('>', i); if (j < 0 || /[\s"]/.test(src.slice(i + 1, j))) throw new Error('Thiếu dấu ">" đóng IRI mở bằng "<" (' + lc(i) + ')'); push({k: 'iri', v: src.slice(i + 1, j)}, i); i = j + 1; continue; }
      if (c === '"' || c === "'") {
        var q = c, triple = rest.startsWith(q + q + q), s = '', k = i + (triple ? 3 : 1);
        var start = i;
        while (k < n) {
          if (src[k] === '\\') { var e = src[k + 1]; s += e === 'n' ? '\n' : e === 't' ? '\t' : e; k += 2; continue; }
          if (triple ? src.startsWith(q + q + q, k) : src[k] === q) break;
          s += src[k]; k++;
        }
        if (k >= n) throw new Error('Thiếu dấu ' + q + ' đóng chuỗi (' + lc(start) + ')');
        i = k + (triple ? 3 : 1);
        var tok = {k: 'lit', v: s, pos: start};
        if (src[i] === '@') { m = /^@([A-Za-z0-9\-]+)/.exec(src.slice(i)); if (!m) throw new Error('Sau "@" phải có mã ngôn ngữ, vd "Hà Nội"@vi (' + lc(i) + ')'); tok.lang = m[1]; i += m[0].length; }
        else if (src.startsWith('^^', i)) {
          i += 2;
          if (src[i] === '<') { var j2 = src.indexOf('>', i); if (j2 < 0) throw new Error('Thiếu ">" đóng kiểu dữ liệu (' + lc(i) + ')'); tok.dtIri = src.slice(i + 1, j2); i = j2 + 1; }
          else { m = reName.exec(src.slice(i)); if (!m || m[0].indexOf(':') < 0) throw new Error('Sau "^^" phải có kiểu, vd xsd:integer (' + lc(i) + ')'); tok.dtName = m[0]; i += m[0].length; }
        }
        toks.push(tok); continue;
      }
      if ((m = /^@?(prefix|base)\b/i.exec(rest)) && (c === '@' || /^(prefix|base)\s/i.test(rest))) {
        push({k: 'dir', v: m[1].toLowerCase(), isAt: c === '@'}, i); i += m[0].length; continue;
      }
      if ((m = /^[+-]?(\d+\.\d+|\.\d+|\d+)([eE][+-]?\d+)?/.exec(rest))) {
        push({k: 'num', v: m[0]}, i); i += m[0].length; continue;
      }
      if ((m = /^_:([\wÀ-￿\-]+)/.exec(rest))) { push({k: 'bnl', v: m[1]}, i); i += m[0].length; continue; }
      if ((m = /^(true|false)\b/.exec(rest))) { push({k: 'bool', v: m[1]}, i); i += m[0].length; continue; }
      if ((m = /^a(?=[\s\[<"(])/.exec(rest))) { push({k: 'a'}, i); i += 1; continue; }
      if ((m = reName.exec(rest)) && m[0].indexOf(':') >= 0) { push({k: 'pn', v: m[0]}, i); i += m[0].length; continue; }
      if ('.;,[]()'.indexOf(c) >= 0) { push({k: c}, i); i++; continue; }
      throw new Error('Không hiểu "' + rest.slice(0, 15).split('\n')[0] + '" (' + lc(i) + ') — tên phải có dấu ":" (vd :Ann), chuỗi phải trong ngoặc kép');
    }
    return toks;
  }

  function parse(src) {
    var toks = tokenize(src), p = 0, prefixes = {}, triples = [], bn = 0;
    function peek() { return toks[p] || {k: 'eof'}; }
    function next() { return toks[p++] || {k: 'eof'}; }
    function where(t) { return t && t.pos !== undefined ? ' (' + lineCol(src, t.pos) + ')' : ' (cuối văn bản)'; }
    function expect(k) { var t = next(); if (t.k !== k) throw new Error('Thiếu "' + k + '"' + where(t) + (t.k === 'eof' ? '' : ' — gặp "' + (t.v || t.k) + '"') + (k === '.' ? '. Mỗi câu Turtle kết thúc bằng dấu chấm.' : '')); return t; }
    function expand(pn) {
      var i = pn.indexOf(':'), pf = pn.slice(0, i), loc = pn.slice(i + 1);
      var ns = prefixes.hasOwnProperty(pf) ? prefixes[pf] : STD[pf];
      if (ns === undefined) { ns = 'http://example.org/' + (pf ? pf + '/' : ''); prefixes[pf] = ns; }  // dễ dãi: đoạn trích thiếu @prefix
      return ns + loc;
    }
    function newBn() { return {t: 'bn', v: 'b' + (++bn)}; }
    function add(s, pr, o) { triples.push({s: s, p: pr, o: o}); }
    function term(t) {
      if (t.k === 'iri') return {t: 'iri', v: t.v};
      if (t.k === 'pn') return {t: 'iri', v: expand(t.v)};
      if (t.k === 'a') return {t: 'iri', v: RDFNS + 'type'};
      if (t.k === 'bnl') return {t: 'bn', v: 'L_' + t.v};
      if (t.k === 'lit') return {t: 'lit', v: t.v, lang: t.lang, dt: t.dtIri || (t.dtName ? expand(t.dtName) : undefined)};
      if (t.k === 'num') return {t: 'lit', v: t.v, dt: STD.xsd + (/[eE]/.test(t.v) ? 'double' : t.v.indexOf('.') >= 0 ? 'decimal' : 'integer')};
      if (t.k === 'bool') return {t: 'lit', v: t.v, dt: STD.xsd + 'boolean'};
      throw new Error((t.k === 'eof' ? 'Câu Turtle bị cụt' : 'Không mong đợi "' + (t.v || t.k) + '"') + where(t));
    }
    function object() {
      var t = peek();
      if (t.k === '[') { next(); var b = newBn(); if (peek().k !== ']') predObjList(b); expect(']'); return b; }
      if (t.k === '(') { next(); return collection(); }
      return term(next());
    }
    function collection() {
      var items = [];
      while (peek().k !== ')') { if (peek().k === 'eof') throw new Error('Thiếu ")"'); items.push(object()); }
      next();
      if (!items.length) return {t: 'iri', v: RDFNS + 'nil'};
      var head = newBn(), cur = head;
      items.forEach(function (it, idx) {
        add(cur, {t: 'iri', v: RDFNS + 'first'}, it);
        var nx = idx === items.length - 1 ? {t: 'iri', v: RDFNS + 'nil'} : newBn();
        add(cur, {t: 'iri', v: RDFNS + 'rest'}, nx); cur = nx;
      });
      return head;
    }
    function predObjList(s) {
      for (;;) {
        var pr = term(next());
        for (;;) { add(s, pr, object()); if (peek().k === ',') { next(); continue; } break; }
        if (peek().k === ';') { while (peek().k === ';') next(); var k = peek().k; if (k === '.' || k === ']' || k === 'eof') return; continue; }
        return;
      }
    }
    while (peek().k !== 'eof') {
      var t = peek();
      if (t.k === 'dir') {
        next();
        if (t.v === 'prefix') { var pn = next(); var iri = expect('iri'); prefixes[pn.v.replace(/:$/, '')] = iri.v; }
        else expect('iri');
        if (t.isAt) expect('.'); else if (peek().k === '.') next();
        continue;
      }
      var s;
      if (t.k === '[') { next(); s = newBn(); if (peek().k !== ']') predObjList(s); expect(']'); if (peek().k === '.') { next(); continue; } }
      else if (t.k === '(') { next(); s = collection(); }
      else s = term(next());
      predObjList(s);
      expect('.');
    }
    return {triples: triples, prefixes: prefixes};
  }

  function compact(iri, prefixes) {
    var best = null, all = Object.assign({}, STD, prefixes || {});
    Object.keys(all).forEach(function (k) {
      var ns = all[k];
      if (ns && iri.indexOf(ns) === 0 && (!best || ns.length > all[best].length)) best = k;
    });
    if (best !== null && /^[\wÀ-￿\-.]*$/.test(iri.slice(all[best].length))) return best + ':' + iri.slice(all[best].length);
    return '<' + iri + '>';
  }
  function label(term, prefixes) {
    if (term.t === 'iri') return compact(term.v, prefixes);
    if (term.t === 'bn') return '';
    var s = term.v;
    if (term.lang) s = '"' + s + '"@' + term.lang;
    else if (term.dt && !/XMLSchema#(integer|decimal|double|boolean|string)$/.test(term.dt)) s = '"' + s + '"^^' + compact(term.dt, prefixes);
    return s;
  }

  // term → đúng cú pháp Turtle (dùng khi bảng vẽ xuất lại Turtle)
  function ttlTerm(t, prefixes) {
    if (t.t === 'iri') return compact(t.v, prefixes);
    if (t.t === 'bn') return '[]';
    if (!t.lang && t.dt && /XMLSchema#(integer|decimal|double|boolean)$/.test(t.dt)) return t.v;
    var q = '"' + String(t.v).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n') + '"';
    if (t.lang) return q + '@' + t.lang;
    if (t.dt && !/XMLSchema#string$/.test(t.dt)) return q + '^^' + compact(t.dt, prefixes);
    return q;
  }

  function wrap(s, w) {
    if (s.length <= w) return s;
    var out = [], line = '';
    s.split(/(?<=[\s_\-\/])/).forEach(function (part) {
      if ((line + part).length > w && line) { out.push(line); line = ''; }
      while (part.length > w) { out.push(part.slice(0, w)); part = part.slice(w); }
      line += part;
    });
    if (line) out.push(line);
    return out.join('\n');
  }

  // dựng dữ liệu nodes/edges theo quy ước vẽ của thầy
  function toVis(parsed) {
    var nodes = [], edges = [], seen = {}, litN = 0, pf = parsed.prefixes;
    function nodeId(t) {
      if (t.t === 'lit') {
        var id = 'lit' + (++litN);
        nodes.push({id: id, label: wrap(label(t, pf), 28), shape: 'box', kind: 'lit', ttl: ttlTerm(t, pf)});
        return id;
      }
      var key = t.t + ':' + t.v;
      if (!seen[key]) {
        seen[key] = 1;
        nodes.push(t.t === 'bn'
          ? {id: key, label: ' ', shape: 'ellipse', kind: 'bn', widthConstraint: {minimum: 46}, heightConstraint: {minimum: 26}}
          : {id: key, label: wrap(label(t, pf), 22), shape: 'ellipse', kind: 'iri', ttl: ttlTerm(t, pf)});
      }
      return key;
    }
    parsed.triples.forEach(function (tr) {
      var a = nodeId(tr.s), b = nodeId(tr.o);
      edges.push({from: a, to: b, label: label(tr.p, pf), ttl: ttlTerm(tr.p, pf)});
    });
    return {nodes: nodes, edges: edges};
  }

  var BW = {
    nodes: {color: {background: '#ffffff', border: '#000000', highlight: {background: '#ffffff', border: '#000000'}},
      font: {color: '#000000', face: 'Arial', size: 17}, borderWidth: 1.4, margin: 8},
    edges: {color: {color: '#000000', highlight: '#000000'}, arrows: {to: {enabled: true, scaleFactor: 0.6}},
      font: {color: '#000000', size: 14, face: 'Arial', strokeWidth: 4, strokeColor: '#ffffff', align: 'middle'},
      smooth: {enabled: true, type: 'dynamic'}, width: 1.2}
  };

  function draw(container, ttl, opts) {
    opts = opts || {};
    var parsed = parse(ttl), data = toVis(parsed);
    if (!data.nodes.length) throw new Error('Không có triple nào.');
    var n = data.nodes.length;
    container.style.height = (opts.height || Math.min(720, Math.max(260, 120 + n * 34))) + 'px';
    var options = {
      nodes: BW.nodes, edges: BW.edges,
      layout: {randomSeed: 11, improvedLayout: true},
      physics: {solver: 'forceAtlas2Based', forceAtlas2Based: {gravitationalConstant: -70, springLength: 95, springConstant: 0.08, avoidOverlap: 0.6},
        stabilization: {iterations: 600, fit: true}},
      interaction: {dragNodes: true, zoomView: !!opts.zoom, dragView: !opts.print, hover: false, keyboard: false}
    };
    var net = new vis.Network(container, {nodes: new vis.DataSet(data.nodes), edges: new vis.DataSet(data.edges)}, options);
    var froze = false;
    function freeze() { if (froze) return; froze = true; net.setOptions({physics: false}); net.fit(); if (opts.done) setTimeout(function () { opts.done(net); }, 60); }
    net.once('stabilizationIterationsDone', freeze); net.once('stabilized', freeze); setTimeout(freeze, 3000);
    return {net: net, parsed: parsed};
  }

  // dựng SVG đen trắng từ vị trí do vis tính (dùng cho bản in)
  function svgOf(data, pos) {
    var CW = 7.6, LH = 15, nodes = {}, out = [];
    var minX = 1e9, minY = 1e9, maxX = -1e9, maxY = -1e9;
    function xe(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
    data.nodes.forEach(function (n) {
      var p = pos[n.id], lines = n.kind === 'bn' ? [''] : String(n.label).split('\n');
      var w = Math.max.apply(null, lines.map(function (l) { return l.length; })) * CW;
      var g = {x: p.x, y: p.y, kind: n.kind, lines: lines};
      if (n.kind === 'lit') { g.hw = w / 2 + 8; g.hh = lines.length * LH / 2 + 6; }
      else if (n.kind === 'bn') { g.hw = 24; g.hh = 14; }
      else { g.hw = w / 2 + 16; g.hh = lines.length * LH / 2 + 9; }
      nodes[n.id] = g;
      minX = Math.min(minX, p.x - g.hw); maxX = Math.max(maxX, p.x + g.hw);
      minY = Math.min(minY, p.y - g.hh); maxY = Math.max(maxY, p.y + g.hh);
    });
    function edgePt(g, dx, dy) {
      var f;
      if (g.kind === 'lit') f = Math.min(g.hw / Math.max(Math.abs(dx), 1e-6), g.hh / Math.max(Math.abs(dy), 1e-6));
      else f = 1 / Math.sqrt(Math.pow(dx / g.hw, 2) + Math.pow(dy / g.hh, 2));
      return {x: g.x + dx * f, y: g.y + dy * f};
    }
    var pairCount = {};
    data.edges.forEach(function (e) {
      var a = nodes[e.from], b = nodes[e.to], dx = b.x - a.x, dy = b.y - a.y;
      var key = [e.from, e.to].sort().join('|'), k = pairCount[key] = (pairCount[key] || 0) + 1;
      var p1 = edgePt(a, dx, dy), p2 = edgePt(b, -dx, -dy);
      var mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2, len = Math.sqrt(dx * dx + dy * dy) || 1;
      var off = (k - 1) * 18, ox = -dy / len * off, oy = dx / len * off;
      out.push('<path d="M' + p1.x.toFixed(1) + ',' + p1.y.toFixed(1) + ' Q' + (mx + 2 * ox).toFixed(1) + ',' + (my + 2 * oy).toFixed(1) + ' ' + p2.x.toFixed(1) + ',' + p2.y.toFixed(1) + '" fill="none" stroke="#000" stroke-width="1.2" marker-end="url(#ah)"/>');
      out.push('<text x="' + (mx + ox).toFixed(1) + '" y="' + (my + oy + 4).toFixed(1) + '" text-anchor="middle" font-size="12" font-family="Arial" fill="#000" stroke="#fff" stroke-width="4" paint-order="stroke">' + xe(e.label) + '</text>');
    });
    var shapes = [];
    Object.keys(nodes).forEach(function (id) {
      var g = nodes[id];
      if (g.kind === 'lit') shapes.push('<rect x="' + (g.x - g.hw).toFixed(1) + '" y="' + (g.y - g.hh).toFixed(1) + '" width="' + (2 * g.hw).toFixed(1) + '" height="' + (2 * g.hh).toFixed(1) + '" fill="#fff" stroke="#000" stroke-width="1.3"/>');
      else shapes.push('<ellipse cx="' + g.x.toFixed(1) + '" cy="' + g.y.toFixed(1) + '" rx="' + g.hw.toFixed(1) + '" ry="' + g.hh.toFixed(1) + '" fill="#fff" stroke="#000" stroke-width="1.3"/>');
      g.lines.forEach(function (l, i) {
        shapes.push('<text x="' + g.x.toFixed(1) + '" y="' + (g.y - (g.lines.length - 1) * LH / 2 + i * LH + 4.5).toFixed(1) + '" text-anchor="middle" font-size="13" font-family="Arial" fill="#000">' + xe(l) + '</text>');
      });
    });
    var pad = 14, W = maxX - minX + 2 * pad, H = maxY - minY + 2 * pad;
    return '<svg xmlns="http://www.w3.org/2000/svg" class="gsvg" viewBox="' + (minX - pad).toFixed(0) + ' ' + (minY - pad).toFixed(0) + ' ' + W.toFixed(0) + ' ' + H.toFixed(0) + '" width="' + Math.min(W, 660).toFixed(0) + '" style="max-width:100%;height:auto">' +
      '<defs><marker id="ah" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#000"/></marker></defs>' +
      shapes.join('') + out.join('') + '</svg>';
  }
  // vẽ thành SVG: dùng vis để tính bố cục (không cần vẽ canvas)
  function drawSVG(container, ttl, cb) {
    var parsed = parse(ttl), data = toVis(parsed);
    container.style.width = '700px'; container.style.height = '600px';
    var net = new vis.Network(container, {nodes: new vis.DataSet(data.nodes), edges: new vis.DataSet(data.edges)}, {
      nodes: BW.nodes, edges: BW.edges, layout: {randomSeed: 11},
      physics: {solver: 'forceAtlas2Based', forceAtlas2Based: {gravitationalConstant: -70, springLength: 95, springConstant: 0.08, avoidOverlap: 0.6}, stabilization: {iterations: 800, fit: false, updateInterval: 200}}
    });
    var fired = false;
    function fin() { if (fired) return; fired = true; var svg = svgOf(data, net.getPositions()); net.destroy(); cb(svg); }
    net.once('stabilizationIterationsDone', fin);
    setTimeout(fin, 4000);
  }

  return {ttlTerm: ttlTerm, parse: parse, svgOf: svgOf, drawSVG: drawSVG, compact: compact, label: label, draw: draw, toVis: toVis, BW: BW, STD: STD, RDFNS: RDFNS};
})();
