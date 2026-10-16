# Luyện đề — 3 đề luyện tập (chia 8 câu, 10 điểm)

> **Lưu ý format:** 3 đề cũ thật mỗi đề có **5 câu** (nhiều ý nhỏ, không in điểm, ≈ 2 điểm/câu; nghe nói câu truy vấn SPARQL 2.5 điểm). Các đề luyện dưới đây chia nhỏ thành 8 câu để tiện luyện và tự chấm.
> Cách dùng: bấm giờ 150 phút, làm ra giấy (hoặc ô làm bài). Mỗi câu: đọc đề → tự làm → mở **Gợi ý / Khuôn** nếu bí → mở **Đáp án + barem**, tick các ý mình làm được để tự chấm.
> Mỗi đề có đúng **1 câu SPARQL 2.5đ** (Câu 6 — theo tin "nghe nói", chưa kiểm chứng). Dữ liệu của câu SPARQL có sẵn trong Playground: `de1.ttl`, `de2.ttl`, `de3.ttl`.
> Mọi kết quả SPARQL dưới đây đã **chạy thật bằng rdflib** trên đúng dữ liệu của đề.

---

## Đề 1 — Ghép và biến tấu từ 3 đề cũ (10 điểm, 150 phút)

### Câu 1 (1.25 điểm) · [D1]
Tạo dữ liệu RDF theo cú pháp Turtle biểu diễn các thông tin sau, sau đó vẽ đồ thị RDF tương ứng:

> Học phần *Semantic Web* do thầy Hùng giảng dạy, gồm các chương theo thứ tự: RDF, RDFS, OWL, SPARQL. Sinh viên Trần Thị B đạt điểm 9 học phần này. Thầy Hùng cho rằng Trần Thị B là một sinh viên chăm chỉ.

*Tự tạo IRI cho các thành phần. Viết không quá 25 bộ-3.*

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- "gồm các chương **theo thứ tự**" → **collection** `( … )`, tự bung thành `rdf:first` / `rdf:rest` / `rdf:nil`.
- "đạt điểm 9 **học phần này**": điểm gắn với cặp (sinh viên, học phần), là quan hệ n-ngôi → **blank node** `[ :course … ; :score 9 ]`.
- "Thầy Hùng **cho rằng** …": đây là phát biểu về một phát biểu → **reification** `rdf:Statement` với `rdf:subject` / `rdf:predicate` / `rdf:object`.
- Viết `rdf:type` cho mọi thực thể có tên, rồi thêm nhãn/tên dạng literal.
- Quy ước vẽ: IRI là elip, literal là chữ nhật, blank node là elip rỗng.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```turtle graph
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:sw a :Course ; rdfs:label "Semantic Web" ; :taughtBy :hung ; :chapters ( :RDF :RDFS :OWL :SPARQL ) .
:hung a :Teacher ; :name "Hùng" .
:ttb a :Student ; :name "Trần Thị B" ; :result [ :course :sw ; :score 9 ] .
:hung :believes [ a rdf:Statement ; rdf:subject :ttb ; rdf:predicate rdf:type ; rdf:object :DiligentStudent ] .
```

**Đếm bộ-3 (24):**
- `:sw` có 4 bộ-3, cộng 8 bộ-3 của danh sách 4 phần tử (4 `rdf:first` + 4 `rdf:rest`).
- `:hung` có 2.
- `:ttb` có 3, cộng 2 của nút điểm.
- `:believes` có 1, cộng 4 của nút `rdf:Statement`.

**Cách vẽ:**
- Từ nút `:sw`, cạnh `:chapters` đi tới một chuỗi 4 blank node nối nhau bằng `rdf:rest`. Mỗi blank node có cạnh `rdf:first` tới một chương. Blank node cuối có `rdf:rest` tới `rdf:nil`.
- Nút điểm là blank node có 2 cạnh: `:course` tới `:sw` và `:score` tới hộp literal `9`.

- [ ] Prefix đúng, IRI tự đặt nhất quán (0.25đ)
- [ ] Collection có thứ tự cho các chương (0.25đ)
- [ ] Blank node n-ngôi cho điểm 9 + học phần (0.25đ)
- [ ] Reification: rdf:subject, rdf:predicate, rdf:object + rdf:type rdf:Statement (4 bộ-3) (0.25đ)
- [ ] Đồ thị vẽ đúng quy ước elip / chữ nhật / blank (0.25đ)

</details>

### Câu 2 (0.75 điểm) · [D4]
Cho CSTT:

```turtle
@prefix : <http://exam.hust.edu.vn/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:a :teaches :b .
:d :assists :c .
:c a :LabCourse .
:teaches rdfs:domain :Teacher ; rdfs:range :Course .
:assists rdfs:subPropertyOf :teaches .
:LabCourse rdfs:subClassOf :Course .
:Teacher rdfs:subClassOf :Person .
```
a) Viết ít nhất 5 bộ-3 suy ra được trong phạm vi ngữ nghĩa RDFS và nêu cơ sở của từng suy diễn.
b) Các mệnh đề sau đúng hay không xác định: (1) `:assists rdfs:domain :Teacher` (2) `:b a :LabCourse`.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Viết theo format thầy: `bộ-3 mới  <=  bộ-3 cơ sở 1 . bộ-3 cơ sở 2 .  (tên luật)`.
- Thứ tự áp luật nên làm: rdfs7 (subProperty) → rdfs2/rdfs3 (domain/range) → rdfs9 (subClass), rồi lặp lại trên bộ-3 vừa sinh.
- Bộ-3 `subP rdfs:domain C` **không suy ra được** bằng luật RDFS (→ không xác định), nhưng ở mức cá thể domain/range vẫn "truyền": `x subP y` ⇒ rdfs7 ⇒ rdfs2 ⇒ `x a C` (slide: "inherited by sub properties").

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```text
:a a :Teacher .      <=  :a :teaches :b .  :teaches rdfs:domain :Teacher .       (rdfs2)
:a a :Person .       <=  :a a :Teacher .   :Teacher rdfs:subClassOf :Person .    (rdfs9)
:b a :Course .       <=  :a :teaches :b .  :teaches rdfs:range :Course .         (rdfs3)
:d :teaches :c .     <=  :d :assists :c .  :assists rdfs:subPropertyOf :teaches . (rdfs7)
:d a :Teacher .      <=  :d :teaches :c .  :teaches rdfs:domain :Teacher .       (rdfs2)
:d a :Person .       <=  :d a :Teacher .   :Teacher rdfs:subClassOf :Person .    (rdfs9)
:c a :Course .       <=  :c a :LabCourse . :LabCourse rdfs:subClassOf :Course .  (rdfs9)  [hoặc rdfs3 từ :d :teaches :c]
```
b)
- (1) **Không xác định.** RDFS không có luật cho domain kế thừa từ `:teaches` xuống `:assists`. Lưu ý mọi chủ thể của `:assists` vẫn là Teacher (qua rdfs7 rồi rdfs2), nhưng bộ-3 schema thì không được sinh ra.
- (2) **Không xác định.** Chỉ biết `:b a :Course`, mà Course không phải lớp con của LabCourse. Theo OWA, không suy ra được thì không có nghĩa là sai.

- [ ] ≥5 bộ-3 đúng (0.25đ)
- [ ] Mỗi bộ-3 có cơ sở + tên luật (0.25đ)
- [ ] b) đúng cả 2, giải thích OWA / bộ-3 domain của subproperty không được sinh (0.25đ)

</details>

### Câu 3 (1.25 điểm) · [D5]
Định nghĩa các lớp và thuộc tính bằng RDFS và OWL (Turtle), đồng thời viết biểu thức DL tương ứng:
- Các lớp: Thiết bị điện tử, Điện thoại, Máy tính bảng, Laptop, Thiết bị lai, Thiết bị Windows.
- Các thuộc tính: chạy hệ điều hành (runsOS), kết nối (connectsTo), imei.

a) Điện thoại, máy tính bảng, laptop là các loại thiết bị điện tử.
b) runsOS có miền là thiết bị điện tử, giá trị chỉ có thể là Android, iOS hoặc Windows.
c) Kết nối là quan hệ đối xứng giữa các thiết bị.
d) Thiết bị lai là thiết bị thuộc ít nhất 2 trong 3 lớp Điện thoại / Máy tính bảng / Laptop.
e) Mỗi điện thoại có đúng 1 số IMEI.
f) Thiết bị Windows là thiết bị điện tử chạy hệ điều hành Windows.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

| Đề nói | Cấu trúc OWL |
|---|---|
| "là các loại …" | `rdfs:subClassOf` |
| "chỉ có thể là A, B, C" | `owl:oneOf ( … )` làm range |
| "đối xứng" | `owl:SymmetricProperty` |
| "ít nhất 2 trong 3" | `unionOf` của các `intersectionOf` từng cặp (giống "phương tiện lưỡng cư", đề 2023) |
| "đúng 1" | `owl:cardinality 1` (hoặc FunctionalProperty + minCardinality 1) |
| "chạy Windows" (một cá thể cụ thể) | `owl:hasValue :Windows` |

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:Phone  rdfs:subClassOf :Device .
:Tablet rdfs:subClassOf :Device .
:Laptop rdfs:subClassOf :Device .
:runsOS a owl:ObjectProperty ; rdfs:domain :Device ;
    rdfs:range [ a owl:Class ; owl:oneOf ( :Android :iOS :Windows ) ] .
:connectsTo a owl:ObjectProperty , owl:SymmetricProperty ;
    rdfs:domain :Device ; rdfs:range :Device .
:imei a owl:DatatypeProperty ; rdfs:range xsd:string .
:Hybrid owl:equivalentClass [ owl:unionOf (
    [ owl:intersectionOf ( :Phone :Tablet ) ]
    [ owl:intersectionOf ( :Phone :Laptop ) ]
    [ owl:intersectionOf ( :Tablet :Laptop ) ] ) ] .
