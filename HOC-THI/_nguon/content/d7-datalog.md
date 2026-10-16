## D7 Datalog — cây chứng minh và điểm cố định

### Hiểu: Datalog là gì

**Datalog** là ngôn ngữ luật dạng logic. Một chương trình Datalog gồm 2 thành phần:

| Thành phần | Dạng | Ví dụ |
|---|---|---|
| **Dữ kiện (fact)** | vị từ áp lên các **hằng**, không có biến | `Đường-một-chiều(A, B)` |
| **Luật (rule)** | `đầu ← thân₁ ∧ thân₂ ∧ …` | `Có-đường-đi(X, Z) ← Có-đường-đi(X, Y) ∧ Có-đường-đi(Y, Z)` |

- **Đầu (head)** đứng bên trái dấu `←` và là kết luận. **Thân (body)** đứng bên phải và là điều kiện; các điều kiện nối với nhau bằng "và" (∧).
- **Biến** viết hoa (X, Y, Z). Mọi biến xuất hiện ở đầu luật cũng phải xuất hiện trong thân (điều kiện an toàn, *safety*).
- Cách đọc luật: **nếu** thân đúng với một phép gán biến thành hằng **thì** đầu cũng đúng với phép gán đó.
- Datalog **không có ký hiệu hàm**, nên số dữ kiện có thể sinh ra là **hữu hạn**. Nhờ đó suy diễn luôn dừng.

**Suy diễn tiến (forward chaining, naive evaluation)** dùng toán tử bước T_P:

```text
B0 = tập dữ kiện ban đầu
B(i+1) = B(i) ∪ { đầu luật | có phép gán làm mọi điều kiện trong thân ∈ B(i) }
Dừng khi B(i+1) = B(i)   →   B(i) gọi là ĐIỂM CỐ ĐỊNH (fixpoint, mô hình nhỏ nhất)
```

- Ở mỗi bước, mọi luật được áp lên **toàn bộ tập của bước trước**. Dữ kiện nào mới sinh **trong** bước i thì phải đợi tới bước i+1 mới được dùng làm điều kiện.
- **Điểm cố định** là tập dữ kiện mà áp mọi luật lên cũng không sinh thêm dữ kiện nào. Đây là toàn bộ tri thức suy ra được.

**Cây chứng minh (proof tree)** của một mệnh đề G được dựng như sau:
- gốc là G;
- mỗi nút trong là đầu của một luật đã được gán biến, các con của nó là những điều kiện trong thân luật đó;
- mọi lá là **dữ kiện** thuộc B0.

Độ sâu của cây **nông nhất** (trong các cây chứng minh của G) cho biết G xuất hiện lần đầu ở bước nào: lá ở B0 thì nút cha mới sinh ở B1, và cứ thế lên trên. Một cây sâu hơn vẫn hợp lệ nhưng không cho biết đúng bước xuất hiện.

**Liên hệ với RDFS:** các luật RDFS chính là luật Datalog trên vị từ triple(S, P, O). Ví dụ rdfs9 viết thành:
`triple(X, rdf:type, D) ← triple(X, rdf:type, C) ∧ triple(C, rdfs:subClassOf, D)`.
Vì vậy tính bao đóng RDFS cũng là tính điểm cố định.

### Khuôn làm bài (đúng format đáp án của thầy)

1. **Liệt kê B0**: chép toàn bộ dữ kiện (các dòng không có `←`).
2. **B1**: lần lượt xét **từng luật**, thử mọi cách gán biến bằng các dữ kiện **trong B0**, rồi ghi `B1: + {các dữ kiện MỚI}`.
3. **B2, B3, …**: lặp lại bước trên, nhưng điều kiện được lấy từ **toàn bộ** tập hiện có (gồm B0 và mọi dữ kiện đã thêm). Chỉ ghi những dữ kiện **chưa có**.
4. Khi một bước không thêm được gì, ghi `B(k+1): + {}` và kết luận: **"Điểm cố định thu được ở Bước k"**. Nên liệt kê lại toàn bộ tập điểm cố định.
5. **Cây chứng minh**: viết mệnh đề cần chứng minh ở gốc, chọn luật có đầu khớp, vẽ các điều kiện thân làm con, đi xuống tới khi mọi lá là dữ kiện B0. Ghi tên luật cạnh mỗi nút nếu còn thời gian.

Mẹo với luật bắc cầu `R(X,Z) ← R(X,Y) ∧ R(Y,Z)`: lập **bảng "từ X đi tới được đâu"** sau mỗi bước rồi ghép các cặp, sẽ nhanh và ít sót hơn.

