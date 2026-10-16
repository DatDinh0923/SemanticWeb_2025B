## D1 RDF: câu → Turtle + vẽ đồ thị

### 1. Mô hình dữ liệu: mọi thứ là bộ-3 (triple)

Một **triple** = `chủ thể (subject) — vị từ (predicate) — đối tượng (object)`. Một **đồ thị RDF** = tập các triple. Mỗi triple là **một cạnh có hướng, có nhãn** từ subject sang object.

```text
   (subject) ──predicate──▶ (object)
   :hung     ──:teaches───▶ :SemanticWeb
```

| Vị trí | Được phép là | KHÔNG được là |
|---|---|---|
| Subject | IRI, blank node | literal |
| Predicate | **chỉ IRI** | blank node, literal |
| Object | IRI, blank node, literal | — |

**3 loại term:**

| Loại | Ví dụ | Vẽ trên đồ thị (quy ước của thầy) |
|---|---|---|
| **IRI** (định danh toàn cục) | `<http://ex.org/hung>`, `:hung`, `rdf:type` | **hình elip**, ghi tên IRI bên trong |
| **Blank node** (nút vô danh, "có một cái gì đó") | `_:b1`, `[ ]` | **hình elip rỗng** (không ghi gì) |
| **Literal** (giá trị) | `"Hà Nội"`, `"Hanoi"@en`, `10`, `"2024-01-01"^^xsd:date` | **hình chữ nhật**, ghi giá trị |

Cạnh = **mũi tên** từ subject tới object, nhãn = predicate (`rdf:type` viết tắt `a`).

### 2. Turtle trong 1 phút

| Cú pháp | Nghĩa | Ví dụ |
|---|---|---|
| `@prefix ex: <http://ex.org/> .` | khai báo tiền tố | `ex:hung` = `<http://ex.org/hung>` |
| `.` | kết thúc triple/khối | `:a :p :b .` |
| `;` | **cùng subject**, đổi predicate | `:a :p :b ; :q :c .` |
| `,` | **cùng subject + predicate**, nhiều object | `:a :p :b , :c .` |
| `a` | viết tắt `rdf:type` | `:hung a :Teacher .` |
| `[ ... ]` | blank node có thuộc tính | `:nva :score [ :value 10 ] .` |
| `( ... )` | **collection** (danh sách đóng, có thứ tự) | `:c :ref ( :b1 :b2 ) .` |
| `"..."@vi` | literal có ngôn ngữ | `"Hà Nội"@vi` |
| `"..."^^xsd:integer` / `10` | literal có kiểu | `10` = `"10"^^xsd:integer` (khác `"10"^^xsd:int` — `xsd:int` là kiểu khác) |

Ví dụ đầy đủ và đồ thị của nó:

```turtle graph
@prefix : <http://ex.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
:hung a :Teacher ;
  foaf:name "Nguyễn Hùng" ;
  :teaches :SemanticWeb , :DataIntegration .
:SemanticWeb :room "B1-404" .
```

### 3. Các "mẫu" biểu diễn hay ra thi: nhìn câu → chọn cấu trúc

| Đề nói | Dùng | Vì sao |
|---|---|---|
| "A **nghĩ / cảm thấy / nhận xét / cho rằng** …", "theo X thì …" (khi là **ý kiến**) | **Reification** `rdf:Statement` | phát biểu *về* một phát biểu, KHÔNG khẳng định nó đúng |
| "**theo X**, thứ hạng là a, b, c" (xếp hạng có nguồn — TIOBE, đề 6390 C1c) | **Collection gắn vào nút xếp hạng** `:tiobe2023 a :Ranking ; :source :TIOBE ; :order ( :C :CPP :Python :Java )` | giữ thứ tự + ghi nguồn; cách khác: `rdf:Seq`, hoặc reification nếu câu là ý kiến |
| "… **gồm có** a, b, c" / danh sách / thứ tự / "nhóm tác giả" | **Collection** `( a b c )` | danh sách đóng, có thứ tự |
| "điểm 10 **môn X**", "học **ở phòng** … **vào ngày** …" (quan hệ nhiều thành phần) | **Blank node n-ngôi** `[ :value 10 ; :course :X ]` | RDF chỉ có quan hệ 2 ngôi |
| "**một** giáo viên (không rõ là ai)", "một công ty nào đó" | blank node `[ a :Teacher ]` | thực thể không có tên |
| tên, tuổi, năm, điểm | literal | giá trị, không phải tài nguyên |

