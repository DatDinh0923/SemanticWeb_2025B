# 05 — Linked Open Data & Knowledge Modeling (★★)

> Slide: `04_LOD.pdf`, `07-Knowledge-Modeling.pdf` · Liên quan: đề Capstone (xây ứng dụng LOD 5 sao + SPARQL endpoint)
> Dạng bài: **D9** sửa lỗi mô hình (OntoClean, anti-pattern, sameAs) · **D10** thiết kế ứng dụng LOD · câu lý thuyết so sánh/giải thích

---

## Phần A — Linked Open Data (04_LOD)

### A1. Vì sao cần Linked Data (★★)
- Link HTML **không có kiểu** ("trang này trỏ tới trang kia" — vì sao?); link RDF **có kiểu** (`:Mannheim :locatedIn :Germany`) và URI **dereference được** ⇒ máy tự đi theo link để lấy thêm dữ liệu.

### A2. Bốn nguyên tắc Linked Data — Tim Berners-Lee 2006 (★★★ học thuộc)
1. **Use URIs as names for things** — dùng URI làm tên cho sự vật.
2. **Use HTTP URIs** so that people can look up those names — để tra được.
3. When someone looks up a URI, **provide useful information, using the standards** (RDF\*, SPARQL).
4. **Include links to other URIs**, so that they can discover more things.

### A3. Lược đồ 5 sao (Berners-Lee 2010) (★★★ học thuộc + ví dụ định dạng)
| Sao | Yêu cầu | Ví dụ | Lợi ích thêm / chi phí *(bổ sung, 5stardata.info)* |
|---|---|---|---|
| ★ | Có trên Web (định dạng bất kỳ) với **giấy phép mở** | PDF, ảnh scan | xem, in, lưu — người phát hành làm rất đơn giản |
| ★★ | Dữ liệu **có cấu trúc, máy đọc được** | Excel (XLS) | xử lý bằng phần mềm (tính toán, vẽ biểu đồ) |
| ★★★ | Định dạng **không độc quyền** | CSV | không phụ thuộc phần mềm cụ thể; cần bộ chuyển đổi |
| ★★★★ | Dùng **chuẩn mở W3C (RDF, SPARQL)** — **URI** để định danh sự vật | RDF | người khác trỏ tới, tái dùng một phần, ghép an toàn với dữ liệu khác; chi phí: phải gán URI, học RDF |
| ★★★★★ | **Liên kết** tới dữ liệu của người khác để cung cấp ngữ cảnh | LOD (RDF + `owl:sameAs`…) | khám phá thêm dữ liệu; chi phí: bảo trì link hỏng |

*Linked Data không nhất thiết "Open": có giấy phép mở mới là **Linked Open Data**.*

### A4. 9 best practices — Heath & Bizer 2011 (★★, slide tr. 24)
1. Provide **dereferencable URIs** · 2. Set **RDF links** pointing at other data sources · 3. Use terms from **widely deployed vocabularies** · 4. Make **proprietary vocabulary terms dereferencable** · 5. **Map proprietary terms** to other vocabularies · 6. Provide **provenance** metadata · 7. Provide **licensing** metadata · 8. Provide **data-set-level metadata** (VoID) · 9. Refer to **additional access methods** (SPARQL endpoint, dump).

*(bổ sung)* Ba loại link: **relationship links** (`foaf:knows`, `foaf:based_near`), **identity links** (`owl:sameAs`), **vocabulary links** (`rdfs:subClassOf`, `owl:equivalentClass`, `skos:exactMatch`).

### A5. `owl:sameAs` — dùng đúng và lạm dụng (★★★ — hay hỏi "chỉ ra lỗi")
- **Nghĩa:** hai URI chỉ **cùng một thực thể** ⇒ mọi phát biểu về URI này đúng cho URI kia (rất mạnh!).
- **Dùng đúng:** cùng một người trong DBpedia và trong dữ liệu của bạn.
- **Lạm dụng (ví dụ slide):** một người vs **trang chủ** của họ (dùng `foaf:homepage`); **một cửa hàng Starbucks** (quán ở O7) vs **công ty** Starbucks; **Hamburg** thành phố vs **bang**; quốc hội là **tổ chức** vs **tòa nhà**. Hậu quả: suy ra "tòa nhà quốc hội có 700 nghị sĩ", "công ty có giờ mở cửa"…
- **Thay thế:** `rdfs:seeAlso` (liên quan), `foaf:homepage`, `skos:closeMatch`, quan hệ riêng (`:hasHeadquarters`).

