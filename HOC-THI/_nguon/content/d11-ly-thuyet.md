## D11 Lý thuyết mở

### Câu mở: "Chức năng của reasoner (bộ suy diễn) trong cơ sở tri thức (KB) là gì?"

> **Dạng:** D11 · **Nguồn:** Notes.png ("có 1 câu hỏi dạng kiểu mở hỏi chức năng của reasoner trong KB là gì")

<details class="ans"><summary>Đáp án (bài viết sẵn, chép được ngay)</summary>

**Định nghĩa.** Một cơ sở tri thức KB = **TBox** (tri thức lược đồ: lớp, thuộc tính, tiên đề, ví dụ `Professor ⊑ Teacher`) + **ABox** (dữ kiện về cá thể, ví dụ `Professor(hung)`, `teaches(hung, SW)`). **Reasoner** là chương trình dựa trên **ngữ nghĩa hình thức** (logic mô tả – DL, ngữ nghĩa RDFS/OWL) để rút ra các tri thức **ngầm định** (implicit) từ tri thức **tường minh** (explicit) và kiểm tra tính đúng đắn của KB.

**Danh sách tác vụ theo slide của thầy (06-OWL2 tr. 24/33):** **subsumption** (lớp con — mọi chim có là động vật biết bay?), **equivalence** (hai lớp tương đương), **disjointness** (hai lớp rời nhau), **class consistency / satisfiability** (lớp thoả được — có thú đẻ trứng không?), **consistency** của KB (nhất quán), **instantiation / instance checking** (Flipper có là Dolphin?), **retrieval / class enumeration** (liệt kê mọi cá thể của lớp). **Mọi tác vụ đều quy về kiểm tra nhất quán** (slide tr. 34), ví dụ `C ⊑ D` ⇔ KB ∪ {`(C ⊓ ¬D)(i)`} không nhất quán.

Các chức năng chính (diễn giải):

1. **Kiểm tra tính nhất quán (consistency checking)** – KB có mô hình nào không, có mâu thuẫn không.
   *Ví dụ:* `Penguin ⊑ Bird`, `Bird ⊑ Flies`, `Penguin ⊑ ¬Flies`, `Penguin(pingu)` ⇒ **không nhất quán**. Với RDFS không có phủ định nên luôn nhất quán; OWL có `disjointWith`, `complementOf` nên phát hiện được mâu thuẫn.
2. **Kiểm tra tính thỏa được của lớp (concept satisfiability)** – lớp có thể có cá thể không.
   *Ví dụ (pizza):* `IceCream` dùng `hasTopping` (domain `Pizza`) ⇒ IceCream ⊑ Pizza, mà `IceCream` disjoint `Pizza` ⇒ IceCream **unsatisfiable** (≡ ⊥, hiện màu đỏ trong Protégé).
3. **Phân loại (classification / subsumption)** – tính toàn bộ cây phân cấp lớp, tìm quan hệ `C ⊑ D` ngầm; kèm theo là kiểm tra **tương đương** (`C ⊑ D` và `D ⊑ C`) và **rời nhau** (`C ⊓ D` không thoả được).
   *Ví dụ:* `Professor ⊑ Teacher`, `Teacher ⊑ Person` ⇒ `Professor ⊑ Person`; trong pizza.owl của môn, lớp định nghĩa `VegetarianPizza ≡ Pizza ⊓ ¬∃hasTopping.FishTopping ⊓ ¬∃hasTopping.MeatTopping` ⇒ reasoner xếp `Margherita` vào dưới `VegetarianPizza` **chỉ nhờ closure axiom** `Margherita ⊑ ∀hasTopping.(MozzarellaTopping ⊔ TomatoTopping)` (hai topping này rời Meat/Fish); thiếu closure thì theo OWA Margherita vẫn có thể có topping thịt ⇒ không xếp được.
4. **Nhận diện cá thể (realization / instance checking)** – tìm các lớp (cụ thể nhất) mà mỗi cá thể thuộc về; **retrieval / class enumeration** = lặp instance checking cho mọi cá thể đã biết để liệt kê thể hiện của một lớp.
   *Ví dụ:* `teaches rdfs:domain Teacher`, `hung teaches SW` ⇒ `hung` là `Teacher`; `Father ≡ Man ⊓ ∃hasChild.Person`, `Carl` là Man và có con ⇒ `Carl` là `Father`.
5. **Suy ra / vật chất hóa tri thức ngầm (entailment / materialization)** – sinh các triple mới (luật rdfs2, rdfs3, rdfs7, rdfs9, rdfs11; `inverseOf`, `TransitiveProperty`, `SymmetricProperty`, `sameAs`…).
   *Ví dụ:* `Milo offspring Molly` + `sprungBy owl:inverseOf offspring` ⇒ `Molly sprungBy Milo`; `ancestorOf` bắc cầu ⇒ thêm cạnh ông → cháu.
