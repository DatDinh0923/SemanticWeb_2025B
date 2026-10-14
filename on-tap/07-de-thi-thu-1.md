# ĐỀ THI THỬ SỐ 1 — IT6390E Semantic Web

**Thời gian:** 180 phút · **Hình thức:** tự luận, làm trên giấy · **Tổng:** 100 điểm
**Cách dùng:** bấm giờ thật, không mở tài liệu, viết tay. Xong rồi chấm theo `07-dap-an.md` (có barem). Đề mô phỏng theo tin đồn (bài OWL kiểu "bài 3" + phần SPARQL) và theo các dạng bài thầy đã giao (RDFS true/unknown, tableau).

---

## Câu 1 (30 điểm) — Thiết kế ontology OWL
Cho mô tả sau về hệ thống phản biện hội nghị:

> *A workshop paper is a paper. Papers are submitted by authors. Reviewers can be senior reviewers or junior reviewers, but not both. A senior reviewer reviews papers, while a junior reviewer only reviews workshop papers. A review is part of a paper; every paper has at least two reviews. Nobody may review a paper that they submitted.*

a) (6đ) Vẽ sơ đồ ontology (class, property, quan hệ subClassOf, domain/range, restriction).
b) (10đ) Viết các tiên đề bằng ký pháp Description Logic.
c) (8đ) Viết ontology bằng Turtle (đầy đủ khai báo `owl:Class`, `owl:ObjectProperty`).
d) (3đ) Viết định nghĩa lớp `JuniorReviewer` và `Paper` bằng Manchester syntax.
e) (3đ) Thêm dữ liệu: `:erin a :JuniorReviewer ; :reviews :p1 .` và `:p1 a :Paper .` Reasoner kết luận gì? Ontology có inconsistent không? Giải thích theo Open World Assumption.

## Câu 2 (20 điểm) — SPARQL
Cho dữ liệu (`files/de-thi-thu-1.ttl`), prefix `: <http://example.org/review#>`:
```turtle
@prefix :     <http://example.org/review#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:WorkshopPaper  rdfs:subClassOf :Paper .
:SeniorReviewer rdfs:subClassOf :Reviewer .
:JuniorReviewer rdfs:subClassOf :Reviewer .
:p1 a :Paper         ; :title "Graph Embeddings"       ; :submittedBy :alice , :bob .
:p2 a :WorkshopPaper ; :title "SPARQL Tricks"          ; :submittedBy :carol .
:p3 a :Paper         ; :title "OWL Reasoning at Scale" ; :submittedBy :alice .
:p4 a :WorkshopPaper ; :title "Linked Data in Vietnam" ; :submittedBy :bob .
:alice :name "Alice" .  :bob :name "Bob" .  :carol :name "Carol" .
:dave  a :SeniorReviewer ; :name "Dave"  ; :reviews :p1 , :p3 .
:erin  a :JuniorReviewer ; :name "Erin"  ; :reviews :p2 .
:frank a :SeniorReviewer ; :name "Frank" ; :reviews :p1 , :p2 .
:r1 a :Review ; :isPartOf :p1 ; :writtenBy :dave  ; :score 4 .
:r2 a :Review ; :isPartOf :p1 ; :writtenBy :frank ; :score 2 .
:r3 a :Review ; :isPartOf :p2 ; :writtenBy :erin  ; :score 5 .
:r4 a :Review ; :isPartOf :p2 ; :writtenBy :frank ; :score 3 .
:r5 a :Review ; :isPartOf :p3 ; :writtenBy :dave  ; :score 1 .
```
Viết truy vấn SPARQL và ghi kết quả:
a) (4đ) Tiêu đề mỗi bài báo và số bài phản biện; bài chưa có phản biện phải hiện số 0.
b) (4đ) Các bài báo **vi phạm** yêu cầu "ít nhất 2 phản biện".
c) (3đ) Điểm trung bình của mỗi bài báo, cao nhất trước.
d) (3đ) Tác giả nộp từ 2 bài trở lên.
e) (3đ) Phản biện viên không phải junior nhưng có phản biện bài workshop.
f) (3đ) Truy vấn `SELECT ?x WHERE { ?x a :Reviewer }` trả về gì? Vì sao? Sửa để lấy được mọi reviewer.

## Câu 3 (20 điểm) — Suy diễn bằng tableau
a) (8đ) Kiểm tra tính nhất quán bằng tableau (chuyển NNF, vẽ cây, ghi số luật):
```
Lecturer ⊑ ∀teaches.Course       Course ⊓ Person ⊑ ⊥
Lecturer(an)      teaches(an, binh)      Person(binh)
```
b) (12đ) Cho `Manager ≡ Employee ⊓ ∃manages.Team`, `Director ⊑ Employee ⊓ ∃manages.Department`, `Department ⊑ Team`. Chứng minh bằng tableau rằng `Director ⊑ Manager`.

## Câu 4 (15 điểm) — RDF/RDFS
Cho đồ thị G:
```turtle
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://example.com/terms#> .
:Lecturer rdfs:subClassOf :Staff .
:Staff rdfs:subClassOf :Person .
:teaches rdfs:domain :Lecturer ; rdfs:range :Course .
:supervises rdfs:subPropertyOf :advises .
:advises rdfs:domain :Staff ; rdfs:range :Student .
:hung :teaches :SW ; :supervises :hieu .
```
a) (4đ) Vẽ đồ thị RDF của G.
b) (11đ) Mỗi mệnh đề sau là **true** (RDFS-entailed) hay **unknown**? Giải thích bằng tên luật.
1. `:hung a :Person .`
2. `:hieu a :Student .`
3. `:supervises rdfs:range :Student .`
4. `:hung :advises [ a :Student ] .`
5. `:SW a :Person .`
6. `:Lecturer rdfs:subClassOf [ rdfs:subClassOf :Person ] .`
7. `:hieu :advisedBy :hung .`

## Câu 5 (15 điểm) — Lý thuyết
a) (5đ) Phân biệt Open World Assumption và Closed World Assumption. Nêu một hệ quả của OWA trong OWL và một trong SPARQL.
b) (5đ) Một bộ dữ liệu khai báo `:Hamburg_City owl:sameAs :Hamburg_State .` Nhận xét. Nêu cách sửa.
c) (5đ) Trình bày lược đồ 5 sao của Linked Open Data, mỗi mức cho một ví dụ định dạng.