:Phone rdfs:subClassOf [ a owl:Restriction ; owl:onProperty :imei ;
    owl:cardinality "1"^^xsd:nonNegativeInteger ] .
:WindowsDevice owl:equivalentClass [ owl:intersectionOf ( :Device
    [ a owl:Restriction ; owl:onProperty :runsOS ; owl:hasValue :Windows ] ) ] .
```
```text
Phone ⊑ Device      Tablet ⊑ Device      Laptop ⊑ Device
∃runsOS.⊤ ⊑ Device               ⊤ ⊑ ∀runsOS.{Android, iOS, Windows}
connectsTo ≡ connectsTo⁻         ∃connectsTo.⊤ ⊑ Device     ⊤ ⊑ ∀connectsTo.Device
Hybrid ≡ (Phone ⊓ Tablet) ⊔ (Phone ⊓ Laptop) ⊔ (Tablet ⊓ Laptop)
Phone ⊑ =1 imei
WindowsDevice ≡ Device ⊓ ∃runsOS.{Windows}
```
Giải thích ý d):
- Dùng `≡` (equivalentClass) để reasoner **tự phân loại**: một máy vừa là Phone vừa là Tablet sẽ được suy ra là Hybrid.
- Không bắt buộc "đúng 2 lớp", vì máy thuộc cả 3 lớp vẫn là Hybrid.

- [ ] a) 3 subClassOf (0.25đ)
- [ ] b) domain + range oneOf (0.25đ)
- [ ] c) SymmetricProperty (0.25đ)
- [ ] d) union của các intersection, dùng ≡ (0.25đ)
- [ ] e) f) cardinality 1 + hasValue, kèm DL đúng (0.25đ)

</details>

### Câu 4 (1 điểm) · [D6 · D11]
a) Nêu các chức năng chính của **reasoner** (bộ suy diễn) trong một cơ sở tri thức (KB).
b) Cho CSTT:

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:C rdfs:subClassOf :D ;
   owl:equivalentClass [ a owl:Restriction ; owl:onProperty :p ; owl:allValuesFrom :F ] .
:x a :C ; :p :e .
:y :p :f .   :f a :F .
```
- (i) Reasoner suy ra được những bộ-3 nào về `:x` và `:e`? Giải thích.
- (ii) Có suy ra được `:y a :C` không? Nếu không, cần bổ sung gì để suy ra được?
- (iii) Viết ngữ nghĩa của `:C` bằng DL.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- a) Nêu đủ 8 chức năng (giống bài viết sẵn ở trang D11): consistency, satisfiability, classification, realization, entailment/materialization, hỗ trợ trả lời truy vấn, giải thích (justification), tích hợp dữ liệu. Mỗi chức năng kèm 1 ví dụ. Nên nhắc danh sách tác vụ của slide thầy: subsumption, equivalence, disjointness, class satisfiability, consistency, instantiation, retrieval — tất cả quy về kiểm tra nhất quán.
- b) `C ≡ ∀p.F`:
  - Chiều C ⊑ ∀p.F: cá thể thuộc C thì mọi giá trị p của nó thuộc F.
  - Chiều ngược lại: phải biết **tất cả** giá trị p của một cá thể. Vì OWA nên không biết hết được, trừ khi có ràng buộc đóng (cardinality).

</details>

<details class="ans"><summary>Đáp án + barem</summary>

**a) Chức năng của reasoner trong KB:**
1. **Kiểm tra tính nhất quán (consistency):** KB có mâu thuẫn không. Ví dụ Pingu vừa là Animal vừa là Plant, trong khi Animal rời Plant.
2. **Kiểm tra tính thỏa được của lớp (satisfiability):** lớp có thể có cá thể không. Ví dụ `IceCream ⊑ ∃hasTopping.⊤` mà domain của hasTopping là Pizza, Pizza lại rời IceCream, nên IceCream không thỏa được.
3. **Phân loại (classification):** tính cây phân cấp subsumption đầy đủ giữa các lớp. Ví dụ suy ra Father ⊑ Person.
4. **Realization / class instantiation:** tìm mọi lớp mà một cá thể thuộc về. Ví dụ Carl là Father.
5. **Suy ra tri thức ẩn (entailment, materialization):** sinh các bộ-3 ngầm định như domain/range, subPropertyOf, inverse, transitive.
6. **Hỗ trợ trả lời truy vấn:** truy vấn trên dữ liệu đã suy diễn (hỏi "mọi Person" trả cả Student, Teacher).
7. **Giải thích (justification):** chỉ ra tập tiên đề gây ra một kết luận hoặc một mâu thuẫn ⇒ gỡ lỗi ontology.
8. **Tích hợp dữ liệu:** nhờ `owl:sameAs`, `owl:equivalentClass`, `owl:equivalentProperty` hợp nhất dữ liệu nhiều nguồn.

Kỹ thuật: RDFS và OWL RL dùng forward chaining; OWL DL dùng tableau, trong đó mọi bài toán được quy về kiểm tra consistency.

**b)**
- (i) Hai bộ-3 suy ra được:
  - `:x a :D`, vì `:x a :C` và `:C rdfs:subClassOf :D` (subClassOf).
  - `:e a :F`, vì `:x ∈ C ⊑ ∀p.F` và `p(x, e)` nên e ∈ F (∀-rule).
- (ii) **Không suy ra được** `:y a :C`. Lý do: theo OWA, `:y` có thể còn giá trị p khác chưa biết, và giá trị đó có thể không thuộc F.
  - Cách bổ sung: đóng số giá trị, ví dụ `:y a [ a owl:Restriction ; owl:onProperty :p ; owl:maxCardinality 1 ]`.
  - Khi đó mọi giá trị p của y đều bằng f, mà f ∈ F, nên y ∈ ∀p.F ≡ C.
- (iii) `C ⊑ D`, `C ≡ ∀p.F`.

- [ ] a) ≥4 chức năng đúng, có ví dụ (0.5đ)
- [ ] b-i) :x a :D và :e a :F (0.25đ)
- [ ] b-ii, iii) OWA + cách đóng + DL (0.25đ)

</details>

### Câu 5 (1 điểm) · [D7]
Cho chương trình Datalog (X, Y, Z là biến):

```text
Cha(An, Binh)      Cha(Binh, Cuong)      Me(Hoa, An)
R1: ChaMe(X, Y) ← Cha(X, Y)
R2: ChaMe(X, Y) ← Me(X, Y)
R3: ToTien(X, Y) ← ChaMe(X, Y)
R4: ToTien(X, Z) ← ChaMe(X, Y) ∧ ToTien(Y, Z)
```
a) Vẽ cây chứng minh cho `ToTien(Hoa, Cuong)`.
b) Tìm điểm cố định, viết chi tiết các bước mở rộng tập dữ kiện.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Cây chứng minh: gốc là kết luận. Mỗi nút được nối xuống các tiền đề của luật sinh ra nó. Lá là dữ kiện gốc.
- Điểm cố định (naive): B0 là dữ kiện gốc. Ở mỗi bước, áp **mọi luật** lên toàn bộ tập hiện có và chỉ ghi phần **mới**. Dừng khi một bước không sinh thêm gì.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

a)
```text
ToTien(Hoa, Cuong)                                   [R4]
├── ChaMe(Hoa, An)                                   [R2]
│   └── Me(Hoa, An)
└── ToTien(An, Cuong)                                [R4]
    ├── ChaMe(An, Binh)                              [R1]
    │   └── Cha(An, Binh)
    └── ToTien(Binh, Cuong)                          [R3]
        └── ChaMe(Binh, Cuong)                       [R1]
            └── Cha(Binh, Cuong)
```
b) (đã chạy kiểm bằng máy)
```text
B0: {Cha(An,Binh), Cha(Binh,Cuong), Me(Hoa,An)}
B1: + {ChaMe(An,Binh), ChaMe(Binh,Cuong), ChaMe(Hoa,An)}                 (R1, R2)
B2: + {ToTien(An,Binh), ToTien(Binh,Cuong), ToTien(Hoa,An)}              (R3)
B3: + {ToTien(An,Cuong), ToTien(Hoa,Binh)}                               (R4)
B4: + {ToTien(Hoa,Cuong)}                                                (R4)
B5: không sinh thêm dữ kiện mới ⇒ điểm cố định đạt ở Bước 4 (12 dữ kiện).
```

- [ ] Cây đúng, ghi luật ở mỗi nút (0.5đ)
- [ ] Các bước B1–B4 đúng + kết luận điểm cố định (0.5đ)

</details>

### Câu 6 (2.5 điểm) · [D8] — câu SPARQL
Cho CSDL RDF (`de1.ttl`):

