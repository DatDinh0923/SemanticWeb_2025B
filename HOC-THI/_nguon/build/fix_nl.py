from pathlib import Path
p = Path(__file__).parent / "rdf.js"
s = p.read_text(encoding="utf-8")
s = s.replace("split('\n')", "split('\\n')")
p.write_text(s, encoding="utf-8")
print("ok")
