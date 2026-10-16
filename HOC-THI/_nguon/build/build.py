# -*- coding: utf-8 -*-
"""Ghép nội dung thành HOC-THI/index.html (web) và HOC-THI/in-thi.html (bản in)."""
import html, json, re, shutil, sys
from pathlib import Path
from markdown_it import MarkdownIt

HERE = Path(__file__).parent
SCR = HERE.parent
CONTENT = SCR / "content"
REPO = Path(r"C:\Users\hieunt15\SemanticWeb_OnTap")
ONTAP = REPO / "on-tap"
OUT = REPO / "HOC-THI"
OUT.mkdir(exist_ok=True)
(OUT / "data").mkdir(exist_ok=True)
(OUT / "lib").mkdir(exist_ok=True)


def vendor():
    """thư viện offline: vis-network + oxigraph (wasm nhúng base64) — web chạy không cần mạng"""
    import base64
    V = HERE / "vendor"
    shutil.copy(V / "vis-network.min.js", OUT / "lib" / "vis-network.min.js")
    shutil.copy(V / "mermaid.min.js", OUT / "lib" / "mermaid.min.js")
    js = (V / "ox-web.js").read_text(encoding="utf-8")
    js = re.sub(r"^export (function|class) ", r"\1 ", js, flags=re.M)
    js = re.sub(r"^export \{ initSync \};\s*$|^export default __wbg_init;\s*$", "", js, flags=re.M)
    js = js.replace("import.meta.url", "location.href")
    names = ["Store", "namedNode", "blankNode", "literal", "defaultGraph", "variable", "triple", "quad", "fromTerm", "fromQuad"]
    js = "(function(){\n" + js + "\nwindow.oxigraph={" + ",".join(f"{n}:{n}" for n in names) + ",init:__wbg_init,initSync:initSync};\n})();\n"
    b64 = base64.b64encode((V / "ox-web_bg.wasm").read_bytes()).decode()
    (OUT / "lib" / "oxigraph.js").write_text("window.OX_WASM='" + b64 + "';\n" + js, encoding="utf-8")
    if (ONTAP / "img").exists():
        shutil.copytree(ONTAP / "img", OUT / "img", dirs_exist_ok=True)

md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")

# mã dạng cũ trong on-tap/*.md -> mã dạng mới
OLD2NEW = {"1": "D5", "2": "D8", "3": "D12", "4": "D4", "5": "D1", "6": "D2", "7": "D3", "8": "D6", "9": "D11", "10": "D11"}


def read(p):
    p = Path(p)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _remap(chunk):
    # nhãn bước bao đóng (D1)…(Dn) KHÔNG phải mã dạng → đổi thành T1…Tn
    chunk = chunk.replace("(D1)…(Dn)", "(T1)…(Tn)").replace("D1…Dn", "T1…Tn")
    out, proof = [], False
    for line in chunk.split("\n"):
        if line.startswith("**B. Bao đóng"):
            proof = True
        elif proof and line.startswith("## "):
            proof = False
        if proof:
            line = re.sub(r"\bD([1-9])\b", r"T\1", line)
        else:
            line = re.sub(r"\bD(10|[1-9])\b", lambda m: OLD2NEW[m.group(1)], line)
        out.append(line)
    return "\n".join(out)


def clean_ontap(text):
    # bỏ qua khối mermaid (id nút D1, D2 là tên nút, không phải mã dạng)
    parts = re.split(r"(```mermaid[\s\S]*?```)", text)
    text = "".join(p if p.startswith("```mermaid") else _remap(p) for p in parts)
    text = text.replace("bài 5.9 của chính bạn cũng dùng triple này ở bước T2", "bài 5.9 cũng dùng triple này ở bước T2")
    text = re.sub(r"(?<!!)\[([^\]]+)\]\((?!https?:)[^)]*\)", r"\1", text)  # bỏ link nội bộ, giữ ảnh
    return deadrefs(text)


MDPAGE = {"00": "trang ⌂ Bắt đầu", "01": "trang D1–D4", "02": "trang D5", "03": "trang D12", "04": "trang D8",
          "05": "trang D11", "06": "trang D11"}


def deadrefs(text):
    """bỏ/đổi tham chiếu tới file không có trong HOC-THI (md, files/, .py, .docx, Notes.png…)"""
    text = "\n".join(l for l in text.split("\n") if "run_queries.py" not in l and not l.startswith("**Nguồn:** slide"))
    text = re.sub(r"\s*\(đã kiểm bằng máy: `files/rdfs_closure\.py`\)", " (đã kiểm bằng máy)", text)
    text = re.sub(r"`07-dap-an\.md`", "phần đáp án bên dưới", text)
    text = re.sub(r"`(0[0-6])-[\w\-]+\.md`(?:\s*§[\w.]+(?:,\s*§[\w.]+)*)?", lambda m: MDPAGE[m.group(1)], text)
    text = re.sub(r"<code>files/queries/(q\d+)[\w\-]*\.rq</code>", r"\1", text)
    text = re.sub(r"`files/queries/(q\d+)[\w\-]*(?:\.rq)?`", r"bài \1 (trang D8)", text)
    text = re.sub(r"`files/([\w\-]+)\.ttl`", r"dữ liệu `\1` (chọn trong SPARQL Playground)", text)
    text = re.sub(r"\s*Khớp bài giải `[^`]+`\.", "", text)
    text = re.sub(r"`?Course materials/pizza\.owl`?|`pizza\.owl`|pizza\.owl", "pizza ontology", text)
    text = re.sub(r"\s*·?\s*\*\*Nguồn:\*\*\s*Notes\.png\s*\(([^)]*)\)", r" · (ghi chú của thầy: \1)", text)
    text = text.replace("Notes.png", "ghi chú ôn thi").replace("(Notes)", "")
    # thống nhất quy ước + luật thi (tránh mâu thuẫn giữa các trang)
    text = text.replace("**ellipse nét đứt** = blank node", "**elip rỗng** (không ghi tên) = blank node")
    text = text.replace("nét đứt = blank node", "elip rỗng = blank node")
    text = text.replace("bấm giờ thật, không mở tài liệu, viết tay", "bấm giờ thật, chỉ dùng tài liệu giấy như khi thi thật, viết tay")
    text = re.sub(r"\s*→\s*xem [A-H]\d\.?", "", text)
    text = text.replace("| 7 | `(∀R.C)(a)` | For all `b` with `R(a,b) ∈ T`: add `C(b)` |\n",
                        "| 7 | `(∀R.C)(a)` | For all `b` with `R(a,b) ∈ T`: add `C(b)` |\n\n*Dịch:* **Add** = thêm vào nhánh đang xét · **Split** = tách thành 2 nhánh · **Choose an individual** = chọn một cá thể (nên chọn cá thể đang có ∀/∃) · **For all b with R(a,b) ∈ T** = với mọi b đã nối với a qua R.\n")
    return text


def headings(lines):
    """[(idx, level, text)] bỏ qua heading nằm trong code fence"""
    out, fence = [], False
    for i, l in enumerate(lines):
        if l.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            m = re.match(r"^(#{1,6})\s+(.*)", l)
            if m:
                out.append((i, len(m.group(1)), m.group(2).strip()))
    return out