```turtle
@prefix :     <http://semweb.edu.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:CPP    a :PL ; rdfs:label "C++" ; :creator :bjarne_stroustrup ; :year 1985 ; :influencedBy :C ;
        :hasFeature :type , :function , :pointer , :class , :template .
:C      a :PL ; rdfs:label "C" ; :creator :dennis_ritchie ; :year 1972 ;
        :hasFeature :type , :pointer , :function .
:Java   a :PL ; rdfs:label "Java" ; :creator :james_gosling ; :year 1995 ; :influencedBy :CPP ;
        :hasFeature :type , :class .
:Kotlin a :PL ; :creator :jetbrains ; :year 2011 ; :influencedBy :Java ;
        :hasFeature :class , :function .
:Python :year 1991 ; :hasFeature :function , :class .
:Lisp   a :PL ; :year 1958 ; :hasFeature :function .
:Ruby   a :PL ; :influencedBy :Lisp .
```
Viết các truy vấn SPARQL:
- a) (0.5đ) Các ngôn ngữ lập trình (`:PL`) có tính năng con trỏ (`:pointer`) **hoặc** lớp (`:class`), không trùng lặp.
- b) (0.25đ) Các NNLT cùng người sáng lập nếu có; để trống nếu không có dữ liệu.
- c) (0.25đ) Các NNLT **không có** tính năng nào.
- d) (0.5đ) Số tính năng của mỗi NNLT, chỉ lấy NNLT có **từ 2 tính năng trở lên**, sắp xếp giảm dần.
- e) (0.25đ) Tất cả ngôn ngữ ảnh hưởng tới Kotlin, **trực tiếp hoặc gián tiếp**.
- f) (0.5đ) Khẳng định (CONSTRUCT) các NNLT có tính năng lớp là `:OOPL`.
- g) (0.25đ) Các NNLT ra đời trong khoảng 1980–2000.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- "hoặc" → UNION (hoặc `FILTER(?f IN (:pointer, :class))`). "không trùng lặp" → DISTINCT.
- "nếu có / để trống" → OPTIONAL.
- "không có" → `FILTER NOT EXISTS`.
- "số … mỗi" → `GROUP BY` + `COUNT`; điều kiện trên nhóm → `HAVING`.
- "trực tiếp hoặc gián tiếp" → property path `:influencedBy+`.
- "khẳng định" → CONSTRUCT.
- **Bẫy:** `:Python` không có `a :PL`, nên mọi câu có `?x a :PL` đều **không trả về Python**.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
# a)
SELECT DISTINCT ?lang WHERE {
  { ?lang a :PL ; :hasFeature :pointer . }
  UNION
  { ?lang a :PL ; :hasFeature :class . }
}
```
Kết quả a): `:C`, `:CPP`, `:Java`, `:Kotlin` (không có Python vì Python không có `a :PL`).

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
# b)
SELECT ?lang ?creator WHERE {
  ?lang a :PL .
  OPTIONAL { ?lang :creator ?creator . }
}
```
| ?lang | ?creator |
|---|---|
| :C | :dennis_ritchie |
| :CPP | :bjarne_stroustrup |
| :Java | :james_gosling |
| :Kotlin | :jetbrains |
| :Lisp | |
| :Ruby | |

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
# c)
SELECT ?lang WHERE {
  ?lang a :PL .
  FILTER NOT EXISTS { ?lang :hasFeature ?f . }
}
```
Kết quả c): `:Ruby`.

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
# d)
SELECT ?lang (COUNT(?f) AS ?n) WHERE {
  ?lang a :PL ; :hasFeature ?f .
}
GROUP BY ?lang
HAVING (COUNT(?f) >= 2)
ORDER BY DESC(?n)
```
| ?lang | ?n |
|---|---|
| :CPP | 5 |
| :C | 3 |
| :Java | 2 |
| :Kotlin | 2 |

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
# e)
SELECT ?anc WHERE { :Kotlin :influencedBy+ ?anc . }
```
Kết quả e): `:Java`, `:CPP`, `:C`.

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
# f)
CONSTRUCT { ?lang a :OOPL . }
WHERE { ?lang a :PL ; :hasFeature :class . }
```
Kết quả f): `:CPP a :OOPL . :Java a :OOPL . :Kotlin a :OOPL .`

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
# g)
SELECT ?lang ?year WHERE {
  ?lang a :PL ; :year ?year .
  FILTER (?year >= 1980 && ?year <= 2000)
}
ORDER BY ?year
```
Kết quả g): `:CPP 1985`, `:Java 1995`.

- [ ] a) UNION (hoặc FILTER IN) + DISTINCT (0.5đ)
- [ ] b) OPTIONAL đúng chỗ (0.25đ)
- [ ] c) FILTER NOT EXISTS (0.25đ)
- [ ] d) GROUP BY + COUNT + HAVING + ORDER BY DESC (0.5đ)
- [ ] e) property path `+` (0.25đ)
- [ ] f) CONSTRUCT đúng template (0.5đ)
- [ ] g) FILTER so sánh số, có `&&` (0.25đ)

</details>

### Câu 7 (1 điểm) · [D9]
Với dữ liệu Câu 6, xét truy vấn (câu a không có DISTINCT):

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
SELECT ?lang WHERE {
  { ?lang a :PL . ?lang :hasFeature :pointer . }
  UNION
  { ?lang a :PL . ?lang :hasFeature :class . }
}
```
Viết biểu thức đại số SPARQL tương ứng và giải thích chi tiết từng bước thực hiện cùng kết quả thu được.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Dịch từ trong ra ngoài:
  - mỗi nhóm `{ … }` → `BGP(...)`;
  - UNION → `Union(…, …)`;
  - OPTIONAL → `LeftJoin`;
  - FILTER → `Filter(expr, …)` bọc ngoài cả nhóm;
  - `SELECT ?v` → `Project(…, {?v})`;
  - DISTINCT → `Distinct(...)`.
- Mỗi bước vẽ **bảng ánh xạ μ** (một cột cho mỗi biến).

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```text
Project( Union( BGP(?lang a :PL . ?lang :hasFeature :pointer),
                BGP(?lang a :PL . ?lang :hasFeature :class) ),
         {?lang} )
```
**Bước 1:** BGP₁ (`?lang a :PL . ?lang :hasFeature :pointer`)

| ?lang |
|---|
| :CPP |
| :C |

**Bước 2:** BGP₂ (`?lang a :PL . ?lang :hasFeature :class`). Python bị loại vì không có `a :PL`.

| ?lang |
|---|
| :CPP |
| :Java |
| :Kotlin |

**Bước 3:** Union = hợp đa tập, **giữ trùng lặp**.

| ?lang |
|---|
| :CPP |
| :C |
| :CPP |
| :Java |
| :Kotlin |

**Bước 4:** Project({?lang}) giữ nguyên 5 dòng. Kết quả có `:CPP` **xuất hiện 2 lần**. Muốn bỏ trùng thì thêm `Distinct(...)` (SELECT DISTINCT) để còn 4 dòng.

- [ ] Biểu thức đại số đúng cấu trúc (0.25đ)
- [ ] Bảng BGP₁, BGP₂ đúng (0.25đ)
- [ ] Union giữ trùng (0.25đ)
- [ ] Project + nhận xét DISTINCT (0.25đ)

</details>

### Câu 8 (1.25 điểm) · [D10]
Kiểm duyệt dữ liệu Câu 6 bằng SHACL:
- a) Tạo hình trạng `:PLShape` đảm bảo:
  - mỗi NNLT (`:PL`) có ít nhất 1 nhãn `rdfs:label`;
  - mỗi NNLT được liệt kê ít nhất 1 tính năng;
  - năm ra đời (nếu có) là số nguyên ≥ 1950 và tối đa 1 giá trị.
- b) Những nút nào được kiểm tra? Những nút nào vi phạm, vi phạm ràng buộc nào? Đề xuất bổ sung dữ liệu.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Khuôn: `:Shape a sh:NodeShape ; sh:targetClass :X ; sh:property [ sh:path :p ; <ràng buộc> ]`.
- "ít nhất 1" → `sh:minCount 1`. "tối đa 1" → `sh:maxCount 1`. "≥" → `sh:minInclusive`. "kiểu số nguyên" → `sh:datatype xsd:integer`.
- "(nếu có)" → **không** đặt minCount.
- Nút được kiểm = những nút có `rdf:type :PL` **hoặc** `rdf:type :Sub` với `:Sub rdfs:subClassOf* :PL` có **trong data graph** (định nghĩa "SHACL instance", giống `sh:class` ở Đề 2 Câu 7). SHACL **không** suy kiểu từ domain/range/OWL. SHACL là CWA: thiếu dữ liệu là vi phạm.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```turtle
@prefix :     <http://semweb.edu.vn/exam#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
:PLShape a sh:NodeShape ;
    sh:targetClass :PL ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] ;
    sh:property [ sh:path :hasFeature ; sh:minCount 1 ] ;
    sh:property [ sh:path :year ; sh:datatype xsd:integer ; sh:minInclusive 1950 ; sh:maxCount 1 ] .
```
b)
- **Nút được kiểm** (focus node): `:CPP, :C, :Java, :Kotlin, :Lisp, :Ruby`, là 6 nút có `a :PL`.
- `:Python` **không bị kiểm**, vì không có `a :PL` (cũng không có kiểu nào là lớp con của `:PL` trong dữ liệu; SHACL không suy kiểu từ domain/range).
- **Vi phạm:**
  - `:Kotlin`: thiếu `rdfs:label` (minCount).
  - `:Lisp`: thiếu `rdfs:label`.
  - `:Ruby`: thiếu `rdfs:label` **và** thiếu `:hasFeature`.
- Không nút nào vi phạm ràng buộc `:year`. Năm nhỏ nhất là Lisp 1958 ≥ 1950. Ruby không có `:year` cũng không vi phạm vì không có minCount.
- **Bổ sung dữ liệu:**

```turtle
@prefix :     <http://semweb.edu.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:Kotlin rdfs:label "Kotlin" .
:Lisp   rdfs:label "Lisp" .
:Ruby   rdfs:label "Ruby" ; :hasFeature :class .
```

- [ ] NodeShape + targetClass (0.25đ)
- [ ] 3 property shape đúng ràng buộc (0.5đ)
- [ ] Liệt kê đúng nút được kiểm, nêu Python bị loại (0.25đ)
- [ ] Đúng các vi phạm + đề xuất sửa (0.25đ)

</details>

---

## Đề 2 — Ghép từ bài tập tuần (10 điểm, 150 phút)

### Câu 1 (1.25 điểm) · [D1 · D2]
a) (0.75đ) Viết các câu sau bằng RDF (Turtle), **mỗi câu ít nhất 3 bộ-3**:
- SOICT is located at No. 1, Dai Co Viet, Hai Ba Trung, Hanoi.
- Website https://soict.hust.edu.vn/ is the homepage of SOICT.
- Resource URI1 is a course on Semantic Web, taught by Lecturer Hung in room B1-404.