### A6. Bộ dữ liệu & từ vựng (★★)
| Bộ dữ liệu | Nguồn / đặc điểm |
|---|---|
| **DBpedia** | trích từ **infobox** Wikipedia; ontology ~1.800 lớp, ~1.200 object property, ~1.700 data property (số liệu slide); URI `dbpedia.org/resource/…` |
| **YAGO** | từ Wikipedia, dùng **categories** để gán kiểu (~500.000 kiểu) + **WordNet**; ~4,6M thực thể; biểu diễn thời gian bằng **reification** (cầu thủ chơi cho đội nào, khi nào) |
| **Wikidata** | cộng đồng biên tập; ~15M thực thể, ~23k lớp; có **provenance** (statement lấy từ đâu) |
| LinkedMDB, MusicBrainz, DBLP, GeoNames | phim, nhạc, thư mục khoa học, địa danh |

| Từ vựng | Prefix | Dùng cho |
|---|---|---|
| Dublin Core | `dc:` (1.1) / `dcterms:` | metadata tài liệu: `title`, `creator`, `publisher`, `date` |
| FOAF | `foaf:` | người: `Person`, `name`, `knows`, `homepage`, `mbox` |
| WGS84 Geo | `geo:` | `lat`, `long` |
| schema.org | `schema:` | dữ liệu nhúng trang web (Microdata/JSON-LD) |
| SKOS | `skos:` | thesaurus, phân loại: `Concept`, `broader`, `prefLabel` |
- Tra cứu: **LOV** (Linked Open Vocabularies), **prefix.cc**. **LOD Cloud**: >1.250 bộ dữ liệu (chính phủ, khoa học sự sống…).

### A7. Xuất bản Linked Data (★)
- **Pubby** đứng trước triple store để dereference URI; **D2R/D2RQ**: ánh xạ CSDL quan hệ → RDF ảo (`d2rq:ClassMap`, `d2rq:PropertyBridge`) — **virtual KG**.
- **Hash URI vs 303 URI** *(bổ sung, W3C Cool URIs)*: `…/about#alice` (client bỏ `#…`, server trả cả tài liệu; ít request; hợp cho tập nhỏ ổn định như ontology) vs `…/id/alice` → **303 See Other** → `…/doc/alice` (linh hoạt, 2 request; hợp cho tập lớn như DBpedia `/resource/` → `/page/`, `/data/`).
- schema.org/Microdata vs LOD: Microdata chỉ tạo cây blank node; chỉ ~0,02% nhà cung cấp dùng `schema:sameAs` ⇒ ít liên kết.
- Lập trình: **Jena** (`Model`, `Resource`, iterator — KG quá lớn để giữ list; `ModelFactory.createRDFSModel(schema, data)` để suy diễn), **rdflib** (`Graph`, `g.triples((None, RDF.type, FOAF.Person))`, `g.value`, `g.add`, `serialize`).

---

## Phần B — Knowledge Modeling (07)

### B1. Phương pháp luận (★★)
- **Ontology hacking vs ontology engineering** (làm tùy hứng vs có phương pháp, như kỹ nghệ phần mềm).
- **SECI** (Nonaka & Takeuchi): **tacit** knowledge (khó hình thức hóa — đi xe đạp) ↔ **explicit** knowledge (động học); tri thức tạo ra qua chuyển hóa qua lại, thường là quá trình hợp tác.
- **Grüninger & Fox (1995):** Motivating scenario → **Informal competency questions** (ngôn ngữ tự nhiên) → Terminology (FOL) → **Formal competency questions** (ví dụ **SPARQL** có kết quả mong đợi — *như unit test*) → Axioms (FOL) → Completeness theorems.
- **Methontology (Fernández 1997):** Glossary of terms → Concept taxonomies → Ad hoc binary relations → Concept dictionary → mô tả relations, instance/class attributes, constants, formal axioms, rules, instances. *Từng bước từ ít đến nhiều hình thức; được quay lui; tài liệu hóa dọc đường.*
- *(bổ sung)* **Ontology Development 101 (Noy & McGuinness):** 1) xác định miền & phạm vi (viết competency questions) 2) cân nhắc tái dùng 3) liệt kê thuật ngữ 4) định nghĩa lớp & phân cấp (top-down / bottom-up / kết hợp) 5) định nghĩa thuộc tính (slot) 6) định nghĩa facet (cardinality, kiểu giá trị, domain/range) 7) tạo cá thể.
- **Ví dụ SNOMED (slide):** `partOf` transitive + property chain `onBodyPart ∘ partOf ⊑ onBodyPart` ⇒ "mổ ngón tay là mổ bàn tay" (tốt) nhưng "**cắt cụt ngón tay là cắt cụt cả cánh tay**" (tệ!) ⇒ suy diễn tự động cần thiết kế cẩn thận.

