W = lambda name, title: f'\n\n<div class="widget" data-w="{name}" data-title="{title}"></div>\n\n'


def drop(text, *prefixes):
    """bỏ các mục con (theo tiêu đề) khỏi một khối md"""
    for p in prefixes:
        s = sect(text, p, quiet=True)
        if s:
            text = text.replace(s, "", 1)
        else:
            print("  !! drop: không thấy", p, file=sys.stderr)
    return text


def take(text, *prefixes):
    return "\n\n".join(sect(text, p) for p in prefixes)


def drop_line(text, start):
    """bỏ một đoạn 1 dòng bắt đầu bằng `start`, trả (text, đoạn đã bỏ)"""
    m = re.search(r"^" + re.escape(start) + r".*$", text, flags=re.M)
    if not m:
        print("  !! drop_line: không thấy", start, file=sys.stderr)
        return text, ""
    return text[:m.start()] + text[m.end():], m.group(0)


def EXTRA(title, body):
    return (f'\n\n<details class="extra" data-no-work><summary>📚 Đọc thêm: {title} (ít khả năng ra thi)</summary>\n\n'
            + body + "\n\n</details>\n")


def decu(d, top=3):
    b = DECU.get(d, [])
    return L("④ Đề thi cũ dạng này (tự làm → mở đáp án)", "\n\n".join(shift(x[2], top) for x in b)) if b else ""


QUIZ = lambda d: f'\n\n<div class="quiz" data-d="{d}"></div>'

# ---- nội dung từng dạng ----
_d1_intro = ct_body("intro.md", "D1 ")
D1_KHUON = take(_d1_intro, "4. Khuôn làm bài D1")
D1_HIEU = drop(_d1_intro, "4. Khuôn làm bài D1")
_d2_intro = ct_body("intro.md", "D2 ")
D2_KHUON = take(_d2_intro, "Khuôn đồ thị → Turtle", "Khuôn Turtle → đồ thị")
D2_HIEU = drop(_d2_intro, "Khuôn đồ thị → Turtle", "Khuôn Turtle → đồ thị")
D3_HIEU, _ = drop_line(ct_body("intro.md", "D3 "), "**Khuôn D3:**")
D5_HIEU = drop(ct_body("intro.md", "D5 "), "Khuôn thiết kế (6 bước)")
D6_HIEU, D6_KHUON = drop_line(ct_body("intro.md", "D6 "), "**Cách viết lời giải suy diễn OWL:**")
D8_HIEU = (ct_body("intro.md", "D8 ") + "\n\n" + drop(ot("04-sparql.md", "## Phần A"), "A1.", "A6.", "A7.", "A8.")
           + "\n\n" + drop(ot("04-sparql.md", "## Phần B"), "B5."))
D8_EXTRA = EXTRA("federation, Triple Pattern Fragments, named graph & UPDATE",
                 shift(sect(O["04-sparql.md"], "### A7."), 3) + "\n\n" + shift(sect(O["04-sparql.md"], "### A8."), 3) + "\n\n" + shift(sect(O["04-sparql.md"], "### B5."), 3))
D12_HIEU = ct_body("intro.md", "D12 ") + "\n\n" + drop(ot("03-owl2-tableau.md", "## 1."), "1.2", "1.4", "1.5")

_d7 = C["d7-datalog.md"]
_d9 = C["d9-dai-so-sparql.md"]
_d10 = C["d10-shacl.md"]
_d11 = C["d11-ly-thuyet.md"]


