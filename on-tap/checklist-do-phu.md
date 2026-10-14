# Checklist độ phủ — mọi khái niệm của khóa học

Đánh dấu `[x]` khi đã **tự giải thích được bằng lời + cho ví dụ** (không chỉ "đã đọc").
Mức: ★★★ trọng tâm (gần như chắc ra) · ★★ cần biết (có thể là câu nhỏ/ý phụ) · ★ đọc hiểu.

## 01_Intro → `06-ly-thuyet.md` §A
- [ ] ★★ Định nghĩa knowledge graph (Paulheim 2017, 4 tiêu chí), "things, not strings" — T1
- [ ] ★ Tầm nhìn Semantic Web 2001; ví dụ Dr. Mark Smith; vấn đề Web cổ điển — T2
- [ ] ★ Wolfram Alpha vs ChatGPT — T2
- [ ] ★★ Semantic Web stack — T3
- [ ] ★ Interoperability cú pháp vs ngữ nghĩa; XML, XPath, namespace, DTD, XML Schema — T4
- [ ] ★ URI vs URL — T5

## 02_RDF → `01-rdf-rdfs.md` §A, §D
- [ ] ★★★ Triple; vị trí cho phép URI/blank/literal — A1
- [ ] ★★★ Literal: datatype XOR language tag; không có default datatype — A1
- [ ] ★★★ Blank node: hai cách viết, biến tồn tại, n-ary relation (recipe) — A2
- [ ] ★★★ N-Triples / Turtle / RDF/XML / JSON-LD — A3, Part 1 Ex2–Ex6
- [ ] ★★★ Reification (Peter says…), provenance — A4, Part 1 Ex2
- [ ] ★★ Container vs collection — A5
- [ ] ★★★ Non-unique name assumption, Open World Assumption (Peter fatherOf Julia, Mary) — A6
- [ ] ★ Content negotiation, 303, MIME types, RDFa, Microdata, JSON-LD nhúng — A7
- [ ] ★ "RDF có mạnh hơn XML?" — A7

## 03_RDFS → `01-rdf-rdfs.md` §B, §E
- [ ] ★★ Định nghĩa ontology (Gruber); explicit/formal/shared/partial; các loại ngữ nghĩa — B1
- [ ] ★★★ Từ vựng RDFS; T-Box vs A-Box — B2
- [ ] ★★★ Nhiều domain = giao — B2
- [ ] ★★★ Luật rdfs1–13, se1/se2, axiomatic triples — B3
- [ ] ★★★ True vs unknown; blank node trong câu hỏi; domain/range không kế thừa xuống — B3, Part 2 Ex2
- [ ] ★★ Forward chaining; ví dụ Tim/worksIn, Madrid — B4
- [ ] ★★★ Giới hạn RDFS (không phủ định → không mâu thuẫn; Baby/Adult) — B5
- [ ] ★★ Part 2 Ex1 (Sebastian/Thai curry, ContainerMembershipProperty) — §E

## 04_LOD → `05-lod-modeling.md` §A
- [ ] ★★★ 4 nguyên tắc Linked Data — A2
- [ ] ★★★ 5 sao + ví dụ định dạng — A3
- [ ] ★★ 9 best practices Heath & Bizer — A4
- [ ] ★★★ owl:sameAs: đúng vs lạm dụng (homepage, Starbucks, Hamburg, quốc hội); thay thế — A5
- [ ] ★★ DBpedia / YAGO / Wikidata; FOAF, Dublin Core, geo, schema.org, SKOS; LOV, prefix.cc — A6
- [ ] ★ Pubby, D2RQ, hash vs 303 URI, Microdata vs LOD, Jena/rdflib — A7

## 05_OWL → `02-owl.md` §A, §C–F
- [ ] ★★ OWL Lite / DL / Full — A1
- [ ] ★★★ Thing/Nothing; Object vs Datatype property; sameAs/differentFrom/AllDifferent; equivalentClass/Property — A2
- [ ] ★★★ Đặc tính property + ví dụ slide; Functional ⇒ sameAs (Helsinki); InverseFunctional = khóa — A3
- [ ] ★★★ Hoàn thiện ví dụ Madrid (3 câu "false") — A3
- [ ] ★★★ some / only / value / min / max / exactly / qualified / Self — A4
- [ ] ★★★ only thỏa tầm thường; closure; restriction cục bộ vs range toàn cục — A4
- [ ] ★★★ subClassOf vs equivalentClass (BallSports) — A4
- [ ] ★★★ union / intersection / complement / disjoint; VegetarianRecipe — A5
- [ ] ★★★ oneOf, lớp đóng, Mike in D219 — A5, Pizza câu 6 (Norway)
- [ ] ★ Sudoku, OWL Full meta-modelling (Elephant a Species) — A5, A1
- [ ] ★★★ Thiết kế: Part 3 Ex2 (thuốc), **Ex3 (môn học)**, Ex4 (phim) — §C, §D, §E
- [ ] ★★★ Pizza: Margherita, hasIngredient, owl:Nothing (CheeseyVegetableTopping, IceCream), Grandiosa, Norway — §F

