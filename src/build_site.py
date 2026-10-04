#!/usr/bin/env python3
"""Build a static Linked Data browser suitable for GitHub Pages."""

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
from pathlib import Path

from rdflib import BNode, DCTERMS, OWL, RDF, RDFS, Graph, Literal, URIRef
from rdflib.compare import to_canonical_graph

from convert_to_rdf import BASE_URL, FOOT, SCHEMA


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = PROJECT_ROOT / "data/rdf/football-data.ttl"
DEFAULT_ONTOLOGY = PROJECT_ROOT / "ontology/football.ttl"
DEFAULT_OUTPUT = PROJECT_ROOT / "_site"

REPOSITORY_URL = "https://github.com/DatDinh0923/SemanticWeb_2025B"
SITE_NAME = "Premier League Linked Open Data"
# A competition is referenced by every match; list a readable number of them.
MAX_INBOUND_LINKS = 500

STYLES = """
:root {
  --ink: #10231e;
  --muted: #53635d;
  --paper: #f4f0e5;
  --panel: #fffdf6;
  --line: #c9d0c2;
  --accent: #087f5b;
  --accent-dark: #075b43;
  --navy: #102a43;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(circle at 8% 10%, rgba(8, 127, 91, .13), transparent 25rem),
    linear-gradient(135deg, var(--paper), #e8ede3);
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, serif;
  line-height: 1.55;
}
main { width: min(1120px, calc(100% - 2rem)); margin: 0 auto; padding: 3rem 0 5rem; }
.eyebrow { color: var(--accent-dark); font: 700 .78rem/1.2 ui-monospace, monospace; letter-spacing: .12em; text-transform: uppercase; }
h1 { max-width: 900px; margin: .4rem 0 1rem; color: var(--navy); font-size: clamp(2.2rem, 6vw, 5rem); line-height: .98; }
h2 { margin-top: 2rem; color: var(--navy); }
a { color: var(--accent-dark); text-decoration-thickness: .08em; text-underline-offset: .16em; overflow-wrap: anywhere; }
.lead { max-width: 780px; color: var(--muted); font-size: 1.15rem; }
.actions, .metrics { display: flex; flex-wrap: wrap; gap: .75rem; margin: 1.5rem 0; }
.button, .metric { border: 1px solid var(--line); background: rgba(255, 253, 246, .88); border-radius: .65rem; padding: .75rem 1rem; }
.button { background: var(--accent); color: white; font-weight: 700; text-decoration: none; }
.metric strong { display: block; color: var(--navy); font-size: 1.45rem; }
.panel { margin-top: 1.25rem; border: 1px solid var(--line); background: rgba(255, 253, 246, .9); border-radius: .85rem; padding: 1rem; box-shadow: 0 1rem 3rem rgba(16, 42, 67, .07); overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: .7rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { width: 28%; color: var(--navy); }
code, pre { font-family: "Cascadia Code", "IBM Plex Mono", ui-monospace, monospace; }
pre { padding: 1rem; background: #10231e; color: #e8fff6; border-radius: .6rem; overflow-x: auto; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--line); color: var(--muted); }
@media (max-width: 640px) { main { padding-top: 2rem; } th, td { display: block; width: 100%; } th { border-bottom: 0; padding-bottom: 0; } }
""".strip()


def title_for(graph: Graph, subject: URIRef) -> str:
    for predicate in (SCHEMA.name, RDFS.label, DCTERMS.title):
        value = graph.value(subject, predicate)
        if value is not None:
            return str(value)
    path = str(subject).rstrip("/").rsplit("/", 1)[-1]
    return path.replace("-", " ").title() or "Football Linked Data"


def local_output_path(output_dir: Path, subject: URIRef) -> Path:
    uri = str(subject)
    if not uri.startswith(BASE_URL):
        raise ValueError(f"Not a local project URI: {uri}")
    relative = uri[len(BASE_URL) :].strip("/")
    parts = [part for part in relative.split("/") if part]
    if any(part in {".", ".."} for part in parts):
        raise ValueError(f"Unsafe URI path: {uri}")
    return output_dir.joinpath(*parts, "index.html") if parts else output_dir / "index.html"


def relative_href(page_path: Path, target_path: Path) -> str:
    """Return a browser-safe relative link from one generated file to another."""
    return Path(os.path.relpath(target_path, start=page_path.parent)).as_posix()