**Reification**: biến triple `S P O` thành một nút có 4 cạnh:

```turtle graph
@prefix : <http://ex.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
:An :thinks [ a rdf:Statement ;
  rdf:subject :CPP ;
  rdf:predicate rdf:type ;
  rdf:object :InterestingLanguage ] .
```

**Collection** `( :a :b )` thực chất là chuỗi blank node `rdf:first` / `rdf:rest`, kết thúc ở `rdf:nil`:

```turtle graph
@prefix : <http://ex.org/> .
:book :writtenBy ( :gamma :helm :johnson ) .
```

**Xếp hạng "theo X"** (đề 6390 C1c — cách chính): collection có thứ tự gắn vào một nút xếp hạng mang nguồn:

```turtle graph
@prefix : <http://ex.org/> .
:tiobe2023 a :Ranking ; :source :TIOBE ; :order ( :C :CPP :Python :Java ) .
```

**Container** (danh sách *mở*): `rdf:Bag` (không thứ tự), `rdf:Seq` (có thứ tự), `rdf:Alt` (lựa chọn), phần tử gắn bằng `rdf:_1`, `rdf:_2`… — cách **thay thế** cho xếp hạng:

```turtle graph
@prefix : <http://ex.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
:tiobe2023 :order [ a rdf:Seq ; rdf:_1 :C ; rdf:_2 :CPP ; rdf:_3 :Python ; rdf:_4 :Java ] .
```

| | Collection `( )` | Container Bag/Seq/Alt |
|---|---|---|
| Đóng/mở | **đóng** (có `rdf:nil`, không thêm được) | **mở** (ai cũng thêm `rdf:_5` được) |
| Cấu trúc | `rdf:first` / `rdf:rest` | `rdf:_1`, `rdf:_2`… |
| Khi nào dùng | "gồm **đúng** các …"; xếp hạng (gắn vào nút `:Ranking` có nguồn — cách chính) | "trong đó có …"; xếp hạng bằng `rdf:Seq` (cách thay thế) |

**N-ary (quan hệ nhiều ngôi) bằng blank node**:

```turtle graph
@prefix : <http://ex.org/> .
:nva a :Student ; :score [ :value 10 ; :course :sw_course ] .
```

### 4. Khuôn làm bài D1 (7 bước)

1. Viết **@prefix** (`:`, `rdf:`, `rdfs:`, `xsd:`, `foaf:` nếu dùng).
2. Gạch chân **thực thể** → tạo IRI (`:sw_course`, `:nva`…); thực thể không tên → blank node.
3. Mỗi thực thể: thêm **`a :Lớp`** (rdf:type) + **tên/nhãn** (`rdfs:label` / `foaf:name` literal).
4. Gạch **quan hệ** → predicate; giá trị số/chuỗi → literal.
5. Nhận dạng mẫu đặc biệt: *nghĩ/nhận xét* → reification; *gồm* → collection; *xếp hạng theo X* → collection gắn nút `:Ranking` có `:source`; *nhiều thành phần* → n-ary.
6. Viết Turtle gọn bằng `;` `,` `[ ]` `( )`.
7. **Vẽ đồ thị**: elip = IRI, chữ nhật = literal, elip rỗng = blank node; collection phải vẽ **bung ra** first/rest/nil; đếm số cạnh nếu đề giới hạn (≤ 20).

## D2 Chuyển đổi: đồ thị ↔ Turtle ↔ N-Triples ↔ RDF/XML

### Một ví dụ, 3 cách viết

Câu: "Georges là một Saint, tên "Georges", đã đánh bại một con rồng (blank node) thuộc lớp Dragon."

```turtle graph
@prefix : <http://example.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
:Georges a :Saint ; foaf:name "Georges" ; :defeated [ a :Dragon ] .
```

**N-Triples** (mỗi dòng 1 triple, IRI đầy đủ trong `< >`, blank node `_:x`, kết thúc `.`):