b) (0.5đ) Vẽ đồ thị cho đoạn Turtle sau, viết lại bằng N-Triples và diễn đạt bằng lời:

```turtle
@prefix : <http://example.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
:Minh a :Teacher ; :teaches "Semantic Web" , "Data Integration" ; foaf:member :SOICT .
[] foaf:knows :Minh ; foaf:member [ a :Company ] .
```

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Địa chỉ nhiều thành phần → blank node n-ngôi. Website là một **IRI** (không phải literal), nên có thể gắn thêm kiểu cho nó.
- Liệt kê **hết** các bộ-3 có thể (theo Notes): `rdf:type` cho mọi thực thể, tên/nhãn, quan hệ chính.
- `[]` và `[ … ]` là blank node. Đếm bộ-3: mỗi `;` và mỗi `,` sinh thêm 1 bộ-3.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

a)
```turtle graph
@prefix : <http://example.org/hust#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dc: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:SOICT a foaf:Organization ; :locatedAt [ :street "No. 1 Dai Co Viet" ; :district "Hai Ba Trung" ; :city "Hanoi" ] .
:SOICT foaf:homepage <https://soict.hust.edu.vn/> .
<https://soict.hust.edu.vn/> a foaf:Document ; dc:title "SOICT homepage"@en .
:URI1 a :Course ; :subject "Semantic Web" ; :taughtBy :Hung ; :room :B1-404 .
:Hung a :Lecturer ; foaf:name "Hung" .
:B1-404 a :Room ; rdfs:label "B1-404" .
```

b) Đồ thị có **7 bộ-3, 2 blank node**:

```turtle graph
@prefix : <http://example.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
:Minh a :Teacher ; :teaches "Semantic Web" , "Data Integration" ; foaf:member :SOICT .
[] foaf:knows :Minh ; foaf:member [ a :Company ] .
```
```text
<http://example.org/Minh> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.org/Teacher> .
<http://example.org/Minh> <http://example.org/teaches> "Semantic Web" .
<http://example.org/Minh> <http://example.org/teaches> "Data Integration" .
<http://example.org/Minh> <http://xmlns.com/foaf/0.1/member> <http://example.org/SOICT> .
_:b1 <http://xmlns.com/foaf/0.1/knows> <http://example.org/Minh> .
_:b1 <http://xmlns.com/foaf/0.1/member> _:b2 .
_:b2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.org/Company> .
```
Diễn đạt bằng lời: Minh là giáo viên, dạy "Semantic Web" và "Data Integration", là thành viên SOICT. Có một người (không rõ là ai) quen Minh, và người đó là thành viên của một công ty nào đó.

- [ ] a) mỗi câu ≥3 bộ-3, địa chỉ dùng blank node (0.5đ)
- [ ] a) homepage là IRI, có rdf:type (0.25đ)
- [ ] b) đồ thị đúng 2 blank node + N-Triples dùng IRI đầy đủ, `_:b` (0.25đ)
- [ ] b) diễn đạt bằng lời đúng (0.25đ)

</details>

### Câu 2 (1.25 điểm) · [D3 · D4]
Cho đồ thị RDF:

```turtle graph
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://example.com/terms#> .
:Person a rdfs:Class .
:Man a rdfs:Class ; rdfs:subClassOf :Person .
:Parent a rdfs:Class ; rdfs:subClassOf :Person .
:Father a rdfs:Class ; rdfs:subClassOf :Parent , :Man .
:Child a rdfs:Class ; rdfs:subClassOf :Person .
:hasParent a rdf:Property ; rdfs:domain :Person ; rdfs:range :Parent .
:hasFather a rdf:Property ; rdfs:subPropertyOf :hasParent ; rdfs:range :Father .
:isChildOf a rdf:Property ; rdfs:domain :Child ; rdfs:range :Parent .
:Ann a :Person ; :hasFather :Carl .
:Carl a :Man .
```
a) (0.25đ) Vẽ đồ thị biểu diễn các bộ-3 trên.
b) (1đ) Các mệnh đề sau đúng (TRUE) hay không xác định (UNKNOWN)? Giải thích bằng tên luật.
1. `:Father rdfs:subClassOf :Person`
2. `:Man rdfs:subClassOf :Person`
3. `:Carl a :Person`
4. `:Carl a :Parent`
5. `:Carl :hasChild :Ann`
6. `:Carl a :Man`
7. `:Carl a :Father`
8. `:Child rdf:type rdfs:Resource`

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Với mỗi mệnh đề: (1) có sẵn trong G? → TRUE. (2) Tìm chuỗi luật rdfs2/3/7/9/11/4a dẫn tới nó → TRUE, ghi rõ chuỗi. (3) Không tìm được → **UNKNOWN**, không ghi FALSE (vì OWA, và RDFS không có phủ định).
- Predicate không xuất hiện trong G (ví dụ `:hasChild`) không bao giờ được suy ra.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

a) Xem đồ thị tự vẽ ở trên đề. Mỗi class còn có `rdf:type rdfs:Class`, mỗi property có `rdf:type rdf:Property`.

b)

| # | Kết quả | Giải thích |
|---|---|---|
| 1 | TRUE | rdfs11: Father ⊑ Parent ⊑ Person |
| 2 | TRUE | có sẵn trong G |
| 3 | TRUE | `:Carl a :Man` + `Man ⊑ Person` (rdfs9) |
| 4 | TRUE | rdfs3: `:Ann :hasFather :Carl` + range hasFather = Father cho ra `:Carl a :Father`; rồi rdfs9 với Father ⊑ Parent. (Cách khác: rdfs7 cho `:Ann :hasParent :Carl`, rồi rdfs3 với range Parent) |
| 5 | UNKNOWN | `:hasChild` không có trong G. RDFS không có inverse |
| 6 | TRUE | có sẵn trong G |
| 7 | TRUE | rdfs3 (range của hasFather là Father) |
| 8 | TRUE | rdfs4a: `:Child` là chủ thể của một bộ-3 (`:Child a rdfs:Class`) |

- [ ] a) đồ thị đủ subClassOf/subPropertyOf/domain/range/instance (0.25đ)
- [ ] b) mỗi 2 mệnh đề đúng + lý do (0.25đ × 4)

</details>

### Câu 3 (1.5 điểm) · [D5] — "bài 3"
Xây dựng ontology OWL (DL + Turtle) cho mô tả:

> *A laboratory-course is a course. Courses are organized by teachers. Teachers can be professors or assistants. The professor teaches the courses, while the assistant only teaches the practical courses. Homework is part of the course.*

<details class="hint"><summary>Gợi ý / Khuôn</summary>

1. Gạch chân danh từ → lớp; động từ → thuộc tính (đặt domain/range).
2. "is a" → ⊑. "can be A or B" → A ⊑ T, B ⊑ T (thêm covering `T ≡ A ⊔ B` + disjoint nếu giả định; nêu rõ giả định).
3. "teaches the courses" → `∃teaches.Course`. "**only** teaches practical courses" → `∀teaches.LaboratoryCourse` (**không** dùng range).
4. "are organized by" → ∃isOrganizedBy.Teacher + inverseOf.
5. Trình bày theo thứ tự: bảng câu → tiên đề, DL, Turtle, giải thích lựa chọn.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```text
LaboratoryCourse ⊑ Course
Professor ⊑ Teacher            Assistant ⊑ Teacher
Teacher ≡ Professor ⊔ Assistant          (giả định covering)
Professor ⊓ Assistant ⊑ ⊥                (giả định disjoint)
Course ⊑ ∃isOrganizedBy.Teacher          isOrganizedBy ≡ organizes⁻
∃organizes.⊤ ⊑ Teacher     ⊤ ⊑ ∀organizes.Course
∃teaches.⊤ ⊑ Teacher       ⊤ ⊑ ∀teaches.Course
Professor ⊑ ∃teaches.Course
Assistant ⊑ ∀teaches.LaboratoryCourse
Homework ⊑ ∃isPartOf.Course
∃isPartOf.⊤ ⊑ Homework     ⊤ ⊑ ∀isPartOf.Course
```
```turtle
@prefix :     <http://example.org/course#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:LaboratoryCourse a owl:Class ; rdfs:subClassOf :Course .
:Course a owl:Class ;
    rdfs:subClassOf [ a owl:Restriction ; owl:onProperty :isOrganizedBy ; owl:someValuesFrom :Teacher ] .
:Teacher a owl:Class ;
    owl:equivalentClass [ a owl:Class ; owl:unionOf ( :Professor :Assistant ) ] .
:Professor a owl:Class ; rdfs:subClassOf :Teacher ,
    [ a owl:Restriction ; owl:onProperty :teaches ; owl:someValuesFrom :Course ] ;
    owl:disjointWith :Assistant .
:Assistant a owl:Class ; rdfs:subClassOf :Teacher ,
    [ a owl:Restriction ; owl:onProperty :teaches ; owl:allValuesFrom :LaboratoryCourse ] .
:Homework a owl:Class ;
    rdfs:subClassOf [ a owl:Restriction ; owl:onProperty :isPartOf ; owl:someValuesFrom :Course ] .
:organizes     a owl:ObjectProperty ; rdfs:domain :Teacher ; rdfs:range :Course .
:isOrganizedBy a owl:ObjectProperty ; owl:inverseOf :organizes .
:teaches       a owl:ObjectProperty ; rdfs:domain :Teacher ; rdfs:range :Course .
:isPartOf      a owl:ObjectProperty ; rdfs:domain :Homework ; rdfs:range :Course .
```
Giải thích các lựa chọn:
- **Vì sao không dùng `teaches rdfs:range LaboratoryCourse`?** Range là toàn cục, nên giáo sư cũng sẽ chỉ dạy được môn thực hành, là sai. Phải dùng `∀teaches.LaboratoryCourse`, chỉ áp riêng cho Assistant.
- **Vì sao Professor dùng `some`?** "teaches the courses" khẳng định giáo sư có dạy ít nhất một môn.

