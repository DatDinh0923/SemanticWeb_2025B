# Giải thích dự án "Bóng đá Anh thành Dữ liệu Liên kết"

> Tài liệu này giải thích **toàn bộ** dự án bằng lời thật dễ hiểu – như kể cho một bạn học lớp 5.
> Mỗi phần đều chỉ ra **dòng code** đang làm việc đó, để bạn mở file ra xem tận mắt.

---

## Mục lục

0. [Câu chuyện tổng quát](#0-câu-chuyện-tổng-quát)
1. [Kiến thức nền: Web ngữ nghĩa là gì?](#1-kiến-thức-nền-web-ngữ-nghĩa-là-gì)
2. [Bước 1 – Ontology: cuốn "từ điển luật chơi"](#2-bước-1--ontology-cuốn-từ-điển-luật-chơi)
3. [Bước 2 – Thu thập và làm sạch dữ liệu](#3-bước-2--thu-thập-và-làm-sạch-dữ-liệu)
4. [Bước 3 – Biến bảng thành RDF (4 sao)](#4-bước-3--biến-bảng-thành-rdf-4-sao)
5. [Bước 4 – Nối sang Wikidata, DBpedia (5 sao)](#5-bước-4--nối-sang-wikidata-dbpedia-5-sao)
6. [Kiểm tra chất lượng bằng SHACL](#6-kiểm-tra-chất-lượng-bằng-shacl)
7. [Tấm "thẻ giới thiệu" VoID/DCAT](#7-tấm-thẻ-giới-thiệu-voiddcat)
8. [Bước 5 – Hỏi đáp bằng SPARQL](#8-bước-5--hỏi-đáp-bằng-sparql)
9. [Các bài kiểm thử (test)](#9-các-bài-kiểm-thử-test)
10. [Cách chạy toàn bộ](#10-cách-chạy-toàn-bộ)
11. [Từ điển nhỏ](#11-từ-điển-nhỏ)

---

## 0. Câu chuyện tổng quát

Hãy tưởng tượng bạn có **một thùng giấy** chứa hàng trăm tờ ghi kết quả bóng đá Anh từ năm 1992 đến 2021.
Mỗi tờ viết kiểu: *"Ngày 10/8/2018, Manchester United thắng Leicester City 2–1"*.

Con người đọc thì hiểu, nhưng **máy tính thì không** – với máy, đó chỉ là một chuỗi chữ.
Máy không biết "Manchester United" là một đội bóng, không biết "2–1" nghĩa là ai thắng.

Dự án này làm 5 việc (đúng 5 yêu cầu của đề bài):

| Bước | Ví von cho dễ hiểu | Làm gì thật sự | File chính |
|---|---|---|---|
| 1 | Viết **cuốn luật chơi** | Định nghĩa ontology: có những "loại" nào (Đội, Trận, Mùa…) và chúng liên quan ra sao | [ontology/football.ttl](../ontology/football.ttl) |
| 2 | **Dọn dẹp thùng giấy** | Đọc 97 file CSV, sửa tên đội viết lung tung, bỏ trận chưa đá | [src/clean_data.py](../src/clean_data.py) |
| 3 | Dán **thẻ căn cước** cho mọi thứ | Mỗi đội, mỗi trận có một địa chỉ web riêng (URI) và viết thành câu RDF | [src/to_rdf.py](../src/to_rdf.py) |
| 4 | **Bắt tay** với bạn bè | Nói cho máy biết "đội Arsenal của mình = Arsenal bên Wikidata" | [src/link_wikidata.py](../src/link_wikidata.py) |
| 5 | Mở **quầy hỏi đáp** | Chạy máy chủ SPARQL để ai cũng hỏi được | [fuseki/config.ttl](../fuseki/config.ttl), [src/query.py](../src/query.py) |

Thêm hai việc phụ để dữ liệu "xịn" hơn:
- **Cô giáo chấm bài** (SHACL) – kiểm tra dữ liệu không có lỗi: [shapes/football-shapes.ttl](../shapes/football-shapes.ttl)
- **Thẻ giới thiệu** (VoID) – mô tả bộ dữ liệu có gì: `data/rdf/void.ttl`

Dòng chảy (pipeline) đi như sau:

```
england_csv/ (97 file CSV gốc)
   │  clean_data.py          ← dọn dẹp
   ▼
data/processed/*.csv  (4 bảng sạch: trận, đội, mùa, giải)
   │  link_wikidata.py       ← đi hỏi Wikidata
   ▼
data/links/*.csv      (bảng "đội của mình = đội bên Wikidata")
   │  to_rdf.py              ← viết thành câu RDF
   ▼
data/rdf/football.ttl + links.ttl + void.ttl
   │  validate.py            ← chấm bài
   │  Fuseki                 ← mở quầy hỏi đáp
   ▼
python src/query.py queries/01_standings.rq   ← đặt câu hỏi
```

---

## 1. Kiến thức nền: Web ngữ nghĩa là gì?

### 1.1. Web bình thường vs Web ngữ nghĩa

- **Web bình thường** giống một thư viện toàn sách viết cho **người** đọc. Máy tính chỉ thấy chữ, không hiểu nghĩa.
- **Web ngữ nghĩa** (Semantic Web) là viết thêm một phiên bản cho **máy** đọc – mỗi thông tin được viết thành câu ngắn, rõ ràng, có "nghĩa" mà máy hiểu được.

### 1.2. RDF – viết mọi thứ thành câu 3 từ

RDF là cách viết thông tin thành **câu ba phần** (gọi là *triple*):

```
  CHỦ NGỮ        VỊ NGỮ          TÂN NGỮ
  Trận đấu X     có đội nhà là   Manchester United
  Trận đấu X     có số bàn nhà   2
  Manchester U.  có tên là       "Manchester United FC"
```

Giống như chơi trò ghép câu: *Ai – làm gì / có gì – cái gì*.
Cả dự án này có khoảng **447.000 câu** như vậy.

Đây là một trận thật trong file [data/rdf/football.ttl](../data/rdf/football.ttl) (định dạng Turtle – một cách viết RDF gọn gàng):

```turtle
<.../match/2018-08-10-manchester-united-leicester-city> a fb:Match ;
    fb:homeTeam  <.../team/manchester-united> ;
    fb:awayTeam  <.../team/leicester-city> ;
    fb:homeGoals 2 ;
    fb:awayGoals 1 ;
    fb:matchDate "2018-08-10" ;
    fb:matchday  1 ;
    fb:winner    <.../team/manchester-united> ;
    fb:loser     <.../team/leicester-city> .
```

Đọc thành lời: *"Trận này là một trận đấu; đội nhà là Man United; đội khách là Leicester; nhà ghi 2, khách ghi 1; đá ngày 10/8/2018; vòng 1; Man United thắng; Leicester thua."*

### 1.3. URI – thẻ căn cước

Trong lớp có thể có 2 bạn tên "Nam". Để không nhầm, mỗi bạn có **mã học sinh** riêng.
Trên web ngữ nghĩa, mỗi thứ có một **URI** – một địa chỉ web duy nhất, ví dụ:

```
http://example.org/football/resource/team/arsenal
```

Nhờ vậy "Arsenal" của mình không bao giờ bị nhầm với "Arsenal" là kho vũ khí.

### 1.4. Thang 5 sao của dữ liệu mở (Tim Berners-Lee)

| Sao | Ý nghĩa | Ví von | Dự án này |
|---|---|---|---|
| ★ | Đưa dữ liệu lên mạng, giấy phép mở | Dán bài lên bảng tin | Nguồn OpenFootball là public domain |
| ★★ | Dữ liệu có cấu trúc | Viết thành bảng chứ không phải ảnh chụp | File CSV |
| ★★★ | Định dạng ai cũng mở được | Không cần phần mềm trả phí | CSV, Turtle |
| ★★★★ | Dùng URI để gọi tên mọi thứ | Ai cũng có mã học sinh | `to_rdf.py` gán URI cho mọi đội/trận/mùa |
| ★★★★★ | Nối sang dữ liệu của người khác | Kết bạn với lớp bên cạnh | `owl:sameAs` sang Wikidata, DBpedia |

---

## 2. Bước 1 – Ontology: cuốn "từ điển luật chơi"

File: [ontology/football.ttl](../ontology/football.ttl)

### 2.1. Ontology là gì?

**Ontology** giống cuốn sách luật chơi của một môn thể thao. Nó nói:
- Có những **loại đồ vật** nào (gọi là *class*): Đội, Trận đấu, Mùa giải, Giải đấu…
- Chúng **liên quan** với nhau thế nào (gọi là *property*): trận đấu *có đội nhà*, mùa giải *thuộc về* giải đấu…
- Những **luật** không được phá: một trận chỉ có **một** đội nhà; trận hoà thì **không có** đội thắng…

Ontology viết bằng ngôn ngữ **OWL** (Web Ontology Language).

### 2.2. Các "loại" (class)

| Class | Dòng | Nghĩa | Luật đi kèm |
|---|---|---|---|
| `fb:Competition` | [L31](../ontology/football.ttl#L31) | Giải đấu (chung chung) | là một loại `schema:SportsOrganization` |
| `fb:League` | [L36](../ontology/football.ttl#L36) | Giải vô địch (đá vòng tròn) | **phải có đúng 1** hạng (`tier`) – dòng 38 |
| `fb:Cup` | [L42](../ontology/football.ttl#L42) | Cúp (đá loại trực tiếp) | **không thể** vừa là League vừa là Cup (`owl:disjointWith`) |
| `fb:Season` | [L48](../ontology/football.ttl#L48) | Một mùa giải, ví dụ "Premier League 2018/19" | thuộc **đúng 1** giải |
| `fb:Team` | [L54](../ontology/football.ttl#L54) | Câu lạc bộ | là một loại `schema:SportsTeam` |
| `fb:Match` | [L59](../ontology/football.ttl#L59) | Một trận đã đá | **đúng 1** đội nhà, **đúng 1** đội khách, **đúng 1** mùa |
| `fb:Draw` | [L67](../ontology/football.ttl#L67) | Trận hoà | là một loại Match, và **không thể** có đội thắng |

**Cây gia đình** của các class (giống "chó là động vật, động vật là sinh vật"):

```
schema:SportsOrganization          schema:SportsEvent        schema:SportsTeam
        │                                 │                        │
  fb:Competition                      fb:Match                 fb:Team
     ┌──┴──┐                              │
 fb:League fb:Cup                      fb:Draw
```

Dòng [L73-74](../ontology/football.ttl#L73) nói: *Giải đấu, Mùa giải, Đội, Trận đấu là 4 thứ hoàn toàn khác nhau* – một đội không thể đồng thời là một trận.

> **Kiến thức:** `rdfs:subClassOf` = "là một loại của". Nhờ nó, máy tự **suy ra**: mọi trận hoà cũng là trận đấu, mọi trận đấu cũng là "sự kiện thể thao" theo schema.org.

### 2.3. Vì sao lại dính tới `schema:` ?

`schema.org` là bộ từ vựng mà Google, Bing… dùng. Ở dòng [L15-25](../ontology/football.ttl#L15) mình **khai báo mượn** các từ của họ, rồi nói "Team của mình là một loại SportsTeam của schema.org".
Như vậy, máy nào hiểu schema.org cũng hiểu được dữ liệu của mình. Đây gọi là **tái sử dụng từ vựng** – một nguyên tắc quan trọng của Linked Data: *đừng tự phát minh lại cái bánh xe*.

### 2.4. Các "mối quan hệ" (object property – nối vật với vật)

| Property | Dòng | Nghĩa | Luật |
|---|---|---|---|
| `fb:participant` | [L80](../ontology/football.ttl#L80) | "đội tham gia trận" (cha của 4 cái dưới) | – |
| `fb:homeTeam` | [L85](../ontology/football.ttl#L85) | đội nhà | *Functional* = chỉ có 1 giá trị |
| `fb:awayTeam` | [L89](../ontology/football.ttl#L89) | đội khách | Functional |
| `fb:winner` | [L93](../ontology/football.ttl#L93) | đội thắng | Functional |
| `fb:loser` | [L97](../ontology/football.ttl#L97) | đội thua | **không được trùng** với đội thắng (`propertyDisjointWith`) |
| `fb:inSeason` | [L102](../ontology/football.ttl#L102) | trận thuộc mùa nào | Functional |
| `fb:seasonOf` | [L108](../ontology/football.ttl#L108) | mùa thuộc giải nào | Functional |
| `fb:hasSeason` | [L113](../ontology/football.ttl#L113) | giải có những mùa nào | là **chiều ngược** của `seasonOf` |
| `fb:inCompetition` | [L117](../ontology/football.ttl#L117) | trận thuộc giải nào | **tự suy ra** – xem dưới |

**Chuỗi suy luận** ở dòng [L120](../ontology/football.ttl#L120):

```turtle
owl:propertyChainAxiom ( fb:inSeason fb:seasonOf )
```

Nghĩa là: *"Nếu trận X thuộc mùa Y, và mùa Y thuộc giải Z, thì trận X thuộc giải Z."*
Giống như: *"Nếu Lan học lớp 5A, và lớp 5A thuộc trường Kim Đồng, thì Lan học trường Kim Đồng."*
Mình **không cần** ghi thẳng "trận X thuộc giải Z" vào dữ liệu – một chương trình suy luận (reasoner, ví dụ HermiT trong Protégé) sẽ tự hiểu.

### 2.5. Các "thuộc tính số/chữ" (datatype property – nối vật với con số, ngày tháng)

Dòng [L128-177](../ontology/football.ttl#L128): `homeGoals`, `awayGoals` (số bàn, ≥ 0), `matchDate` (ngày), `matchday` (vòng đấu, ≥ 1), `stage` (tên vòng cúp, ví dụ "Final"), `tier` (hạng 1–5), `seasonLabel` ("2018/19"), `startDate`, `endDate`.

> **Kiến thức:** Có 2 loại property. *Object property* nối **vật ↔ vật** (trận → đội). *Datatype property* nối **vật ↔ giá trị** (trận → số 2).

---

## 3. Bước 2 – Thu thập và làm sạch dữ liệu

File: [src/clean_data.py](../src/clean_data.py)

### 3.1. Dữ liệu gốc trông thế nào?

Thư mục `england_csv/` (lấy từ dự án OpenFootball) có các thư mục theo thập kỷ → mùa → file. Một file như `england_csv/2010s/2018-19/eng.1.csv`:

```
Round,Date,Team 1,FT,Team 2
1,Fri Aug 10 2018,Manchester United FC,2-1,Leicester City FC
```

- `eng.1` = Premier League (hạng 1), `eng.2` = hạng 2, …, `eng.5` = hạng 5, `eng.cup` = FA Cup.
- `FT` = Full Time = tỉ số cuối trận.

### 3.2. Vì sao phải "làm sạch"?

Dữ liệu thật **luôn bừa bộn**, giống vở ghi của nhiều bạn khác nhau:
- Có bạn viết "Manchester Utd", có bạn viết "Manchester United FC" → thực ra là **một** đội.
- Có trận chưa đá (hoãn vì COVID) → không có tỉ số.
- Năm 2004 các giải hạng 2–4 **đổi tên** (First Division → Championship).
- Có hai đội tên gần giống nhau nhưng **khác nhau**: Wimbledon FC (cũ) và AFC Wimbledon (lập năm 2002).

### 3.3. Đi qua từng phần code

**a) Bốn "khuôn" dữ liệu – dòng [L47-79](../src/clean_data.py#L47)**
`Match`, `Team`, `Competition`, `Season` là 4 cái khuôn (`dataclass`). Giống tờ phiếu in sẵn ô: phiếu trận đấu có ô *ngày*, *đội nhà*, *đội khách*, *bàn nhà*, *bàn khách*…

**b) Danh sách 9 giải – dòng [L82-95](../src/clean_data.py#L82)**
Mỗi giải có mã, tên và hạng (`tier`). FA Cup có `tier = None` vì cúp không có hạng.

**c) Xử lý chuyện đổi tên năm 2004 – dòng [L98-111](../src/clean_data.py#L98)**
```python
renamed = start_year >= 2004
"eng.2": "championship" if renamed else "first-division",
```
Nghĩa: file `eng.2` của mùa từ 2004 trở đi là "Championship", trước đó là "First Division". Hai giải là **hai thứ khác nhau** trong dữ liệu, nhưng cùng `tier = 2`.

**d) Gộp tên đội viết khác nhau – dòng [L27-36](../src/clean_data.py#L27) và [L118-122](../src/clean_data.py#L118)**
`TEAM_ALIASES` là một "sổ tra biệt danh": `"Wolves" → "Wolverhampton Wanderers FC"`.
Hàm `canonical_team_name` tra sổ đó, rồi xoá phần ghi chú trong ngoặc (ví dụ "(1992-2011)").

**e) Tạo mã đội (slug) – dòng [L125-136](../src/clean_data.py#L125)**
Từ tên đội tạo ra mã ngắn, chỉ có chữ thường và dấu gạch:
`"Brighton & Hove Albion FC"` → `brighton-and-hove-albion`.
- Bỏ dấu tiếng nước ngoài (dòng 129-130).
- `&` thành `and` (dòng 131).
- Bỏ chữ "fc", "afc" (dòng 133) để "Arsenal" và "Arsenal FC" ra **cùng** một mã.
- Riêng AFC Wimbledon được giữ mã `afc-wimbledon` (dòng [L38-40](../src/clean_data.py#L38)) để không bị nhập nhầm với Wimbledon FC cũ.

> **Kiến thức:** Mã này sẽ trở thành đuôi của URI (`.../team/arsenal`). URI phải **ổn định** – chạy lại bao nhiêu lần cũng ra y hệt – nên mới cần quy tắc chặt chẽ như vậy.

**f) Đọc ngày tháng – dòng [L139-148](../src/clean_data.py#L139)**
`"Sat Aug 15 1992"` → ngày 15/8/1992 (dùng `datetime.strptime` có sẵn của Python).
Dòng 146 còn **kiểm tra thứ trong tuần**: nếu file ghi "Thứ Hai" mà ngày đó thật ra là "Thứ Ba" → báo lỗi. Đây là cách bắt lỗi gõ sai.

**g) Đọc tỉ số – dòng [L151-155](../src/clean_data.py#L151)**
`"2-1"` → `(2, 1)`. Chấp nhận cả gạch ngắn `-` và gạch dài `–` (dòng 23).

**h) Đọc vòng đấu – dòng [L158-171](../src/clean_data.py#L158)**
Giải vô địch: vòng là **số** (1, 2, …, 38). Cúp: vòng là **tên** ("Final", "Semi-finals").

**i) Đọc cả một file – dòng [L174-243](../src/clean_data.py#L174)**
Với mỗi dòng trong file:
1. Không có tỉ số → **bỏ qua** và đếm (dòng 200-202). Có 2.061 trận như vậy.
2. Đọc vòng, ngày, tên đội, tỉ số (dòng 204-208).
3. Đội nhà trùng đội khách → **lỗi** (dòng 215-216).
4. Nếu một đội xuất hiện với 2 tên ("Arsenal" và "Arsenal FC"), giữ **tên dài hơn** (dòng 222-225).
5. Tạo mã trận = `ngày-độinhà-độikhách`, ví dụ `2018-08-10-manchester-united-leicester-city` (dòng 229).

**j) Cảnh báo mùa giải bất thường – dòng [L246-263](../src/clean_data.py#L246)**
Luật bóng đá: giải vô địch đá **vòng tròn 2 lượt** – mỗi đội gặp mọi đội khác 1 lần sân nhà, 1 lần sân khách.
Với *n* đội thì có đúng **n × (n − 1)** trận. Ví dụ 20 đội → 20 × 19 = 380 trận.
Nếu đếm ra số khác → in **cảnh báo** (không dừng chương trình), vì dữ liệu gốc có vài lỗi thật (ví dụ Bury v Brentford mùa 2000-01 bị ghi 2 lần).

**k) Chạy tất cả – dòng [L288-338](../src/clean_data.py#L288)**
- Tìm mọi file `eng.*.csv` (dòng 266-276).
- Đọc từng file, tạo mùa giải với ngày bắt đầu = trận sớm nhất, ngày kết thúc = trận muộn nhất (dòng 305-314).
- Kiểm tra **không có hai trận trùng mã** (dòng 317-319).
- Ghi ra 4 file sạch trong `data/processed/` (dòng 324-331).

**Kết quả:** 45.849 trận, 153 đội, 97 mùa giải, 9 giải đấu.

---

## 4. Bước 3 – Biến bảng thành RDF (4 sao)

File: [src/to_rdf.py](../src/to_rdf.py)

### 4.1. Ý tưởng

Mỗi **dòng** trong bảng CSV → một **nhóm câu RDF**. Mỗi ô trong dòng → một câu.

```
matches.csv:  match_id | home_team_id | home_goals | ...
              m1       | arsenal      | 2          | ...
                   ↓
RDF:          m1  fb:homeTeam  arsenal .
              m1  fb:homeGoals 2 .
```

### 4.2. Đi qua từng phần code

**a) Các "họ" địa chỉ (namespace) – dòng [L18-23](../src/to_rdf.py#L18)**
```python
FB  = Namespace("http://example.org/football/ontology#")   # từ trong cuốn luật chơi
RES = Namespace("http://example.org/football/resource/")   # các đồ vật thật (đội, trận…)
WD  = Namespace("http://www.wikidata.org/entity/")          # Wikidata
DBR = Namespace("http://dbpedia.org/resource/")             # DBpedia
```
Namespace giống **họ** của một người: thay vì viết cả địa chỉ dài, chỉ cần `fb:Match` hay `wd:Q9617`.

**b) Hàm tạo URI – dòng [L45-47](../src/to_rdf.py#L45)**
```python
def uri(kind, entity_id):
    return RES[f"{kind}/{entity_id}"]
```
`uri("team", "arsenal")` → `http://example.org/football/resource/team/arsenal`. Đây chính là **sao thứ 4**: mọi thứ có tên riêng trên web.

**c) Giải đấu – dòng [L53-60](../src/to_rdf.py#L53)**
Có hạng → là `fb:League` và ghi `fb:tier`. Không có hạng → là `fb:Cup`.

**d) Mùa giải – dòng [L62-71](../src/to_rdf.py#L62)**
Ghi: là `fb:Season`, thuộc giải nào (`fb:seasonOf`), nhãn "2018/19", ngày bắt đầu/kết thúc, và tên đầy đủ "Premier League 2018/19".

**e) Đội – dòng [L73-76](../src/to_rdf.py#L73)**
Ghi: là `fb:Team`, tên là gì (`rdfs:label`).

**f) Trận đấu – dòng [L78-100](../src/to_rdf.py#L78)** – phần quan trọng nhất
- Dòng 83-89: loại, mùa, đội nhà, đội khách, số bàn, ngày.
- Dòng 90-93: vòng là số → `fb:matchday`; là chữ → `fb:stage`.
- Dòng 95-100: **tính kết quả**:
  - Bàn bằng nhau → gắn thêm loại `fb:Draw` (trận hoà).
  - Không thì ghi `fb:winner` (đội thắng) và `fb:loser` (đội thua).

> **Kiến thức – kiểu dữ liệu:** Số bàn được ghi là `xsd:nonNegativeInteger` (số nguyên không âm), ngày là `xsd:date`. Nhờ vậy máy biết `2` là **con số** (cộng trừ được) chứ không phải chữ "2", và biết so sánh ngày trước/sau.

**g) Ghi ra file – dòng [L165-183](../src/to_rdf.py#L165)**
Ba file trong `data/rdf/`:
- `football.ttl` – dữ liệu chính (~447.000 câu)
- `links.ttl` – các liên kết ra ngoài (333 câu)
- `void.ttl` – thẻ giới thiệu bộ dữ liệu (38 câu)

---

## 5. Bước 4 – Nối sang Wikidata, DBpedia (5 sao)

### 5.1. Vì sao phải nối?

Dữ liệu của mình chỉ biết tỉ số. Nhưng **Wikidata** (một "Wikipedia cho máy") biết thêm: sân vận động, năm thành lập, thành phố…
Nếu mình nói được *"Arsenal của mình **chính là** Arsenal bên Wikidata (mã Q9617)"*, thì máy có thể **ghép** hai nguồn lại và trả lời câu hỏi mà một mình không trả lời được.

Câu nối đó dùng từ `owl:sameAs` – nghĩa là **"chính là cùng một thứ"**:

```turtle
<.../team/arsenal> owl:sameAs wd:Q9617 , dbr:Arsenal_F.C. .
```

Đây chính là **sao thứ 5**.

### 5.2. Tìm Wikidata cho từng đội – [src/link_wikidata.py](../src/link_wikidata.py)

Có 153 đội, tra tay thì mỏi tay, nên chương trình tự đi hỏi:

**a) Gọi API Wikidata, kiên nhẫn khi bị từ chối – dòng [L37-56](../src/link_wikidata.py#L37)**
Wikidata không thích bị hỏi dồn dập. Nếu nó trả lời "chậm lại!" (mã lỗi 429) thì chương trình **đợi** rồi hỏi lại, mỗi lần đợi lâu gấp đôi (2s, 4s, 8s…). Cách này gọi là *exponential backoff* – giống khi gõ cửa không ai mở thì đợi lâu hơn rồi gõ tiếp, không đập cửa liên tục.

**b) Thử nhiều cách viết tên – dòng [L59-65](../src/link_wikidata.py#L59)**
Wikipedia hay viết "Arsenal F.C." (có dấu chấm) còn dữ liệu mình viết "Arsenal FC". Nên thử cả hai.

**c) Chọn đúng kết quả – dòng [L68-98](../src/link_wikidata.py#L68)**
Tìm "Arsenal" có thể ra: CLB bóng đá, ga tàu điện, kho vũ khí…
Chương trình chỉ nhận kết quả mà Wikidata ghi là **"là một câu lạc bộ bóng đá"** (thuộc tính `P31` nằm trong `CLUB_CLASSES`, dòng [L30-34](../src/link_wikidata.py#L30)).
Từ kết quả đó lấy luôn tên trang Wikipedia tiếng Anh → đó cũng là tên trên DBpedia (dòng 92-96).

**d) Lưu dần, chạy lại được – dòng [L123-134](../src/link_wikidata.py#L123)**
Sau **mỗi** đội là lưu file ngay. Nếu mất mạng giữa chừng, chạy lại sẽ **bỏ qua** đội đã tìm xong. Như chơi game có "lưu điểm".

**Kết quả:** `data/links/team_links.csv`, ví dụ:
```
team_id,name,wikidata,wikidata_label,dbpedia
arsenal,Arsenal FC,Q9617,Arsenal F.C.,Arsenal_F.C.
```
153/153 đội có link (5 đội phải sửa tay vì tên quá cũ). 9 giải đấu được tra tay trong `data/links/competition_links.csv`.

### 5.3. Viết link thành RDF – [src/to_rdf.py L105-124](../src/to_rdf.py#L105)

- Dòng 109-110: mọi giải đấu đều **diễn ra ở** nước Anh (`schema:location wd:Q21` – Q21 là mã của nước Anh trên Wikidata).
- Dòng 112-122: đọc hai file link, mỗi dòng sinh ra 2 câu `owl:sameAs` (một sang Wikidata, một sang DBpedia).

---

## 6. Kiểm tra chất lượng bằng SHACL

Files: [shapes/football-shapes.ttl](../shapes/football-shapes.ttl), [src/validate.py](../src/validate.py)

### 6.1. Ontology và SHACL khác nhau thế nào?

Đây là điểm **khó hiểu nhất**, nên giải thích kỹ:

- **OWL (ontology)** sống theo kiểu *"thế giới mở"*: nếu thiếu thông tin, nó nghĩ *"chắc có, chỉ là chưa ai ghi thôi"*. Ví dụ một trận không ghi đội nhà, OWL **không** báo lỗi – nó cho rằng đội nhà có tồn tại, chỉ là mình chưa biết.
- **SHACL** sống theo kiểu *"thế giới đóng"*: như **cô giáo chấm bài** – thiếu ô nào là trừ điểm ô đó.

Vì vậy cần cả hai: OWL để **suy luận**, SHACL để **bắt lỗi**.

### 6.2. Các luật kiểm tra

| Luật | Dòng | Bằng lời |
|---|---|---|
| `fb:MatchShape` | [L10](../shapes/football-shapes.ttl#L10) | Mỗi trận phải có **đúng 1** mùa, 1 đội nhà, 1 đội khách, 1 số bàn mỗi bên, 1 ngày |
| `sh:disjoint` | [L14](../shapes/football-shapes.ttl#L14) | Đội nhà **khác** đội khách |
| `sh:xone` thứ nhất | [L20](../shapes/football-shapes.ttl#L20) | Có **hoặc** số vòng **hoặc** tên vòng cúp – không được cả hai, không được thiếu cả hai (`xone` = "đúng một trong số này") |
| `sh:xone` thứ hai | [L25](../shapes/football-shapes.ttl#L25) | Trận **hoặc** là hoà, **hoặc** có đúng 1 đội thắng và 1 đội thua |
| `sh:lessThanOrEquals` | [L38](../shapes/football-shapes.ttl#L38) | Ngày bắt đầu mùa ≤ ngày kết thúc |
| `fb:LeagueShape` | [L41](../shapes/football-shapes.ttl#L41) | Giải vô địch phải có hạng |
| `fb:LinkedShape` | [L46](../shapes/football-shapes.ttl#L46) | Mọi đội và giải phải có **đúng 1** link Wikidata (kiểm tra sao thứ 5) |

### 6.3. Chương trình chấm – [src/validate.py](../src/validate.py)

- Dòng 13: nạp cả ontology – để SHACL biết "League là một loại Competition" (nếu không, nó tưởng mùa giải trỏ tới một thứ lạ).
- Dòng 17-19: hàm `check` gọi thư viện `pyshacl` để chấm.
- Dòng 22-28: chấm toàn bộ dữ liệu, in kết quả; đạt → thoát mã 0, trượt → mã 1.

**Kết quả hiện tại:** `Conforms: True` – toàn bộ 447.000 câu đều đạt.

---

## 7. Tấm "thẻ giới thiệu" VoID/DCAT

Code: [src/to_rdf.py L127-162](../src/to_rdf.py#L127) → file `data/rdf/void.ttl`

Khi mua một hộp bánh, bên ngoài hộp có ghi: tên, nhà sản xuất, thành phần, khối lượng. **VoID** và **DCAT** là cái "vỏ hộp" cho bộ dữ liệu, để người khác (và máy tìm kiếm) biết bên trong có gì **mà không cần mở ra**:

| Thông tin | Dòng | Ví dụ |
|---|---|---|
| Tên, mô tả | 137-139 | "English Football Linked Data" |
| Nguồn gốc | 140 | github.com/footballcsv/england |
| Giấy phép | 141 | CC0 (ai dùng cũng được) |
| Nơi hỏi đáp | 142 | `http://localhost:3030/football/sparql` |
| Tổng số câu | 146 | 447.315 |
| Có bao nhiêu thứ mỗi loại | 147-151 | 45.849 trận, 153 đội, 97 mùa… |
| Nối ra ngoài bao nhiêu | 153-161 | 162 link Wikidata, 162 link DBpedia |

Các con số được **tự đếm** từ dữ liệu thật, nên không bao giờ bị sai lệch.

---

## 8. Bước 5 – Hỏi đáp bằng SPARQL

### 8.1. SPARQL là gì?

**SPARQL** là ngôn ngữ để **hỏi** dữ liệu RDF – giống như SQL cho cơ sở dữ liệu thường.
Cách hỏi rất giống **trò điền vào chỗ trống**: mình viết câu có chỗ trống (biến bắt đầu bằng `?`), máy tìm mọi cách điền cho đúng.

```sparql
SELECT ?doi WHERE {
  ?tran fb:winner ?doi .        # "trận ___ có đội thắng là ___"
}
```

### 8.2. Máy chủ Fuseki – [fuseki/config.ttl](../fuseki/config.ttl)

**Apache Jena Fuseki** là một "quầy hỏi đáp" chạy trên máy: nhận câu hỏi SPARQL qua web và trả lời.
- Dòng [L9-11](../fuseki/config.ttl#L9): cho phép **hỏi sang máy chủ khác** (Wikidata) – cần cho truy vấn liên hợp.
- Dòng [L13-18](../fuseki/config.ttl#L13): mở dịch vụ tên `football`, địa chỉ `/football/sparql`, **chỉ đọc** (không ai sửa/xoá được dữ liệu).
- Dòng [L20-24](../fuseki/config.ttl#L20): nạp 4 file vào bộ nhớ: ontology, dữ liệu, link, thẻ giới thiệu.

Mở trình duyệt vào http://localhost:3030 là thấy giao diện để gõ câu hỏi.

### 8.3. Hỏi từ cửa sổ dòng lệnh – [src/query.py](../src/query.py)

- Dòng [L22-32](../src/query.py#L22) `run_remote`: gửi câu hỏi tới Fuseki, nhận kết quả dạng JSON.
- Dòng [L35-43](../src/query.py#L35) `run_local`: **không cần** Fuseki – tự nạp file vào Python rồi hỏi (chậm hơn).
- Dòng [L46-54](../src/query.py#L46) `shorten`: cắt bớt phần địa chỉ dài cho dễ đọc (`.../team/arsenal` → `team/arsenal`).
- Dòng [L57-65](../src/query.py#L57) `print_table`: in kết quả thành bảng ngay ngắn.

### 8.4. Các câu hỏi mẫu – thư mục [queries/](../queries/)

| File | Câu hỏi | Kiến thức minh hoạ |
|---|---|---|
| `01_standings` | Bảng xếp hạng Premier League 2018/19 | `UNION`, `GROUP BY`, `SUM` – **tự tính** điểm từ tỉ số. Ra Man City 98 điểm, Liverpool 97 – đúng như ngoài đời! |
| `02_head_to_head` | Arsenal gặp Tottenham bao nhiêu lần, ai thắng | Lọc theo 2 đội |
| `03_biggest_wins` | 10 trận thắng đậm nhất | `ORDER BY`, `LIMIT` |
| `04_all_tiers` | Đội nào từng đá ở cả 4 hạng | Đường đi thuộc tính `fb:homeTeam\|fb:awayTeam` |
| `05_home_advantage` | Tỉ lệ thắng sân nhà theo mùa | Thống kê |
| `06_ontology_reasoning` | Có bao nhiêu "sự kiện thể thao" theo schema.org | `rdfs:subClassOf*` – **dùng ontology để suy luận** ngay khi hỏi |
| `07_links` | Liệt kê các liên kết `owl:sameAs` | Chứng minh sao thứ 5 |
| `08_federated_wikidata` | Sân vận động và năm thành lập của các đội | `SERVICE` – **hỏi sang Wikidata** ngay trong câu hỏi |
| `09_fa_cup_finals` | Các trận chung kết FA Cup | Lọc theo `fb:stage` |

### 8.5. Ví dụ đọc hiểu: bảng xếp hạng (`01_standings.rq`)

```sparql
?m fb:inSeason <.../season/premier-league-2018-19> .      # lấy mọi trận của mùa 2018/19
{ ?m fb:homeTeam ?t ; fb:homeGoals ?gf ; fb:awayGoals ?ga }  # nhìn từ phía đội nhà
UNION
{ ?m fb:awayTeam ?t ; fb:awayGoals ?gf ; fb:homeGoals ?ga }  # HOẶC nhìn từ phía đội khách
BIND(IF(?gf > ?ga, 1, 0) AS ?w)                              # ghi bàn nhiều hơn → thắng
...
(3 * SUM(?w) + SUM(?d) AS ?Pts)                              # thắng 3 điểm, hoà 1 điểm
```

Mỗi trận được nhìn **hai lần** – một lần từ đội nhà, một lần từ đội khách – rồi cộng dồn theo từng đội. Luật tính điểm bóng đá (thắng 3, hoà 1, thua 0) nằm ngay trong câu hỏi.

### 8.6. Ví dụ đọc hiểu: hỏi liên hợp (`08_federated_wikidata.rq`)

```sparql
?t owl:sameAs ?wd .                                  # ở NHÀ MÌNH: đội ?t chính là ?wd bên Wikidata
SERVICE <https://query.wikidata.org/sparql> {        # chạy SANG WIKIDATA hỏi tiếp:
   ?wd wdt:P115 ?stadium .                           #   ?wd có sân nhà là gì? (P115 = sân nhà)
   ?wd wdt:P571 ?inception .                         #   ?wd thành lập năm nào? (P571 = ngày thành lập)
}
```

Dữ liệu của mình **không hề có** sân vận động hay năm thành lập. Nhưng nhờ cây cầu `owl:sameAs`, câu hỏi đi **sang nhà hàng xóm** lấy về. Đây là sức mạnh thật sự của 5 sao.

---

## 9. Các bài kiểm thử (test)

Test là các bài **tự kiểm tra** – chạy lệnh là biết code còn đúng không.

| File | Kiểm tra gì |
|---|---|
| [src/test_clean_data.py](../src/test_clean_data.py) | Tạo mã đội, đọc tỉ số, đọc ngày (kể cả ngày ghi sai thứ), biệt danh đội, đổi tên giải năm 2004, gộp giải + cúp, bỏ trận chưa đá |
| [src/test_to_rdf.py](../src/test_to_rdf.py) | Trận thắng có winner/loser đúng, trận hoà là `Draw` và không có winner, vòng đấu đúng, cúp là `Cup`, link `owl:sameAs` đúng, thẻ VoID đếm đúng |
| [src/test_validate.py](../src/test_validate.py) | Dữ liệu đúng → đạt; cố tình làm sai 4 kiểu (có cả vòng số lẫn tên vòng, trận hoà mà có đội thắng, đội nhà = đội khách, đội thiếu link) → **phải** bị bắt |

Chạy: `python -m unittest discover -s src -p "test_*.py"`

---

## 10. Cách chạy toàn bộ

```bash
pip install -r requirements.txt          # cài rdflib, pyshacl

python src/clean_data.py                 # 1. dọn dẹp → data/processed/
python src/link_wikidata.py              # 2. tìm link Wikidata (lâu; đã có sẵn kết quả, có thể bỏ qua)
python src/to_rdf.py                     # 3. viết RDF → data/rdf/  (~1 phút)
python src/validate.py                   # 4. chấm bài SHACL (~2 phút)

# 5. mở quầy hỏi đáp (cần Java 17+, Fuseki đặt trong tools/)
java -jar tools/apache-jena-fuseki-6.2.0/fuseki-server.jar --config fuseki/config.ttl

# 6. đặt câu hỏi (mở cửa sổ dòng lệnh khác)
python src/query.py queries/01_standings.rq
python src/query.py queries/01_standings.rq --local     # không cần Fuseki
```

---

## 11. Từ điển nhỏ

| Từ | Giải thích cho bạn lớp 5 |
|---|---|
| **Semantic Web** (Web ngữ nghĩa) | Phiên bản của web mà máy tính cũng **hiểu nghĩa** |
| **RDF** | Cách viết mọi thông tin thành câu 3 phần: *ai – có gì – cái gì* |
| **Triple** | Một câu 3 phần như vậy |
| **Turtle (.ttl)** | Một cách viết RDF gọn gàng, dễ đọc |
| **URI** | "Mã học sinh" trên web – mỗi thứ một mã, không trùng |
| **Namespace / prefix** | "Họ" của URI, viết tắt cho gọn (`fb:`, `wd:`) |
| **Ontology** | Cuốn luật chơi: có những loại gì, liên quan thế nào |
| **OWL** | Ngôn ngữ để viết ontology |
| **Class** | Một "loại" (Đội, Trận đấu…) |
| **Property** | Một "mối quan hệ" (có đội nhà, thuộc mùa…) |
| **subClassOf** | "là một loại của" (Trận hoà là một loại Trận đấu) |
| **Functional property** | Quan hệ chỉ có **một** giá trị (một trận chỉ có một đội nhà) |
| **Reasoner** | Chương trình **tự suy ra** điều mới từ luật (như giải toán suy luận) |
| **owl:sameAs** | "Chính là cùng một thứ" – cây cầu nối sang dữ liệu khác |
| **Wikidata** | Wikipedia dành cho máy, ai cũng sửa được, có mã Q cho mọi thứ |
| **DBpedia** | Dữ liệu được rút ra từ Wikipedia |
| **SHACL** | "Cô giáo chấm bài" – kiểm tra dữ liệu có thiếu, có sai không |
| **VoID / DCAT** | "Vỏ hộp" ghi bộ dữ liệu có gì bên trong |
| **SPARQL** | Ngôn ngữ để **hỏi** dữ liệu RDF, kiểu điền vào chỗ trống |
| **Endpoint** | Địa chỉ web để gửi câu hỏi SPARQL tới |
| **Fuseki** | Phần mềm làm "quầy hỏi đáp" SPARQL |
| **Federated query** | Câu hỏi chạy **sang máy chủ khác** để lấy thêm thông tin |
| **CSV** | Bảng tính đơn giản, các ô cách nhau bằng dấu phẩy |
| **Slug** | Mã ngắn chỉ có chữ thường và gạch ngang (`manchester-united`) |
| **Pipeline** | Dây chuyền: đầu ra của bước trước là đầu vào của bước sau |

---

## Hạn chế cần biết (để trình bày thật thà với thầy cô)

1. **URI dùng `example.org`** – đây là tên miền "mẫu", gõ vào trình duyệt sẽ không ra gì. Muốn chuẩn 5 sao tuyệt đối thì cần đăng ký địa chỉ thật (ví dụ w3id.org hoặc GitHub Pages).
2. **Link DBpedia** được suy ra từ tên trang Wikipedia, chưa kiểm tra trực tiếp trên DBpedia.
3. **Suy luận OWL** (ví dụ `fb:inCompetition`) cần chạy reasoner (Protégé + HermiT) mới thấy; Fuseki hiện chỉ trả lời theo dữ liệu đã ghi.
4. **Dữ liệu gốc có vài lỗi** (Bury v Brentford 2000-01 bị ghi 2 lần, Championship 2015-16 thiếu 2 trận) – chương trình đã in cảnh báo chứ không tự đoán sửa.