def d9_decu():
    """3 câu đại số đề cũ: đề nằm ở trang D8 (phần b), lời giải tóm tắt gấp lại"""
    refs = {"1": ("q-2023-3-c4", "2023-3 · Câu 4b"), "2": ("q-2022-1-c5", "2022-1 · Câu 5b"), "3": ("q-6390-c4", "6390 · Câu 4d")}
    out = ["Câu đại số trong đề cũ luôn là **phần (b)** của câu SPARQL. Đọc đề + truy vấn ở trang D8 (nút bên dưới), tự lập bảng từng bước, rồi mới mở lời giải."]
    for n in ("1", "2", "3"):
        s = sect(_d9, f"### Ví dụ mẫu {n}", include_head=False)
        s = re.sub(r"^> \*\*Dạng:\*\*.*$", "", s, flags=re.M)
        s = re.sub(r"Xem lời giải đầy đủ ở tab \*\*Đề cũ → [^*]+\*\*\. ", "", s)
        s = re.sub(r"\s*(Xem bảng từng bước ở tab Đề cũ\.|Xem đủ 7 bảng ở tab Đề cũ\.)", "", s)
        qi, name = refs[n]
        out.append(f'### {name}\n\n<p><a class="btn sm ghost" href="#D8/{qi}">Xem đề + truy vấn (trang D8) →</a></p>\n\n'
                   f'<details class="ans"><summary>Lời giải tóm tắt (biểu thức + kết quả từng bước)</summary>\n\n{s}\n\n</details>')
    return L("④ Đề thi cũ dạng này (tự làm → mở đáp án)", "\n\n".join(out))


def luyen(n):
    s = C["luyen-de.md"]
    body = shift(sect(s, f"## Đề {n}", include_head=False), 2)
    head = ""
    if n == 1:
        head = s.split("## Đề 1")[0].split("\n", 1)[1]
    return '<div class="timer"></div>\n\n' + head + "\n\n" + body