6. **Hỗ trợ trả lời truy vấn (query answering)** – trả lời SPARQL trên đồ thị đã suy diễn: hỏi "mọi Person" trả cả Student, Teacher dù dữ liệu chỉ ghi lớp con. Không có reasoner thì phải viết `rdfs:subClassOf*`.
7. **Giải thích (explanation / justification)** – chỉ ra tập tiên đề tối thiểu gây ra một kết luận hay một mâu thuẫn ⇒ giúp **gỡ lỗi ontology** (ontology debugging), sửa mô hình.
8. **Tích hợp dữ liệu** – nhờ `owl:sameAs`, `owl:equivalentClass`, `owl:equivalentProperty` hợp nhất dữ liệu từ nhiều nguồn (LOD).

**Cách reasoner làm việc.**
- **RDFS / OWL RL reasoner:** **forward chaining** (áp luật dạng if-then đến **điểm cố định**, luôn dừng vì không sinh tài nguyên mới) hoặc **backward chaining** (từ câu hỏi lùi về dữ kiện, như Datalog/Prolog).
- **OWL DL reasoner:** thuật toán **tableau** – quy mọi bài toán (subsumption, instance, satisfiability) về **kiểm tra nhất quán bằng phản chứng**: chuyển NNF, áp 7 luật mở rộng, tách nhánh ở ⊔, sinh cá thể ở ∃, **blocking** để dừng; mọi nhánh đóng ⇒ mâu thuẫn.
- Reasoner tuân theo **giả thiết thế giới mở (OWA)** và **không giả định tên duy nhất (no UNA)**: thiếu dữ liệu ≠ sai; FunctionalProperty với 2 giá trị ⇒ suy ra `sameAs` chứ không báo lỗi. Muốn **kiểm tra ràng buộc** dữ liệu (đóng) thì dùng **SHACL**.
- Ví dụ reasoner: **HermiT, Pellet, FaCT++, ELK** (OWL DL/EL), Jena rule reasoner, GraphDB/RDFox (RDFS, OWL RL). Độ phức tạp: OWL 2 DL rất cao (N2EXPTIME) ⇒ có các **profile** EL, QL, RL suy diễn trong thời gian đa thức.

**Kết luận.** Reasoner biến KB từ "kho dữ liệu" thành **hệ tri thức**: tự động suy ra tri thức ngầm, đảm bảo tính đúng đắn (nhất quán, thỏa được), tổ chức lại phân cấp và hỗ trợ truy vấn, tích hợp, gỡ lỗi.

</details>

### Các khả năng của triple: "liệt kê HẾT"

> **Dạng:** D1 / D11 · **Nguồn:** Notes.png ("câu rdf mà viết triple thì … gen hết các khả năng có của triple, tại câu hỏi bắt liệt kê ra hết")

**Bảng vị trí S / P / O**

| Vị trí | IRI | Blank node | Literal thường `"x"` | Literal ngôn ngữ `"x"@vi` | Literal kiểu `"10"^^xsd:int` |
|---|---|---|---|---|---|
| Subject | ✔ | ✔ | ✘ | ✘ | ✘ |
| Predicate | ✔ | ✘ | ✘ | ✘ | ✘ |
| Object | ✔ | ✔ | ✔ | ✔ | ✔ |

⇒ Có **2 × 1 × 5 = 10** kiểu triple hợp lệ (S ∈ {IRI, blank}, P = IRI, O ∈ {IRI, blank, literal thường, literal ngôn ngữ, literal có kiểu}).

**Checklist liệt kê hết triple cho một câu** (đánh ■ từng mục):

- ■ **Kiểu** của MỌI thực thể: `:x a :Lớp` (kể cả thực thể chỉ xuất hiện ở object).
- ■ **Tên / nhãn** dạng literal: `rdfs:label`, `foaf:name`, `:title` (có thể kèm `@vi` / `@en`).
- ■ **Quan hệ chính** của câu (động từ).
- ■ **Thuộc tính giá trị** (số, năm, địa chỉ, phòng…) – chọn kiểu `^^xsd:…` nếu có.
- ■ **Quan hệ ngược** nếu đề hàm ý ("là trang chủ của" ⇔ "có trang chủ").
- ■ **Cấu trúc**: thành phần địa chỉ tách nhỏ (số nhà, đường, quận, thành phố) bằng blank node.
- ■ **Reification / provenance** nếu có "ai nói / theo ai".
- ■ **Collection / container** nếu có danh sách.
- ■ **Schema đi kèm** (nếu đề hỏi RDFS): `a rdfs:Class`, `a rdf:Property`, domain, range.
- ■ Có thể ghi thêm **dạng N-Triples** để thấy rõ từng triple, và **đếm**.

