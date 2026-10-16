## Semantic Web là gì? (1 câu)

**Viết dữ liệu theo cách máy "hiểu" được**: mọi thông tin đều viết thành những câu cực ngắn **chủ ngữ – vị ngữ – tân ngữ**. Sau đó máy có thể **tự suy ra** thông tin mới, **trả lời câu hỏi**, và **kiểm tra** dữ liệu có đúng khuôn không.

Cả môn học chỉ có **5 việc**. 12 dạng bài thi đều nằm trong 5 việc này. Bấm vào mã dạng (chữ gạch chân) trong hình để mở dạng đó.

<div class="tq-wrap"><svg class="tq" viewBox="0 0 900 400" role="img" aria-label="Sơ đồ 5 việc của Semantic Web và 12 dạng bài">
<defs><marker id="tqa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="tq-arrowhead"/></marker></defs>
<g class="tq-box"><rect x="20" y="20" width="250" height="150" rx="12"/><text x="36" y="50" class="tq-h">① DỮ LIỆU · RDF</text><text x="36" y="76">viết sự thật thành bộ-3</text><text x="36" y="96">:hung :teaches :SW .</text><text x="36" y="116" class="tq-s">(Turtle, vẽ đồ thị)</text><text x="36" y="152" class="tq-s">Dạng:</text><a href="#D1"><text x="84" y="152" class="tq-code">D1</text></a><a href="#D2"><text x="114" y="152" class="tq-code">D2</text></a></g>
<g class="tq-box"><rect x="20" y="230" width="250" height="150" rx="12"/><text x="36" y="260" class="tq-h">② ĐỊNH NGHĨA · RDFS / OWL</text><text x="36" y="286">có những lớp, thuộc tính nào,</text><text x="36" y="306">luật giữa chúng là gì</text><text x="36" y="326" class="tq-s">"Giáo viên là một Người"</text><text x="36" y="362" class="tq-s">Dạng:</text><a href="#D3"><text x="84" y="362" class="tq-code">D3</text></a><a href="#D5"><text x="114" y="362" class="tq-code">D5</text></a></g>
<g class="tq-box tq-main"><rect x="330" y="110" width="250" height="180" rx="12"/><text x="346" y="140" class="tq-h">③ SUY DIỄN · reasoner</text><text x="346" y="166">máy tự rút ra sự thật mới</text><text x="346" y="186">từ ① + ②</text><text x="346" y="206" class="tq-s">"hung dạy ⇒ hung là Giáo viên</text><text x="346" y="224" class="tq-s"> ⇒ hung là Người"</text><text x="346" y="272" class="tq-s">Dạng:</text><a href="#D4"><text x="394" y="272" class="tq-code">D4</text></a><a href="#D6"><text x="424" y="272" class="tq-code">D6</text></a><a href="#D12"><text x="454" y="272" class="tq-code">D12</text></a><a href="#D7"><text x="494" y="272" class="tq-code">D7</text></a><a href="#D11"><text x="524" y="272" class="tq-code">D11</text></a></g>
<g class="tq-box"><rect x="640" y="20" width="240" height="150" rx="12"/><text x="656" y="50" class="tq-h">④ HỎI · SPARQL</text><text x="656" y="76">lấy dữ liệu ra, giống SQL</text><text x="656" y="96" class="tq-s">"ai dạy môn SW?"</text><text x="656" y="116" class="tq-s">+ đại số: máy chạy từng bước</text><text x="656" y="152" class="tq-s">Dạng:</text><a href="#D8"><text x="704" y="152" class="tq-code">D8 (2.5đ)</text></a><a href="#D9"><text x="790" y="152" class="tq-code">D9</text></a></g>
<g class="tq-box"><rect x="640" y="230" width="240" height="150" rx="12"/><text x="656" y="260" class="tq-h">⑤ KIỂM TRA · SHACL</text><text x="656" y="286">dữ liệu có đúng khuôn không</text><text x="656" y="306" class="tq-s">"mỗi giáo viên phải có tên"</text><text x="656" y="362" class="tq-s">Dạng:</text><a href="#D10"><text x="704" y="362" class="tq-code">D10</text></a></g>
<path d="M270,95 C300,95 300,170 328,170" class="tq-line" marker-end="url(#tqa)"/>
<path d="M270,305 C300,305 300,230 328,230" class="tq-line" marker-end="url(#tqa)"/>
<path d="M580,170 C610,170 610,95 638,95" class="tq-line" marker-end="url(#tqa)"/>
<path d="M580,230 C610,230 610,305 638,305" class="tq-line" marker-end="url(#tqa)"/>
</svg></div>

## 1 ví dụ đi xuyên cả 5 việc

Đề kể: *"Thầy Hùng dạy môn Semantic Web."*

**① Dữ liệu (RDF, dạng D1, D2).** Viết thành bộ-3 rồi vẽ thành đồ thị. Hình elip là **tên** của sự vật (IRI), hình chữ nhật là **giá trị** (literal), mũi tên là **quan hệ**.