def sect(text, prefix, include_head=True, quiet=False):
    lines = text.splitlines()
    hs = headings(lines)
    for k, (i, lv, t) in enumerate(hs):
        if ("#" * lv + " " + t).startswith(prefix) or t.startswith(prefix):
            end = len(lines)
            for (j, lv2, _) in hs[k + 1:]:
                if lv2 <= lv:
                    end = j
                    break
            return "\n".join(lines[i if include_head else i + 1:end])
    if not quiet:
        print("  !! không thấy mục:", prefix, file=sys.stderr)
    return ""


def shift(text, top):
    """dời cấp heading để heading lớn nhất thành cấp `top`"""
    lines = text.splitlines()
    hs = headings(lines)
    if not hs:
        return text
    d = top - min(lv for _, lv, _ in hs)
    for i, lv, t in hs:
        lines[i] = "#" * max(1, min(6, lv + d)) + " " + t
    return "\n".join(lines)


def tidy(text):
    lines, fence = text.split("\n"), False
    for i, l in enumerate(lines):
        if l.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence or not l.startswith("#"):
            continue
        l = re.sub(r"^(#+)\s+Phần [A-H] — ", r"\1 ", l)
        l = re.sub(r"^(#+)\s+[A-H]\d+\.\s+", r"\1 ", l)
        l = re.sub(r"^(#+)\s+\d\.\d+\s+", r"\1 ", l)
        l = re.sub(r"\s*\(★+[^)]*\)", "", l)
        l = re.sub(r"\s*\*\(bổ sung[^)]*\)\*", "", l)
        lines[i] = l
    return "\n".join(lines)


def render(text):
    text = tidy(text)
    text = re.sub(r"^(\s*)```\s*turtle\s+graph\s*$", r"\1```turtle-graph", text, flags=re.M)
    return md.render(text)


O = {n: clean_ontap(read(ONTAP / n)) for n in
     ["00-chien-luoc-lam-bai.md", "01-rdf-rdfs.md", "02-owl.md", "03-owl2-tableau.md", "04-sparql.md",
      "05-lod-modeling.md", "06-ly-thuyet.md", "07-de-thi-thu-1.md", "07-de-thi-thu-2.md", "07-dap-an.md"]}
C = {n: deadrefs(read(CONTENT / n)) for n in
     ["intro.md", "de-cu.md", "d7-datalog.md", "d9-dai-so-sparql.md", "d10-shacl.md", "d11-ly-thuyet.md", "luyen-de.md"]}


def ot(f, *prefixes):
    return "\n\n".join(shift(sect(O[f], p), 3) for p in prefixes)


def otb(f, prefix):
    return shift(sect(O[f], prefix, include_head=False), 3)


def ct(f, prefix, top=3):
    return shift(sect(C[f], prefix), top)


def ct_body(f, prefix):
    """nội dung của 1 mục '## ...' trong content, bỏ dòng heading, dời cấp con về 3"""
    return shift(sect(C[f], prefix, include_head=False), 3)


# ---- tách các câu đề cũ theo dạng ----
def qid(t):
    """'2022-1 · Câu 3 — …' → 'q-2022-1-c3' (neo để nhảy tới đúng câu)"""
    m = re.match(r"([\w\-]+)\s*·\s*Câu\s*(\d+)", t)
    return ("q-" + m.group(1) + "-c" + m.group(2)).lower() if m else None


def decu_blocks():
    """tách các câu đề cũ theo dạng: {dạng: [(id, tiêu đề, md)]} + danh sách theo đề"""
    lines = C["de-cu.md"].splitlines()
    hs = headings(lines)
    blocks, index = {}, []
    exam = ""
    for k, (i, lv, t) in enumerate(hs):
        if lv == 2:
            exam = t
            continue
        if lv != 3:
            continue
        end = len(lines)
        for (j, lv2, _) in hs[k + 1:]:
            if lv2 <= 3:
                end = j
                break
        body = "\n".join(lines[i:end])
        m = re.search(r"\*\*Dạng:\*\*\s*(D\d+)", body)
        if m:
            qi = qid(t)
            index.append((exam, qi, t, m.group(1), body))
            if qi:
                body = body.replace("### " + t, f'<a class="anchor" id="{qi}"></a>\n\n### ' + t, 1)
            blocks.setdefault(m.group(1), []).append((qi, t, shift(body, 4)))
    return blocks, index


DECU, DECU_INDEX = decu_blocks()


def decu_page():
    """trang Đề cũ: nguyên văn đề theo từng đề + nút nhảy tới chỗ làm bài (không chép lại lời giải)"""
    out, cur = [read_intro_decu()], None
    for exam, qi, t, d, body in DECU_INDEX:
        if exam != cur:
            out.append(f"\n\n## {exam}\n")
            cur = exam
        q = re.sub(r"<details[\s\S]*?</details>", "", body)
        q = re.sub(r"^> \*\*Dạng:\*\*.*$", "", q, flags=re.M)
        q = q.replace("### " + t, "### " + t, 1)
        link = f'\n\n<p><a class="btn sm" href="#{d}/{qi}">✍ Làm câu này + xem đáp án ở trang {d} →</a></p>\n' if qi else ""
        out.append(shift(q, 3) + link)
    return "\n".join(out)


def read_intro_decu():
    s = C["de-cu.md"]
    intro = s.split("## Đề 2023-3")[0].replace("## Đề cũ có lời giải", "").replace("---", "")
    return intro + "\n\n> Trang này chỉ in **nguyên văn đề** để bạn đọc cả đề một lượt (bấm giờ nếu muốn). Mỗi câu có nút **✍ Làm câu này** nhảy tới đúng chỗ trong trang dạng: ở đó có ô làm bài, gợi ý và đáp án.\n"


KHUON_D1 = """
**Bảng chọn cấu trúc: đề nói gì → viết gì**

| Đề nói… | Dùng cấu trúc |
|---|---|
| "A **nghĩ / cho rằng / nhận xét / cảm thấy** rằng X" | **Reification**: `[a rdf:Statement; rdf:subject …; rdf:predicate …; rdf:object …]`, A trỏ tới nút đó |
| "gồm / danh sách / theo thứ tự / nhóm tác giả" | **Collection** `( :a :b :c )` (bung ra rdf:first / rdf:rest / rdf:nil) hoặc `rdf:Seq`/`rdf:Bag` |
| "đạt điểm 10 môn X", "đặt lịch ngày …" (quan hệ ≥ 3 thành phần) | **n-ary** qua blank node: `:sv :score [ :value 10 ; :course :X ]` |
| "một người nào đó / không rõ tên" | **Blank node** `[]` |
| tên, tiêu đề, số, ngày | **Literal** (hình chữ nhật); ngày/số có `^^xsd:…`, ngôn ngữ `@vi`/`@en` |
| "là một …" | `rdf:type` (`a`) — **mọi** thực thể đều nên có `a :Lớp` |

"""

