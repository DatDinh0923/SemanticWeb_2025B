# 04 — SPARQL (★★★ — tin đồn: "một phần SPARQL")

> Slide: `Ext_SPARQL.pdf` (dù tên "Ext" nhưng là kiến thức lõi) · Liên quan: competency questions (`07-Knowledge-Modeling.pdf`), SPARQL endpoint (đề Capstone)
> Dạng bài **D2**: viết truy vấn từ câu hỏi tiếng Việt / đọc truy vấn đoán kết quả.
> **Tự chạy:** `cd on-tap/files && pip install rdflib && python run_queries.py` (hoặc `python run_queries.py q04 q15`).
> ⚠️ Slide **không** có GROUP BY/COUNT/HAVING, property path, MINUS, BIND, VALUES, UPDATE — phần B bổ sung từ W3C SPARQL 1.1 (đánh dấu *bổ sung*).

---

## Phần A — Kiến thức trên slide (★★★)

### A1. Ý tưởng: khớp mẫu đồ thị (graph pattern matching)
- Câu hỏi slide: *"Các bang chứa 5 thành phố lớn nhất nước Đức?"* — đi theo link (dereference) thì rất chậm ⇒ **truy vấn** trên triple store.
- Truy vấn = đồ thị có **biến** (`?x`); kết quả = mọi cách gán biến sao cho mẫu khớp với dữ liệu.
```sparql
PREFIX : <http://example.org/>
SELECT ?p ?c
WHERE {
  ?p :knows ?c .          # cú pháp mẫu giống Turtle: ; lặp subject, , lặp subject+predicate, a = rdf:type
  ?c :knows :Ellen .
}
```
**Bẫy trên slide:**
- Hai biến khác nhau **có thể gán cùng một tài nguyên** (`?c1 = ?c2 = :Julia`) ⇒ muốn khác nhau phải `FILTER(?c1 != ?c2)`.
- Nhưng `FILTER(?c1 != ?c2)` **vẫn chưa chứng minh** có 2 người con: hai URI khác nhau có thể là một người (**non-unique name**), và có thể còn con khác (**OWA**).
- Tên blank node trong kết quả chỉ duy nhất **trong một tập kết quả**.

### A2. Literal trong truy vấn
- `"Germany"` ≠ `"Germany"@en` (khác literal ⇒ không khớp!). `42` viết tắt cho `"42"^^xsd:integer`.
- `str(?x)` lấy chuỗi; `lang(?x)` lấy tag; `datatype(?x)`; `langMatches(lang(?x), "de")` — bẫy: `"Januar"@DE` vs `"Jänner"@DE-at` (langMatches "de" khớp cả hai).

### A3. FILTER
| Loại | Cú pháp |
|---|---|
| so sánh | `= != < > <= >=` |
| logic | `&& \|\| !` |
| chuỗi | `regex(?n, "^Ann$")`, `regex(?n, "ann", "i")`; `"Ann"` bằng `=` so khớp **nguyên chuỗi**; `regex(?n,"Ann")` khớp cả "Mary-Ann" |
| kiểu | `isURI(?x)`, `isBLANK(?x)`, `isLITERAL(?x)`, `DATATYPE(?x)`, `LANG(?x)`, `bound(?x)` |
- Ví dụ slide: anh/chị/em lớn tuổi hơn — `FILTER(?b1 < ?b2)` trên ngày sinh.

### A4. UNION, OPTIONAL
```sparql
# điện thoại riêng HOẶC điện thoại cơ quan
{ ?p :privatePhone ?tel } UNION { ?p :workPhone ?tel }
# fax nếu có — người không có fax vẫn xuất hiện, ?fax unbound
?p :name ?n . OPTIONAL { ?p :fax ?fax }
```

### A5. Sắp xếp, phân trang, trùng lặp
- `ORDER BY ?x`, `ORDER BY DESC(?pop)`; **không có thứ tự mặc định**.
- `LIMIT 100`, `OFFSET 100` (ví dụ: 100 thành phố lớn nhất).
- `DISTINCT` loại **dòng kết quả trùng** — không phải loại thực thể trùng ngoài đời (UNA).

### A6. Bốn dạng truy vấn
| Dạng | Trả về | Ghi chú |
|---|---|---|
| `SELECT` | bảng biến | |
| `ASK` | true/false | **false = không tìm thấy khớp**, *không* phải "sai" (OWA) |
| `CONSTRUCT { mẫu }` | **đồ thị RDF mới** | ví dụ slide thêm `rdfs:seeAlso` tới Berlin; dùng để chuyển đổi vocab, sinh triple nghịch đảo (Q9) |
| `DESCRIBE <uri>` | đồ thị mô tả tài nguyên | nội dung **tùy cài đặt** endpoint |