def local_uri_href(
    graph: Graph, value: URIRef, page_path: Path, output_dir: Path
) -> str:
    """Map a canonical project URI to its local preview/deployment target."""
    uri = str(value)
    if uri == BASE_URL:
        target = output_dir / "index.html"
    elif any(graph.triples((value, None, None))):
        target = local_output_path(output_dir, value)
    else:
        target = output_dir / uri[len(BASE_URL) :].lstrip("/")
    return relative_href(page_path, target)


def describe_subject(graph: Graph, subject: URIRef) -> Graph:
    description = Graph()
    for prefix, namespace in graph.namespaces():
        description.bind(prefix, namespace)

    queue: list[URIRef | BNode] = [subject]
    visited: set[URIRef | BNode] = set()
    while queue:
        current = queue.pop()
        if current in visited:
            continue
        visited.add(current)
        for triple in graph.triples((current, None, None)):
            description.add(triple)
            if isinstance(triple[2], BNode):
                queue.append(triple[2])
    return description


def qname(graph: Graph, value: URIRef) -> str:
    try:
        return graph.namespace_manager.normalizeUri(value)
    except Exception:
        return str(value)


def render_term(
    graph: Graph, value: object, page_path: Path, output_dir: Path
) -> str:
    if isinstance(value, URIRef):
        uri = html.escape(str(value), quote=True)
        label = html.escape(qname(graph, value))
        href = (
            local_uri_href(graph, value, page_path, output_dir)
            if str(value).startswith(BASE_URL)
            else str(value)
        )
        return f'<a href="{html.escape(href, quote=True)}" title="{uri}">{label}</a>'
    if isinstance(value, Literal):
        text = html.escape(str(value))
        annotation = ""
        if value.language:
            annotation = f" <small>@{html.escape(value.language)}</small>"
        elif value.datatype:
            annotation = f" <small>^^{html.escape(qname(graph, value.datatype))}</small>"
        return f"{text}{annotation}"
    if isinstance(value, BNode):
        return "<em>Anonymous RDF definition (see Turtle)</em>"
    return html.escape(str(value))


def canonical_json_ld(graph: Graph) -> str:
    """Serialize JSON-LD with stable blank-node IDs and collection ordering."""
    document = json.loads(to_canonical_graph(graph).serialize(format="json-ld"))

    def normalize(value: object, parent_key: str | None = None) -> object:
        if isinstance(value, dict):
            return {
                key: normalize(item, key)
                for key, item in sorted(value.items())
            }
        if isinstance(value, list):
            items = [normalize(item) for item in value]
            if parent_key == "@list":
                return items
            return sorted(
                items,
                key=lambda item: json.dumps(
                    item, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ),
            )
        return value

    return json.dumps(
        normalize(document), ensure_ascii=False, indent=2, sort_keys=True
    ).replace("</", "<\\/")