HOME_MD = """
## Đề thi trông như thế nào?

- Tự luận **2–3 tiếng**, được **mang tài liệu giấy** ⇒ không cần thuộc, cần **nhận ra dạng** và **làm theo các bước trong sổ tay**.
- **3 đề cũ đều có 5 câu**, mỗi câu vài ý nhỏ (đề không ghi điểm, ≈ 2 điểm/câu). Câu 1 luôn là **D1**; đề nào cũng có câu **OWL (D5)** và câu **SPARQL (D8 + D9)**; 2/3 đề có **SHACL (D10)**; mỗi đề có một câu suy diễn (D4, D6 hoặc D7).
- **Nghe nói năm nay:** câu SPARQL 2.5 điểm; câu OWL giống **"bài 3"** (Laboratory-course, có bài giải mẫu trong sổ tay D5).

## Bản đồ đề thi: thấy gì → dạng nào

| Dấu hiệu trong đề | Dạng | Đề cũ có ra | Ưu tiên |
|---|---|---|---|
| "Viết truy vấn **SPARQL** tìm…" (nghe nói 2.5đ) | **D8** SPARQL | 3/3 đề | ★★★★ |
| "Tạo dữ liệu RDF / viết Turtle **và vẽ đồ thị** cho đoạn văn…" | **D1** Turtle + đồ thị | 3/3 (luôn là Câu 1) | ★★★ |
| "Định nghĩa các lớp, thuộc tính bằng **RDFS + OWL**" / "biểu thức **DL**" / ontology | **D5** OWL + DL | 3/3 | ★★★ |
| "Viết **biểu thức đại số SPARQL**, giải thích từng bước" | **D9** Đại số | 3/3 (ý sau của câu SPARQL) | ★★★ |
| "Tầng nào (RDFS hay OWL) bổ sung ràng buộc để suy ra…" / "bộ-3 suy ra từ restriction" | **D6** Suy diễn OWL | 2/3 | ★★ |
| "Tạo **khuôn hình SHACL**…", "nút nào được kiểm, vi phạm" | **D10** SHACL | 2/3 | ★★ |
| "Viết các bộ-3 **suy ra được** trong RDFS" / "đúng hay sai (true/false/unknown)" | **D4** Suy diễn RDFS | 1/3 | ★★ |
| "Chương trình **Datalog**… vẽ **cây chứng minh**… tìm **điểm cố định**" | **D7** Datalog | 1/3 | ★★ |
| "Biểu diễn đồ thị sau bằng Turtle" / "Vẽ đồ thị cho các triple" / N-Triples / RDF/XML | **D2** Chuyển đổi | nằm trong D1 | ★ |
| "Dùng RDF/RDFS biểu diễn: URI1 là lớp, có domain…" / "vẽ đồ thị schema" | **D3** RDFS schema | nằm trong D5 | ★ |
| "Chứng minh bằng **tableau**", NNF, consistency, subsumption | **D12** Tableau | chưa ra | ★ |
| "Chức năng của **reasoner** trong KB?", câu hỏi lý thuyết, LOD | **D11** Lý thuyết | chưa ra riêng | ★ |

## Cách dùng web này

1. Đi theo **⚡ Lộ trình 3 giờ** ở trên (bấm vào từng dòng), cuối mỗi trang có nút **Tiếp theo →**. Xong dạng nào tick **"Tôi đã hiểu"** ở cuối trang dạng đó.
2. Đầu mỗi trang dạng có thẻ **⚡**: mở sổ tay đúng trang → tự làm đúng một câu (link) chỉ nhìn sổ tay → so đáp án. Phần còn lại của trang (**① Hiểu**, **② Khuôn**, **③ Bài tập tuần**, **④ Đề cũ**, **📚 Đọc thêm**) để tra khi chưa hiểu hoặc khi còn thời gian.
3. Trước mỗi đáp án có **ô tự làm** (tự lưu trên máy). Câu Turtle có nút **"Vẽ Turtle của tôi"** để thấy đồ thị bạn viết.
4. Nút **📋 Tra nhanh** (góc phải dưới) mở bảng tra ở mọi trang. Di chuột lên chữ gạch chấm để xem định nghĩa.
5. **SPARQL Playground** chạy truy vấn thật ngay trên trình duyệt và so với đáp án. **Bảng vẽ** để vẽ đồ thị RDF và tự sinh Turtle.
6. **TAI-LIEU-IN.pdf** cùng thư mục = **sổ tay làm bài @SOTAY_N@ trang** đen trắng để in 2 mặt mang vào phòng thi: mỗi dạng có các bước, bảng tra, bài giải mẫu và checklist. (TAI-LIEU-DAY-DU.pdf là bản đầy đủ, chỉ để tra trên máy — không cần in.)
"""