- [ ] Phân cấp lớp + covering/disjoint có ghi giả định (0.25đ)
- [ ] 4 thuộc tính có domain/range, inverse (0.25đ)
- [ ] `Professor ⊑ ∃teaches.Course` (0.25đ)
- [ ] `Assistant ⊑ ∀teaches.LaboratoryCourse` + giải thích vì sao không dùng range (0.5đ)
- [ ] Homework ⊑ ∃isPartOf.Course; Turtle khớp DL (0.25đ)

</details>

### Câu 4 (1.25 điểm) · [D12]
Cho TBox:
1. `Professor ⊑ ∃supervises.PhDStudent`
2. `PhDStudent ⊑ Student ⊓ Researcher`
3. `Professor ⊑ ∀supervises.(¬Student ⊔ Employee)`

a) Dùng tableau chứng minh hoặc bác bỏ `Professor ⊑ ∃supervises.Employee`.
b) Nếu bỏ tiên đề 3 thì kết luận thay đổi thế nào?

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- **Subsumption C ⊑ D** được chứng minh bằng cách cho thấy `C ⊓ ¬D` **không thỏa được**: tạo cá thể mới i, thêm `C(i)` và `NNF(¬D)(i)`. Nếu mọi nhánh đóng thì C ⊑ D đúng.
- NNF: `X ⊑ Y` thành `¬X ⊔ Y`; `¬∃R.C` thành `∀R.¬C`.
- 7 luật: 3 = áp tiên đề TBox cho cá thể; 4 = ⊓; 5 = ⊔ (tách nhánh); 6 = ∃ (sinh cá thể mới); 7 = ∀.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

NNF:
- a) `¬Professor ⊔ ∃supervises.PhDStudent`
- b) `¬PhDStudent ⊔ (Student ⊓ Researcher)`
- c) `¬Professor ⊔ ∀supervises.(¬Student ⊔ Employee)`

Phản chứng: `Professor(i)`, `(∀supervises.¬Employee)(i)`.
```text
Professor(i), (∀supervises.¬Employee)(i)
└─[3a] (¬Professor ⊔ ∃supervises.PhDStudent)(i)
   ├─[5] ¬Professor(i)                         ✗ (mâu thuẫn Professor(i))
   └─[5] (∃supervises.PhDStudent)(i)
      └─[6] supervises(i,b0), PhDStudent(b0)
         └─[7] ¬Employee(b0)
            └─[3c] (¬Professor ⊔ ∀supervises.(¬Student ⊔ Employee))(i)
               ├─[5] ¬Professor(i)             ✗
               └─[5] (∀supervises.(¬Student ⊔ Employee))(i)
                  └─[7] (¬Student ⊔ Employee)(b0)
                     └─[3b] (¬PhDStudent ⊔ (Student ⊓ Researcher))(b0)
                        ├─[5] ¬PhDStudent(b0)  ✗ (mâu thuẫn PhDStudent(b0))
                        └─[5] (Student ⊓ Researcher)(b0)
                           └─[4] Student(b0), Researcher(b0)
                              ├─[5 trên (¬Student ⊔ Employee)(b0)] ¬Student(b0) ✗
                              └─[5] Employee(b0)  ✗ (mâu thuẫn ¬Employee(b0))
```
- a) **Mọi nhánh đóng**, nên `Professor ⊓ ¬∃supervises.Employee` không thỏa được. Vậy `Professor ⊑ ∃supervises.Employee` **ĐÚNG**.
- b) Bỏ tiên đề 3 thì không có bước 3c. Nhánh chứa `Professor(i), supervises(i,b0), PhDStudent(b0), Student(b0), Researcher(b0), ¬Employee(b0)` cùng với `¬Professor(b0)` (chọn khi áp 3a cho b0) **không còn mâu thuẫn và không còn luật áp được**. Nhánh mở nên **không suy ra được** kết luận.

- [ ] NNF đúng 3 tiên đề (0.25đ)
- [ ] Phản chứng đúng: ¬∃ thành ∀¬ (0.25đ)
- [ ] Cây áp đúng luật, đánh dấu nhánh đóng (0.5đ)
- [ ] b) chỉ ra nhánh mở (0.25đ)

</details>

### Câu 5 (0.75 điểm) · [D9]
Trên dữ liệu ontology môn học (`de2.ttl`, phần A-Box), cho truy vấn:

```sparql
PREFIX : <http://example.org/course#>
SELECT ?c ?h WHERE {
  ?c :credits ?cr .
  OPTIONAL { ?h :isPartOf ?c }
  FILTER (?cr >= 2)
}
```
Dữ liệu liên quan:
- `:credits`: SemanticWeb 3, DataIntegration 2, MachineLearning 3, SemanticWebLab 1, MLLab 1.
- `:isPartOf`: hw1, hw2, hw3 → SemanticWeb; hw4 → SemanticWebLab; hw5 → MachineLearning.

Viết biểu thức đại số và giải từng bước.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- FILTER trong nhóm có OPTIONAL bọc **ngoài** LeftJoin: `Filter(expr, LeftJoin(BGP₁, BGP₂))`.
- LeftJoin giữ mọi dòng bên trái. Dòng nào không ghép được thì để trống biến bên phải.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```text
Project( Filter( ?cr >= 2,
                 LeftJoin( BGP(?c :credits ?cr), BGP(?h :isPartOf ?c) ) ),
         {?c, ?h} )
```
- BGP₁ = {(SemanticWeb,3), (DataIntegration,2), (MachineLearning,3), (SemanticWebLab,1), (MLLab,1)}
- BGP₂ = {(hw1,SemanticWeb), (hw2,SemanticWeb), (hw3,SemanticWeb), (hw4,SemanticWebLab), (hw5,MachineLearning)}
- LeftJoin cho 7 dòng:

| ?c | ?cr | ?h |
|---|---|---|
| :SemanticWeb | 3 | :hw1 |
| :SemanticWeb | 3 | :hw2 |
| :SemanticWeb | 3 | :hw3 |
| :DataIntegration | 2 | |
| :MachineLearning | 3 | :hw5 |
| :SemanticWebLab | 1 | :hw4 |
| :MLLab | 1 | |

- Filter(?cr ≥ 2) loại 2 dòng có credits = 1, còn 5 dòng.
- Project({?c, ?h}):

| ?c | ?h |
|---|---|
| :SemanticWeb | :hw1 |
| :SemanticWeb | :hw2 |
| :SemanticWeb | :hw3 |
| :MachineLearning | :hw5 |
| :DataIntegration | |

(đã chạy kiểm bằng rdflib)

- [ ] Biểu thức đúng thứ tự Filter ngoài LeftJoin (0.25đ)
- [ ] Bảng LeftJoin 7 dòng (0.25đ)
- [ ] Filter + Project đúng (0.25đ)

</details>

### Câu 6 (2.5 điểm) · [D8] — câu SPARQL
Dữ liệu: `de2.ttl` (ontology môn học Câu 3 + A-Box):
- `:hung`, `:lan` a `:Professor`; `:minh`, `:an` a `:Assistant`.
- hung teaches SemanticWeb, DataIntegration và organizes SemanticWeb.
- lan teaches MachineLearning và organizes MachineLearning, DataIntegration.
- minh teaches SemanticWebLab; an teaches SemanticWebLab, MLLab.
- SemanticWeb, DataIntegration, MachineLearning a `:Course`; SemanticWebLab, MLLab a `:LaboratoryCourse`.
- Mỗi người/môn/homework có `:name`, mỗi môn có `:credits`.
- hw1–hw3 isPartOf SemanticWeb, hw4 isPartOf SemanticWebLab, hw5 isPartOf MachineLearning.

Viết truy vấn:
- a) (0.25đ) Tên giáo viên và tên môn họ dạy.
- b) (0.5đ) Các môn học (kể cả môn thực hành, vốn chỉ có kiểu `:LaboratoryCourse`) **không có** homework.
- c) (0.5đ) Các môn có **ít nhất 2** homework, kèm số lượng.
- d) (0.25đ) Giáo viên vừa dạy vừa tổ chức **cùng một** môn.
- e) (0.25đ) Mọi môn có kiểu `:Course` kèm người tổ chức nếu có.
- f) (0.25đ) Hỏi (ASK): có trợ giảng nào dạy môn không phải môn thực hành không?
- g) (0.5đ) Sinh các bộ-3 `:isTaughtBy` (ngược của `:teaches`).

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- b) dữ liệu **không được suy diễn**: SemanticWebLab chỉ có `a :LaboratoryCourse`. Hãy dùng path `a/rdfs:subClassOf*` (hoặc UNION hai kiểu), sau đó `FILTER NOT EXISTS`.
- c) `GROUP BY ?c HAVING(COUNT(?h) >= 2)`.
- d) dùng **cùng biến** ?c cho cả 2 bộ-3.
- f) `ASK { … FILTER NOT EXISTS { ?c a :LaboratoryCourse } }`.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```sparql
PREFIX : <http://example.org/course#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# a)
SELECT ?tname ?cname WHERE { ?t :teaches ?c . ?t :name ?tname . ?c :name ?cname . }
```
| ?tname | ?cname |
|---|---|
| An | Machine Learning Lab |
| An | Semantic Web Lab |
| Hung | Data Integration |
| Hung | Semantic Web |
| Lan | Machine Learning |
| Minh | Semantic Web Lab |

```sparql
PREFIX : <http://example.org/course#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# b)
SELECT ?c WHERE {
  ?c a/rdfs:subClassOf* :Course .
  FILTER NOT EXISTS { ?h :isPartOf ?c }
}
```
Kết quả b): `:DataIntegration`, `:MLLab`.

