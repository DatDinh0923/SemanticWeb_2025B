## D9 Đại số SPARQL — dịch truy vấn và giải từng bước bằng bảng

### Hiểu: lời giải (solution mapping) và các phép toán

- Một **lời giải μ** là một phép gán từ biến sang giá trị, ví dụ μ = {?p → :Mi26, ?t → :Helicopter}. Một **bảng kết quả Ω** là **đa tập** (multiset) các μ, nghĩa là cho phép các dòng trùng nhau.
- Hai lời giải μ1 và μ2 **tương thích** (compatible) khi mọi biến chung của chúng có **cùng giá trị**. Hai lời giải không có biến chung thì luôn tương thích.

| Phép | Định nghĩa (dễ hiểu) |
|---|---|
| **BGP(P)** | mọi cách gán biến làm cho tất cả triple pattern trong P đều có mặt trong đồ thị |
| **Join(Ω1, Ω2)** | ghép **mỗi** μ1 với **mỗi** μ2 tương thích, kết quả là μ1 ∪ μ2 (giống inner join) |
| **LeftJoin(Ω1, Ω2, expr)** | giống Join, nhưng **giữ lại** những μ1 không ghép được với μ2 nào (hoặc ghép được nhưng expr sai). Các biến của vế phải khi đó để trống (giống left outer join) |
| **Union(Ω1, Ω2)** | gộp hai bảng, giữ cả dòng trùng. Biến chỉ có ở một bên thì để trống ở bên kia |
| **Filter(expr, Ω)** | giữ những μ làm expr **đúng**. Nếu expr bị lỗi (ví dụ biến chưa gán) thì coi là **sai** và dòng bị loại |
| **Project(Ω, V)** | chỉ giữ các cột thuộc tập biến V |
| **Distinct(Ω)** | bỏ các dòng trùng |
| **OrderBy(Ω, cond)** | sắp xếp theo ORDER BY |
| **Slice(Ω, start, length)** | lấy một đoạn theo OFFSET / LIMIT |
| **Group / Aggregation / Extend** | GROUP BY chia nhóm, sau đó tính COUNT / SUM / AVG cho mỗi nhóm, rồi gán kết quả vào biến mới bằng (… AS ?v) |

### Quy tắc dịch cú pháp sang đại số

| Cú pháp SPARQL | Đại số |
|---|---|
| các triple liền nhau `t1 . t2 .` | **BGP(t1 . t2)**, gộp chung thành một BGP |
| hai nhóm liền nhau `{A} {B}` | **Join(A, B)** |
| `A OPTIONAL { B }` | **LeftJoin(A, B, true)** |
| `A OPTIONAL { B FILTER(e) }` | **LeftJoin(A, B, e)**: FILTER nằm **trong** OPTIONAL trở thành điều kiện của LeftJoin |
| `{A} UNION {B}` | **Union(A, B)** |
| `FILTER(e)` ở bất kỳ vị trí nào trong một nhóm | **Filter(e, cả nhóm)**: FILTER bọc **ngoài cùng** nhóm chứa nó, dù được viết ở đầu hay ở cuối nhóm |
| `SELECT ?x ?y` | **Project(…, {?x, ?y})**. `SELECT *` thì không cần Project |
| `SELECT DISTINCT` | **Distinct(Project(…))** |
| `ORDER BY` / `LIMIT n OFFSET k` | **OrderBy** (bên trong Project) / **Slice(…, k, n)** (ngoài cùng) |

Thứ tự lồng nhau từ trong ra ngoài như sau:
```text
Slice( Distinct( Project( OrderBy( Filter( e, Join/LeftJoin/Union( BGP… ) ) ) ) ) )
```

### Khuôn làm bài (4 bước, mỗi bước là một bảng)

