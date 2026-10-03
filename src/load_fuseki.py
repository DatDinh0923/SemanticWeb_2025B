"""Replace only phongph5's default graph with validated local artifacts."""
from urllib.request import Request, urlopen

from common import load_graph
from validate_rdf import validate_graph

URL = "http://localhost:3035/phongph5/data?default"


def main():
    graph = load_graph()
    conforms, _, report = validate_graph(graph)
    if not conforms:
        raise ValueError(report)
    request = Request(URL, data=graph.serialize(format="turtle").encode("utf-8"), method="PUT",
                      headers={"Content-Type": "text/turtle; charset=utf-8"})
    with urlopen(request, timeout=60) as response:
        print(f"Loaded {len(graph)} triples into phongph5 (HTTP {response.status}).")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Fuseki load failed (is scripts/fuseki.ps1 start running?): {exc}") from exc
