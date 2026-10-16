# -*- coding: utf-8 -*-
"""Sổ tay làm bài (bản in ≤ 32 trang) → HOC-THI/TAI-LIEU-IN.pdf.

sotay.md: mỗi "# D… · tiêu đề" là một dạng. Các dạng chạy liền nhau; dạng nào có tiêu đề rơi xuống
dưới 70% trang thì tự đẩy sang trang mới. In nhiều lượt cho tới khi số trang ổn định, điền số trang
vào bảng tra ở trang 1, sinh mục lục từ khoá A–Z (phần IDX, quét chữ PDF), đóng dấu nhãn [mã dạng] ở mép ngoài (in 2 mặt), rồi audit cỡ chữ / font / màu.
Chạy: PYTHONIOENCODING=utf-8 python sotay.py        (thêm --check để kiểm code bị xuống dòng)
"""
import json
import os
import re
import subprocess
import sys
import collections
import fitz
import build

CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = build.OUT
SRC = build.HERE / "sotay.md"
HTML = OUT / "sotay.html"
TOPY = {}
CODES = ["D1", "D2", "D3", "D4", "D5", "D6", "D12", "D7", "D8", "D9", "D10", "D11", "TV", "IDX"]
MAX_PAGES = 32

# Consolas không có ký hiệu toán (⊑ ⊓ ∃ ∀ ⊤ …) → lấy từ DejaVu Sans Mono, co 91.3% cho bằng
# độ rộng ký tự Consolas để các cây tableau / Datalog không lệch cột. Có bản đậm thật → không còn Type3.
FONTS = """
@font-face{font-family:"SymMono";src:url("lib/fonts/DejaVuSansMono.ttf");font-weight:400;size-adjust:91.3%;
  unicode-range:U+2190-21FF,U+2200-22FF,U+2700-27BF}
@font-face{font-family:"SymMono";src:url("lib/fonts/DejaVuSansMono-Bold.ttf");font-weight:700;size-adjust:91.3%;
  unicode-range:U+2190-21FF,U+2200-22FF,U+2700-27BF}
@font-face{font-family:"SymText";src:url("lib/fonts/DejaVuSansMono.ttf");font-weight:400;
  unicode-range:U+2190-21FF,U+2200-22FF,U+2700-27BF}
@font-face{font-family:"SymText";src:url("lib/fonts/DejaVuSansMono-Bold.ttf");font-weight:700;
  unicode-range:U+2190-21FF,U+2200-22FF,U+2700-27BF}
"""

CSS = FONTS + """
@page{size:A4;margin:13mm 10mm 10mm 10mm}
*{box-sizing:border-box;color:#000 !important;background:#fff !important;box-shadow:none !important;font-synthesis:none}
html,body{margin:0;background:#fff}
body{font:10pt/1.3 Arial,"Segoe UI Symbol","SymText",sans-serif}
section.dang{margin-top:12pt}
section.dang:first-of-type{margin-top:0}
section.dang.np{break-before:page;page-break-before:always;margin-top:0}
h1{font-size:14.5pt;margin:0 0 4pt;padding:3pt 7pt;border:2.2pt solid #000;break-inside:avoid;break-after:avoid}
h2{font-size:11.5pt;margin:8pt 0 3pt;padding:0 0 1pt;border-bottom:1.2pt solid #000;break-after:avoid}
h2 + *{break-before:avoid}
p:has(+ pre),p:has(+ table),p:has(+ .gfig),p:has(+ ul),p:has(+ ol){break-after:avoid}
p{margin:2.5pt 0}
p.nd{break-before:avoid;border:0.8pt solid #000;border-left:3.5pt solid #000;padding:2.5pt 6pt;margin:0 0 5pt}
ul,ol{margin:1.5pt 0 2.5pt 15pt;padding:0}
li{margin:1pt 0}
li > ul, li > ol{margin-top:0.5pt}
li.ck{list-style:none;margin-left:-13pt}
li.ck .box{font:12pt/1 "Segoe UI Symbol",sans-serif;margin-right:3pt;vertical-align:-1pt}
code{font:9.2pt/1.25 Consolas,"SymMono",monospace}
pre{font:9pt/1.25 Consolas,"SymMono",monospace;border:0.7pt solid #000;padding:3pt 5pt;margin:3pt 0;
    white-space:pre-wrap;word-break:break-word;break-inside:avoid;page-break-inside:avoid}
pre code{font:inherit}
table{border-collapse:collapse;margin:3pt 0;width:100%;font-size:9.4pt;break-inside:auto}
tr{break-inside:avoid;page-break-inside:avoid}
th,td{border:0.7pt solid #000;padding:1.5pt 3.5pt;vertical-align:top;text-align:left}
th{font-weight:700}
td code,th code{font-size:9pt;overflow-wrap:anywhere;word-break:break-word}
th{overflow-wrap:normal;word-break:keep-all}
.gfig{text-align:center;margin:3pt 0 2pt;break-inside:avoid;page-break-inside:avoid}
.gfig svg{max-width:100%;height:auto}
.gfig .legend{font-size:9pt;font-style:italic;margin:1pt 0 4pt}
em{font-style:italic}
.idx{column-count:3;column-gap:5mm;font-size:9pt;line-height:1.22}
.idx div{break-inside:avoid}.idx .L{font:700 10.5pt Arial,sans-serif;border-bottom:0.8pt solid #000;margin:3pt 0 1pt}
.idx code{font-size:9pt}
@media screen{body{width:190mm;margin:0 auto}}
"""