STEPS = [("TQ", 6, "TỔNG QUAN: Semantic Web là gì, 5 việc, 12 dạng bài nằm ở đâu (đọc trước tiên)"),
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

TRA_MD = """
## Prefix chuẩn (chép đầu mọi bài)

```turtle
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dc:   <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .    # một số lời giải dùng dcterms:
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix :     <http://example.org/> .
```

## Cú pháp Turtle rút gọn

| Viết | Nghĩa |
|---|---|
| `:s :p :o .` | 1 triple |
| `:s :p :o1 , :o2 .` | cùng s, p — nhiều object |
| `:s :p1 :o1 ; :p2 :o2 .` | cùng subject |
| `:s a :C .` | `:s rdf:type :C` |
| `[ :p :o ]` / `[]` | blank node |
| `( :a :b )` | collection: rdf:first / rdf:rest / rdf:nil |
| `"Hà Nội"@vi`, `"10"^^xsd:integer`, `10`, `"2024-01-01"^^xsd:date` | literal |
| `[ a rdf:Statement ; rdf:subject :s ; rdf:predicate :p ; rdf:object :o ]` | reification |

## SPARQL — khung và từ khoá

```sparql
PREFIX : <http://example.org/>
SELECT DISTINCT ?x ?y (COUNT(?z) AS ?n)
WHERE {
  ?x a :C ; :p ?y .                    # khớp mẫu
  OPTIONAL { ?x :label ?l FILTER(lang(?l) = "en") }   # "nếu có": FILTER của phần này để TRONG
  { ?x :q ?z } UNION { ?x :r ?z }      # "hoặc"
  FILTER (?y > 1990)
  FILTER NOT EXISTS { ?x :bad ?w }     # "không có"
  ?x :p+ ?anc .                        # đường đi bắc cầu (+ ≥1, * ≥0)
}
GROUP BY ?x ?y  HAVING (COUNT(?z) >= 2)
ORDER BY DESC(?n)  LIMIT 10
```

| Đề nói | Dùng |
|---|---|
| "nếu có / để trống nếu không" | `OPTIONAL` |
| "hoặc" | `UNION`, hoặc `FILTER (… \\|\\| …)`, hoặc `VALUES ?t { :A :B }` |
| "không có / chưa" | `FILTER NOT EXISTS { }` hoặc `MINUS { }` |
| "đếm / mỗi / tổng / trung bình" | `GROUP BY` + `COUNT / SUM / AVG / MIN / MAX` |
| "ít nhất 2", "nhiều hơn" | `HAVING (COUNT(?x) >= 2)` |
| "tất cả kể cả gián tiếp" | property path `:p+`, `rdfs:subClassOf*` |
| "khẳng định / sinh triple mới" | `CONSTRUCT { … } WHERE { … }` |
| "có … không?" | `ASK { … }` |
| "chứa chữ / bắt đầu bằng" | `FILTER regex(?s, "abc", "i")`, `CONTAINS`, `STRSTARTS` |
| "sắp xếp / top" | `ORDER BY DESC(?x) LIMIT k` |

**Dịch sang đại số (trong ra ngoài):** BGP → `Join` (các nhóm nối nhau) → `OPTIONAL` = `LeftJoin` → `UNION` = `Union` → `FILTER` = `Filter` bọc **cả nhóm** chứa nó → `GROUP BY` = `Extend(Group(…), ?n, COUNT(…))` → `ORDER BY` = `OrderBy` → `SELECT ?x` = `Project` → `DISTINCT` → `LIMIT` = `Slice`. OrderBy nằm **trong** Project.

## SHACL — khuôn

```turtle
:XShape a sh:NodeShape ;
  sh:targetClass :X ;                     # nút được kiểm = mọi ?n a :X
  sh:property [ sh:path :p ; sh:minCount 1 ; sh:maxCount 1 ;
                sh:datatype xsd:integer ; sh:minExclusive 1900 ] ;
  sh:property [ sh:path :q ; sh:class :Y ; sh:in ( :a :b ) ; sh:pattern "^A" ] .
```

## Datalog — khuôn

B0 = dữ kiện cho sẵn → B1 = B0 + mọi dữ kiện suy ra **từ B0** bằng 1 lần áp luật → B2 từ B1 → … dừng khi một bước không thêm gì: **điểm cố định**. Cây chứng minh: gốc = khẳng định, con = tiền đề của luật đã dùng, lá = dữ kiện.
"""


def tra_full():
    return (TRA_MD + "\n\n## Luật suy diễn RDFS\n\n" + shift(sect(O["01-rdf-rdfs.md"], "### B3.", include_head=False), 3)
            + "\n\n## OWL ↔ DL ↔ Manchester ↔ Turtle\n\n" + shift(sect(O["02-owl.md"], "### A7.", include_head=False), 3)
            + "\n\n## Tableau — 7 luật\n\n" + shift(sect(O["03-owl2-tableau.md"], "### 1.5", include_head=False), 3)
            + "\n\n## NNF\n\n" + shift(sect(O["03-owl2-tableau.md"], "### 1.4", include_head=False), 3))


def L(title, body):
    return f"\n\n## {title}\n\n{body}\n"


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
        out.append(f'<a class="anchor" id="d9-{qi}"></a>\n\n### {name}\n\n<p><a class="btn sm ghost" href="#D8/{qi}">Xem đề + truy vấn (trang D8) →</a></p>\n\n'
                   f'<details class="ans"><summary>Lời giải tóm tắt (biểu thức + kết quả từng bước)</summary>\n\n{s}\n\n</details>')
    return L("④ Đề thi cũ dạng này (tự làm → mở đáp án)", "\n\n".join(out))


def luyen(n):
    s = C["luyen-de.md"]
    body = shift(sect(s, f"## Đề {n}", include_head=False), 2)
    body = re.sub(r"^(## Câu (\d+)\b.*)$", lambda m: f'<a class="anchor" id="l{n}-c{m.group(2)}"></a>\n\n{m.group(1)}', body, flags=re.M)
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
         desc="Prefix, Turtle, SPARQL, luật RDFS, bảng OWL–DL, tableau, SHACL, Datalog. Cũng mở được bằng nút Tra nhanh ở góc phải dưới.", md=tra_full()),
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
            + L("③ Bài tập tuần — lời giải mẫu (che phần lời giải, tự làm trước)", ot("01-rdf-rdfs.md", "### Part 1 Ex4", "### Part 1 Ex6")) + decu("D2") + QUIZ("D2")),
    dict(id="D3", code="D3", title="RDFS: schema (lớp, thuộc tính, domain, range)", group="RDF & RDFS", track=True,
         desc="Đề bắt khai báo lớp, thuộc tính, domain/range bằng RDFS và vẽ đồ thị schema.",
         md=L("① Hiểu", D3_HIEU + "\n\n" + ot("01-rdf-rdfs.md", "### B1.", "### B2.", "### B5."))
            + L("② Khuôn làm bài", ot("01-rdf-rdfs.md", "### D3."))
            + L("③ Bài tập tuần — lời giải mẫu (che phần lời giải, tự làm trước)", ot("01-rdf-rdfs.md", "### Part 1 Ex3", "### Part 1 Ex5", "### Part 1 Ex7", "### Part 2 Ex1"))
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
         desc="Câu hỏi lý thuyết mở. Hay hỏi: \"chức năng của reasoner trong KB là gì\" — bài viết sẵn ngay dưới. (3 đề cũ chưa có câu lý thuyết riêng.)",
         md=L("① Câu hay hỏi: chức năng của reasoner", shift(sect(_d11, "### Câu mở", include_head=True), 3)
              + "\n\n> Câu \"liệt kê hết các khả năng của triple\" nằm ở trang **D1 → ② Khuôn làm bài**.")
            + L("② Hỏi đáp lý thuyết hay gặp", "### Q: Vẽ" + _d11.split("### Q: Vẽ", 1)[1])
            + EXTRA("nhập môn, Knowledge Graph, LPG, câu tổng hợp", ot("06-ly-thuyet.md", "## Phần A", "## Phần B", "## Phần C", "## Phần D", "## Phần E", "## Phần F"))
            + EXTRA("Linked Open Data & mô hình hoá tri thức", ot("05-lod-modeling.md", "## Phần A", "## Phần B", "## Phần C")) + QUIZ("D11")),
    dict(id="DECU", code="📄", title="Đề thi cũ (3 đề, nguyên văn)", group="Luyện đề", track=False,
         desc="Đọc cả đề một lượt. Mỗi câu có nút nhảy tới chỗ làm bài + đáp án trong trang dạng.", md=decu_page()),
    dict(id="LUYEN1", code="⏱1", title="Luyện đề 1: ghép từ 3 đề cũ", group="Luyện đề", track=False,
         desc="8 câu (đề thật 5 câu nhiều ý, ở đây tách nhỏ để luyện). Bấm giờ, tự làm, mở gợi ý → đáp án, tick barem để tự chấm.", md=luyen(1)),
    dict(id="LUYEN2", code="⏱2", title="Luyện đề 2: ghép từ bài tập tuần", group="Luyện đề", track=False,
         desc="8 câu tách nhỏ, dữ liệu lấy từ bài tập tuần.", md=luyen(2)),
    dict(id="LUYEN3", code="⏱3", title="Luyện đề 3: đề mới (miền Bệnh viện)", group="Luyện đề", track=False,
         desc="8 câu tách nhỏ, dữ liệu hoàn toàn mới — kiểm tra bạn đã nắm khuôn chưa.",
         md=luyen(3) + EXTRA("2 đề thi thử cũ (format 5 câu) + đáp án",
                             shift(O["07-de-thi-thu-1.md"], 3) + "\n\n" + shift(O["07-de-thi-thu-2.md"], 3) + "\n\n" + shift(O["07-dap-an.md"], 3))),
    dict(id="PLAY", code="▶", title="SPARQL Playground (chạy thật)", group="Công cụ", track=False,
         desc="Chọn bài mẫu → tự viết truy vấn → Chạy → So với đáp án. Chạy offline ngay trong trình duyệt.",
         md=W("sparql", "▶ SPARQL Playground")),
    dict(id="VE", code="✎", title="Bảng vẽ đồ thị RDF", group="Công cụ", track=False,
         desc="Vẽ nút/cạnh → Turtle tự sinh. Hoặc dán Turtle → ra đồ thị để sửa.",
         md=W("drawpad", "✎ Bảng vẽ đồ thị RDF") + "\n\n**Luyện:** P1 Ex4 (đồ thị Georges/Michael → Turtle) và P1 Ex6 (Turtle → đồ thị) ở trang **D2**; câu 1 các đề cũ ở trang **D1**."),
]

