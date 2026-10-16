"""tái cấu trúc build.py: thứ tự học, khung ①–④, Đề cũ dạng chỉ mục, Luyện đề tách 3 trang"""
import re
from pathlib import Path
H = Path(__file__).parent
p = H / "build.py"
s = p.read_text(encoding="utf-8")


def rep(old, new, cnt=1):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, cnt)


def splice(a_marker, b_marker, new):
    global s
    a = s.index(a_marker)
    b = s.index(b_marker, a)
    s = s[:a] + new + s[b:]


# 1) sect có chế độ im lặng
rep("def sect(text, prefix, include_head=True):", "def sect(text, prefix, include_head=True, quiet=False):")
rep('    print("  !! không thấy mục:", prefix, file=sys.stderr)\n    return ""',
    '    if not quiet:\n        print("  !! không thấy mục:", prefix, file=sys.stderr)\n    return ""')

# 2) render dọn tiêu đề (bỏ "Phần A —", "A1.", "1.2", sao ★ trong tiêu đề)
rep('''def render(text):
    text = re.sub''', '''def tidy(text):
    lines, fence = text.split("\\n"), False
    for i, l in enumerate(lines):
        if l.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence or not l.startswith("#"):
            continue
        l = re.sub(r"^(#+)\\s+Phần [A-H] — ", r"\\1 ", l)
        l = re.sub(r"^(#+)\\s+[A-H]\\d+\\.\\s+", r"\\1 ", l)
        l = re.sub(r"^(#+)\\s+\\d\\.\\d+\\s+", r"\\1 ", l)
        l = re.sub(r"\\s*\\(★+[^)]*\\)", "", l)
        l = re.sub(r"\\s*\\*\\(bổ sung[^)]*\\)\\*", "", l)
        lines[i] = l
    return "\\n".join(lines)


def render(text):
    text = tidy(text)
    text = re.sub''')

# 3) otb = thân một mục (không tiêu đề)
rep("def ct(f, prefix, top=3):", '''def otb(f, prefix):
    return shift(sect(O[f], prefix, include_head=False), 3)


def ct(f, prefix, top=3):''')

# 4) đề cũ: neo + chỉ mục
splice("# ---- tách các câu đề cũ theo dạng ----", "KHUON_D1 = ", "# ---- tách các câu đề cũ theo dạng ----\n" + (H / "blk_decu.py").read_text(encoding="utf-8") + "\n\n")

# 5) khuôn D1: chỉ giữ bảng "đề nói → dùng" (khuôn 7 bước đã có)
rep('''**Khuôn trình bày (đủ điểm):** ① khai báo `@prefix` → ② tự đặt IRI cho từng thực thể (ghi rõ) → ③ viết Turtle → ④ vẽ đồ thị: IRI = elip, literal = chữ nhật, blank node = elip rỗng, mỗi triple = 1 mũi tên có nhãn predicate → ⑤ đếm số triple nếu đề giới hạn (vd "≤ 20 bộ-3").
''', "")
rep('KHUON_D1 = """\n', 'KHUON_D1 = """\n**Bảng chọn cấu trúc: đề nói gì → viết gì**\n\n')

# 6) HOME
rep("1. Đi theo **Lộ trình 60 phút** ở trên (bấm vào từng dòng). Xong dạng nào tick **\"Tôi đã hiểu\"** ở cuối trang dạng đó.",
    "1. Đi theo **Lộ trình** ở trên (bấm vào từng dòng), cuối mỗi trang có nút **Dạng tiếp theo →**. Xong dạng nào tick **\"Tôi đã hiểu\"** ở cuối trang dạng đó.")
rep("2. Mỗi trang dạng có 4 lớp: **① Hiểu** → **② Khuôn làm bài** → **③ Bài mẫu + bài tập tuần** → **④ Đề cũ & tự luyện**.",
    "2. Mỗi trang dạng có 4 lớp, đọc từ trên xuống: **① Hiểu** → **② Khuôn làm bài** → **③ Bài mẫu + bài tập tuần** → **④ Đề cũ** (tự làm rồi mới mở đáp án). Mục **📚 Đọc thêm** ở cuối trang là phần ít khả năng ra thi, bỏ qua nếu thiếu giờ.")
rep("3. Trước mỗi đáp án có **ô tự làm** (tự lưu). Viết Turtle xong bấm **\"Vẽ Turtle của tôi\"** để thấy đồ thị.",
    "3. Trước mỗi đáp án có **ô tự làm** (tự lưu trên máy). Câu Turtle có nút **\"Vẽ Turtle của tôi\"** để thấy đồ thị bạn viết.")