# mermaid đen trắng, vector (không filter → Chrome không rasterize), nhãn cạnh có nền trắng
MM_INIT = """mermaid.initialize({startOnLoad:false,theme:'base',securityLevel:'loose',
 themeVariables:{primaryColor:'#ffffff',primaryBorderColor:'#000000',primaryTextColor:'#000000',lineColor:'#000000',
   secondaryColor:'#ffffff',tertiaryColor:'#ffffff',edgeLabelBackground:'#ffffff',fontFamily:'Verdana',fontSize:'15px'},
 themeCSS:'.edgeLabel rect,.labelBkg{fill:#fff !important;opacity:1 !important} .flowchart-link{stroke:#000 !important;stroke-width:1.3px !important} .node rect,.node circle,.node ellipse{fill:#fff !important;stroke:#000 !important;stroke-width:1.3px !important} text{fill:#000 !important}',
 flowchart:{htmlLabels:false,useMaxWidth:true,padding:12,nodeSpacing:22,rankSpacing:30}});"""

# stadium ([…]) → elip nội tiếp (IRI); rect góc vuông giữ nguyên (literal); circle (( )) = blank node
MM_POST = r"""
window.__mmpost=function(fig){
  var svg=fig.querySelector('svg'); if(!svg) return;
  svg.querySelectorAll('g.node rect').forEach(function(r){
    var rx=parseFloat(r.getAttribute('rx')||0), h=parseFloat(r.getAttribute('height')), w=parseFloat(r.getAttribute('width'));
    if(!(rx>0)) return;
    var x=parseFloat(r.getAttribute('x')), y=parseFloat(r.getAttribute('y'));
    var e=document.createElementNS('http://www.w3.org/2000/svg','ellipse');
    e.setAttribute('cx',x+w/2); e.setAttribute('cy',y+h/2); e.setAttribute('rx',w/2); e.setAttribute('ry',h/2);
    e.setAttribute('style','fill:#fff;stroke:#000;stroke-width:1.3px');
    r.parentNode.replaceChild(e,r);
  });
  var lg=document.createElement('div'); lg.className='legend';
  lg.textContent='Quy ước: elip = IRI · chữ nhật = literal · elip rỗng (nhỏ) = blank node · mũi tên = 1 bộ-3';
  fig.appendChild(lg);
};
window.__legendfix=function(){
  document.querySelectorAll('.gfig .legend').forEach(function(lg){
    var nx=lg.parentNode.nextElementSibling;
    if(nx&&nx.classList.contains('gfig')) lg.remove();
  });
};
"""

# chế độ --check: đánh dấu <pre> bị trình duyệt bẻ xuống dòng (so số dòng hiển thị với số dòng nguồn)
CHECK_JS = r"""
(function wait(){
  if(!window.__ready){setTimeout(wait,200);return;}
  var bad=[];
  document.querySelectorAll('pre').forEach(function(p,i){
    var src=p.textContent.replace(/\n$/,'').split('\n').length;
    var cs=getComputedStyle(p), lh=parseFloat(cs.lineHeight);
    var inner=p.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom);
    var shown=Math.round(inner/lh);
    if(shown>src) bad.push(i+':'+src+'->'+shown+':'+p.textContent.slice(0,40).replace(/\s+/g,' '));
  });
  var m=document.createElement('meta'); m.name='wrapped'; m.content=JSON.stringify(bad); document.head.appendChild(m);
  document.title='CHECKED';
})();
"""