### Ví dụ mẫu 2023-C3 — giải chi tiết từng bước
> **Dạng:** D7 · **Nguồn:** 2023-C3

```text
Dữ kiện:  Đường-một-chiều(A, B)   Đường-một-chiều(B, C)   Đường-hai-chiều(D, C)
L1: Đường-hai-chiều(Y, X) ← Đường-hai-chiều(X, Y)               (đối xứng)
L2: Có-đường-đi(X, Y) ← Đường-hai-chiều(X, Y)
L3: Có-đường-đi(X, Y) ← Đường-một-chiều(X, Y)
L4: Có-đường-đi(X, Z) ← Có-đường-đi(X, Y) ∧ Có-đường-đi(Y, Z)   (bắc cầu)
```

Viết tắt: 1C = Đường-một-chiều, 2C = Đường-hai-chiều, Đi = Có-đường-đi.

| Bước | Dữ kiện mới | Vì sao (luật + điều kiện) |
|---|---|---|
| B0 | 1C(A,B), 1C(B,C), 2C(D,C) | dữ kiện cho sẵn |
| B1 | 2C(C,D) | L1 với 2C(D,C) |
| | Đi(A,B), Đi(B,C) | L3 với 1C(A,B), 1C(B,C) |
| | Đi(D,C) | L2 với 2C(D,C) |
| | *(L4 chưa áp được)* | B0 chưa có dữ kiện Đi nào |
| B2 | Đi(C,D) | L2 với 2C(C,D), dữ kiện mới có từ B1 |
| | Đi(A,C) | L4: Đi(A,B) ∧ Đi(B,C) |
| B3 | Đi(B,D) | L4: Đi(B,C) ∧ Đi(C,D) |
| | Đi(A,D) | L4: Đi(A,C) ∧ Đi(C,D) |
| | Đi(C,C) | L4: Đi(C,D) ∧ Đi(D,C) |
| | Đi(D,D) | L4: Đi(D,C) ∧ Đi(C,D) |
| B4 | ∅ | mọi cặp bắc cầu đều đã có, nên **dừng** |

Kiểm tra B4 bằng bảng "đi tới được": A → {B, C, D}; B → {C, D}; C → {C, D}; D → {C, D}. Ghép mọi cặp bắc cầu đều không ra cặp mới. **Điểm cố định thu được ở Bước 3.** Các bước này khớp với đáp án của thầy.

Cây chứng minh Có-đường-đi(A, D):
```text
Có-đường-đi(A, D)                                 [L4]
├── Có-đường-đi(A, C)                             [L4]
│   ├── Có-đường-đi(A, B)                         [L3]
│   │   └── Đường-một-chiều(A, B)                 (dữ kiện)
│   └── Có-đường-đi(B, C)                         [L3]
│       └── Đường-một-chiều(B, C)                 (dữ kiện)
└── Có-đường-đi(C, D)                             [L2]
    └── Đường-hai-chiều(C, D)                     [L1]
        └── Đường-hai-chiều(D, C)                 (dữ kiện)
```
Cây có độ sâu 3, khớp với việc Đi(A,D) xuất hiện ở B3.

### Luyện tập 1 — Tổ tiên
> **Dạng:** D7 · **Nguồn:** bài tự luyện

```text
Cha-mẹ(an, bình)   Cha-mẹ(bình, chi)   Cha-mẹ(chi, dũng)
L1: Tổ-tiên(X, Y) ← Cha-mẹ(X, Y)
L2: Tổ-tiên(X, Z) ← Cha-mẹ(X, Y) ∧ Tổ-tiên(Y, Z)
```
a) Vẽ cây chứng minh Tổ-tiên(an, dũng). b) Tìm điểm cố định.

<details class="hint"><summary>Gợi ý / Khuôn</summary>

L2 là luật **tuyến tính**: điều kiện thứ nhất là Cha-mẹ (một dữ kiện gốc), không phải Tổ-tiên. Vì vậy mỗi bước chỉ kéo dài chuỗi thêm đúng 1 bậc.

</details>

<details class="ans"><summary>Đáp án</summary>

```text
B0: {Cha-mẹ(an,bình), Cha-mẹ(bình,chi), Cha-mẹ(chi,dũng)}
B1: + {Tổ-tiên(an,bình), Tổ-tiên(bình,chi), Tổ-tiên(chi,dũng)}          (L1)
B2: + {Tổ-tiên(an,chi), Tổ-tiên(bình,dũng)}                             (L2)
B3: + {Tổ-tiên(an,dũng)}                                                (L2: Cha-mẹ(an,bình) ∧ Tổ-tiên(bình,dũng))
B4: + {}   → Điểm cố định thu được ở Bước 3.
```
```text
Tổ-tiên(an, dũng)                      [L2]
├── Cha-mẹ(an, bình)                   (dữ kiện)
└── Tổ-tiên(bình, dũng)                [L2]
    ├── Cha-mẹ(bình, chi)              (dữ kiện)
    └── Tổ-tiên(chi, dũng)             [L1]
        └── Cha-mẹ(chi, dũng)          (dữ kiện)
```

