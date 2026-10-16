## Đề cũ có lời giải

Ba đề thi cũ dưới đây đều có khung chung: **RDF/Turtle + đồ thị → RDFS/OWL + DL → suy diễn → SPARQL + đại số → SHACL**. Mỗi đề cũ có **5 câu** (nhiều ý nhỏ, đề không in điểm, ≈ 2 điểm/câu; nghe nói câu truy vấn SPARQL 2.5 điểm); các đề luyện của trang này chia thành 8 câu chỉ để luyện, còn câu thi thật vẫn rơi vào đúng những dạng này. Hãy luyện theo thứ tự: đọc đề, tự làm ra giấy, mở **Gợi ý** rồi mới mở **Đáp án**.

Các lời giải của đề 2023-3 và 2022-1 được trình bày **theo lời giải tham chiếu của thầy**, có sửa vài lỗi gõ. Đề 6390-20231 không có lời giải tham chiếu nên được giải đầy đủ ở đây. Mọi truy vấn SPARQL đã được chạy thử bằng rdflib và bảng kết quả khớp.

---

## Đề 2023-3

### 2023-3 · Câu 1 — Turtle + đồ thị RDF
> **Dạng:** D1 · **Nguồn:** 2023-C1

*Tạo dữ liệu RDF theo cú pháp Turtle biểu diễn các thông tin, sau đó vẽ đồ thị RDF tương ứng:*

Học phần The Semantic Web có danh mục sách tham khảo bao gồm: Foundations of Semantic Web Technologies, Learning SPARQL, Semantic Web for the Working Ontologist. Sinh viên Nguyễn Văn A đã đạt điểm 10 học phần này. Thầy giáo nhận xét Nguyễn Văn A là 1 sinh viên xuất sắc.

*!Lưu ý: Tự tạo IRI cho các thành phần (khóa học, sách và sinh viên), chỉ viết không quá 20 bộ-3 cơ bản/20 cạnh đồ thị RDF.*

<details class="hint"><summary>Gợi ý / Khuôn</summary>

Tách đề thành 3 mệnh đề và chọn cấu trúc theo **dấu hiệu** của từng mệnh đề:

| Cụm từ trong đề | Cấu trúc RDF |
|---|---|
| "danh mục … **bao gồm** A, B, C" (một danh sách) | **collection** `( :a :b :c )` → bung thành rdf:first / rdf:rest / rdf:nil |
| "đạt **điểm 10** học phần này" (quan hệ 3 ngôi: SV – điểm – học phần) | **blank node n-ngôi** `:score [ :value 10 ; :course :sw_course ]` |
| "Thầy giáo **nhận xét** A là …" (một câu nói *về* một câu khác) | **reification** `[ a rdf:Statement ; rdf:subject … ; rdf:predicate … ; rdf:object … ]` |
| "thầy giáo" không có tên | blank node `[ a :Teacher ]` |

Cách đếm triple: mỗi cạnh trên đồ thị là 1 triple. Collection 3 phần tử tốn 6 cạnh (3 first + 3 rest). Đề giới hạn 20 cạnh, lời giải dưới đây dùng 19 cạnh.

Quy ước vẽ: **IRI vẽ hình elip có tên**, **blank node vẽ elip rỗng**, **literal vẽ hình chữ nhật**, cạnh là mũi tên có nhãn predicate.

</details>

<details class="ans"><summary>Đáp án</summary>

```turtle graph
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:sw_course :ref (:foswt :learning_sparql :sw_ontologist) ;
    rdfs:label "The Semantic Web" .
:nva a :Student ;
    :score [ :value 10 ; :course :sw_course ] .
[ a :Teacher ; :course :sw_course ] :comment [ a rdf:Statement ;
    rdf:subject :nva ; rdf:predicate rdf:type ; rdf:object :ExcellentStudent ] .
```

Giải thích để ăn điểm:
- `:ref ( … )`: danh sách sách tham khảo là **đóng và có thứ tự**, nên dùng collection. Đồ thị vẽ thành chuỗi blank node nối bằng `rdf:first` / `rdf:rest`, kết thúc ở `rdf:nil`.
- `:score [ :value 10 ; :course :sw_course ]`: điểm là quan hệ 3 ngôi (sinh viên, giá trị, học phần), nên dùng một blank node trung gian.
- Nhận xét của thầy là một mệnh đề nói **về mệnh đề** "nva là ExcellentStudent", nên dùng reification `rdf:Statement`. Thầy là blank node vì đề không cho tên.
- Nếu muốn ghi rõ tên sách, có thể thêm `:foswt rdfs:label "Foundations of Semantic Web Technologies"`. Làm vậy thì tốn thêm cạnh, phải đếm lại để không vượt 20 cạnh.

</details>

### 2023-3 · Câu 2 — RDFS + OWL + DL (phương tiện giao thông)
> **Dạng:** D5 · **Nguồn:** 2023-C2

*Định nghĩa các lớp và các thuộc tính dựa trên RDF, RDFS và OWL sử dụng cú pháp Turtle.*
Các lớp: Phương tiện giao thông, phương tiện đường bộ, phương tiện đường thủy, phương tiện đường không, đường giao thông, phương tiện lưỡng cư. Các thuộc tính: Vận hành, nhiên liệu. *(Được tùy ý bổ sung các lớp và các thuộc tính cần thiết.)*

a) Phương tiện giao thông đường bộ, phương tiện giao thông đường thủy, và phương tiện giao thông đường hàng không là các loại phương tiện giao thông. Đường giao thông là tên gọi chung cho đường bộ, đường thủy, đường hàng không.
b) Thuộc tính vận hành có miền là phương tiện giao thông và khoảng là đường giao thông. Thuộc tính nhiên liệu có miền là phương tiện giao thông, và giá trị có thể là xăng, dầu, hoặc điện.
c) Phương tiện lưỡng cư là phương tiện thuộc 2 lớp nhưng không bắt buộc phải đúng 2 lớp. *(Ví dụ: dựa trên các dữ kiện Amphicar vừa là Phương tiện đường bộ vừa là Phương tiện đường thủy có thể suy ra nó là Phương tiện lưỡng cư, không phụ thuộc vào việc nó có thể bay hay không.)*
d) Biểu diễn lớp Phương tiện lưỡng cư, các thuộc tính vận hành, nhiên liệu bằng các biểu thức DL.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