### A7. Federation, built-in riêng, không suy diễn
- `SERVICE <http://dbpedia.org/sparql> { … }` — gửi một phần truy vấn tới endpoint khác, nối qua `owl:sameAs`.
- Built-in riêng của từng hệ: Virtuoso `bif:st_intersects` (bảo tàng trong bán kính 10 km).
- **SPARQL mặc định KHÔNG suy diễn** (simple entailment): `Museum ⊑ Building`, `Technoseum a Museum` ⇒ `?x a :Building` **không** trả Technoseum. Cách xử lý (slide): UNION với `?t rdfs:subClassOf :Building`, hoặc truy vấn trên **Jena RDFS model** (khi đó còn trả cả `rdfs:Resource` là kiểu). *(bổ sung: property path `a/rdfs:subClassOf*`; SPARQL 1.1 Entailment Regimes định nghĩa chế độ RDFS/OWL.)*

### A8. Triple Pattern Fragments (★)
- Máy chủ chỉ trả lời mẫu đơn `?s ?p ?o` có phân trang; client tự ghép ⇒ rẻ cho server, nhiều request (ví dụ phi hành gia: ~3.000 HTTP GET). Điểm giữa "chạy endpoint" và "tải dump".

---

## Phần B — Bổ sung SPARQL 1.1 (★★ — rất hay dùng khi viết truy vấn thật)

