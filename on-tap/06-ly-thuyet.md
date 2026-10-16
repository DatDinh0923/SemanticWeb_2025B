# 06 — Lý thuyết tự luận: câu hỏi + dàn ý trả lời (★–★★)

> Slide: `01_Intro.pdf`, `Ext_Knowledge-Graphs.pdf`, `Ext. Labeled-Property-Graphs.pdf`, `Ext. App-Linked Widget.pdf`, `Ext. App-StatSpace.pdf` + câu tổng hợp xuyên suốt khóa.
> Cách học: đọc câu hỏi → **tự viết dàn ý 3–5 ý** ra giấy (2–3 phút) → mở đáp án so sánh. Câu lý thuyết trong đề tự luận thường chiếm ít điểm nhưng dễ ăn nếu có **định nghĩa + ví dụ + so sánh**.

---

## Phần A — Nhập môn (01_Intro) ★★

**T1. Knowledge graph là gì? Nêu các định nghĩa và đặc điểm.**
<details><summary>Dàn ý</summary>

- Các định nghĩa trên slide: Blumauer 2014, Pujara 2013, Krötzsch & Weikum 2016. **Paulheim 2017** — một KG:
  1. mô tả **thực thể và quan hệ** giữa chúng dưới dạng **đồ thị**;
  2. định nghĩa **lớp và quan hệ** trong một **schema/ontology**;
  3. cho phép **liên kết tùy ý** các thực thể với nhau;
  4. bao phủ **nhiều miền** (domain).
- Google 2012: *"things, not strings"*.
- Về hình thức: đồ thị có hướng, có nhãn, không đồng nhất, có chu trình; kiểu nút = class, kiểu cạnh = property.
</details>

**T2. Tầm nhìn Semantic Web; vấn đề của "Web cổ điển".**
<details><summary>Dàn ý</summary>

- Berners-Lee, Hendler & Lassila, *Scientific American* 2001. Web tài liệu: **người đọc được, máy không hiểu**. Ví dụ slide: trang "Dr. Mark Smith, Physician, Smalltown" — người thấy tên, nghề, địa chỉ; máy chỉ thấy chuỗi ký tự/thẻ HTML.
- Vấn đề:
  - tìm kiếm theo từ khóa (đồng nghĩa, đồng âm);
  - link không có kiểu;
  - thông tin rải rác nhiều trang, không tự động gom được.
- Mục tiêu: dữ liệu có ngữ nghĩa máy xử lý được ⇒ trả lời câu hỏi, tích hợp, suy diễn.
- So sánh trên slide:
  - **Wolfram Alpha**: tri thức có cấu trúc, suy diễn tường minh ⇒ dữ kiện chính xác.
  - **ChatGPT**: tri thức phi cấu trúc, suy diễn heuristic ⇒ tri thức phổ thông, có thể "ảo giác".
</details>

**T3. Vẽ và giải thích Semantic Web stack ("layer cake").**
<details><summary>Dàn ý</summary>

- Từ dưới lên:
  - **URI/IRI + Unicode**
  - **XML** (+ namespace)
  - **RDF** (mô hình dữ liệu)
  - **RDFS** (từ vựng/schema)
  - **OWL** (ontology), **SPARQL** (truy vấn), **RIF/SWRL** (luật)
  - Logic → Proof → **Trust**
  - Crypto (chữ ký) chạy dọc; User interface & applications trên cùng.
- Slide ghi các tầng trên cùng là *"here be dragons"* — chưa chuẩn hóa/chưa giải quyết.
- Ý nghĩa: mỗi tầng dựa trên tầng dưới. Cú pháp (XML, Turtle) ⇒ **interoperability cú pháp**; RDFS/OWL ⇒ **interoperability ngữ nghĩa**.
</details>

**T4. Phân biệt interoperability cú pháp và ngữ nghĩa. Vì sao XML chưa đủ?**
<details><summary>Dàn ý</summary>

- **Cú pháp:**
  - Bảng mã: ASCII, ISO-8859, Unicode.
  - XML well-formed; XPath (`/physician[name='Dr. Mark Smith']/telephone/number`); namespace.
  - **DTD / XML Schema** quy định *cấu trúc* hợp lệ.
- **Ngữ nghĩa:** máy hiểu *nghĩa* của thẻ.
  - DTD/Schema chỉ quy định cú pháp. Slide minh họa bằng cách **xáo trộn tên thẻ**: với máy, tài liệu vẫn "như nhau".
  - Tên thẻ vô nghĩa với máy ⇒ cần RDF (mô hình triple thống nhất) + RDFS/OWL (định nghĩa nghĩa hình thức, cho suy diễn).
