# ĐỀ THI THỬ SỐ 2 — IT6390E Semantic Web

**Thời gian:** 180 phút · **Hình thức:** tự luận, làm trên giấy · **Tổng:** 100 điểm
**Cách dùng:** làm sau khi đã chữa đề 1. Đáp án + barem ở `07-dap-an.md`.

---

## Câu 1 (30 điểm) — Thiết kế ontology OWL & giải thích reasoner
> *A dish is made of ingredients. Meat and seafood are animal products; vegetables and grains are plant products. Every ingredient is either an animal product or a plant product, never both. A vegetarian dish is a dish that contains only plant products. A chef cooks dishes; a head chef is a chef who manages at least two chefs. Every dish has exactly one price.*

a) (5đ) Vẽ sơ đồ ontology.
b) (10đ) Viết DL **và** Manchester syntax cho toàn bộ mô tả.
c) (7đ) Viết Turtle cho các lớp `Ingredient`, `VegetarianDish`, `HeadChef` và thuộc tính `price`.
d) (8đ) Với dữ liệu: `RauCuXao` là Dish, `hasIngredient` Carrot (Vegetable) và Onion (Vegetable); `Pho` là Dish, `hasIngredient` Noodle (Grain) và Onion. Reasoner có xếp `RauCuXao` và `Pho` vào `VegetarianDish` không? Giải thích. Cần thêm gì để reasoner xếp được? Và nếu `Pho` thực ra có thêm `hasIngredient Beef` (Meat) thì sao?

## Câu 2 (20 điểm) — Biểu diễn RDF
> *Bài báo "Linked Data in Vietnam" do An và một đồng tác giả không rõ tên viết, đăng năm 2024 tại hội nghị ISWC. Bình cho rằng bài báo này đã được trích dẫn 50 lần.*

a) (6đ) Vẽ đồ thị RDF (dùng Dublin Core `dcterms:` và FOAF khi phù hợp).
b) (7đ) Viết Turtle.
c) (7đ) Viết RDF/XML. Giải thích cách bạn biểu diễn "đồng tác giả không rõ tên" và "Bình cho rằng…".

## Câu 3 (20 điểm) — SPARQL
Dữ liệu (`files/de-thi-thu-2.ttl`), prefix `: <http://example.org/food#>`:
```turtle
@prefix :     <http://example.org/food#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:Meat rdfs:subClassOf :AnimalProduct .     :Seafood rdfs:subClassOf :AnimalProduct .
:Vegetable rdfs:subClassOf :PlantProduct . :Grain rdfs:subClassOf :PlantProduct .
:beef a :Meat . :pork a :Meat . :shrimp a :Seafood .
:noodle a :Grain . :onion a :Vegetable . :carrot a :Vegetable . :herb a :Vegetable .
:pho     a :Dish ; :name "Phở bò"@vi     ; :price 50000 ; :hasIngredient :beef , :noodle , :onion .
:buncha  a :Dish ; :name "Bún chả"@vi    ; :price 45000 ; :hasIngredient :pork , :noodle .
:goicuon a :Dish ; :name "Gỏi cuốn"@vi   ; :price 30000 ; :hasIngredient :shrimp , :noodle , :herb .
:raucu   a :Dish ; :name "Rau củ xào"@vi ; :price 35000 ; :hasIngredient :carrot , :onion .
:lan  a :HeadChef ; :name "Lan"  ; :cooks :pho , :buncha ; :manages :minh .
:minh a :Chef     ; :name "Minh" ; :cooks :goicuon .
```
a) (3đ) Món có giá dưới 40.000, kèm tên và giá, rẻ nhất trước.
b) (4đ) Món không chứa nguyên liệu động vật nào. (Chú ý: dữ liệu ghi `:beef a :Meat`, không ghi `a :AnimalProduct`.)
c) (4đ) Nguyên liệu dùng trong từ 2 món trở lên, kèm số món.
d) (3đ) Mọi món kèm tên đầu bếp nấu món đó (món chưa có người nấu vẫn phải hiện).
e) (3đ) Dùng CONSTRUCT để sinh triple `?d a :VegetarianDish` cho các món ở câu b.
f) (3đ) Đoán kết quả: `SELECT (AVG(?p) AS ?avg) (COUNT(?d) AS ?n) WHERE { ?d :price ?p }`.

## Câu 4 (15 điểm) — Tableau
a) (9đ) `Expert ≡ Person ⊓ ∃writes.Book`, `Person(an)`, `writes(an, kg)`, `Book(kg)`. Dùng tableau để kiểm tra `Expert(an)`.
b) (6đ) Ontology `{Person ⊑ ∃knows.Person, Person(an)}` có consistent không? Giải thích vì sao cần **rule blocking**.

## Câu 5 (15 điểm) — Knowledge modeling
a) (5đ) Một ontology bán hàng khai báo `Person ⊑ Customer` và `Company ⊑ Customer`. Dùng OntoClean chỉ ra lỗi và sửa.
b) (5đ) `SpicyDish ≡ ∃hasIngredient.Chili`. Dữ liệu có `:SrirachaBottle :hasIngredient :RedChili . :RedChili a :Chili .` Reasoner suy ra gì? Đây là anti-pattern nào? Sửa.
c) (5đ) Xếp vào 12 phạm trù của Sowa: (i) Hồ Gươm (ii) buổi thi cuối kỳ ngày 17/10 (iii) quy chế thi của trường (iv) mục tiêu đạt điểm A của bạn.