### B1. Gom nhóm & hàm tổng hợp *(bổ sung)*
```sparql
SELECT ?director (COUNT(?m) AS ?n) (GROUP_CONCAT(?title; separator=", ") AS ?titles)
WHERE { ?m :director ?director ; dc:title ?title }
GROUP BY ?director
HAVING (COUNT(?m) >= 2)          # lọc NHÓM (FILTER lọc DÒNG)
ORDER BY DESC(?n)
```
- Hàm: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP_CONCAT` (mặc định ngăn cách bằng **dấu cách**), `SAMPLE`; đều nhận `DISTINCT`.
- `COUNT(*)` đếm dòng; `COUNT(?x)` đếm dòng có ?x **bound**; `COUNT(DISTINCT ?x)`.
- **Luật vàng:** khi có GROUP BY, SELECT chỉ được chứa **biến đã group** hoặc **biểu thức tổng hợp** (`?name` không group ⇒ lỗi; dùng `SAMPLE(?name)`).
- Muốn hiện nhóm có 0 phần tử ⇒ dùng `OPTIONAL` rồi `COUNT(?x)` (xem Q4, P2).

### B2. Property path *(bổ sung)*
| Cú pháp | Nghĩa | Ví dụ |
|---|---|---|
| `p1/p2` | nối tiếp | `?x foaf:knows/foaf:name ?n` |
| `p1\|p2` | hoặc | `dc:title\|rdfs:label` |
| `^p` | ngược chiều | `?book ^:wrote ?author` = `?author :wrote ?book` |
| `p*` | 0 hoặc nhiều bước | `?c rdfs:subClassOf* :Teacher` (kể cả chính nó) |
| `p+` | 1 hoặc nhiều bước | `:dlHandbook :citedBy+ ?b` (Q21) |
| `p?` | 0 hoặc 1 bước | |
| `!p` | mọi predicate trừ p | `?x !rdf:type ?y` |
- Thành ngữ quan trọng: **`?x a/rdfs:subClassOf* :C`** = mọi thể hiện của C kể cả lớp con (giả lập rdfs9 + rdfs11); **`?s ?p ?o . ?p rdfs:subPropertyOf* :actor`** = giả lập rdfs7. Không giả lập được domain/range.
- Phần tử của danh sách RDF: `:list rdf:rest*/rdf:first ?e`.

### B3. Phủ định *(bổ sung)*
```sparql
# 1) FILTER NOT EXISTS — môn không có homework (Q3)
?c a :Course . FILTER NOT EXISTS { ?hw :isPartOf ?c }
# 2) MINUS
?c a :Course . MINUS { ?hw :isPartOf ?c }
# 3) "negation as failure" kiểu SPARQL 1.0 — OPTIONAL + !bound (Q20)
?c a :Course . OPTIONAL { ?hw :isPartOf ?c } FILTER (!bound(?hw))
```
- Thường cho cùng kết quả khi hai vế **có chung biến**. Khác nhau khi **không chung biến**: `MINUS { ?x ?y ?z }` không loại gì, còn `FILTER NOT EXISTS { ?x ?y ?z }` loại hết.
- Đây là suy luận **đóng** (closed-world) — trái với OWA của RDF/OWL; dùng để *kiểm tra dữ liệu*, không phải để suy diễn.

### B4. BIND, VALUES, biểu thức, subquery *(bổ sung)*
```sparql
BIND (2026 - xsd:integer(str(?year)) AS ?age)     # tạo biến mới (Q25)
VALUES ?publisher { "Springer" "MIT Press" }      # dữ liệu nội tuyến
SELECT (CONCAT(?first, " ", ?last) AS ?full) …    # biểu thức trong SELECT
FILTER (?x IN (:a, :b))     IF(?age >= 18, "adult", "minor")     COALESCE(?label, ?name, "?")
STRSTARTS / STRENDS / CONTAINS / STRLEN / UCASE / LCASE / SUBSTR(s, 1-based) / REPLACE / YEAR(?date) / NOW()
{ SELECT ?y (MIN(?name) AS ?minName) WHERE { ?y :name ?name } GROUP BY ?y }   # subquery
```

### B5. Named graph & UPDATE *(bổ sung, ★)*
```sparql
SELECT ?g ?s WHERE { GRAPH ?g { ?s a :Course } }          # FROM / FROM NAMED / GRAPH
INSERT DATA { :hw6 a :Homework ; :isPartOf :DataIntegration . }
DELETE DATA { :hw5 :isPartOf :MachineLearning . }
DELETE { ?p :name "Hung" } INSERT { ?p :name "Nguyen Hung" } WHERE { ?p :name "Hung" }
DELETE WHERE { ?hw :isPartOf :MLLab }
LOAD <http://example.org/data.ttl>      CLEAR GRAPH <http://example.org/g>
```

---

## Phần C — Khuôn viết truy vấn (D2)
1. **Đọc câu hỏi → gạch chân** cái cần trả về (→ SELECT), điều kiện (→ mẫu / FILTER), "nếu có" (→ OPTIONAL), "hoặc" (→ UNION), "không có" (→ FILTER NOT EXISTS), "bao nhiêu / mỗi" (→ COUNT + GROUP BY), "nhiều nhất / top k" (→ ORDER BY DESC + LIMIT k).
2. **Viết PREFIX** đầy đủ (mất điểm nếu thiếu).
3. **Vẽ nhanh mẫu đồ thị** trên giấy: nút = biến/URI, cạnh = property — rồi chép thành triple pattern.
4. **Kiểm tra:** literal có lang tag/datatype không? cần DISTINCT không? ontology có lớp con/property con mà dữ liệu dùng không (⇒ cần property path)? biến trong SELECT đã group chưa?
5. **Ghi kết quả mong đợi** (nếu đề có dữ liệu) — 1–2 dòng là đủ.

---

## Phần D — Bài tập viết truy vấn (25 câu — kết quả chạy thật bằng rdflib)

**Tóm tắt dữ liệu** (để làm trên giấy):
- **Môn học:** Professor `hung` (dạy SemanticWeb, DataIntegration; tổ chức SemanticWeb), `lan` (dạy MachineLearning; tổ chức MachineLearning, DataIntegration); Assistant `minh` (dạy SemanticWebLab), `an` (dạy SemanticWebLab, MLLab). Course: SemanticWeb (3 tín chỉ), DataIntegration (2), MachineLearning (3); LaboratoryCourse: SemanticWebLab (1), MLLab (1). Homework hw1–hw3 ⊂ SemanticWeb, hw4 ⊂ SemanticWebLab, hw5 ⊂ MachineLearning. Mọi thứ có `:name`.
- **Phim:** Avatar 2009 (James Cameron; leading Sam, Zoe; supporting Michelle) · Titanic 1997 (Cameron; male-lead Leo, female-lead Kate; supporting Billy; có thêm tiêu đề `@vi`) · The Terminator 1984 (Cameron; leading Arnold; supporting Michael) · Inception 2010 (Nolan; leading Leo; supporting Michael) · Our Planet 2019 (không diễn viên) · Fantasia 1940 (AnimatedMovie, không diễn viên). Tiêu đề dùng `dc:title "…"@en`, tên người `foaf:name`.
- **Thư viện:** A Semantic Web Primer (Textbook, 2012, 288 tr., Antoniou + van Harmelen, MIT Press) · Knowledge Graphs (Textbook, 2021, 257 tr., Hogan, Springer; citedBy owlGuide) · The DL Handbook (Textbook, 2003, 574 tr., Baader, Cambridge; citedBy swPrimer, kgBook) · Semantic Web for the Working Ontologist (Book, 2011, *không có số trang*, Allemang + Hendler, Morgan Kaufmann) · Truyện Kiều (Novel, 1820, 254 tr., Nguyễn Du, *không có NXB*; tiêu đề @vi và @en).

### Bộ 1 — Ontology môn học (Part 3 Ex3) · `files/ex3-lab-course.ttl`

**Q1.** Liệt kê tên giáo viên và tên môn họ dạy, sắp theo tên giáo viên.
<details><summary>Lời giải — <code>files/queries/q01-teacher-courses.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?teacherName ?courseName
WHERE {
  ?t :teaches ?c ;
     :name ?teacherName .
  ?c :name ?courseName .
}
ORDER BY ?teacherName ?courseName
```
| ?teacherName | ?courseName |
|---|---|
| "An" | "Machine Learning Lab" |
| "An" | "Semantic Web Lab" |
| "Hung" | "Data Integration" |
| "Hung" | "Semantic Web" |
| "Lan" | "Machine Learning" |
| "Minh" | "Semantic Web Lab" |

</details>