| Câu trong đề | Cấu trúc |
|---|---|
| "X, Y, Z là **các loại** W" | `X rdfs:subClassOf W` (mỗi lớp một triple) |
| "W là **tên gọi chung** cho X, Y, Z" | `W owl:equivalentClass [ owl:unionOf (X Y Z) ]` (DL: W ≡ X ⊔ Y ⊔ Z) |
| "miền / khoảng" | `rdfs:domain` / `rdfs:range` (DL: ∃p.⊤ ⊑ D, ⊤ ⊑ ∀p.R) |
| "giá trị **có thể là** a, b, c" | range là lớp liệt kê `[ owl:oneOf (:a :b :c) ]` |
| "thuộc **(ít nhất) 2 trong 3 lớp**" | **hợp của các giao từng cặp**: (A⊓B) ⊔ (A⊓C) ⊔ (B⊓C) |

Phải dùng `≡` (owl:equivalentClass, hoặc unionOf đặt trực tiếp như lời giải của thầy) chứ không dùng `⊑`. Lý do: đề yêu cầu **suy ra được** Amphicar là lưỡng cư, mà muốn suy theo chiều "đủ điều kiện ⇒ thuộc lớp" thì định nghĩa phải là tương đương.

</details>

<details class="ans"><summary>Đáp án</summary>

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
# a)
:Phương_Tiện_Đường_Bộ rdfs:subClassOf :Phương_Tiện_Giao_Thông .
:Phương_Tiện_Đường_Thủy rdfs:subClassOf :Phương_Tiện_Giao_Thông .
:Phương_Tiện_Đường_Không rdfs:subClassOf :Phương_Tiện_Giao_Thông .
:Đường_Giao_Thông owl:unionOf (:Đường_Bộ :Đường_Thủy :Đường_Không) .
# b)
:vận_hành rdfs:domain :Phương_Tiện_Giao_Thông ; rdfs:range :Đường_Giao_Thông .
:nhiên_liệu rdfs:domain :Phương_Tiện_Giao_Thông ;
    rdfs:range [ owl:oneOf (:xăng :dầu :điện) ] .
# c)
:Phương_Tiện_Lưỡng_Cư owl:unionOf (
    [ owl:intersectionOf (:Phương_Tiện_Đường_Bộ :Phương_Tiện_Đường_Thủy) ]
    [ owl:intersectionOf (:Phương_Tiện_Đường_Bộ :Phương_Tiện_Đường_Không) ]
    [ owl:intersectionOf (:Phương_Tiện_Đường_Thủy :Phương_Tiện_Đường_Không) ] ) .
```

Muốn viết chuẩn OWL 2 DL hơn thì khai báo kiểu và dùng `owl:equivalentClass`. Hai cách đều được chấp nhận:

```turtle
:Phương_Tiện_Lưỡng_Cư a owl:Class ; owl:equivalentClass [ a owl:Class ; owl:unionOf ( … như trên … ) ] .
:vận_hành a owl:ObjectProperty .  :nhiên_liệu a owl:ObjectProperty .
:xăng a :Nhiên_Liệu . :dầu a :Nhiên_Liệu . :điện a :Nhiên_Liệu .
```

**d) Biểu thức DL**

```text
Phương_Tiện_Lưỡng_Cư ≡ (Phương_Tiện_Đường_Bộ ⊓ Phương_Tiện_Đường_Thủy)
                     ⊔ (Phương_Tiện_Đường_Bộ ⊓ Phương_Tiện_Đường_Không)
                     ⊔ (Phương_Tiện_Đường_Thủy ⊓ Phương_Tiện_Đường_Không)
∃vận_hành.⊤ ⊑ Phương_Tiện_Giao_Thông        (miền)
⊤ ⊑ ∀vận_hành.Đường_Giao_Thông               (khoảng)
∃nhiên_liệu.⊤ ⊑ Phương_Tiện_Giao_Thông      (miền)
⊤ ⊑ ∀nhiên_liệu.{xăng, dầu, điện}           (khoảng)
```

**Lưu ý:** bản lời giải tham chiếu gõ nhầm khoảng của vận_hành thành `∀vận_hành.Phương_Tiện_Giao_Thông`. Khoảng đúng là **Đường_Giao_Thông**, như ghi ở trên.

Kiểm tra với ví dụ trong đề: Amphicar ∈ Bộ ⊓ Thủy, nên Amphicar thuộc vế phải của hợp, và vì có ≡ nên suy ra Amphicar ∈ Lưỡng_Cư. Kết luận này không phụ thuộc Amphicar có bay được hay không.

</details>

### 2023-3 · Câu 3 — Datalog: cây chứng minh + điểm cố định
> **Dạng:** D7 · **Nguồn:** 2023-C3

Cho chương trình Datalog:
```text
Đường-một-chiều(A, B)
Đường-một-chiều(B, C)
Đường-hai-chiều(D, C)
Đường-hai-chiều(Y, X) ← Đường-hai-chiều(X, Y)
Có-đường-đi(X, Y) ← Đường-hai-chiều(X, Y)
Có-đường-đi(X, Y) ← Đường-một-chiều(X, Y)
Có-đường-đi(X, Z) ← Có-đường-đi(X, Y) ∧ Có-đường-đi(Y, Z)
```
a) Hãy vẽ cây chứng minh cho khẳng định Có-đường-đi(A, D).
b) Tìm điểm cố định của tiến trình suy diễn — viết chi tiết các bước mở rộng tập dữ kiện.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- **Cây chứng minh:** gốc là mệnh đề cần chứng minh. Mỗi nút được chọn một luật có **đầu (head)** khớp với nó, sau đó vẽ các mệnh đề trong **thân (body)** làm con. Đi xuống cho tới khi lá đều là **dữ kiện** có sẵn trong B0.
- **Điểm cố định:** bắt đầu từ B0 là tập dữ kiện. Ở mỗi bước, áp dụng **mọi luật** lên **toàn bộ tập của bước trước** và ghi lại các dữ kiện **mới**. Dừng khi một bước không thêm được dữ kiện nào; tập ở bước cuối có thêm dữ kiện chính là điểm cố định.
- Chi tiết hơn xem tab **D7 Datalog**.

</details>

<details class="ans"><summary>Đáp án</summary>

**a) Cây chứng minh**

```text
                         Có-đường-đi(A, D)
                  ┌──────────────┴───────────────┐
         Có-đường-đi(A, C)                  Có-đường-đi(C, D)
        ┌────────┴─────────┐                        │
Có-đường-đi(A, B)   Có-đường-đi(B, C)        Đường-hai-chiều(C, D)
        │                  │                        │