## 06-OWL2 → `02-owl.md` §A6, `03-owl2-tableau.md`
- [ ] ★★ disjointUnion, AllDisjointClasses, NegativePropertyAssertion, hasSelf, property chain — 02 A6
- [ ] ★★ Profiles EL / QL / RL — 03 §1.6
- [ ] ★ Barber paradox; giới hạn OWL → SWRL/RIF — 02 A6, 03 §1.6
- [ ] ★★★ Vì sao forward chaining không đủ; mọi task quy về consistency — 03 §1.1–1.2
- [ ] ★★★ Bảng DL↔OWL — 03 §1.3
- [ ] ★★★ NNF — 03 §1.4
- [ ] ★★★ 7 luật tableau, nhánh đóng, rule blocking — 03 §1.5
- [ ] ★★★ Exercises-OWL2 Ex1 (Pingu), Ex2 (Mary), **Ex3 (Professor)** — 03 §3
- [ ] ★★ Seth, Jane, Jimmy, Married Bachelor, Flipper — 03 §4
- [ ] ★★ Tên DL (ALC, S, H, O, I, N, Q, F, (D)); reasoner nào hỗ trợ gì — 03 §1.6

## 07-Knowledge-Modeling → `05-lod-modeling.md` §B
- [ ] ★ Ontology hacking vs engineering; SECI — B1
- [ ] ★★ Grüninger & Fox (competency questions = unit test SPARQL); Methontology; Ontology 101 — B1
- [ ] ★★ SNOMED amputation — B1
- [ ] ★★★ OntoClean: rigidity (Passenger), identity (Interval/Duration, Country, Book), unity (Animal/OrganicMatter) — B2
- [ ] ★★ Design patterns: presentation (đặt tên), logical (ternary), content (RoleAtTime), transformation — B3
- [ ] ★★★ Anti-pattern: rampant classism (Goethe), exclusivity (CoastalCity/Germany) — B4
- [ ] ★★ Top-level: Aristotle, Sowa 12 phạm trù (+ bài tập slide), DOLCE (endurant/perdurant/quality/abstract) — B5

## Ext_SPARQL → `04-sparql.md`
- [ ] ★★★ Graph pattern; bẫy biến trùng; blank node trong kết quả — A1
- [ ] ★★★ Literal & lang trong truy vấn — A2
- [ ] ★★★ FILTER, regex, isURI/isBLANK/isLITERAL/LANG/DATATYPE/langMatches — A3
- [ ] ★★★ UNION, OPTIONAL, ORDER BY, LIMIT/OFFSET, DISTINCT — A4, A5
- [ ] ★★★ SELECT / ASK / CONSTRUCT / DESCRIBE — A6
- [ ] ★★★ SPARQL không suy diễn (Technoseum) — A7
- [ ] ★ SERVICE federation, Virtuoso built-in, Triple Pattern Fragments — A7, A8
- [ ] ★★ *(bổ sung)* GROUP BY / COUNT / HAVING, property path, NOT EXISTS / MINUS, BIND, VALUES, UPDATE — B1–B5
- [ ] ★★★ 25 bài viết truy vấn + 5 bài đoán kết quả — D, E

## Ext. (KG, LPG, App) → `06-ly-thuyet.md`
- [ ] ★ Lịch sử KG, bài học, chi phí mỗi triple — T12, T13
- [ ] ★★ Reification vs named graph vs RDF-star — T11
- [ ] ★★ LPG / Cypher vs RDF (closed vs open world) — T14, T15
- [ ] ★ Linked Widgets, StatSpace — T16, T17

## Bài về nhà đã làm (đối chiếu)
- [ ] 29.08 (Part 1 Ex2) — `01-rdf-rdfs.md` Part 1 Ex2
- [ ] 5.9 (Part 2 Ex2, câu 10–13) — bảng 18 mệnh đề
- [ ] 12.9 (Part 2 Ex2, câu 14–18) — bảng 18 mệnh đề + **đính chính câu 16**
- [ ] 03.10 (Exercises-OWL2 Ex1, Ex2) — `03-owl2-tableau.md` §3
