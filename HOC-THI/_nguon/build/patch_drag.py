from pathlib import Path
H = Path(__file__).parent


def rep(s, old, new, count=1):
    assert old in s, old[:80]
    return s.replace(old, new, count)


p = H / "app.js"
s = p.read_text(encoding="utf-8")
# nút "Di chuyển" để thoát mọi chế độ thêm nút / nối cạnh
s = rep(s, """'<button class="btn sm" data-a="iri">＋ Nút IRI (elip)</button>' +""",
        """'<button class="btn sm" data-a="move">✋ Di chuyển / chọn</button>' +
      '<button class="btn sm" data-a="iri">＋ Nút IRI (elip)</button>' +""")
s = rep(s, """'<p class="muted">Bấm "＋" rồi bấm vào chỗ trống trên khung để đặt nút. Bấm đúp vào nút/cạnh để sửa nhãn. Kéo thả để sắp xếp.</p>' +""",
        """'<p class="muted"><b>Kéo thả:</b> nhấn giữ chuột <u>ngay trên một nút</u> rồi kéo (kéo chỗ trống = dời cả khung, lăn chuột = phóng to). ' +
      '<b>Thêm nút:</b> bấm "＋" rồi bấm vào chỗ trống. <b>Nối cạnh:</b> bấm "→ Nối cạnh" rồi kéo từ nút này sang nút kia (xong tự quay về chế độ Di chuyển). Bấm đúp vào nút/cạnh để sửa nhãn.</p>' +
      '<p class="mode muted">Chế độ: <b>✋ Di chuyển</b></p>' +""")
s = rep(s, "d.id = 'n' + (++seq); cb(d); sync();", "d.id = 'n' + (++seq); cb(d); sync(); setMode('move');")
s = rep(s, "d.label = l.trim(); cb(d); sync(); setTimeout(function () { net.addEdgeMode(); }, 0);",
        "d.label = l.trim(); cb(d); sync(); setMode('move');")
s = rep(s, """        if (a === 'iri' || a === 'lit' || a === 'bn') { pending = a; net.addNodeMode(); }
        else if (a === 'edge') net.addEdgeMode();""",
        """        if (a === 'move') setMode('move');
        else if (a === 'iri' || a === 'lit' || a === 'bn') { pending = a; setMode('node'); }
        else if (a === 'edge') setMode('edge');""")
s = rep(s, "    var pending = null;\n",
        """    var pending = null;
    function setMode(m) {
      try { net.disableEditMode(); } catch (e) {}
      if (m === 'node') net.addNodeMode();
      if (m === 'edge') net.addEdgeMode();
      $('.mode', w).innerHTML = 'Chế độ: <b>' + (m === 'node' ? '＋ Thêm nút — bấm vào chỗ trống' : m === 'edge' ? '→ Nối cạnh — kéo từ nút này sang nút kia' : '✋ Di chuyển (kéo nút để sắp xếp)') + '</b>';
    }
""")
# sau khi nạp: tắt physics chắc chắn (sự kiện + hẹn giờ dự phòng) để nút không bị kéo về chỗ cũ
s = rep(s, """        net.once('stabilizationIterationsDone', function () { net.setOptions({physics: false}); net.fit(); });
        net.stabilize(500);""",
        """        var froze = false;
        var freeze = function () { if (froze) return; froze = true; net.setOptions({physics: false}); net.fit(); };
        net.once('stabilizationIterationsDone', freeze); net.once('stabilized', freeze);
        net.stabilize(500); setTimeout(freeze, 2500);
        setMode('move');""")
p.write_text(s, encoding="utf-8")

p = H / "rdf.js"
s = p.read_text(encoding="utf-8")
s = rep(s, """    net.once('stabilizationIterationsDone', function () { net.setOptions({physics: false}); net.fit(); if (opts.done) setTimeout(function () { opts.done(net); }, 60); });""",
        """    var froze = false;
    function freeze() { if (froze) return; froze = true; net.setOptions({physics: false}); net.fit(); if (opts.done) setTimeout(function () { opts.done(net); }, 60); }
    net.once('stabilizationIterationsDone', freeze); net.once('stabilized', freeze); setTimeout(freeze, 3000);""")
p.write_text(s, encoding="utf-8")
print("ok")