Đường-một-chiều(A,B) Đường-một-chiều(B,C)   Đường-hai-chiều(D, C)
```

Tên luật dùng ở từng nút:
- Gốc và nút (A,C) dùng luật bắc cầu `Có-đường-đi(X,Z) ← Có-đường-đi(X,Y) ∧ Có-đường-đi(Y,Z)`.
- Các nút (A,B) và (B,C) dùng luật `Có-đường-đi ← Đường-một-chiều`.
- Nút (C,D) dùng luật `Có-đường-đi ← Đường-hai-chiều`.
- Đường-hai-chiều(C,D) suy ra từ Đường-hai-chiều(D,C) nhờ luật đối xứng.

**b) Điểm cố định**

```text
B0: {Đường-một-chiều(A, B), Đường-một-chiều(B, C), Đường-hai-chiều(D, C)}
B1: + {Đường-hai-chiều(C, D), Có-đường-đi(A, B), Có-đường-đi(B, C), Có-đường-đi(D, C)}
B2: + {Có-đường-đi(C, D), Có-đường-đi(A, C)}
B3: + {Có-đường-đi(B, D), Có-đường-đi(A, D), Có-đường-đi(C, C), Có-đường-đi(D, D)}
B4: + {}  (không có dữ kiện mới)
```

Điểm cố định thu được ở **Bước 3**. Tập điểm cố định gồm 3 dữ kiện ban đầu, 1 Đường-hai-chiều mới và 9 Có-đường-đi: AB, BC, DC, CD, AC, BD, AD, CC, DD.

Kiểm tra B4: từ A đi tới được B, C, D; từ B tới C, D; từ C tới C, D; từ D tới C, D. Mọi cặp bắc cầu đều đã có trong tập, nên B4 rỗng. Không suy ra được Có-đường-đi(A,A) vì không có đường nào quay về A.

</details>

### 2023-3 · Câu 4 — SPARQL + đại số (máy bay)
> **Dạng:** D8 + D9 · **Nguồn:** 2023-C4

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:Caspar a :Seaplane; :crew 2; :flight 1900.
:Convair a :Seaplane; :crew 1; :flight 1953.
:Su27 a :JetFighter; :crew 1.
:Mig35 a :JetFighter; :speed 2400.
:Mi26 a :Helicopter; :speed 295; :crew 5; :flight 1983; rdfs:label "Mil Mi-26".
```
a) Viết 1 truy vấn SPARQL tìm các dòng thủy phi cơ (:Seaplane) và các dòng trực thăng (:Helicopter). Dữ liệu đầu ra phải chứa IRI của dòng máy bay, và nhãn (rdfs:label) của nó nếu có hoặc bỏ trống nếu không.
b) Viết biểu thức đại số SPARQL tương ứng với yêu cầu truy vấn ở mục a, sau đó giải thích chi tiết từng bước thực hiện và các kết quả thu được.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Cụm "**A và B**" ở đây nghĩa là lấy cả hai loại, tức là phép **hoặc** trên kiểu. Viết bằng `FILTER (?t = :A || ?t = :B)` hoặc bằng `{…} UNION {…}`.
- Cụm "**nếu có, bỏ trống nếu không**" thì dùng `OPTIONAL`.
- Dịch sang đại số: `OPTIONAL` thành **LeftJoin**. `FILTER` bọc **ngoài toàn bộ nhóm** chứa nó, kể cả khi nó được viết ở cuối nhóm.

</details>

<details class="ans"><summary>Đáp án</summary>

**a)**
```sparql
PREFIX : <http://semweb.edu.vn/exam#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT *
WHERE {
  { ?p a ?t } OPTIONAL { ?p rdfs:label ?label }
  FILTER (?t = :Seaplane || ?t = :Helicopter)
}
```
Viết cách khác cũng đúng: `SELECT ?p ?label WHERE { {?p a :Seaplane} UNION {?p a :Helicopter} OPTIONAL {?p rdfs:label ?label} }`.

**b) Biểu thức đại số**
```text
Filter( (?t = :Seaplane || ?t = :Helicopter),
        LeftJoin( BGP(?p a ?t), BGP(?p rdfs:label ?label) ) )
```

**Các bước thực hiện**

Bước 1. BGP(?p a ?t) cho 5 lời giải:

| ?p | ?t |
|---|---|
| :Caspar | :Seaplane |
| :Convair | :Seaplane |
| :Su27 | :JetFighter |
| :Mig35 | :JetFighter |
| :Mi26 | :Helicopter |

Bước 2. BGP(?p rdfs:label ?label) cho 1 lời giải:

| ?p | ?label |
|---|---|
| :Mi26 | "Mil Mi-26" |

Bước 3. LeftJoin giữ **mọi** dòng của vế trái. Dòng nào có dòng tương thích ở vế phải (cùng giá trị ?p) thì được ghép thêm ?label:

| ?p | ?t | ?label |
|---|---|---|
| :Caspar | :Seaplane | |
| :Convair | :Seaplane | |
| :Su27 | :JetFighter | |
| :Mig35 | :JetFighter | |
| :Mi26 | :Helicopter | "Mil Mi-26" |

Bước 4. Filter chỉ giữ những dòng có ?t = :Seaplane hoặc ?t = :Helicopter, tức là loại 2 dòng JetFighter. Đây cũng là **kết quả truy vấn**:

| ?p | ?t | ?label |
|---|---|---|
| :Caspar | :Seaplane | |
| :Convair | :Seaplane | |
| :Mi26 | :Helicopter | "Mil Mi-26" |

</details>

### 2023-3 · Câu 5 — SHACL
> **Dạng:** D10 · **Nguồn:** 2023-C5

Tạo các khuôn hình SHACL biểu diễn các ràng buộc cho dữ liệu trong câu 4:
a) Giá trị của thuộc tính năm cất cánh đầu tiên (:flight) của các dòng thủy phi cơ phải > 1900.
b) Dữ liệu về các dòng máy bay chiến đấu phản lực (:JetFighter) phải có các thuộc tính :crew và :speed.
*Gợi ý của đề: a) sh:minExclusive  b) sh:minCount*

<details class="hint"><summary>Gợi ý / Khuôn</summary>

```text
:TênShape a sh:NodeShape ;
    sh:targetClass :Lớp ;                 # chọn những nút cần kiểm tra
    sh:property [ sh:path :thuộc_tính ;   # thuộc tính bị ràng buộc
                  <ràng buộc> giá_trị ] .
```

Đề nói "> 1900" (lớn hơn hẳn) thì dùng `sh:minExclusive 1900`. Nếu đề nói "≥ 1900" thì dùng `sh:minInclusive`.

Đề nói "phải có" một thuộc tính thì dùng `sh:minCount 1`. Đề đòi 2 thuộc tính thì viết 2 khối `sh:property` riêng.

</details>

<details class="ans"><summary>Đáp án</summary>

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
:SeaPlaneShape a sh:NodeShape ;
    sh:targetClass :Seaplane ;
    sh:property [
        sh:path :flight ;
        sh:minExclusive 1900
    ] .