</details>

### Luyện tập 2 — Chuyến bay khứ hồi
> **Dạng:** D7 · **Nguồn:** bài tự luyện

```text
Chuyến(HAN, DAD)   Chuyến(DAD, SGN)   Khứ-hồi(SGN, PQC)
L1: Chuyến(X, Y) ← Khứ-hồi(X, Y)
L2: Chuyến(Y, X) ← Khứ-hồi(X, Y)
L3: Đến-được(X, Y) ← Chuyến(X, Y)
L4: Đến-được(X, Z) ← Đến-được(X, Y) ∧ Chuyến(Y, Z)
```
a) Cây chứng minh Đến-được(HAN, PQC). b) Điểm cố định.

<details class="ans"><summary>Đáp án</summary>

Viết tắt: H = HAN, D = DAD, S = SGN, P = PQC.
```text
B0: {Chuyến(H,D), Chuyến(D,S), Khứ-hồi(S,P)}
B1: + {Chuyến(S,P), Chuyến(P,S), Đến-được(H,D), Đến-được(D,S)}
      (L1, L2 với Khứ-hồi(S,P);  L3 với Chuyến(H,D), Chuyến(D,S))
B2: + {Đến-được(S,P), Đến-được(P,S), Đến-được(H,S), Đến-được(D,P)}
      (L3 với 2 chuyến mới;  L4: Đến(H,D)∧Chuyến(D,S);  Đến(D,S)∧Chuyến(S,P))
B3: + {Đến-được(H,P), Đến-được(P,P), Đến-được(S,S)}
      (L4: Đến(H,S)∧Chuyến(S,P);  Đến(P,S)∧Chuyến(S,P);  Đến(S,P)∧Chuyến(P,S))
B4: + {}   → Điểm cố định thu được ở Bước 3.
```
```text
Đến-được(H, P)                     [L4]
├── Đến-được(H, S)                 [L4]
│   ├── Đến-được(H, D)             [L3]
│   │   └── Chuyến(H, D)           (dữ kiện)
│   └── Chuyến(D, S)               (dữ kiện)
└── Chuyến(S, P)                   [L1]
    └── Khứ-hồi(S, P)              (dữ kiện)
```

</details>

### Luyện tập 3 — Luật RDFS viết bằng Datalog
> **Dạng:** D7 + D4 · **Nguồn:** bài tự luyện

```text
Rel(owns, anna, fido)   Domain(owns, Person)   Range(owns, Dog)
Sub(Dog, Mammal)   Sub(Mammal, Animal)
L1: Type(X, C) ← Rel(P, X, Y) ∧ Domain(P, C)        (rdfs2)
L2: Type(Y, C) ← Rel(P, X, Y) ∧ Range(P, C)         (rdfs3)
L3: Type(X, C) ← Type(X, B) ∧ Sub(B, C)             (rdfs9)
L4: Sub(A, C) ← Sub(A, B) ∧ Sub(B, C)               (rdfs11)
```
a) Cây chứng minh Type(fido, Animal). b) Điểm cố định.

<details class="ans"><summary>Đáp án</summary>

```text
B0: {Rel(owns,anna,fido), Domain(owns,Person), Range(owns,Dog), Sub(Dog,Mammal), Sub(Mammal,Animal)}
B1: + {Type(anna,Person), Type(fido,Dog), Sub(Dog,Animal)}          (L1, L2, L4)
B2: + {Type(fido,Mammal), Type(fido,Animal)}                        (L3 với Sub(Dog,Mammal), Sub(Dog,Animal))
B3: + {}   → Điểm cố định thu được ở Bước 2.
```
```text
Type(fido, Animal)                 [L3]
├── Type(fido, Dog)                [L2]
│   ├── Rel(owns, anna, fido)      (dữ kiện)
│   └── Range(owns, Dog)           (dữ kiện)
└── Sub(Dog, Animal)               [L4]
    ├── Sub(Dog, Mammal)           (dữ kiện)
    └── Sub(Mammal, Animal)        (dữ kiện)
```
Có một cây khác cũng đúng: đi qua Type(fido, Mammal) rồi dùng L3 với Sub(Mammal, Animal).

</details>
