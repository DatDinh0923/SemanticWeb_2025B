# -*- coding: utf-8 -*-
"""Bản in BAI-TAP-GIAI-CHI-TIET.pdf: bài tập tuần + đề cũ + lời giải, xếp theo dạng. In 2 lượt để điền số trang."""
import os
import subprocess
import fitz
import build

CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = build.OUT
HTML = (OUT / "bai-tap.html").as_uri()


def chrome_pdf(dst):
    subprocess.run([CH, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=300000",
                    f"--print-to-pdf={dst}", HTML], check=True, capture_output=True)


def norm(s):
    return " ".join(s.split())


def find_pages(pdf):
    """trang bắt đầu của từng dạng + trang của từng bài (bỏ trang bìa khi tìm)"""
    d = fitz.open(pdf)
    texts = [norm(p.get_text()) for p in d]
    n = len(d)
    cover_end = next(i for i, t in enumerate(texts) if "D1 Câu văn → Turtle" in t and i > 0 and "Mục lục theo dạng" not in t)
    parts, last = {}, cover_end
    for code, title, desc, _ in build.baitap_parts():
        for i in range(last, n):
            if norm(build.bw(desc))[:40] in texts[i] and norm(title)[:30] in texts[i]:
                parts[f"{code} · {title}"] = i + 1
                last = i
                break
    items, last = {}, cover_end
    for code, t in build.baitap_index():
        key = build.plain(t)[:40]
        for i in range(last, n):
            if key in texts[i]:
                items[t] = i + 1
                last = i
                break
    d.close()
    return parts, items, n


tmp = OUT / "_baitap_draft.pdf"
build.build_baitap()
chrome_pdf(tmp)
parts, items, n = find_pages(tmp)
print("lượt 1:", n, "trang;", parts)
miss = [t for _, t in build.baitap_index() if t not in items]
build.build_baitap({k: str(v) for k, v in parts.items()}, {k: str(v) for k, v in items.items()})
chrome_pdf(tmp)
parts2, items2, n2 = find_pages(tmp)
assert (parts, items, n) == (parts2, items2, n2), ("số trang lệch", parts, parts2)

# đóng dấu header / footer
d = fitz.open(tmp)
font = fitz.Font(fontfile=r"C:\Windows\Fonts\arialbd.ttf")
seq = sorted((v, k) for k, v in parts.items())
for i, page in enumerate(d):
    pno = i + 1
    cur = None
    for v, k in seq:
        if v <= pno:
            cur = k
    w = page.rect.width
    tw = fitz.TextWriter(page.rect)
    if cur:
        label = "[" + cur.split(" · ")[0] + "]"
        title = "Bài tập + lời giải · " + cur
        title = title if len(title) < 80 else title[:77] + "…"
        tw.append((36, 24), title, font=font, fontsize=8)
        tw.append((w - 36 - font.text_length(label, fontsize=11), 25), label, font=font, fontsize=11)
        page.draw_line((36, 30), (w - 36, 30), color=(0, 0, 0), width=0.6)
    foot = f"{pno} / {len(d)}"
    tw.append((w / 2 - font.text_length(foot, fontsize=9) / 2, page.rect.height - 18), foot, font=font, fontsize=9)
    tw.write_text(page, color=(0, 0, 0))
new = OUT / "_baitap_stamped.pdf"
d.save(new, garbage=3, deflate=True)
d.close()
tmp.unlink()
dst = OUT / "BAI-TAP-GIAI-CHI-TIET.pdf"
try:
    os.replace(new, dst)
except PermissionError:
    dst = OUT / "BAI-TAP-GIAI-CHI-TIET (ban moi).pdf"
    os.replace(new, dst)
    print("!! BAI-TAP-GIAI-CHI-TIET.pdf đang bị mở ở chương trình khác; bản mới lưu tại", dst.name)

# kiểm tra không có màu
d = fitz.open(dst)
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
print("PDF:", dst.name, len(d), "trang; trang có màu:", colored or "không có")
print("bài không tìm thấy trang:", miss or "không có")