**Q2.** Các trợ giảng (Assistant) và môn thực hành họ dạy.
<details><summary>Lời giải — <code>files/queries/q02-assistants.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?assistant ?lab
WHERE {
  ?a a :Assistant ; :name ?assistant ; :teaches ?l .
  ?l a :LaboratoryCourse ; :name ?lab .
}
ORDER BY ?assistant ?lab
```
| ?assistant | ?lab |
|---|---|
| "An" | "Machine Learning Lab" |
| "An" | "Semantic Web Lab" |
| "Minh" | "Semantic Web Lab" |

</details>

**Q3.** Môn học (kể cả môn thực hành) KHÔNG có bài tập về nhà nào.
<details><summary>Lời giải — <code>files/queries/q03-courses-without-homework.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?courseName
WHERE {
  { ?c a :Course } UNION { ?c a :LaboratoryCourse }
  ?c :name ?courseName .
  FILTER NOT EXISTS { ?hw :isPartOf ?c }
}
ORDER BY ?courseName
```
| ?courseName |
|---|
| "Data Integration" |
| "Machine Learning Lab" |

</details>

**Q4.** Số bài tập về nhà của mỗi môn (môn không có bài tập phải hiện 0), sắp giảm dần.
<details><summary>Lời giải — <code>files/queries/q04-homework-count.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?courseName (COUNT(?hw) AS ?n)
WHERE {
  ?c :credits ?cr ; :name ?courseName .
  OPTIONAL { ?hw :isPartOf ?c }
}
GROUP BY ?courseName
ORDER BY DESC(?n) ?courseName
```
| ?courseName | ?n |
|---|---|
| "Semantic Web" | "3" |
| "Machine Learning" | "1" |
| "Semantic Web Lab" | "1" |
| "Data Integration" | "0" |
| "Machine Learning Lab" | "0" |

</details>

**Q5.** Giáo viên vừa dạy vừa tổ chức CÙNG một môn.
<details><summary>Lời giải — <code>files/queries/q05-teach-and-organize.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?teacherName ?courseName
WHERE {
  ?t :teaches ?c ; :organizes ?c ; :name ?teacherName .
  ?c :name ?courseName .
}
```
| ?teacherName | ?courseName |
|---|---|
| "Hung" | "Semantic Web" |
| "Lan" | "Machine Learning" |

</details>

**Q6.** Tất cả Teacher. SPARQL KHÔNG suy diễn: '?t a :Teacher' trả về rỗng vì dữ liệu chỉ ghi :Professor / :Assistant -> dùng property path rdfs:subClassOf* để tự đi lên cây lớp.
<details><summary>Lời giải — <code>files/queries/q06-all-teachers-path.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?name ?type
WHERE {
  ?t rdf:type ?type ; :name ?name .
  ?type rdfs:subClassOf* :Teacher .
}
ORDER BY ?name
```
| ?name | ?type |
|---|---|
| "An" | :Assistant |
| "Hung" | :Professor |
| "Lan" | :Professor |
| "Minh" | :Assistant |

</details>

**Q7.** Tổng số tín chỉ mỗi giáo viên dạy; chỉ giữ người dạy >= 3 tín chỉ.
<details><summary>Lời giải — <code>files/queries/q07-credits-per-teacher.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?teacherName (SUM(?cr) AS ?total)
WHERE {
  ?t :teaches ?c ; :name ?teacherName .
  ?c :credits ?cr .
}
GROUP BY ?teacherName
HAVING (SUM(?cr) >= 3)
ORDER BY DESC(?total) ?teacherName
```
| ?teacherName | ?total |
|---|---|
| "Hung" | "5" |
| "Lan" | "3" |

</details>

**Q8.** ASK: có trợ giảng nào dạy môn KHÔNG phải môn thực hành không? (kiểm tra ràng buộc 'only')
<details><summary>Lời giải — <code>files/queries/q08-ask-assistant-nonlab.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
ASK {
  ?a a :Assistant ; :teaches ?c .
  FILTER NOT EXISTS { ?c a :LaboratoryCourse }
}
```
Kết quả: **false**

</details>

**Q9.** CONSTRUCT: sinh các bộ ba nghịch đảo :isTaughtBy từ :teaches.
<details><summary>Lời giải — <code>files/queries/q09-construct-inverse.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
CONSTRUCT { ?c :isTaughtBy ?t }
WHERE     { ?t :teaches ?c }
```
Đồ thị kết quả:
```
:DataIntegration :isTaughtBy :hung .
:MLLab :isTaughtBy :an .
:MachineLearning :isTaughtBy :lan .
:SemanticWeb :isTaughtBy :hung .
:SemanticWebLab :isTaughtBy :an .
:SemanticWebLab :isTaughtBy :minh .
```

</details>

**Q10.** Mỗi môn kèm người tổ chức NẾU CÓ (OPTIONAL) — môn chưa có người tổ chức vẫn hiện.
<details><summary>Lời giải — <code>files/queries/q10-optional-organizer.rq</code></summary>

```sparql
PREFIX :     <http://example.org/course#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?courseName ?organizerName
WHERE {
  ?c :credits ?cr ; :name ?courseName .
  OPTIONAL { ?o :organizes ?c ; :name ?organizerName }
}
ORDER BY ?courseName ?organizerName
```
| ?courseName | ?organizerName |
|---|---|
| "Data Integration" | "Lan" |
| "Machine Learning" | "Lan" |
| "Machine Learning Lab" | - |
| "Semantic Web" | "Hung" |
| "Semantic Web Lab" | - |

