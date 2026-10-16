## D10 SHACL — kiểm duyệt dữ liệu RDF

### Hiểu: SHACL để làm gì?

**SHACL** (Shapes Constraint Language) là chuẩn W3C để **kiểm tra dữ liệu RDF có thỏa ràng buộc không**. Nó hay bị nhầm với OWL, nên cần phân biệt rõ:

| | OWL / RDFS | SHACL |
|---|---|---|
| Mục đích | **suy diễn** tri thức mới | **kiểm tra (validate)** dữ liệu |
| Giả thiết | **thế giới mở (OWA)**: thiếu dữ liệu nghĩa là *chưa biết* | **thế giới đóng (CWA)**: thiếu dữ liệu nghĩa là *vi phạm* |
| Ví dụ: "mỗi người có ≥ 1 tên", dữ liệu thiếu tên | không lỗi, reasoner coi như có một tên chưa biết | **vi phạm minCount** |
| Ví dụ: range là Person, giá trị không có kiểu Person | reasoner *suy ra* giá trị đó là Person | `sh:class` báo **vi phạm** |

- **Shapes graph** là đồ thị chứa các ràng buộc (shape). **Data graph** là đồ thị dữ liệu cần kiểm tra.
- **NodeShape** là ràng buộc áp lên chính nút được kiểm tra. **PropertyShape** (`sh:property [ sh:path … ]`) là ràng buộc áp lên các giá trị của một thuộc tính.
- **Focus node** là nút được kiểm tra, được chọn bằng **target**:

| Target | Chọn những nút nào |
|---|---|
| `sh:targetClass :C` | mọi nút có `rdf:type :C` trong dữ liệu (kể cả qua `rdfs:subClassOf` **có trong data graph**) |
| `sh:targetNode :x` | đúng nút :x |
| `sh:targetSubjectsOf :p` | mọi nút đứng ở vị trí **chủ ngữ** của :p |
| `sh:targetObjectsOf :p` | mọi nút đứng ở vị trí **tân ngữ** của :p |

**Bảng ràng buộc hay dùng:**

| Ràng buộc | Ý nghĩa | Đề nói |
|---|---|---|
| `sh:minCount n` | có ít nhất n giá trị | "phải có", "tối thiểu" |
| `sh:maxCount n` | có nhiều nhất n giá trị | "tối đa", "duy nhất" (min 1 + max 1) |
| `sh:datatype xsd:integer` | giá trị phải là literal thuộc kiểu dữ liệu này | "là số nguyên / chuỗi / ngày" |
| `sh:class :C` | giá trị phải là cá thể của :C | "giá trị phải là một Person" |
| `sh:nodeKind sh:IRI` | loại nút: sh:IRI, sh:Literal, sh:BlankNode … | "phải là IRI" |
| `sh:in ( :a :b )` | giá trị phải nằm trong danh sách | "chỉ có thể là a, b" |
| `sh:hasValue :v` | phải có giá trị :v | "phải có giá trị là …" |
| `sh:pattern "^[A-Z]"` | giá trị phải khớp regex | "bắt đầu bằng chữ hoa" |
| `sh:minLength` / `sh:maxLength` | độ dài chuỗi | "tên tối đa 50 ký tự" |
| `sh:minInclusive` / `sh:maxInclusive` | ≥ / ≤ | "từ 1 đến 10" |
| `sh:minExclusive` / `sh:maxExclusive` | > / < | "lớn hơn 1900" |

**Báo cáo kiểm tra (validation report):** `sh:conforms true/false`, và mỗi vi phạm là một `sh:result` gồm `sh:focusNode` (nút vi phạm), `sh:resultPath` (thuộc tính), `sh:value` (giá trị gây lỗi, nếu có), `sh:sourceConstraintComponent` (ràng buộc bị vi phạm) và `sh:resultSeverity` — mặc định là `sh:Violation`, nhưng shape có thể đặt `sh:severity sh:Warning` hoặc `sh:Info` (mức nhẹ hơn).

### Khuôn làm bài

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:TenShape a sh:NodeShape ;
    sh:targetClass :Lop ;                # 1. chọn focus node
    sh:property [                        # 2. mỗi thuộc tính một khối
        sh:path :thuocTinh ;
        sh:minCount 1 ;                  # 3. ràng buộc
        sh:datatype xsd:integer
    ] .
```

Với câu hỏi "nút nào được kiểm tra, nút nào vi phạm, sửa thế nào", trả lời theo 4 bước:
1. Liệt kê **focus node** dựa đúng vào triple `a :Lop` có trong dữ liệu (hoặc `a :LopCon` với `:LopCon rdfs:subClassOf* :Lop` có **trong data graph**). SHACL **không suy kiểu** từ domain/range/OWL.
2. Lập bảng: **focus node | các giá trị của path | đạt / vi phạm (ràng buộc nào)**.
3. Ghi những nút **không** được kiểm tra và giải thích vì sao. Đây là chỗ thầy hay hỏi bẫy.
4. Đề xuất triple cần thêm hoặc sửa cho từng nút vi phạm.

### Ví dụ mẫu — 2023-C5 và 6390-C5
> **Dạng:** D10 · **Nguồn:** 2023-C5, 6390-C5

Lời giải đầy đủ nằm ở tab **Đề cũ**. Tóm tắt kết quả:
- **2023-C5a:** :SeaPlaneShape kiểm tra Caspar và Convair. **Caspar vi phạm** vì 1900 không > 1900.
- **2023-C5b:** :JetFighterShape kiểm tra Su27 và Mig35. **Su27 thiếu :speed, Mig35 thiếu :crew**, cả hai đều vi phạm.
- **6390-C5:** :PLFeatures kiểm tra CPP, C, Java, Lisp, Ruby. **Ruby vi phạm**. Python không được kiểm tra vì không có `a :PL`.

### Luyện tập 1 — Nhãn duy nhất
> **Dạng:** D10 · **Nguồn:** bài tự luyện (dữ liệu 2023-C4)

Mỗi trực thăng (:Helicopter) phải có **đúng 1** nhãn rdfs:label kiểu chuỗi. Viết shape và cho biết kết quả kiểm tra.

<details class="ans"><summary>Đáp án</summary>

```turtle
@prefix : <http://semweb.edu.vn/exam#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
:HelicopterShape a sh:NodeShape ;
    sh:targetClass :Helicopter ;
    sh:property [ sh:path rdfs:label ;
                  sh:minCount 1 ; sh:maxCount 1 ;
                  sh:datatype xsd:string ] .
