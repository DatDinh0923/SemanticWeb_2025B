# 00 — Chiến lược làm bài thi tự luận 2–3 tiếng

## 1. Phân bổ thời gian (đề 180 phút, ~5 câu)
| Phút | Việc |
|---|---|
| 0–10 | **Đọc hết đề**, đánh dấu câu chắc ăn, ghi nháp bảng luật RDFS + 7 luật tableau + bảng DL↔Manchester ra lề giấy nháp (để dùng suốt bài) |
| 10–60 | **Câu thiết kế OWL** (thường nhiều điểm nhất) — theo khuôn 5 phần ở `02-owl.md` §B |
| 60–90 | **SPARQL** — viết luôn trên ontology vừa thiết kế nếu đề cho |
| 90–125 | **Tableau** — NNF cẩn thận, vẽ cây rõ ràng |
| 125–150 | **RDF/RDFS** (vẽ đồ thị, true/unknown, serialization) |
| 150–170 | **Lý thuyết** — dàn ý gạch đầu dòng, có ví dụ |
| 170–180 | **Soát lại:** prefix, ngoặc Manchester, số luật, kết luận từng câu |

Nguyên tắc: câu nào kẹt quá 1,5 lần thời gian dự kiến ⇒ ghi hướng giải rồi chuyển câu; quay lại sau.

## 2. Khuôn trình bày cho từng dạng
| Dạng | Khuôn (tóm tắt) | Chi tiết |
|---|---|---|
| **D1** thiết kế OWL | bảng câu→tiên đề · sơ đồ · DL · Turtle/Manchester · giải thích + suy diễn | `02-owl.md` §B, §C |
| **D2** SPARQL | PREFIX → vẽ mẫu đồ thị → triple pattern → FILTER/OPTIONAL/GROUP → ghi kết quả mong đợi | `04-sparql.md` §C |
| **D3** tableau | DL → giả thiết phản chứng → NNF (a, b, c…) → cây ghi "3a, 5, 7" → kết luận (+OWA) | `03-owl2-tableau.md` §2 |
| **D4** RDFS true/unknown | đồ thị gốc (T-Box/A-Box) → luật dùng → bao đóng D1…Dn → trả lời có tên luật → bảng tổng kết | `01-rdf-rdfs.md` §C |
| **D5** vẽ đồ thị RDF | ellipse = URI, chữ nhật = literal, elip rỗng = blank node, nhãn = predicate; đếm số triple | `01-rdf-rdfs.md` §C |
| **D6** serialization | Turtle ↔ N-Triples ↔ RDF/XML: bung prefix, `rdf:resource` / `rdf:nodeID` / `rdf:datatype` / `xml:lang` | `01-rdf-rdfs.md` §A3 |
| **D7** schema RDFS | lớp + phân cấp, property + domain/range, tái dùng FOAF/DC, chỉ ra giới hạn RDFS | `01-rdf-rdfs.md` §C |
| **D8** giải thích reasoner | trích định nghĩa → chuỗi suy diễn → nói rõ vai trò OWA/closure/disjoint/domain | `02-owl.md` §F |
| **D9** sửa lỗi mô hình | gọi tên lỗi (rigidity / identity / unity / rampant classism / exclusivity / sameAs) → hậu quả suy diễn sai → sửa | `05-lod-modeling.md` §B |
| **D10** thiết kế LOD | nguồn → URI → vocab → link (★5) → truy cập (endpoint, dump, VoID) → competency questions | `05-lod-modeling.md` §C |

