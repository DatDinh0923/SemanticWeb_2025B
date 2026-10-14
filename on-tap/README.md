# Ôn thi Semantic Web (IT6390E) — thi viết tự luận 2–3 tiếng, **17/10/2026**

Bộ ôn tập dựa trên **bài tập giao trên lớp** (`Course materials/Exercises-en.docx`, `Exercises-OWL2.pdf`), **bài về nhà đã nộp** và **slide** (bộ IE650 Knowledge Graphs — Paulheim). Phần slide thiếu được bổ sung từ đặc tả W3C, mỗi chỗ đều đánh dấu *(bổ sung)* và ghi nguồn.

## Khoanh vùng
| Nguồn | Gợi ý |
|---|---|
| Ghi chú nghe ngóng (chưa chắc) | thi **bài OWL giống "bài 3"** + **một phần SPARQL**, tự luận 2–3 tiếng |
| "Bài 3" | khớp nhất với **Part 3 Ex3** (laboratory-course / teacher / professor / assistant / homework). Cũng có thể là **Exercises-OWL2 Ex3** (chứng minh tableau `Professor ⊑ ∃supervises.Employee`) ⇒ ôn **cả hai** |
| Bài về nhà | thầy giao tiếp phần bài trên lớp qua nhiều buổi: 29.08 → Part 1 Ex2 (RDF 3 dạng); 5.9 và 12.9 → **Part 2 Ex2 (suy diễn RDFS true/unknown — 2 tuần liền)**; 03.10 → tableau Ex1, Ex2 |

**Thứ tự ưu tiên:**
1. **D1** thiết kế OWL
2. **D2** SPARQL
3. **D3** tableau
4. **D4** suy diễn RDFS
5. **D5–D7** vẽ đồ thị, serialization, schema RDF/RDFS
6. **D8–D10** reasoner, sửa mô hình, LOD
7. lý thuyết

## Tài liệu
| File | Nội dung | Mức |
|---|---|---|
| [`00-chien-luoc-lam-bai.md`](00-chien-luoc-lam-bai.md) | phân bổ thời gian, khuôn trình bày từng dạng, lỗi hay mất điểm, những thứ phải thuộc | đọc đầu tiên + sáng ngày thi |
| [`02-owl.md`](02-owl.md) | OWL đầy đủ, bảng DL↔Manchester↔Turtle, khuôn thiết kế 6 bước, **lời giải Ex2/Ex3 (+6 biến thể)/Ex4, pizza**, bài tự luyện | ★★★ |
| [`03-owl2-tableau.md`](03-owl2-tableau.md) | DL, NNF, 7 luật, blocking, profiles; **cây tableau Ex1–Ex3**, 5 bài tự luyện | ★★★ |
| [`04-sparql.md`](04-sparql.md) | SPARQL slide + bổ sung 1.1; **25 bài viết truy vấn + 5 bài đoán kết quả** (kết quả chạy thật) | ★★★ |
| [`01-rdf-rdfs.md`](01-rdf-rdfs.md) | RDF/RDFS đầy đủ, bảng luật; **lời giải Part 1 Ex1–7, Part 2 Ex1–2 (18 mệnh đề)** | ★★★ |
| [`05-lod-modeling.md`](05-lod-modeling.md) | LOD (4 nguyên tắc, 5 sao, sameAs), OntoClean, anti-pattern, Sowa/DOLCE | ★★ |
| [`06-ly-thuyet.md`](06-ly-thuyet.md) | Intro + Ext (KG, LPG/Cypher, App) + câu tổng hợp — dạng hỏi/đáp | ★–★★ |
| [`07-de-thi-thu-1.md`](07-de-thi-thu-1.md), [`07-de-thi-thu-2.md`](07-de-thi-thu-2.md), [`07-dap-an.md`](07-dap-an.md) | 2 đề 180 phút (~70% thực hành) + đáp án + barem | ★★★ |
| [`checklist-do-phu.md`](checklist-do-phu.md) | mọi khái niệm của từng slide, tick khi đã tự giải thích được | dùng cuối mỗi ngày |
| [`files/`](files/) | ontology & dữ liệu chạy được (`.ttl`), 37 truy vấn (`queries/*.rq`), `run_queries.py`, `rdfs_closure.py` | thực hành |