</details>

**T5. URI vs URL; vì sao Semantic Web dùng URI làm định danh?**
<details><summary>Dàn ý</summary>

- Cấu trúc URI: scheme://authority/path?query#fragment.
- **URL** = URI **định vị được** (dereference qua giao thức).
- URI giúp định danh **toàn cục, không trùng tên** giữa các nguồn dữ liệu.
- HTTP URI vừa định danh vừa tra được ⇒ nguyên tắc 2 của Linked Data.
- Phân biệt URI của **sự vật** và URI của **tài liệu** mô tả nó (303 / hash URI).
</details>

---

## Phần B — Câu tổng hợp xuyên suốt ★★★ (rất hay ra)

**T6. Open World Assumption vs Closed World Assumption. Ảnh hưởng tới RDFS, OWL, SPARQL, cơ sở dữ liệu.**
<details><summary>Dàn ý</summary>

- **OWA:** không biết ≠ sai.
  - Ví dụ: `:Peter :fatherOf :Julia , :Mary` ⇒ Peter có **ít nhất** 1 con.
- **CWA** (CSDL, Prolog, Cypher): không có trong dữ liệu ⇒ sai.
- Hệ quả trong RDFS/OWL:
  - suy diễn thận trọng: unknown thay vì false (bài 5.9/12.9);
  - cần **closure axiom** (pizza Margherita);
  - `only` thỏa tầm thường;
  - reasoner không báo "thiếu dữ liệu" (Course phải có homework mà chưa có ⇒ không lỗi).
