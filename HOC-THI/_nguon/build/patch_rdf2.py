from pathlib import Path
H = Path(__file__).parent
def rep(s, old, new, count=1):
    assert old in s, old[:80]
    return s.replace(old, new, count)
p = H / "rdf.js"; s = p.read_text(encoding="utf-8")
s = rep(s, "    var toks = [], i = 0, n = src.length, m;\n",
"""    var toks = [], i = 0, n = src.length, m;
    function lc(at) { var pre = src.slice(0, at).split('\n'); return 'dòng ' + pre.length + ', cột ' + (pre[pre.length - 1].length + 1); }
    function push(t, at) { t.at = lc(at); toks.push(t); }
""")
s = rep(s, "if (c === '<') { var j = src.indexOf('>', i); toks.push({k: 'iri', v: src.slice(i + 1, j)}); i = j + 1; continue; }",
        "if (c === '<') { var j = src.indexOf('>', i); if (j < 0 || /[\s\"]/.test(src.slice(i + 1, j))) throw new Error('Thiếu dấu \">\" đóng IRI mở bằng \"<\" (' + lc(i) + ')'); push({k: 'iri', v: src.slice(i + 1, j)}, i); i = j + 1; continue; }")
s = rep(s, "        while (k < n) {\n", "        var start = i;\n        while (k < n) {\n")
s = rep(s, "        i = k + (triple ? 3 : 1);\n        var tok = {k: 'lit', v: s};",
        "        if (k >= n) throw new Error('Thiếu dấu ' + q + ' đóng chuỗi (' + lc(start) + ')');\n        i = k + (triple ? 3 : 1);\n        var tok = {k: 'lit', v: s, at: lc(start)};")
s = rep(s, "m = /^@([A-Za-z0-9\-]+)/.exec(src.slice(i)); tok.lang = m[1];",
        "m = /^@([A-Za-z0-9\-]+)/.exec(src.slice(i)); if (!m) throw new Error('Sau \"@\" phải có mã ngôn ngữ, vd \"Hà Nội\"@vi (' + lc(i) + ')'); tok.lang = m[1];")
s = rep(s, "if (src[i] === '<') { var j2 = src.indexOf('>', i); tok.dtIri",
        "if (src[i] === '<') { var j2 = src.indexOf('>', i); if (j2 < 0) throw new Error('Thiếu \">\" đóng kiểu dữ liệu (' + lc(i) + ')'); tok.dtIri")
s = rep(s, "else { m = reName.exec(src.slice(i)); tok.dtName = m[0];",
        "else { m = reName.exec(src.slice(i)); if (!m || m[0].indexOf(':') < 0) throw new Error('Sau \"^^\" phải có kiểu, vd xsd:integer (' + lc(i) + ')'); tok.dtName = m[0];")
# chuyển các toks.push còn lại sang push(…, i)
for a in ["toks.push({k: 'dir', v: m[1].toLowerCase(), at: c === '@'});", ]:
    s = rep(s, a, "push({k: 'dir', v: m[1].toLowerCase(), isAt: c === '@'}, i);")
s = rep(s, "toks.push({k: 'num', v: m[0]});", "push({k: 'num', v: m[0]}, i);")
s = rep(s, "toks.push({k: 'bnl', v: m[1]});", "push({k: 'bnl', v: m[1]}, i);")
s = rep(s, "toks.push({k: 'bool', v: m[1]});", "push({k: 'bool', v: m[1]}, i);")
s = rep(s, "toks.push({k: 'a'});", "push({k: 'a'}, i);")
s = rep(s, "toks.push({k: 'pn', v: m[0]});", "push({k: 'pn', v: m[0]}, i);")
s = rep(s, "toks.push({k: c});", "push({k: c}, i);")
s = rep(s, "throw new Error('Không hiểu ký tự \"' + rest.slice(0, 15) + '\" (vị trí ' + i + ')');",
        "throw new Error('Không hiểu \"' + rest.slice(0, 15).split('\n')[0] + '\" (' + lc(i) + ') — tên phải có dấu \":\" (vd :Ann), chuỗi phải trong ngoặc kép');")
s = rep(s, "if (t.at) expect('.');", "if (t.isAt) expect('.');")
s = rep(s, "function next() { return toks[p++] || {k: 'eof'}; }",
        "function next() { return toks[p++] || {k: 'eof'}; }\n    function where(t) { return t && t.at ? ' (' + t.at + ')' : ' (cuối văn bản)'; }")
s = rep(s, "if (t.k !== k) throw new Error('Thiếu \"' + k + '\" gần token thứ ' + p + ' (gặp ' + (t.v || t.k) + ')'); return t; }",
        "if (t.k !== k) throw new Error('Thiếu \"' + k + '\"' + where(t) + (t.k === 'eof' ? '' : ' — gặp \"' + (t.v || t.k) + '\"') + (k === '.' ? '. Mỗi câu Turtle kết thúc bằng dấu chấm.' : '')); return t; }")
s = rep(s, "throw new Error('Không mong đợi \"' + (t.v || t.k) + '\"');",
        "throw new Error((t.k === 'eof' ? 'Câu Turtle bị cụt' : 'Không mong đợi \"' + (t.v || t.k) + '\"') + where(t));")
p.write_text(s, encoding="utf-8"); print("ok")