1. **Viết biểu thức** theo bảng quy tắc ở trên, lồng các phép từ trong ra ngoài.
2. **Tính các BGP trong cùng trước**: với mỗi BGP, lập một bảng các lời giải lấy từ dữ liệu.
3. **Đi dần ra ngoài**, mỗi phép một bảng: Join, LeftJoin, Union, rồi Filter, Project, Distinct. Mỗi bước ghi một câu giải thích, kiểu "dòng nào bị loại / được giữ, vì sao".
4. **Kết luận**: chép bảng kết quả cuối, ghi rõ số dòng.

Ký hiệu nên dùng (như đáp án của thầy): `μ1: ?pet→bio:Milo`. Ô **để trống** nghĩa là biến chưa được gán.

### Ví dụ mẫu 1 — LeftJoin + Filter (2023-C4)
> **Dạng:** D9 · **Nguồn:** 2023-C4

Xem lời giải đầy đủ ở tab **Đề cũ → 2023-3 Câu 4**. Tóm tắt:
```text
Filter( (?t = :Seaplane || ?t = :Helicopter),
        LeftJoin( BGP(?p a ?t), BGP(?p rdfs:label ?label) ) )
```
BGP1 có 5 dòng, BGP2 có 1 dòng (Mi26). LeftJoin cho 5 dòng, chỉ Mi26 có label. Filter giữ lại 3 dòng: **Caspar, Convair, Mi26 ("Mil Mi-26")**.

### Ví dụ mẫu 2 — Union + Project (2022-C5)
> **Dạng:** D9 · **Nguồn:** 2022-C5

```text
Project( Union( BGP(bio:Anna bio:own ?pet . ?pet a bio:Cat .),
                BGP(bio:Anna bio:own ?x . ?x a bio:Cat . ?x bio:offspring ?pet .) ), {?pet} )
```
Union cho 2 dòng: {?pet→Milo} và {?x→Milo, ?pet→Kitty}. Project lên ?pet cho kết quả **Milo, Kitty**. Xem bảng từng bước ở tab Đề cũ.

### Ví dụ mẫu 3 — Join + Union + Distinct (6390-C4d)
> **Dạng:** D9 · **Nguồn:** 6390-C4d

```text
Distinct( Project( Join( BGP(?pl a :PL),
                         Union( BGP(?pl :hasFeature :pointer), BGP(?pl :hasFeature :class) ) ), {?pl} ) )
```
Kết quả đi qua các bước như sau:
- BGP(:PL) có 5 dòng.
- Union có 5 dòng: CPP, C, CPP, Java, Python.
- Join còn 4 dòng, Python bị loại vì không có trong BGP(:PL).
- Distinct cho kết quả cuối: **CPP, C, Java**.

Xem đủ 7 bảng ở tab Đề cũ.

### Luyện tập 1 — FILTER bên trong OPTIONAL và FILTER bên ngoài
> **Dạng:** D9 · **Nguồn:** bài tự luyện (dữ liệu máy bay 2023-C4)

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
SELECT ?x ?f
WHERE { ?x a :Seaplane . OPTIONAL { ?x :flight ?f FILTER(?f > 1950) } }
```
a) Viết biểu thức đại số và giải từng bước. b) Nếu chuyển FILTER ra ngoài OPTIONAL thì kết quả thay đổi thế nào?

<details class="hint"><summary>Gợi ý / Khuôn</summary>

FILTER nằm **trong** OPTIONAL trở thành điều kiện thứ 3 của LeftJoin. Dòng nào của vế trái không thỏa điều kiện thì **vẫn được giữ**, chỉ là biến ?f để trống.

</details>

<details class="ans"><summary>Đáp án</summary>

a) Biểu thức:
```text
Project( LeftJoin( BGP(?x a :Seaplane), BGP(?x :flight ?f), (?f > 1950) ), {?x, ?f} )
```
Bước 1. BGP(?x a :Seaplane):

| ?x |
|---|
| :Caspar |
| :Convair |

Bước 2. BGP(?x :flight ?f):

| ?x | ?f |
|---|---|
| :Caspar | 1900 |
| :Convair | 1953 |
| :Mi26 | 1983 |

Bước 3. LeftJoin với điều kiện ?f > 1950:
- Caspar ghép được với 1900, nhưng 1900 > 1950 là sai, nên giữ Caspar và để trống ?f.
- Convair ghép với 1953, điều kiện đúng, nên giữ cả dòng.

| ?x | ?f |
|---|---|
| :Caspar | |
| :Convair | 1953 |

Bước 4. Project lên {?x, ?f} không đổi bảng. **Kết quả có 2 dòng**, đã kiểm bằng rdflib.

b) Khi chuyển FILTER ra ngoài, biểu thức là `Filter( ?f > 1950, LeftJoin( BGP1, BGP2 ) )`. LeftJoin cho 2 dòng (Caspar 1900, Convair 1953). Filter loại Caspar, nên kết quả **chỉ còn Convair 1953**.

Kết luận: vị trí của FILTER làm thay đổi kết quả.

</details>

### Luyện tập 2 — Union + Join + Filter
> **Dạng:** D9 · **Nguồn:** bài tự luyện (dữ liệu máy bay 2023-C4)

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
SELECT ?x ?c
WHERE { { ?x a :Seaplane } UNION { ?x a :JetFighter }
        ?x :crew ?c
        FILTER(?c >= 2) }
```