- Trong SPARQL:
  - truy vấn trên dữ liệu thực tế mang tính đóng: `FILTER NOT EXISTS`, `COUNT`;
  - nhưng **ASK false** chỉ là "không tìm thấy".
  - Muốn kiểm tra ràng buộc đóng ⇒ SPARQL/**SHACL**.
- Vì sao Web dùng OWA: Web không bao giờ đầy đủ; nguyên tắc **AAA** (Anybody can say Anything about Anything).
</details>

**T7. Non-unique name assumption. Ví dụ hệ quả trong OWL và SPARQL.**
<details><summary>Dàn ý</summary>

- Hai URI khác nhau có thể cùng chỉ một thực thể (`:Munich`, `:München`).
- **OWL:**
  - FunctionalProperty sinh `sameAs` thay vì mâu thuẫn (Helsinki/Helsingfors);
  - cardinality ≥ 2 chỉ được thỏa khi các cá thể `differentFrom` nhau.
- **SPARQL:** `FILTER(?a != ?b)` không chứng minh hai thực thể khác nhau; `DISTINCT` không gộp thực thể trùng.
- Công cụ: `owl:sameAs`, `owl:differentFrom`, `owl:AllDifferent`.
</details>

**T8. So sánh RDFS và OWL (bảng).**
<details><summary>Dàn ý</summary>

| | RDFS | OWL |
|---|---|---|
| Biểu đạt | lớp, thuộc tính, phân cấp, domain/range | + restriction, cardinality, đặc tính property, toán tử tập hợp, disjoint, equality, oneOf |
| Phủ định / mâu thuẫn | không có ⇒ luôn consistent | có (complementOf, disjointWith) ⇒ phát hiện inconsistency |
| Suy diễn | forward chaining, luật rdfs1–13, luôn dừng | tableau (DL), có thể đắt (N2EXPTIME cho OWL 2 DL); profile EL/QL/RL đa thức |
| Ví dụ không làm được | "Madrid không phải bang", "Baby và Adult rời nhau" | làm được bằng `disjointWith` |
| Quan hệ | OWL Full tương thích hoàn toàn với RDFS | OWL DL hạn chế để quyết định được |
</details>

**T9. Forward chaining vs tableau.**
<details><summary>Dàn ý</summary>

- **Forward chaining** (RDFS, OWL RL):
  - áp luật từ dữ liệu đến điểm bất động;
  - đơn giản, materialize được, luôn dừng (không tạo tài nguyên mới);
  - **không xử lý được ⊔ và ¬**.
- **Tableau** (OWL DL):
  - chứng minh phản chứng, tách nhánh khi gặp ⊔, sinh cá thể mới khi gặp ∃ (cần **blocking** để dừng);
  - mọi bài toán quy về consistency.
- Ví dụ: `TwoWheeledVehicle ≡ Bicycle ⊔ Motorbike` chỉ tableau xử lý được.
</details>

**T10. Domain/range trong RDFS/OWL khác "ràng buộc" trong CSDL / lập trình hướng đối tượng thế nào?**
<details><summary>Dàn ý</summary>

- Trong RDFS/OWL, domain/range là **tiên đề suy diễn**, không phải ràng buộc kiểm tra.
- Dùng property với "sai" kiểu ⇒ reasoner **suy ra kiểu mới**, không báo lỗi. Ví dụ pizza: IceCream dùng `hasTopping` (domain Pizza) ⇒ IceCream thành Pizza ⇒ do disjoint ⇒ unsatisfiable.
- Nhiều domain = **giao** (không phải hợp).
- Muốn kiểm tra kiểu ⇒ SHACL / SPARQL.
</details>

**T11. Reification, named graph, RDF-star: so sánh cách "phát biểu về phát biểu".**
<details><summary>Dàn ý</summary>

| | Reification (RDF) | Named graph (TriG/quad) | RDF-star |
|---|---|---|---|
| Cú pháp | `rdf:Statement` + subject/predicate/object | `GRAPH :g { … }` | `<< :s :p :o >> :source :x` |
| Chi phí | 4 triple / phát biểu | 1 IRI đồ thị cho nhóm triple | gọn, lồng được |
| Khẳng định triple gốc? | **không** (ngữ nghĩa W3C) | có (trong đồ thị đó) | quoted triple **không** được khẳng định; `{| … |}` annotation thì có |

- *Slide LPG (tr. 22) lưu ý:* "In RDF, when we make a statement about a statement S, S is automatically assumed to be true" — cách hiểu trong thực hành. Khi làm bài lấy ngữ nghĩa W3C làm câu trả lời chính: reify một phát biểu **không** khẳng định triple gốc.

- Ví dụ slide (RDF-star): "Peter nói Hamburg là City, Mary nói là Country" — **không mâu thuẫn** vì không khẳng định.
- DBpedia CareerStation chiếm ~45% thực thể: minh họa RDF "dài dòng" cho dữ liệu n-ngôi.
</details>

---

## Phần C — Mở rộng: Knowledge Graphs công cộng (Ext_Knowledge-Graphs) ★

**T12. Lịch sử xây dựng KG và bài học từ mỗi dự án.**
<details><summary>Dàn ý</summary>

| Dự án | Bài học |
|---|---|
| **Cyc** | công sức thủ công cao ↔ chính xác cao |
| **Freebase** | sự tham gia của người dùng ↔ tính hình thức |
| **Wikidata** | đơn giản ↔ đa nguồn (plurality) + provenance |
| **DBpedia / YAGO** | heuristic tăng độ phủ nhưng giảm độ chính xác |
| **NELL** (đọc web liên tục; ví dụ mẫu "X singer Y" → band_member) | chất lượng cần con người can thiệp |

- KG riêng: Google KG, Microsoft Satori, Facebook…
- So sánh KG (Ringler & Paulheim 2017): kích thước, độ phủ 25 lớp, độ chồng lấn.
</details>

**T13. Chi phí mỗi triple của các KG (slide) và ý nghĩa.**
<details><summary>Dàn ý</summary>

- Số liệu: Cyc **$5.71**, Freebase **$2.25**, NELL 14.25¢, DBpedia **1.85¢**, YAGO 0.83¢.
- Ý nghĩa: tự động hóa (trích từ Wikipedia) **rẻ hơn 16–250 lần** (Ext_KG tr. 52) nhưng phải đánh đổi về chất lượng.
- Các hướng tăng độ phủ:
  - red links / list pages;
  - **Cat2Ax** (tiên đề từ category, ví dụ `∃genre.{Rock}`);
  - CaLiGraph (15M thực thể);
  - DBkWik (wiki Fandom);
  - WebIsALOD (mẫu Hearst, 400M quan hệ is-a, điểm tin cậy bằng RandomForest).
</details>

---

## Phần D — Labeled Property Graph & Cypher (Ext. LPG) ★★

**T14. So sánh RDF (RDF-star) và Labeled Property Graph (Neo4j).**
<details><summary>Dàn ý</summary>

| | RDF / RDF-star | LPG (Neo4j) |
|---|---|---|
| Nút | URI / blank node / literal | nút có **nhiều label** + cặp key/value |
| Cạnh | predicate (URI), không có thuộc tính (trừ reification/RDF-star) | **một type**, **có thuộc tính** key/value (chỉ literal) |
| Định danh toàn cục | URI — liên kết Web | ID cục bộ |
| Ngữ nghĩa | **open world**, có RDFS/OWL suy diễn | **closed world**, không suy diễn chuẩn |
| Truy vấn | SPARQL (path quantifier yếu) | Cypher (variable-length path mạnh) |
| Phát biểu về phát biểu | RDF-star quoted triple | không quote được statement |
</details>

**T15. Viết Cypher tương đương SPARQL.**
<details><summary>Dàn ý</summary>

```
MATCH (m:Movie {title:"The Matrix"})<-[r:ACTED_IN]-(p:Person) RETURN p.name, r.roles
MATCH (p:Person)-[:ACTED_IN]->(m) WITH p, COUNT(m) AS c WHERE c >= 2 RETURN p.name, c
MATCH (a)-[:KNOWS*1..4]->(b) RETURN b        // độ dài đường đi biến thiên
```

- Hàm hay gặp: `labels(n)`, `type(r)`, `WHERE n.name STARTS WITH "A"`.
- Cập nhật bằng `CREATE` / `SET` — đây là cập nhật đồ thị, **không** phải suy diễn.
- Cypher **đếm theo closed-world** (giống SQL `HAVING`), khác cách hiểu OWA của RDF.
</details>

---

## Phần E — Hai bài ứng dụng (Ext. App) ★

**T16. Linked Widgets.**
<details><summary>Dàn ý</summary>

- Mục tiêu: tích hợp dữ liệu Linked Data kiểu **mashup** cho người dùng cuối. Ví dụ: công viên, bể bơi, chất lượng không khí Vienna từ CSV/XML/JSON.
- Widget W3C có **mô hình ngữ nghĩa** cho input/output (chạy client hoặc server).
- Các bước:
  - khám phá widget theo ngữ nghĩa (Ontology Alignment API);
  - so khớp terminal (cây input/output);
  - **tự động ghép** widget — quy về tìm mọi chu trình (thuật toán Johnson).
</details>

**T17. StatSpace.**
<details><summary>Dàn ý</summary>

- Khám phá và tích hợp **dữ liệu thống kê** không đồng nhất. Ba loại không đồng nhất: **cú pháp, ngữ nghĩa, truy cập**.
- Ánh xạ **RML** (JSON World Bank → **RDF Data Cube** `qb:Observation`).
- Gắn chiều không gian/thời gian dùng chung:
  - SDMX `refArea` / `refPeriod`;
  - dịch vụ tham chiếu thời gian UK;
  - geocoding để ánh xạ vùng.
- Giải quyết "cùng một khu vực" bằng URI dùng chung, `owl:sameAs` hoặc so khớp nhãn.
</details>

---

## Phần F — Câu hỏi "vì sao" ngắn (luyện trả lời 3–4 dòng)
1. Vì sao literal không được làm subject? ⇒ Hệ quả: DatatypeProperty không thể Symmetric, Transitive, Inverse.
2. Vì sao suy diễn RDFS luôn dừng? ⇒ Không tạo tài nguyên mới; số triple có thể có là hữu hạn.
3. Vì sao OWL Full không quyết định được? ⇒ Không tách class / property / individual (lớp vừa là cá thể); quá biểu đạt.
4. Vì sao cần rule blocking? ⇒ Luật ∃ sinh cá thể mới vô hạn (ví dụ Jane `hasMother`).
5. Vì sao `FILTER(?c1 != ?c2)` không chứng minh "có 2 con"? ⇒ **Không có** UNA (hai URI khác nhau vẫn có thể là một người) + OWA.
6. Vì sao dùng `EquivalentTo` thay vì `SubClassOf` cho lớp định nghĩa? ⇒ Để reasoner **tự phân loại** cá thể và lớp vào đó.
7. Vì sao `owl:sameAs` giữa một người và trang chủ của họ là sai? ⇒ Mọi thuộc tính bị chia sẻ: trang web "có ngày sinh", người "có định dạng HTML".
8. Microdata/schema.org khác Linked Open Data ở đâu? (slide so Microdata với **LOD**, không so với RDFa) ⇒ Microdata nhúng trong cây DOM nên RDF sinh ra luôn là tập cây: không chu trình, không reification; chỉ có blank node + literal (không URI tra cứu được) ⇒ trái nguyên tắc LOD, khó liên kết.
9. Vì sao không có default datatype trong RDF? ⇒ `"München"@de` khác `"München"@en` khác `"München"^^xsd:string`.
10. Vì sao tableau dùng NNF? ⇒ Phủ định chỉ đứng trước lớp nguyên tử ⇒ chỉ cần 7 luật, phát hiện mâu thuẫn dạng `A` và `¬A`.

---
**Nguồn:** slide 01_Intro, Ext_Knowledge-Graphs, Ext. Labeled-Property-Graphs, Ext. App-Linked Widget, Ext. App-StatSpace (Paulheim và nhóm, IE650).
