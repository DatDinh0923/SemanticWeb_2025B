"""thay đoạn app.js giữa 2 mốc bằng nội dung file: python splice.py <start-marker> <end-marker> <file>"""
import sys
from pathlib import Path
H = Path(__file__).parent
p = H / "app.js"
s = p.read_text(encoding="utf-8")
a = s.index(sys.argv[1])
b = s.index(sys.argv[2], a + 1)
s = s[:a] + (H / sys.argv[3]).read_text(encoding="utf-8") + s[b:]
p.write_text(s, encoding="utf-8")
print("spliced", a, b)