```text
<http://example.org/Georges> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.org/Saint> .
<http://example.org/Georges> <http://xmlns.com/foaf/0.1/name> "Georges" .
<http://example.org/Georges> <http://example.org/defeated> _:d .
_:d <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.org/Dragon> .
```

**RDF/XML**:

```text
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:foaf="http://xmlns.com/foaf/0.1/"
         xmlns:ex="http://example.org/">
  <ex:Saint rdf:about="http://example.org/Georges">
    <foaf:name>Georges</foaf:name>
    <ex:defeated>
      <ex:Dragon/>            <!-- nút lồng không rdf:about = blank node -->
    </ex:defeated>
  </ex:Saint>
</rdf:RDF>
```

| Thành phần | Turtle | N-Triples | RDF/XML |
|---|---|---|---|
| IRI subject | `:Georges` | `<http://…/Georges>` | `rdf:about="…"` |
| Kiểu | `a :Saint` | `<…#type> <…Saint>` | tên thẻ `<ex:Saint …>` hoặc `<rdf:type rdf:resource="…"/>` |
| IRI object | `:p :o` | `<…p> <…o>` | `<ex:p rdf:resource="…o"/>` |
| Literal | `"x"@en` | `"x"@en` | `<ex:p xml:lang="en">x</ex:p>` |
| Blank node | `[ ]`, `_:b` | `_:b` | thẻ lồng / `rdf:nodeID="b"` |
| Collection | `( :a :b )` | bung first/rest | `rdf:parseType="Collection"` |

### Khuôn đồ thị → Turtle
1. Liệt kê **mọi mũi tên** thành bảng S | P | O (đếm đủ số cạnh!).
2. Elip có tên → IRI; elip rỗng → blank node `_:b1` hoặc `[ ]`; chữ nhật → literal `"…"`.
3. Gom theo subject bằng `;`, cùng P bằng `,`.
4. Đối chiếu: số triple viết ra = số cạnh trên hình.

### Khuôn Turtle → đồ thị
1. Bung mọi viết tắt (`;` `,` `a` `[ ]` `( )`) thành triple đầy đủ.
2. Mỗi term khác nhau → 1 nút (cùng IRI = cùng 1 nút; mỗi `[ ]` = 1 nút rỗng MỚI).
3. `[] foaf:knows :Minh` → blank node là **subject**.
4. Vẽ mũi tên từng triple, ghi nhãn predicate.

## D3 RDFS: schema (lớp, thuộc tính, domain, range)

| Từ vựng | Nghĩa | Ví dụ |
|---|---|---|
| `rdfs:Class` | X là một lớp | `:Person a rdfs:Class .` |
| `rdf:Property` | X là một thuộc tính | `:teaches a rdf:Property .` |
| `rdf:type` (`a`) | cá thể thuộc lớp | `:hung a :Teacher .` |
| `rdfs:subClassOf` | lớp con (mọi A là B) | `:Professor rdfs:subClassOf :Teacher .` |
| `rdfs:subPropertyOf` | thuộc tính con | `:hasFather rdfs:subPropertyOf :hasParent .` |
| `rdfs:domain` | **chủ thể** dùng P thì thuộc lớp C | `:teaches rdfs:domain :Teacher .` |
| `rdfs:range` | **đối tượng** của P thuộc lớp C | `:teaches rdfs:range :Course .` |
| `rdfs:label`, `rdfs:comment` | nhãn, chú thích | `:Person rdfs:label "Người"@vi .` |
| `rdfs:Literal`, `rdfs:Resource`, `rdfs:Datatype` | lớp đặc biệt | |

Ví dụ (đề Ex3 URI1–URI6):

```turtle graph
@prefix : <http://ex.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:URI1 a rdfs:Class .
:URI2 a rdfs:Class .
:URI3 a rdf:Property ; rdfs:domain :URI1 ; rdfs:range :URI2 .
:URI4 a :URI1 .
:URI5 a :URI2 .
:URI6 a :URI2 .
```

**Ghi nhớ:** domain/range trong RDFS là **luật suy diễn**, không phải ràng buộc kiểm tra: dùng sai kiểu thì máy *suy ra kiểu mới* chứ không báo lỗi. Nhiều domain = **giao** các lớp.