## Lộ trình 3 ngày
| Thời gian | Việc | Mục tiêu đầu ra |
|---|---|---|
| **14/10 tối** | `00` + `02-owl.md` §A–C: tự làm **Ex3 trên giấy** trước, rồi so lời giải; làm V1–V6 | viết được Ex3 đủ 5 phần trong 40 phút |
| **15/10 sáng** | `02-owl.md` §D–G (Ex2, Ex4, pizza, M1–M3); `03-owl2-tableau.md`: tự vẽ lại Ex1–Ex3, rồi P1–P5 | không sai NNF; nhớ 7 luật |
| **15/10 chiều** | `04-sparql.md`: che lời giải, viết Q1–Q25, mở so sánh; làm P1–P5 | viết GROUP BY / OPTIONAL / NOT EXISTS / path không cần nhìn |
| **15/10 tối** | **Đề thi thử 1** — bấm giờ 180 phút, viết tay → chấm theo barem → ghi lỗi vào "sổ lỗi" | ≥ 70 điểm |
| **16/10 sáng** | `01-rdf-rdfs.md` (bảng 18 mệnh đề, RDF/XML) + `05-lod-modeling.md` | true/unknown có tên luật |
| **16/10 chiều** | **Đề thi thử 2** (180 phút) → chấm → sửa | ≥ 75 điểm |
| **16/10 tối** | `06-ly-thuyet.md` (tự trả lời T1–T17); `checklist-do-phu.md` tick hết ★★★; đọc lại sổ lỗi; **ngủ sớm** | |
| **17/10 sáng** | đọc `00-chien-luoc-lam-bai.md` §3–§4, bảng tra trong `02-owl.md` §A7 và `03` §1.5 | |

## Phương pháp
1. **Active recall:** luôn tự làm trên giấy **trước** khi mở `<details>` đáp án. Đọc lời giải mà không tự làm gần như không giúp nhớ.
2. **Viết tay:** thi tự luận viết tay. Hãy luyện viết Turtle, RDF/XML, vẽ cây tableau bằng tay, bấm giờ.
3. **Sổ lỗi:** mỗi lỗi sai ghi một dòng: *dạng bài – sai gì – vì sao – quy tắc đúng*. Đọc lại tối 16/10.
4. **Giải thích bằng lời:** một khái niệm chỉ được tick trong checklist khi nói lại được kèm ví dụ (OWA → Peter fatherOf Julia, Mary).
5. **Kiểm bằng máy khi nghi ngờ:** `cd files && pip install rdflib && python run_queries.py` (SPARQL); `python rdfs_closure.py` (bao đóng RDFS, 18 mệnh đề).

## Đính chính phát hiện khi soạn
- **Bài 12.9, câu 3** (`:hasFather rdfs:range :Father`): bài nộp ghi *Unknown*, đúng ra là **TRUE**. Triple này **có sẵn** trong đồ thị đề cho. Xem `01-rdf-rdfs.md` Part 2 Ex2; đã kiểm bằng `rdfs_closure.py`.
- **Bài 5.9:** luật "thay IRI ở vị trí object bằng blank node" có tên **se1** trong RDF 1.0 Semantics. **se2** là luật thay ở vị trí subject.

## Tài liệu gốc
Toàn bộ slide, đề bài tập, bài về nhà nằm ở [`../Course materials/`](../Course%20materials/). Danh sách lớp (`.xlsx`) cố ý **không** đưa lên vì chứa thông tin cá nhân. Lịch học xem `Schedule.png`.