### Bài mẫu "liệt kê hết": Part 1 Ex1 (SOICT)

> **Dạng:** D1 · **Nguồn:** Exercises-en Part 1 Ex1 (ảnh bài tập 2) – mỗi câu ≥ 3 triple

Đề: (1) SOICT is located at No. 1, Dai Co Viet, Hai Ba Trung, Hanoi. (2) Website https://soict.hust.edu.vn/ is the homepage of SOICT. (3) Resource URI1 is a course on Semantic Web, taught by Lecturer Hung in room B1-404. Viết dưới dạng ngôn ngữ tự nhiên (mỗi triple một câu) rồi viết RDF.

<details class="ans"><summary>Đáp án</summary>

**Câu tự nhiên (mỗi dòng 1 triple):**

1. SOICT là một tổ chức (School). SOICT có tên "SOICT". SOICT nằm tại một địa chỉ (blank node). Địa chỉ đó có số nhà "No. 1". Địa chỉ đó thuộc đường "Dai Co Viet". Địa chỉ đó thuộc quận "Hai Ba Trung". Địa chỉ đó thuộc thành phố Hanoi. Hanoi là một City. Hanoi có nhãn "Hà Nội"@vi.
2. https://soict.hust.edu.vn/ là một Website (foaf:Document). SOICT có trang chủ https://soict.hust.edu.vn/. https://soict.hust.edu.vn/ là trang chủ của SOICT (quan hệ ngược). Trang có tiêu đề "SOICT – HUST".
3. URI1 là một Course. URI1 có chủ đề "Semantic Web". URI1 được dạy bởi Hung. Hung là một Lecturer. Hung có tên "Hung". URI1 được dạy ở phòng B1-404. B1-404 là một Room. B1-404 có nhãn "B1-404". Hung dạy URI1 (quan hệ ngược).

```turtle graph
@prefix : <http://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
:SOICT a :School ; foaf:name "SOICT" ;
  :locatedAt [ a :Address ; :number "No. 1" ; :street "Dai Co Viet" ; :district "Hai Ba Trung" ; :city :Hanoi ] ;
  foaf:homepage <https://soict.hust.edu.vn/> .
:Hanoi a :City ; rdfs:label "Hà Nội"@vi .
<https://soict.hust.edu.vn/> a foaf:Document ; :homepageOf :SOICT ; dc:title "SOICT – HUST" .
:URI1 a :Course ; :subject "Semantic Web"@en ; :taughtBy :Hung ; :room :B1-404 .
:Hung a :Lecturer ; foaf:name "Hung" ; :teaches :URI1 .
:B1-404 a :Room ; rdfs:label "B1-404" .
```

Đếm: câu 1 có 10 triple, câu 2 có 3–4 triple, câu 3 có 9 triple ⇒ mọi câu đều ≥ 3 triple. Khi đi thi: viết **đủ** kiểu, tên, quan hệ chính, quan hệ ngược.

</details>

### Bài mẫu "liệt kê hết": Part 1 Ex3 (URI1…URI6)

> **Dạng:** D3 · **Nguồn:** Exercises-en Part 1 Ex3 (ảnh bài tập 6)

Đề: URI1 và URI2 là lớp; URI3 là thuộc tính; URI4 là cá thể của URI1; URI5, URI6 là cá thể của URI2; URI3 có domain URI1, range URI2.

<details class="ans"><summary>Đáp án</summary>

```turtle graph
@prefix : <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:URI1 a rdfs:Class .
:URI2 a rdfs:Class .
:URI3 a rdf:Property ; rdfs:domain :URI1 ; rdfs:range :URI2 .
:URI4 a :URI1 .
:URI5 a :URI2 .
:URI6 a :URI2 .
```

8 triple cơ bản. "Liệt kê hết" thêm các triple **suy ra được** (nếu đề hỏi): `:URI1 rdfs:subClassOf rdfs:Resource` (rdfs8), `:URI1 rdfs:subClassOf :URI1` (rdfs10), `:URI3 rdfs:subPropertyOf :URI3` (rdfs6), `:URI4 a rdfs:Resource` (rdfs4a)… Nếu có thêm `:URI4 :URI3 :URI5` thì minh họa domain/range đúng chiều.

</details>

### Q: Vẽ và giải thích Semantic Web stack