**Khuôn D3:** (1) liệt kê lớp → `a rdfs:Class`; (2) phân cấp → `subClassOf`; (3) thuộc tính → `a rdf:Property` + domain + range; (4) cá thể → `a :Lớp`; (5) vẽ đồ thị schema (mỗi triple 1 mũi tên, cả `rdfs:subClassOf`, `rdfs:domain`, `rdfs:range`).

## D4 Suy diễn RDFS

### Bảng luật (trích đúng tên luật khi làm bài)

| Luật | Nếu có | Thì suy ra | Nhớ nhanh |
|---|---|---|---|
| **rdf1** | `x p y .` | `p a rdf:Property .` | vị từ là Property |
| **rdfs2** | `p rdfs:domain C .` + `x p y .` | `x a C .` | domain → subject |
| **rdfs3** | `p rdfs:range C .` + `x p y .` | `y a C .` | range → object |
| **rdfs4a** | `x p y .` | `x a rdfs:Resource .` | |
| **rdfs4b** | `x p y .` | `y a rdfs:Resource .` | |
| **rdfs5** | `p subPropertyOf q .` + `q subPropertyOf r .` | `p subPropertyOf r .` | bắc cầu |
| **rdfs6** | `p a rdf:Property .` | `p subPropertyOf p .` | phản xạ |
| **rdfs7** | `p subPropertyOf q .` + `x p y .` | `x q y .` | kế thừa property |
| **rdfs8** | `C a rdfs:Class .` | `C subClassOf rdfs:Resource .` | |
| **rdfs9** | `C subClassOf D .` + `x a C .` | `x a D .` | kế thừa kiểu |
| **rdfs10** | `C a rdfs:Class .` | `C subClassOf C .` | phản xạ |
| **rdfs11** | `C subClassOf D .` + `D subClassOf E .` | `C subClassOf E .` | bắc cầu |
| **rdfs12** | `p a rdfs:ContainerMembershipProperty .` | `p subPropertyOf rdfs:member .` | |
| **rdfs13** | `D a rdfs:Datatype .` | `D subClassOf rdfs:Literal .` | |
| **se1** | `x p y .` | `x p _:b .` | thay object bằng blank |
| **se2** | `x p y .` | `_:b p y .` | thay subject bằng blank |

**Forward chaining**: lặp áp mọi luật → thêm triple mới → đến khi không thêm được (điểm bất động). Luôn dừng vì không tạo tài nguyên mới.

```text
:a :r :b .  +  :r rdfs:domain :D .     ==rdfs2==>  :a a :D .
:a a :D .   +  :D rdfs:subClassOf :F . ==rdfs9==>  :a a :F .
```

### Phương pháp "đúng / sai / không xác định" (OWA)
1. Triple **có sẵn** trong đồ thị → **ĐÚNG** (ghi "có sẵn").
2. Suy ra được bằng chuỗi luật → **ĐÚNG**, ghi từng bước: `kết luận <= tiền đề 1 . tiền đề 2 . (luật)`.
3. Không suy ra được → **KHÔNG XÁC ĐỊNH (unknown)**, KHÔNG phải "sai": RDF theo **giả thiết thế giới mở** (OWA), không biết ≠ sai.
4. RDFS **không có phủ định** → không bao giờ chứng minh được "sai" (trừ khi đề hỏi theo CWA).

**Bẫy hay gặp:**
- RDFS **không có inverse**: `:Ann :hasFather :Carl` KHÔNG suy ra `:Carl :hasChild :Ann` → unknown.
- Luôn kiểm **cả domain lẫn range**: `:Ann :hasFather :Carl` + `:hasFather rdfs:range :Father` ⇒ `:Carl a :Father` (rdfs3) → ĐÚNG; rồi `:Father subClassOf :Parent` ⇒ `:Carl a :Parent` (rdfs9).
- `subPropertyOf` truyền triple lên (rdfs7) nhưng domain/range của property **cha** áp cho triple đã truyền lên; domain/range của property **con** không áp cho property cha.

## D5 Thiết kế ontology OWL + biểu thức DL

### Bảng tra: câu tiếng Việt → OWL Turtle → DL → Manchester