# lộ trình 3 giờ: học theo sổ tay in, thứ tự theo điểm kỳ vọng (tần suất trong 3 đề cũ) và kiến thức cần trước
# (trang, phút, việc làm, (neo câu tự làm, nhãn) hoặc None, lý do, chỉ làm nếu còn giờ)
CRASH = [
    ("TQ", 10, "Đọc trang này (5 việc, 7 từ). Rồi mở sổ tay trang 1: bảng tra dạng, thuật ngữ, ký hiệu vẽ.", None, "nền tảng", False),
    ("D1", 20, "Sổ tay D1: A, B, bài mẫu 2023. Rồi tự làm câu bên cạnh, bấm \"Vẽ Turtle của tôi\".", ("D1/q-2022-1-c1", "Đề 2022 · Câu 1"), "3/3 đề, luôn là Câu 1", False),
    ("D8", 30, "Sổ tay D8: A, B, bài mẫu 6390. Rồi tự viết truy vấn, chạy trong ▶ Playground (bộ dữ liệu \"luyện de3\").", ("LUYEN3/l3-c6", "Luyện đề 3 · Câu 6"), "3/3 đề, nghe nói 2.5đ", False),
    ("D9", 15, "Sổ tay D9: A, B, bài mẫu 1–3. Rồi tự lập bảng từng bước.", ("D9/d9-q-2022-1-c5", "Đề 2022 · Câu 5b"), "3/3 đề", False),
    ("D5", 30, "Sổ tay D5: A, B, bài mẫu 2 \"bài 3\" (đọc kỹ). Rồi tự làm câu bên cạnh.", ("D5/q-2023-3-c2", "Đề 2023 · Câu 2"), "3/3 đề, tin đồn bài 3", False),
    ("D6", 15, "Sổ tay D6: bảng B, hai bài mẫu.", ("LUYEN1/l1-c4", "Luyện đề 1 · Câu 4"), "2/3 đề", False),
    ("D10", 15, "Sổ tay D10: A, B, bài mẫu 1.", ("LUYEN1/l1-c8", "Luyện đề 1 · Câu 8"), "2/3 đề", False),
    ("D4", 10, "Sổ tay D4: bảng luật, bài mẫu 1.", ("LUYEN1/l1-c2", "Luyện đề 1 · Câu 2"), "1/3 đề", True),
    ("D7", 10, "Sổ tay D7: các bước, bài mẫu 2023.", ("LUYEN1/l1-c5", "Luyện đề 1 · Câu 5"), "1/3 đề", True),
    ("D2", 3, "Chỉ đọc Nhận dạng + A. Các bước trong sổ tay.", None, "nằm trong D1", True),
    ("D3", 3, "Chỉ đọc Nhận dạng + A. Các bước trong sổ tay.", None, "nằm trong D5", True),
    ("D12", 2, "Chỉ đọc Nhận dạng + A. Các bước; biết bài mẫu ở trang nào.", None, "chưa ra", True),
    ("D11", 2, "Chỉ đọc câu reasoner trong sổ tay.", None, "chưa ra riêng", True),
    ("HOME", 10, "Sáng mai: đọc \"Lỗi hay mất điểm\" cuối trang này, rồi dò mục D. Kiểm trước khi nộp của D8, D1, D5 trong sổ tay.", None, "trước giờ thi", False),
]
# thứ tự học duy nhất (lộ trình, nút "Tiếp theo"); menu bên trái vẫn nhóm theo chủ đề
ORDER = [c[0] for c in CRASH if c[0] != "HOME"] + ["LUYEN1", "LUYEN2", "LUYEN3"]
PAGE = {p["id"]: p for p in PAGES}


# ---------- dữ liệu SPARQL ----------
EXAM_DATA = {
    "đề 2023 · máy bay": """@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:Caspar a :Seaplane; :crew 2; :flight 1900.
:Convair a :Seaplane; :crew 1; :flight 1953.
:Su27 a :JetFighter; :crew 1.
:Mig35 a :JetFighter; :speed 2400.
:Mi26 a :Helicopter; :speed 295; :crew 5; :flight 1983; rdfs:label "Mil Mi-26".""",
    "đề 2022 · thú cưng": """@prefix bio: <http://exam.hust.edu.vn/bio/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
bio:Fido a bio:Dog; bio:offspring bio:Spot, bio:Ted.
bio:Milo a bio:Cat; bio:offspring bio:Kitty.
bio:Anna bio:own bio:Fido, bio:Milo.""",
    "đề 6390 · ngôn ngữ lập trình": """@prefix : <http://semweb.edu.vn/exam#> .
:CPP a :PL; :creator :bjarne_stroustrup; :hasFeature :type, :function, :pointer, :class, :template.
:C a :PL; :creator :dennis_ritchie; :hasFeature :type, :pointer, :function.
:Java a :PL; :creator :james_gosling; :hasFeature :type, :class.
:Python :hasFeature :function, :class .
:Lisp a :PL; :hasFeature :function.
:Ruby a :PL.""",
}
EXAM_Q = [
    ("Đề 2023-C4a · thủy phi cơ + trực thăng, kèm nhãn nếu có", "đề 2023 · máy bay",
     "Tìm các dòng thủy phi cơ (:Seaplane) và trực thăng (:Helicopter). Đầu ra: IRI dòng máy bay và nhãn rdfs:label nếu có, bỏ trống nếu không.",
     """PREFIX : <http://semweb.edu.vn/exam#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?p ?t ?label
WHERE {
  { ?p a ?t } OPTIONAL { ?p rdfs:label ?label }
  FILTER (?t = :Seaplane || ?t = :Helicopter)
}"""),
    ("Đề 2022-C5a · mèo của Anna và con của chúng", "đề 2022 · thú cưng",
     "Xuất danh sách những con mèo của Anna — gồm mèo Anna sở hữu và con của chúng.",
     """PREFIX bio: <http://exam.hust.edu.vn/bio/>
SELECT ?pet
WHERE {
  { bio:Anna bio:own ?pet . ?pet a bio:Cat . }
  UNION
  { bio:Anna bio:own ?x . ?x a bio:Cat . ?x bio:offspring ?pet . }
}"""),
    ("Đề 6390-C4a · NNLT có con trỏ hoặc lớp", "đề 6390 · ngôn ngữ lập trình",
     "Tìm các ngôn ngữ lập trình (:PL) có tính năng (hasFeature) con trỏ (:pointer) hoặc lớp (:class).",
     """PREFIX : <http://semweb.edu.vn/exam#>
SELECT DISTINCT ?pl
WHERE {
  ?pl a :PL ; :hasFeature ?f .
  FILTER (?f = :pointer || ?f = :class)
}"""),
    ("Đề 6390-C4b · NNLT kèm người sáng lập nếu có", "đề 6390 · ngôn ngữ lập trình",
     "Tìm các ngôn ngữ lập trình (PL) cùng người sáng lập nếu có, để trống nếu không.",
     """PREFIX : <http://semweb.edu.vn/exam#>
SELECT ?pl ?creator
WHERE {
  ?pl a :PL .
  OPTIONAL { ?pl :creator ?creator }
}"""),
    ("Đề 6390-C4c · CONSTRUCT :OOPL nếu có tính năng lớp", "đề 6390 · ngôn ngữ lập trình",
     "Tìm và khẳng định (construct) các ngôn ngữ là :OOPL nếu có tính năng lớp.",
     """PREFIX : <http://semweb.edu.vn/exam#>
CONSTRUCT { ?pl a :OOPL }
WHERE { ?pl :hasFeature :class }"""),
]