<details class="ans"><summary>Đáp án</summary>

Từ dưới lên: **URI/IRI + Unicode** → **XML** (+ namespace) → **RDF** (mô hình dữ liệu) → **RDFS** (từ vựng, schema) → **OWL** (ontology), **SPARQL** (truy vấn), **RIF/SWRL** (luật) → **Logic** → **Proof** → **Trust**; **Crypto** chạy dọc; **User interface & applications** ở trên cùng. Mỗi tầng dựa trên tầng dưới; cú pháp (XML, Turtle) đem lại *interoperability cú pháp*, RDFS/OWL đem lại *interoperability ngữ nghĩa*.

</details>

### Q: Bốn nguyên tắc Linked Data và lược đồ 5 sao

<details class="ans"><summary>Đáp án</summary>

**4 nguyên tắc (Berners-Lee 2006):** (1) dùng **URI** làm tên cho sự vật; (2) dùng **HTTP URI** để tra cứu được; (3) khi tra URI, trả về **thông tin hữu ích theo chuẩn** (RDF, SPARQL); (4) **liên kết** tới URI khác để khám phá thêm.

**5 sao:** ★ có trên Web, giấy phép mở (PDF); ★★ có cấu trúc, máy đọc được (Excel); ★★★ định dạng không độc quyền (CSV); ★★★★ dùng chuẩn W3C RDF/SPARQL, URI định danh; ★★★★★ liên kết tới dữ liệu người khác (LOD, `owl:sameAs`).

</details>

### Q: OWA vs CWA – ảnh hưởng tới RDFS, OWL, SPARQL

<details class="ans"><summary>Đáp án</summary>

- **OWA (thế giới mở):** không biết ≠ sai. `:Peter :fatherOf :Julia , :Mary` ⇒ Peter có **ít nhất 1** con (không có UNA nên Julia có thể là Mary), có thể nhiều hơn (OWA) — không biết chính xác bao nhiêu. Muốn kết luận ≥ 2 con phải thêm `:Julia owl:differentFrom :Mary`.
- **CWA (thế giới đóng – CSDL, Prolog):** không có trong dữ liệu ⇒ sai.
- RDFS/OWL dùng OWA: mệnh đề không suy ra được là **unknown**; cần **closure axiom** (pizza); reasoner không báo "thiếu dữ liệu".
- SPARQL trên dữ liệu có sẵn hoạt động kiểu đóng (`FILTER NOT EXISTS`, `COUNT`), nhưng `ASK` = false chỉ nghĩa là "không tìm thấy". Kiểm tra ràng buộc đóng ⇒ **SHACL**.
- Web dùng OWA vì Web không bao giờ đầy đủ (AAA: Anybody can say Anything about Anything).

</details>

### Q: Unique Name Assumption (UNA)

<details class="ans"><summary>Đáp án</summary>

OWL **không** giả định tên duy nhất: hai URI khác nhau có thể chỉ cùng một thực thể (`:Munich`, `:München`). Hệ quả: FunctionalProperty có 2 giá trị ⇒ suy ra `owl:sameAs` thay vì mâu thuẫn; cardinality ≥ 2 chỉ thỏa nếu các cá thể được khai báo `owl:differentFrom` / `owl:AllDifferent`.

</details>

### Q: So sánh RDFS và OWL

<details class="ans"><summary>Đáp án</summary>

| | RDFS | OWL |
|---|---|---|
| Biểu đạt | lớp, thuộc tính, phân cấp, domain/range | + restriction (∃, ∀, hasValue), cardinality, đặc tính property (transitive, symmetric, functional, inverse), ⊓ ⊔ ¬, disjoint, sameAs, oneOf |
| Phủ định / mâu thuẫn | không có ⇒ luôn nhất quán | có ⇒ phát hiện inconsistency |
| Suy diễn | forward chaining, luật rdfs1–13, luôn dừng, đa thức | tableau; OWL 2 DL rất đắt; profile EL/QL/RL đa thức; OWL Full không quyết định được |
| Ví dụ RDFS không làm được | "Baby và Adult rời nhau", "Molly là mèo vì mẹ là mèo", "có đúng 2 con" | làm được bằng `disjointWith`, restriction, cardinality |

</details>

### Q: Các profile OWL 2 và OWL Lite / DL / Full

<details class="ans"><summary>Đáp án</summary>

- **OWL 1:** Lite (cardinality 0/1, không union/complement), DL (đầy đủ nhưng tách lớp/cá thể/thuộc tính ⇒ quyết định được, SHOIN(D)), Full (tương thích hoàn toàn RDFS, không quyết định được).
- **OWL 2 DL** (SROIQ(D)) + 3 profile: **EL** (ontology lớn, phân loại đa thức – y sinh SNOMED), **QL** (trả lời truy vấn qua viết lại thành SQL – OBDA), **RL** (luật, forward chaining – triple store).