:JetFighterShape a sh:NodeShape ;
    sh:targetClass :JetFighter ;
    sh:property [ sh:path :crew ;  sh:minCount 1 ] ;
    sh:property [ sh:path :speed ; sh:minCount 1 ] .
```

**Kết quả kiểm tra (nên ghi thêm để ăn điểm trọn):**
- `:SeaPlaneShape` kiểm tra 2 nút :Caspar và :Convair. **:Caspar vi phạm** vì 1900 không lớn hơn hẳn 1900. :Convair (1953) đạt.
- `:JetFighterShape` kiểm tra 2 nút :Su27 và :Mig35. **:Su27 vi phạm** vì thiếu :speed. **:Mig35 vi phạm** vì thiếu :crew.

</details>

---

## Đề 5390-2022-1

### 2022-1 · Câu 1 — Đồ thị RDF + Turtle (sách Design Patterns)
> **Dạng:** D1 · **Nguồn:** 2022-C1

*Vẽ đồ thị RDF và viết các bộ-3 theo cú pháp Turtle biểu diễn thông tin trong mô tả sau:* Sách Design Patterns: Elements of Reusable Object-Oriented Software được viết bởi 1 nhóm tác giả bao gồm Erich Gamma, Richard Helm, Ralph Johnson và John Vlissides. Nguyễn Văn A cảm thấy đây là 1 cuốn sách hay.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- "**nhóm tác giả bao gồm** …" là danh sách có thứ tự, đóng, nên dùng collection `( … )`.
- "**A cảm thấy** đây là 1 cuốn sách hay" là ý kiến của A về một mệnh đề, nên dùng reification: mệnh đề (sách, rdf:type, :GoodBook) được bọc trong một `rdf:Statement`.
- Mỗi người được đặt một IRI và gắn `b:name` dạng literal. Sách được gắn `a b:Book` và `b:title`.

</details>

<details class="ans"><summary>Đáp án</summary>

```turtle graph
@prefix b: <http://exam.hust.edu.vn/book/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
b:nguyen-van-a b:name "Nguyễn Văn A" ;
    b:feels [ a rdf:Statement ;
              rdf:subject b:design-patterns ;
              rdf:predicate rdf:type ;
              rdf:object b:GoodBook ] .
b:design-patterns a b:Book ;
    b:title "Design Patterns: Elements of Reusable Object-Oriented Software" ;
    b:writtenBy (b:erich-gamma b:richard-helm b:ralph-johnson b:john-vlissides) .
b:erich-gamma b:name "Erich Gamma" .
b:richard-helm b:name "Richard Helm" .
b:ralph-johnson b:name "Ralph Johnson" .
b:john-vlissides b:name "John Vlissides" .
```

Trên đồ thị, `b:writtenBy` trỏ tới blank node đầu tiên của chuỗi 4 nút. Mỗi nút có `rdf:first` trỏ tới một tác giả và `rdf:rest` trỏ tới nút tiếp theo, nút cuối có `rdf:rest` trỏ tới `rdf:nil`. Mỗi tác giả có thêm cạnh `b:name` trỏ tới một literal (hình chữ nhật).

</details>

### 2022-1 · Câu 2 — Suy diễn RDFS
> **Dạng:** D4 · **Nguồn:** 2022-C2

*Hãy viết 4 bộ-3 có thể được suy ra dựa trên CSTT như sau trong phạm vi ngữ nghĩa RDFS và giải thích các bộ-3 là cơ sở của các suy diễn đó:*
```turtle
@prefix : <http://exam.hust.edu.vn/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:a :r :b.
:c a :C.
:r rdfs:range :C; rdfs:domain :D.
:C rdfs:subClassOf :E.
:D rdfs:subClassOf :F.
```

<details class="hint"><summary>Gợi ý / Khuôn</summary>

Viết theo mẫu `triple suy ra  <=  triple cơ sở 1.  triple cơ sở 2.  (tên luật)`. Các luật hay dùng:
- **rdfs2 (domain):** `x p y` và `p domain D` cho ra `x a D`.
- **rdfs3 (range):** `x p y` và `p range R` cho ra `y a R`.
- **rdfs9 (subClass):** `x a C` và `C subClassOf E` cho ra `x a E`.

Đề yêu cầu 4 triple, nhưng nên viết cả 5 để chắc điểm.

</details>

<details class="ans"><summary>Đáp án</summary>

```text
:a a :D.  <=  :a :r :b.   :r rdfs:domain :D.        (rdfs2)
:a a :F.  <=  :a a :D.    :D rdfs:subClassOf :F.    (rdfs9)
:c a :E.  <=  :c a :C.    :C rdfs:subClassOf :E.    (rdfs9)
:b a :C.  <=  :a :r :b.   :r rdfs:range :C.         (rdfs3)
:b a :E.  <=  :b a :C.    :C rdfs:subClassOf :E.    (rdfs9)
```

Các triple suy ra được nhưng tầm thường (vẫn đúng, chỉ nên ghi thêm): `:r a rdf:Property` (rdf1), `:C a rdfs:Class` (rdfs2 + tiên đề `rdfs:subClassOf rdfs:domain rdfs:Class`), `:C rdfs:subClassOf :C` (rdfs10).

</details>

### 2022-1 · Câu 3 — RDFS hay OWL? (Molly là mèo, Spot thì không)
> **Dạng:** D6 · **Nguồn:** 2022-C3

```turtle
@prefix bio: <http://exam.hust.edu.vn/bio/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
bio:offspring rdfs:domain bio:Animal; rdfs:range bio:Animal .
bio:Fido a bio:Dog; bio:offspring bio:Spot.
bio:Milo a bio:Cat; bio:offspring bio:Molly.
```
Trong tầng ngữ nghĩa nào (RDFS hay OWL) có thể bổ sung các ràng buộc để có thể suy diễn Molly là mèo, nhưng không suy ra Spot là mèo? Hãy bổ sung các ràng buộc đó.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Trong RDFS, khoảng (range) của một thuộc tính là **toàn cục**: mọi giá trị của thuộc tính đều thuộc lớp đó, không phân biệt chủ thể là ai. Nếu đặt range là Cat thì Spot cũng thành mèo. Vậy **RDFS không làm được**.
- OWL có **restriction gắn vào lớp**, ví dụ "con của mèo là mèo". Có hai cách làm:
  1. dùng thuộc tính ngược `sprungBy` kèm `allValuesFrom`;
  2. viết `Cat ⊑ ∀offspring.Cat`.

</details>

<details class="ans"><summary>Đáp án</summary>

**Lựa chọn: OWL.**

Với CSTT đã cho, trong phạm vi RDFS chỉ suy ra được Molly và Spot là động vật. Nếu đổi khoảng của offspring thành Cat thì suy ra **cả** Molly và Spot là mèo. RDFS không cho phép ràng buộc khoảng theo miền, nên không biểu diễn được yêu cầu đề bài.

OWL cho phép định nghĩa lớp dựa trên giới hạn giá trị thuộc tính. Lời giải tham chiếu như sau:
```turtle
@prefix bio: <http://exam.hust.edu.vn/bio/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
bio:sprungBy owl:inverseOf bio:offspring .
bio:Cat owl:equivalentClass [ a owl:Restriction ;
    owl:onProperty bio:sprungBy ; owl:allValuesFrom bio:Cat ] .