def print_js():
    js = build.PRINT_JS
    a = "mermaid.initialize({startOnLoad:false,theme:'neutral',securityLevel:'loose',flowchart:{htmlLabels:false,useMaxWidth:true}});"
    b = "fig.innerHTML=r.svg;"
    assert a in js and b in js
    return MM_POST + js.replace(a, MM_INIT).replace(b, b + " window.__mmpost(fig);").replace("function done(){", "function done(){window.__legendfix();")


# mục lục A–Z: từ khoá → các trang có từ đó (quét chữ PDF, trừ trang 1 và chính phần IDX)
INDEX_TERMS = """
rdf:type rdf:Property rdf:Statement rdf:subject rdf:first rdf:rest rdf:nil rdf:List rdf:Bag rdf:Seq rdf:Alt rdf:value
rdf:langString rdf:nodeID rdf:resource rdf:about rdfs:Class rdfs:Resource rdfs:Literal rdfs:Datatype rdfs:subClassOf
rdfs:subPropertyOf rdfs:domain rdfs:range rdfs:label rdfs:comment rdfs:seeAlso rdfs:isDefinedBy rdfs:member rdfs:Container
rdfs2 rdfs3 rdfs5 rdfs7 rdfs9 rdfs11 @prefix xsd:integer xsd:nonNegativeInteger xsd:date
owl:Class owl:ObjectProperty owl:DatatypeProperty owl:AnnotationProperty owl:equivalentClass owl:disjointWith
owl:intersectionOf owl:unionOf owl:complementOf owl:oneOf owl:Restriction owl:onProperty owl:someValuesFrom
owl:allValuesFrom owl:hasValue owl:minCardinality owl:maxCardinality owl:cardinality owl:qualifiedCardinality
owl:minQualifiedCardinality owl:maxQualifiedCardinality owl:onClass owl:inverseOf owl:TransitiveProperty
owl:SymmetricProperty owl:AsymmetricProperty owl:ReflexiveProperty owl:IrreflexiveProperty owl:FunctionalProperty
owl:InverseFunctionalProperty owl:equivalentProperty owl:propertyChainAxiom owl:propertyDisjointWith owl:hasKey
owl:hasSelf owl:disjointUnionOf owl:AllDisjointClasses owl:AllDifferent owl:sameAs owl:differentFrom
owl:NegativePropertyAssertion owl:Thing owl:Nothing owl:imports owl:Ontology owl:NamedIndividual
SubClassOf: EquivalentTo: DisjointWith: DisjointUnionOf: Characteristics: InverseOf: SubPropertyChain: HasKey:
DisjointClasses: DifferentIndividuals: Individual: Facts:
SELECT ASK CONSTRUCT DESCRIBE DISTINCT REDUCED ORDER|BY LIMIT OFFSET OPTIONAL UNION MINUS FILTER NOT|EXISTS BIND VALUES
GRAPH SERVICE GROUP|BY HAVING COUNT SUM AVG GROUP_CONCAT SAMPLE regex langMatches isIRI isLiteral isBlank bound
COALESCE CONTAINS STRSTARTS STRLEN SUBSTR UCASE CONCAT YEAR NOW INSERT|DATA DELETE|DATA PREFIX
BGP Join LeftJoin Project Slice OrderBy Extend Group Distinct
sh:NodeShape sh:PropertyShape sh:targetClass sh:targetNode sh:targetSubjectsOf sh:targetObjectsOf sh:path
sh:inversePath sh:property sh:minCount sh:maxCount sh:class sh:datatype sh:nodeKind sh:minInclusive sh:maxInclusive
sh:minExclusive sh:minLength sh:maxLength sh:pattern sh:languageIn sh:uniqueLang sh:equals sh:disjoint sh:lessThan
sh:not sh:and sh:or sh:xone sh:node sh:qualifiedValueShape sh:hasValue sh:in sh:closed sh:severity sh:message
sh:sparql sh:ValidationReport sh:ValidationResult sh:conforms sh:focusNode
Manchester NNF GCI TBox ABox RBox clash blocking De|Morgan tableau ALC SHOIN SROIQ N2EXPTIME OWA CWA UNA
subsumption consistency instantiation retrieval satisfiability classification Datalog fixpoint proof|tree
forward|chaining backward|chaining solution|mapping compatible focus|node validation|report reification RDF-star
named|graph blank|node literal IRI collection N-Triples N-Quads TriG Turtle RDF/XML JSON-LD RDFa Microdata
schema.org FOAF Dublin|Core SKOS VoID DBpedia Wikidata YAGO LPG Cypher SWRL RIF OntoClean reasoner
Linked|Data 5|sao Knowledge|Graph EL QL RL OBDA rampant|classism
""".split()
INDEX = {}