</details>

### Bộ 2 — Ontology phim (Part 3 Ex4) · `files/ex4-film.ttl`

**Q11.** Tên phim tiếng Anh và năm phát hành, sắp theo năm tăng dần.
<details><summary>Lời giải — <code>files/queries/q11-movies-by-year.rq</code></summary>

```sparql
PREFIX :      <http://example.org/film#>
PREFIX film:  <http://example.org/film/>
PREFIX people:<http://example.org/people/>
PREFIX dc:    <http://purl.org/dc/elements/1.1/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?year
WHERE {
  ?m :releaseYear ?year ; dc:title ?title .
  FILTER (lang(?title) = "en")
}
ORDER BY ?year
```
| ?title | ?year |
|---|---|
| "Fantasia"@en | "1940"^^xsd:gYear |
| "The Terminator"@en | "1984"^^xsd:gYear |
| "Titanic"@en | "1997"^^xsd:gYear |
| "Avatar"@en | "2009"^^xsd:gYear |
| "Inception"@en | "2010"^^xsd:gYear |
| "Our Planet"@en | "2019"^^xsd:gYear |

</details>

**Q12.** Phim do 'James Cameron' đạo diễn, phát hành sau năm 1990.
<details><summary>Lời giải — <code>files/queries/q12-cameron-after-1990.rq</code></summary>

```sparql
PREFIX :      <http://example.org/film#>
PREFIX film:  <http://example.org/film/>
PREFIX people:<http://example.org/people/>
PREFIX dc:    <http://purl.org/dc/elements/1.1/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?year
WHERE {
  ?m :director ?d ; dc:title ?title ; :releaseYear ?year .
  ?d foaf:name "James Cameron" .
  FILTER (lang(?title) = "en" && xsd:integer(str(?year)) > 1990)
}
ORDER BY ?year
```
| ?title | ?year |
|---|---|
| "Titanic"@en | "1997"^^xsd:gYear |
| "Avatar"@en | "2009"^^xsd:gYear |

</details>

**Q13.** Mọi diễn viên của mọi phim, dù dùng :leading-actor, :supporting-actor, :male-lead hay :female-lead. Không có suy diễn subPropertyOf -> tự đi theo rdfs:subPropertyOf*.
<details><summary>Lời giải — <code>files/queries/q13-all-actors-subproperty.rq</code></summary>

```sparql
PREFIX :      <http://example.org/film#>
PREFIX film:  <http://example.org/film/>
PREFIX people:<http://example.org/people/>
PREFIX dc:    <http://purl.org/dc/elements/1.1/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?title ?actorName
WHERE {
  ?m ?p ?a ; dc:title ?title .
  ?p rdfs:subPropertyOf* :actor .
  ?a foaf:name ?actorName .
  FILTER (lang(?title) = "en")
}
ORDER BY ?title ?actorName
```
| ?title | ?actorName |
|---|---|
| "Avatar"@en | "Michelle Rodriguez" |
| "Avatar"@en | "Sam Worthington" |
| "Avatar"@en | "Zoe Saldana" |
| "Inception"@en | "Leonardo DiCaprio" |
| "Inception"@en | "Michael Biehn" |
| "The Terminator"@en | "Arnold Schwarzenegger" |
| "The Terminator"@en | "Michael Biehn" |
| "Titanic"@en | "Billy Zane" |
| "Titanic"@en | "Kate Winslet" |
| "Titanic"@en | "Leonardo DiCaprio" |

</details>

**Q14.** Phim không có diễn viên nào (ứng viên AnimalDocumentary / AnimatedMovie).
<details><summary>Lời giải — <code>files/queries/q14-movies-without-actor.rq</code></summary>

```sparql
PREFIX :      <http://example.org/film#>
PREFIX film:  <http://example.org/film/>
PREFIX people:<http://example.org/people/>
PREFIX dc:    <http://purl.org/dc/elements/1.1/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT ?title
WHERE {
  ?m dc:title ?title .
  FILTER NOT EXISTS { ?m ?p ?a . ?p rdfs:subPropertyOf* :actor . }
}
ORDER BY ?title
```
| ?title |
|---|
| "Fantasia"@en |
| "Our Planet"@en |

</details>

**Q15.** Diễn viên đóng từ 2 phim trở lên, kèm số phim.
<details><summary>Lời giải — <code>files/queries/q15-actors-two-movies.rq</code></summary>

```sparql
PREFIX :      <http://example.org/film#>
PREFIX film:  <http://example.org/film/>
PREFIX people:<http://example.org/people/>
PREFIX dc:    <http://purl.org/dc/elements/1.1/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT ?name (COUNT(DISTINCT ?m) AS ?movies)
WHERE {
  ?m ?p ?a .
  ?p rdfs:subPropertyOf* :actor .
  ?a foaf:name ?name .
}
GROUP BY ?name
HAVING (COUNT(DISTINCT ?m) >= 2)
ORDER BY DESC(?movies) ?name
```
| ?name | ?movies |
|---|---|
| "Leonardo DiCaprio" | "2" |
| "Michael Biehn" | "2" |