```

Cách khác ngắn hơn, cũng đúng:
```turtle
bio:Cat rdfs:subClassOf [ a owl:Restriction ; owl:onProperty bio:offspring ; owl:allValuesFrom bio:Cat ] .
```
Viết bằng DL: Cat ⊑ ∀offspring.Cat. Milo ∈ Cat và (Milo, Molly) ∈ offspring nên Molly ∈ Cat. Không có dữ kiện Fido là Cat (Fido là Dog), nên không suy ra gì về Spot.

**Lưu ý về cách của thầy** (Cat ≡ ∀sprungBy.Cat): chiều ⊒ cho rằng nếu mọi cha/mẹ đều là mèo thì là mèo. Dưới giả thiết thế giới mở, không thể biết Molly chỉ có duy nhất Milo là cha/mẹ, nên chiều này **không tự suy ra** Molly là mèo. Vì vậy khi đi thi nên ghi **cả hai cách**, hoặc dùng cách ∀offspring cho chắc.

</details>

### 2022-1 · Câu 4 — DL + RDFS/OWL (thú cưng)
> **Dạng:** D5 · **Nguồn:** 2022-C4

Biểu diễn các khái niệm theo mô tả sau: *Thú cưng gồm có chó và mèo và không có thú cưng nào vừa là chó và vừa là mèo.* a) Bằng DL. b) Bằng RDFS, OWL sử dụng Turtle.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- "**gồm có** chó và mèo" nghĩa là chó và mèo là lớp con của thú cưng (⊑). Nếu hiểu chặt hơn là "chỉ gồm" thì viết Pet ≡ Dog ⊔ Cat.
- "**không có** cái nào vừa là A vừa là B" nghĩa là A ⊓ B ⊑ ⊥, tức là `owl:disjointWith`.

</details>

<details class="ans"><summary>Đáp án</summary>

a) DL:
```text
Dog ⊑ Pet
Cat ⊑ Pet
Dog ⊓ Cat ⊑ ⊥
```
b) Turtle:
```turtle
@prefix bio: <http://exam.hust.edu.vn/bio/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
bio:Cat rdfs:subClassOf bio:Pet .
bio:Dog rdfs:subClassOf bio:Pet .
bio:Cat owl:disjointWith bio:Dog .
```
Có thể viết theo cách khác, ví dụ `bio:Pet owl:equivalentClass [ owl:unionOf (bio:Dog bio:Cat) ]`, tương ứng Pet ≡ Dog ⊔ Cat, nếu hiểu thú cưng **chỉ** gồm chó và mèo.

</details>

### 2022-1 · Câu 5 — SPARQL + đại số (mèo của Anna)
> **Dạng:** D8 + D9 · **Nguồn:** 2022-C5

```turtle
@prefix bio: <http://exam.hust.edu.vn/bio/> .
bio:Fido a bio:Dog; bio:offspring bio:Spot, bio:Ted.
bio:Milo a bio:Cat; bio:offspring bio:Kitty.
bio:Anna bio:own bio:Fido, bio:Milo.
```
a) Hãy viết 1 truy vấn SPARQL xuất danh sách những con mèo của Anna, bao gồm cả những con mèo mà Anna sở hữu và cả con của chúng.
b) Viết biểu thức đại số SPARQL tương ứng với truy vấn ở mục a và giải thích chi tiết từng bước thực hiện.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

Đề nói "**bao gồm cả** A **và cả** B" nghĩa là kết quả là hợp của hai nhóm, nên dùng `UNION`:
- nhánh 1: mèo Anna sở hữu;
- nhánh 2: con của mèo Anna sở hữu.

Dịch sang đại số: `Project( Union( BGP1, BGP2 ), {?pet} )`.

</details>

<details class="ans"><summary>Đáp án</summary>

a)
```sparql
PREFIX bio: <http://exam.hust.edu.vn/bio/>
SELECT ?pet
WHERE {
  { bio:Anna bio:own ?pet . ?pet a bio:Cat . }
  UNION
  { bio:Anna bio:own ?x . ?x a bio:Cat . ?x bio:offspring ?pet . }
}
```
b) Biểu thức đại số:
```text
Project( Union( BGP(bio:Anna bio:own ?pet . ?pet a bio:Cat .),
                BGP(bio:Anna bio:own ?x . ?x a bio:Cat . ?x bio:offspring ?pet .) ),
         {?pet} )
```
Bước 1. BGP(bio:Anna bio:own ?pet . ?pet a bio:Cat .). Anna sở hữu Fido và Milo, trong đó chỉ Milo là Cat:

| ?pet |
|---|
| bio:Milo |

Bước 2. BGP(bio:Anna bio:own ?x . ?x a bio:Cat . ?x bio:offspring ?pet .):

| ?x | ?pet |
|---|---|
| bio:Milo | bio:Kitty |

Bước 3. Union({μ1: ?pet→bio:Milo}, {μ2: ?x→bio:Milo, ?pet→bio:Kitty}):

| ?x | ?pet |
|---|---|
| | bio:Milo |
| bio:Milo | bio:Kitty |

Bước 4. Project lên biến ?pet:

| ?pet |
|---|
| bio:Milo |
| bio:Kitty |

Kết quả gồm 2 tài nguyên là bio:Milo và bio:Kitty. Đã chạy thử bằng rdflib, kết quả khớp.

</details>

---

## Đề 6390-20231 (không có lời giải tham chiếu, lời giải tự soạn)

### 6390 · Câu 1 — Turtle + đồ thị (C++)
> **Dạng:** D1 · **Nguồn:** 6390-C1

Hãy tạo biểu diễn RDF bằng Turtle và vẽ đồ thị RDF tương ứng cho những nội dung sau:
(a) C++ là 1 ngôn ngữ lập trình, được sáng tạo bởi Bjarne Stroustrup.
(b) An (1 sinh viên giả định) nghĩ rằng C++ rất thú vị và tương đối dễ học.
(c) Theo chỉ số TIOBE C, C++, Python, Java đang là những ngôn ngữ được sử dụng phổ biến nhất.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- (a) Có 2 sự kiện đơn: kiểu của C++ và người tạo ra C++. Nên thêm **kiểu cho mọi thực thể** (Bjarne a :Person) và **nhãn/tên dạng literal**. Theo ghi chú của bạn: liệt kê **đủ** các triple.
- (b) "An **nghĩ rằng** …" là ý kiến về các mệnh đề, nên dùng **reification**. Có 2 ý ("thú vị", "dễ học"), mỗi ý là một `rdf:Statement`.
- (c) Danh sách **có thứ tự** (xếp hạng) lấy từ một **nguồn** (TIOBE), nên dùng collection `( :C :CPP :Python :Java )` gắn vào một nút bảng xếp hạng. Cách khác: dùng `rdf:Seq` với rdf:_1 … rdf:_4.

</details>

<details class="ans"><summary>Đáp án</summary>

(a)
```turtle graph
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:CPP a :ProgrammingLanguage ;
    rdfs:label "C++" ;
    :createdBy :bjarne_stroustrup .