def _key(t):
    import unicodedata
    k = t.split(":", 1)[1] if ":" in t[1:] and not t.endswith(":") else t
    k = unicodedata.normalize("NFD", k.lstrip("@")).encode("ascii", "ignore").decode().lower()
    return k


def find_index(path):
    """{từ: [(trang, số lần)]} trên các trang 2 … (trang đầu IDX − 1)"""
    d = fitz.open(path)
    texts = [" ".join(p.get_text().split()) for p in d]
    end = next((i for i, t in enumerate(texts) if "IDX · Mục lục từ khoá" in t), len(d))
    res = {}
    for raw in INDEX_TERMS:
        t = raw.replace("|", " ")
        pat = re.compile(r"(?<![A-Za-z0-9_:@-])" + re.escape(t) + (r"(?![A-Za-z0-9_])" if t[-1].isalnum() else ""))
        hits = [(i + 1, len(pat.findall(texts[i]))) for i in range(1, end)]
        res[t] = [h for h in hits if h[1]]
    d.close()
    return res


def index_html():
    if not INDEX:
        return '<div class="idx"><div>(số trang được điền ở lượt in cuối)</div></div>'
    out, cur = [], None
    for t in sorted(INDEX, key=_key):
        hits = INDEX[t]
        if not hits:
            continue
        L = _key(t)[:1].upper()
        if L != cur:
            out.append(f'<div class="L">{L}</div>')
            cur = L
        best = max(hits, key=lambda h: h[1])[0]
        pages = sorted({h[0] for h in sorted(hits, key=lambda h: -h[1])[:4]})
        ps = ", ".join(f"<b>{x}</b>" if x == best else str(x) for x in pages)
        name = f"<code>{t}</code>" if (":" in t or t.isupper() or "_" in t) else t
        out.append(f"<div>{name} {ps}</div>")
    return '<div class="idx">' + "".join(out) + "</div>"


def html(page_of=None, newpage=(), check=False):
    text = build.read(SRC)
    if page_of:
        for c, pg in page_of.items():
            text = text.replace(f"tr.@{c} |", f"tr.{pg} |").replace(f"tr.@{c}.", f"tr.{pg}.")
    text = re.sub(r"tr\.@[A-Z]+\d*", "tr. …", text)
    text = text.replace("@INDEX@", index_html())
    secs = []
    for n, ch in enumerate(c for c in re.split(r"(?m)^# ", text) if c.strip()):
        code = ch.split(" · ")[0].strip()
        cls = "dang np" if n == 1 or code in newpage or code == "IDX" else "dang"
        body = build.bw(build.render("# " + ch))
        body = body.replace("<li>☐", '<li class="ck"><span class="box">☐</span>')
        secs.append(f'<section class="{cls}">{body}</section>')
    page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Sổ tay làm bài Semantic Web</title>