def norm_term(t):
    from rdflib import URIRef, BNode, Literal
    if t is None:
        return ""
    if isinstance(t, URIRef):
        return str(t)
    if isinstance(t, BNode):
        return "_:"
    if isinstance(t, Literal):
        if t.language:
            return f'"{t}"@{t.language}'
        dt = str(t.datatype or "")
        if re.search(r"XMLSchema#(integer|decimal|double|float|int|long|boolean)$", dt):
            return str(t)
        if dt and not dt.endswith("#string") and not dt.endswith("#langString"):
            return f'"{t}"^^{dt}'
        return f'"{t}"'
    return str(t)


def run_expected(ttl, q):
    from rdflib import Graph
    g = Graph()
    g.parse(data=ttl, format="turtle", publicID="http://example.org/")
    r = g.query(q)
    if r.type == "ASK":
        return {"type": "ASK", "value": bool(r.askAnswer)}
    if r.type == "CONSTRUCT":
        return {"type": "CONSTRUCT", "vars": ["s", "p", "o"], "rows": [{"s": norm_term(s), "p": norm_term(p), "o": norm_term(o)} for s, p, o in r]}
    vs = [str(v) for v in r.vars]
    return {"type": "SELECT", "vars": vs, "rows": [{v: norm_term(row[i]) for i, v in enumerate(vs)} for row in r]}


def sparql_data():
    datasets, examples = {}, []
    for f in sorted((ONTAP / "files").glob("*.ttl")):
        datasets[f.stem] = f.read_text(encoding="utf-8")
        shutil.copy(f, OUT / "data" / f.name)
    for k, v in EXAM_DATA.items():
        datasets[k] = v
    for f in sorted((CONTENT / "data").glob("*.ttl")):
        datasets["luyện " + f.stem] = f.read_text(encoding="utf-8")
        shutil.copy(f, OUT / "data" / ("luyen-" + f.name))
    for title, ds, task, q in EXAM_Q:
        examples.append(dict(title=title, dataset=ds, task=task, query=q, prefix=q.split("SELECT")[0].split("CONSTRUCT")[0].split("ASK")[0],
                             expected=run_expected(datasets[ds], q)))
    for f in sorted((ONTAP / "files" / "queries").glob("*.rq")):
        q = f.read_text(encoding="utf-8")
        lines = q.splitlines()
        ds = lines[0].split("data:")[1].strip().replace(".ttl", "")
        task = re.sub(r"^#\s*", "", lines[1]) if len(lines) > 1 and lines[1].startswith("#") else f.stem
        prefix = "\n".join(l for l in lines if l.upper().startswith("PREFIX")) + "\n"
        examples.append(dict(title=f"{f.stem} · {task[:70]}", dataset=ds, task=task, query="\n".join(lines[1:]), prefix=prefix,
                             expected=run_expected(datasets[ds], q)))
    return {"datasets": datasets, "examples": examples}


def jsonish(path, default):
    try:
        return json.loads(read(path) or json.dumps(default))
    except Exception as e:
        print("  !! JSON lỗi", path, e, file=sys.stderr)
        return default


def esc(s):
    return html.escape(s, quote=True)


def sotay_pages():
    """số trang từng dạng trong TAI-LIEU-IN.pdf (sotay.py ghi ra): {mã: (từ, đến)}, tổng số trang"""
    po = jsonish(HERE / "sotay_pages.json", {})
    n = po.pop("_total", 0)
    starts = sorted(po.items(), key=lambda kv: kv[1])
    rng = {"TQ": (1, 1), "HOME": None}
    for k, (c, a) in enumerate(starts):
        b = starts[k + 1][1] if k + 1 < len(starts) else n + 1
        rng[c] = (a, max(a, b - 1))
    return rng, n


def pdf_link(r):
    if not r:
        return ""
    t = f"tr.{r[0]}" if r[0] == r[1] else f"tr.{r[0]}–{r[1]}"
    return f'<a href="TAI-LIEU-IN.pdf#page={r[0]}" target="_blank" rel="noopener">📄 Sổ tay {t}</a>'


def crash_home(rng):
    rows, tot, core = [], 0, 0
    for k, (sid, mins, todo, ex, why, opt) in enumerate(CRASH, 1):
        q = PAGE[sid]
        tot += mins
        core += 0 if opt else mins
        code = q["code"] if q["code"].startswith("D") else ("⌂" if sid == "HOME" else "Bắt đầu")
        acts = " · ".join(x for x in [pdf_link(rng.get(sid)), f'<a href="#{ex[0]}">✍ {esc(ex[1])}</a>' if ex else ""] if x)
        rows.append(f'<div class="step-row{" later" if opt else ""}" data-go="{sid}"><span class="min">{k}. ≈{mins}′</span>'
                    f'<span><b>{esc(code)}</b> · {esc(q["title"])} <span class="why">{esc(why)}{" · nếu còn giờ" if opt else ""}</span>'
                    f'<br><span class="todo">{esc(todo)}{(" " + acts) if acts else ""}</span></span><span class="go btn sm ghost">Mở →</span></div>')
    more = "".join(f'<li><a href="#{i}">{esc(PAGE[i]["title"])}</a></li>' for i in ["LUYEN1", "LUYEN2", "LUYEN3", "DECU", "PLAY"])
    return (f'<h2>⚡ Lộ trình 3 giờ (học bằng sổ tay in)</h2>'
            f'<p><b>Bước 0:</b> in <a href="TAI-LIEU-IN.pdf" target="_blank" rel="noopener">TAI-LIEU-IN.pdf</a> 2 mặt rồi học trên chính bản giấy đó. Trong phòng thi bạn sẽ làm đúng như vậy: '
            f'<b>đọc câu → tra trang 1 → lật tới dạng → làm theo A. Các bước → so bài mẫu → dò checklist</b>.</p>'
            f'<p class="muted">Tổng ≈ {round(tot / 60, 1)} giờ. Thiếu giờ: làm trước các dòng không ghi "nếu còn giờ" (≈ {round(core / 60, 1)} giờ); còn dưới 2 giờ thì làm bước 1–5 (≈ {round(sum(c[1] for c in CRASH[:5]) / 60, 1)} giờ) và đọc "Lỗi hay mất điểm". '
            f'Mỗi dòng: mở sổ tay đúng trang → tự làm đúng một câu (link ✍) chỉ nhìn sổ tay → mở đáp án, ghi lỗi của mình vào lề sổ tay.</p>'
            f'<div class="steps">{"".join(rows)}</div>'
            f'<details class="extra" data-no-work><summary>Học thêm khi đã xong lộ trình</summary><ul>{more}</ul></details>')