:bjarne_stroustrup a :Person ;
    :name "Bjarne Stroustrup" .
```

(b)
```turtle graph
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
:an a :Student ; :name "An" ;
    :thinks [ a rdf:Statement ;
              rdf:subject :CPP ; rdf:predicate rdf:type ; rdf:object :InterestingLanguage ] ,
            [ a rdf:Statement ;
              rdf:subject :CPP ; rdf:predicate :learningDifficulty ; rdf:object :RelativelyEasy ] .
```

(c)
```turtle graph
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:tiobe_index a :Ranking ;
    rdfs:label "TIOBE index" ;
    :mostPopular (:C :CPP :Python :Java) .
```

Giải thích:
- (b) không được viết thẳng `:CPP a :InterestingLanguage`. Viết như vậy là khẳng định một **sự thật**, trong khi đề chỉ nói đó là **ý kiến của An**. Phải dùng reification.
- (c) collection giữ được **thứ tự** xếp hạng và là danh sách **đóng** (đúng 4 ngôn ngữ). Nếu muốn có thể thêm `:C a :ProgrammingLanguage .` cho cả 4 ngôn ngữ.

Cách viết khác cho (c) bằng container:
```turtle
:tiobe_index :mostPopular [ a rdf:Seq ; rdf:_1 :C ; rdf:_2 :CPP ; rdf:_3 :Python ; rdf:_4 :Java ] .
```

</details>

### 6390 · Câu 2 — RDFS + OWL (phần mềm C++)
> **Dạng:** D5 · **Nguồn:** 6390-C2

Hãy tạo biểu diễn cho các khái niệm sau bằng RDFS và OWL, sử dụng định dạng Turtle:
a. Phụ thuộc (giữa các gói phần mềm) là 1 thuộc tính đối tượng có tính chất bắc cầu.
b. Phụ thuộc tương đương với sử dụng.
c. Trình biên dịch C++ gồm có g++, clang++, msvc.
d. Chương trình C++ là những chương trình được viết bằng ngôn ngữ C++ và được biên dịch bằng trình biên dịch C++.
e. Chương trình đa nền tảng là chương trình có thể hoạt động tối thiểu trên 2 hệ điều hành khác nhau.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

| Câu | Cấu trúc OWL | DL |
|---|---|---|
| bắc cầu | `owl:ObjectProperty, owl:TransitiveProperty` + domain/range | Trans(phụThuộc) |
| tương đương (thuộc tính) | `owl:equivalentProperty` | phụThuộc ≡ sửDụng |
| "gồm có a, b, c" (cá thể cụ thể) | `owl:oneOf (…)` hoặc khai báo từng cá thể | TBD ≡ {a, b, c} |
| "là những X **được** … **và được** …" | `owl:equivalentClass [ owl:intersectionOf ( X restriction1 restriction2 ) ]` | X ⊓ ∃p.{CPP} ⊓ ∃q.TBD |
| "tối thiểu 2 Y" | `owl:minQualifiedCardinality "2"^^xsd:nonNegativeInteger ; owl:onClass Y` | ≥2 p.Y |

</details>

<details class="ans"><summary>Đáp án</summary>

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Khai báo các lớp và thuộc tính được dùng bên dưới
:GoiPhanMem a owl:Class .
:ChuongTrinh a owl:Class .
:HeDieuHanh a owl:Class .
:NgonNguLapTrinh a owl:Class .
:vietBang a owl:ObjectProperty .
:bienDichBoi a owl:ObjectProperty .
:hoatDongTren a owl:ObjectProperty .

# a. Phụ thuộc là thuộc tính đối tượng bắc cầu giữa các gói phần mềm
:phuThuoc a owl:ObjectProperty , owl:TransitiveProperty ;
    rdfs:domain :GoiPhanMem ; rdfs:range :GoiPhanMem .

# b. Phụ thuộc tương đương với sử dụng
:suDung a owl:ObjectProperty .
:phuThuoc owl:equivalentProperty :suDung .

# c. Trình biên dịch C++ gồm có g++, clang++, msvc
:TrinhBienDichCPP a owl:Class ;
    owl:equivalentClass [ a owl:Class ; owl:oneOf (:gpp :clangpp :msvc) ] .
:gpp a :TrinhBienDichCPP ; rdfs:label "g++" .
:clangpp a :TrinhBienDichCPP ; rdfs:label "clang++" .
:msvc a :TrinhBienDichCPP ; rdfs:label "msvc" .

# d. Chương trình C++ = chương trình viết bằng C++ VÀ biên dịch bằng trình biên dịch C++
:CPP a :NgonNguLapTrinh .
:ChuongTrinhCPP a owl:Class ;
    owl:equivalentClass [ a owl:Class ;
        owl:intersectionOf ( :ChuongTrinh
            [ a owl:Restriction ; owl:onProperty :vietBang ; owl:hasValue :CPP ]
            [ a owl:Restriction ; owl:onProperty :bienDichBoi ; owl:someValuesFrom :TrinhBienDichCPP ] ) ] .

# e. Chương trình đa nền tảng: hoạt động trên tối thiểu 2 hệ điều hành
:ChuongTrinhDaNenTang a owl:Class ;
    owl:equivalentClass [ a owl:Class ;
        owl:intersectionOf ( :ChuongTrinh
            [ a owl:Restriction ; owl:onProperty :hoatDongTren ;
              owl:minQualifiedCardinality "2"^^xsd:nonNegativeInteger ;
              owl:onClass :HeDieuHanh ] ) ] .
```