def page_shell(
    title: str,
    body: str,
    style_href: str,
    canonical_uri: str | None = None,
    alternate_href: str | None = None,
) -> str:
    canonical = (
        f'<link rel="canonical" href="{html.escape(canonical_uri, quote=True)}">'
        if canonical_uri
        else ""
    )
    alternate = (
        '<link rel="alternate" type="text/turtle" '
        f'href="{html.escape(alternate_href, quote=True)}">'
        if alternate_href
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | {SITE_NAME}</title>
  {canonical}
  {alternate}
  <link rel="stylesheet" href="{html.escape(style_href, quote=True)}">
</head>
<body>
  <main>{body}</main>
</body>
</html>
"""


def inbound_index(graph: Graph) -> dict[URIRef, list[tuple[URIRef, URIRef]]]:
    """Map each local resource to the local resources that point at it."""
    index: dict[URIRef, list[tuple[URIRef, URIRef]]] = {}
    for subject, predicate, obj in graph:
        if (
            isinstance(obj, URIRef)
            and isinstance(subject, URIRef)
            and str(obj).startswith(BASE_URL)
            and str(subject).startswith(BASE_URL)
            and predicate != RDF.type
        ):
            index.setdefault(obj, []).append((subject, predicate))
    return index


def render_inbound(
    graph: Graph,
    references: list[tuple[URIRef, URIRef]],
    page_path: Path,
    output_dir: Path,
) -> str:
    """Render the resources that link to this page, so browsing works both ways."""
    if not references:
        return ""
    ordered = sorted(
        references, key=lambda item: (str(item[1]), title_for(graph, item[0]))
    )
    rows = "\n".join(
        f"<tr><th>{render_term(graph, predicate, page_path, output_dir)}</th>"
        f"<td>{render_term(graph, source, page_path, output_dir)}"
        f" <small>{html.escape(title_for(graph, source))}</small></td></tr>"
        for source, predicate in ordered[:MAX_INBOUND_LINKS]
    )
    hidden = len(ordered) - MAX_INBOUND_LINKS
    more = (
        f"<p>…and {hidden} more; use the SPARQL queries to list them all.</p>"
        if hidden > 0
        else ""
    )
    return f"""
<section class="panel">
  <h2>Referenced by ({len(ordered)})</h2>
  <table><tbody>{rows}</tbody></table>
  {more}
</section>"""


def write_resource_page(
    graph: Graph,
    subject: URIRef,
    output_dir: Path,
    references: list[tuple[URIRef, URIRef]] | None = None,
) -> None:
    title = title_for(graph, subject)
    description = describe_subject(graph, subject)
    page_path = local_output_path(output_dir, subject)
    triples = sorted(
        description.triples((subject, None, None)),
        key=lambda triple: (str(triple[1]), str(triple[2])),
    )
    rows = "\n".join(
        f"<tr><th>{render_term(graph, predicate, page_path, output_dir)}</th>"
        f"<td>{render_term(graph, obj, page_path, output_dir)}</td></tr>"
        for _, predicate, obj in triples
    )
    inbound = render_inbound(graph, references or [], page_path, output_dir)
    json_ld = canonical_json_ld(description)
    home_href = relative_href(page_path, output_dir / "index.html")
    body = f"""
<p class="eyebrow">Linked data resource</p>
<h1>{html.escape(title)}</h1>
<p class="lead">Canonical URI: <a href="{html.escape(str(subject), quote=True)}">{html.escape(str(subject))}</a></p>
<div class="actions">
  <a class="button" href="data.ttl">Download this resource as Turtle</a>
  <a href="{html.escape(home_href, quote=True)}">Dataset home</a>
</div>
<section class="panel">
  <table><tbody>{rows}</tbody></table>
</section>
{inbound}
<script type="application/ld+json">{json_ld}</script>
<footer>{SITE_NAME} · CC0 1.0</footer>
"""
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(
        page_shell(
            title,
            body,
            relative_href(page_path, output_dir / "assets/style.css"),
            canonical_uri=str(subject),
            alternate_href="data.ttl",
        ),
        encoding="utf-8",
    )
    description.serialize(destination=page_path.parent / "data.ttl", format="turtle")


def copy_public_downloads(
    output_dir: Path, data_path: Path, ontology_path: Path
) -> None:
    download_dir = output_dir / "download"
    csv_dir = download_dir / "csv"
    ontology_dir = output_dir / "ontology"
    download_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    ontology_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(data_path, download_dir / "football-data.ttl")
    shutil.copy2(ontology_path, ontology_dir / "football.ttl")
    shutil.copy2(
        PROJECT_ROOT / "shapes/football-shapes.ttl",
        download_dir / "football-shapes.ttl",
    )
    shutil.copy2(
        PROJECT_ROOT / "data/links/entity-links.csv",
        download_dir / "entity-links.csv",
    )
    shutil.copy2(PROJECT_ROOT / "LICENSE-DATA.md", download_dir / "LICENSE-DATA.md")
    for source in sorted((PROJECT_ROOT / "data/processed").glob("*.csv")):
        shutil.copy2(source, csv_dir / source.name)


def resource_list(graph: Graph, resources: list[URIRef]) -> str:
    items = "\n".join(
        f'    <li><a href="{html.escape(str(resource)[len(BASE_URL):], quote=True)}/">'
        f"{html.escape(title_for(graph, resource))}</a></li>"
        for resource in resources
    )
    return f"  <ul>\n{items}\n  </ul>"


def write_home_page(graph: Graph, output_dir: Path) -> None:
    seasons = sorted(
        set(graph.subjects(RDF.type, FOOT.Season)),
        key=lambda season: str(graph.value(season, FOOT.seasonLabel) or season),
    )
    teams = sorted(
        set(graph.subjects(RDF.type, FOOT.FootballTeam)),
        key=lambda team: title_for(graph, team),
    )
    match_count = len(set(graph.subjects(RDF.type, FOOT.FootballMatch)))
    external_link_count = len(list(graph.triples((None, OWL.sameAs, None))))
    first_season = graph.value(seasons[0], FOOT.seasonLabel) if seasons else ""
    last_season = graph.value(seasons[-1], FOOT.seasonLabel) if seasons else ""
    body = f"""
<p class="eyebrow">Five-star linked open data</p>
<h1>Premier League, expressed as a knowledge graph.</h1>
<p class="lead">Clubs and results from {len(seasons)} seasons ({first_season} to {last_season}), published as RDF with stable HTTP URIs and verified links to Wikidata and DBpedia.</p>
<div class="metrics">
  <div class="metric"><strong>{len(seasons)}</strong>seasons</div>
  <div class="metric"><strong>{len(teams)}</strong>clubs</div>
  <div class="metric"><strong>{match_count}</strong>matches</div>
  <div class="metric"><strong>{external_link_count}</strong>external links</div>
  <div class="metric"><strong>{len(graph):,}</strong>RDF triples</div>
</div>
<div class="actions">
  <a class="button" href="download/football-data.ttl">Download Turtle</a>
  <a href="ontology/">Browse the ontology</a>
  <a href="resource/team/arsenal/">Open an example team</a>
  <a href="{REPOSITORY_URL}">Source repository</a>
</div>
<section class="panel">
  <h2>Published artifacts</h2>
  <ul>
    <li><a href="download/football-data.ttl">Complete RDF dataset</a></li>
    <li><a href="ontology/football.ttl">OWL ontology</a></li>
    <li><a href="download/football-shapes.ttl">SHACL shapes</a></li>
    <li><a href="download/entity-links.csv">Wikidata and DBpedia mappings</a></li>
    <li><a href="download/csv/competitions.csv">Competition CSV</a></li>
    <li><a href="download/csv/seasons.csv">Season CSV</a></li>
    <li><a href="download/csv/teams.csv">Team CSV</a></li>
    <li><a href="download/csv/matches.csv">Match CSV</a></li>
    <li><a href="download/LICENSE-DATA.md">CC0 data license</a></li>
  </ul>
</section>
<section class="panel">
  <h2>Seasons</h2>
{resource_list(graph, seasons)}
</section>
<section class="panel">
  <h2>Clubs</h2>
{resource_list(graph, teams)}
</section>
<footer>Generated from the public-domain OpenFootball dataset.</footer>
"""
    (output_dir / "index.html").write_text(
        page_shell(
            SITE_NAME,
            body,
            "assets/style.css",
            canonical_uri=BASE_URL,
            alternate_href="download/football-data.ttl",
        ),
        encoding="utf-8",
    )


def build_site(data_path: Path, ontology_path: Path, output_dir: Path) -> int:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    data_graph = Graph().parse(data_path, format="turtle")
    ontology_graph = Graph().parse(ontology_path, format="turtle")
    graph = data_graph + ontology_graph

    (output_dir / "assets").mkdir()
    (output_dir / "assets/style.css").write_text(STYLES + "\n", encoding="utf-8")
    (output_dir / ".nojekyll").write_text("", encoding="ascii")
    copy_public_downloads(output_dir, data_path, ontology_path)
    write_home_page(data_graph, output_dir)

    local_subjects = sorted(
        {
            subject
            for subject in graph.subjects()
            if isinstance(subject, URIRef) and str(subject).startswith(BASE_URL)
        },
        key=str,
    )
    references = inbound_index(graph)
    for subject in local_subjects:
        write_resource_page(graph, subject, output_dir, references.get(subject))

    not_found = """
<p class="eyebrow">Resource not found</p>
<h1>This URI is not part of the published dataset.</h1>
<p class="lead"><a href="./">Return to the dataset home page</a>.</p>
"""
    (output_dir / "404.html").write_text(
        page_shell("Resource not found", not_found, "assets/style.css"),
        encoding="utf-8",
    )
    return len(local_subjects)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the static Linked Data site.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    page_count = build_site(args.data, args.ontology, args.output)
    print(f"Built {page_count} resource pages in {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