```turtle graph
@prefix : <http://example.org/> .
:hung :teaches :SW ; :name "Hùng" .
:SW :title "Semantic Web" .
```

**② Định nghĩa (RDFS / OWL, dạng D3, D5).** Nói cho máy biết từ vựng nghĩa là gì:

```turtle
@prefix : <http://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
:teaches rdfs:domain :Teacher .        # ai "dạy" thì người đó là Teacher
:Teacher rdfs:subClassOf :Person .     # Teacher là một loại Person
:Teacher owl:disjointWith :Student .   # (OWL) không ai vừa là Teacher vừa là Student
```

**③ Suy diễn (dạng D4, D6, D12, D7, D11).** Máy (reasoner) tự suy ra **những điều không ai viết ra**:

- `:hung a :Teacher`, vì hung dạy và domain của "dạy" là Teacher (luật **rdfs2**).
- `:hung a :Person`, vì Teacher là một loại Person (luật **rdfs9**).
- Nếu ai đó ghi thêm `:hung a :Student` thì máy báo **mâu thuẫn** (OWL).

Bài thi bắt bạn **viết ra các bước suy luận đó**. Dạng D4 dùng luật RDFS, D6 dùng OWL, D12 dùng tableau (chứng minh bằng cây), D7 dùng Datalog (luật nếu–thì). D11 là câu lý thuyết "reasoner làm được gì".

**④ Hỏi (SPARQL, dạng D8, D9).** Viết câu hỏi có **chỗ trống** `?x`, máy tìm mọi cách điền:

```sparql
PREFIX : <http://example.org/>
SELECT ?x WHERE { ?x :teaches :SW . }      # → :hung
```

Dạng D9 bắt bạn giải thích máy chạy câu hỏi đó **từng bước** (BGP → Join → Filter → Project), mỗi bước là một bảng.

**⑤ Kiểm tra (SHACL, dạng D10).** Đặt khuôn "mỗi Teacher phải có ít nhất 1 tên". Máy chỉ ra **ai thiếu**:

```turtle
@prefix : <http://example.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
:TeacherShape a sh:NodeShape ; sh:targetClass :Teacher ;
  sh:property [ sh:path :name ; sh:minCount 1 ] .
```

## 7 từ phải hiểu trước khi học tiếp

| Từ | Nghĩa đơn giản | Ví dụ |
|---|---|---|
| **Triple (bộ-3)** | 1 câu: chủ ngữ – vị ngữ – tân ngữ | `:hung :teaches :SW .` |
| **IRI** | tên duy nhất của một sự vật (giống địa chỉ web) | `:hung`, `foaf:name` |
| **Literal** | một giá trị: chữ, số, ngày | `"Hùng"`, `10` |
| **Blank node** | sự vật **không có tên** ("một người nào đó") | `[ a :Teacher ]` |
| **Lớp (Class)** | một nhóm sự vật | `:Teacher`, `:Person` |
| **Thuộc tính (Property)** | loại quan hệ | `:teaches` |
| **Cá thể (Instance)** | một sự vật cụ thể thuộc lớp | `:hung a :Teacher` |

**Turtle** là cách viết các bộ-3 cho gọn: `;` = cùng chủ ngữ, `,` = cùng chủ ngữ và vị ngữ, `a` = "là một", `.` = hết câu.

## Đề thi gồm gì?

- Đề cũ: **5 câu tự luận** (nhiều ý nhỏ), được mang tài liệu giấy. Mỗi câu rơi vào **1 ô** trong sơ đồ trên.
- Có **1 câu 2.5 điểm chỉ viết SPARQL** (ô ④) *(nghe nói)*. Đây là câu nặng điểm nhất.
- Cách làm bài: đọc câu hỏi → xem nó thuộc ô nào (bảng **Bản đồ đề thi** ở trang **⌂ Bắt đầu**) → mở dạng đó → làm theo **khuôn**.

## Học theo thứ tự nào?

Học theo **từng ngôn ngữ**, từ đơn giản đến phức tạp. Mỗi ngôn ngữ có phần "viết" và phần "suy diễn":

1. **RDF & RDFS:** D1 viết Turtle → D2 chuyển đổi → D3 schema → D4 suy diễn RDFS.
2. **OWL:** D5 viết ontology + DL → D6 suy diễn OWL → D12 tableau.
3. **Datalog:** D7 (luật nếu–thì, cùng ý tưởng "áp luật đến điểm cố định" như D4).
4. **SPARQL:** D8 viết truy vấn (câu 2.5đ) → D9 đại số.
5. **SHACL:** D10. Cuối cùng là **D11** lý thuyết.

Menu bên trái, lộ trình ở trang ⌂ và nút **Tiếp theo →** cuối mỗi trang đều đi đúng thứ tự này. Xong 12 dạng thì làm 3 **Luyện đề** (chia 8 câu để luyện).