Biểu thức DL tương ứng:
```text
a. Trans(phuThuoc);  ∃phuThuoc.⊤ ⊑ GoiPhanMem;  ⊤ ⊑ ∀phuThuoc.GoiPhanMem
b. phuThuoc ≡ suDung
c. TrinhBienDichCPP ≡ {gpp, clangpp, msvc}
d. ChuongTrinhCPP ≡ ChuongTrinh ⊓ ∃vietBang.{CPP} ⊓ ∃bienDichBoi.TrinhBienDichCPP
e. ChuongTrinhDaNenTang ≡ ChuongTrinh ⊓ ≥2 hoatDongTren.HeDieuHanh
```

Ghi chú ăn điểm:
- (c) Nếu chỉ hiểu "gồm có" là "có các thành viên này", không bắt buộc là "chỉ gồm", thì viết 3 triple `a :TrinhBienDichCPP` là đủ. `owl:oneOf` thì đóng lớp, tức là chỉ có đúng 3 trình biên dịch.
- (e) Cụm "khác nhau": OWL **không có giả thiết tên duy nhất** (UNA). Muốn reasoner đếm được 2 hệ điều hành là 2 cá thể khác nhau thì phải khai báo thêm, ví dụ `[] a owl:AllDifferent ; owl:distinctMembers (:windows :linux :macos)`.
- (d) Dùng `owl:equivalentClass` chứ không dùng subClassOf, vì đề nói "là **những** chương trình …", tức là một định nghĩa có điều kiện đủ.

</details>

### 6390 · Câu 3 — Suy diễn OWL với allValuesFrom
> **Dạng:** D6 · **Nguồn:** 6390-C3

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:C rdfs:subClassOf :D, :E;
   owl:equivalentClass [a owl:Restriction; owl:onProperty :p; owl:allValuesFrom :F].
:x :p :e, :f.   :y :p :f.   :e a :E.   :f a :F.
```
a) Tìm 1 bộ-3 liên quan tới :C có thể được suy ra từ CSTT đã cho đồng thời giải thích cách suy diễn.
b) Giải thích ngữ nghĩa hình thức của lớp :C bằng cách chuyển các bộ-3 về :C sang lô-gic mô tả.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Đây là **bẫy giả thiết thế giới mở (OWA)**. :y chỉ có một giá trị p là :f, và :f ∈ F. Dễ nghĩ ngay rằng ":y a :C", nhưng điều đó **SAI**: dữ liệu không nói :y không có giá trị p nào khác, nên không thể kết luận "mọi giá trị p của :y đều thuộc F".
- Triple **chắc chắn** suy ra được nằm ở tầng lớp:
  - equivalentClass kéo theo subClassOf theo cả hai chiều;
  - kết hợp với C ⊑ D và C ⊑ E bằng tính bắc cầu, ta được "lớp restriction ⊑ D, E".

</details>

<details class="ans"><summary>Đáp án</summary>

**a)** Gọi `_:r` là lớp restriction `[a owl:Restriction; owl:onProperty :p; owl:allValuesFrom :F]`.

```text
(1) :C rdfs:subClassOf _:r .      <=  :C owl:equivalentClass _:r .         (eqc ⇒ sco, chiều 1)
(2) _:r rdfs:subClassOf :C .      <=  :C owl:equivalentClass _:r .         (eqc ⇒ sco, chiều 2)
(3) _:r rdfs:subClassOf :D .      <=  (2)  và  :C rdfs:subClassOf :D .     (bắc cầu rdfs11)
    _:r rdfs:subClassOf :E .      <=  (2)  và  :C rdfs:subClassOf :E .     (bắc cầu rdfs11)
```

Câu trả lời chính nên chọn **(3)**: mọi đối tượng có tất cả giá trị p thuộc F thì thuộc D (và E). Nói cách khác, ∀p.F ⊑ D ⊓ E.

Giải thích vì sao **không** suy ra được `:y a :C` và `:x a :C`:
- Với :y: OWL theo giả thiết **thế giới mở**. Biết (y, f) ∈ p và f ∈ F, nhưng không biết :y còn giá trị p nào khác không, nên không kết luận được y ∈ ∀p.F.
- Với :x: x có giá trị p là :e ∈ E, và không biết e ∈ F hay không. Vì vậy cũng **không** suy ra được `:x a :C`, mà cũng không suy ra được x ∉ C.
- Muốn suy ra được `:y a :C` thì phải "đóng" thông tin, ví dụ thêm `:y a [a owl:Restriction; owl:onProperty :p; owl:maxCardinality 1]`. Khi đó :f là giá trị p duy nhất của :y, nên y ∈ ∀p.F, rồi suy tiếp `:y a :C`, `:y a :D`, `:y a :E`.

**b)** Chuyển sang DL:
```text
C ⊑ D
C ⊑ E
C ≡ ∀p.F
```
Ngữ nghĩa hình thức theo một diễn giải I = (Δᴵ, ·ᴵ):
```text
Cᴵ ⊆ Dᴵ ,  Cᴵ ⊆ Eᴵ
Cᴵ = (∀p.F)ᴵ = { a ∈ Δᴵ | ∀b : (a, b) ∈ pᴵ → b ∈ Fᴵ }
```
Như vậy :C là tập các cá thể mà **mọi** giá trị p của nó (nếu có) đều thuộc F, và tập đó nằm trong D ∩ E.

Lưu ý ngữ nghĩa: một cá thể **không có giá trị p nào** vẫn thuộc ∀p.F (thỏa mãn một cách hiển nhiên), nên cũng thuộc C.

</details>

### 6390 · Câu 4 — SPARQL (ngôn ngữ lập trình) + đại số
> **Dạng:** D8 + D9 · **Nguồn:** 6390-C4

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
:CPP a :PL; :creator :bjarne_stroustrup; :hasFeature :type, :function, :pointer, :class, :template.
:C a :PL; :creator :dennis_ritchie; :hasFeature :type, :pointer, :function.
:Java a :PL; :creator :james_gosling; :hasFeature :type, :class.
:Python :hasFeature :function, :class .
:Lisp a :PL; :hasFeature :function.
:Ruby a :PL.
```
a) Viết truy vấn tìm các ngôn ngữ lập trình có tính năng (hasFeature) con trỏ (pointer) hoặc lớp (class).
b) Tìm các ngôn ngữ lập trình (PL) cùng với người sáng lập nếu có dữ liệu, để trống cột người sáng lập nếu không có dữ liệu.
c) Tìm và khẳng định (construct) các ngôn ngữ là :OOPL (NNLT HĐT) nếu có tính năng lớp.
d) Viết biểu thức đại số cho mục a và giải thích chi tiết từng bước thực hiện biểu thức.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- (a) Chữ "**hoặc**" ứng với `UNION`, hoặc `FILTER(?f = :pointer || ?f = :class)`. Thêm `DISTINCT` vì C++ có cả hai tính năng, nếu không sẽ bị lặp 2 lần. Cụm "ngôn ngữ lập trình" nên ứng với `?pl a :PL`. Khi đó **Python bị loại** vì không có `a :PL`; nên ghi chú điều này.
- (b) Cụm "nếu có … để trống nếu không" ứng với `OPTIONAL`.
- (c) Cụm "khẳng định là …" ứng với `CONSTRUCT { ?pl a :OOPL } WHERE { … }`.