```sparql
PREFIX : <http://example.org/course#>
# c)
SELECT ?c (COUNT(?h) AS ?n) WHERE { ?h a :Homework ; :isPartOf ?c . }
GROUP BY ?c HAVING (COUNT(?h) >= 2)
```
Kết quả c): `:SemanticWeb 3`.

```sparql
PREFIX : <http://example.org/course#>
# d)
SELECT ?t ?c WHERE { ?t :teaches ?c ; :organizes ?c . }
```
Kết quả d): `:hung :SemanticWeb`, `:lan :MachineLearning`.

```sparql
PREFIX : <http://example.org/course#>
# e)
SELECT ?c ?org WHERE { ?c a :Course . OPTIONAL { ?org :organizes ?c } }
```
Kết quả e): `:DataIntegration :lan`, `:MachineLearning :lan`, `:SemanticWeb :hung`. Hai môn Lab không xuất hiện vì không có `a :Course` tường minh.

```sparql
PREFIX : <http://example.org/course#>
# f)
ASK { ?a a :Assistant ; :teaches ?c . FILTER NOT EXISTS { ?c a :LaboratoryCourse } }
```
Kết quả f): `false`.

```sparql
PREFIX : <http://example.org/course#>
# g)
CONSTRUCT { ?c :isTaughtBy ?t } WHERE { ?t :teaches ?c }
```
Kết quả g): 6 bộ-3, ví dụ `:SemanticWeb :isTaughtBy :hung`, `:MLLab :isTaughtBy :an`, …

- [ ] a) join 3 bộ-3 (0.25đ)
- [ ] b) path subClassOf* + NOT EXISTS (0.5đ)
- [ ] c) GROUP BY + HAVING (0.5đ)
- [ ] d) dùng chung biến (0.25đ)
- [ ] e) OPTIONAL (0.25đ)
- [ ] f) ASK + NOT EXISTS (0.25đ)
- [ ] g) CONSTRUCT (0.5đ)

</details>

### Câu 7 (0.5 điểm) · [D10]
Viết hình trạng SHACL `:HomeworkShape` đảm bảo mỗi Homework thuộc **đúng một** môn học (giá trị của `:isPartOf` phải là `:Course`). Với dữ liệu `de2.ttl`, kết quả kiểm tra thế nào? Riêng `:hw4` (thuộc SemanticWebLab, vốn chỉ có kiểu `:LaboratoryCourse`) có vi phạm không?

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- "đúng một" → `sh:minCount 1 ; sh:maxCount 1`. "là Course" → `sh:class :Course`.
- `sh:class` chấp nhận cả lớp con, theo `rdfs:subClassOf*` **có trong data graph**.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```turtle
@prefix :   <http://example.org/course#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
:HomeworkShape a sh:NodeShape ;
    sh:targetClass :Homework ;
    sh:property [ sh:path :isPartOf ; sh:minCount 1 ; sh:maxCount 1 ; sh:class :Course ] .
```
- Nút được kiểm: hw1 đến hw5. Mỗi nút có đúng 1 `:isPartOf`.
- `:hw4` **không vi phạm**: `:SemanticWebLab a :LaboratoryCourse`, và data graph có `:LaboratoryCourse rdfs:subClassOf :Course`. Theo định nghĩa "SHACL instance" (rdf:type kết hợp rdfs:subClassOf*), nó được tính là một Course.
- Kết luận: **conforms = true**.

- [ ] Shape đúng (0.25đ)
- [ ] Giải thích hw4 qua subClassOf* (0.25đ)

</details>

### Câu 8 (1 điểm) · [D11]
a) Phân biệt Giả thiết thế giới mở (OWA) và thế giới đóng (CWA). Nêu hệ quả trong RDFS/OWL, SPARQL và SHACL.
b) So sánh RDFS và OWL: khả năng biểu đạt, phủ định/mâu thuẫn, kỹ thuật suy diễn.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

Mỗi ý: định nghĩa, ví dụ, hệ quả. Nên trình bày b) dạng bảng 3 hàng.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

**a) OWA và CWA**
- **OWA:** không biết thì **không** có nghĩa là sai. Ví dụ `:Peter :fatherOf :Julia, :Mary` chỉ cho biết Peter có **ít nhất 1** con (không có UNA nên Julia có thể là Mary), có thể nhiều hơn (OWA). Muốn kết luận ≥ 2 con phải thêm `:Julia owl:differentFrom :Mary`.
- **CWA** (CSDL, Prolog): không có trong dữ liệu thì là sai.
- Hệ quả trong RDFS/OWL:
  - suy diễn chỉ trả lời TRUE hoặc UNKNOWN, không trả lời FALSE;
  - `allValuesFrom` không phân loại được cá thể nếu thiếu tiên đề đóng (closure axiom, ví dụ pizza Margherita);
  - thiếu dữ liệu bắt buộc **không** gây lỗi.
- Hệ quả trong SPARQL: truy vấn chạy trên dữ liệu có thật. `FILTER NOT EXISTS` và `COUNT` mang tính đóng; ASK trả `false` chỉ có nghĩa là "không tìm thấy".
- Hệ quả trong SHACL: kiểm tra ràng buộc theo CWA, nên thiếu `minCount` là vi phạm.

**b) RDFS và OWL**

| | RDFS | OWL |
|---|---|---|
| Biểu đạt | lớp, thuộc tính, subClass/subProperty, domain/range | + restriction (some/only/hasValue), cardinality, đặc tính thuộc tính (transitive, symmetric, inverse, functional), union/intersection/complement, oneOf, disjoint, sameAs |
| Phủ định | không có, nên luôn consistent | có (disjointWith, complementOf), nên phát hiện được mâu thuẫn |
| Suy diễn | forward chaining theo luật rdfs1–13, luôn dừng | tableau (OWL DL), các profile EL/QL/RL có độ phức tạp đa thức |

- [ ] OWA/CWA định nghĩa + ví dụ (0.25đ)
- [ ] Hệ quả cho ≥2 trong RDFS/OWL, SPARQL, SHACL (0.25đ)
- [ ] Bảng so sánh đủ 3 hàng (0.5đ)

</details>

---

## Đề 3 — Đề mới: miền Bệnh viện (10 điểm, 150 phút)

### Câu 1 (1.25 điểm) · [D1]
Biểu diễn bằng Turtle và vẽ đồ thị RDF:

> Bệnh nhân Minh (35 tuổi) được bác sĩ Lan khám ngày 10/10/2026 và được chẩn đoán mắc bệnh cúm. Đơn thuốc của lần khám này gồm Paracetamol, Vitamin C và Oseltamivir. Y tá Tuấn cho rằng bệnh nhân Minh cần nhập viện.

Liệt kê đầy đủ các bộ-3 (đếm số bộ-3).

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- "lần khám" có nhiều thuộc tính (bệnh nhân, bác sĩ, ngày, chẩn đoán, đơn thuốc) → tạo **một nút sự kiện** (IRI `:kham01` hoặc blank node), là quan hệ n-ngôi.
- Đơn thuốc "gồm" → collection. Ngày → literal `"2026-10-10"^^xsd:date`. Tuổi → số nguyên.
- "Y tá Tuấn **cho rằng**" → reification.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```turtle graph
@prefix : <http://hospital.vn/exam#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:minh a :Patient ; :name "Minh" ; :age 35 .
:lan a :Doctor ; :name "Lan" .
:tuan a :Nurse ; :name "Tuấn" .
:kham01 a :Examination ; :patient :minh ; :doctor :lan ; :date "2026-10-10"^^xsd:date ; :diagnosis :Cum ; :prescription ( :Paracetamol :VitaminC :Oseltamivir ) .
:tuan :thinks [ a rdf:Statement ; rdf:subject :minh ; rdf:predicate :needs ; rdf:object :Hospitalization ] .
```
**Đếm bộ-3 (24):**
- Minh 3, Lan 2, Tuấn 2.
- `:kham01` có 6, cộng 6 của danh sách 3 thuốc.
- `:thinks` có 1, cộng 4 của nút `rdf:Statement`.

Cách khác cũng được chấp nhận: biểu diễn trực tiếp `:minh :diagnosedWith :Cum`. Nhưng khi đó mất thông tin "lần khám nào, ngày nào", nên nút sự kiện tốt hơn.

- [ ] Nút sự kiện n-ngôi cho lần khám (0.25đ)
- [ ] Literal có kiểu (xsd:date, số) (0.25đ)
- [ ] Collection đơn thuốc (0.25đ)
- [ ] Reification "cho rằng" (0.25đ)
- [ ] Đồ thị + đếm đúng bộ-3 (0.25đ)

</details>

### Câu 2 (1 điểm) · [D3 · D4]
a) (0.5đ) Dùng RDFS biểu diễn:
- Bác sĩ và y tá là nhân viên y tế; nhân viên y tế là người; bệnh nhân là người.
- `:treatedBy` có miền là bệnh nhân, khoảng là bác sĩ.
- `:worksIn` có miền là nhân viên y tế, khoảng là khoa (`:Department`).
- `:headOf` (trưởng khoa) là thuộc tính con của `:worksIn`.

b) (0.5đ) Thêm dữ kiện `:hoa :treatedBy :hai . :hai :headOf :KhoaNhi .` Các mệnh đề sau TRUE hay UNKNOWN?
1. `:hoa a :Person`
2. `:hai a :MedicalStaff`
3. `:hai :worksIn :KhoaNhi`
4. `:KhoaNhi a :Department`
5. `:hoa a :Doctor`
6. `:headOf rdfs:domain :MedicalStaff`

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Chuỗi luật: rdfs7 (subProperty) → rdfs2 / rdfs3 → rdfs9.
- Câu 5: RDFS không có disjoint, nên không bao giờ trả lời FALSE.
- Câu 6: bộ-3 `subP rdfs:domain C` không suy ra được bằng luật RDFS (dù ở mức cá thể domain vẫn "truyền": `x headOf y` ⇒ rdfs7 ⇒ rdfs2 ⇒ `x a :MedicalStaff`).

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```turtle graph
@prefix : <http://hospital.vn/exam#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:Doctor rdfs:subClassOf :MedicalStaff .
:Nurse rdfs:subClassOf :MedicalStaff .
:MedicalStaff rdfs:subClassOf :Person .
:Patient rdfs:subClassOf :Person .
:treatedBy a rdf:Property ; rdfs:domain :Patient ; rdfs:range :Doctor .
:worksIn a rdf:Property ; rdfs:domain :MedicalStaff ; rdfs:range :Department .
:headOf a rdf:Property ; rdfs:subPropertyOf :worksIn .
```