PAGES = [
    dict(id="HOME", code="⌂", title="Bắt đầu: lộ trình học & bản đồ đề thi", group="Bắt đầu", track=False,
         desc="Đọc trang này trước. Đi theo lộ trình, mỗi dòng mở một dạng bài.",
         md=HOME_MD + L("Lỗi hay mất điểm (đọc lại sáng ngày thi)", otb("00-chien-luoc-lam-bai.md", "## 3."))
            + L("Mẹo trình bày trên giấy", otb("00-chien-luoc-lam-bai.md", "## 5."))),
    dict(id="TQ", code="🧭", title="Tổng quan từ con số 0: 5 việc, 12 dạng", group="Bắt đầu", track=False,
         desc="Đọc trang này đầu tiên: Semantic Web là gì và mỗi dạng bài nằm ở đâu trong bức tranh chung.",
         md=read(HERE / "tongquan.md")),
    dict(id="TRA", code="📋", title="Bảng tra nhanh", group="Bắt đầu", track=False,
         desc="Prefix, Turtle, SPARQL, luật RDFS, bảng OWL–DL, tableau, SHACL, Datalog. Cũng mở được bằng nút 📋 ở góc phải dưới.", md=tra_full()),
    dict(id="D1", code="D1", title="Câu văn → Turtle + vẽ đồ thị RDF", group="RDF & RDFS", track=True,
         desc="Đề cho một đoạn văn → viết Turtle và vẽ đồ thị RDF, liệt kê HẾT các triple.",
         md=L("① Hiểu", D1_HIEU + "\n\n" + ot("01-rdf-rdfs.md", "### A2.", "### A4.", "### A6."))
            + L("② Khuôn làm bài", D1_KHUON + "\n\n" + KHUON_D1 + "\n\n" + ct("d11-ly-thuyet.md", "### Các khả năng của triple"))
            + L("③ Bài mẫu + bài tập tuần", ct("d11-ly-thuyet.md", "### Bài mẫu \"liệt kê hết\": Part 1 Ex1") + "\n\n" + ot("01-rdf-rdfs.md", "### Part 1 Ex2"))
            + decu("D1") + QUIZ("D1")),
    dict(id="D2", code="D2", title="Chuyển đổi đồ thị ↔ Turtle ↔ N-Triples ↔ RDF/XML", group="RDF & RDFS", track=True,
         desc="Đề cho đồ thị → viết Turtle / N-Triples / RDF-XML, hoặc ngược lại.",
         md=L("① Hiểu", D2_HIEU + "\n\n" + ot("01-rdf-rdfs.md", "### A3."))
            + L("② Khuôn làm bài", D2_KHUON + "\n\n> Luyện tay: mở **Bảng vẽ** ở thanh bên, vẽ đồ thị của đề → Turtle tự sinh để đối chiếu.")
            + L("③ Bài tập tuần (tự làm → mở đáp án)", ot("01-rdf-rdfs.md", "### Part 1 Ex4", "### Part 1 Ex6")) + decu("D2") + QUIZ("D2")),
    dict(id="D3", code="D3", title="RDFS: schema (lớp, thuộc tính, domain, range)", group="RDF & RDFS", track=True,
         desc="Đề bắt khai báo lớp, thuộc tính, domain/range bằng RDFS và vẽ đồ thị schema.",
         md=L("① Hiểu", D3_HIEU + "\n\n" + ot("01-rdf-rdfs.md", "### B1.", "### B2.", "### B5."))
            + L("② Khuôn làm bài", ot("01-rdf-rdfs.md", "### D3."))
            + L("③ Bài tập tuần (tự làm → mở đáp án)", ot("01-rdf-rdfs.md", "### Part 1 Ex3", "### Part 1 Ex5", "### Part 1 Ex7", "### Part 2 Ex1"))
            + decu("D3") + QUIZ("D3")),
    dict(id="D4", code="D4", title="Suy diễn RDFS: luật + cơ sở, true / unknown", group="RDF & RDFS", track=True,
         desc="Đề cho một đồ thị → viết các triple suy ra được (kèm tên luật) hoặc trả lời đúng / không xác định.",
         md=L("① Hiểu", ct_body("intro.md", "D4 ") + "\n\n" + ot("01-rdf-rdfs.md", "### B4."))
            + L("② Khuôn làm bài", ot("01-rdf-rdfs.md", "### D4.") + W("rdfs", "⚙ Bộ suy diễn RDFS từng bước — nhập KB, bấm Bước tiếp"))
            + L("③ Bài tập tuần (HW 5.9, 12.9)", ot("01-rdf-rdfs.md", "### Part 2 Ex2"))
            + decu("D4") + L("Tự luyện thêm (RDF/RDFS tổng hợp)", otb("01-rdf-rdfs.md", "## Phần F")) + QUIZ("D4")),
    dict(id="D5", code="D5", title="Thiết kế ontology OWL + biểu thức DL", group="OWL", track=True,
         desc="Đề cho câu mô tả → viết tiên đề OWL (Turtle), biểu thức DL (và Manchester nếu đề hỏi).",
         md=L("① Hiểu", D5_HIEU + "\n\n" + drop(ot("02-owl.md", "## Phần A"), "A7."))
            + L("② Khuôn làm bài", otb("02-owl.md", "## Phần B"))
            + L("③ Bài tập tuần (bài 3 laboratory-course, thuốc, phim)", ot("02-owl.md", "## Phần C", "## Phần D", "## Phần E"))
            + decu("D5") + L("Tự luyện thêm", otb("02-owl.md", "## Phần G")) + QUIZ("D5")),
    dict(id="D6", code="D6", title="Suy diễn OWL / reasoner", group="OWL", track=True,
         desc="Đề hỏi reasoner suy ra được gì, hoặc cần thêm tiên đề OWL nào để suy ra X (và không suy ra Y).",
         md=L("① Hiểu", D6_HIEU) + L("② Khuôn làm bài", D6_KHUON.replace("**Cách viết lời giải suy diễn OWL:**", "**4 bước viết lời giải:**"))
            + L("③ Bài tập tuần: Pizza (P3 Ex1)", otb("02-owl.md", "## Phần F"))
            + decu("D6") + QUIZ("D6")),
    dict(id="D12", code="D12", title="Tableau: NNF, 7 luật, consistency / subsumption", group="OWL", track=True,
         desc="Đề bắt chứng minh bằng tableau: KB nhất quán không, a có thuộc C không, C có bao hàm trong D không.",
         md=L("① Hiểu", D12_HIEU)
            + L("② Khuôn làm bài", otb("03-owl2-tableau.md", "## 2."))
            + L("③ Bài tập tuần (Pingu, Mary, Professor)", ot("03-owl2-tableau.md", "## 3.", "## 4."))
            + L("④ Tự luyện (tự làm → mở đáp án)", otb("03-owl2-tableau.md", "## 5.")) + QUIZ("D12")),
    dict(id="D7", code="D7", title="Datalog: cây chứng minh + điểm cố định", group="Datalog (luật)", track=True,
         desc="Đề cho chương trình Datalog → vẽ cây chứng minh và tính điểm cố định B0 → B1 → …",
         md=L("① Hiểu", shift(sect(_d7, "### Hiểu", include_head=False), 3))
            + L("② Khuôn làm bài", shift(sect(_d7, "### Khuôn", include_head=False), 3) + W("datalog", "⚙ Datalog từng bước — B0 → B1 → … → điểm cố định"))
            + L("③ Bài luyện (tự làm → mở đáp án)", take(_d7, "### Luyện tập 1", "### Luyện tập 2", "### Luyện tập 3"))
            + decu("D7") + QUIZ("D7")),
    dict(id="D8", code="D8", title="Viết truy vấn SPARQL (câu 2.5 điểm)", group="SPARQL", track=True,
         desc="Câu 2.5 điểm: viết truy vấn SPARQL từ câu hỏi tiếng Việt. Mọi truy vấn chạy thật được ở Playground.",
         md=L("① Hiểu", D8_HIEU)
            + L("② Khuôn viết truy vấn", otb("04-sparql.md", "## Phần C") + "\n\n### Bẫy hay gặp (tự kiểm trước khi nộp)\n\n" + otb("04-sparql.md", "## Phần F")
                + "\n\n> Mọi khối SPARQL có nút **▶ Mở trong SPARQL Playground** để chạy thật và so kết quả.")
            + L("③ 25 bài viết truy vấn (bài tập tuần, kết quả chạy thật)", otb("04-sparql.md", "## Phần D"))
            + decu("D8") + L("Luyện thêm: đoán kết quả truy vấn", otb("04-sparql.md", "## Phần E")) + D8_EXTRA + QUIZ("D8")),
    dict(id="D9", code="D9", title="Đại số SPARQL: dịch query → bảng từng bước", group="SPARQL", track=True,
         desc="Đi kèm câu SPARQL: dịch truy vấn sang biểu thức đại số và lập bảng kết quả từng bước.",
         md=L("① Hiểu", shift(take(_d9, "### Hiểu", "### Quy tắc dịch"), 3))
            + L("② Khuôn làm bài", shift(sect(_d9, "### Khuôn", include_head=False), 3))
            + L("③ Bài luyện (tự làm → mở đáp án)", take(_d9, "### Luyện tập 1", "### Luyện tập 2", "### Luyện tập 3"))
            + d9_decu() + QUIZ("D9")),
    dict(id="D10", code="D10", title="SHACL: khuôn hình, nút được kiểm, vi phạm", group="SHACL", track=True,
         desc="Đề bắt viết khuôn hình SHACL, chỉ ra nút nào được kiểm, nút nào vi phạm và sửa thế nào.",
         md=L("① Hiểu", shift(sect(_d10, "### Hiểu", include_head=False), 3))
            + L("② Khuôn làm bài", shift(sect(_d10, "### Khuôn", include_head=False), 3))
            + L("③ Bài luyện (tự làm → mở đáp án)", take(_d10, "### Luyện tập 1", "### Luyện tập 2", "### Luyện tập 3", "### Luyện tập 4"))
            + decu("D10") + QUIZ("D10")),
    dict(id="D11", code="D11", title="Lý thuyết mở: reasoner, OWA, RDFS vs OWL…", group="Lý thuyết", track=True,
         desc="Câu hỏi lý thuyết mở. Chắc chắn có: \"chức năng của reasoner trong KB là gì\" — bài viết sẵn ngay dưới.",
         md=L("① Câu chắc chắn ra: chức năng của reasoner", shift(sect(_d11, "### Câu mở", include_head=True), 3)
              + "\n\n> Câu \"liệt kê hết các khả năng của triple\" nằm ở trang **D1 → ② Khuôn làm bài**.")
            + L("② Hỏi đáp lý thuyết hay gặp", "### Q: Vẽ" + _d11.split("### Q: Vẽ", 1)[1])
            + EXTRA("nhập môn, Knowledge Graph, LPG, câu tổng hợp", ot("06-ly-thuyet.md", "## Phần A", "## Phần B", "## Phần C", "## Phần D", "## Phần E", "## Phần F"))
            + EXTRA("Linked Open Data & mô hình hoá tri thức", ot("05-lod-modeling.md", "## Phần A", "## Phần B", "## Phần C")) + QUIZ("D11")),
    dict(id="DECU", code="📄", title="Đề thi cũ (3 đề, nguyên văn)", group="Luyện đề", track=False,
         desc="Đọc cả đề một lượt. Mỗi câu có nút nhảy tới chỗ làm bài + đáp án trong trang dạng.", md=decu_page()),
    dict(id="LUYEN1", code="⏱1", title="Luyện đề 1: ghép từ 3 đề cũ", group="Luyện đề", track=False,
         desc="8 câu đúng format thi. Bấm giờ, tự làm, mở gợi ý → đáp án, tick barem để tự chấm.", md=luyen(1)),
    dict(id="LUYEN2", code="⏱2", title="Luyện đề 2: ghép từ bài tập tuần", group="Luyện đề", track=False,
         desc="8 câu đúng format thi, dữ liệu lấy từ bài tập tuần.", md=luyen(2)),
    dict(id="LUYEN3", code="⏱3", title="Luyện đề 3: đề mới (miền Bệnh viện)", group="Luyện đề", track=False,
         desc="8 câu đúng format thi, dữ liệu hoàn toàn mới — kiểm tra bạn đã nắm khuôn chưa.",
         md=luyen(3) + EXTRA("2 đề thi thử cũ (format 5 câu) + đáp án",
                             shift(O["07-de-thi-thu-1.md"], 3) + "\n\n" + shift(O["07-de-thi-thu-2.md"], 3) + "\n\n" + shift(O["07-dap-an.md"], 3))),
    dict(id="PLAY", code="▶", title="SPARQL Playground (chạy thật)", group="Công cụ", track=False,
         desc="Chọn bài mẫu → tự viết truy vấn → Chạy → So với đáp án. Chạy offline ngay trong trình duyệt.",
         md=W("sparql", "▶ SPARQL Playground")),
    dict(id="VE", code="✎", title="Bảng vẽ đồ thị RDF", group="Công cụ", track=False,
         desc="Vẽ nút/cạnh → Turtle tự sinh. Hoặc dán Turtle → ra đồ thị để sửa.",
         md=W("drawpad", "✎ Bảng vẽ đồ thị RDF") + "\n\n**Luyện:** P1 Ex4 (đồ thị Georges/Michael → Turtle) và P1 Ex6 (Turtle → đồ thị) ở trang **D2**; câu 1 các đề cũ ở trang **D1**."),
]

# thứ tự học duy nhất (lộ trình, menu, nút "Dạng tiếp theo")
ORDER = ["TQ", "D1", "D2", "D3", "D4", "D5", "D6", "D12", "D7", "D8", "D9", "D10", "D11", "LUYEN1", "LUYEN2", "LUYEN3"]
PAGE = {p["id"]: p for p in PAGES}

