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
