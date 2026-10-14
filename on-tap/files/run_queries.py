"""Chạy mọi truy vấn trong queries/*.rq trên file dữ liệu ghi ở dòng '# data:' và in kết quả.

Dùng:  python run_queries.py            # chạy tất cả
       python run_queries.py q04 q15    # chỉ chạy các truy vấn có tên bắt đầu như vậy
Cần:   pip install rdflib
"""
import sys
from pathlib import Path

from rdflib import Graph, URIRef

HERE = Path(__file__).parent
QUERIES = sorted((HERE / "queries").glob("*.rq"))
_graphs = {}


def graph_for(data_file):
    if data_file not in _graphs:
        g = Graph()
        g.parse(HERE / data_file, format="turtle")
        _graphs[data_file] = g
    return _graphs[data_file]


SHORT = {"http://example.org/course#": ":", "http://example.org/film#": ":",
         "http://example.org/library#": ":", "http://example.org/review#": ":",
         "http://example.org/food#": ":", "http://example.org/film/": "film:",
         "http://example.org/people/": "people:"}


def show(value):
    if value is None:
        return "-"
    if isinstance(value, URIRef):
        for long, short in SHORT.items():
            if value.startswith(long):
                return short + value[len(long):]
    return value.n3()


def run(path):
    text = path.read_text(encoding="utf-8")
    data = text.splitlines()[0].split("data:")[1].strip()
    result = graph_for(data).query(text)
    print(f"\n=== {path.stem}  ({data}) ===")
    if result.type == "ASK":
        print(result.askAnswer)
    elif result.type == "CONSTRUCT":
        for s, p, o in sorted(result):
            print(show(s), show(p), show(o), ".")
    else:
        names = [str(v) for v in result.vars]
        print(" | ".join(names))
        for row in result:
            print(" | ".join(show(row[v]) for v in names))


if __name__ == "__main__":
    prefixes = sys.argv[1:]
    for q in QUERIES:
        if not prefixes or any(q.stem.startswith(p) for p in prefixes):
            run(q)