rep("| \"Chứng minh bằng **tableau**\", NNF, consistency, subsumption | **D12** Tableau | ★★★ |\n", "")
rep("| \"Chương trình **Datalog**… vẽ **cây chứng minh**… tìm **điểm cố định**\" | **D7** Datalog | ★★ |\n",
    "| \"Chứng minh bằng **tableau**\", NNF, consistency, subsumption | **D12** Tableau | ★★★ |\n| \"Chương trình **Datalog**… vẽ **cây chứng minh**… tìm **điểm cố định**\" | **D7** Datalog | ★★ |\n")

# 7) trang: thay toàn bộ PAGES
splice("W = lambda name, title:", "# ---------- dữ liệu SPARQL ----------", (H / "blk_pages.py").read_text(encoding="utf-8") + "\n")
# bỏ định nghĩa decu() cũ (đã có bản mới trong blk_pages)
s = re.sub(r"def decu\(d\):\n    b = DECU\.get\(d, \[\]\)\n    return L\([^\n]*\n\n\n", "", s, count=1)

# 8) build_web: lộ trình tính phút theo độ dài thật + nút trang tiếp theo
rep('''        extra = ""
        if p["id"] == "HOME":
            rows = "".join(f'<div class="step-row" data-go="{s}"><span class="min">{m} phút</span><span>{esc(t)}</span><span class="go btn sm ghost">Bắt đầu →</span></div>' for s, m, t in STEPS)
            extra = f'<h2>Lộ trình 60 phút</h2><div class="steps">{rows}</div>'
        head = f'<div class="page-head"><span class="tag">{esc(p["code"])}</span><h1>{esc(p["title"])}</h1><p>{esc(p["desc"])}</p></div>'
        body.append(f'<section class="page" id="p-{p["id"]}"{" data-track" if p["track"] else ""} hidden>{head}{extra}{render(p["md"])}</section>')''',
    '''        extra, html_md = "", render(p["md"])
        if p["id"] == "HOME":
            rows, tot = [], 0
            for sid in ORDER:
                q = PAGE[sid]
                mins = max(3, round(len(re.sub(r"<[^>]+>", "", render(q["md"]))) / 2600))
                tot += mins
                code = q["code"] if q["code"].startswith("D") else ("Đề" if sid.startswith("LUYEN") else "Bắt đầu")
                rows.append(f'<div class="step-row" data-go="{sid}"><span class="min">≈{mins} phút</span><span><b>{esc(code)}</b> · {esc(q["title"])}</span><span class="go btn sm ghost">Mở →</span></div>')
            extra = f'<h2>Lộ trình học (≈ {round(tot / 60, 1)} giờ nếu đọc hết)</h2><p class="muted">Thiếu giờ: ưu tiên TQ → D1 → D4 → D5 → D8 (câu 2.5đ) → D9 → D12 → các dạng còn lại; mỗi dạng đọc ② Khuôn + làm ④ Đề cũ.</p><div class="steps">{"".join(rows)}</div>'
        if p["id"] in ORDER:
            k = ORDER.index(p["id"])
            prv = ORDER[k - 1] if k > 0 else "HOME"
            nxt = ORDER[k + 1] if k + 1 < len(ORDER) else None
            nb = f'<a class="btn ghost" href="#{prv}">← {esc(PAGE[prv]["code"])} {esc(PAGE[prv]["title"])}</a>'
            if nxt:
                nb += f'<a class="btn" href="#{nxt}">Tiếp theo: {esc(PAGE[nxt]["code"])} {esc(PAGE[nxt]["title"])} →</a>'
            html_md += f'<div class="nextpage">{nb}</div>'
        head = f'<div class="page-head"><span class="tag">{esc(p["code"])}</span><h1>{esc(p["title"])}</h1><p>{esc(p["desc"])}</p></div>'
        body.append(f'<section class="page" id="p-{p["id"]}"{" data-track" if p["track"] else ""} hidden>{head}{extra}{html_md}</section>')''')

# 9) bản in: thứ tự mới
rep('PRINT_ORDER = ["HOME", "TRA", "D1", "D2", "D3", "D4", "D5", "D6", "D12", "D7", "D8", "D9", "D10", "D11", "LUYEN"]',
    'PRINT_ORDER = ["HOME", "TRA", "D1", "D2", "D3", "D4", "D5", "D6", "D12", "D7", "D8", "D9", "D10", "D11", "LUYEN1", "LUYEN2", "LUYEN3"]')
rep('            text = HOME_MD.split("## Cách dùng web này")[0] + L("Lỗi hay mất điểm", ot("00-chien-luoc-lam-bai.md", "## 3.")) + L("Mẹo trình bày trên giấy", ot("00-chien-luoc-lam-bai.md", "## 5."))',
    '            text = HOME_MD.split("## Cách dùng web này")[0] + L("Lỗi hay mất điểm", otb("00-chien-luoc-lam-bai.md", "## 3.")) + L("Mẹo trình bày trên giấy", otb("00-chien-luoc-lam-bai.md", "## 5."))')

p.write_text(s, encoding="utf-8")
print("ok")
