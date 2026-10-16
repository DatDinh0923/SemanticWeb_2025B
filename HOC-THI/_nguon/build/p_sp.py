from pathlib import Path
p = Path(__file__).parent / "app.js"; s = p.read_text(encoding="utf-8")
def rep(old, new):
    global s
    assert old in s, old[:70]; s = s.replace(old, new, 1)
i = s.index("    function fail(e) {"); j = s.index("\n", i)
s = s[:i] + "    function fail(e) { status.textContent = ''; res.innerHTML = '<p class=\"err\">⚠ ' + esc(e && e.message || e) + '</p>'; }" + s[j:]
rep("""            $('.cmp', w).innerHTML = ok ? '<p class="ok big">✔ Kết quả KHỚP đáp án (' + (e.rows ? e.rows.length + ' dòng' : e.value) + ').</p>'""",
"""            var needOrder = ok && /order\s+by/i.test(cur.query) && !/order\s+by/i.test(q.value);
            $('.cmp', w).innerHTML = needOrder ? '<p class="no big">≈ Đúng các dòng kết quả, nhưng đề yêu cầu <b>sắp xếp</b> — thêm ORDER BY như đáp án.</p>'
              : ok ? '<p class="ok big">✔ Kết quả KHỚP đáp án (' + (e.rows ? e.rows.length + ' dòng' : e.value) + ').</p>'""")
# mở từ nút "▶ Mở trong SPARQL Playground" khi widget chưa khởi tạo
rep("btn.addEventListener('click', function () { location.hash = 'PLAY'; setTimeout(function () { var w = $('#p-PLAY .widget'); if (w && w._setQuery) w._setQuery(q); }, 0); });",
    "btn.addEventListener('click', function () { var w = $('#p-PLAY .widget'); if (w && w._setQuery) w._setQuery(q); else pendingQ = q; location.hash = 'PLAY'; });")
rep("  function attachSparqlBtn(pre) {", "  var pendingQ = null;\n  function attachSparqlBtn(pre) {")
rep("        else if (a === 'draw') { var gb = $('.graph-box', w); gb.hidden = !gb.hidden; if (!gb.hidden) renderGraph(gb, data.value); }\n      });\n    });\n",
    "        else if (a === 'draw') { var gb = $('.graph-box', w); gb.hidden = !gb.hidden; if (!gb.hidden) renderGraph(gb, data.value); }\n      });\n    });\n    if (pendingQ) { w._setQuery(pendingQ); pendingQ = null; }\n")
p.write_text(s, encoding="utf-8"); print("ok")