</details>

**Q16.** Mỗi đạo diễn làm bao nhiêu phim và danh sách tên phim.
<details><summary>Lời giải — <code>files/queries/q16-movies-per-director.rq</code></summary>

```sparql
PREFIX :      <http://example.org/film#>
PREFIX film:  <http://example.org/film/>
PREFIX people:<http://example.org/people/>
PREFIX dc:    <http://purl.org/dc/elements/1.1/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT ?director (COUNT(?m) AS ?n) (GROUP_CONCAT(?title; separator=", ") AS ?titles)
WHERE {
  ?m :director ?d ; dc:title ?title .
  ?d foaf:name ?director .
  FILTER (lang(?title) = "en")
}
GROUP BY ?director
ORDER BY DESC(?n)
```
| ?director | ?n | ?titles |
|---|---|---|
| "James Cameron" | "3" | "Avatar, Titanic, The Terminator" |
| "Christopher Nolan" | "1" | "Inception" |

</details>

**Q17.** Các cặp diễn viên cùng đóng một phim (mỗi cặp chỉ một lần).
<details><summary>Lời giải — <code>files/queries/q17-coactors.rq</code></summary>

```sparql
PREFIX :      <http://example.org/film#>
PREFIX film:  <http://example.org/film/>
PREFIX people:<http://example.org/people/>
PREFIX dc:    <http://purl.org/dc/elements/1.1/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?n1 ?n2 ?title
WHERE {
  ?m ?p1 ?a1 ; ?p2 ?a2 ; dc:title ?title .
  ?p1 rdfs:subPropertyOf* :actor .
  ?p2 rdfs:subPropertyOf* :actor .
  ?a1 foaf:name ?n1 . ?a2 foaf:name ?n2 .
  FILTER (str(?n1) < str(?n2) && lang(?title) = "en")
}
ORDER BY ?title ?n1 ?n2
```
| ?n1 | ?n2 | ?title |
|---|---|---|
| "Michelle Rodriguez" | "Sam Worthington" | "Avatar"@en |
| "Michelle Rodriguez" | "Zoe Saldana" | "Avatar"@en |
| "Sam Worthington" | "Zoe Saldana" | "Avatar"@en |
| "Leonardo DiCaprio" | "Michael Biehn" | "Inception"@en |
| "Arnold Schwarzenegger" | "Michael Biehn" | "The Terminator"@en |
| "Billy Zane" | "Kate Winslet" | "Titanic"@en |
| "Billy Zane" | "Leonardo DiCaprio" | "Titanic"@en |
| "Kate Winslet" | "Leonardo DiCaprio" | "Titanic"@en |

</details>

**Q18.** Tên phim tiếng Anh, kèm tên tiếng Việt nếu có (FILTER lang đặt TRONG OPTIONAL).
<details><summary>Lời giải — <code>files/queries/q18-vietnamese-title-optional.rq</code></summary>

```sparql
PREFIX :      <http://example.org/film#>
PREFIX film:  <http://example.org/film/>
PREFIX people:<http://example.org/people/>
PREFIX dc:    <http://purl.org/dc/elements/1.1/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT ?en ?vi
WHERE {
  ?m dc:title ?en .
  FILTER (lang(?en) = "en")
  OPTIONAL { ?m dc:title ?vi . FILTER (lang(?vi) = "vi") }
}
ORDER BY ?en
```
| ?en | ?vi |
|---|---|
| "Avatar"@en | - |
| "Fantasia"@en | - |
| "Inception"@en | - |
| "Our Planet"@en | - |
| "The Terminator"@en | - |
| "Titanic"@en | "Titanic"@vi |

</details>

### Bộ 3 — Thư viện (Part 1 Ex7) · `files/library.ttl`

**Q19.** Mỗi cuốn sách (tiêu đề tiếng Anh) và danh sách tác giả.
<details><summary>Lời giải — <code>files/queries/q19-books-authors.rq</code></summary>

```sparql
PREFIX :     <http://example.org/library#>
PREFIX dc:   <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?title (GROUP_CONCAT(?author; separator="; ") AS ?authors)
WHERE {
  ?b dc:title ?title ; :writtenBy ?a .
  ?a foaf:name ?author .
  FILTER langMatches(lang(?title), "en")
}
GROUP BY ?title
ORDER BY ?title
```
| ?title | ?authors |
|---|---|
| "A Semantic Web Primer"@en | "Grigoris Antoniou; Frank van Harmelen" |
| "Knowledge Graphs"@en | "Aidan Hogan" |
| "Semantic Web for the Working Ontologist"@en | "Dean Allemang; James Hendler" |
| "The Description Logic Handbook"@en | "Franz Baader" |
| "The Tale of Kieu"@en | "Nguyễn Du" |

</details>

**Q20.** Sách thiếu nhà xuất bản HOẶC thiếu số trang (mẫu OPTIONAL + !bound).
<details><summary>Lời giải — <code>files/queries/q20-books-missing-info.rq</code></summary>

