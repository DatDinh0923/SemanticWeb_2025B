# -*- coding: utf-8 -*-
"""In PDF 2 lượt (điền số trang mục lục), đóng dấu header mã dạng + số trang, kiểm tra đen trắng."""
import subprocess, sys
from pathlib import Path
import fitz
import build

CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = build.OUT
HTML = (OUT / "in-thi.html").as_uri()


def chrome_pdf(dst, html=None):
    subprocess.run([CH, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=300000",
                    f"--print-to-pdf={dst}", html or HTML], check=True, capture_output=True)


def parts():
    res = []
    for pid in build.PRINT_ORDER:
        p = next(x for x in build.PAGES if x["id"] == pid)
        code = p["code"] if p["code"].startswith("D") else ""
        res.append((f'{code + " · " if code else ""}{p["title"]}', p["desc"][:40], code, p["title"]))
    res.append(("Phụ lục · Dữ liệu Turtle dùng cho bài SPARQL", "Tra khi viết truy vấn.", "", "Phụ lục · Dữ liệu"))
    return res


def norm(s):
    return " ".join(s.split())


def find_starts(pdf):
    d = fitz.open(pdf)
    texts = [norm(p.get_text()) for p in d]
    starts, last = {}, 1
    for name, desc, code, title in parts():
        for i in range(last, len(d)):
            if norm(desc) in texts[i] and norm(title)[:30] in texts[i]:
                starts[name] = i + 1
                last = i
                break
    return starts, len(d)


tmp = OUT / "_draft.pdf"
build.build_print()
chrome_pdf(tmp)
starts, n = find_starts(tmp)
print("lượt 1:", n, "trang;", starts)
build.build_print({k: str(v) for k, v in starts.items()})
chrome_pdf(tmp)
starts2, n = find_starts(tmp)
assert starts == starts2, ("số trang lệch", starts, starts2)

# đóng dấu header / footer
d = fitz.open(tmp)
font = fitz.Font(fontfile=r"C:\Windows\Fonts\arialbd.ttf")
seq = sorted((v, k) for k, v in starts.items())
for i, page in enumerate(d):
    pno = i + 1
    cur = None
    for v, k in seq:
        if v <= pno:
            cur = k
    w = page.rect.width
    tw = fitz.TextWriter(page.rect)
    if cur and pno > 1:
        label = "[" + cur.split(" · ")[0] + "]" if cur.startswith("D") else "[" + cur.split(":")[0][:40] + "]"
        title = cur if len(cur) < 70 else cur[:67] + "…"
        tw.append((36, 24), title, font=font, fontsize=8)
        lw = font.text_length(label, fontsize=11)
        tw.append((w - 36 - lw, 25), label, font=font, fontsize=11)
        page.draw_line((36, 30), (w - 36, 30), color=(0, 0, 0), width=0.6)
    foot = f"{pno} / {len(d)}"
    tw.append((w / 2 - font.text_length(foot, fontsize=9) / 2, page.rect.height - 18), foot, font=font, fontsize=9)
    tw.write_text(page, color=(0, 0, 0))
final = OUT / "TAI-LIEU-DAY-DU.pdf"
d.save(final, garbage=3, deflate=True)
d.close()
tmp.unlink()
(OUT / "draft.pdf").unlink(missing_ok=True)

# kiểm tra không có màu
d = fitz.open(final)
colored = []
for i, p in enumerate(d):
    pix = p.get_pixmap(dpi=40)
    s = pix.samples
    mx = 0
    for j in range(0, len(s), pix.n * 7):
        r, g, b = s[j], s[j + 1], s[j + 2]
        mx = max(mx, max(r, g, b) - min(r, g, b))
    if mx > 40:
        colored.append((i + 1, mx))
print("PDF:", final, len(d), "trang; trang có màu:", colored or "không có")

# ---------- CHEATSHEET 4 trang (bản cũ) → CHEATSHEET-4-TRANG.pdf ----------
CHEAT = (OUT / "cheatsheet.html").as_uri()
codes = ["D1", "D2", "D3", "D4", "D5", "D6", "D12", "D7", "D8", "D9", "D10", "D11"]
build.build_cheat()
chrome_pdf(tmp, CHEAT)
d = fitz.open(tmp)
page_of = {}
for c in codes:
    for i, p in enumerate(d):
        if any(b[4].strip().startswith(c + " · ") for b in p.get_text("blocks")):
            page_of[c] = i + 1
            break
d.close()
print("cheatsheet:", page_of)
build.build_cheat(page_of)
chrome_pdf(tmp, CHEAT)
d = fitz.open(tmp)
for i, page in enumerate(d):
    foot = f"Cheatsheet Semantic Web · trang {i + 1} / {len(d)}"
    page.wrap_contents()
    page.insert_text((page.rect.width / 2 - font.text_length(foot, fontsize=8) / 2, page.rect.height - 12), foot,
                     fontsize=8, fontname="arialbd", fontfile=r"C:/Windows/Fonts/arialbd.ttf", color=(0, 0, 0))
d.save(OUT / "CHEATSHEET-4-TRANG.pdf", garbage=3, deflate=True)
n = len(d)
d.close()
tmp.unlink()
(OUT / "_cheat.pdf").unlink(missing_ok=True)
print("CHEATSHEET-4-TRANG.pdf:", n, "trang")

# ---------- SỔ TAY LÀM BÀI → TAI-LIEU-IN.pdf ----------
import runpy
runpy.run_path(str(build.HERE / "sotay.py"), run_name="__main__")
