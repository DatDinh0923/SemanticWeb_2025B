from pathlib import Path
H = Path(__file__).parent

css = """
.tq-wrap{overflow-x:auto;margin:14px 0}
svg.tq{width:100%;min-width:640px;height:auto;font-family:inherit}
svg.tq text{fill:var(--ink);font-size:14px}
svg.tq .tq-h{font-weight:800;font-size:15px}
svg.tq .tq-s{fill:var(--muted);font-size:13px}
svg.tq .tq-mid{text-anchor:middle}
svg.tq .tq-code{fill:var(--accent);font-weight:800;font-size:15px;text-decoration:underline;cursor:pointer}
svg.tq .tq-box rect{fill:var(--panel);stroke:var(--line);stroke-width:2}
svg.tq .tq-main rect{stroke:var(--accent);stroke-width:2.5}
svg.tq .tq-line{fill:none;stroke:var(--muted);stroke-width:2}
svg.tq .tq-arrowhead{fill:var(--muted)}
"""
p = H / "web.css"
s = p.read_text(encoding="utf-8")
if "svg.tq" not in s:
    p.write_text(s + css, encoding="utf-8")

p = H / "build.py"
s = p.read_text(encoding="utf-8")
i = s.index("STEPS = [")
j = s.index("]\n", i) + 2
s = s[:i] + '''STEPS = [("TQ", 6, "TỔNG QUAN: Semantic Web là gì, 5 việc, 12 dạng bài nằm ở đâu (đọc trước tiên)"),
         ("D1", 7, "① Dữ liệu: câu văn → Turtle + vẽ đồ thị"),
         ("D2", 3, "① Dữ liệu: đồ thị ↔ Turtle ↔ N-Triples ↔ RDF/XML"),
         ("D3", 3, "② Định nghĩa: RDFS schema"),
         ("D4", 5, "③ Suy diễn RDFS (luật + cơ sở), true/unknown"),
         ("D8", 9, "④ Hỏi: viết truy vấn SPARQL (câu 2.5đ) + chạy thử Playground"),
         ("D9", 5, "④ Hỏi: đại số SPARQL — bảng từng bước"),
         ("D5", 6, "② Định nghĩa: ontology OWL + DL"),
         ("D6", 4, "③ Suy diễn OWL"),
         ("D12", 4, "③ Suy diễn bằng tableau"),
         ("D7", 3, "③ Suy diễn Datalog: cây chứng minh + điểm cố định"),
         ("D10", 3, "⑤ Kiểm tra: SHACL"),
         ("D11", 2, "Lý thuyết mở: reasoner, các dạng triple")]
''' + s[j:]
anchor = '    dict(id="TRA", code="📋"'
if 'dict(id="TQ"' not in s:
    s = s.replace(anchor, '''    dict(id="TQ", code="🧭", title="Tổng quan từ con số 0: 5 việc, 12 dạng", group="Bắt đầu", track=False,
         desc="Đọc trang này đầu tiên: Semantic Web là gì và mỗi dạng bài nằm ở đâu trong bức tranh chung.",
         md=read(HERE / "tongquan.md") + '\\n\\n<p><a class="btn" href="#D1">Học dạng đầu tiên: D1 →</a></p>'),
''' + anchor, 1)
p.write_text(s, encoding="utf-8")

p = H / "app.js"
s = p.read_text(encoding="utf-8")
old = "$$('.step-row').forEach(function (r) { r.addEventListener('click', function () { location.hash = r.dataset.go; }); });"
if old in s:
    s = s.replace(old, "$$('.step-row').forEach(function (r) { r.addEventListener('click', function () { if (location.hash.slice(1) === r.dataset.go) show(r.dataset.go); else location.hash = r.dataset.go; }); });")
old2 = "window.addEventListener('hashchange', function () { show(location.hash.slice(1)); });"
add2 = """
  // bấm link trỏ về đúng trang đang mở (hash không đổi) vẫn phải chạy
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (a && a.getAttribute('href') === location.hash) { e.preventDefault(); show(location.hash.slice(1)); }
  });"""
if add2.strip() not in s:
    s = s.replace(old2, old2 + add2)
p.write_text(s, encoding="utf-8")
print("ok")
