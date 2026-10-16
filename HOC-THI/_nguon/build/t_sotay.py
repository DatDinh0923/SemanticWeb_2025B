# -*- coding: utf-8 -*-
"""Kiểm nội dung sổ tay (sotay.md) bằng máy: Turtle parse được, kết quả SPARQL / RDFS / Datalog / SHACL
in trong bài mẫu khớp với kết quả tính thật.  Chạy: PYTHONIOENCODING=utf-8 python t_sotay.py"""
import re
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, BNode
from rdflib.plugins.sparql import prepareQuery

SRC = Path(__file__).parent / "sotay.md"
S = SRC.read_text(encoding="utf-8")
PFX = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix bio: <http://exam.hust.edu.vn/bio/> .
"""
EX = "http://semweb.edu.vn/exam#"
results = []


def ok(name, cond, info=""):
    results.append((name, bool(cond), info))


def section(code):
    i = S.index(f"\n# {code} · ")
    j = S.find("\n# D", i + 5)
    return S[i:j if j > 0 else len(S)]


def blocks(text, lang):
    return re.findall(r"```" + lang + r"\n(.*?)```", text, re.S)


def graph(ttl, base=EX):
    g = Graph()
    pre = PFX
    if not re.search(r"@prefix\s+:\s", ttl):
        pre += f"@prefix : <{base}> .\n"
    g.parse(data=pre + ttl, format="turtle")
    return g


# ---------- 1. mọi khối Turtle parse được ----------
for k, b in enumerate(blocks(S, "turtle")):
    try:
        graph(b)
        ok(f"turtle #{k + 1} parse", True)
    except Exception as e:
        ok(f"turtle #{k + 1} parse", False, f"{e} :: {b[:60]!r}")

# ---------- 2. D1 + D2: số cạnh ----------
d1 = section("D1")
g1 = graph(next(b for b in blocks(d1, "turtle") if "sw_course" in b))
ok("D1 Turtle 2023-C1 = 19 bộ-3", len(g1) == 19, len(g1))
e1 = sum(len(re.findall(r"--\s*\"", m)) for m in blocks(d1, "mermaid"))
ok("D1 sơ đồ = 19 cạnh", e1 == 19, e1)
d2 = section("D2")
g2 = graph(next(b for b in blocks(d2, "turtle") if "Georges" in b))
ok("D2 Turtle Georges/Michael = 9 bộ-3", len(g2) == 9, len(g2))
e2 = sum(len(re.findall(r"--\s*\"", m)) for m in blocks(d2, "mermaid"))
ok("D2 sơ đồ = 9 cạnh", e2 == 9, e2)

# ---------- 3. D4: bao đóng RDFS ----------


def rdfs_closure(g):
    g = Graph() + g
    while True:
        new = set()
        for p, _, c in g.triples((None, RDFS.domain, None)):
            for x, _, _ in g.triples((None, p, None)):
                new.add((x, RDF.type, c))
        for p, _, c in g.triples((None, RDFS.range, None)):
            for _, _, y in g.triples((None, p, None)):
                if isinstance(y, (URIRef, BNode)):
                    new.add((y, RDF.type, c))
        for p, _, q in g.triples((None, RDFS.subPropertyOf, None)):
            for x, _, y in g.triples((None, p, None)):
                new.add((x, q, y))
            for _, _, r in g.triples((q, RDFS.subPropertyOf, None)):
                new.add((p, RDFS.subPropertyOf, r))
        for c, _, d in g.triples((None, RDFS.subClassOf, None)):
            for x, _, _ in g.triples((None, RDF.type, c)):
                new.add((x, RDF.type, d))
            for _, _, e in g.triples((d, RDFS.subClassOf, None)):
                new.add((c, RDFS.subClassOf, e))
        new -= set(g)
        if not new:
            return g
        for t in new:
            g.add(t)


d4 = section("D4")
E = Namespace(EX)
m = re.search(r"Bài mẫu 1.*?\*\*Đề:\*\* `([^`]+)`", d4, re.S)
gc = rdfs_closure(graph(m.group(1)))
for s_, o_ in [("a", "D"), ("a", "F"), ("b", "C"), ("b", "E"), ("c", "E")]:
    ok(f"D4 2022-C2: :{s_} a :{o_}", (E[s_], RDF.type, E[o_]) in gc)
gf = rdfs_closure(graph(blocks(d4, "turtle")[0]))
T = {"T1": (E.Ann, E.hasParent, E.Carl), "T2": (E.Carl, RDF.type, E.Father), "T3": (E.Carl, RDF.type, E.Parent),
     "T4": (E.Carl, RDF.type, E.Person), "T5": (E.Father, RDFS.subClassOf, E.Person)}
for k, t in T.items():
    ok(f"D4 gia đình ({k}) suy ra được", t in gf)
ok("D4 #5 Carl hasChild Ann = UNKNOWN", (E.Carl, E.hasChild, E.Ann) not in gf)
ok("D4 #6 Ann a Child = UNKNOWN", (E.Ann, RDF.type, E.Child) not in gf)
ok("D4 #7 hasFather domain Person = UNKNOWN", (E.hasFather, RDFS.domain, E.Person) not in gf)
ok("D4 #8 Ann hasParent _:x = TRUE", any(gf.triples((E.Ann, E.hasParent, None))))
ok("D4 #9 Ann hasParent [a Person] = TRUE",
   any((o, RDF.type, E.Person) in gf for _, _, o in gf.triples((E.Ann, E.hasParent, None))))

# ---------- 4. D8 + D9: SPARQL trên dữ liệu đề ----------
d8 = section("D8")
PL = graph(blocks(d8, "turtle")[0])
air_txt = re.search(r"2023, Câu 4a\.\*\* Dữ liệu: `([^`]+)`", d8).group(1)
AIR = graph("@prefix : <%s> .\n" % EX + air_txt)
bio_txt = re.search(r"2022, Câu 5a\.\*\* Dữ liệu: `([^`]+)`", d8).group(1)
BIO = graph(bio_txt)
NS = {"": Namespace(EX), "rdfs": RDFS, "bio": Namespace("http://exam.hust.edu.vn/bio/")}


def run(g, q):
    return g.query(q, initNs=NS)


def loc(x):
    return None if x is None else (str(x).split("#")[-1].split("/")[-1] if isinstance(x, URIRef) else str(x))


qs = blocks(d8, "sparql")
for q in qs:
    try:
        prepareQuery(q, initNs=NS)
        ok("SPARQL cú pháp: " + q.strip().splitlines()[-1][:40], True)
    except Exception as e:
        ok("SPARQL cú pháp", False, f"{e} :: {q[:60]!r}")
qa = next(q for q in qs if ":pointer" in q)
ok("D8 a) = CPP, C, Java", sorted(loc(r[0]) for r in run(PL, qa)) == ["C", "CPP", "Java"])
qb = next(q for q in qs if "?creator" in q)
rb = {loc(r[0]): loc(r[1]) for r in run(PL, qb)}
ok("D8 b) 5 dòng, Lisp/Ruby trống", rb == {"CPP": "bjarne_stroustrup", "C": "dennis_ritchie", "Java": "james_gosling",
                                          "Lisp": None, "Ruby": None}, rb)
qc = next(q for q in qs if "CONSTRUCT" in q)
rc = sorted(loc(s_) for s_, _, _ in run(PL, qc).graph)
ok("D8 c) CONSTRUCT CPP, Java, Python", rc == ["CPP", "Java", "Python"], rc)
qn = next(q for q in qs if "COUNT(?f)" in q)
rn = {loc(r[0]): int(r[1]) for r in run(PL, qn)}
ok("D8 mẫu đếm CPP5 C3 Java2 Lisp1 Ruby0", rn == {"CPP": 5, "C": 3, "Java": 2, "Lisp": 1, "Ruby": 0}, rn)
qair = next(q for q in qs if "Seaplane" in q)
ra = sorted((loc(r.p), loc(r.t), loc(r.label)) for r in run(AIR, qair))
ok("D8 2023-4a", ra == [("Caspar", "Seaplane", None), ("Convair", "Seaplane", None),
                        ("Mi26", "Helicopter", "Mil Mi-26")], ra)
qbio = next(q for q in qs if "bio:Anna" in q)
ok("D8 2022-5a = Milo, Kitty", sorted(loc(r[0]) for r in run(BIO, qbio)) == ["Kitty", "Milo"])
d9 = section("D9")
fin = re.search(r"`(\{ \?p a \?t OPTIONAL \{ \?p :speed \?s FILTER\(\?s > 1000\) \} \})`", d9).group(1)
fout = re.search(r"`(\{ \?p a \?t OPTIONAL \{ \?p :speed \?s \} FILTER\(\?s > 1000\) \})`", d9).group(1)
r_in = {loc(r.p): loc(r.s) for r in run(AIR, "SELECT * WHERE " + fin)}
r_out = {loc(r.p): loc(r.s) for r in run(AIR, "SELECT * WHERE " + fout)}
ok("D9 FILTER trong OPTIONAL: còn 5 máy bay, chỉ Mig35 có ?s", len(r_in) == 5 and
   [k for k, v in r_in.items() if v] == ["Mig35"], r_in)
ok("D9 FILTER ngoài OPTIONAL: chỉ Mig35", list(r_out) == ["Mig35"], r_out)
bgp = lambda q: sorted(loc(r[0]) for r in run(PL, q))
ok("D9 bước 1 BGP(?pl a :PL)", bgp("SELECT ?pl WHERE {?pl a :PL}") == ["C", "CPP", "Java", "Lisp", "Ruby"])
ok("D9 bước 2 pointer", bgp("SELECT ?pl WHERE {?pl :hasFeature :pointer}") == ["C", "CPP"])
ok("D9 bước 3 class", bgp("SELECT ?pl WHERE {?pl :hasFeature :class}") == ["CPP", "Java", "Python"])

# ---------- 5. D10: SHACL bằng SPARQL tương đương ----------
v1 = bgp_air = sorted(loc(r[0]) for r in run(AIR, "SELECT ?x WHERE {?x a :Seaplane; :flight ?f FILTER(!(?f > 1900))}"))
ok("D10 Seaplane flight > 1900: Caspar vi phạm", v1 == ["Caspar"], v1)
nc = sorted(loc(r[0]) for r in run(AIR, "SELECT ?x WHERE {?x a :JetFighter FILTER NOT EXISTS {?x :crew ?c}}"))
nsp = sorted(loc(r[0]) for r in run(AIR, "SELECT ?x WHERE {?x a :JetFighter FILTER NOT EXISTS {?x :speed ?c}}"))
ok("D10 JetFighter: Mig35 thiếu crew, Su27 thiếu speed", nc == ["Mig35"] and nsp == ["Su27"], (nc, nsp))
nf = sorted(loc(r[0]) for r in run(PL, "SELECT ?x WHERE {?x a :PL FILTER NOT EXISTS {?x :hasFeature ?f}}"))
ok("D10 PLFeatures: Ruby vi phạm", nf == ["Ruby"], nf)

# ---------- 6. D7: điểm cố định Datalog (mỗi bước dùng tập của bước trước) ----------
B = [{("1C", "A", "B"), ("1C", "B", "C"), ("2C", "D", "C")}]
while True:
    cur, new = B[-1] if len(B) == 1 else set().union(*B), set()
    for f in cur:
        if f[0] == "2C":
            new |= {("2C", f[2], f[1]), ("Đi", f[1], f[2])}
        if f[0] == "1C":
            new.add(("Đi", f[1], f[2]))
    di = [f for f in cur if f[0] == "Đi"]
    new |= {("Đi", a[1], b[2]) for a in di for b in di if a[2] == b[1]}
    new -= cur
    B.append(new)
    if not new:
        break
want = [{("2C", "C", "D"), ("Đi", "A", "B"), ("Đi", "B", "C"), ("Đi", "D", "C")},
        {("Đi", "C", "D"), ("Đi", "A", "C")},
        {("Đi", "B", "D"), ("Đi", "A", "D"), ("Đi", "C", "C"), ("Đi", "D", "D")}, set()]
ok("D7 B1..B4 khớp sổ tay", B[1:] == want, B[1:])
ok("D7 điểm cố định có 9 dữ kiện Đi", len([f for f in set().union(*B) if f[0] == "Đi"]) == 9)

# ---------- 6. D2 RDF/XML: mọi bộ-3 (blank node = biến) đều có trong Turtle ----------
OWL = Namespace("http://www.w3.org/2002/07/owl#")
gx = Graph().parse(data=blocks(d2, "xml")[0], format="xml")


def term(t):
    return "?" + "b" + str(abs(hash(t)) % 10 ** 6) if isinstance(t, BNode) else t.n3()


bvars = {term(t) for tr in gx for t in tr if isinstance(t, BNode)}
askx = "ASK {" + " ".join(f"{term(a)} {term(b)} {term(c)} ." for a, b, c in gx) + "".join(f" FILTER(isBlank({v}))" for v in bvars) + "}"
ok("D2 RDF/XML ⊆ Turtle (Michael defeated Satan, Georges defeated _:d)", len(gx) == 7 and g2.query(askx).askAnswer, (len(gx), askx[:120]))

# ---------- 7. D5: mọi lớp / thuộc tính dùng tới đều được khai báo ----------


def undeclared(g):
    classes = {o for o in g.objects(None, RDFS.subClassOf)} | {o for o in g.objects(None, OWL.onClass)} \
        | {o for o in g.objects(None, OWL.someValuesFrom)} | {o for o in g.objects(None, OWL.allValuesFrom)} \
        | {o for o in g.objects(None, OWL.disjointWith)} | {o for o in g.objects(None, RDFS.domain)} | {o for o in g.objects(None, RDFS.range)}
    for lst in list(g.objects(None, OWL.unionOf)) + list(g.objects(None, OWL.members)) + list(g.objects(None, OWL.intersectionOf)):
        classes |= set(g.items(lst))
    props = set(g.objects(None, OWL.onProperty)) | set(g.objects(None, OWL.inverseOf)) | set(g.objects(None, OWL.equivalentProperty))
    miss = {c for c in classes if isinstance(c, URIRef) and (c, RDF.type, OWL.Class) not in g}
    miss |= {q for q in props if isinstance(q, URIRef) and (q, RDF.type, OWL.ObjectProperty) not in g}
    return sorted(loc(x) for x in miss)


d5 = section("D5")
g3 = graph(next(b for b in blocks(d5, "turtle") if "LaboratoryCourse" in b))
ok("D5 bài 3: mọi lớp/thuộc tính đã khai báo", not undeclared(g3), undeclared(g3))
ok("D5 bài 3: Assistant ⊑ ∀teaches.LaboratoryCourse", g3.query(
    "ASK { :Assistant rdfs:subClassOf [ owl:onProperty :teaches ; owl:allValuesFrom :LaboratoryCourse ] }", initNs={"owl": OWL, "rdfs": RDFS, "": Namespace(EX)}).askAnswer)
g6390 = graph(next(b for b in blocks(d5, "turtle") if "phuThuoc" in b))
ok("D5 6390: mọi lớp/thuộc tính đã khai báo", not [x for x in undeclared(g6390) if x not in ("CPP",)], undeclared(g6390))

# ---------- 8. D9 2022-5b: bảng từng bước ----------
b1 = sorted(loc(r[0]) for r in run(BIO, "SELECT ?pet WHERE { bio:Anna bio:own ?pet . ?pet a bio:Cat }"))
b2 = sorted((loc(r[0]), loc(r[1])) for r in run(BIO, "SELECT ?x ?pet WHERE { bio:Anna bio:own ?x . ?x a bio:Cat . ?x bio:offspring ?pet }"))
ok("D9 2022-5b bước 1 = Milo, bước 2 = (Milo, Kitty)", b1 == ["Milo"] and b2 == [("Milo", "Kitty")], (b1, b2))

# ---------- báo cáo ----------
bad = [r for r in results if not r[1]]
for n, c, i in results:
    print(("PASS " if c else "FAIL ") + n + ("" if c else f"   → {i}"))
print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
raise SystemExit(1 if bad else 0)