| Đề nói | DL | Turtle | Manchester |
|---|---|---|---|
| "A là một loại B", "mọi A là B" | `A ⊑ B` | `:A rdfs:subClassOf :B .` | `A SubClassOf B` |
| "A **chính là / được định nghĩa là** …" | `A ≡ C` | `:A owl:equivalentClass C .` | `A EquivalentTo C` |
| "**vừa là** A **vừa là** B" | `A ⊓ B` | `[ owl:intersectionOf ( :A :B ) ]` | `A and B` |
| "A **hoặc** B", "X là **tên gọi chung** của A, B" | `X ≡ A ⊔ B` | `[ owl:unionOf ( :A :B ) ]` | `A or B` |
| "X **gồm (có)** A, B" (các loại con) | `A ⊑ X`, `B ⊑ X` (+ rời nhau nếu đề nói) | `:A rdfs:subClassOf :X .` `:B rdfs:subClassOf :X .` | `A SubClassOf X` |
| "**không phải** A" | `¬A` | `[ owl:complementOf :A ]` | `not A` |
| "**không có** cái nào vừa A vừa B" / "rời nhau" | `A ⊓ B ⊑ ⊥` (dạng slide: `A ⊑ ¬B`) | `:A owl:disjointWith :B .` | `DisjointClasses: A, B` |
| "**có ít nhất một** p là C" | `∃p.C` | `[ a owl:Restriction ; owl:onProperty :p ; owl:someValuesFrom :C ]` | `p some C` |
| "**mọi / chỉ** p đều là C" | `∀p.C` | `… owl:allValuesFrom :C ]` | `p only C` |
| "p **có giá trị** a" | `∃p.{a}` | `… owl:hasValue :a ]` | `p value a` |
| "**tối thiểu** n" | `≥n p` | `… owl:minCardinality "n"^^xsd:nonNegativeInteger ]` | `p min n` |
| "tối thiểu n **C**" (có điều kiện) | `≥n p.C` | `… owl:minQualifiedCardinality "n"^^xsd:nonNegativeInteger ; owl:onClass :C ]` | `p min n C` |
| "tối đa / đúng n" | `≤n p` / `=n p` | `owl:maxCardinality` / `owl:cardinality` | `p max n` / `p exactly n` |
| "tối đa / đúng n **C**" (có điều kiện) | `≤n p.C` / `=n p.C` | `owl:maxQualifiedCardinality` / `owl:qualifiedCardinality` + `owl:onClass :C` | `p max n C` / `p exactly n C` |
| "giá trị có thể là a, b, c" | `{a,b,c}` | `[ owl:oneOf ( :a :b :c ) ]` | `{a, b, c}` |
| "domain của p là C" | `∃p.⊤ ⊑ C` | `:p rdfs:domain :C .` | `Domain: C` |
| "range của p là C" | `⊤ ⊑ ∀p.C` | `:p rdfs:range :C .` | `Range: C` |
| "p **bắc cầu**" | `Trans(p)` | `:p a owl:TransitiveProperty .` | `Characteristics: Transitive` |
| "p **đối xứng**" | `p ≡ p⁻` | `:p a owl:SymmetricProperty .` | `Symmetric` |
| "p **hàm** (tối đa 1 giá trị)" | `⊤ ⊑ ≤1 p` | `:p a owl:FunctionalProperty .` | `Functional` |
| "q là **nghịch đảo** của p" | `q ≡ p⁻` | `:q owl:inverseOf :p .` | `InverseOf: p` |
| "p **tương đương** q" | `p ≡ q` | `:p owl:equivalentProperty :q .` | `EquivalentTo: q` |
| "p là thuộc tính con của q" | `p ⊑ q` | `:p rdfs:subPropertyOf :q .` | `SubPropertyOf: q` |
| "a và b là một" | `a = b` | `:a owl:sameAs :b .` | `SameAs: b` |
| "thuộc tính đối tượng / dữ liệu" | | `a owl:ObjectProperty` / `a owl:DatatypeProperty` | |

### Ví dụ: "Phương tiện gồm ô tô và xe máy; không cái nào vừa là ô tô vừa là xe máy"

```text
DL:    Car ⊑ Vehicle      Motorbike ⊑ Vehicle      Car ⊓ Motorbike ⊑ ⊥
```

```turtle graph
@prefix : <http://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
:Car rdfs:subClassOf :Vehicle .
:Motorbike rdfs:subClassOf :Vehicle .
:Car owl:disjointWith :Motorbike .
```