<details class="ans"><summary>Đáp án</summary>

Biểu thức:
```text
Project( Filter( ?c >= 2,
                 Join( Union( BGP(?x a :Seaplane), BGP(?x a :JetFighter) ),
                       BGP(?x :crew ?c) ) ),
         {?x, ?c} )
```

| Bước | Bảng |
|---|---|
| Union | ?x = Caspar, Convair, Su27, Mig35 |
| BGP(?x :crew ?c) | (Caspar,2), (Convair,1), (Su27,1), (Mi26,5) |
| Join | (Caspar,2), (Convair,1), (Su27,1). Mig35 không có crew; Mi26 không có trong Union |
| Filter ?c ≥ 2 | (Caspar,2) |

**Kết quả có 1 dòng: :Caspar, 2**, đã kiểm bằng rdflib.

FILTER được viết ở cuối nhóm nhưng vẫn **bọc toàn bộ nhóm**, tức là bọc cả Join chứ không chỉ bọc BGP crew.

</details>

### Luyện tập 3 — GROUP BY + COUNT/SUM
> **Dạng:** D9 · **Nguồn:** bài tự luyện (dữ liệu máy bay 2023-C4)

```sparql
PREFIX : <http://semweb.edu.vn/exam#>
SELECT ?t (COUNT(?x) AS ?n) (SUM(?c) AS ?tong)
WHERE { ?x a ?t . ?x :crew ?c }
GROUP BY ?t
```

<details class="ans"><summary>Đáp án</summary>

Biểu thức:
```text
Project( Extend( Extend( Group( (?t), BGP(?x a ?t . ?x :crew ?c) ),
                         ?n, COUNT(?x) ),
                 ?tong, SUM(?c) ),
         {?t, ?n, ?tong} )
```
Bước 1. BGP:

| ?x | ?t | ?c |
|---|---|---|
| :Caspar | :Seaplane | 2 |
| :Convair | :Seaplane | 1 |
| :Su27 | :JetFighter | 1 |
| :Mi26 | :Helicopter | 5 |

Bước 2. Group theo ?t, được 3 nhóm:
- Seaplane gồm {Caspar, Convair};
- JetFighter gồm {Su27};
- Helicopter gồm {Mi26}.

Mig35 không xuất hiện vì không có :crew.

Bước 3. Tính hàm tổng hợp (Aggregation / Extend) cho mỗi nhóm. Bước 4. Project:

| ?t | ?n | ?tong |
|---|---|---|
| :Seaplane | 2 | 3 |
| :JetFighter | 1 | 1 |
| :Helicopter | 1 | 5 |

Đã kiểm bằng rdflib.

</details>
