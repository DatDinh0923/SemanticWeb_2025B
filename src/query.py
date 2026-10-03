"""Run saved SELECT/ASK queries locally or against Fuseki; optionally compare both."""
import argparse
import json
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rdflib import Literal
from rdflib.namespace import XSD
from common import CONFIG, RES, ROOT, load_graph, rows, template


def render_query(path, season="2018-19", team="arsenal", opponent="tottenham-hotspur"):
    seasons = {r["label"] for r in rows(ROOT / "config/seasons.csv")}
    teams = {r["team_id"] for r in rows(ROOT / "config/team-aliases.csv")}
    if season not in seasons or team not in teams or opponent not in teams:
        raise ValueError("Unknown season/team parameter; consult the manifest and alias table")
    text = template(path)
    for key, value in {
        "season": RES[f"season/{CONFIG['competition_id']}-{season}"],
        "team": RES[f"team/{team}"], "opponent": RES[f"team/{opponent}"],
    }.items():
        text = text.replace("{{" + key + "}}", value.n3())
    if "{{" in text:
        raise ValueError("Unresolved query parameter")
    return text


def run_local(graph, query):
    result = graph.query(query)
    if result.type == "ASK":
        return ["boolean"], [[Literal(result.askAnswer)]]
    if result.type != "SELECT":
        raise ValueError("Terminal supports SELECT and ASK queries")
    return [str(v) for v in result.vars], [list(row) for row in result]


def run_remote(query, endpoint=CONFIG["endpoint"]):
    request = Request(endpoint, data=urlencode({"query": query}).encode(),
                      headers={"Accept": "application/sparql-results+json"})
    with urlopen(request, timeout=60) as response:
        data = json.load(response)
    if "boolean" in data:
        return ["boolean"], [[Literal(data["boolean"])]]
    from rdflib import URIRef, BNode
    def term(binding):
        if binding is None:
            return None
        if binding["type"] == "uri":
            return URIRef(binding["value"])
        if binding["type"] == "bnode":
            return BNode(binding["value"])
        return Literal(binding["value"], lang=binding.get("xml:lang"), datatype=binding.get("datatype"))
    columns = data["head"]["vars"]
    return columns, [[term(row.get(c)) for c in columns] for row in data["results"]["bindings"]]


def canonical(value):
    if value is None:
        return ("unbound", "")
    if isinstance(value, Literal):
        python = value.toPython()
        if isinstance(python, (int, float, Decimal)) and not isinstance(python, bool):
            # AVG precision differs by engine; compare ten decimal places.
            return ("number", str(Decimal(str(python)).quantize(Decimal("0.0000000001"))))
        # RDF 1.1 plain strings and explicit xsd:string denote the same value.
        datatype = str(value.datatype or "")
        if not value.language and datatype in ("", str(XSD.string)):
            datatype = str(XSD.string)
        return ("literal", str(value), value.language or "", datatype)
    return ("term", str(value))


def equivalent(left, right):
    return left[0] == right[0] and Counter(tuple(canonical(v) for v in row) for row in left[1]) == Counter(tuple(canonical(v) for v in row) for row in right[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("query", nargs="?", type=Path)
    group.add_argument("--all", action="store_true")
    parser.add_argument("--season", default="2018-19")
    parser.add_argument("--team", default="arsenal")
    parser.add_argument("--opponent", default="tottenham-hotspur")
    parser.add_argument("--endpoint", nargs="?", const=CONFIG["endpoint"])
    parser.add_argument("--compare", action="store_true", help="Compare local results with Fuseki")
    parser.add_argument("--render", action="store_true", help="Print bound SPARQL for pasting into Fuseki")
    args = parser.parse_args()
    graph = load_graph() if not args.render and (not args.endpoint or args.compare) else None
    paths = sorted((ROOT / "queries").glob("*.rq")) if args.all else [args.query]
    if not paths:
        raise ValueError("No query files found")
    for path in paths:
        query = render_query(path, args.season, args.team, args.opponent)
        if args.render:
            print(query)
            continue
        result = run_remote(query, args.endpoint) if args.endpoint else run_local(graph, query)
        if args.compare:
            local = run_local(graph, query) if args.endpoint else result
            remote = result if args.endpoint else run_remote(query)
            if not equivalent(local, remote):
                raise ValueError(f"Result mismatch: {path.name}")
            print(f"MATCH {path.name}: {len(local[1])} rows")
        else:
            print(f"\n{path.name}\n" + "\t".join(result[0]))
            for row in result[1]:
                print("\t".join("" if v is None else re.sub(r"[\t\r\n]", " ", str(v)) for v in row))
            print(f"({len(result[1])} rows)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Query failed: {exc}") from exc