"gồm" ⇒ `subClassOf` (mỗi lớp con là một loại của lớp cha); "không cái nào vừa là… vừa là…" ⇒ `owl:disjointWith`. Chỉ khi đề nói "X là **tên gọi chung** của A, B" mới dùng `X ≡ A ⊔ B`. Đề 2022-C4 (thú cưng) cùng khuôn này — đáp án của thầy: `Dog ⊑ Pet`, `Cat ⊑ Pet`, `Dog ⊓ Cat ⊑ ⊥`; tự làm ở mục ④.

### Khuôn thiết kế (6 bước)
1. Liệt kê **lớp** (`a owl:Class`), **thuộc tính** (`owl:ObjectProperty` / `owl:DatatypeProperty`).
2. Mỗi câu đề → 1 tiên đề: dịch theo bảng trên (gạch chân từ khóa "vừa…vừa", "hoặc", "ít nhất", "chỉ", "không").
3. Định nghĩa (điều kiện cần **và đủ**) → `owl:equivalentClass`; chỉ điều kiện cần → `rdfs:subClassOf`.
4. Viết DL song song từng tiên đề.
5. Kiểm tra cú pháp: cardinality `"n"^^xsd:nonNegativeInteger` (slide thầy viết `^^xsd:integer` — cả hai đều được chấp nhận); `unionOf/intersectionOf/oneOf` nhận **danh sách `( )`**; restriction phải có `owl:onProperty`.
6. Giải thích ngắn lựa chọn (vì sao equivalent / subClass, vì sao union…).

## D6 Suy diễn OWL / reasoner

| Mẫu | Tiên đề | Dữ kiện | Suy ra |
|---|---|---|---|
| allValuesFrom (∀) | `C ≡ ∀p.F` | `x a C`, `x p y` | `y a F` |
| allValuesFrom ngược | `C ≡ ∀p.F` | **mọi** p-giá trị của x là F (và biết đủ — OWA!) | `x a C` chỉ khi đóng được thế giới; thường **không** suy ra được |
| someValuesFrom (∃) | `C ≡ ∃p.F` | `x p y`, `y a F` | `x a C` |
| someValuesFrom xuôi | `C ⊑ ∃p.F` | `x a C` | có một y (chưa biết) với `x p y`, `y a F` |
| hasValue | `C ≡ ∃p.{a}` | `x p a` | `x a C` |
| inverseOf | `q owl:inverseOf p` | `x p y` | `y q x` |
| Transitive | `p` bắc cầu | `x p y`, `y p z` | `x p z` |
| Symmetric | `p` đối xứng | `x p y` | `y p x` |
| Functional | `p` hàm | `x p a`, `x p b` | `a owl:sameAs b` (không mâu thuẫn, vì không có UNA) |
| intersectionOf | `C ≡ A ⊓ B` | `x a A`, `x a B` | `x a C` |
| unionOf | `C ≡ A ⊔ B` | `x a A` | `x a C` |
| disjointWith | `A ⊓ B ⊑ ⊥` | `x a A`, `x a B` | **mâu thuẫn** (inconsistent) |
| subClassOf (TBox) | `C ⊑ D`, `C ⊑ E` | | `C ⊑ D ⊓ E` |

**Ví dụ:** dữ liệu có `:Tom a :Bird ; :hasChick :Kiwi .` Muốn reasoner suy ra **Kiwi là chim** (con của chim là chim), nhưng không suy ra con của mèo là chim. RDFS không làm được: `rdfs:range` áp cho **mọi** chủ thể, kể cả mèo. OWL dùng restriction gắn vào lớp Bird:

```turtle graph
@prefix : <http://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
:Bird rdfs:subClassOf [ a owl:Restriction ; owl:onProperty :hasChick ; owl:allValuesFrom :Bird ] .
```

Lập luận: DL `Bird ⊑ ∀hasChick.Bird`. Tom ∈ Bird và (Tom, Kiwi) ∈ hasChick ⇒ theo nghĩa của ∀, Kiwi ∈ Bird. Một con mèo không thuộc Bird nên tiên đề không áp dụng cho con của nó.