</details>

### Q: Knowledge Graph là gì?

<details class="ans"><summary>Đáp án</summary>

Theo Paulheim 2017, một KG: (1) mô tả **thực thể và quan hệ** dưới dạng **đồ thị**; (2) định nghĩa **lớp và quan hệ** trong **schema/ontology**; (3) cho phép **liên kết tùy ý** các thực thể; (4) bao phủ **nhiều miền**. Ví dụ: DBpedia, Wikidata, YAGO, Google KG ("things, not strings"). Về hình thức: đồ thị có hướng, có nhãn, không đồng nhất.

</details>

### Q: SHACL khác OWL thế nào?

<details class="ans"><summary>Đáp án</summary>

| | OWL | SHACL |
|---|---|---|
| Mục đích | **suy diễn** tri thức mới | **kiểm tra (validate)** dữ liệu theo ràng buộc |
| Giả thiết | OWA, không UNA | **CWA**, có UNA |
| Thiếu giá trị bắt buộc | không lỗi (có thể tồn tại mà chưa biết) | **vi phạm** (`sh:minCount 1`) |
| Kết quả | đồ thị suy diễn, phân loại | **validation report** (nút vi phạm, lý do) |

Ví dụ: `:JetFighter` phải có `:speed`; Su27 không có speed ⇒ OWL không báo gì, SHACL báo vi phạm.

</details>

### Q: Reification, named graph, RDF-star

<details class="ans"><summary>Đáp án</summary>

| | Reification | Named graph | RDF-star |
|---|---|---|---|
| Cú pháp | `[ a rdf:Statement ; rdf:subject … ; rdf:predicate … ; rdf:object … ]` | `GRAPH :g { … }` (TriG, quad) | `<< :s :p :o >> :source :x` |
| Chi phí | 4 triple / phát biểu | 1 IRI cho nhóm triple | gọn |
| Khẳng định triple gốc? | **không** (ngữ nghĩa W3C) | có | không (quoted) |

Slide LPG (tr. 22) lưu ý: trong thực hành, khi đã phát biểu *về* một phát biểu S thì S thường được coi là đúng ("S is automatically assumed to be true") — khi thi vẫn lấy ngữ nghĩa W3C làm câu trả lời chính.

Dùng khi "A nghĩ / nói / theo nguồn X…" (provenance). Ví dụ: "An nghĩ C++ thú vị" – không khẳng định C++ thú vị.

</details>

### Q: owl:sameAs dùng đúng và lạm dụng

<details class="ans"><summary>Đáp án</summary>

`owl:sameAs` = hai URI chỉ **cùng một thực thể** ⇒ mọi phát biểu chia sẻ cho nhau. Dùng đúng: cùng một người trong DBpedia và dữ liệu của bạn. Lạm dụng: người ↔ trang chủ của họ (dùng `foaf:homepage`), thành phố Hamburg ↔ bang Hamburg, một cửa hàng Starbucks (quán ở O7) ↔ công ty Starbucks. Thay thế: `rdfs:seeAlso`, `skos:closeMatch`, quan hệ riêng.

</details>

### Q: Câu "vì sao" ngắn

<details class="ans"><summary>Đáp án</summary>

1. Vì sao literal không được làm subject? ⇒ Theo định nghĩa RDF; hệ quả: DatatypeProperty không thể Symmetric, Transitive, Inverse.
2. Vì sao suy diễn RDFS luôn dừng? ⇒ Không tạo tài nguyên mới; số triple có thể có là hữu hạn ⇒ đạt điểm cố định.
3. Vì sao OWL Full không quyết định được? ⇒ Không tách lớp / thuộc tính / cá thể, quá biểu đạt.
4. Vì sao cần blocking trong tableau? ⇒ Luật ∃ sinh cá thể mới vô hạn (`Woman ⊑ ∃hasMother.Woman`).
5. Vì sao dùng `EquivalentTo` thay vì `SubClassOf` cho lớp định nghĩa? ⇒ Để reasoner tự phân loại cá thể/lớp vào đó.
6. Vì sao tableau dùng NNF? ⇒ ¬ chỉ đứng trước lớp nguyên tử ⇒ chỉ cần 7 luật, mâu thuẫn có dạng `A(a)` và `¬A(a)`.
7. Vì sao không có datatype mặc định? ⇒ `"München"@de` ≠ `"München"@en` ≠ `"München"^^xsd:string`.

</details>
