# Premier League Linked Data — phongph5

Bài tập Semantic Web, đề tài **Build a Linked Open Data (LOD) application**.
Nhánh `phongph5` xử lý **10 mùa Premier League 2011/12–2020/21**: **3.800 trận,
35 CLB, 1 giải đấu**, với terminal SPARQL và Apache Jena Fuseki.

Đây là phiên bản chạy local. RDF sử dụng URI HTTP và liên kết Wikidata/DBpedia
theo yêu cầu 4★/5★ của đề. Namespace `example.org` chỉ minh họa, chưa xuất bản;
không khẳng định đã công bố dataset Open Data 5★ trên Web.
Không bao gồm slide, báo cáo, video, website riêng hoặc hosting.

## Đối chiếu với đề bài

| Yêu cầu | Sản phẩm | Kiểm tra |
| --- | --- | --- |
| 1. Define an ontology | `ontology/football.ttl`: Competition, Season, Team, Match | Đọc Turtle hoặc mở bằng Protégé |
| 2. Collect relevant data | 10 CSV gốc, manifest và bảng tên CLB | `src/clean_data.py` |
| 3. Transform into 4★ standard | URI HTTP, RDF/Turtle, literal có kiểu, metadata và nguồn | `src/convert_to_rdf.py`, `src/validate_rdf.py` |
| 4. Establish links to other datasets | 72 `owl:sameAs` tới Wikidata/DBpedia | `data/links/`, query 10 |
| 5. SPARQL endpoint/terminal | 10 truy vấn, terminal và Fuseki | `src/query.py`, http://localhost:3035/ |

SHACL và tests kiểm chứng các sản phẩm trên, không thay thế ontology hoặc liên kết ngoài.

## Chạy nhanh trên Windows / PowerShell

Chạy tại thư mục gốc repo trên nhánh `phongph5`. Đã kiểm tra với **Python 3.13.5**.
Không cần activate venv hoặc đổi ExecutionPolicy hệ thống:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/pipeline.py
```

Pipeline: CSV → chuẩn hóa → RDF + liên kết → SHACL → tests, bao gồm đủ 10 câu hỏi
và phép tính độc lập từ CSV gốc. Sau khi cài dependencies, pipeline chạy offline.
Bất kỳ lỗi nào cũng trả mã thoát khác 0.

```powershell
# Chạy từng bước khi cần tìm lỗi
.\.venv\Scripts\python.exe src/clean_data.py
.\.venv\Scripts\python.exe src/convert_to_rdf.py
.\.venv\Scripts\python.exe src/validate_rdf.py
.\.venv\Scripts\python.exe -m unittest discover -s src -p 'test_*.py' -v

# Truy vấn local; mặc định 2018-19, Arsenal và Tottenham
.\.venv\Scripts\python.exe src/query.py --all
.\.venv\Scripts\python.exe src/query.py queries/03-standings.rq --season 2020-21
.\.venv\Scripts\python.exe src/query.py queries/06-head-to-head.rq --team liverpool --opponent manchester-city
```

Tham số đội là `team_id` trong `config/team-aliases.csv`, không phải tên hiển thị.
Tham số mùa chỉ nhận 10 mùa trong manifest. CLI hỗ trợ file SELECT/ASK.

## Fuseki và giao diện web

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup-tools.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/fuseki.ps1 start
.\.venv\Scripts\python.exe src/load_fuseki.py
```