<style>{CSS}</style></head><body>
{"".join(secs)}
<script src="lib/vis-network.min.js"></script><script src="lib/mermaid.min.js"></script><script>{build.read(build.HERE / "rdf.js")}</script><script>{print_js()}</script>{"<script>" + CHECK_JS + "</script>" if check else ""}</body></html>"""
    HTML.write_text(page, encoding="utf-8")


def pdf(dst):
    subprocess.run([CH, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=300000",
                    f"--print-to-pdf={dst}", HTML.as_uri()], check=True, capture_output=True)


def starts(path):
    d = fitz.open(path)
    res, titles = {}, {}
    for c in CODES:
        for i, p in enumerate(d):
            bs = [b for b in p.get_text("blocks") if b[4].strip().startswith(c + " · ")]
            if bs:
                res[c] = i + 1
                TOPY[c] = bs[0][1] / p.rect.height
                titles[c] = " ".join(bs[0][4].split())
                break
    d.close()
    return res, titles


def fills(path):
    """tỉ lệ chiều cao đã dùng của mỗi trang (bản chưa đóng dấu)"""
    d = fitz.open(path)
    res = {}
    for i, p in enumerate(d):
        ys = [b[3] for b in p.get_text("blocks") if b[4].strip()]
        res[i + 1] = (max(ys) - 37) / (p.rect.height - 65) if ys else 0
    d.close()
    return res


def blanks(path):
    d = fitz.open(path)
    res = {i + 1 for i, p in enumerate(d) if not [b for b in p.get_text("blocks") if b[4].strip()]}
    d.close()
    return res


NEVER = set()


def stamp(src, dst, page_of, titles):
    d = fitz.open(src)
    font = fitz.Font(fontfile=r"C:\Windows\Fonts\arialbd.ttf")
    seq = sorted((v, k) for k, v in page_of.items())
    for i, page in enumerate(d):
        pno = i + 1
        here = [k for v, k in seq if v == pno]
        before = [k for v, k in seq if v < pno]
        on = ([before[-1]] if before and (not here or TOPY[here[0]] > 0.1) else []) + here
        w, h = page.rect.width, page.rect.height
        L, R = 28, w - 28
        tw = fitz.TextWriter(page.rect)
        if on:
            t = "  |  ".join(titles[k] for k in on)
            t = t if len(t) < 90 else t[:87] + "…"
            lab = "[" + " · ".join(on) + "]"
        else:
            t, lab = "SỔ TAY LÀM BÀI SEMANTIC WEB · mang vào phòng thi", "[0]"
        lw = font.text_length(lab, fontsize=15)
        tl = font.text_length(t, fontsize=7.5)
        if pno % 2:  # trang lẻ (mặt trước): nhãn bên phải
            tw.append((R - lw, 25), lab, font=font, fontsize=15)
            tw.append((L, 23), t, font=font, fontsize=7.5)
        else:  # trang chẵn (mặt sau): nhãn bên trái
            tw.append((L, 25), lab, font=font, fontsize=15)
            tw.append((R - tl, 23), t, font=font, fontsize=7.5)
        page.draw_line((L, 29), (R, 29), color=(0, 0, 0), width=0.7)
        foot = f"Sổ tay làm bài Semantic Web · trang {pno} / {len(d)}"
        tw.append((w / 2 - font.text_length(foot, fontsize=8) / 2, h - 11), foot, font=font, fontsize=8)
        tw.write_text(page, color=(0, 0, 0))
    d.save(dst, garbage=3, deflate=True)
    n = len(d)
    d.close()
    return n


def audit(path):
    d = fitz.open(path)
    errs, sizes = [], collections.Counter()
    fonts = set()
    for i in range(len(d)):
        for f in d.get_page_fonts(i):
            fonts.add((f[1], f[2], f[3]))
    if any(f[1] == "Type3" for f in fonts):
        errs.append("có font Type3")
    if any(f[0] == "n/a" for f in fonts):
        errs.append("có font không nhúng")
    figmin = 99
    for pi, p in enumerate(d):
        H = p.rect.height
        if p.get_image_info():
            errs.append(f"tr.{pi + 1}: có ảnh raster")
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    t = s["text"].strip()
                    if not t or s["bbox"][1] < 32 or s["bbox"][3] > H - 18:
                        continue  # header / footer đóng dấu
                    sz = round(s["size"], 1)
                    fn = s["font"]
                    if "Cambria" in fn:
                        errs.append(f"tr.{pi + 1}: ký hiệu dùng Cambria Math: {t[:10]}")
                    if "Verdana" in fn:
                        figmin = min(figmin, sz)
                        continue
                    sizes[(("mono" if ("Consolas" in fn or "DejaVu" in fn) else "text"), sz)] += len(t)
                    lim = 8.0 if "DejaVu" in fn else 8.6
                    if sz < lim and "Segoe" not in fn:
                        errs.append(f"tr.{pi + 1}: chữ {sz}pt < {lim}: {t[:20]}")
    body = max((v, k) for k, v in sizes.items() if k[0] == "text")[1][1]
    if body < 9.6:
        errs.append(f"cỡ chữ thường phổ biến {body}pt < 9.6")
    if figmin < 8.8:
        errs.append(f"chữ trong sơ đồ nhỏ nhất {figmin}pt < 8.8")
    colored = []
    for i, p in enumerate(d):
        pix = p.get_pixmap(dpi=40)
        s = pix.samples
        mx = 0
        for j in range(0, len(s), pix.n * 7):
            mx = max(mx, max(s[j], s[j + 1], s[j + 2]) - min(s[j], s[j + 1], s[j + 2]))
        if mx > 40:
            colored.append((i + 1, mx))
    if colored:
        errs.append(f"trang có màu: {colored}")
    if len(d) > MAX_PAGES:
        errs.append(f"{len(d)} trang > {MAX_PAGES}")
    print("cỡ chữ thường phổ biến:", body, "pt · chữ sơ đồ nhỏ nhất:", figmin, "pt")
    print("font:", sorted(f[2] for f in fonts))
    d.close()
    return errs


def check_wrap():
    html(check=True)
    r = subprocess.run([CH, "--headless=new", "--disable-gpu", "--virtual-time-budget=300000", "--dump-dom",
                        HTML.as_uri()], capture_output=True, text=True, encoding="utf-8")
    m = re.search(r'<meta name="wrapped" content="([^"]*)"', r.stdout)
    import html as H
    return H.unescape(m.group(1)) if m else "KHÔNG ĐỌC ĐƯỢC"


if __name__ == "__main__":
    if "--check" in sys.argv:
        print("pre bị xuống dòng:", check_wrap())
        sys.exit()
    tmp = OUT / "_sotay.pdf"
    page_of, newpage = None, set()
    for it in range(6):
        html(page_of, newpage)
        pdf(tmp)
        po, titles = starts(tmp)
        fill = fills(tmp)
        drop = {c for c in newpage if fill.get(po[c] - 1, 0) < 0.25}
        if drop:
            newpage -= drop
            NEVER.update(drop)
            page_of = None
            continue
        late = {c for c in CODES if TOPY[c] > 0.80 and c not in newpage and c not in NEVER}
        if late:
            newpage |= late
        elif po == page_of:
            break
        page_of = po
    else:
        raise SystemExit("số trang không ổn định")
    # lượt cuối: điền mục lục A–Z (chỉ đổi phần IDX ở cuối) cho tới khi ổn định
    for it in range(3):
        idx = find_index(tmp)
        if idx == INDEX:
            break
        INDEX.clear()
        INDEX.update(idx)
        html(page_of, newpage)
        pdf(tmp)
        po, titles = starts(tmp)
        assert po == page_of, ("mục lục A–Z làm lệch trang", po, page_of)
    else:
        raise SystemExit("mục lục A–Z không ổn định")
    miss = [t for t, h in INDEX.items() if not h]
    print("mục lục A–Z:", len(INDEX) - len(miss), "từ · không thấy:", miss or "không")
    assert not blanks(tmp), ("trang trắng", blanks(tmp))
    dst = OUT / "TAI-LIEU-IN.pdf"
    new = OUT / "_sotay_stamped.pdf"
    n = stamp(tmp, new, page_of, titles)
    tmp.unlink()
    try:
        os.replace(new, dst)
    except PermissionError:
        # file đang mở trong trình xem (VS Code, Acrobat…): giữ bản mới bên cạnh
        dst = OUT / "TAI-LIEU-IN (ban moi).pdf"
        os.replace(new, dst)
        print("!! TAI-LIEU-IN.pdf đang bị mở ở chương trình khác; bản mới lưu tại", dst.name)
    # số trang từng dạng cho web (nút "Sổ tay tr. X")
    (build.HERE / "sotay_pages.json").write_text(json.dumps(dict(page_of, _total=n)), encoding="utf-8")
    print("sổ tay:", page_of, "· sang trang mới:", sorted(newpage) or "không")
    print(dst.name + ":", n, "trang")
    errs = audit(dst)
    print("AUDIT:", "OK" if not errs else "\n  " + "\n  ".join(errs[:40]))