### B2. OntoClean — Guarino & Welty (★★★ cho D9)
| Kiểm tra | Định nghĩa | Luật | Ví dụ lỗi (slide) | Cách sửa |
|---|---|---|---|---|
| **Rigidity** | lớp **rigid**: cá thể thuộc lớp "mãi mãi" — rời lớp là ngừng tồn tại (Person, Mountain, Company). **Non-rigid**: Student, Passenger, Caterpillar/Butterfly, Town | **Lớp rigid không được là lớp con của lớp non-rigid** (anti-rigid không bao lớp rigid) | `Person ⊑ Passenger`, `Animal ⊑ Passenger` ⇒ `:peter a :Person` suy ra Peter là hành khách | quan hệ `hasRole`: Person/Animal —hasRole→ Passenger |
| **Identity** | tiêu chí xác định hai thực thể là một (MSSV, mã số thuế, mã quốc gia) | **Lớp con không được có tiêu chí đồng nhất mà lớp cha không có** | `Interval ⊑ Duration` ⇒ `Mo10-11 sameAs 1h`, `Mo11-12 sameAs 1h` ⇒ `Mo10-11 sameAs Mo11-12` | `Interval —hasDuration→ Duration`. Tương tự: GeographicalObject/Country, Book/Edition/Copy |
| **Unity** | **unity class**: cá thể là "toàn thể" (người, thành phố); **anti-unity**: chia ra vẫn cùng loại (một lượng nước, một nhóm) | **unity chỉ có lớp con unity; anti-unity chỉ có lớp con anti-unity** | `Animal ⊑ OrganicMatter ⊑ AmountOfMatter` ⇒ "tập thú cưng của Peter" (gộp 2 con) cũng là Animal | `Animal —contains→ OrganicMatter` |

*(bổ sung, Guarino & Welty)* Ký hiệu meta-property: `+R` rigid, `~R` anti-rigid, `+I` có tiêu chí đồng nhất, `+O` tự cung cấp tiêu chí, `+U` unity, `~U` anti-unity, `+D` phụ thuộc. Bốn ràng buộc khi q bao p: ~R không bao +R; +I bao thì con cũng +I (cùng tiêu chí); +U bao thì con cũng +U; ~U bao thì con cũng ~U. Thêm: +D không bao −D. Ví dụ kinh điển: `Apple ⊑ Food` sai (Food là **vai trò** ~R, Apple rigid); Caterpillar/Butterfly cần lớp rigid chung **Lepidopteran**.

### B3. Design pattern (★★)
- Gốc: Christopher Alexander, *A Pattern Language* (1977) — vấn đề lặp lại + lời giải chuẩn có độ tự do (mưa vào nhà → mái: mái lệch, mái hai dốc…).
- **Presentation patterns** — quy ước đặt tên: **CamelCase**; lớp viết hoa, **danh từ số ít** (`City`); property viết thường, **động từ**, đọc một chiều rõ ràng (`isLocatedIn`, `isCapitalOf`); cá thể viết hoa (`Paris`); **label** cho mọi thứ.
- **Logical patterns** (độc lập miền, phụ thuộc ngôn ngữ) — ví dụ **quan hệ ba ngôi** r(X,Y,Z): `:X :hasR [ a :R ; :hasComp1 :Y ; :hasComp2 :Z ]`.
- **Content patterns** (phụ thuộc miền) — **RoleAtTime**: "Merkel là thủ tướng Đức 2005–2021" (Agent – RoleAtTime – Role – TimeInterval); competency question "ai giữ vai trò X tại thời điểm T?".
- **Transformation patterns** — chuyển ontology giữa các ngôn ngữ.

