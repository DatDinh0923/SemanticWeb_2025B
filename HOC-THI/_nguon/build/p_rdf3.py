from pathlib import Path
p = Path(__file__).parent / "rdf.js"; s = p.read_text(encoding="utf-8")
def rep(old, new):
    global s
    assert old in s, old[:70]; s = s.replace(old, new, 1)
rep("""  function wrap(s, w) {""", """  // term → đúng cú pháp Turtle (dùng khi bảng vẽ xuất lại Turtle)
  function ttlTerm(t, prefixes) {
    if (t.t === 'iri') return compact(t.v, prefixes);
    if (t.t === 'bn') return '[]';
    if (!t.lang && t.dt && /XMLSchema#(integer|decimal|double|boolean)$/.test(t.dt)) return t.v;
    var q = '"' + String(t.v).replace(/\\/g, '\\\\').replace(/"/g, '\\\\"').replace(/\n/g, '\\n') + '"';
    if (t.lang) return q + '@' + t.lang;
    if (t.dt && !/XMLSchema#string$/.test(t.dt)) return q + '^^' + compact(t.dt, prefixes);
    return q;
  }

  function wrap(s, w) {""")
rep("nodes.push({id: id, label: wrap(label(t, pf), 28), shape: 'box', kind: 'lit'});",
    "nodes.push({id: id, label: wrap(label(t, pf), 28), shape: 'box', kind: 'lit', ttl: ttlTerm(t, pf)});")
rep(": {id: key, label: wrap(label(t, pf), 22), shape: 'ellipse', kind: 'iri'});",
    ": {id: key, label: wrap(label(t, pf), 22), shape: 'ellipse', kind: 'iri', ttl: ttlTerm(t, pf)});")
rep("edges.push({from: a, to: b, label: label(tr.p, pf)});", "edges.push({from: a, to: b, label: label(tr.p, pf), ttl: ttlTerm(tr.p, pf)});")
# lăn chuột trên đồ thị = cuộn trang (không bắt zoom); giữ phím Ctrl để phóng to thì dùng nút +/- của trình duyệt
rep("interaction: {dragNodes: true, zoomView: !opts.print, dragView: !opts.print, hover: false}",
    "interaction: {dragNodes: true, zoomView: !!opts.zoom, dragView: !opts.print, hover: false, navigationButtons: !opts.print && !opts.zoom, keyboard: false}")
rep("return {parse: parse", "return {ttlTerm: ttlTerm, parse: parse")
p.write_text(s, encoding="utf-8"); print("ok")
