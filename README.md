# English Football Linked Data

Bộ dữ liệu 5★ Linked Open Data về bóng đá Anh 1992–2021 (Premier League, 3 hạng
Football League, National League, FA Cup), xây dựng từ
[OpenFootball `england_csv`](https://github.com/footballcsv/england) (public domain).

| Bước | Kết quả | File |
|---|---|---|
| 1. Ontology | OWL 2: `Competition/League/Cup`, `Season`, `Team`, `Match/Draw`, liên kết với schema.org | [ontology/football.ttl](ontology/football.ttl) |
| 2. Thu thập + làm sạch | 97 file CSV → 45.849 trận, 153 đội, 97 mùa, 9 giải | [src/clean_data.py](src/clean_data.py) → `data/processed/` |
| 3. 4★ (RDF) | ~447k triple, URI cho mọi thực thể | [src/to_rdf.py](src/to_rdf.py) → `data/rdf/football.ttl` |
| 4. 5★ (liên kết) | `owl:sameAs` tới Wikidata + DBpedia cho đội và giải | [src/link_wikidata.py](src/link_wikidata.py) → `data/links/` → `data/rdf/links.ttl` |
| 5. Truy vấn | Fuseki SPARQL endpoint + CLI | [fuseki/config.ttl](fuseki/config.ttl), [src/query.py](src/query.py), [queries/](queries/) |

## Chạy từ đầu

```bash
pip install -r requirements.txt

python src/clean_data.py        # england_csv/ -> data/processed/*.csv
python src/link_wikidata.py     # -> data/links/team_links.csv (chạy lại được, giữ kết quả cũ)
python src/to_rdf.py            # -> data/rdf/football.ttl + links.ttl  (~1 phút)

python -m unittest discover -s src -p "test_*.py"
```

`data/links/competition_links.csv` được tra tay. `team_links.csv` sinh tự động
bằng Wikidata Action API (chỉ nhận item có `P31` là câu lạc bộ bóng đá); sửa tay
dòng sai/thiếu rồi chạy lại `to_rdf.py`.

## SPARQL endpoint (Apache Jena Fuseki 6, cần Java 17+)

Tải [apache-jena-fuseki-6.2.0.zip](https://dlcdn.apache.org/jena/binaries/), giải nén vào `tools/`, rồi từ thư mục gốc:

```bash
java -jar tools/apache-jena-fuseki-6.2.0/fuseki-server.jar --config fuseki/config.ttl
```

- Giao diện web: http://localhost:3030 (dataset `football`)
- Endpoint: `http://localhost:3030/football/sparql`

## Truy vấn từ terminal

```bash
python src/query.py queries/01_standings.rq
python src/query.py "SELECT ?t WHERE { ?t a <http://example.org/football/ontology#Team> } LIMIT 5"
python src/query.py queries/01_standings.rq --local   # không cần Fuseki (rdflib, chậm hơn)
```

| Query | Nội dung |
|---|---|
| 01_standings | Bảng xếp hạng Premier League 2018/19 tính từ kết quả trận |
| 02_head_to_head | Đối đầu Arsenal – Tottenham mọi giải |
| 03_biggest_wins | 10 trận thắng cách biệt nhất |
| 04_all_tiers | CLB từng đá ở cả 4 hạng |
| 05_home_advantage | Tỉ lệ thắng sân nhà theo mùa |
| 06_ontology_reasoning | Dùng `rdfs:subClassOf*` để thấy dữ liệu dưới góc nhìn schema.org |
| 07_links | Các liên kết `owl:sameAs` (5★) |
| 08_federated_wikidata | Truy vấn liên hợp sang Wikidata lấy sân vận động, năm thành lập |
| 09_fa_cup_finals | Chung kết FA Cup |

## Mô hình dữ liệu

```
fb:Match --fb:homeTeam/awayTeam/winner/loser--> fb:Team --owl:sameAs--> wd:Q…, dbr:…
   |  fb:homeGoals, fb:awayGoals, fb:matchDate, fb:matchday | fb:stage
   +--fb:inSeason--> fb:Season --fb:seasonOf--> fb:League | fb:Cup --owl:sameAs--> wd:Q…
                       fb:seasonLabel, startDate, endDate       fb:tier, schema:location wd:Q21
```

URI: `http://example.org/football/resource/{team|competition|season|match}/<id>`.

## Ghi chú dữ liệu

- Bỏ 2.061 trận không có tỉ số (mùa 2019-20 bị dừng vì COVID; dữ liệu 2020-21 hạng dưới chưa đủ).
- Hạng 2–4 đổi tên từ 2004-05 (First Division → Championship, …) nên là các `fb:League` khác nhau, cùng `fb:tier`.
- Tên đội được chuẩn hoá (`Manchester Utd` → `Manchester United FC`); `Wimbledon FC` và `AFC Wimbledon` là 2 CLB riêng.
- Nguồn có lỗi đã biết: Bury v Brentford 2000-01 xuất hiện 2 lần trên sân Bury; Championship 2015-16 thiếu 2 trận. `clean_data.py` in cảnh báo.