```sparql
PREFIX :     <http://example.org/library#>
PREFIX dc:   <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?publisher ?pages
WHERE {
  ?b dc:title ?title .
  FILTER (lang(?title) = "en")
  OPTIONAL { ?b :publishedBy ?p . ?p foaf:name ?publisher }
  OPTIONAL { ?b :pages ?pages }
  FILTER (!bound(?publisher) || !bound(?pages))
}
ORDER BY ?title
```
| ?title | ?publisher | ?pages |
|---|---|---|
| "Semantic Web for the Working Ontologist"@en | "Morgan Kaufmann" | - |
| "The Tale of Kieu"@en | - | "254" |

</details>

**Q21.** Mọi sách trích dẫn DL Handbook trực tiếp hoặc bắc cầu (:citedBy+).
<details><summary>Lời giải — <code>files/queries/q21-transitive-citations.rq</code></summary>

```sparql
PREFIX :     <http://example.org/library#>
PREFIX dc:   <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?title
WHERE {
  :dlHandbook :citedBy+ ?b .
  ?b dc:title ?title .
}
ORDER BY ?title
```
| ?title |
|---|
| "A Semantic Web Primer"@en |
| "Knowledge Graphs"@en |
| "Semantic Web for the Working Ontologist"@en |

</details>

**Q22.** Số trang trung bình, lớn nhất, nhỏ nhất của các sách có ghi số trang.
<details><summary>Lời giải — <code>files/queries/q22-avg-pages.rq</code></summary>

```sparql
PREFIX :     <http://example.org/library#>
PREFIX dc:   <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT (AVG(?p) AS ?avg) (MAX(?p) AS ?max) (MIN(?p) AS ?min) (COUNT(?b) AS ?n)
WHERE { ?b :pages ?p }
```
| ?avg | ?max | ?min | ?n |
|---|---|---|---|
| "343.25" | "574" | "254" | "4" |

</details>

**Q23.** Tác giả có tên chứa 'an' (không phân biệt hoa thường).
<details><summary>Lời giải — <code>files/queries/q23-regex-authors.rq</code></summary>

```sparql
PREFIX :     <http://example.org/library#>
PREFIX dc:   <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?name
WHERE {
  ?a a :Author ; foaf:name ?name .
  FILTER regex(?name, "an", "i")
}
ORDER BY ?name
```
| ?name |
|---|
| "Aidan Hogan" |
| "Dean Allemang" |
| "Frank van Harmelen" |
| "Franz Baader" |
| "Grigoris Antoniou" |

</details>

**Q24.** Tất cả :Book (kể cả :Textbook, :Novel) qua rdf:type/rdfs:subClassOf*, sách mới nhất trước.
<details><summary>Lời giải — <code>files/queries/q24-books-typed-via-path.rq</code></summary>

```sparql
PREFIX :     <http://example.org/library#>
PREFIX dc:   <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?title ?year
WHERE {
  ?b a/rdfs:subClassOf* :Book ; dc:title ?title ; :year ?year .
  FILTER (lang(?title) = "en")
}
ORDER BY DESC(?year)
```
| ?title | ?year |
|---|---|
| "Knowledge Graphs"@en | "2021"^^xsd:gYear |
| "A Semantic Web Primer"@en | "2012"^^xsd:gYear |
| "Semantic Web for the Working Ontologist"@en | "2011"^^xsd:gYear |
| "The Description Logic Handbook"@en | "2003"^^xsd:gYear |
| "The Tale of Kieu"@en | "1820"^^xsd:gYear |

</details>

**Q25.** VALUES + BIND: với 2 nhà xuất bản cho trước, liệt kê sách và 'tuổi' sách tính đến 2026.
<details><summary>Lời giải — <code>files/queries/q25-values-bind.rq</code></summary>

```sparql
PREFIX :     <http://example.org/library#>
PREFIX dc:   <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
SELECT ?publisher ?title ?age
WHERE {
  VALUES ?publisher { "Springer" "MIT Press" }
  ?p foaf:name ?publisher .
  ?b :publishedBy ?p ; dc:title ?title ; :year ?y .
  BIND (2026 - xsd:integer(str(?y)) AS ?age)
}
ORDER BY ?age
```
| ?publisher | ?title | ?age |
|---|---|---|
| "Springer" | "Knowledge Graphs"@en | "5" |
| "MIT Press" | "A Semantic Web Primer"@en | "14" |

</details>

---

## Phần E — Đoán kết quả (che lời giải, tự viết bảng kết quả ra giấy)

**P1.** Ontology có `Professor ⊑ Teacher`. Truy vấn sau trả về gì?
```sparql
PREFIX : <http://example.org/course#>
SELECT ?t WHERE { ?t a :Teacher }
```
<details><summary>Đáp án</summary>

| ?t |
|---|
| *(không có dòng nào)* |

Rỗng — SPARQL mặc định **không suy diễn** (simple entailment); dữ liệu chỉ ghi `a :Professor` / `a :Assistant`. Sửa: `?t a/rdfs:subClassOf* :Teacher` (Q6) hoặc chạy trên endpoint có RDFS reasoning.
</details>