```
Shape chỉ kiểm tra một focus node là :Mi26. Mi26 có đúng 1 nhãn "Mil Mi-26", kiểu xsd:string, nên **đạt**. Kết quả: `sh:conforms true`.

</details>

### Luyện tập 2 — Khoảng giá trị, chọn target theo thuộc tính
> **Dạng:** D10 · **Nguồn:** bài tự luyện (dữ liệu 2023-C4)

Mọi máy bay **có khai báo** :crew thì số phi hành đoàn phải là số nguyên từ 1 đến 4. Nút nào được kiểm tra, nút nào vi phạm?

<details class="ans"><summary>Đáp án</summary>

```turtle
:CrewShape a sh:NodeShape ;
    sh:targetSubjectsOf :crew ;
    sh:property [ sh:path :crew ; sh:datatype xsd:integer ;
                  sh:minInclusive 1 ; sh:maxInclusive 4 ] .
```

| Focus node | :crew | Kết quả |
|---|---|---|
| :Caspar | 2 | đạt |
| :Convair | 1 | đạt |
| :Su27 | 1 | đạt |
| :Mi26 | 5 | **vi phạm** (maxInclusive 4) |

- **Mig35 không được kiểm tra**, vì nó không đứng ở vị trí chủ ngữ của :crew.
- Sửa: hoặc đổi dữ liệu của Mi26 cho đúng thực tế, hoặc nới ràng buộc lên `sh:maxInclusive 10`.

</details>

### Luyện tập 3 — sh:class và OWL allValuesFrom
> **Dạng:** D10 + D6 · **Nguồn:** bài tự luyện (dữ liệu 2022-C5)

Dữ liệu: `bio:Milo a bio:Cat; bio:offspring bio:Kitty.` `bio:Fido a bio:Dog; bio:offspring bio:Spot, bio:Ted.`
Ràng buộc: con của mèo phải là mèo. a) Viết bằng SHACL và cho biết kết quả. b) So sánh với tiên đề OWL `Cat ⊑ ∀offspring.Cat`.

<details class="ans"><summary>Đáp án</summary>

```turtle
@prefix bio: <http://exam.hust.edu.vn/bio/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
bio:CatShape a sh:NodeShape ;
    sh:targetClass bio:Cat ;
    sh:property [ sh:path bio:offspring ; sh:class bio:Cat ] .
```

a) Shape kiểm tra một focus node là Milo. Giá trị :Kitty **không có** triple `a bio:Cat`, nên **vi phạm sh:class**. Fido không được kiểm tra vì là Dog. Sửa: thêm `bio:Kitty a bio:Cat .`

b) Với OWL, reasoner **suy ra** `bio:Kitty a bio:Cat` và không báo lỗi gì. Đây chính là khác biệt suy diễn (OWA) và kiểm tra (CWA).

</details>

### Luyện tập 4 — Giá trị liệt kê (sh:in)
> **Dạng:** D10 · **Nguồn:** bài tự luyện (nối với 2023-C2 "nhiên liệu")

Dữ liệu: `:amphicar :nhienLieu :xang . :tesla :nhienLieu :dien . :xeX :nhienLieu :gas . :xeY :nhienLieu :xang, :dien .`
Ràng buộc:
- giá trị nhiên liệu chỉ có thể là xăng, dầu hoặc điện;
- mỗi xe khai báo **tối đa 1** nhiên liệu.

<details class="ans"><summary>Đáp án</summary>

```turtle
:FuelShape a sh:NodeShape ;
    sh:targetSubjectsOf :nhienLieu ;
    sh:property [ sh:path :nhienLieu ;
                  sh:in ( :xang :dau :dien ) ;
                  sh:maxCount 1 ] .
```

| Focus node | Giá trị | Kết quả |
|---|---|---|
| :amphicar | :xang | đạt |
| :tesla | :dien | đạt |
| :xeX | :gas | **vi phạm sh:in** (:gas không có trong danh sách) |
| :xeY | :xang, :dien | **vi phạm sh:maxCount** (có 2 giá trị) |

Sửa dữ liệu:
- đổi giá trị của :xeX thành `:xang` hoặc `:dau`;
- với :xeY, bỏ bớt 1 giá trị, hoặc bỏ `sh:maxCount` nếu xe hybrid được phép dùng 2 nhiên liệu.

Khác với OWL: nếu dùng `owl:oneOf`, :gas không bị báo lỗi. Do OWL không có giả thiết tên duy nhất, reasoner sẽ suy ra :gas phải trùng với một trong ba cá thể xăng, dầu, điện.

</details>