</details>

<details class="ans"><summary>Đáp án</summary>

**a)**
```sparql
PREFIX : <http://semweb.edu.vn/exam#>
SELECT DISTINCT ?pl
WHERE {
  ?pl a :PL .
  { ?pl :hasFeature :pointer } UNION { ?pl :hasFeature :class }
}
```

| ?pl |
|---|
| :CPP |
| :C |
| :Java |

Nếu bỏ điều kiện `?pl a :PL` thì kết quả có thêm :Python, vì Python có tính năng :class nhưng dữ liệu không khai báo nó là :PL.

**b)**
```sparql
PREFIX : <http://semweb.edu.vn/exam#>
SELECT ?pl ?creator
WHERE {
  ?pl a :PL .
  OPTIONAL { ?pl :creator ?creator }
}
```

| ?pl | ?creator |
|---|---|
| :CPP | :bjarne_stroustrup |
| :C | :dennis_ritchie |
| :Java | :james_gosling |
| :Lisp | |
| :Ruby | |

**c)**
```sparql
PREFIX : <http://semweb.edu.vn/exam#>
CONSTRUCT { ?pl a :OOPL }
WHERE { ?pl :hasFeature :class }
```
Kết quả là đồ thị gồm 3 triple: `:CPP a :OOPL . :Java a :OOPL . :Python a :OOPL .` Nếu thêm `?pl a :PL` vào WHERE thì Python bị loại.

**d)** Biểu thức đại số cho mục a:
```text
Distinct( Project( Join( BGP(?pl a :PL),
                         Union( BGP(?pl :hasFeature :pointer),
                                BGP(?pl :hasFeature :class) ) ),
                   {?pl} ) )
```
Bước 1. BGP(?pl a :PL):

| ?pl |
|---|
| :CPP |
| :C |
| :Java |
| :Lisp |
| :Ruby |

Bước 2. BGP(?pl :hasFeature :pointer):

| ?pl |
|---|
| :CPP |
| :C |

Bước 3. BGP(?pl :hasFeature :class):

| ?pl |
|---|
| :CPP |
| :Java |
| :Python |

Bước 4. Union(Bước 2, Bước 3) là hợp đa tập, giữ cả các dòng trùng nhau:

| ?pl |
|---|
| :CPP |
| :C |
| :CPP |
| :Java |
| :Python |

Bước 5. Join(Bước 1, Bước 4) chỉ giữ các cặp μ tương thích, tức là cùng giá trị ?pl. :Python bị loại vì không có trong Bước 1:

| ?pl |
|---|
| :CPP |
| :C |
| :CPP |
| :Java |

Bước 6. Project lên {?pl} không đổi bảng (bảng chỉ có một biến). Bước 7. Distinct bỏ dòng :CPP bị trùng. **Kết quả:**

| ?pl |
|---|
| :CPP |
| :C |
| :Java |

</details>

### 6390 · Câu 5 — SHACL
> **Dạng:** D10 · **Nguồn:** 6390-C5

Kiểm duyệt dữ liệu với SHACL, sử dụng dữ liệu trong câu 4:
a) Tạo hình trạng :PLFeatures đảm bảo mỗi NNLT (thuộc lớp :PL) được liệt kê tối thiểu 1 tính năng.
b) Khi thực hiện kiểm tra theo :PLFeatures những nút nào sẽ được kiểm tra? Những nút nào vi phạm ràng buộc? Hãy đề xuất bổ sung dữ liệu đối với các nút vi phạm (nếu có) để đáp ứng yêu cầu.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

- Cụm "thuộc lớp :PL" ứng với `sh:targetClass :PL`. Cụm "tối thiểu 1" ứng với `sh:minCount 1`.
- **Nút được kiểm tra (focus node)** là những nút có `rdf:type :PL`, hoặc `rdf:type :Sub` với `:Sub rdfs:subClassOf* :PL` có **trong data graph** (định nghĩa "SHACL instance"). SHACL **không suy kiểu** từ domain/range/OWL: :Python có tính năng nhưng không có `a :PL` (cũng không thuộc lớp con nào của :PL) nên **không được kiểm tra**.
- Muốn tìm nút vi phạm: đếm số giá trị :hasFeature của từng focus node, nút nào có 0 giá trị là vi phạm.

</details>

<details class="ans"><summary>Đáp án</summary>

**a)**
```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
:PLFeatures a sh:NodeShape ;
    sh:targetClass :PL ;
    sh:property [
        sh:path :hasFeature ;
        sh:minCount 1
    ] .
```

**b)**

| Focus node | Số giá trị :hasFeature | Kết quả |
|---|---|---|
| :CPP | 5 | đạt |
| :C | 3 | đạt |
| :Java | 2 | đạt |
| :Lisp | 1 | đạt |
| :Ruby | 0 | **VI PHẠM** (minCount 1) |

- **Nút được kiểm tra:** :CPP, :C, :Java, :Lisp, :Ruby, tức là mọi nút có `a :PL`.
- **:Python không được kiểm tra**, vì dữ liệu không có triple `:Python a :PL` (hay `a` một lớp con của :PL). SHACL kiểm tra theo đúng dữ liệu: chỉ đi theo `rdfs:subClassOf*` có sẵn trong data graph, không suy kiểu từ domain/range/OWL.
- **Nút vi phạm:** :Ruby, vì không có giá trị :hasFeature nào.
- **Đề xuất sửa:** bổ sung tính năng cho Ruby, ví dụ `:Ruby :hasFeature :class, :function .` (Ruby là ngôn ngữ hướng đối tượng). Có thể bổ sung thêm `:Python a :PL .` để Python cũng được kiểm tra; Python sẽ đạt vì có 2 tính năng.

Báo cáo kiểm tra (validation report) sẽ có dạng:
```turtle
[ a sh:ValidationReport ; sh:conforms false ;
  sh:result [ a sh:ValidationResult ;
      sh:focusNode :Ruby ; sh:resultPath :hasFeature ;
      sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
      sh:resultSeverity sh:Violation ] ] .
```

</details>
