# Các chương trình Python

Hướng dẫn đầy đủ nằm trong [README gốc](../README.md).

| Chương trình | Vai trò |
| --- | --- |
| `pipeline.py` | Toàn bộ quy trình offline và tests |
| `clean_data.py` | Chuẩn hóa dữ liệu từ manifest 10 mùa |
| `convert_to_rdf.py` | Sinh RDF và liên kết đã xác minh |
| `validate_rdf.py` | Kiểm định SHACL |
| `query.py` | Truy vấn local/Fuseki, render hoặc so kết quả |
| `load_fuseki.py` | Nạp graph đã kiểm định vào dataset phongph5 |
| `collect_link_evidence.py` | Thu thập bằng chứng online, không tự xác minh mapping |

Chạy lệnh từ thư mục gốc repo:

```powershell
.\.venv\Scripts\python.exe src/pipeline.py
```