**P2.** Bỏ `OPTIONAL` trong Q4 thì kết quả khác gì?
```sparql
PREFIX : <http://example.org/course#>
SELECT ?courseName (COUNT(?hw) AS ?n)
WHERE { ?c :name ?courseName . ?hw :isPartOf ?c }
GROUP BY ?courseName ORDER BY DESC(?n)
```
<details><summary>Đáp án</summary>

| ?courseName | ?n |
|---|---|
| "Semantic Web" | "3" |
| "Machine Learning" | "1" |
| "Semantic Web Lab" | "1" |

Hai môn **không có homework biến mất** (không thể đếm ra 0) — muốn hiện 0 phải dùng OPTIONAL rồi `COUNT(?hw)` (COUNT bỏ qua giá trị unbound).
</details>

**P3.** Đặt `FILTER(lang(?vi) = "vi")` **ngoài** OPTIONAL (so với Q18) thì sao?
```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT ?en ?vi
WHERE { ?m dc:title ?en . FILTER(lang(?en) = "en")
        OPTIONAL { ?m dc:title ?vi }
        FILTER(lang(?vi) = "vi") }
```
<details><summary>Đáp án</summary>

| ?en | ?vi |
|---|---|
| "Titanic"@en | "Titanic"@vi |

Chỉ còn Titanic: FILTER ngoài áp cho **cả nhóm** ⇒ loại mọi dòng mà ?vi không phải tiếng Việt (hoặc unbound → lỗi → bị loại). FILTER *trong* OPTIONAL chỉ là điều kiện ghép.
</details>

**P4.** Phim Avatar có `male-lead` không? (ontology: `male-lead ⊑ leading-actor`, Sam là `:Man`)
```sparql
PREFIX : <http://example.org/film#>
PREFIX film: <http://example.org/film/>
ASK { film:avatar :male-lead ?x }
```
<details><summary>Đáp án</summary>

Kết quả: **false**

**false** — dữ liệu chỉ có `:leading-actor`; subPropertyOf suy theo chiều **từ con lên cha** (male-lead ⇒ leading-actor), không có chiều ngược lại; và SPARQL không suy diễn. `false` của ASK nghĩa là *không tìm thấy*, không phải *sai trong thế giới thật* (OWA).
</details>

**P5.** So sánh hai truy vấn: có DISTINCT và không có DISTINCT.
```sparql
PREFIX : <http://example.org/film#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name WHERE { ?m :director ?d . ?d foaf:name ?name }
```
<details><summary>Đáp án</summary>

| ?name |
|---|
| "James Cameron" |
| "James Cameron" |
| "James Cameron" |
| "Christopher Nolan" |

James Cameron xuất hiện **3 lần** (một lần mỗi phim). `SELECT DISTINCT ?name` ⇒ 2 dòng. Nhớ: DISTINCT loại **dòng trùng**, không gộp hai URI khác nhau chỉ cùng một người (UNA).
</details>

---

## Phần F — Bẫy hay gặp (tự kiểm trước khi nộp)
| Bẫy | Hậu quả | Cách tránh |
|---|---|---|
| quên lang tag: `?m dc:title "Avatar"` | 0 kết quả vì dữ liệu là `"Avatar"@en` | `"Avatar"@en` hoặc `FILTER(str(?t) = "Avatar")` |
| truy vấn lớp cha `?x a :Teacher` | rỗng — không suy diễn | `?x a/rdfs:subClassOf* :Teacher` |
| dùng property cha `?m :actor ?a` | rỗng — dữ liệu dùng property con | `?m ?p ?a . ?p rdfs:subPropertyOf* :actor` |
| FILTER đặt ngoài OPTIONAL | mất các dòng "không có" | đặt FILTER bên trong OPTIONAL |
| SELECT biến chưa GROUP BY | lỗi cú pháp | thêm vào GROUP BY hoặc `SAMPLE()` |
| đếm với join thường | nhóm 0 phần tử biến mất | `OPTIONAL` + `COUNT(?x)` |
| hiểu ASK false = "sai" | sai lý thuyết (OWA) | "không tìm thấy trong dữ liệu" |
| `FILTER(?a != ?b)` = "hai người khác nhau" | sai lý thuyết (UNA) | cần `owl:differentFrom` để khẳng định |
| so sánh năm `xsd:gYear` | một số engine không so sánh được | `xsd:integer(str(?y)) > 1990` |
| thứ tự `GROUP_CONCAT` | không xác định | không dựa vào thứ tự |

---
**Nguồn:** slide Ext_SPARQL (Paulheim, IE650). *(bổ sung)* W3C SPARQL 1.1 Query https://www.w3.org/TR/sparql11-query/ · SPARQL 1.1 Update https://www.w3.org/TR/sparql11-update/ · SPARQL 1.1 Entailment Regimes https://www.w3.org/TR/sparql11-entailment/ · SPARQL 1.1 Federated Query https://www.w3.org/TR/sparql11-federated-query/