| # | Kết quả | Giải thích |
|---|---|---|
| 1 | TRUE | rdfs2 (domain treatedBy) cho `:hoa a :Patient`; rdfs9 với Patient ⊑ Person |
| 2 | TRUE | rdfs3 (range treatedBy) cho `:hai a :Doctor`; rdfs9 với Doctor ⊑ MedicalStaff (cũng có thể qua rdfs7 rồi rdfs2) |
| 3 | TRUE | rdfs7: headOf ⊑ worksIn |
| 4 | TRUE | rdfs7 cho 3, rồi rdfs3 (range worksIn) |
| 5 | UNKNOWN | không có luật nào dẫn tới; RDFS không có phủ định nên không thể là FALSE |
| 6 | UNKNOWN | không luật RDFS nào sinh ra bộ-3 `:headOf rdfs:domain …`; ở mức cá thể thì mọi chủ thể của headOf vẫn là MedicalStaff (rdfs7 ⇒ rdfs2), nhưng mệnh đề hỏi bộ-3 schema |

- [ ] a) schema đủ subClassOf, domain/range, subPropertyOf (0.5đ)
- [ ] b) ≥5/6 đúng có tên luật (0.5đ)

</details>

### Câu 3 (1.25 điểm) · [D5]
Biểu diễn bằng OWL (Turtle) và DL:
- a) Bệnh nhân nội trú (`:Inpatient`) và bệnh nhân ngoại trú (`:Outpatient`) là bệnh nhân; không ai vừa nội trú vừa ngoại trú.
- b) `:treats` là thuộc tính ngược của `:treatedBy`. Bác sĩ **chỉ** điều trị bệnh nhân.
- c) Bác sĩ chuyên khoa (`:Specialist`) là bác sĩ có ít nhất một chuyên khoa (`:hasSpecialty`).
- d) Bệnh nhân nặng (`:CriticalPatient`) là bệnh nhân mắc **ít nhất 2** bệnh (`:diagnosedWith` thuộc lớp `:Disease`).
- e) Mỗi bệnh nhân có đúng một mã hồ sơ (`:recordId`). Nhóm máu (`:bloodType`) chỉ nhận một trong các giá trị A, B, AB, O.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

| Đề nói | Cấu trúc OWL |
|---|---|
| "không ai vừa … vừa …" | `owl:disjointWith` |
| "ngược" | `owl:inverseOf` |
| "chỉ" | `owl:allValuesFrom` |
| "ít nhất một" | `owl:someValuesFrom` |
| "ít nhất 2 bệnh" | `owl:minQualifiedCardinality 2` + `owl:onClass :Disease` |
| "đúng một" | `owl:cardinality 1` hoặc `owl:FunctionalProperty` |
| "chỉ một trong" | `owl:oneOf` |
| lớp được định nghĩa ("là … có …") | `owl:equivalentClass` |

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```turtle
@prefix : <http://hospital.vn/exam#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:Inpatient  rdfs:subClassOf :Patient ; owl:disjointWith :Outpatient .
:Outpatient rdfs:subClassOf :Patient .
:treats a owl:ObjectProperty ; owl:inverseOf :treatedBy .
:Doctor rdfs:subClassOf [ a owl:Restriction ; owl:onProperty :treats ; owl:allValuesFrom :Patient ] .
:Specialist owl:equivalentClass [ owl:intersectionOf ( :Doctor
    [ a owl:Restriction ; owl:onProperty :hasSpecialty ; owl:someValuesFrom owl:Thing ] ) ] .
:CriticalPatient owl:equivalentClass [ owl:intersectionOf ( :Patient
    [ a owl:Restriction ; owl:onProperty :diagnosedWith ;
      owl:minQualifiedCardinality "2"^^xsd:nonNegativeInteger ; owl:onClass :Disease ] ) ] .
:recordId a owl:DatatypeProperty .
:Patient rdfs:subClassOf [ a owl:Restriction ; owl:onProperty :recordId ;
    owl:cardinality "1"^^xsd:nonNegativeInteger ] .
:bloodType a owl:ObjectProperty ; rdfs:range [ a owl:Class ; owl:oneOf ( :A :B :AB :O ) ] .
```
```text
Inpatient ⊑ Patient     Outpatient ⊑ Patient     Inpatient ⊓ Outpatient ⊑ ⊥
treats ≡ treatedBy⁻     Doctor ⊑ ∀treats.Patient
Specialist ≡ Doctor ⊓ ∃hasSpecialty.⊤
CriticalPatient ≡ Patient ⊓ ≥2 diagnosedWith.Disease
Patient ⊑ =1 recordId
⊤ ⊑ ∀bloodType.{A, B, AB, O}
```
Lưu ý: ở ý d), muốn reasoner đếm được "2 bệnh" thì hai bệnh phải được khẳng định là khác nhau (`owl:differentFrom` / `owl:AllDifferent`), vì OWL không dùng giả định tên duy nhất (non-UNA).

- [ ] a) subClassOf + disjointWith (0.25đ)
- [ ] b) inverseOf + allValuesFrom (0.25đ)
- [ ] c) equivalentClass + someValuesFrom (0.25đ)
- [ ] d) minQualifiedCardinality 2 + onClass (0.25đ)
- [ ] e) cardinality 1 + oneOf, kèm DL đúng (0.25đ)

</details>

### Câu 4 (1 điểm) · [D12]
Cho TBox: (1) `Inpatient ⊑ ∃stayIn.Hospital`, (2) `Hospital ⊑ HealthFacility`. Dùng tableau chứng minh `Inpatient ⊑ ∃stayIn.HealthFacility`.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

Phản chứng: thêm `Inpatient(i)` và `(∀stayIn.¬HealthFacility)(i)`. NNF của các tiên đề: `¬Inpatient ⊔ ∃stayIn.Hospital`, `¬Hospital ⊔ HealthFacility`.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```text
Inpatient(i), (∀stayIn.¬HealthFacility)(i)
└─[3 với (1)] (¬Inpatient ⊔ ∃stayIn.Hospital)(i)
   ├─[5] ¬Inpatient(i)                     ✗ (mâu thuẫn Inpatient(i))
   └─[5] (∃stayIn.Hospital)(i)
      └─[6] stayIn(i,b), Hospital(b)
         └─[7] ¬HealthFacility(b)
            └─[3 với (2)] (¬Hospital ⊔ HealthFacility)(b)
               ├─[5] ¬Hospital(b)          ✗ (mâu thuẫn Hospital(b))
               └─[5] HealthFacility(b)     ✗ (mâu thuẫn ¬HealthFacility(b))
```
Mọi nhánh đóng, nên `Inpatient ⊓ ¬∃stayIn.HealthFacility` không thỏa được. Vậy **`Inpatient ⊑ ∃stayIn.HealthFacility` đúng**.

- [ ] NNF + giả thiết phản chứng (0.25đ)
- [ ] Áp đúng luật 6, 7 (0.25đ)
- [ ] Đủ nhánh, đánh dấu đóng (0.25đ)
- [ ] Kết luận (0.25đ)

</details>

### Câu 5 (1 điểm) · [D7]
Mạng tiếp xúc dịch bệnh. Cho chương trình Datalog:

```text
TiepXuc(A, B)     TiepXuc(C, B)     TiepXuc(C, D)     Nhiem(A)
R1: TiepXuc(Y, X) ← TiepXuc(X, Y)
R2: NguyCo(Y) ← Nhiem(X) ∧ TiepXuc(X, Y)
R3: NguyCo(Z) ← NguyCo(Y) ∧ TiepXuc(Y, Z)
```
a) Vẽ cây chứng minh `NguyCo(D)`.
b) Tìm điểm cố định (các bước mở rộng).

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- R1 làm quan hệ tiếp xúc trở thành đối xứng. Để đi từ B tới C cần `TiepXuc(B, C)`, mà dữ kiện này phải sinh từ R1.
- Mỗi bước áp mọi luật trên tập hiện có và chỉ ghi phần mới.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

a)
```text
NguyCo(D)                                [R3]
├── NguyCo(C)                            [R3]
│   ├── NguyCo(B)                        [R2]
│   │   ├── Nhiem(A)
│   │   └── TiepXuc(A, B)
│   └── TiepXuc(B, C)                    [R1]
│       └── TiepXuc(C, B)
└── TiepXuc(C, D)
```
b) (đã chạy kiểm bằng máy)
```text
B0: {TiepXuc(A,B), TiepXuc(C,B), TiepXuc(C,D), Nhiem(A)}
B1: + {TiepXuc(B,A), TiepXuc(B,C), TiepXuc(D,C), NguyCo(B)}      (R1, R2)
B2: + {NguyCo(A), NguyCo(C)}                                      (R3: B→A, B→C)
B3: + {NguyCo(D)}                                                 (R3: C→D)
B4: không có dữ kiện mới ⇒ điểm cố định ở Bước 3.
```
Nhận xét: `NguyCo(A)` cũng được suy ra (đi A→B rồi B→A). Đây là hệ quả của cách viết luật, không phải lỗi.

- [ ] Cây đúng, có R1 cho TiepXuc(B,C) (0.5đ)
- [ ] Các bước + điểm cố định đúng (0.5đ)

</details>