def crash_card(sid, rng):
    k = next((i for i, c in enumerate(CRASH, 1) if c[0] == sid), None)
    if not k:
        return ""
    _, mins, todo, ex, why, opt = CRASH[k - 1]
    steps = [f"Mở {pdf_link(rng.get(sid))}: " + esc(todo) if rng.get(sid) else esc(todo)]
    if ex:
        steps.append(f'Tự làm <a href="#{ex[0]}">✍ {esc(ex[1])}</a> <b>chỉ nhìn sổ tay</b>, viết vào ô tự làm, rồi mới mở đáp án.')
        steps.append("So với đáp án; ghi lỗi của mình vào lề sổ tay giấy.")
    li = "".join(f"<li>{x}</li>" for x in steps)
    return (f'<div class="crash-card"><b>⚡ Lộ trình 3 giờ · bước {k}/{len(CRASH)} · ≈ {mins} phút</b> <span class="why">{esc(why)}{" · nếu còn giờ" if opt else ""}</span>'
            f'<ol>{li}</ol><p class="muted">Lúc này bỏ qua ③ bài tập tuần, 📚 Đọc thêm, Luyện thêm. Chỉ đọc ① Hiểu khi sổ tay chưa đủ rõ.</p></div>')


def build_web():
    vendor()
    rng, n_sotay = sotay_pages()
    nav, body, groups = [], [], []
    for p in PAGES:
        if p["group"] not in groups:
            groups.append(p["group"])
            nav.append(f'<div class="grp">{esc(p["group"])}</div>')
        nav.append(f'<a href="#{p["id"]}"><span class="code">{esc(p["code"])}</span><span>{esc(p["title"])}</span></a>')
        extra, html_md = "", render(p["md"].replace("@SOTAY_N@", str(n_sotay or "≤ 22")))
        if p["id"] == "HOME":
            extra = crash_home(rng)
        else:
            extra = crash_card(p["id"], rng)
        if p["id"] in ORDER:
            k = ORDER.index(p["id"])
            prv = ORDER[k - 1] if k > 0 else "HOME"
            nxt = ORDER[k + 1] if k + 1 < len(ORDER) else None
            nb = f'<a class="btn ghost" href="#{prv}">← {esc(PAGE[prv]["code"])} {esc(PAGE[prv]["title"])}</a>'
            if nxt:
                nb += f'<a class="btn" href="#{nxt}">Tiếp theo: {esc(PAGE[nxt]["code"])} {esc(PAGE[nxt]["title"])} →</a>'
            html_md += f'<div class="nextpage">{nb}</div>'
        head = f'<div class="page-head"><span class="tag">{esc(p["code"])}</span><h1>{esc(p["title"])}</h1><p>{esc(p["desc"])}</p></div>'
        body.append(f'<section class="page" id="p-{p["id"]}"{" data-track" if p["track"] else ""} hidden>{head}{extra}{html_md}</section>')
    data = sparql_data()
    gloss = jsonish(CONTENT / "glossary.json", {})
    quiz = jsonish(CONTENT / "quiz.json", [])
    # xáo phương án (cố định theo seed) để đáp án đúng không dồn vào B
    import random
    for i, q in enumerate(quiz):
        opts = q.get("opts") or []
        if len(opts) < 2 or not isinstance(q.get("a"), int) or any(re.search(r"(cả|tất cả).*(trên|đều)|A và B|B và C", o, re.I) for o in opts):
            continue
        order = list(range(len(opts)))
        random.Random(1000 + i).shuffle(order)
        q["a"] = order.index(q["a"])
        q["opts"] = [opts[k] for k in order]
    qref = render(tra_full())
    js_data = ("window.SW_DATA=" + json.dumps(data, ensure_ascii=False) + ";\nwindow.SW_GLOSS=" + json.dumps(gloss, ensure_ascii=False)
               + ";\nwindow.SW_QUIZ=" + json.dumps(quiz, ensure_ascii=False) + ";").replace("</", "<\\/")
    page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ôn thi Semantic Web</title>
<style>{read(HERE / "web.css")}</style>
</head><body>
<header id="top"><button id="menuBtn" class="btn sm ghost" aria-label="Mục lục">☰</button><h1>Ôn thi Semantic Web · 12 dạng bài</h1>
<div class="prog"><div class="bar"><div id="progBar"></div></div><span id="progTxt"></span></div></header>
<div id="layout"><nav id="nav">{''.join(nav)}</nav><main>{''.join(body)}</main></div>
<button id="qrefBtn" class="btn">📋 Tra nhanh</button>
<aside id="qref"><button id="qrefClose" class="btn sm">✕ Đóng</button><div class="qref"></div></aside>
<script>window.addEventListener("error",function(e){{document.documentElement.setAttribute("data-jserr",(e.message||"")+" @"+(e.lineno||""));}});{js_data}</script>
<script src="lib/vis-network.min.js"></script>
<script>{read(HERE / "rdf.js")}</script>
<script>{read(HERE / "app.js")}</script>
</body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print("index.html", round(len(page) / 1024), "KB;", len(data["examples"]), "bài SPARQL")


# ---------- bản in ----------
PRINT_ORDER = ["HOME", "TRA", "D1", "D2", "D3", "D4", "D5", "D6", "D12", "D7", "D8", "D9", "D10", "D11", "LUYEN1", "LUYEN2", "LUYEN3"]

PRINT_JS = r"""
(function(){
  document.querySelectorAll('details').forEach(function(d){d.open=true;});
  var list=[].slice.call(document.querySelectorAll('pre > code.language-turtle-graph'));
  var i=0;
  function next(){
    if(i>=list.length){mm();return;}
    var code=list[i++], pre=code.parentNode, box=document.createElement('div');
    box.className='graph-box';
    pre.parentNode.insertBefore(box, pre.nextSibling);
    try{
      RDF.drawSVG(box, code.textContent, function(svg){
        var fig=document.createElement('div'); fig.className='gfig'; fig.innerHTML=svg;
        box.parentNode.replaceChild(fig, box); next();
      });
    }catch(e){box.textContent='(không vẽ được đồ thị: '+e.message+')'; next();}
  }
  function done(){document.title='READY';window.__ready=true;}
  function mm(){
    var codes=[].slice.call(document.querySelectorAll('pre > code.language-mermaid'));
    if(!window.mermaid||!codes.length){done();return;}
    mermaid.initialize({startOnLoad:false,theme:'neutral',securityLevel:'loose',flowchart:{htmlLabels:false,useMaxWidth:true}});
    var k=0;
    (function one(){
      if(k>=codes.length){done();return;}
      var c=codes[k++], pre=c.parentNode;
      mermaid.render('pm'+k, c.textContent).then(function(r){var fig=document.createElement('div'); fig.className='gfig mmfig'; fig.innerHTML=r.svg; pre.parentNode.replaceChild(fig, pre); one();}).catch(function(){one();});
    })();
  }
  if(window.vis) next(); else mm();
})();
"""