### B4. Anti-pattern (★★★ cho D9)
- **Rampant classism** — biến cá thể thành lớp: `:Goethe rdfs:subClassOf :Writer . :Faust rdfs:subClassOf :Drama . :Goethe :authorOf :Faust .` ⇒ reasoner DL **không suy ra được gì** (không phải DL hợp lệ). Kiểm tra: "X là **một** Goethe?" có nghĩa không; "Mọi Goethe đều là Writer?".
- **Exclusivity** — ontology chỉ nghĩ cho một miền: `CoastalCity ⊑ City`, `CoastalCity ≡ ∃bordering.Ocean` ⇒ `:Germany :bordering :AtlanticOcean` ⇒ **Germany là CoastalCity ⇒ là City**! Sửa: `CoastalCity ≡ City ⊓ ∃bordering.Ocean`. Gắn với nguyên tắc **AAA** — phát biểu phải đúng trong mọi ngữ cảnh. Ví dụ khác: "mỗi người kết hôn với tối đa một người" (sai ở nơi cho phép đa thê / theo thời gian).

### B5. Top-level ontology (★★)
- Mục tiêu: **độc lập miền và tác vụ**, rất tổng quát ⇒ tái dùng, rõ nghĩa, hướng dẫn mô hình hóa, **interoperability**. Phân loại ontology theo Guarino 1998: top-level → domain / task → application.
- Lịch sử: cây **Porphyry**; **hình vuông bản thể Aristotle** (universal/particular × substantial/not — ví dụ "cốc cà phê trắng").
- Các phân biệt: trừu tượng vs cụ thể; **3D vs 4D**; actualism vs possibilism; **co-location** (bức tượng và khối đất sét cùng chỗ; lỗ trong miếng phô mai).
- **Sowa (1999) — 12 phạm trù** = {Physical, Abstract} × {Continuant, Occurrent} × {Independent, Relative, Mediating}:

|  | Physical Continuant | Physical Occurrent | Abstract Continuant | Abstract Occurrent |
|---|---|---|---|---|
| **Independent** | Object | Process | Schema | Script |
| **Relative** | Juncture | Participation | Description | History |
| **Mediating** | Structure | Situation | Reason | Purpose |

  **Bài tập slide (+ đáp án đề xuất):** tòa nhà B6 → *Object*; buổi giảng hôm nay → *Process*; kỳ nghỉ giữa hai học kỳ → *Situation*; động lực đi học của bạn → *Purpose*.
- **DOLCE** (WonderWeb 2002–2004; lõi 37 lớp/70 quan hệ): ontology của **particulars**, possibilistic, 4D, cho phép co-location (tượng + đất sét, không phải hai tượng).
  - 4 lớp đỉnh rời nhau: **Endurant** (tồn tại trọn vẹn tại mỗi thời điểm — người, sách, tổ chức) · **Perdurant** ("xảy ra" — sự kiện, quá trình) · **Quality** (màu, chiều cao — gắn với một thực thể) · **Abstract** (số, đơn vị).
  - Endurant *tham gia* Perdurant (chủ động: người đọc; bị động: cuốn sách). Endurant chỉ gồm endurant; perdurant chỉ gồm perdurant.
  - **Amount of Matter vs Physical Object** (một phần nước vẫn là nước; một phần cái cốc không là cốc ↔ unity của OntoClean); **Feature** (lỗ, mép — không tồn tại độc lập).
  - Perdurant: **Event** (Achievement — không chia được "chạm biên giới"; Accomplishment — chia được "đi Trung Quốc") vs **Stative** (State — "ngồi chơi", gộp hai lần vẫn là ngồi chơi; Process — "học" gồm nghe giảng, làm dự án…).
  - **Quality vs quality space:** mỗi chiếc xe có quality "màu" **riêng**; hai xe "cùng màu" = hai quality có cùng **giá trị** trong không gian RGB (nếu dùng chung thì xe này mất, xe kia mất màu!).
- SUMO, Cyc, PROTON; DBpedia + DOLCE: **24,4%** khẳng định DBpedia vi phạm ontology kết hợp ⇒ top-level ontology giúp phát hiện lỗi dữ liệu.