## 3. Lỗi hay mất điểm (đọc lại sáng ngày thi)
1. **"only" ⇒ `∀` (allValuesFrom)**, không phải range — range là toàn cục.
2. Dùng `some` mà quên **closure** `only` khi đề nói "chỉ gồm".
3. Hai `only` riêng lẻ bị **giao** nhau ⇒ phải gộp `only (A or B)`.
4. Định nghĩa ("X **là** Y mà/có…") phải dùng **EquivalentTo**, điều kiện cần dùng SubClassOf.
5. Quên **disjoint** giữa các lớp anh em khi đề nói "không thể vừa… vừa…".
6. **"zero or more"** ⇒ không cần restriction.
7. Cardinality trong Turtle: `"2"^^xsd:nonNegativeInteger` (chuẩn OWL 2; slide thầy viết `^^xsd:integer` — cả hai đều được chấp nhận); qualified: "ít nhất n" → `owl:minQualifiedCardinality`, "đúng n" → `owl:qualifiedCardinality`, "tối đa n" → `owl:maxQualifiedCardinality`, luôn kèm `owl:onProperty` + `owl:onClass`.
8. RDFS: trả lời **unknown** chứ không phải "false"; bộ-3 `subP rdfs:domain C` **không suy ra được** bằng luật RDFS (→ unknown), nhưng ở mức cá thể vẫn "truyền": `x subP y` ⇒ rdfs7 ⇒ rdfs2 ⇒ `x a C` (slide: *"inherited by sub properties"*); **không có inverse**.
9. Blank node trong câu hỏi = "tồn tại một cái gì đó" ⇒ chỉ ra phép thay `_:x ↦ …`.
10. Tableau: NNF của `¬∃R.C` là `∀R.¬C`; tách ≡ thành **hai** chiều; nhớ ghi **số luật + chữ axiom**; luật 3 áp cho cá thể **có liên quan**.
11. SPARQL: thiếu PREFIX; quên **lang tag** (`"Avatar"@en`); `?x a :LớpCha` trả rỗng vì không suy diễn ⇒ `a/rdfs:subClassOf*`; biến trong SELECT chưa GROUP BY; muốn đếm 0 phải OPTIONAL.
12. Lý thuyết: luôn kèm **ví dụ** (Peter fatherOf Julia, Mary; Hamburg; Margherita; CoastalCity/Germany; Interval/Duration).
13. Datalog: mỗi bước B(k+1) chỉ dùng các dữ kiện của B(k); dừng khi một bước không thêm gì (điểm cố định); lá của cây chứng minh phải là dữ kiện gốc.

## 4. Phải thuộc lòng (viết ra giấy nháp trong 10 phút đầu)
- Luật RDFS: **rdfs2** domain · **rdfs3** range · **rdfs4a/b** Resource · **rdfs5** subProp bắc cầu · **rdfs6** subProp phản xạ · **rdfs7** kế thừa property · **rdfs8** ⊑ Resource · **rdfs9** kế thừa kiểu · **rdfs10** subClass phản xạ · **rdfs11** subClass bắc cầu · **rdfs12** member · **rdfs13** Literal · (**se1** object→blank, **se2** subject→blank).
- 7 luật tableau: **1** C(a) · **2** R(a,b) · **3** axiom toàn cục → C(a) · **4** ⊓ · **5** ⊔ tách nhánh · **6** ∃ cá thể mới (block) · **7** ∀ lan truyền.
- NNF: `C ⊑ D ↦ ¬C ⊔ D`; De Morgan; `¬∃R.C = ∀R.¬C`; `¬∀R.C = ∃R.¬C`.
- Manchester: `and / or / not / some / only / value / min / max / exactly / {a,b} / inverse / Self`; frame `Class: SubClassOf: EquivalentTo: DisjointWith: DisjointUnionOf:`; `ObjectProperty: Domain: Range: Characteristics: InverseOf: SubPropertyOf: SubPropertyChain:`; `Individual: Types: Facts: SameAs: DifferentFrom:`.
- 4 nguyên tắc LOD · 5 sao (PDF / XLS / CSV / RDF / LOD) · 9 best practices.
- OntoClean: rigidity · identity · unity (+ ví dụ Passenger, Interval/Duration, Animal/OrganicMatter).
- Sowa 3 trục → 12 phạm trù; DOLCE: Endurant / Perdurant / Quality / Abstract.

## 5. Mẹo trình bày trên giấy
- Đánh số ý (a), (b)… theo đúng đề; mỗi câu bắt đầu trang mới nếu được.
- Turtle: viết prefix một lần ở đầu câu, thụt lề `;` thẳng hàng; ghi chú `#` ngắn bên cạnh tiên đề quan trọng ("# only → allValuesFrom").
- Cây tableau: vẽ từ trên xuống, nhánh tách ghi rõ T1/T2, đánh **✗** + cặp mâu thuẫn ở lá đóng, **✓ mở** ở lá mở.
- Khi đề mơ hồ: **ghi rõ giả định** ("Giả định giáo viên chỉ là giáo sư hoặc trợ giảng ⇒ covering axiom") — giám khảo chấm lập luận.