*Ghi chú OWA (ghi thêm để ăn điểm):* dùng ∀ ở chiều **xuôi** (`Bird ⊑ ∀hasChick.Bird`) là chắc chắn suy ra được. Chiều **ngược** (`Bird ≡ ∀parentOf⁻.Bird`, "mọi cha mẹ là chim thì là chim") thường **không** suy ra được vì OWA: không biết đã đủ hết cha mẹ chưa. Đề 2022-C3 (Fido/Milo) cùng khuôn này: tự làm ở mục ④.

**Cách viết lời giải suy diễn OWL:** (1) dịch tiên đề sang DL; (2) nêu ngữ nghĩa hình thức (`C^I = {x | ∀y: (x,y)∈p^I → y∈F^I}`); (3) áp từng bước kèm tên tiên đề; (4) kết luận + lưu ý OWA.

## D8 SPARQL từ con số 0

### Ý tưởng: khớp mẫu đồ thị
Câu truy vấn là một **đồ thị có biến** (`?x`). Máy tìm mọi cách gán giá trị cho biến sao cho mẫu nằm trong dữ liệu.

```text
Dữ liệu:  :Fido a :Dog .   :Milo a :Cat .   :Anna :own :Fido , :Milo .
Mẫu:      :Anna :own ?pet .  ?pet a :Cat .
Kết quả:  ?pet = :Milo         (Fido bị loại vì không khớp "?pet a :Cat")
```

### Cấu trúc 1 câu SELECT

```sparql
PREFIX : <http://ex.org/>
SELECT ?x ?name                 # cột đầu ra (hoặc *)
WHERE {
  ?x a :Student .               # triple pattern (dấu . nối, dùng ; , như Turtle)
  OPTIONAL { ?x :name ?name }   # có thì lấy, không thì để trống
  FILTER (?x != :An)            # lọc
}
ORDER BY ?name LIMIT 10
```

| Từ khóa | Tác dụng | Ví dụ ngắn |
|---|---|---|
| `FILTER(expr)` | giữ dòng thỏa điều kiện | `FILTER(?year > 1990 && ?t = :Seaplane)` |
| `OPTIONAL { }` | nối trái: không có thì biến **trống** | `OPTIONAL { ?p rdfs:label ?l }` |
| `{ A } UNION { B }` | hợp kết quả hai mẫu | `{ ?x a :Seaplane } UNION { ?x a :Helicopter }` |
| `VALUES ?t { :A :B }` | gán sẵn danh sách giá trị | `VALUES ?t { :Seaplane :Helicopter }` |
| `FILTER NOT EXISTS { }` | **không có** mẫu | `FILTER NOT EXISTS { ?c :hasHomework ?h }` |
| `MINUS { }` | trừ đi các dòng khớp | `MINUS { ?x a :Lab }` |
| `GROUP BY ?x` + `COUNT/SUM/AVG/MIN/MAX` | gom nhóm, tổng hợp | `SELECT ?d (COUNT(?m) AS ?n) … GROUP BY ?d` |
| `HAVING(cond)` | lọc sau khi gom | `HAVING(COUNT(?m) >= 2)` |
| `DISTINCT` | bỏ dòng trùng | `SELECT DISTINCT ?x` |
| `ORDER BY ?x` / `DESC(?x)` | sắp xếp | |
| `LIMIT n` / `OFFSET n` | phân trang | |
| property path `p+`, `p*`, `p/q`, `^p`, `p\|q` | đi nhiều bước / ngược / hoặc | `?c rdfs:subClassOf* :Person` |
| `BIND(expr AS ?v)` | tạo biến mới | `BIND(YEAR(?d) AS ?y)` |
| `regex(?s, "pat", "i")`, `CONTAINS`, `STRSTARTS` | xử lý chuỗi | `FILTER regex(?name, "^Ng", "i")` |
| `bound(?v)` | biến có giá trị không | `FILTER(!bound(?l))` |
| `CONSTRUCT { } WHERE { }` | tạo đồ thị mới (khẳng định) | `CONSTRUCT { ?x a :OOPL } WHERE { ?x :hasFeature :class }` |
| `ASK { }` | trả về true/false | `ASK { :Su27 :speed ?s }` |
| `DESCRIBE :x` | trả mô tả về tài nguyên | |