---

## Phần C — Bài giải & tự luyện

**L1 (D9). Ontology giao thông: `Passenger ⊒ Person`, `Passenger ⊒ Animal`. Chỉ ra lỗi và sửa.**
<details><summary>Đáp án</summary>

Vi phạm **rigidity**: Person, Animal rigid; Passenger anti-rigid (một người chỉ là hành khách khi đang đi xe) ⇒ không được làm lớp cha. Hậu quả: mọi Person bị suy ra là Passenger. Sửa: `Person —hasRole→ PassengerRole` (hoặc `Passenger ≡ ∃travelsOn.Vehicle` và **không** đặt Person dưới Passenger).
</details>

**L2 (D9). `BookCopy ⊑ Book`? `BookEdition ⊑ Book`? (slide 07 ghi "Book > Book edition", "Book > Book copy") Áp dụng tiêu chí đồng nhất.**
<details><summary>Đáp án</summary>

Book đồng nhất theo (tiêu đề, tác giả)/ISBN; Edition theo ISBN hoặc (tiêu đề, tác giả, số lần in); Copy theo **mã kiểm kê**. Lớp con có tiêu chí lớp cha không có ⇒ vi phạm identity ⇒ dùng quan hệ: `Copy —isCopyOf→ Edition —isEditionOf→ Book`.
</details>

**L3 (D10). Thiết kế ứng dụng LOD "Di sản Hà Nội" đạt 5 sao (giống đề Capstone).**
<details><summary>Dàn ý trả lời</summary>

1. **Nguồn**: CSV danh sách di tích (★★★) → chuyển RDF (★★★★) bằng script/RML; giấy phép CC-BY (★).
2. **URI**: `http://data.example.vn/heritage/resource/VanMieu` (303 → `/page/`, `/data/`) cho cá thể; hash URI cho ontology `…/ontology#Temple`.
3. **Vocabulary**: tái dùng `schema:LandmarksOrHistoricalBuildings`, `geo:lat/long`, `dcterms:created`, `rdfs:label "Văn Miếu"@vi, "Temple of Literature"@en`; lớp riêng map bằng `rdfs:subClassOf schema:Place`.
4. **Link (★★★★★)**: `owl:sameAs dbpedia:Temple_of_Literature,_Hanoi`, `wikidata:Q…`; `:locatedIn` → GeoNames. Kiểm tra sameAs đúng thực thể (không trỏ vào trang web!).
5. **Truy cập**: SPARQL endpoint (Fuseki), dump `.ttl`, VoID mô tả dataset (license, nguồn, số triple) — best practice 6–9.
6. **Competency questions → SPARQL**: "di tích nào xây trước 1500?", "di tích trong quận Đống Đa"… (formal CQ = unit test).
</details>

**L4. Xếp các thực thể vào 12 phạm trù Sowa: (a) chiếc điện thoại của bạn (b) trận chung kết World Cup 2022 (c) định lý Pythagoras (d) hợp đồng thuê nhà (e) mục tiêu tốt nghiệp của bạn.**
<details><summary>Đáp án đề xuất</summary>

(a) Physical-Continuant-Independent → **Object** (b) Physical-Occurrent-Independent → **Process** (c) Abstract-Continuant-Independent → **Schema** (d) Abstract-Continuant-Mediating → **Reason**? hoặc Physical-Continuant-Mediating → **Structure** (văn bản hợp đồng như thực thể vật lý liên kết hai bên) — câu mở, chấm theo lập luận (e) Abstract-Occurrent-Mediating → **Purpose**.
</details>

**L5. So sánh hash URI và 303 URI; nêu khi nào chọn mỗi loại.** → xem A7.

---
**Nguồn:** slide 04_LOD, 07-Knowledge-Modeling (Paulheim, IE650). *(bổ sung)* Berners-Lee, *Linked Data — Design Issues* https://www.w3.org/DesignIssues/LinkedData.html · https://5stardata.info/ · Heath & Bizer, *Linked Data* (2011) https://linkeddatabook.com/editions/1.0/ · W3C *Cool URIs for the Semantic Web* https://www.w3.org/TR/cooluris/ · Guarino & Welty, *An Overview of OntoClean* · Noy & McGuinness, *Ontology Development 101*.