### Câu 6 (2.5 điểm) · [D8] — câu SPARQL
Cho CSDL (`de3.ttl`):

```turtle
@prefix :     <http://hospital.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:lan   a :Doctor ; :name "Lan" ; :specialty "Nội khoa" .
:hai   a :Doctor ; :name "Hải" ; :specialty "Nhi khoa" .
:quang a :Doctor ; :name "Quang" .
:minh  a :Patient ; :name "Minh" ; :age 35 ; :treatedBy :lan ; :diagnosedWith :Cum .
:hoa   a :Patient ; :name "Hoa" ; :age 7 ; :treatedBy :hai , :lan ; :diagnosedWith :SotXuatHuyet .
:nam   a :Patient ; :name "Nam" ; :age 68 ; :diagnosedWith :TieuDuong .
:binh  a :Patient ; :age 15 ; :treatedBy :hai .
:Cum           :isA :BenhHoHap .
:BenhHoHap     :isA :BenhTruyenNhiem .
:SotXuatHuyet  :isA :BenhTruyenNhiem .
:TieuDuong     :isA :BenhManTinh .
```
Viết truy vấn:
- a) (0.25đ) Mọi bệnh nhân kèm bác sĩ điều trị; để trống nếu chưa có.
- b) (0.25đ) Bệnh nhân dưới 18 tuổi **hoặc** trên 60 tuổi, sắp theo tuổi tăng dần.
- c) (0.25đ) Bác sĩ **chưa điều trị** bệnh nhân nào.
- d) (0.5đ) Số bệnh nhân của mỗi bác sĩ, chỉ lấy bác sĩ có ≥ 2 bệnh nhân.
- e) (0.5đ) Bệnh nhân mắc bệnh thuộc nhóm `:BenhTruyenNhiem` (trực tiếp hoặc qua nhiều cấp `:isA`).
- f) (0.25đ) Hỏi: có bệnh nhân nào chưa có bác sĩ điều trị không?
- g) (0.25đ) Sinh các bộ-3 `?bacsi :treats ?benhnhan`.
- h) (0.25đ) Tuổi trung bình của các bệnh nhân.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

| Đề nói | Dùng |
|---|---|
| "để trống nếu chưa có" | OPTIONAL |
| "hoặc" trên giá trị số | `FILTER(?age < 18 \|\| ?age > 60)` |
| "chưa" | `FILTER NOT EXISTS` |
| "≥ 2" | `HAVING` |
| "qua nhiều cấp" | `:isA+` |
| "có … không" | ASK |
| "trung bình" | `AVG` |

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```sparql
PREFIX : <http://hospital.vn/exam#>
# a)
SELECT ?p ?d WHERE { ?p a :Patient . OPTIONAL { ?p :treatedBy ?d } }
```
| ?p | ?d |
|---|---|
| :binh | :hai |
| :hoa | :hai |
| :hoa | :lan |
| :minh | :lan |
| :nam | |

```sparql
PREFIX : <http://hospital.vn/exam#>
# b)
SELECT ?p ?age WHERE { ?p a :Patient ; :age ?age . FILTER (?age < 18 || ?age > 60) }
ORDER BY ?age
```
Kết quả b): `:hoa 7`, `:binh 15`, `:nam 68`.

```sparql
PREFIX : <http://hospital.vn/exam#>
# c)
SELECT ?d WHERE { ?d a :Doctor . FILTER NOT EXISTS { ?p :treatedBy ?d } }
```
Kết quả c): `:quang`.

```sparql
PREFIX : <http://hospital.vn/exam#>
# d)
SELECT ?d (COUNT(?p) AS ?n) WHERE { ?p a :Patient ; :treatedBy ?d . }
GROUP BY ?d HAVING (COUNT(?p) >= 2)
```
Kết quả d): `:lan 2` (minh, hoa) và `:hai 2` (hoa, binh).

```sparql
PREFIX : <http://hospital.vn/exam#>
# e)
SELECT ?p ?b WHERE { ?p :diagnosedWith ?b . ?b :isA+ :BenhTruyenNhiem . }
```
Kết quả e): `:minh :Cum` (đi qua BenhHoHap, 2 cấp), `:hoa :SotXuatHuyet`.

```sparql
PREFIX : <http://hospital.vn/exam#>
# f)
ASK { ?p a :Patient . FILTER NOT EXISTS { ?p :treatedBy ?d } }
```
Kết quả f): `true` (vì có `:nam`).

```sparql
PREFIX : <http://hospital.vn/exam#>
# g)
CONSTRUCT { ?d :treats ?p } WHERE { ?p :treatedBy ?d }
```
Kết quả g): `:lan :treats :minh , :hoa . :hai :treats :hoa , :binh .`

```sparql
PREFIX : <http://hospital.vn/exam#>
# h)
SELECT (AVG(?a) AS ?avg) WHERE { ?p a :Patient ; :age ?a }
```
Kết quả h): `31.25` (= (35 + 7 + 68 + 15) / 4).

- [ ] a) OPTIONAL (0.25đ)
- [ ] b) FILTER `||` + ORDER BY (0.25đ)
- [ ] c) NOT EXISTS (0.25đ)
- [ ] d) GROUP BY + HAVING (0.5đ)
- [ ] e) path `+` (0.5đ)
- [ ] f) ASK (0.25đ)
- [ ] g) CONSTRUCT (0.25đ)
- [ ] h) AVG (0.25đ)

</details>

### Câu 7 (1 điểm) · [D10]
Với dữ liệu Câu 6, tạo `:PatientShape` đảm bảo mỗi bệnh nhân:
- có đúng 1 tên kiểu chuỗi;
- có tuổi là số nguyên ≥ 0;
- được điều trị bởi ít nhất 1 bác sĩ (giá trị phải thuộc lớp `:Doctor`).

Những nút nào được kiểm? Nút nào vi phạm, vi phạm gì? Đề xuất sửa.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Dùng `sh:datatype xsd:string`, `sh:minCount 1 ; sh:maxCount 1`, `sh:datatype xsd:integer ; sh:minInclusive 0`, `sh:minCount 1 ; sh:class :Doctor`.
- Duyệt từng bệnh nhân, đối chiếu với từng ràng buộc.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

```turtle
@prefix :    <http://hospital.vn/exam#> .
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:PatientShape a sh:NodeShape ;
    sh:targetClass :Patient ;
    sh:property [ sh:path :name ; sh:datatype xsd:string ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path :age ; sh:datatype xsd:integer ; sh:minInclusive 0 ] ;
    sh:property [ sh:path :treatedBy ; sh:minCount 1 ; sh:class :Doctor ] .
```
- **Nút được kiểm:** `:minh, :hoa, :nam, :binh` (có `a :Patient`).
- **Vi phạm:**
  - `:nam`: thiếu `:treatedBy` (minCount 1).
  - `:binh`: thiếu `:name` (minCount 1).
- `:minh` và `:hoa` hợp lệ: lan và hai đều có `a :Doctor`; tuổi là số nguyên không âm.
- **Đề xuất sửa:** `:nam :treatedBy :quang .` và `:binh :name "Bình" .`

- [ ] Shape đúng 3 property (0.5đ)
- [ ] Nút được kiểm + 2 vi phạm đúng (0.25đ)
- [ ] Đề xuất sửa (0.25đ)

</details>

### Câu 8 (1 điểm) · [D11]
a) Một bộ-3 RDF gồm những thành phần nào? Mỗi vị trí (chủ thể, vị từ, tân ngữ) được nhận những loại term nào?
b) Cho câu "Bác sĩ Lan điều trị bệnh nhân Minh". Viết nó theo 3 cách serialization (N-Triples, Turtle, RDF/XML) và nêu khi nào cần dùng blank node.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- a) Trình bày bảng 3 cột S/P/O × IRI / blank / literal.
- b) Viết N-Triples với IRI đầy đủ; Turtle dùng prefix; RDF/XML dùng `rdf:Description rdf:about`.

</details>

<details class="ans"><summary>Đáp án + barem</summary>

a) Bộ-3 = (chủ thể, vị từ, tân ngữ).

| Vị trí | IRI | Blank node | Literal |
|---|---|---|---|
| Chủ thể (S) | có | có | không |
| Vị từ (P) | có | không | không |
| Tân ngữ (O) | có | có | có: literal thường, có thẻ ngôn ngữ `"..."@vi`, có kiểu `"35"^^xsd:integer` |

Các khả năng tổ hợp: S ∈ {IRI, blank}, P = IRI, O ∈ {IRI, blank, literal thường, literal @ngôn ngữ, literal ^^kiểu}. Tổng cộng **2 × 1 × 5 = 10** kiểu bộ-3 (giống trang D1/D11; nếu gộp 3 kiểu literal làm một thì là 2 × 1 × 3 = 6 tổ hợp loại term).

b)
```text
<http://hospital.vn/exam#lan> <http://hospital.vn/exam#treats> <http://hospital.vn/exam#minh> .
```
```turtle
@prefix : <http://hospital.vn/exam#> .
:lan :treats :minh .
```
```text
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:h="http://hospital.vn/exam#">
  <rdf:Description rdf:about="http://hospital.vn/exam#lan">
    <h:treats rdf:resource="http://hospital.vn/exam#minh"/>
  </rdf:Description>
</rdf:RDF>
```
Khi nào dùng blank node:
- tài nguyên không cần hoặc không có tên (ví dụ "một con rồng", "một người nào đó");
- nút trung gian của quan hệ n-ngôi (địa chỉ, điểm số, lần khám);
- nút của collection, nút `rdf:Statement` khi reification.

Lưu ý: blank node không tham chiếu được từ bên ngoài đồ thị.

- [ ] a) bảng vị trí đúng (0.5đ)
- [ ] b) 3 serialization đúng (0.25đ)
- [ ] b) nêu ≥2 trường hợp blank node (0.25đ)

</details>