### 4 dạng truy vấn
`SELECT` (bảng), `CONSTRUCT` (đồ thị RDF), `ASK` (true/false), `DESCRIBE` (mô tả tài nguyên).

**Lưu ý:** SPARQL truy vấn **dữ liệu có sẵn**, không tự suy diễn (trừ khi endpoint bật reasoner) → muốn "kể cả lớp con" phải dùng `rdfs:subClassOf*`.

## D12 Tableau từ con số 0

### Ý tưởng
Mọi bài toán suy diễn DL quy về **kiểm tra nhất quán (consistency)** bằng **phản chứng**:

| Muốn chứng minh | Thêm vào KB | Kết luận nếu **mọi nhánh đóng** |
|---|---|---|
| KB nhất quán? | (không thêm) | KB **không** nhất quán |
| `a` là `C`? (instance) | `¬C(a)` | `C(a)` đúng |
| `C ⊑ D`? (subsumption) | `(C ⊓ ¬D)(x)` với cá thể mới x | `C ⊑ D` đúng |
| C thỏa được? | `C(x)` | C không thỏa được |

### Bước 1: chuyển sang NNF (¬ chỉ đứng trước tên lớp)

| Biểu thức | NNF |
|---|---|
| `C ⊑ D` | `¬C ⊔ D` |
| `C ≡ D` | `¬C ⊔ D` và `¬D ⊔ C` |
| `¬¬C` | `C` |
| `¬(C ⊓ D)` | `¬C ⊔ ¬D` |
| `¬(C ⊔ D)` | `¬C ⊓ ¬D` |
| `¬∃R.C` | `∀R.¬C` |
| `¬∀R.C` | `∃R.¬C` |
| `C ⊓ D ⊑ ⊥` | `¬C ⊔ ¬D` |

### Bước 2: áp 7 luật (đánh số đúng như slide)

| Nr | Có | Làm |
|---|---|---|
| 1 | `C(a)` trong ABox | thêm `C(a)` |
| 2 | `R(a,b)` | thêm `R(a,b)` |
| 3 | `C` (tiên đề TBox ở dạng NNF) | chọn cá thể `a`, thêm `C(a)` |
| 4 | `(C ⊓ D)(a)` | thêm `C(a)` và `D(a)` |
| 5 | `(C ⊔ D)(a)` | **tách nhánh**: T1 thêm `C(a)`, T2 thêm `D(a)` |
| 6 | `(∃R.C)(a)` | thêm `R(a,b)`, `C(b)` với `b` **mới** |
| 7 | `(∀R.C)(a)` | mọi b có `R(a,b)`: thêm `C(b)` |

- **Nhánh đóng** khi chứa `X(a)` và `¬X(a)`.
- **Blocking:** đã dùng luật 6 cho một assertion `(∃R.C)(a)` thì block chính assertion đó, không dùng lại (slide tr. 63: "If rule 6 was used, block A for T" — tính theo **từng assertion**, không phải theo từng cá thể; tránh sinh cá thể vô hạn).
- **Kết luận:** còn ≥ 1 nhánh **mở** và không áp thêm luật được ⇒ nhất quán; **mọi** nhánh đóng ⇒ không nhất quán ⇒ điều cần chứng minh đúng.

```text
Ví dụ: KB = { Penguin ⊑ Bird, Bird ⊑ Flies, Penguin ⊑ ¬Flies, Penguin(pingu) }
NNF:  ¬Penguin ⊔ Bird ;  ¬Bird ⊔ Flies ;  ¬Penguin ⊔ ¬Flies
(1) Penguin(pingu)
(3)+(5) ¬Penguin(pingu) ✗ đóng  |  Bird(pingu)
        (3)+(5) ¬Bird(pingu) ✗  |  Flies(pingu)
                (3)+(5) ¬Penguin(pingu) ✗ | ¬Flies(pingu) ✗
=> mọi nhánh đóng => KB không nhất quán.
```

**Mẹo:** ưu tiên luật không tách nhánh (1, 2, 4, 6, 7) trước luật 5; luật 3 chọn cá thể đang "dính" vào ∀/∃ để đóng nhánh sớm. Trình bày: đánh số dòng, ghi (luật số mấy, từ dòng nào), đánh dấu ✗ nhánh đóng.
