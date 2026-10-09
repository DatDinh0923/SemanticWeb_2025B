# Tổng quan dự án: Premier League Linked Open Data

> Tài liệu tổng hợp cho nhóm: (1) nhánh `main` được ghép từ 3 branch như thế nào,
> (2) toàn bộ pipeline xử lý, (3) kiến thức Semantic Web dùng ở từng bước và lý do
> chọn cách làm, (4) bộ câu hỏi – trả lời để ôn tập / bảo vệ.

---

## Mục lục

1. [Bài toán và kết quả cuối cùng](#1-bài-toán-và-kết-quả-cuối-cùng)
2. [Nhánh main được ghép từ 3 branch như thế nào](#2-nhánh-main-được-ghép-từ-3-branch-như-thế-nào)
3. [Full pipeline xử lý](#3-full-pipeline-xử-lý)
4. [Kiến thức Semantic Web trong pipeline và lý do lựa chọn](#4-kiến-thức-semantic-web-trong-pipeline-và-lý-do-lựa-chọn)
5. [Câu hỏi – trả lời](#5-câu-hỏi--trả-lời)

---

## 1. Bài toán và kết quả cuối cùng

Đề bài yêu cầu 5 việc: (1) định nghĩa ontology, (2) thu thập dữ liệu, (3) chuyển
dữ liệu lên mức 4 sao, (4) liên kết sang dataset khác để đạt 5 sao, (5) dựng SPARQL
endpoint / terminal.

Kết quả trên `main`:

| Hạng mục | Số liệu |
| --- | --- |
| Phạm vi | Premier League, 10 mùa 2011/12 → 2020/21 |
| Thực thể | 1 giải đấu, 10 mùa, 35 CLB, 3.800 trận (908 trận hòa) |
| RDF | 52.609 triple dữ liệu (52.815 khi gộp ontology) |
| Liên kết ngoài | 46 thực thể × 2 = 92 `owl:sameAs` sang Wikidata + DBpedia |
| Truy vấn | 16 competency question + 1 truy vấn federated sang Wikidata |
| Kiểm thử | 61 unit test, SHACL, CI GitHub Actions |
| Xuất bản | Static Linked Data site trên GitHub Pages, Fuseki qua Docker |

Nguồn dữ liệu: [footballcsv/england](https://github.com/footballcsv/england)
(CC0, public domain), lưu nguyên bản trong `england_csv/`.

---

## 2. Nhánh main được ghép từ 3 branch như thế nào

### 2.1. Lịch sử commit

```text
f67dc63  (DatDQ)  first commit, using csv data, clean data          ← gốc chung của cả 3 branch
 │
 ├── dqdat-dev (DatDQ)
 │     c92403d  ontology, SHACL, CQ, Fuseki, link Wikidata/DBpedia (bản nháp)
 │     23408ef  sửa CQ 1, 3, 8, kiểm tra bằng Fuseki
 │     0642a7f  publication readiness, pipeline tái lập được
 │
 ├── hung (mhungdangbuonngu)
 │     2b3e89f  pipeline 5 sao: ontology, RDF, link Wikidata, Fuseki
 │     70a8f70  SHACL + metadata VoID/DCAT
 │
 └── phongph5 (phongph)
       f6aa34a  ontology: competition / season / team / match
       f18d8b0  chuẩn hoá 10 mùa Premier League + bảng alias CLB
       500a45f  RDF tất định, provenance, SHACL
       4d1c782  xác minh 36 định danh với Wikidata/DBpedia (có evidence)
       ef0a2c8  10 truy vấn tham số hoá, Fuseki portable
       7166d0d  acceptance test offline + hướng dẫn tiếng Việt
       bb4e08c  chuẩn hoá line ending cho file sinh ra

main = dqdat-dev
     + f9c4b40  (DatDQ)    "update ideas from hung branch while keeping the data to 2018/19"
     + c51b8af  (Insomnia) "adding from hung and phong"   ← commit ghép chính, 98 file
     + bd32135  (Insomnia) bật GitHub Pages / Actions
```

Lưu ý: **main không dùng `git merge`**. Main là dòng commit thẳng của `dqdat-dev`,
sau đó ý tưởng/code của `hung` và `phongph5` được **chép tay và viết lại** vào hai
commit `f9c4b40` và `c51b8af`. Vì vậy `git log main` không thấy commit của hung và
phong, và nhiều file của hai nhánh đó (ví dụ `src/to_rdf.py`, `src/link_wikidata.py`,
`src/pipeline.py`, `src/common.py`) **không còn** trên main — chức năng của chúng đã
được gộp vào các file của nhánh dqdat-dev.

### 2.2. Mỗi branch đóng góp gì vào main

| Branch | Phần được giữ trên main | File trên main |
| --- | --- | --- |
| **dqdat-dev** (khung chính) | Namespace HTTP URI `https://datdinh0923.github.io/SemanticWeb_2025B/`; static Linked Data site; metadata DCAT/VoID/PROV; SHACL shapes; Fuseki chạy bằng Docker; CI; cách viết test; bộ competency question; `suggest_links.py` | `src/convert_to_rdf.py`, `src/build_site.py`, `src/validate_rdf.py`, `src/load_fuseki.py`, `src/run_sparql.py`, `src/suggest_links.py`, `docker-compose.yml`, `.github/workflows/*`, `Makefile` |
| **phongph5** (phạm vi dữ liệu + độ tin cậy) | Phạm vi 10 mùa Premier League; manifest mùa giải; bảng alias CLB (54 cách viết → 35 CLB); provenance tới từng dòng CSV; file evidence cho mỗi liên kết; kiểm tra bảng xếp hạng so với tính toán độc lập từ CSV gốc; kiểm tra double round-robin | `config/seasons.csv`, `config/team-aliases.csv`, logic trong `src/clean_data.py`, `data/links/evidence/`, test trong `src/test_*.py` |
| **hung** (ontology giàu ngữ nghĩa) | Tiên đề OWL: qualified cardinality, disjointness, cây thuộc tính `participant`, property chain, lớp `League`/`Cup`/`Draw`, `tier`, `stage`, `winner`/`loser`; VoID class partition; truy vấn federated sang Wikidata | `ontology/football.ttl`, `queries/16-ontology-reasoning.rq`, `queries/federated/wikidata-club-facts.rq`, phần VoID trong `convert_to_rdf.py` |
| **Mới trong commit ghép** | Mở rộng liên kết từ 36 (phong: 1 giải + 35 CLB) lên 46 (thêm 10 mùa); script thu thập evidence tự động | `src/collect_link_evidence.py`, `data/links/entity-links.csv` |

### 2.3. Phần **không** được đưa vào main và lý do

- **Hạng dưới (Championship, League One/Two, National League) và FA Cup** từ nhánh
  `hung`: bị loại vì các *phoenix club* (CLB giải thể rồi lập lại với tên gần giống)
  bị gộp sai định danh và link sai Wikidata, ví dụ Halifax Town AFC (giải thể 2008) và
  FC Halifax Town (lập 2008), Chester City và Chester FC. Một `owl:sameAs` sai tệ hơn
  không có link (xem mục 4.6).
- **Các script riêng** (`to_rdf.py`, `query.py`, `validate.py`, `link_wikidata.py`
  của hung; `pipeline.py`, `common.py`, `scripts/*.ps1` của phong): chức năng trùng,
  đã gộp vào bộ script của dqdat-dev.
- **`data/rdf/links.ttl`, `void.ttl` tách rời**: main sinh một file duy nhất
  `data/rdf/football-data.ttl` chứa cả dữ liệu, link và metadata.

### 2.4. File chưa commit trong working tree

`docs/GIAI_THICH.md`, `run/` và `tools/apache-jena-fuseki-6.2.0/` là file local chưa
được track (Fuseki portable để chạy không cần Docker). Chúng không thuộc pipeline
chính thức trên main.

---

## 3. Full pipeline xử lý

### 3.1. Sơ đồ tổng quát

```text
england_csv/**/eng.1.csv  (10 file gốc, không sửa)
   │   + config/seasons.csv        (manifest: mùa nào, file nào, kỳ vọng 380 trận / 20 đội)
   │   + config/team-aliases.csv   (54 cách viết tên → 35 ID CLB)
   ▼
[1] src/clean_data.py ───────────► data/processed/{matches,teams,seasons,competitions}.csv
   ▼
[2] src/convert_to_rdf.py ◄────── data/links/entity-links.csv + data/links/evidence/*.json
   │                               (sinh offline bởi [0] collect_link_evidence.py)
   ▼
   data/rdf/football-data.ttl   (RDF Turtle: dữ liệu + owl:sameAs + DCAT/VoID/PROV)
   ▼
[3] src/validate_rdf.py  (pySHACL + shapes/football-shapes.ttl + ontology)
   │                     ──► data/rdf/validation-report.ttl
   ▼
[4] unittest (61 test)   ──► kiểm tra từng bước + tái lập byte-for-byte
   ▼
[5] src/build_site.py    ──► _site/  (mỗi URI một trang HTML + data.ttl + JSON-LD)
   ▼
[6] Truy vấn:  src/run_sparql.py (rdflib, offline)
              Fuseki (docker compose + src/load_fuseki.py)  → http://localhost:3030/football/sparql
              queries/federated/*.rq  → SERVICE sang query.wikidata.org
```

`make pipeline` = `clean-data → rdf → validate → test → site`, chạy hoàn toàn offline.
CI (`.github/workflows/ci.yml`) chạy `make pipeline` rồi `git diff --exit-code` trên
`data/processed` và `data/rdf` để đảm bảo file commit đúng bằng file sinh lại.
`pages.yml` build `_site/` và deploy lên GitHub Pages khi push `main`.

### 3.2. Bước 0 (offline, chạy tay khi cần) – Tìm và xác minh liên kết ngoài

- `src/suggest_links.py`: gọi Wikidata search API, ghi ứng viên vào
  `data/links/wikidata-suggestions.csv` (bị `.gitignore`, trạng thái `unverified`).
  Không bao giờ ghi đè file link đã xác minh.
- `src/collect_link_evidence.py`: với mỗi dòng trong `entity-links.csv`, tải entity
  Wikidata (JSON) và hỏi DBpedia SPARQL endpoint, rồi chạy các kiểm tra:

  | Kiểm tra | Bắt lỗi gì |
  | --- | --- |
  | `wikidata_type_matches` – P31 là CLB/đội bóng, giải bóng đá, hoặc mùa giải | trang định hướng, người, sân vận động |
  | `wikidata_sport_is_association_football` – P641 = Q2736 | môn thể thao khác trùng tên |
  | `wikidata_season_of_premier_league` – P3450 = Q9448 (chỉ cho mùa) | mùa Premier League của Bosnia… |
  | `wikipedia_title_matches_dbpedia` | Wikidata và DBpedia trỏ hai thứ khác nhau |
  | `dbpedia_links_to_wikidata` – `owl:sameAs` của DBpedia trỏ ngược về đúng Q-id | cặp link lệch nhau |

  Kết quả lưu vào `data/links/evidence/<type>/<id>.json` (kèm revision Wikidata).
  Chỉ khi chạy `--promote` và **mọi** check pass thì dòng mới chuyển sang `verified`.

### 3.3. Bước 1 – Làm sạch dữ liệu (`src/clean_data.py`)

Input: 10 file CSV với cột `Round, Date, Team 1, FT, Team 2`.

1. `load_manifest`: đọc `config/seasons.csv`, kiểm tra `season_id` hợp lệ, không trùng
   ID / trùng file.
2. `load_aliases`: đọc bảng alias; tên chuẩn phải *slugify* ra đúng `team_id`
   (`"Arsenal FC"` → `arsenal`), một ID không được có hai tên.
3. `load_matches`: với từng dòng:
   - parse ngày dạng `Sat Aug 11 2018` → ISO `2018-08-11`, **kiểm tra thứ trong tuần**
     khớp với ngày;
   - parse tỉ số `2-1` → (2, 1);
   - tên đội phải có trong bảng alias, nếu không → dừng và báo **file + số dòng**,
     không tự đoán;
   - sinh `match_id = <ngày>-<đội nhà>-<đội khách>`, kiểm tra không trùng;
   - ghi lại `source_file`, `source_line` (provenance).
4. `validate_season`: mỗi mùa phải là **double round-robin hoàn chỉnh**: 380 trận,
   20 đội, 380 cặp sân nhà/sân khách khác nhau, mỗi đội 19 trận sân nhà + 19 sân khách,
   38 vòng mỗi vòng 10 trận.
5. Tính `start_date`/`end_date` của mùa từ ngày trận sớm/muộn nhất.
6. Ghi 4 bảng chuẩn hoá vào `data/processed/`.

### 3.4. Bước 2 – Chuyển sang RDF (`src/convert_to_rdf.py`)

Dùng `rdflib`. Mỗi hàng CSV thành một tài nguyên có **HTTP URI**:

| Thực thể | Mẫu URI |
| --- | --- |
| Ontology | `…/SemanticWeb_2025B/ontology/` (prefix `foot:`) |
| Giải | `…/resource/competition/premier-league` |
| Mùa | `…/resource/season/premier-league-2018-19` |
| CLB | `…/resource/team/arsenal` |
| Trận | `…/resource/match/2018-08-10-manchester-united-leicester-city` |
| Dataset | `…/dataset/premier-league` |

Ví dụ một trận sau khi chuyển:

```turtle
match:2018-08-10-manchester-united-leicester-city a foot:FootballMatch ;
    rdfs:label "Manchester United FC 2–1 Leicester City FC"@en ;
    foot:homeTeam team:manchester-united ;
    foot:awayTeam team:leicester-city ;
    foot:homeGoals "2"^^xsd:nonNegativeInteger ;
    foot:awayGoals "1"^^xsd:nonNegativeInteger ;
    foot:winner team:manchester-united ;
    foot:loser  team:leicester-city ;
    foot:matchDate "2018-08-10"^^xsd:date ;
    foot:roundNumber "1"^^xsd:positiveInteger ;
    foot:playedInSeason season:premier-league-2018-19 ;
    foot:partOfCompetition competition:premier-league ;
    prov:wasDerivedFrom <https://github.com/footballcsv/england/blob/master/2010s/2018-19/eng.1.csv> ;
    foot:sourceLine "2"^^xsd:positiveInteger .
```

Các việc chính:

- Literal có **datatype XSD** (`xsd:date`, `xsd:nonNegativeInteger`,
  `xsd:positiveInteger`) và tên có **language tag** `@en`.
- Suy ra kết quả từ tỉ số: hòa → thêm `rdf:type foot:Draw`; thắng/thua → `foot:winner`,
  `foot:loser`.
- Ghi `foot:partOfCompetition` cho cả trận (dù OWL có thể suy ra) để SPARQL thường chạy
  được mà không cần reasoner.
- `add_external_links`: chỉ thêm `owl:sameAs` khi dòng link `verified`, có ngày xác
  minh, evidence tồn tại, evidence khớp đúng URI và mọi check `true`. Mỗi thực thể
  phải có đúng 1 link Wikidata + 1 link DBpedia, không target nào bị dùng hai lần,
  không thực thể nào thiếu link.
- Metadata: `dcat:Dataset` + `dcat:Distribution`, `void:Dataset` (dataDump, uriSpace,
  vocabulary, triples, entities, 5 classPartition), 2 `void:Linkset` (Wikidata,
  DBpedia), `prov:Activity` cho quá trình chuyển đổi, `dcterms:license` CC0.
- Output tất định (cùng input → cùng file), nên CI so sánh được bằng `git diff`.

### 3.5. Bước 3 – Kiểm tra bằng SHACL (`src/validate_rdf.py`)

pySHACL chạy `shapes/football-shapes.ttl` trên dữ liệu (kèm ontology, suy diễn
`rdfs`). Hai nhóm ràng buộc:

- **SHACL Core theo từng tài nguyên**: số lượng (`sh:minCount`/`sh:maxCount`), kiểu
  dữ liệu, `sh:class`, `sh:nodeKind sh:IRI`, `sh:pattern` (nhãn mùa `^\d{4}/\d{2}$`,
  URI Wikidata/DBpedia), `sh:disjoint` (đội nhà ≠ đội khách), `sh:lessThan`
  (`startDate < endDate`), `roundNumber` trong 1..38, `sh:qualifiedValueShape` (đúng 1
  link Wikidata và đúng 1 link DBpedia), `Draw` không có winner/loser.
- **SHACL-SPARQL cấp dataset** (chạy một lần trên cả graph): ngày trận nằm trong mùa;
  trận và mùa cùng giải; kiểu `Draw` khớp tỉ số; winner/loser khớp tỉ số; trận và mùa
  cùng file nguồn; không có cặp sân nhà/sân khách lặp trong một mùa.

Báo cáo ghi ra `data/rdf/validation-report.ttl`; không conform → exit code 1, pipeline
dừng.

### 3.6. Bước 4 – Test (`src/test_*.py`, 61 test)

Bao gồm: dữ liệu hỏng phải bị từ chối (đúng file + dòng), link chưa xác minh / trùng /
thiếu phải bị từ chối, SHACL phải bắt được dữ liệu cố tình làm sai, bảng xếp hạng cả 10
mùa tính bằng SPARQL phải trùng với bảng tính trực tiếp từ CSV gốc, truy vấn vô địch
phải ra đúng nhà vô địch thật, pipeline tái lập file commit byte-for-byte.

### 3.7. Bước 5 – Static Linked Data site (`src/build_site.py`)

Với **mỗi URI** trong namespace của dự án, sinh `_site/<đường dẫn>/index.html`:
bảng triple của tài nguyên, file `data.ttl` riêng, JSON-LD nhúng trong
`<script type="application/ld+json">`, và danh sách tài nguyên trỏ *đến* nó (liên
kết ngược). Thêm trang chủ và `download/football-data.ttl`. GitHub Pages phục vụ thư
mục này, nên mở URI trong trình duyệt là ra mô tả của tài nguyên → URI
**dereferenceable**.

### 3.8. Bước 6 – Truy vấn SPARQL

- **Terminal offline**: `python src/run_sparql.py --all` nạp dữ liệu + ontology vào
  rdflib và chạy 16 file `queries/*.rq`.
- **Endpoint**: `docker compose up -d` (Fuseki 5.1, TDB2, bind `127.0.0.1:3030`),
  `python src/load_fuseki.py` nạp dữ liệu + ontology vào default graph;
  `python src/run_sparql.py --all --endpoint` cho kết quả giống hệt bản offline.
  `fuseki/server.ttl` bật `arq:httpServiceAllowed` và timeout 30s/120s.
- **Federated**: `queries/federated/wikidata-club-facts.rq` đi theo `owl:sameAs` sang
  `SERVICE <https://query.wikidata.org/sparql>` để lấy sân nhà (P115) và năm thành lập
  (P571) của các CLB mùa 2018/19. Chạy qua rdflib (Fuseki bị Wikidata chặn user-agent
  Java, HTTP 403).

Các nhóm câu hỏi: trong 1 mùa (CQ1, 2, 4, 5, 6, 11), xuyên mùa (CQ3, 7, 8, 9, 12, 13,
14, 15), linked data / ontology (CQ10, 16, 17). Mọi số liệu tổng hợp (bảng xếp hạng,
vô địch, thống kê) đều **tính bằng SPARQL**, không lưu sẵn trong RDF.

---

## 4. Kiến thức Semantic Web trong pipeline và lý do lựa chọn

### 4.1. Linked Data và thang 5 sao

Bốn nguyên tắc Linked Data của Tim Berners-Lee: (1) dùng URI để đặt tên cho sự vật,
(2) dùng **HTTP** URI để tra được, (3) khi tra URI phải trả về thông tin hữu ích theo
chuẩn (RDF, SPARQL), (4) chứa link sang URI khác để khám phá thêm.

| Sao | Ý nghĩa | Dự án đáp ứng bằng |
| --- | --- | --- |
| ★ | Dữ liệu mở trên web, có license mở | CC0 (`LICENSE-DATA.md`, `dcterms:license`) |
| ★★ | Dữ liệu có cấu trúc, máy đọc được | CSV + RDF |
| ★★★ | Định dạng không độc quyền | CSV, Turtle |
| ★★★★ | Dùng URI/RDF để định danh sự vật | HTTP URI cho mọi thực thể, resolve qua static site |
| ★★★★★ | Liên kết sang dữ liệu người khác | 92 `owl:sameAs` sang Wikidata, DBpedia |

**Vì sao dùng static site trên GitHub Pages thay vì server riêng**: miễn phí, không cần
vận hành, URI ổn định, vẫn đáp ứng nguyên tắc 3 (tra URI → HTML cho người + Turtle /
JSON-LD cho máy). Hạn chế: không có content negotiation thật (cùng URL trả HTML; bản
Turtle nằm ở `data.ttl` bên cạnh, được khai báo bằng `<link rel="alternate">`).

### 4.2. RDF, URI, Literal, Turtle

- **RDF** biểu diễn mọi thứ bằng triple *(subject, predicate, object)*; nhiều triple
  tạo thành đồ thị. Lợi thế so với CSV: gộp nhiều nguồn không cần thống nhất schema
  bảng, quan hệ là first-class, có thể link xuyên dataset.
- **Thiết kế URI**: `resource/<loại>/<slug>` – dễ đọc, ổn định, sinh từ ID đã kiểm tra
  (không dùng số thứ tự hay blank node) để URI không đổi khi chạy lại pipeline. ID trận
  gồm ngày + hai đội → duy nhất và tự mô tả.
- **Literal có kiểu** (`xsd:date`, `xsd:nonNegativeInteger`): giúp so sánh/sắp xếp
  đúng trong SPARQL (so ngày, cộng bàn thắng) và SHACL kiểm tra được kiểu.
- **Language tag** `@en`: chuẩn hoá đa ngôn ngữ, SHACL buộc `sh:languageIn ("en")`.
- **Turtle**: cú pháp RDF gọn, dễ đọc, phổ biến; JSON-LD dùng thêm trong HTML cho công
  cụ web.

### 4.3. Ontology: RDFS + OWL 2

File `ontology/football.ttl`, prefix `foot:`.

**Lớp**: `FootballMatch`, `FootballTeam`, `Competition` (con là `League`, `Cup`),
`Season`, `Draw ⊑ FootballMatch`.

**Thuộc tính đối tượng**: `homeTeam`, `awayTeam`, `winner`, `loser` (đều là con của
`participant`), `playedInSeason`, `partOfCompetition`.
**Thuộc tính dữ liệu**: `matchDate`, `roundNumber`, `homeGoals`, `awayGoals`, `tier`,
`stage`, `sourceLine`, `seasonLabel`.

Các cấu trúc ngữ nghĩa đã dùng và ý nghĩa:

| Cấu trúc | Ví dụ | Ý nghĩa / lý do |
| --- | --- | --- |
| `rdfs:subClassOf` tới schema.org | `FootballMatch ⊑ schema:SportsEvent`, `FootballTeam ⊑ schema:SportsTeam`, `Competition ⊑ schema:EventSeries` | **Tái sử dụng từ vựng phổ biến**: công cụ hiểu schema.org sẽ hiểu dữ liệu mà không cần biết `foot:` |
| `rdfs:subPropertyOf` | `homeTeam ⊑ participant ⊑ schema:competitor`; `playedInSeason ⊑ schema:superEvent, dcterms:isPartOf` | Hỏi "đội nào tham gia trận" một lần qua `participant` thay vì UNION 4 thuộc tính |
| `rdfs:domain` / `rdfs:range` | `homeTeam`: FootballMatch → FootballTeam | Suy diễn kiểu (không phải ràng buộc – xem 4.5) |
| `owl:FunctionalProperty` | `homeTeam`, `matchDate`, `homeGoals`… | Mỗi trận chỉ có một giá trị |
| `owl:qualifiedCardinality` | Trận có đúng 1 `homeTeam` FootballTeam, 1 `awayTeam`, 1 `playedInSeason` Season | Mô tả chính xác cấu trúc trận đấu |
| `owl:propertyDisjointWith` | `homeTeam` ⟂ `awayTeam`, `winner` ⟂ `loser` | Một đội không thể vừa là chủ nhà vừa là khách trong cùng trận |
| `owl:disjointWith`, `owl:AllDisjointClasses` | `League` ⟂ `Cup`; Competition, Season, Team, Match đôi một rời nhau | Reasoner phát hiện mâu thuẫn nếu một URI bị gán hai loại |
| `owl:complementOf` + `someValuesFrom` | `Draw` ⊑ ¬(∃winner.⊤) ⊓ ¬(∃loser.⊤) | Trận hòa không có người thắng/thua |
| `owl:propertyChainAxiom` | `partOfCompetition ⊒ playedInSeason ∘ partOfCompetition` | Reasoner suy ra trận thuộc giải nào từ mùa của nó |
| `owl:unionOf` trong domain | domain của `partOfCompetition` = Match ∪ Season | Một thuộc tính dùng cho hai loại |
| Metadata ontology | `owl:versionInfo`, `dcterms:creator`, `dcterms:license` | Ontology cũng là tài nguyên được xuất bản |

**Vì sao không khai báo `partOfCompetition` là Functional?** OWL 2 DL cấm thuộc tính
được định nghĩa bằng property chain (thuộc tính "phức") đồng thời là functional. Nên
ontology giữ property chain, còn ràng buộc "đúng 1 giá trị" đẩy sang SHACL.

**Vì sao vẫn ghi thẳng `partOfCompetition` cho trận dù suy ra được?** Rdflib và Fuseki
mặc định không chạy OWL reasoner. Ghi sẵn giúp SPARQL thường hoạt động; SHACL kiểm tra
giá trị ghi sẵn khớp với giá trị suy ra từ mùa.

**Vì sao các lớp schema.org được khai báo lại là `owl:Class`?** Để ontology hợp lệ OWL 2
DL khi mở bằng Protégé/HermiT (công cụ cần biết term ngoài là class hay property).

**Vì sao thiết kế dựa trên competency questions?** Đây là phương pháp chuẩn khi xây
ontology (ví dụ METHONTOLOGY, NeOn): liệt kê câu hỏi hệ thống phải trả lời
(`docs/competency-questions.md`) → chỉ mô hình hoá những gì cần để trả lời → tránh
ontology phình to với khái niệm không có dữ liệu (cầu thủ, HLV, chuyển nhượng).

### 4.4. Open World Assumption và Unique Name Assumption

- **OWA**: trong OWL, thiếu một triple không có nghĩa là sai, chỉ là *chưa biết*. Ví dụ
  cardinality "đúng 1 homeTeam" không làm reasoner báo lỗi khi trận thiếu homeTeam – nó
  chỉ suy ra rằng *có tồn tại* một đội nhà chưa biết.
- **Không có UNA**: hai URI khác nhau có thể chỉ cùng một thứ. Đó chính là lý do
  `owl:sameAs` có nghĩa, nhưng cũng là lý do functional property không báo lỗi khi có
  hai giá trị – reasoner sẽ suy ra hai giá trị đó là một.

Hệ quả: **OWL không phải công cụ kiểm tra dữ liệu**. Cần SHACL.

### 4.5. SHACL – kiểm tra dữ liệu theo Closed World

SHACL (W3C, 2017) kiểm tra đồ thị dữ liệu với *shapes* theo kiểu closed-world: thiếu là
lỗi, thừa là lỗi. Dự án tách vai trò:

| | OWL ontology | SHACL shapes |
| --- | --- | --- |
| Mục đích | Mô tả nghĩa, cho phép suy diễn | Kiểm tra chất lượng dữ liệu |
| Giả định | Open world | Closed world |
| Thiếu `homeTeam` | Không lỗi | Vi phạm `sh:minCount 1` |
| Hai `homeTeam` | Suy ra hai đội là một | Vi phạm `sh:maxCount 1` |

Lý do dùng **SHACL-SPARQL** cho luật xuyên tài nguyên (ngày trận trong mùa, tỉ số khớp
winner): SHACL Core chỉ so sánh giá trị trên cùng một node; luật cần join nhiều tài
nguyên phải viết bằng SPARQL. Viết ở cấp dataset (`sh:targetNode dataset:premier-league`)
để chạy **một lần** trên cả graph thay vì 3.800 lần, nhanh hơn nhiều.

Lý do validate với `inference="rdfs"` và nạp ontology: để `sh:class foot:FootballTeam`
nhận cả lớp con, đúng như ý nghĩa ontology.

### 4.6. Liên kết 5 sao: `owl:sameAs` và entity resolution

- `owl:sameAs` khẳng định hai URI **là cùng một thực thể**: mọi phát biểu về cái này
  cũng đúng với cái kia. Đây là liên kết mạnh nhất – và nguy hiểm nhất. Link sai sẽ
  "lây" thông tin sai: ví dụ gộp Chester City (giải thể 2010) với Chester FC (lập 2010)
  làm năm thành lập, sân nhà, lịch sử bị trộn.
- Vì thế dự án dùng quy trình **"candidate → evidence → verified"**: gợi ý tự động chỉ
  là ứng viên; link chỉ được xuất bản khi có bằng chứng lưu lại và mọi kiểm tra đều
  qua. Converter từ chối link không có evidence. Đây là lý do chính để **giới hạn phạm
  vi** ở 10 mùa Premier League (35 CLB, xác minh được hết) thay vì cả hệ thống giải.
- **Wikidata** (Q-id ổn định, dữ liệu có cấu trúc, SPARQL endpoint) và **DBpedia** (trung
  tâm của LOD Cloud, trích từ Wikipedia) là hai hub lớn nhất; link sang cả hai tăng khả
  năng khám phá. DBpedia lại có `owl:sameAs` sang Wikidata → dùng làm kiểm tra chéo.
- Vì sao chọn `owl:sameAs` thay vì `skos:exactMatch` / `rdfs:seeAlso`? CLB/mùa/giải ở
  đây đúng là cùng thực thể thế giới thực (không phải khái niệm gần giống), và
  `owl:sameAs` là predicate được công cụ federated query, thang 5 sao và VoID linkset
  công nhận rộng rãi. Điều kiện là phải xác minh kỹ – đã làm.

### 4.7. Metadata dataset: DCAT, VoID, PROV-O, Dublin Core

- **DCAT**: mô tả dataset như một mục trong catalog (title, license, distribution,
  downloadURL, mediaType) → cổng dữ liệu mở (CKAN, data.europa.eu) đọc được.
- **VoID**: mô tả dataset *Linked Data*: `void:uriSpace`, `void:dataDump`,
  `void:vocabulary`, số triple/entity, `void:classPartition` (đếm theo lớp), và
  `void:Linkset` (bao nhiêu link sang Wikidata/DBpedia, dùng predicate nào).
- **PROV-O**: provenance – mỗi trận `prov:wasDerivedFrom` file CSV gốc + `foot:sourceLine`;
  dataset `prov:wasGeneratedBy` một `prov:Activity`. Người dùng truy ngược được từng
  sự kiện về đúng dòng nguồn → dữ liệu kiểm chứng được.
- **Dublin Core Terms**: title, creator, publisher, issued, modified, license, source.

Lý do: dữ liệu 5 sao không chỉ cần link, mà cần **tự mô tả** để người khác tìm được, tin
được, và biết cách dùng (license, nguồn, cách tải).

### 4.8. SPARQL 1.1 và triple store

- Dùng: `SELECT`, basic graph pattern, `OPTIONAL`, `UNION`, `FILTER`, `BIND`, `IF`,
  `COALESCE`, `VALUES` (tham số hoá), `GROUP BY` + `SUM/COUNT/MAX`, subquery, property
  path (`foot:playedInSeason/foot:seasonLabel`, `rdfs:subClassOf*`), `SERVICE`
  (federated).
- **CQ16** dùng property path `a/rdfs:subClassOf*` và `rdfs:subPropertyOf*` để "suy
  diễn tại thời điểm truy vấn" – xem dữ liệu dưới góc nhìn schema.org mà không cần
  reasoner, miễn ontology được nạp cùng dữ liệu.
- **CQ14** (vô địch): tính điểm 3-1-0 và hiệu số bằng SPARQL, gộp thành khoá
  `điểm × 1000 + hiệu số` để lấy MAX (mùa 2011/12 Man City vô địch nhờ hiệu số).
- **Fuseki + TDB2**: triple store chuẩn của Apache Jena, có SPARQL endpoint HTTP theo
  SPARQL 1.1 Protocol và Graph Store Protocol (`/football/data`) dùng để nạp dữ liệu.
- **Vì sao có cả rdflib terminal lẫn Fuseki?** Terminal chạy offline, dùng trong test/CI
  không cần Docker; Fuseki là endpoint thật theo đề bài. Test khẳng định hai bên trả
  kết quả như nhau.

### 4.9. Tổng hợp các quyết định thiết kế

| Quyết định | Lý do |
| --- | --- |
| 10 mùa Premier League, bỏ hạng dưới + cúp | Đủ lớn (3.800 trận) mà vẫn xác minh 100% định danh; tránh lỗi phoenix club |
| Bảng alias duyệt tay, gặp tên lạ thì dừng | Định danh CLB là nền móng của URI và `owl:sameAs`; đoán sai là sai lan truyền |
| Kiểm tra double round-robin | Phát hiện dữ liệu thiếu/trùng/lệch ngay từ đầu |
| URI tất định, output byte-for-byte | Tái lập được, CI kiểm tra được, URI không bao giờ đổi |
| Tái dùng schema.org, DCAT, VoID, PROV, DC | Interoperability – không phát minh lại từ vựng có sẵn |
| OWL cho nghĩa, SHACL cho kiểm tra | OWA của OWL không phát hiện dữ liệu thiếu |
| Không lưu số liệu tổng hợp | Tránh dữ liệu dư thừa lệch nhau; SPARQL tính lại luôn đúng |
| Pipeline offline, evidence lưu sẵn | CI không phụ thuộc Wikidata/DBpedia đang sống hay chết |

---

## 5. Câu hỏi – trả lời

### Về Git và cách ghép nhánh

**Q1. Main được tạo từ 3 nhánh bằng `git merge` phải không?**
Không. Main là lịch sử thẳng của `dqdat-dev`, rồi hai commit `f9c4b40` (ý tưởng từ
hung) và `c51b8af` (từ hung + phong) chép và viết lại code vào khung của dqdat-dev. Vì
vậy commit của hung và phong không xuất hiện trong `git log main`.

**Q2. Mỗi nhánh đóng góp phần nào chính?**
dqdat-dev: hạ tầng xuất bản (URI, static site, DCAT/VoID/PROV, SHACL, Docker Fuseki,
CI). phongph5: phạm vi 10 mùa, manifest, bảng alias, provenance theo dòng, evidence cho
link, test bảng xếp hạng. hung: tiên đề OWL nâng cao, VoID class partition, truy vấn
federated.

**Q3. Vì sao phần hạng dưới và FA Cup của nhánh hung bị bỏ?**
Vì phoenix club bị gộp nhầm định danh và link sai Wikidata. `owl:sameAs` sai làm hỏng dữ
liệu của cả hai phía, nên nhóm chọn bỏ đến khi bảng alias có thời hạn hiệu lực cho tên CLB.

### Về Linked Data / RDF

**Q4. Dataset đạt sao thứ 4 nhờ đâu?**
Mọi thực thể có HTTP URI trong namespace của nhóm, và URI đó resolve được: GitHub Pages
trả trang HTML có triple, JSON-LD nhúng và `data.ttl`.

**Q5. Sao thứ 5 nhờ đâu? Có bao nhiêu link?**
46 thực thể (1 giải, 10 mùa, 35 CLB), mỗi thực thể 1 link Wikidata + 1 link DBpedia =
92 `owl:sameAs`, mô tả bằng 2 `void:Linkset`.

**Q6. Vì sao không link từng trận đấu?**
Wikidata/DBpedia gần như không có item cho từng trận Premier League thường; link chỉ có
nghĩa khi bên kia có thực thể tương ứng.

**Q7. Vì sao ID trận là `ngày-đội nhà-đội khách`?**
Duy nhất trong một giải vòng tròn (hai đội không gặp nhau hai lần cùng ngày cùng sân),
ổn định khi chạy lại, và người đọc URI hiểu ngay.

**Q8. Blank node có được dùng không? Vì sao?**
Không dùng cho thực thể chính, vì blank node không có định danh toàn cục, không link từ
bên ngoài được và đổi nhãn giữa các lần sinh. Chỉ xuất hiện trong ontology (restriction,
danh sách).

**Q9. Khác nhau giữa `rdfs:label` và `schema:name` trong dự án?**
CLB, mùa, giải dùng `schema:name` (tên thật của thực thể, theo schema.org); trận dùng
`rdfs:label` làm nhãn hiển thị sinh ra ("Man United 2–1 Leicester").

### Về ontology

**Q10. Vì sao `FootballMatch` là lớp con của `schema:SportsEvent`?**
Để tái dùng từ vựng phổ biến: công cụ hiểu schema.org (search engine, tool khác) tự coi
trận đấu là sự kiện thể thao. CQ16 chứng minh điều đó bằng `rdfs:subClassOf*`.

**Q11. Property chain trong ontology làm gì?**
`playedInSeason ∘ partOfCompetition → partOfCompetition`: trận thuộc mùa, mùa thuộc giải
⇒ trận thuộc giải. Reasoner OWL 2 suy ra được.

**Q12. Vì sao `partOfCompetition` không phải FunctionalProperty?**
OWL 2 DL không cho phép thuộc tính có property chain đồng thời là functional (vi phạm
điều kiện "simple property"), nên tính duy nhất được kiểm tra bằng SHACL.

**Q13. `Draw` được định nghĩa thế nào?**
`Draw ⊑ FootballMatch ⊓ ¬∃winner.⊤ ⊓ ¬∃loser.⊤`. Converter gán `rdf:type foot:Draw` khi
tỉ số bằng nhau; SHACL kiểm tra hai chiều: hòa ⇔ có kiểu Draw, và Draw không có winner/loser.

**Q14. `owl:propertyDisjointWith` giữa `homeTeam` và `awayTeam` nghĩa là gì?**
Không có cặp (trận, đội) nào vừa là `homeTeam` vừa là `awayTeam`. Nếu dữ liệu vi phạm,
reasoner báo ontology không nhất quán. SHACL dùng `sh:disjoint` để bắt lỗi tương tự.

**Q15. Competency question là gì và dùng để làm gì?**
Là các câu hỏi ontology phải trả lời được. Chúng xác định phạm vi ontology và là tiêu chí
nghiệm thu: mỗi CQ có một file `.rq` và test.

### Về SHACL và chất lượng dữ liệu

**Q16. Đã có OWL rồi, sao còn cần SHACL?**
OWL theo open world và không có unique name assumption: thiếu giá trị không bị coi là
lỗi, hai giá trị cho functional property thì bị suy ra là cùng một thứ. SHACL kiểm tra
theo closed world nên phát hiện được dữ liệu thiếu, thừa, sai kiểu.

**Q17. SHACL Core và SHACL-SPARQL khác nhau thế nào, dự án dùng ở đâu?**
Core khai báo ràng buộc trên một node (count, datatype, pattern, class). SHACL-SPARQL viết
truy vấn tuỳ ý, dùng cho luật cần join nhiều tài nguyên: ngày trận nằm trong mùa, tỉ số
khớp winner/loser, không lặp fixture, trận và mùa cùng file nguồn.

**Q18. Vì sao các luật SPARQL được đặt trên một target node duy nhất?**
Để mỗi luật chạy một lần trên toàn graph và trả về node vi phạm qua `sh:value`, thay vì
chạy một truy vấn cho mỗi trận trong 3.800 trận.

**Q19. Những lỗi nào bị chặn trước khi tới RDF?**
Ngày sai thứ trong tuần, tỉ số sai định dạng, tên CLB lạ, đội gặp chính mình, trùng trận,
mùa không đủ 380 trận / 20 đội / 38 vòng × 10 trận, mỗi đội không đủ 19 trận nhà + 19 trận
khách. Mỗi lỗi báo kèm file và số dòng.

### Về liên kết và xác minh

**Q20. Làm sao biết `owl:sameAs` sang Wikidata là đúng?**
`collect_link_evidence.py` kiểm tra: loại P31 đúng, môn P641 là bóng đá, mùa thuộc
Premier League (P3450 = Q9448), tiêu đề Wikipedia trùng tên tài nguyên DBpedia, và
DBpedia `owl:sameAs` ngược về đúng Q-id. Evidence (kèm revision Wikidata) được lưu; chỉ
khi mọi check pass mới được `--promote` thành `verified`.

**Q21. Ví dụ thực tế cho thấy các check này cần thiết?**
Tìm "2018–19 Premier League" trên Wikidata ra cả mùa giải Premier League của Bosnia và
Herzegovina; "2020–21 Premier League" ra cả một trang định hướng. Chelsea có P31 là "men's
association football team" chứ không phải "club", nên nhóm phải chấp nhận cả hai lớp.

**Q22. Nếu Wikidata sập thì pipeline có chạy không?**
Có. Converter chỉ đọc evidence đã lưu, nên `make pipeline` chạy offline. Chỉ bước thu thập
evidence và truy vấn federated mới cần mạng.

**Q23. Vì sao chọn Wikidata và DBpedia?**
Đây là hai hub lớn nhất của LOD Cloud, có URI ổn định và SPARQL endpoint công khai; DBpedia
link sẵn sang Wikidata nên dùng để kiểm tra chéo.

### Về SPARQL và endpoint

**Q24. Truy vấn federated hoạt động thế nào?**
Phần ngoài lấy CLB mùa 2018/19 và `owl:sameAs` Wikidata của chúng từ dữ liệu local; khối
`SERVICE <https://query.wikidata.org/sparql>` gửi các Q-id đó sang Wikidata để lấy sân nhà
(P115) và năm thành lập (P571). Đây là minh chứng giá trị thực tế của sao thứ 5.

**Q25. Vì sao truy vấn federated không chạy trên Fuseki?**
Wikidata trả HTTP 403 cho user-agent Java mặc định mà Jena gửi. Truy vấn này chạy bằng
`run_sparql.py` (rdflib). Fuseki vẫn bật `arq:httpServiceAllowed` cho các endpoint khác.

**Q26. Bảng xếp hạng có lưu trong RDF không?**
Không. Bảng xếp hạng (CQ11), vô địch (CQ14), thống kê mùa (CQ13) đều tính bằng SPARQL từ
tỉ số. Lưu sẵn sẽ tạo dữ liệu dư thừa có thể lệch nhau. Test so sánh kết quả SPARQL với
bảng tính trực tiếp từ CSV gốc cho cả 10 mùa.

**Q27. CQ16 "suy diễn" mà không cần reasoner bằng cách nào?**
Dùng property path `?x a/rdfs:subClassOf* schema:SportsEvent` và
`?p rdfs:subPropertyOf* foot:participant` khi ontology được nạp cùng dữ liệu. Đây là
suy diễn RDFS thực hiện lúc truy vấn (query rewriting thủ công).

**Q28. Vì sao vừa có rdflib vừa có Fuseki?**
rdflib chạy offline trong test/CI, không cần Docker; Fuseki là SPARQL endpoint HTTP chuẩn
theo đề bài. Cả hai nạp dữ liệu + ontology nên trả cùng kết quả.

### Về metadata và tái lập

**Q29. DCAT và VoID khác nhau thế nào?**
DCAT mô tả dataset trong catalog dữ liệu (license, distribution, download URL, media
type). VoID chuyên cho Linked Data: URI space, data dump, vocabulary dùng, số triple,
class partition, linkset sang dataset khác.

**Q30. Provenance được ghi ở mức nào?**
Mức từng trận: `prov:wasDerivedFrom` trỏ tới URL file CSV gốc trên GitHub và
`foot:sourceLine` là số dòng. Mùa cũng có `prov:wasDerivedFrom`; dataset có
`prov:wasGeneratedBy` một `prov:Activity`. SHACL kiểm tra trận và mùa cùng file nguồn.

**Q31. "Tái lập byte-for-byte" nghĩa là gì và vì sao quan trọng?**
Chạy lại pipeline từ CSV gốc phải ra đúng các file đã commit (CI chạy `git diff
--exit-code`). Điều đó chứng minh dữ liệu xuất bản thật sự được sinh từ nguồn đã khai báo,
không bị sửa tay, và URI không thay đổi giữa các lần chạy.

**Q32. Muốn thêm mùa 2021/22 thì làm gì?**
Thêm dòng vào `config/seasons.csv` → chạy `clean_data.py`, thêm tên CLB lạ vào bảng alias →
thêm mùa và CLB mới vào `entity-links.csv` dạng `candidate` → chạy
`collect_link_evidence.py --promote` → `make pipeline` và cập nhật số kỳ vọng trong test.

**Q33. Hạn chế hiện tại của dự án?**
Không có cầu thủ, HLV, sân vận động (sân lấy qua federated query); không có content
negotiation thật trên GitHub Pages; chưa hỗ trợ hạng dưới và cúp vì vấn đề định danh
phoenix club; truy vấn federated phụ thuộc Wikidata trực tuyến.