Script tải **Azul Zulu Java 21.0.12.1** và **Fuseki 6.2.0**, kiểm tra SHA256/SHA512,
giải nén trong `tools/` được Git bỏ qua. Java hệ thống giữ nguyên. Jena 6 cần Java 21
trở lên; Java 8 không đủ. [Yêu cầu của Apache](https://jena.apache.org/download/).

- Web: **http://localhost:3035/** → chọn dataset **phongph5** → Query.
- SPARQL: `http://localhost:3035/phongph5/sparql`.
- Graph Store: `http://localhost:3035/phongph5/data`.
- Chỉ lắng nghe localhost. TDB2 nằm ở `.runtime/tdb2`, riêng với dataset của nhóm.

File query có token `{{season}}`, `{{team}}`, `{{opponent}}`. Trước khi dán vào Fuseki,
xuất SPARQL đã gắn tham số bằng `--render`:

```powershell
.\.venv\Scripts\python.exe src/query.py queries/03-standings.rq --season 2018-19 --render
# Có thể thêm | Set-Clipboard để sao chép câu truy vấn.

# Truy vấn từ terminal qua Fuseki
.\.venv\Scripts\python.exe src/query.py queries/03-standings.rq --endpoint

# So cả 10 câu hỏi giữa RDFLib và Fuseki
.\.venv\Scripts\python.exe src/query.py --all --compare

powershell -NoProfile -ExecutionPolicy Bypass -File scripts/fuseki.ps1 status
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/fuseki.ps1 stop
```

Nạp lại dùng HTTP PUT thay thế default graph **của dataset phongph5**, không cộng dồn.
SHACL được kiểm tra trước khi nạp. Dừng server giữ nguyên dữ liệu TDB2.
Script không tự dừng ứng dụng khác nếu cổng 3035 bị chiếm. Log nằm trong
`.runtime/fuseki.stdout.log` và `.runtime/fuseki.stderr.log`.

## Mô hình và luồng dữ liệu

```text
10 CSV gốc → 4 bảng chuẩn hóa → RDF + owl:sameAs → SHACL → terminal / Fuseki

Match ──inSeason──→ Season ──seasonOf──→ Competition
  ├──homeTeam──→ Team ──owl:sameAs──→ Wikidata / DBpedia
  ├──awayTeam──→ Team
  ├──winner/loser──→ Team (chỉ khi tỷ số hai đội khác nhau)
  └──matchDate, roundNumber, homeGoals, awayGoals, sourceFile, sourceLine
```

`Team` kế thừa `schema:SportsTeam`; `Match`/`Season` kế thừa `schema:SportsEvent`;
`Competition` là chuỗi sự kiện `schema:EventSeries`. Ngày dùng `xsd:date`, vòng dùng
`xsd:positiveInteger`, bàn dùng `xsd:nonNegativeInteger`. OWL/RDFS mô tả ý nghĩa,
SHACL kiểm tra dữ liệu cụ thể. Bảng xếp hạng được tính bằng SPARQL, không lưu sẵn.

Ví dụ phần đường dẫn URI sau `<base_uri>resource/`:

```text
team/manchester-united
season/premier-league-2018-19
match/premier-league-2018-19-r01-manchester-united-leicester-city
```

Namespace cấu hình tại `config/project.json`. Đổi `base_uri` rồi chạy lại pipeline
và nạp Fuseki: ontology, shapes và query được thay namespace đồng bộ lúc đọc.
Ontology nguồn giữ namespace mẫu, bản render nằm tại `data/rdf/ontology.ttl`.

## Dữ liệu và quy tắc làm sạch

- Nguồn: [footballcsv/england](https://github.com/footballcsv/england), bản mirror
  CSV của OpenFootball, giấy phép [CC0](england_csv/LICENSE.md).
- `config/seasons.csv` liệt kê đúng 10 file `eng.1.csv`; không tự quét giải khác.
- Bảng alias ánh xạ 54 tên nguồn thành 35 CLB. `Wolves` và `Wolverhampton Wanderers FC`
  dùng chung ID. Tên lạ gây lỗi để kiểm tra, không đoán danh tính chỉ bằng slug.
- Mỗi mùa phải có 380 trận, 20 đội, 38 vòng, 10 trận/vòng; mỗi đội 38 trận,
  mỗi cặp đội có đủ hai lượt sân nhà/sân khách. Không âm thầm bỏ dòng lỗi.
- Mỗi trận giữ file nguồn và số dòng từ 2. Dữ liệu gốc không bị sửa.
- Ngày mùa là ngày trận sớm nhất/muộn nhất, không mặc định kết thúc trong tháng 5:
  mùa 2019/20 kéo dài. Chú thích hoãn trận `(P)` được chấp nhận.
- Không mở rộng sang cầu thủ, sân vận động, dữ liệu trực tiếp hoặc giải cúp.

Cleaner giữ tùy chọn `--input` để thử một mùa với `--output-dir` riêng.
Pipeline chính luôn dùng manifest 10 mùa. Không ghi đè `data/processed/` bằng chế độ
một mùa nếu định chạy bộ kiểm thử 10 mùa.

## Liên kết ngoài và bằng chứng

`data/links/entity-links.csv` có 35 CLB và 1 giải, mỗi thực thể có Wikidata và DBpedia:
tổng **72 triple**. Không bắt buộc liên kết từng trận/mùa.

Mapping `origin/hung` là ứng viên. Ngày **2026-10-03**, Codex đối chiếu tên, mô tả
địa điểm/loại thực thể, trang Wikipedia tiếng Anh, lớp SoccerClub/SoccerLeague và
liên kết DBpedia tới đúng Wikidata ID. Đây là đối chiếu do trợ lý thực hiện, không
phải xác nhận rằng thành viên nhóm đã kiểm tra thủ công. Bằng chứng rút gọn, URL
và revision Wikidata lưu trong `data/links/evidence/`.

Thu thập bằng chứng online, không tự nâng trạng thái mapping:

```powershell
.\.venv\Scripts\python.exe src/collect_link_evidence.py --only arsenal
```

Sau khi xem bằng chứng, cập nhật `status`, `verified_on`, `evidence` trong mapping.
Converter từ chối mapping thiếu/trùng/chưa xác minh hoặc sai bằng chứng. Pipeline
thường ngày chỉ đọc bằng chứng đã lưu, không phụ thuộc API ngoài.

## 10 câu hỏi SPARQL

| # | File trong `queries/` | Câu hỏi | Phạm vi |
| --- | --- | --- | --- |
| 1 | `01-teams.rq` | Những đội nào tham dự? | Một mùa |
| 2 | `02-team-matches.rq` | Lịch sử trận và vai trò sân nhà/khách của một đội? | Một mùa |
| 3 | `03-standings.rq` | Bảng xếp hạng theo điểm, hiệu số, bàn thắng? | Một mùa |
| 4 | `04-highest-scoring.rq` | Trận nhiều bàn nhất, bao gồm đồng hạng? | Một mùa |
| 5 | `05-draws.rq` | Những trận nào hòa? | Một mùa |
| 6 | `06-head-to-head.rq` | Đối đầu của hai CLB? | Cả 10 mùa |
| 7 | `07-home-away-goals.rq` | Bàn sân nhà/sân khách của từng đội? | Một mùa |
| 8 | `08-season-statistics.rq` | Số trận, tổng bàn, trung bình bàn/trận? | Theo từng mùa |
| 9 | `09-season-participation.rq` | Mỗi đội tham dự bao nhiêu mùa? | Cả 10 mùa |
| 10 | `10-external-links.rq` | CLB liên kết với URI ngoài nào? | Tất cả CLB |

Thắng 3 điểm, hòa 1 điểm, thua 0 điểm. Query 3 sắp theo điểm, hiệu số, bàn thắng;
tên đội chỉ để ổn định thứ tự nếu cả ba bằng nhau. Không mô phỏng phạt điểm hoặc
quy tắc ngoài dữ liệu nguồn.

## Kiểm thử và học hỏi giữa các nhánh

Tests kiểm tra số lượng, ID, lịch hai lượt, lỗi dữ liệu, tái lập RDF, mapping và
các mẫu SHACL sai: hai đội giống nhau/không tồn tại, bàn âm/sai kiểu, người thắng
sai/thiếu, trận hòa vẫn có người thắng, ngày/vòng không hợp lệ.

Bảng xếp hạng **cả 10 mùa**, tổng bàn và thống kê được so với phép tính Python độc lập
trên CSV gốc. Fixture mùa 2018/19: Manchester City 98 điểm, Liverpool 97 điểm.
`--compare` so RDFLib/Fuseki không phụ thuộc thứ tự hàng; AVG so đến 10 chữ số thập phân.

RDF xuất N-Triples đã sắp xếp, là tập con hợp lệ của Turtle, giúp diff ổn định.
Graph nghiệp vụ không có blank node. Báo cáo SHACL không dùng để so byte vì công cụ
có thể sinh ID blank node khác nhau.

Kiểm chứng trên máy Windows ngày 2026-10-03:

- 16 tests thành công; toàn bộ dữ liệu đạt SHACL.
- 47.723 triple dữ liệu + 72 liên kết + 114 triple ontology = 47.909 triple trong Fuseki.
- Cả 10 truy vấn cho kết quả tương đương giữa RDFLib/Fuseki; bảng xếp hạng được
  đối chiếu thêm cho từng mùa trong cả 10 mùa.
- Nạp hai lần vẫn giữ 47.909 triple; dừng/khởi động lại giữ nguyên dữ liệu.
- Giao diện Fuseki trả HTTP 200; lỗi query và endpoint chưa chạy trả mã thoát 1.

Nhánh bắt đầu từ `main` tại `f67dc63`, không merge nguyên nhánh của thành viên khác:

- Kế thừa parser ngày/tỷ số, dataclass và xuất CSV của `main`.
- Tham khảo `origin/hung`: nhiều mùa, tên đội, ứng viên liên kết, Fuseki.
- Tham khảo `origin/dqdat-dev`: kiểm định, mapping có bằng chứng, kiểm thử.
- Điểm riêng: 10 mùa Premier League, manifest cố định, bảng alias, nguồn từng dòng,
  tính đối chiếu CSV và endpoint riêng.

So cùng mùa `2018-19` giữa các nhánh; so dữ liệu và kết quả truy vấn thay vì chỉ số
triple vì ontology/metadata khác nhau.

```text
config/          namespace, manifest, bảng alias
england_csv/     dữ liệu gốc và giấy phép
data/processed/  bốn bảng chuẩn hóa
data/links/      mapping và bằng chứng
data/rdf/        ontology render, dữ liệu, liên kết, báo cáo SHACL
ontology/        ontology nguồn
shapes/          ràng buộc SHACL
queries/         mười câu hỏi
src/             pipeline, CLI, kiểm định, nạp Fuseki, tests
scripts/         thiết lập/chạy/dừng Java + Fuseki
tools/           binary tải về, không commit
.runtime/        log, PID và dữ liệu server, không commit
```