def bw(h):
    """bỏ emoji màu cho bản in đen trắng"""
    h = h.replace("️", "").replace("✅", "✔").replace("❌", "✘").replace("⭐", "★").replace("⚠", "(!)")
    return re.sub(r"[\U0001F000-\U0001FFFF]", "", h)


def build_print(toc_pages=None):
    parts, toc = [], []
    for pid in PRINT_ORDER:
        p = next(x for x in PAGES if x["id"] == pid)
        code = p["code"] if p["code"].startswith("D") else ""
        name = f'{code + " · " if code else ""}{p["title"]}'
        text = p["md"]
        if pid == "HOME":
            text = HOME_MD.split("## Cách dùng web này")[0] + L("Lỗi hay mất điểm", otb("00-chien-luoc-lam-bai.md", "## 3.")) + L("Mẹo trình bày trên giấy", otb("00-chien-luoc-lam-bai.md", "## 5."))
        htmlp = bw(render(text))
        pg = (toc_pages or {}).get(name, "")
        toc.append(f'<div class="l1"><span>{esc(name)}</span><span class="d"></span><span>{pg}</span></div>')
        parts.append(f'<section class="part"><div class="part-head">{"<span class=tag>" + esc(code) + "</span>" if code else ""}<h1>{esc(p["title"])}</h1><p>{bw(esc(p["desc"]))}</p></div>{htmlp}</section>')
    # phụ lục dữ liệu
    data_md = "\n\n".join(f"### {f.name}\n\n```turtle\n{f.read_text(encoding='utf-8')}\n```" for f in sorted((OUT / 'data').glob('*.ttl')))
    name = "Phụ lục · Dữ liệu Turtle dùng cho bài SPARQL"
    toc.append(f'<div class="l1"><span>{esc(name)}</span><span class="d"></span><span>{(toc_pages or {}).get(name, "")}</span></div>')
    parts.append(f'<section class="part"><div class="part-head"><h1>Phụ lục · Dữ liệu Turtle dùng cho bài SPARQL</h1><p>Tra khi viết truy vấn.</p></div>{render(data_md)}</section>')
    cover = f"""<section class="cover"><div class="part-head"><h1>TÀI LIỆU MANG VÀO PHÒNG THI · SEMANTIC WEB</h1>
<p>12 dạng bài · khuôn làm bài · lời giải đầy đủ bài tập tuần, 3 đề cũ, 3 đề luyện 8 câu · bản đen trắng</p></div>
<h2>Mục lục</h2><div class="toc">{''.join(toc)}</div>
<p><b>Cách tra khi thi:</b> đọc câu hỏi → trang "Bắt đầu" (bảng <i>Dấu hiệu → Dạng</i>) → lật tới phần có khung mã dạng ở đầu trang (ví dụ <b>[D8]</b>) → chép khuôn → thay dữ liệu của đề.</p></section>"""
    page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Tai lieu in Semantic Web</title>
<style>{read(HERE / "print.css")}</style>
</head><body>{cover}{''.join(parts)}
<script src="lib/vis-network.min.js"></script><script src="lib/mermaid.min.js"></script><script>{read(HERE / "rdf.js")}</script><script>{PRINT_JS}</script></body></html>"""
    (OUT / "in-thi.html").write_text(page, encoding="utf-8")
    return [x for x in PRINT_ORDER]




# ---------- CHEATSHEET (bản in chính, ngắn) ----------
CHEAT_CSS = """
@page{size:A4;margin:9mm 8mm 11mm 8mm}
*{box-sizing:border-box;color:#000 !important;background:#fff !important}
body{margin:0;font:8.35pt/1.27 Arial,"Segoe UI",sans-serif}
.top h1{font-size:13pt;margin:0 0 3pt;border:2pt solid #000;padding:3pt 6pt}
.top p.sub{margin:0 0 4pt;font-style:italic}
.cols{column-count:2;column-gap:5mm;column-rule:0.6pt solid #000}
h2{font-size:10.5pt;margin:6pt 0 3pt;padding:2pt 5pt;border:1.6pt solid #000;break-after:avoid;break-inside:avoid}
h2 + *{break-before:avoid}
p{margin:2.5pt 0}
ul,ol{margin:2pt 0 2pt 13pt;padding:0}
li{margin:0.5pt 0}
code{font:7.9pt/1.25 Consolas,"Courier New",monospace}
pre{font:7.4pt/1.2 Consolas,"Courier New",monospace;border:0.6pt solid #000;padding:2.5pt 4pt;margin:3pt 0;white-space:pre-wrap;word-break:break-word;break-inside:avoid}
pre code{font:inherit}
table{border-collapse:collapse;margin:3pt 0;width:100%;font-size:7.9pt;break-inside:auto}
tr{break-inside:avoid}
th,td{border:0.6pt solid #000;padding:1pt 3pt;vertical-align:top;text-align:left}
th{font-weight:700}
.top table{font-size:8.6pt}
.gfig{text-align:center;margin:2pt 0;break-inside:avoid}.gfig svg{max-height:62mm;max-width:100%}.mmfig svg{filter:grayscale(1)}
em{font-style:italic}
"""


def build_cheat(page_of=None):
    text = read(HERE / "cheatsheet.md")
    head, rest = text.split("\n## D1 ", 1)
    rest = "## D1 " + rest
    if page_of:
        for code, pg in page_of.items():
            head = head.replace(f"| **{code}** |", f"| **{code}** · tr.{pg} |")
    page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Cheatsheet Semantic Web</title>
<style>{CHEAT_CSS}</style></head><body>
<div class="top"><h1>CHEATSHEET SEMANTIC WEB · mang vào phòng thi</h1>
<p class="sub">Đọc câu hỏi → bảng dưới tìm mã dạng → lật tới khung <b>D…</b> → chép khuôn, thay dữ liệu của đề. Bản đầy đủ: TAI-LIEU-DAY-DU.pdf (không cần in).</p>
{bw(render(head))}</div>
<div class="cols">{bw(render(rest))}</div>
<script src="lib/vis-network.min.js"></script><script src="lib/mermaid.min.js"></script><script>{read(HERE / "rdf.js")}</script><script>{PRINT_JS}</script></body></html>"""
    (OUT / "cheatsheet.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    build_web()
    toc = json.loads(sys.argv[1]) if len(sys.argv) > 1 else None
    build_print(toc)
    build_cheat()
    print("in-thi.html, cheatsheet.html xong")
